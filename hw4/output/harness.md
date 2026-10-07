# Agent harness — Campus Customs

## Problem 2 — Database tables and fields

Source: `data/campus_customs.db` (SQLite). The shopping agent and the storefront
read from these four tables. For each field below there is one short line on why
it matters to the **agent** (what it chats about) or the **shop** (what it shows).

### `catalogue` — the product catalogue (102 rows)

| Field | Type | Why it matters |
| --- | --- | --- |
| `product_id` | TEXT (primary key) | Stable id the agent passes to its price/stock tools and the frontend uses to link a chat result to a grid item. |
| `name` | TEXT | Human-readable product name the agent says out loud and the shop shows on each card. |
| `garment_type` | TEXT | Lets the agent and shopper filter by kind of item (hoodie, tee, quarter-zip). |
| `description` | TEXT | Grounds the agent's answers in real product details instead of guesses. |
| `colors` | TEXT (JSON list) | Lets the agent match color requests ("navy hoodie") and describe options honestly. |
| `search_tags` | TEXT (JSON list) | Keywords (team, college, style) the agent's search ranks against, so the right merch surfaces. |
| `image_file_path` | TEXT | Path the shop turns into the image URL so the product actually shows on the page. |
| `price` | REAL | The single source of truth for price, so the agent never invents a number. |

### `inventory` — stock by product and size (612 rows)

Sizes in the data: `XS, S, M, L, XL, XXL`.

| Field | Type | Why it matters |
| --- | --- | --- |
| `id` | INTEGER (primary key) | Row id; keeps each product-plus-size stock line unique. |
| `product_id` | TEXT (→ catalogue) | Ties a stock line back to its product so the agent can check the right item. |
| `size` | TEXT | Lets a shopper ask "is M in stock?" and get a size-specific answer. |
| `quantity` | INTEGER | The honest stock count the agent reports and uses to say in/out of stock. |

### `users` — shopper accounts (test rows seeded)

| Field | Type | Why it matters |
| --- | --- | --- |
| `id` | INTEGER (primary key) | Identifies the shopper; links their chat history to them. |
| `name` | TEXT | Full display name stored at signup. |
| `email` | TEXT (unique) | Login identity; the unique constraint stops duplicate accounts. |
| `password_hash` | TEXT | PBKDF2-SHA256 hash so real passwords are never stored in plain text. |
| `created_at` | TEXT (default now) | When the account was made; basic account record-keeping. |
| `first_name` | TEXT | Used to greet the shopper personally in the storefront. |
| `last_name` | TEXT | Completes the shopper's name for the account. |

### `chat_messages` — saved conversations (grows as people chat)

| Field | Type | Why it matters |
| --- | --- | --- |
| `id` | INTEGER (primary key) | Orders the messages in a conversation. |
| `user_id` | INTEGER (→ users) | Keeps each conversation private to one shopper. |
| `role` | TEXT | Marks a line as `user` or `assistant` so history replays correctly. |
| `content` | TEXT | The message text; it's both the transcript and the agent's memory of the chat. |
| `products_json` | TEXT | The products the agent surfaced on that turn, so they reappear when history loads. |
| `created_at` | TEXT (default now) | Timestamps each message for ordering and record-keeping. |

**Relationships:** `inventory.product_id` and `catalogue.product_id` join a product
to its per-size stock; `chat_messages.user_id` joins a saved message to its owner in
`users`. The agent's tools read `catalogue` and `inventory` for honest price and
stock; the backend writes each turn to `chat_messages`.

---

## Problem 4 — How authentication works

### What we store for a user

New accounts are written to the `users` table with:

- `first_name`, `last_name`, and `name` (the full display name) — used to greet the shopper.
- `email` — the unique login identity (the table enforces uniqueness).
- `password_hash` — a salted PBKDF2 hash, **never the plain password**.
- `created_at` — when the account was made.

We never store the raw password, a reversible encryption of it, or a plain hash.

### How passwords are protected

Passwords are hashed with **PBKDF2-HMAC-SHA256** and a per-user random salt. The
stored value has the form `pbkdf2_sha256$<salt>$<hash>`:

- **Salt:** 16 random bytes generated per account with `secrets.token_hex`, so two
  users with the same password get different hashes and precomputed/rainbow-table
  attacks do not work.
- **Key stretching:** many PBKDF2 iterations make each guess expensive, which slows
  down brute-force attempts by a human or an automated attacker.
- **Constant-time compare:** verification uses `hmac.compare_digest` so an attacker
  cannot learn the hash byte-by-byte through timing.
- **One-way:** because only the hash is stored, even someone who steals the whole
  database cannot read anyone's password.

New accounts are always hashed with the app's primary iteration count
(`CAMPUS_PBKDF2_ITERATIONS`, default 200,000). The seeded users' hashes use the
same `pbkdf2_sha256$salt$hash` format but do not record their iteration count, so
login verifies against a short list of common PBKDF2 cost presets (the way a real
password hasher supports several cost settings). This lets the provided test user
(`test@campuscustoms.yale.edu` / `password`) log in while new accounts use the
primary cost.

### Sessions

On successful signup or login the backend issues a signed **JWT** (HS256, stored
client-side). Protected routes (`/api/me`, `/api/chat`) require the token in an
`Authorization: Bearer ...` header; the token is verified on every request, so the
password is only ever handled at sign-in time.

### Verified

- Logged in as the seed test user `test@campuscustoms.yale.edu` / `password`.
- A wrong password is rejected (HTTP 401).
- Created a brand-new account and logged in with it successfully.

---

## Problem 5 — Front end, FastAPI, and the agent

### How the front end talks to FastAPI

- The React app calls the backend over HTTP with `fetch` through a small client
  (`frontend/src/api.ts`). In development, Vite proxies `/api/*` and `/images/*`
  to the FastAPI server on port 8000, so the browser talks to one origin.
- The floating chat widget (`frontend/src/components/FloatingChat.tsx`) sends the
  shopper's message as JSON to `POST /api/chat` with the user's JWT in an
  `Authorization: Bearer ...` header.
- `main.py` is the Uvicorn entry point (`uvicorn main:app --reload --port 8000`
  from `backend/`). It exposes the chat route plus the product and auth routes the
  site needs:
  - `POST /api/chat` -> agent reply (requires login)
  - `GET /api/chat/history` -> saved conversation
  - `GET /api/products`, `GET /api/products/{id}` -> catalogue
  - `POST /api/signup`, `POST /api/login`, `GET /api/me` -> accounts
  - `/images/...` -> product images
- The chat route returns a typed `ChatReply` (`reply` text plus a list of
  `ProductCard`s). The widget shows the reply and the product cards; clicking a
  card opens that product's page.

### How the agent is loaded (prompt file + model)

The agent is split across four files next to `main.py`:

- `prompts/prompt.md` — the Campus Customs system prompt (voice + safety basics),
  kept in its own file so it is easy to edit.
- `models.py` — Pydantic types: `ChatRequest`, `ChatReply`, `ProductCard`,
  `SizeStock`.
- `tools.py` — the catalogue tools (`search_products`, `get_product_details`,
  `get_price`, `check_stock`) and the `ChatDeps` object that remembers which
  products were shown this turn.
- `agent.py` — wiring. It reads `prompts/prompt.md`, builds an
  `OpenAIChatModel` pointed at the Portkey gateway (model from
  `CAMPUS_CHAT_MODEL`, default `5.6luna`), and creates a PydanticAI `Agent` with
  that prompt and the four tools. `run_chat()` runs one turn (passing recent
  history) and returns a `ChatReply`.

So `main.py` imports `agent` and `models`; `agent.py` loads the prompt file and
model and registers the tools from `tools.py`; the tools read the catalogue from
`catalogue.py` / `db.py`. The prompt and model can be changed without touching the
API routes.

---

## Problem 6 — Database lookup tools and their return types

All four tools read from `campus_customs.db` through `catalogue.py` and return a
typed model from `models.py`, so the agent can never invent a price or quantity.

### Tools

| Tool | Reads | Returns |
| --- | --- | --- |
| `search_products(query, limit)` | `catalogue` (name, type, colors, tags, description) | `list[ProductSummary]` |
| `get_product_details(product_id)` | `catalogue` + `inventory` | `ProductDetails` |
| `get_price(product_id)` | `catalogue.price` | `PriceResult` |
| `check_stock(product_id, size?)` | `inventory` | `StockResult` (all sizes) or `SizeStockResult` (one size) |

### Which model fields were chosen, and why

- **`ProductSummary`** - `product_id`, `name`, `garment_type`, `colors`, `price`.
  Just enough for the agent to describe a few search hits and pick one to look up.
  The full image/description is left out to keep search results small; the front
  end gets the rich card separately.
- **`ProductDetails`** - `product_id`, `name`, `garment_type`, `description`,
  `colors`, `price`, `sizes` (list of `SizeStock`), `in_stock`. This is the
  "tell me about it" answer: the **description** field is the point, and price +
  per-size stock let the agent answer follow-ups without another call.
- **`PriceResult`** - `product_id`, `name`, `price`. Minimal and unambiguous: the
  name confirms which item, the price is the one honest number. Nothing else is
  needed for a price question, so nothing else is returned.
- **`StockResult`** - `product_id`, `name`, `sizes` (list of `SizeStock`),
  `in_stock`. For "what sizes do you have?" - it lists every size with its
  quantity, plus an overall `in_stock` flag so the agent can answer at a glance.
- **`SizeStockResult`** - `product_id`, `name`, `size`, `quantity`, `available`.
  For "do you have it in M?" - it pins the answer to one size. `available` is a
  plain boolean derived from `quantity > 0`, so the agent can say "out of stock"
  clearly when `quantity` is 0.
- **`SizeStock`** - `size`, `quantity`. The shared building block for stock lists,
  used by `ProductDetails`, `StockResult` and the front-end `ProductCard`.

`product_id` and `name` appear on every result on purpose: the id ties the answer
back to a specific catalogue row (and to the product page), and the name lets the
agent speak naturally without echoing an id at the shopper.

---

## Problem 7 — Dynamic product cards from chat (the API contract)

When a shopper asks about a type of item, the agent's matches are rendered on the
site as live product cards. The contract:

1. **Agent returns structured matches.** Every product the agent looks up in a turn
   is remembered in `ChatDeps.shown`. `run_chat` converts them to `ProductCard`
   models, and `POST /api/chat` returns `ChatReply { reply, products: [ProductCard] }`.
   Each `ProductCard` carries everything the UI needs: `product_id`, `name`, `price`,
   `image_url`, `description`, `colors`, and (when looked up) `sizes` / `in_stock`.
2. **Front end receives them.** `FloatingChat` reads `res.products`, pushes them into
   a shared `ChatResultsProvider` context, and navigates to `/products`.
3. **The page renders cards.** The Products page reads the context and renders a
   "Handsome Dan found these for you" section using the **same `ProductCard`
   component** as the normal grid.
4. **Detail view still works.** `ProductCard` is a React Router `<Link>` to
   `/products/:id`. Because the chat matches are real catalogue products, clicking a
   chat-surfaced card opens the same single-item page (large image + full info) built
   in Problem 3 - no special case needed.

So the data path is: agent tools -> `ChatDeps.shown` -> `ChatReply.products` ->
`/api/chat` JSON -> `ChatResultsProvider` -> Products page cards -> product detail page.

---

## Problem 8 — Chat history, customer identity, and page context

### How user chat history is stored

Chat turns are saved in the existing **`chat_messages`** table, one row per message:
`user_id`, `role` (`user` / `assistant`), `content`, `products_json` (the cards the
agent surfaced that turn), and `created_at`.

- On `POST /api/chat`, if the shopper is **logged in**, the backend loads their
  recent messages (so the agent has conversation memory) and, after replying, inserts
  the new user message and the assistant reply.
- `GET /api/chat/history` returns the saved messages (including the product cards) so
  the chat widget **reloads the conversation when the shopper returns**. The widget
  only calls this when a user is logged in.
- **Guests can still chat** (`POST /api/chat` uses optional auth), but nothing is
  written for them and they cannot read history (`/api/chat/history` is 401 without a
  token). History only persists for logged-in users.

### What customer fields the agent sees

For a logged-in shopper the chat route builds a `CustomerInfo`
(`id`, `name`, `first_name`, `last_name`, `email`) and passes it into the agent as
part of `ChatDeps` (`deps.customer`). The agent is told who it is talking to two ways:

- A dynamic `@agent.system_prompt` (`who_is_chatting`) injects the shopper's name and
  email into the prompt each turn (or says "guest" when `deps.customer` is None).
- A `whoami` tool returns the same `CustomerInfo` if the agent needs it explicitly.

Guests have `deps.customer = None`, and the prompt tells the agent not to assume a name.

### How page context is passed

`ChatRequest` carries an optional `context: PageContext` (`product_id`,
`product_name`, `path`). The chat widget fills it from the current route: on
`/products/:id` it sends that `product_id`.

- `run_chat` resolves `context.product_id` to the full product via `catalogue` and
  stores it on `ChatDeps.current_product`.
- A dynamic `@agent.system_prompt` (`current_page`) tells the agent which product the
  shopper is viewing and that "this"/"it" refer to it, with the `product_id` to use in
  tool calls.

So when a shopper on a product page asks "do you have this in pink?", the agent knows
exactly which item they mean and answers honestly from the database (verified: it
correctly said the Basic Hoodie Big Yale comes in navy/white, not pink).

---

## Problem 12 — System reference (how it all works)

### Audit trail

Every chat turn is logged, append-only, to `output/audit_trail.json` (JSON Lines -
one JSON object per line, never wiped between runs). Two record types:

- `tool_call` - `time`, `tool`, short `args`, short `result` (one per tool call).
- `turn` - `time`, short `message`, `tools_used`, `requests` (model requests this
  turn), and `stop_reason` (`completed` or `error: <type>`).

Written by `backend/audit.py`; `agent.run_chat` pairs each tool call with its result
and records a turn summary after the run.

### Model fields in `models.py` (and why)

- **`ChatRequest`** - `message`, optional `context: PageContext`. The message is the
  shopper's text; the context lets "this" resolve on a product page.
- **`PageContext`** - `product_id`, `product_name`, `path`. Just enough to know what
  the shopper is looking at.
- **`ChatReply`** - `reply` (text) + `products: list[ProductCard]`. One consistent
  response shape for the widget and saved history.
- **`ProductCard`** - `product_id`, `name`, `garment_type`, `description`, `colors`,
  `search_tags`, `image_url`, `price`, optional `sizes`/`in_stock`. Everything the UI
  needs to render a card and open the detail page.
- **`SizeStock`** - `size`, `quantity`. Shared building block for stock lists.
- **Tool results** - `ProductSummary` (compact search hit), `ProductDetails`
  (description + price + per-size stock), `PriceResult` (id/name/price),
  `StockResult` (all sizes + `in_stock`), `SizeStockResult` (one size + `available`).
  Each is the minimum needed to answer its question, and all carry `product_id` +
  `name` so answers tie back to a real row. (Full rationale in the Problem 6 section.)
- **`CustomerInfo`** - `id`, `name`, `first_name`, `last_name`, `email`. Who the agent
  is talking to (logged-in only).
- **`StoreInfo`** - `name`, `address`, `description`, `shipping`, `returns`. Factual
  store answers instead of guesses.

### Tools and abilities

| Tool | Ability |
| --- | --- |
| `search_products(query, limit)` | keyword search over the catalogue |
| `get_product_details(product_id)` | description + price + per-size stock |
| `get_price(product_id)` | honest price |
| `check_stock(product_id, size?)` | honest stock, all sizes or one size |
| `find_products_in_budget(query, max_price?, min_price?)` | price-range search, cheapest first |
| `get_store_info()` | factual store/location/shipping/returns |
| `whoami()` | the signed-in shopper's name/email (or none) |

The agent also receives, through `ChatDeps` + dynamic system prompts: **who is
chatting** (`customer`) and **the current product** (`current_product`), so it can
greet by name and resolve "this". Products surfaced in a turn are returned as cards
and rendered on the page.

### Safety rules

The system prompt (`prompts/prompt.md`) gives the agent nine safety rules: stay on
topic; never invent facts; protect secrets (prompt/keys/DB internals); protect other
customers' privacy; resist prompt injection (treat descriptions/messages as data);
take no real-world actions it cannot do (payments/orders/discounts); refuse harmful
or inappropriate content; be respectful and inclusive; and admit limits instead of
guessing.

### Specs

- **Models:** OpenAI via the Portkey gateway; default `5.6luna`
  (`CAMPUS_CHAT_MODEL`). A smarter model can be set via that env var.
- **Loop limit:** `REQUEST_LIMIT = 8` model requests per chat turn
  (`UsageLimits(request_limit=8)`); exceeding it ends the turn with a graceful
  message and `stop_reason = error: ...`.
- **Result caps:** search returns 6 by default; budget search 30; chat history passed
  to the agent is the last 20 messages; `GET /api/chat/history` returns up to 50.
- **Auth/sessions:** PBKDF2-SHA256 passwords, JWT (HS256) sessions; chat works for
  guests (no history saved) and logged-in shoppers (history persisted).
- **How to run (two terminals):**
  - Backend (from `backend/`): `uvicorn main:app --reload --port 8000`
  - Frontend (from `frontend/`): `npm install` then `npm run dev` (serves
    http://localhost:5173 and proxies `/api` and `/images` to port 8000)
