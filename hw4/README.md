# Campus Customs

A customer storefront for **Campus Customs**, the Yale Bulldog Blue store in New
Haven. Shoppers browse officially licensed Yale merch, create an account, and chat
with **Handsome Dan** — an AI shopping assistant that finds matching products, shows
them on the page, and answers honestly about price and stock from a local database.

- **Frontend:** React + Vite + TypeScript
- **Backend:** Python + FastAPI
- **Agent brain:** PydanticAI over OpenAI (via the Portkey gateway)
- **Data:** SQLite (`catalogue`, `inventory`, `users`, `chat_messages`)

The agent is four files under `backend/`: `prompts/prompt.md` (system prompt),
`agent.py` (wiring), `tools.py` (tools), and `models.py` (structured types).

## Project layout

```
hw4/
├── AI_prompts.md          # log of prompts used to build this
├── requirements.txt       # backend Python deps
├── .env.example           # copy to .env and add your key
├── .gitignore
├── README.md
├── frontend/              # Vite React TypeScript app
├── backend/
│   ├── main.py            # FastAPI app — uvicorn main:app --reload --port 8000
│   ├── agent.py           # PydanticAI agent wiring
│   ├── models.py          # Pydantic / PydanticAI types
│   ├── tools.py           # tools the agent can call
│   └── prompts/prompt.md  # system prompt (voice + safety rules)
└── output/                # harness.md, design.md, usability.md, app_check.html, audit_trail.json
```

## 1. Add the local-only data pack

The database and product images are **not** in git. Download the data pack and place
it at the `hw4/` root so you have:

```
hw4/
└── data/
    ├── campus_customs.db
    └── products/          # images referenced by the catalogue
```

## 2. Add your API key

Copy `.env.example` to `.env` (in the `hw4/` folder) and fill in your Portkey key:

```
PORTKEY_API_KEY=your-portkey-key-here
```

(Optional overrides like `CAMPUS_CHAT_MODEL` are listed in `.env.example`.)

## 3. Run the backend (terminal 1)

```bash
cd backend
python -m venv .venv
.venv/Scripts/python -m pip install -r ../requirements.txt     # Windows
# source .venv/bin/activate && pip install -r ../requirements.txt   # macOS/Linux
uvicorn main:app --reload --port 8000
```

## 4. Run the frontend (terminal 2)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. The Vite dev server proxies `/api` and `/images` to
the backend on port 8000.

## Using the app

- Browse **Products** (filter chips + sort), click a card for the single-item page.
- **Create account** / **Log in** (a seeded test user is
  `test@campuscustoms.yale.edu` / `password`).
- Click the **Handsome Dan** image (bottom-right) to open **Ask Dan** and try:
  - "How many hoodies do you have?" → matching cards appear on the page
  - "Which hoodies are under $70?"  → budget-aware results
  - On a product page: "do you have this in pink?" → it knows which item
  - "Where is your store and do you ship internationally?"

## Notes

- Model: `5.6luna` (Portkey/OpenAI) by default; override with `CAMPUS_CHAT_MODEL`.
- Every chat turn is logged append-only to `output/audit_trail.json`.
- See `output/harness.md` for the full system reference (tools, models, safety
  rules, and specs).
