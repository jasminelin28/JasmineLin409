"""structured types for chat replies and product cards."""
from typing import Any

from pydantic import BaseModel, Field


class SizeStock(BaseModel):
    """stock for one size of a product."""

    size: str
    quantity: int


class ProductCard(BaseModel):
    """the product shape the front end renders in the grid and chat results."""

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str] = Field(default_factory=list)
    search_tags: list[str] = Field(default_factory=list)
    image_url: str
    price: float
    sizes: list[SizeStock] | None = None
    in_stock: bool | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProductCard":
        """build a card from a catalogue dict, ignoring any extra keys."""
        sizes = data.get("sizes")
        return cls(
            product_id=data["product_id"],
            name=data["name"],
            garment_type=data["garment_type"],
            description=data["description"],
            colors=data.get("colors", []),
            search_tags=data.get("search_tags", []),
            image_url=data["image_url"],
            price=data["price"],
            sizes=[SizeStock(**s) for s in sizes] if sizes else None,
            in_stock=data.get("in_stock"),
        )


# ---------- tool lookup results (what the agent reads from the database) ----------
class ProductSummary(BaseModel):
    """compact search hit: enough for the agent to describe and pick an item."""

    product_id: str
    name: str
    garment_type: str
    colors: list[str] = Field(default_factory=list)
    price: float


class ProductDetails(BaseModel):
    """full lookup for one product, including description and per-size stock."""

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str] = Field(default_factory=list)
    price: float
    sizes: list[SizeStock] = Field(default_factory=list)
    in_stock: bool


class PriceResult(BaseModel):
    """honest price lookup for one product."""

    product_id: str
    name: str
    price: float


class StockResult(BaseModel):
    """honest stock lookup across all sizes of a product."""

    product_id: str
    name: str
    sizes: list[SizeStock] = Field(default_factory=list)
    in_stock: bool


class SizeStockResult(BaseModel):
    """honest stock lookup for one specific size."""

    product_id: str
    name: str
    size: str
    quantity: int
    available: bool


class StoreInfo(BaseModel):
    """facts about the Campus Customs store, so the agent answers accurately."""

    name: str
    address: str
    description: str
    shipping: str
    returns: str


class CustomerInfo(BaseModel):
    """who the agent is chatting with (only set for logged-in shoppers)."""

    id: int
    name: str
    first_name: str = ""
    last_name: str = ""
    email: str


class PageContext(BaseModel):
    """what the shopper is looking at when they send a message, so 'this' resolves."""

    product_id: str | None = None
    product_name: str | None = None
    path: str | None = None


class ChatRequest(BaseModel):
    """an incoming chat message from the website, with optional page context."""

    message: str = Field(min_length=1)
    context: PageContext | None = None


class ChatReply(BaseModel):
    """the agent's reply plus the products it surfaced for the page."""

    reply: str
    products: list[ProductCard] = Field(default_factory=list)
