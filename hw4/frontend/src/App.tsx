// app shell: nav bar, routed pages, and the floating chat
import { Route, Routes } from "react-router-dom";
import { NavBar } from "./components/NavBar";
import { FloatingChat } from "./components/FloatingChat";
import { Home } from "./pages/Home";
import { Products } from "./pages/Products";
import { ProductDetail } from "./pages/ProductDetail";
import { About } from "./pages/About";
import { Login } from "./pages/Login";
import { Signup } from "./pages/Signup";
import { useAuth } from "./auth";
import "./App.css";

export default function App() {
  const { loading } = useAuth();
  if (loading) return <div className="boot">Loading Campus Customs...</div>;

  return (
    <div className="app">
      <NavBar />
      <main className="content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/products/:productId" element={<ProductDetail />} />
          <Route path="/about" element={<About />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="*" element={<Home />} />
        </Routes>
      </main>
      <footer className="site-footer">
        Campus Customs &middot; 57 Broadway, New Haven CT &middot; Casual comfort,
        classic Bulldog pride.
      </footer>
      <FloatingChat />
    </div>
  );
}
