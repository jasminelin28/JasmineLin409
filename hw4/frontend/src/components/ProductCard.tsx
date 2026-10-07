// a single product tile that links to its detail page
import { Link } from "react-router-dom";
import type { Product } from "../api";

export function ProductCard({ product }: { product: Product }) {
  // trim the description to a short teaser for the card
  const teaser =
    product.description.length > 90
      ? product.description.slice(0, 90).trimEnd() + "..."
      : product.description;

  return (
    <Link
      to={`/products/${product.product_id}`}
      className="product-card"
      title={`View ${product.name}`}
    >
      <div className="product-image">
        <img
          src={product.image_url}
          alt={product.name}
          loading="lazy"
          onError={(e) => {
            // graceful fallback if an image is missing, so cards never show broken icons
            const img = e.currentTarget;
            img.style.display = "none";
            img.parentElement?.classList.add("no-image");
          }}
        />
      </div>
      <div className="product-body">
        <div className="product-name">{product.name}</div>
        <p className="product-teaser">{teaser}</p>
        <div className="product-meta">
          <span className="product-price">${product.price.toFixed(2)}</span>
          <span className="product-type">{product.garment_type}</span>
        </div>
      </div>
    </Link>
  );
}
