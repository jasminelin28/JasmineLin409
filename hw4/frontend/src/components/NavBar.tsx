// no header row: a floating "Y" button in the top-right opens a collapsible menu
import { useEffect, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

export function NavBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  // close the menu on Escape for accessibility
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const close = () => setOpen(false);
  const handleLogout = () => {
    logout();
    close();
    navigate("/");
  };

  return (
    <div className="menu-root">
      <button
        className="menu-button"
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? "Close menu" : "Open menu"}
        aria-expanded={open}
      >
        Y
      </button>

      {open && (
        <>
          <div className="menu-backdrop" onClick={close} />
          <nav className="menu-panel">
            <NavLink to="/" end className="menu-link" onClick={close}>
              Home
            </NavLink>
            <NavLink to="/products" className="menu-link" onClick={close}>
              Products
            </NavLink>
            <NavLink to="/about" className="menu-link" onClick={close}>
              About Us
            </NavLink>
            <div className="menu-divider" />
            {user ? (
              <>
                <span className="menu-greeting">Hi, {user.first_name || "Bulldog"}</span>
                <button className="menu-link as-button" onClick={handleLogout}>
                  Log out
                </button>
              </>
            ) : (
              <>
                <NavLink to="/login" className="menu-link" onClick={close}>
                  Log in
                </NavLink>
                <NavLink to="/signup" className="menu-link accent" onClick={close}>
                  Create account
                </NavLink>
              </>
            )}
          </nav>
        </>
      )}
    </div>
  );
}
