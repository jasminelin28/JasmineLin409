"""campus customs fastapi backend: auth, catalogue and the shopping chatbot."""
import json
import sqlite3

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field

import agent
import auth
import catalogue
import config
import db
from models import ChatReply, ChatRequest, CustomerInfo

app = FastAPI(title="Campus Customs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# serve product images from the gitignored data folder at /images/...
# (kept distinct from the frontend's /products/:id routes)
if config.products_dir.exists():
    app.mount("/images", StaticFiles(directory=config.products_dir), name="images")


# ---------- request / response models ----------
class SignupRequest(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ChatRequest / ChatReply are defined in models.py (shared with the agent)


# ---------- auth dependency ----------
def current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    try:
        payload = auth.decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, email, first_name, last_name FROM users WHERE id = ?",
            (int(payload["sub"]),),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="User not found")
    return db.row_to_dict(row)


def optional_user(authorization: str | None = Header(default=None)) -> dict | None:
    """like current_user, but returns None for guests instead of raising.

    lets guests use the chat while still identifying logged-in shoppers.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    try:
        payload = auth.decode_token(token)
    except Exception:
        return None
    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, email, first_name, last_name FROM users WHERE id = ?",
            (int(payload["sub"]),),
        ).fetchone()
    return db.row_to_dict(row) if row else None


def _public_user(row: dict) -> dict:
    return {
        "id": row["id"],
        "first_name": row.get("first_name") or "",
        "last_name": row.get("last_name") or "",
        "email": row["email"],
    }


# ---------- routes ----------
@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "model": config.chat_model}


@app.post("/api/signup")
def signup(payload: SignupRequest) -> dict:
    full_name = f"{payload.first_name} {payload.last_name}".strip()
    password_hash = auth.hash_password(payload.password)
    try:
        with db.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO users (name, email, password_hash, first_name, last_name) "
                "VALUES (?, ?, ?, ?, ?)",
                (full_name, payload.email, password_hash, payload.first_name, payload.last_name),
            )
            conn.commit()
            user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="An account with that email already exists")
    token = auth.create_token(user_id, payload.email)
    user = {
        "id": user_id,
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "email": payload.email,
    }
    return {"token": token, "user": user}


@app.post("/api/login")
def login(payload: LoginRequest) -> dict:
    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (payload.email,)
        ).fetchone()
    if row is None or not auth.verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    user = db.row_to_dict(row)
    token = auth.create_token(user["id"], user["email"])
    return {"token": token, "user": _public_user(user)}


@app.get("/api/me")
def me(user: dict = Depends(current_user)) -> dict:
    return {"user": _public_user(user)}


@app.get("/api/products")
def products() -> dict:
    return {"products": catalogue.list_products()}


@app.get("/api/products/{product_id}")
def product_detail(product_id: str) -> dict:
    product = catalogue.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"product": product}


def _load_history(conn, user_id: int, limit: int = 20) -> list[dict]:
    rows = conn.execute(
        "SELECT role, content, products_json FROM chat_messages "
        "WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    history = []
    for row in reversed(rows):
        entry = {"role": row["role"], "content": row["content"]}
        if row["products_json"]:
            entry["products"] = json.loads(row["products_json"])
        history.append(entry)
    return history


@app.get("/api/chat/history")
def chat_history(user: dict = Depends(current_user)) -> dict:
    with db.get_connection() as conn:
        return {"messages": _load_history(conn, user["id"], limit=50)}


@app.post("/api/chat", response_model=ChatReply)
async def chat(
    payload: ChatRequest, user: dict | None = Depends(optional_user)
) -> ChatReply:
    # logged-in shoppers get persisted history + are identified to the agent;
    # guests can still chat, but nothing is saved for them
    customer = None
    history: list[dict] = []
    if user is not None:
        customer = CustomerInfo(
            id=user["id"],
            name=user["name"],
            first_name=user.get("first_name") or "",
            last_name=user.get("last_name") or "",
            email=user["email"],
        )
        with db.get_connection() as conn:
            history = _load_history(conn, user["id"], limit=20)

    # the website's message goes to the PydanticAI agent, which returns a typed reply
    reply = await agent.run_chat(
        payload.message, history, customer=customer, context=payload.context
    )

    if user is not None:
        products_json = json.dumps([p.model_dump() for p in reply.products])
        with db.get_connection() as conn:
            conn.execute(
                "INSERT INTO chat_messages (user_id, role, content) VALUES (?, 'user', ?)",
                (user["id"], payload.message),
            )
            conn.execute(
                "INSERT INTO chat_messages (user_id, role, content, products_json) "
                "VALUES (?, 'assistant', ?, ?)",
                (user["id"], reply.reply, products_json),
            )
            conn.commit()

    return reply
