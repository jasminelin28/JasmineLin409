"""product catalogue, search, price and stock lookups backed by sqlite."""
from typing import Any

import db


def _product_from_row(row) -> dict[str, Any]:
    """shape a catalogue row into the json product the frontend expects."""
    data = db.row_to_dict(row)
    return {
        "product_id": data["product_id"],
        "name": data["name"],
        "garment_type": data["garment_type"],
        "description": data["description"],
        "colors": db.parse_json_list(data.get("colors", "")),
        "search_tags": db.parse_json_list(data.get("search_tags", "")),
        # db stores e.g. "products/foo.jpg"; serve it under /images/foo.jpg so the
        # path never collides with the frontend's /products/:id routes
        "image_url": "/images/"
        + data["image_file_path"].replace("\\", "/").split("products/")[-1].lstrip("/"),
        "price": round(float(data["price"]), 2),
    }


def list_products(limit: int = 200) -> list[dict[str, Any]]:
    """return the full catalogue (used for the browse grid)."""
    with db.get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM catalogue ORDER BY name LIMIT ?", (limit,)
        ).fetchall()
    return [_product_from_row(row) for row in rows]


def get_product(product_id: str) -> dict[str, Any] | None:
    """fetch a single product with its per-size stock."""
    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            return None
        product = _product_from_row(row)
        sizes = conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY id",
            (product_id,),
        ).fetchall()
    product["sizes"] = [
        {"size": s["size"], "quantity": int(s["quantity"])} for s in sizes
    ]
    product["in_stock"] = any(s["quantity"] > 0 for s in sizes)
    return product


def search_products(query: str, limit: int = 8) -> list[dict[str, Any]]:
    """keyword search over name, type, description, colors and search tags.

    ranks matches by how many query words land in the product text so the
    most relevant merch surfaces first for the chatbot.
    """
    words = [w.strip().lower() for w in query.split() if w.strip()]
    with db.get_connection() as conn:
        rows = conn.execute("SELECT * FROM catalogue").fetchall()

    scored: list[tuple[int, dict[str, Any]]] = []
    for row in rows:
        product = _product_from_row(row)
        haystack = " ".join(
            [
                product["name"],
                product["garment_type"],
                product["description"],
                " ".join(product["colors"]),
                " ".join(product["search_tags"]),
            ]
        ).lower()
        if not words:
            score = 0
        else:
            # match each word or its singular form, so "hoodies" matches "hoodie",
            # "tees" matches "tee", "crewnecks" matches "crewneck", etc.
            score = sum(
                1 for w in words if w in haystack or w.rstrip("s") in haystack
            )
            if score == 0:
                continue
        scored.append((score, product))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [product for _score, product in scored[:limit]]


def find_in_budget(
    query: str = "",
    min_price: float | None = None,
    max_price: float | None = None,
    limit: int = 8,
) -> list[dict[str, Any]]:
    """search (optionally) then filter by price, cheapest first.

    with an empty query this ranks the whole catalogue by price within the budget,
    so "anything under $40" works as well as "hoodies under $70".
    """
    if query.strip():
        candidates = search_products(query, limit=len(_all_products()))
    else:
        candidates = _all_products()

    results = []
    for product in candidates:
        price = product["price"]
        if min_price is not None and price < min_price:
            continue
        if max_price is not None and price > max_price:
            continue
        results.append(product)

    results.sort(key=lambda p: p["price"])
    return results[:limit]


def _all_products() -> list[dict[str, Any]]:
    """every catalogue product as dicts (used by budget filtering)."""
    with db.get_connection() as conn:
        rows = conn.execute("SELECT * FROM catalogue").fetchall()
    return [_product_from_row(row) for row in rows]


def get_price(product_id: str) -> dict[str, Any] | None:
    """honest price lookup for a single product."""
    product = get_product(product_id)
    if product is None:
        return None
    return {
        "product_id": product["product_id"],
        "name": product["name"],
        "price": product["price"],
    }


def check_stock(product_id: str, size: str | None = None) -> dict[str, Any] | None:
    """honest stock lookup, optionally for one size."""
    product = get_product(product_id)
    if product is None:
        return None
    sizes = product["sizes"]
    if size:
        wanted = size.strip().lower()
        match = next((s for s in sizes if s["size"].lower() == wanted), None)
        return {
            "product_id": product["product_id"],
            "name": product["name"],
            "size": size,
            "quantity": match["quantity"] if match else 0,
            "available": bool(match and match["quantity"] > 0),
        }
    return {
        "product_id": product["product_id"],
        "name": product["name"],
        "sizes": sizes,
        "in_stock": product["in_stock"],
    }
