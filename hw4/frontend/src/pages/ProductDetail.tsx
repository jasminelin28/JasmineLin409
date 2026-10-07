// single-item page: large image on one side, full product text on the other
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, type Product } from "../api";

export function ProductDetail() {
  const { productId } = useParams<{ productId: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!productId) return;
    setLoading(true);
    api
      .product(productId)
      .then((res) => setProduct(res.product))
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Could not load product")
      )
      .finally(() => setLoading(false));
  }, [productId]);

  if (loading) return <div className="page"><div className="loading">Loading...</div></div>;
  if (error || !product)
    return (
      <div className="page">
        <div className="auth-error">{error || "Product not found."}</div>
        <p>
          <Link to="/products">Back to all products</Link>
        </p>
      </div>
    );

  return (
    <div className="page detail">
      <p className="crumbs">
        <Link to="/products">Products</Link> / {product.name}
      </p>

      <div className="detail-grid">
        <div className="detail-image">
          <img src={product.image_url} alt={product.name} />
        </div>

        <div className="detail-info">
          <h1>{product.name}</h1>
          <div className="detail-price">${product.price.toFixed(2)}</div>
          <p className="detail-type">{product.garment_type}</p>
          <p className="detail-desc">{product.description}</p>

          {product.colors?.length > 0 && (
            <p className="detail-colors">
              <strong>Colors:</strong> {product.colors.join(", ")}
            </p>
          )}

          {product.sizes && product.sizes.length > 0 ? (
            <div className="size-list">
              <strong>Sizes &amp; availability</strong>
              <div className="size-chips">
                {product.sizes.map((s) => (
                  <span
                    key={s.size}
                    className={`size-chip${s.quantity > 0 ? "" : " out"}`}
                    title={s.quantity > 0 ? `${s.quantity} in stock` : "Out of stock"}
                  >
                    {s.size}
                    <em>{s.quantity > 0 ? `${s.quantity} left` : "out"}</em>
                  </span>
                ))}
              </div>
            </div>
          ) : (
            <p className="muted">Size and stock information coming soon.</p>
          )}
        </div>
      </div>
    </div>
  );
}
