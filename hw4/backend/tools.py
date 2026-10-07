"""tools the Campus Customs agent can call to read the catalogue honestly.

every tool reads from campus_customs.db (via catalogue.py) and returns a typed
model, so the agent never has to invent a price, size or quantity.
"""
from dataclasses import dataclass, field
from typing import Any

from pydantic_ai import RunContext

import catalogue
from models import (
    CustomerInfo,
    PriceResult,
    ProductDetails,
    ProductSummary,
    SizeStock,
    SizeStockResult,
    StockResult,
    StoreInfo,
)

# known store facts (from the Yale Bulldog Blue / Campus Customs storefront) so the
# agent answers store questions from facts instead of guessing.
STORE_INFO = StoreInfo(
    name="Campus Customs (Yale Bulldog Blue)",
    address="57 Broadway, New Haven, CT 06511",
    description=(
        "The official Yale Bulldog Blue store, selling officially licensed Yale "
        "apparel and merch: tees, hoodies, crewnecks, quarter-zips, fleece, hats "
        "and more, including residential-college and sports-team gear and premium "
        "brands like Champion and Brooks Brothers."
    ),
    shipping="Ships within the U.S. and internationally to 30+ countries.",
    returns=(
        "For returns or exchanges, bring your order details to the store or contact "
        "Campus Customs; please check your order confirmation for the current policy."
    ),
)


@dataclass
class ChatDeps:
    """per-turn dependencies passed to the agent and its tools.

    - `customer`: who is chatting (None for a guest).
    - `current_product`: the product the shopper is viewing, so "this" resolves.
    - `shown`: products surfaced this turn, sent back to the page as cards.
    """

    customer: CustomerInfo | None = None
    current_product: dict[str, Any] | None = None
    shown: dict[str, dict[str, Any]] = field(default_factory=dict)

    def remember(self, products: list[dict[str, Any]]) -> None:
        for product in products:
            self.shown[product["product_id"]] = product


def whoami(ctx: RunContext[ChatDeps]) -> CustomerInfo | None:
    """Return the signed-in shopper's name and email, or null if they are a guest.
    Use this if you need to address the shopper by name."""
    return ctx.deps.customer


def find_products_in_budget(
    ctx: RunContext[ChatDeps],
    query: str = "",
    max_price: float | None = None,
    min_price: float | None = None,
    limit: int = 30,
) -> list[ProductSummary]:
    """Find products within a price range, cheapest first. Use this for budget
    questions like "hoodies under $70" or "anything between $20 and $40". Pass the
    item words as `query` (leave empty for any item) and set `max_price` and/or
    `min_price`. Only returns items that truly fall in the range."""
    results = catalogue.find_in_budget(
        query=query, min_price=min_price, max_price=max_price, limit=limit
    )
    ctx.deps.remember(results)
    return [
        ProductSummary(
            product_id=p["product_id"],
            name=p["name"],
            garment_type=p["garment_type"],
            colors=p["colors"],
            price=p["price"],
        )
        for p in results
    ]


def get_store_info(ctx: RunContext[ChatDeps]) -> StoreInfo:
    """Return factual Campus Customs store information (name, address, what we sell,
    shipping and returns). Use this for questions about the store, location, shipping
    or returns instead of guessing."""
    return STORE_INFO


def search_products(
    ctx: RunContext[ChatDeps], query: str, limit: int = 6
) -> list[ProductSummary]:
    """Search the Campus Customs catalogue by keywords such as garment type,
    color, team, residential college or style. Returns the best matching
    products. Use this whenever a shopper describes what they want."""
    results = catalogue.search_products(query, limit=limit)
    ctx.deps.remember(results)
    return [
        ProductSummary(
            product_id=p["product_id"],
            name=p["name"],
            garment_type=p["garment_type"],
            colors=p["colors"],
            price=p["price"],
        )
        for p in results
    ]


def get_product_details(
    ctx: RunContext[ChatDeps], product_id: str
) -> ProductDetails | None:
    """Look up the full description, price and per-size stock for one product by
    its product_id. Use this to answer questions about what a product is."""
    product = catalogue.get_product(product_id)
    if product is None:
        return None
    ctx.deps.remember([product])
    return ProductDetails(
        product_id=product["product_id"],
        name=product["name"],
        garment_type=product["garment_type"],
        description=product["description"],
        colors=product["colors"],
        price=product["price"],
        sizes=[SizeStock(**s) for s in product["sizes"]],
        in_stock=product["in_stock"],
    )


def get_price(ctx: RunContext[ChatDeps], product_id: str) -> PriceResult | None:
    """Look up the honest current price for a product by its product_id. Always
    use this for price questions - never guess a price."""
    result = catalogue.get_price(product_id)
    if result is None:
        return None
    return PriceResult(**result)


def check_stock(
    ctx: RunContext[ChatDeps], product_id: str, size: str | None = None
) -> StockResult | SizeStockResult | None:
    """Look up honest stock for a product by product_id. Pass a size (e.g. "M",
    "L", "XL") to check one size, or leave it out for all sizes. Always use this
    for availability questions - never guess quantities. If the quantity is 0 the
    item is out of stock."""
    result = catalogue.check_stock(product_id, size=size)
    if result is None:
        return None
    if size:
        return SizeStockResult(**result)
    return StockResult(
        product_id=result["product_id"],
        name=result["name"],
        sizes=[SizeStock(**s) for s in result["sizes"]],
        in_stock=result["in_stock"],
    )
