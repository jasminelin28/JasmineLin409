// api client + shared types for the campus customs frontend

export type ProductSize = { size: string; quantity: number };

export type Product = {
  product_id: string;
  name: string;
  garment_type: string;
  description: string;
  colors: string[];
  search_tags: string[];
  image_url: string;
  price: number;
  sizes?: ProductSize[];
  in_stock?: boolean;
};

export type User = {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
};

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  products?: Product[];
};

export type PageContext = {
  product_id?: string;
  product_name?: string;
  path?: string;
};

const TOKEN_KEY = "campus_customs_token";

export function get_token(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}
export function set_token(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  const token = get_token();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const response = await fetch(path, { ...options, headers });
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* ignore non-json errors */
    }
    throw new Error(detail);
  }
  return (await response.json()) as T;
}

export const api = {
  signup: (data: {
    first_name: string;
    last_name: string;
    email: string;
    password: string;
  }) =>
    request<{ token: string; user: User }>("/api/signup", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  login: (data: { email: string; password: string }) =>
    request<{ token: string; user: User }>("/api/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  me: () => request<{ user: User }>("/api/me"),

  products: () => request<{ products: Product[] }>("/api/products"),

  product: (id: string) =>
    request<{ product: Product }>(`/api/products/${id}`),

  chat_history: () =>
    request<{ messages: ChatMessage[] }>("/api/chat/history"),

  chat: (message: string, context?: PageContext) =>
    request<{ reply: string; products: Product[] }>("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message, context }),
    }),
};
