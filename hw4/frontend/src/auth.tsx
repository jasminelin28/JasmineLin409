// authentication context: holds the current user + token across the app
import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { api, get_token, set_token, type User } from "./api";

type AuthState = {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (data: {
    first_name: string;
    last_name: string;
    email: string;
    password: string;
  }) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // restore the session on first load if a token is present
  useEffect(() => {
    const token = get_token();
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .me()
      .then((res) => setUser(res.user))
      .catch(() => set_token(null))
      .finally(() => setLoading(false));
  }, []);

  const login = async (email: string, password: string) => {
    const res = await api.login({ email, password });
    set_token(res.token);
    setUser(res.user);
  };

  const signup = async (data: {
    first_name: string;
    last_name: string;
    email: string;
    password: string;
  }) => {
    const res = await api.signup(data);
    set_token(res.token);
    setUser(res.user);
  };

  const logout = () => {
    set_token(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
