# AI prompts log — Homework 4 (Campus Customs)

This file logs what I typed to my AI vibe coder while building the Campus Customs
site. One section per problem. Prompts are in my own words. The running site,
the database writes, and screenshots are the real evidence.

---

## Setup — Project scaffold and brand research

**Prompt:**
> We're doing Homework 4. Work only in the Homework 4 folder and make a virtual
> environment there. Campus Customs needs a real customer website with a helpful
> chatbot: a React + Vite + TypeScript front end and a Python FastAPI backend
> whose brain is a PydanticAI agent. Shoppers should browse products, make an
> account, chat about merch, see matching items appear on the page, and get
> honest price and stock answers from the local `campus_customs.db`. Download and
> unzip the data, and research yalebulldogblue.com so the agent sounds like the
> real store. Don't commit the database or the product images.

**Follow-up prompt:**
> The agent's product, price, and stock claims have to come from the database, not
> be made up. Give the agent tools for search, product details, price, and
> per-size stock, and make the items it mentions show up and float to the top of
> the grid.

*What was lacking after the first prompt:* the first pass didn't say strongly
enough that every price/stock fact must be tool-grounded, so I added that rule and
the "show matching items on the page" behavior.

---

## Problem 1 — AI prompts log

**Prompt:**
> Create an `AI_prompts.md` at the start and keep it updated as we go. It's the log
> of what I typed to my vibe coder. One section per problem, each with the problem
> number and title, at least one prompt in my own words, and a follow-up prompt if
> I needed one plus a sentence on what the first prompt was missing. Don't write a
> separate proof essay — the running site, DB writes, and screenshots are the
> evidence.

*No follow-up needed — the instructions were clear the first time.*

---

## Problem 2 — Database tables and fields

**Prompt:**
> Look at `data/campus_customs.db` and write a new harness markdown file in the
> `output` folder. List every table and its fields, and for each field write one
> short line on why it matters to the agent or the shop.

**Follow-up prompt:**
> There's no harness file in Homework 4 yet — don't reuse Homework 3's. Make a new
> `output/harness.md` here, and read the real schema from the database so the field
> list and types are exactly right.

*What was lacking after the first prompt:* I pointed at an "output/harness markdown
file" that didn't exist in this folder, so I clarified to create a fresh one and
pull the schema straight from the database.

---

## Problem 3 — React + Vite + TypeScript front end

**Prompt:**
> Scaffold the Campus Customs front end as React + Vite + TypeScript with a top nav
> bar linking to Home, Products, About Us, Log in, and Create account. Write Home
> and About Us in my own voice using Campus-Customs-style wording from
> yalebulldogblue.com (don't copy their text). On Products, show the catalogue with
> each item's image (use the image paths in the database), name, price, and a short
> description. Clicking a card opens a single-item page with a big image on one side
> and the full text on the other - description, price, and sizes/stock. Add a
> floating chat box in the bottom-right. Start a small FastAPI app in
> `backend/main.py` to serve products and images so the pages have real data.

**Follow-up prompt:**
> The image route and the product page route both started with `/products`, so
> refreshing a product page broke. Serve the images under `/images` instead and
> update the proxy so the single-item routes work on a direct link.

*What was lacking after the first prompt:* the first version served images at
`/products/...`, which collided with the client-side `/products/:id` pages; moving
images to `/images` fixed deep links and refreshes.

---

## Problem 4 — Create-account / login flow

**Prompt:**
> Build a normal create-account and login flow. Sign up takes first name, last name,
> email, and password (add a confirm-password field too). Login takes email and
> password. New accounts go in the `users` table, and passwords must be stored
> securely so nobody - human or AI - can read them. Confirm I can log in as the seed
> test user (`test@campuscustoms.yale.edu` / `password`) and that a brand-new account
> I make also works. Then update `output/harness.md` with what we store for a user
> and how passwords are protected.

**Follow-up prompt:**
> The seed users' hashes are `pbkdf2_sha256$salt$hash` with no iteration count saved,
> so I can't guess the one cost they used. Make the login verifier accept a few common
> PBKDF2 cost presets (like a real hasher does) so the test user logs in, while new
> accounts use our primary cost. Don't try to crack anything.

*What was lacking after the first prompt:* my first verifier assumed a single
iteration count, so the seed test user couldn't log in; supporting a list of known
PBKDF2 costs fixed it without cracking the hash.

---

## Problem 5 — Shop chatbot as a PydanticAI agent behind FastAPI

**Prompt:**
> Build the shop chatbot as a PydanticAI agent behind FastAPI and plug it into the
> front-end chat widget. Keep `main.py` as the Uvicorn entry point and split the
> agent into four files next to it: `prompts/prompt.md` for the system prompt,
> `agent.py` for wiring, `tools.py` for the tools, and `models.py` for the Pydantic
> types. Expose a chat route in `main.py` so a message from the site returns the
> agent's reply (plus the product and auth routes we need). Put the Campus Customs
> voice and safety basics in the prompt file, and note in `output/harness.md` how the
> front end talks to FastAPI and how the agent is loaded (prompt file + model). It
> must run with `uvicorn main:app --reload --port 8000` from the `backend` folder.

**Follow-up prompt:**
> Have the chat route return a typed `ChatReply` with `reply` text and a list of
> `ProductCard`s built in `models.py`, instead of a loose dict, so the widget and the
> saved history use one consistent shape.

*What was lacking after the first prompt:* the first version returned a plain dict
from the agent, so I moved the response shape into `models.py` as `ChatReply` /
`ProductCard` and had the route return that typed object.

---

## Problem 6 — Real database lookup tools

**Prompt:**
> Give the agent tools that look up real info from `campus_customs.db`: product
> description, price, and how many are in stock (by size when the customer asks).
> The agent must use the database and never invent prices or quantities, and when a
> size is out of stock it should say so clearly. Expand `prompts/prompt.md` so the
> agent knows to call these tools for price and stock questions, add or update the
> return types in `models.py`, and in `output/harness.md` list each tool and explain
> which model fields I picked for the lookup results and why.

**Follow-up prompt:**
> Make the tools return typed models instead of loose dicts - a small `ProductSummary`
> for search, `ProductDetails` for the description lookup, `PriceResult` for price, and
> `StockResult` / `SizeStockResult` for all-sizes vs one-size stock - and keep every
> result carrying `product_id` and `name` so answers tie back to a real row.

*What was lacking after the first prompt:* the tools first returned plain dicts, which
made the return shape fuzzy; giving each lookup its own Pydantic model made the fields
explicit and easy to document.

---

## Problem 7 — Dynamic product cards from chat

**Prompt:**
> Add a feature where, when a shopper asks about a type of item (like "how many
> hoodies do you have?"), the agent searches the catalogue and the website
> dynamically shows the matching items as product cards (image, name, price, short
> info). Treat it as an API contract: the agent returns structured product matches
> and the front end renders them. The cards the chat puts on the page must still open
> the Problem 3 single-item detail view when clicked. Update `prompts/prompt.md` and
> `output/harness.md` to explain how search results reach the page.

**Follow-up prompt:**
> Render the chat matches with the same ProductCard component as the normal grid and
> push them through a shared context from the chat widget to the Products page, so the
> cards link to `/products/:id` and the detail view keeps working for chat-surfaced
> items too.

*What was lacking after the first prompt:* at first the matches only showed as small
thumbnails inside the chat bubble; using a shared results context to render full,
clickable cards on the page itself made the feature match the spec.

---

## Problem 8 — Chat history, customer identity, and page context

**Prompt:**
> When a shopper is logged in, save their chat history in the database and reload it
> when they come back. The agent should know who is chatting (name, email) - put that
> in the agent deps (or a clear equivalent) and/or a tool it can call. Also pass enough
> page context that if someone is on a product page and asks "do you have this in
> pink?", the agent knows which item they mean (you can put code into the agent
> context). Guests can still chat, but history only needs to persist for logged-in
> users. Document in `output/harness.md` how history is stored, what customer fields the
> agent sees, and how page context is passed.

**Follow-up prompt:**
> Make the chat route use optional auth so guests can chat without anything being saved,
> and feed the agent a `CustomerInfo` in deps plus a dynamic system prompt for who is
> chatting, and resolve the page's `product_id` into `deps.current_product` so "this"
> works on a product page.

*What was lacking after the first prompt:* the chat route required login, so guests
couldn't chat; switching to optional auth (and only persisting for logged-in users)
plus injecting customer + current-product context through deps covered the whole spec.

---

## Problem 9 — Usability improvements

**Prompt:**
> Now improve the shop. Implement 2 front-end usability improvements (make the site
> look better and easier to use) and 2 agent/backend improvements (make the agent's
> output better, more accurate, or safer - new tools are fine). Write `output/usability.md`
> as I build, saying for each one what I added and why it helps a Campus Customs shopper
> or the business, and make sure all four actually show up in the running app.

**Follow-up prompt:**
> My "hoodies under $70" check showed $88 items on the page and the budget tool returned
> nothing for the plural "hoodies". Make the agent use only the budget tool for price-range
> questions so the cards all fit the budget, and make catalogue search plural-tolerant so
> "hoodies" matches "hoodie".

*What was lacking after the first prompt:* the budget answer was inaccurate - the page
cards weren't price-filtered and plural search words missed matches; forcing the budget
tool and adding singular/plural matching fixed both.

---

## Problem 10 — Design write-up

**Prompt:**
> Write `output/design.md` with my design changes and why they will help bring in
> customers. Use the Inter and Montserrat fonts, and shades of navy blue from Yale.

*No follow-up needed - I applied Inter for body text and Montserrat for headings,
rebuilt the palette around Yale Blue (#00356b) with a range of navy shades, and
documented each change and its customer benefit in `output/design.md`.*

**Q10 follow-up prompts (design iteration):**
> Redesign the landing page: add a banner photo carousel, remove all rounded corners,
> drop the three-column layout, and use more photos.
> Then: delete the top header row (top-left should have nothing) and put all the nav
> links in a collapsible menu on the top-right, opened by a Y-shaped button.

*Result: added a Carousel component driven by real product images, a dense "Shop the
look" photo gallery, a global flat (no-radius) style, and replaced the header bar with
a top-right "Y" button that opens a collapsible menu.*

---

## Problem 11 — Live app check page

**Prompt:**
> Test the live site and document it in `output/app_check.html` (double-click to open).
> Include clear screenshots with short captions for: (1) chat checking an item's
> inventory/price honestly from the DB, (2) dynamic search-result cards after a category
> question like hoodies, and (3) one of the Problem 9 usability features. Put the images
> in `output/app_check_images/` and link them with relative paths; give each check a
> heading, the screenshot, and one or two sentences on what it proves.

*Result: captured three screenshots from the running app (inventory/price chat, "Handsome
Dan found these for you" hoodie cards, and the Products filter chips + sort), saved them
to `output/app_check_images/`, and built a gradable `app_check.html` with a heading,
image, and proof sentence per check.*

---

## Problem 12 — Audit trail, safety rules, and finished harness

**Prompt:**
> Keep an append-only `output/audit_trail.json` of agent-loop activity (time, tool name,
> short args/result, stop reason) that is not wiped between runs. Add safety rules to
> `prompts/prompt.md`. Finish `output/harness.md` so it is clear how the system works:
> model fields and why, tools and abilities, safety rules, and specs (loop limits, result
> caps, models, how to run front + back).

**Follow-up prompt:**
> Log one record per tool call (pairing call args with the result) plus a turn record with
> the model-request count and stop reason, and record requests by counting model responses
> since the usage counter read as 0.

*What was lacking after the first prompt:* the first turn records showed `requests: 0`
because the usage attribute differed in this pydantic-ai version; counting `ModelResponse`
messages gave the correct per-turn request count.
