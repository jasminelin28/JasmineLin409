// create account page
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

export function Signup() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    setError(null);
    setBusy(true);
    try {
      await signup({
        first_name: firstName,
        last_name: lastName,
        email,
        password,
      });
      navigate("/products");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create account");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="page auth-page">
      <div className="auth-card">
        <h1>Create your account</h1>
        <p className="muted">Join Campus Customs to shop and chat.</p>
        <form onSubmit={submit} className="auth-form">
          <div className="row">
            <div>
              <label>First name</label>
              <input
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                required
              />
            </div>
            <div>
              <label>Last name</label>
              <input
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                required
              />
            </div>
          </div>
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <label>Password (at least 6 characters)</label>
          <input
            type="password"
            value={password}
            minLength={6}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <label>Confirm password</label>
          <input
            type="password"
            value={confirm}
            minLength={6}
            onChange={(e) => setConfirm(e.target.value)}
            required
          />
          {error && <div className="auth-error">{error}</div>}
          <button type="submit" disabled={busy}>
            {busy ? "Please wait..." : "Create account"}
          </button>
        </form>
        <p className="auth-hint">
          Already have an account? <Link to="/login">Log in</Link>.
        </p>
      </div>
    </div>
  );
}
