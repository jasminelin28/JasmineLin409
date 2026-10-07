# Campus Customs - usability improvements (Problem 9)

Four improvements: two on the front end (look and ease of use) and two on the
agent/backend (more accurate, grounded answers). All are live in the app.

## Front-end improvements

### 1. Filter chips + sort on the Products page

**What I added:** A row of garment-type filter chips (All items, hoodie, T-shirt,
crewneck, quarter-zip, ...) built from the catalogue, plus a "Sort" dropdown
(Name A-Z, Price low-to-high, Price high-to-low). The grid updates instantly as you
pick a type or sort order, and this works alongside the existing search box.

**Why it helps:** With 102 products, scrolling the whole grid is slow. A shopper who
wants "just hoodies, cheapest first" can get there in two clicks. Faster browsing
means shoppers find what they want and are more likely to buy - good for the shopper
and the business.

*Where to see it:* Products page, above the grid.

### 2. Loading skeletons + broken-image fallback

**What I added:** While the catalogue loads, the grid shows shimmering skeleton
placeholder cards instead of an empty screen. If any product image fails to load, the
card shows a tidy "Campus Customs" placeholder tile instead of a broken-image icon.

**Why it helps:** The page feels fast and intentional instead of blank or glitchy,
even on a slow connection. Shoppers trust a store that looks polished, and never see
an ugly broken image - which protects the brand.

*Where to see it:* Products page on first load (skeletons); any missing image shows
the fallback tile.

## Agent / backend improvements

### 3. Budget-aware product tool (`find_products_in_budget`)

**What I added:** A new agent tool that filters the catalogue by a price range and
returns matches cheapest-first, instead of the agent eyeballing prices. The prompt
tells the agent to use only this tool for budget questions, so the product cards shown
on the page all truly fit the budget. Search is also plural-tolerant now ("hoodies"
matches "hoodie").

**Why it helps:** Budget questions ("which hoodies are under $70?") now get accurate
answers and an accurate set of cards on the page - no $88 item sneaking into an
"under $70" list. Accurate results mean shoppers trust the recommendations and the
business avoids disappointed customers.

*Where to see it:* Ask the chat "which hoodies do you have under $70?" - verified it
returns 25 hoodies, all $68 or less.

### 4. Grounded store-info tool (`get_store_info`)

**What I added:** A new agent tool that returns factual store information (name,
address at 57 Broadway New Haven, what we sell, shipping to 30+ countries, and how
returns are handled), and prompt guidance to use it for store/location/shipping/returns
questions instead of guessing.

**Why it helps:** Shoppers often ask "where are you?" or "do you ship internationally?"
Before, the agent had no source for this and either declined or risked making something
up. Now it answers accurately and consistently, which is more helpful and safer (no
invented policies) - and points real shoppers toward visiting or ordering.

*Where to see it:* Ask the chat "where is your store and do you ship internationally?"
- verified it returns the New Haven address and the 30+ countries shipping fact.
