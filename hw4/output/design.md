# Campus Customs - design changes (Problem 10)

This note records the visual design changes and why each one helps bring in and keep
Campus Customs customers.

## Changes

### 1. Typography: Inter for body, Montserrat for headings

**What changed:** The site now loads two Google fonts. **Montserrat** (a clean,
geometric, collegiate-feeling font) is used for all headings and the brand name, and
**Inter** (a highly legible UI font) is used for body text, labels, and buttons. These
are set with CSS variables (`--font-head`, `--font-body`) so they apply everywhere.

**Why it helps bring customers:** Strong, consistent type makes the store look
professional and trustworthy the moment a shopper lands. Montserrat headings give the
brand a confident, sporty-collegiate voice that fits Yale gear, while Inter keeps
product names, prices, and descriptions easy to read at a glance - lower reading effort
means shoppers browse longer and are more likely to buy.

### 2. Color: shades of Yale navy blue

**What changed:** The palette is rebuilt around **Yale Blue (#00356b)** with a range
of navy shades for depth and hierarchy:

- `--navy-900: #001a33` - deepest navy (strong contrast accents)
- `--navy: #00356b` - Yale Blue, the primary brand color (nav bar, buttons, headings)
- `--navy-soft: #0e4c92` - mid navy for hovers and gradients
- `--blue: #286dc0` - a brighter Yale accent blue
- `--sky: #e6eef8` and `--cream: #f6f9fd` - pale, navy-tinted backgrounds

A restrained Yale gold (`--gold`) remains only as a small accent. Text uses a
near-navy ink (`--ink: #0c1b2e`) so even the copy stays on-brand.

**Why it helps bring customers:** Navy blue is Yale's identity, so a navy-led store
instantly reads as *the* authentic Yale shop - which builds trust and pride, the main
reasons people buy school merch. The graduated shades (deep navy to pale sky) create
clear visual hierarchy so buttons and calls-to-action stand out, guiding shoppers
toward products and checkout. The pale-but-colorful backgrounds keep the pages bright
and modern rather than heavy, which keeps shoppers comfortable and browsing.

## Where to see it

Every page: the Montserrat brand name and headings, Inter body text, the Yale-navy nav
bar and buttons, and the pale navy-tinted page backgrounds. Product cards, the product
detail page, the auth pages, and the floating chat all use the same navy palette for a
single, consistent Campus Customs look.

## Landing page & layout changes

### 3. Banner photo carousel + more photos

**What changed:** The landing page now opens with a full-width **banner photo
carousel** that auto-advances through real product photos (with prev/next arrows and
dot indicators) under the "Wear your Bulldog pride" headline. Below the intro, a large
**"Shop the look" photo gallery** shows many product images in a dense grid, each
linking to its product page.

**Why it helps bring customers:** Big, rotating lifestyle photos make the store feel
lively and aspirational the moment someone lands, and showing lots of real merch up
front (instead of text blocks) gets shoppers clicking into products faster.

### 4. No header row - collapsible "Y" menu

**What changed:** The top header bar was removed; the top-left is empty. All
navigation (Home, Products, About Us, Log in, Create account) now lives in a
**collapsible menu** opened by a square **"Y" button** in the top-right.

**Why it helps bring customers:** It gives the photos the full width of the screen for
an immersive, modern storefront, while the Y button keeps navigation one tap away and
reinforces the Yale brand mark.

### 5. Flat design (no rounded corners) + no three-column block

**What changed:** All rounded corners were removed site-wide for a clean, flat,
editorial look, and the old three-column feature block on the landing page was dropped
in favor of a single centered intro and the full-width photo gallery.

**Why it helps bring customers:** Sharp, flat edges read as premium and collegiate, and
removing the busy three-column block keeps the focus on the product photography that
actually sells the merch.
