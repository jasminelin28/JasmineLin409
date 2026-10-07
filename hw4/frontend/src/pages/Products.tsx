// products page: catalogue grid, chat-agent matches, plus filter + sort controls
import { useEffect, useMemo, useState } from "react";
import { api, type Product } from "../api";
import { useChatResults } from "../chatResults";
import { ProductCard } from "../components/ProductCard";

type SortKey = "name" | "price-asc" | "price-desc";

export function Products() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [type, setType] = useState<string>("All");
  const [sort, setSort] = useState<SortKey>("name");
  const { products: chatProducts, query: chatQuery, clear } = useChatResults();

  useEffect(() => {
    api
      .products()
      .then((res) => setProducts(res.products))
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Could not load products")
      )
      .finally(() => setLoading(false));
  }, []);

  // the garment types present in the catalogue, for the filter chips
  const types = useMemo(() => {
    const set = new Set(products.map((p) => p.garment_type));
    return ["All", ...Array.from(set).sort()];
  }, [products]);

  const visible = useMemo(() => {
    const text = query.trim().toLowerCase();
    let list = products.filter((p) => {
      if (type !== "All" && p.garment_type !== type) return false;
      if (!text) return true;
      return [p.name, p.garment_type, p.description, p.colors.join(" "), p.search_tags.join(" ")]
        .join(" ")
        .toLowerCase()
        .includes(text);
    });
    list = [...list].sort((a, b) => {
      if (sort === "price-asc") return a.price - b.price;
      if (sort === "price-desc") return b.price - a.price;
      return a.name.localeCompare(b.name);
    });
    return list;
  }, [products, query, type, sort]);

  return (
    <div className="page products">
      {/* dynamic cards the chat agent surfaced */}
      {chatProducts.length > 0 && (
        <section className="chat-matches">
          <div className="chat-matches-head">
            <div>
              <h2>Handsome Dan found these for you</h2>
              {chatQuery && <p className="muted">From your chat: "{chatQuery}"</p>}
            </div>
            <button className="ghost" onClick={clear}>
              Clear
            </button>
          </div>
          <div className="grid">
            {chatProducts.map((p) => (
              <ProductCard key={`chat-${p.product_id}`} product={p} />
            ))}
          </div>
        </section>
      )}

      <div className="products-head">
        <div>
          <h1>Shop Yale merch</h1>
          <p className="muted">{products.length} officially licensed pieces.</p>
        </div>
        <input
          className="search"
          placeholder="Search hoodies, tees, colleges, teams..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>

      {/* filter + sort controls */}
      {!loading && !error && (
        <div className="controls">
          <div className="chips">
            {types.map((t) => (
              <button
                key={t}
                className={`chip${type === t ? " active" : ""}`}
                onClick={() => setType(t)}
              >
                {t === "All" ? "All items" : t}
              </button>
            ))}
          </div>
          <label className="sort">
            Sort:
            <select value={sort} onChange={(e) => setSort(e.target.value as SortKey)}>
              <option value="name">Name (A-Z)</option>
              <option value="price-asc">Price (low to high)</option>
              <option value="price-desc">Price (high to low)</option>
            </select>
          </label>
        </div>
      )}

      {error && <div className="auth-error">{error}</div>}

      {loading ? (
        // skeleton placeholders so the grid does not flash empty
        <div className="grid">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="skeleton-card">
              <div className="skeleton-image" />
              <div className="skeleton-line" />
              <div className="skeleton-line short" />
            </div>
          ))}
        </div>
      ) : (
        !error && (
          <div className="grid">
            {visible.map((p) => (
              <ProductCard key={p.product_id} product={p} />
            ))}
            {visible.length === 0 && (
              <div className="loading">No products match that filter.</div>
            )}
          </div>
        )
      )}
    </div>
  );
}
