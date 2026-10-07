// landing page: banner photo carousel, intro, and a product photo gallery
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type Product } from "../api";
import { Carousel } from "../components/Carousel";

export function Home() {
  const [products, setProducts] = useState<Product[]>([]);

  useEffect(() => {
    api
      .products()
      .then((res) => setProducts(res.products))
      .catch(() => setProducts([]));
  }, []);

  // spread picks across the catalogue so the banner shows variety
  const banner = products
    .filter((_, i) => i % 9 === 0)
    .slice(0, 6)
    .map((p) => ({ image_url: p.image_url, alt: p.name }));

  // a larger set of photos for the shop-the-look gallery
  const gallery = products.slice(0, 18);

  return (
    <div className="home">
      <Carousel slides={banner} />

      <section className="home-intro">
        <h2>Casual comfort, classic Bulldog pride.</h2>
        <p>
          Campus Customs is your New Haven home for Yale apparel and keepsakes. We
          stock the soft, sturdy, true-blue pieces students and alumni actually reach
          for - and our shopping helper, Handsome Dan, can find exactly what you want
          with honest prices and stock.
        </p>
        <Link to="/products" className="btn-link">
          Shop the full collection
        </Link>
      </section>

      <section className="home-gallery">
        <h3>Shop the look</h3>
        <div className="gallery-grid">
          {gallery.map((p) => (
            <Link
              key={p.product_id}
              to={`/products/${p.product_id}`}
              className="gallery-item"
              title={p.name}
            >
              <img src={p.image_url} alt={p.name} loading="lazy" />
              <span className="gallery-caption">
                <span className="gallery-name">{p.name}</span>
                <span className="gallery-price">${p.price.toFixed(2)}</span>
              </span>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
