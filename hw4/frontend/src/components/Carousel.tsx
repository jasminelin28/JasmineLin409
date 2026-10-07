// banner photo carousel for the landing page
import { useEffect, useState } from "react";

type Slide = { image_url: string; alt: string };

export function Carousel({ slides }: { slides: Slide[] }) {
  const [index, setIndex] = useState(0);

  // auto-advance every 4 seconds
  useEffect(() => {
    if (slides.length <= 1) return;
    const timer = setInterval(() => {
      setIndex((i) => (i + 1) % slides.length);
    }, 4000);
    return () => clearInterval(timer);
  }, [slides.length]);

  if (slides.length === 0) return <div className="carousel carousel-empty" />;

  const go = (next: number) =>
    setIndex((next + slides.length) % slides.length);

  return (
    <div className="carousel">
      {slides.map((s, i) => (
        <div
          key={i}
          className={`carousel-slide${i === index ? " active" : ""}`}
          aria-hidden={i !== index}
        >
          <img src={s.image_url} alt={s.alt} />
        </div>
      ))}

      <div className="carousel-overlay">
        <p className="eyebrow">Officially licensed Yale gear</p>
        <h1>Wear your Bulldog pride, every day.</h1>
        <p className="lead">
          Game-day hoodies, residential-college classics, and true-blue staples -
          straight from our New Haven shop.
        </p>
      </div>

      {slides.length > 1 && (
        <>
          <button
            className="carousel-nav prev"
            onClick={() => go(index - 1)}
            aria-label="Previous slide"
          >
            &#8249;
          </button>
          <button
            className="carousel-nav next"
            onClick={() => go(index + 1)}
            aria-label="Next slide"
          >
            &#8250;
          </button>
          <div className="carousel-dots">
            {slides.map((_, i) => (
              <button
                key={i}
                className={`carousel-dot${i === index ? " active" : ""}`}
                onClick={() => setIndex(i)}
                aria-label={`Go to slide ${i + 1}`}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
