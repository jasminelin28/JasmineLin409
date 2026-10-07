// log in page
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

export function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await login(email, password);
      navigate("/products");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not log in");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="page auth-page">
      <div className="auth-card">
        <h1>Welcome back</h1>
        <p className="muted">Log in to shop and chat with Handsome Dan.</p>
        <form onSubmit={submit} className="auth-form">
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {error && <div className="auth-error">{error}</div>}
          <button type="submit" disabled={busy}>
            {busy ? "Please wait..." : "Log in"}
          </button>
        </form>
        <p className="auth-hint">
          New here? <Link to="/signup">Create an account</Link>.
        </p>
      </div>
    </div>
  );
}
