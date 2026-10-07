// shared place for the product matches the chat agent returns, so the chat widget
// can push them and the Products page can render them as cards on the site
import { createContext, useContext, useState, type ReactNode } from "react";
import type { Product } from "./api";

type ChatResultsState = {
  products: Product[];
  query: string | null;
  setResults: (products: Product[], query: string) => void;
  clear: () => void;
};

const ChatResultsContext = createContext<ChatResultsState | undefined>(undefined);

export function ChatResultsProvider({ children }: { children: ReactNode }) {
  const [products, setProducts] = useState<Product[]>([]);
  const [query, setQuery] = useState<string | null>(null);

  const setResults = (next: Product[], q: string) => {
    setProducts(next);
    setQuery(q);
  };
  const clear = () => {
    setProducts([]);
    setQuery(null);
  };

  return (
    <ChatResultsContext.Provider value={{ products, query, setResults, clear }}>
      {children}
    </ChatResultsContext.Provider>
  );
}

export function useChatResults(): ChatResultsState {
  const ctx = useContext(ChatResultsContext);
  if (!ctx) throw new Error("useChatResults must be used within ChatResultsProvider");
  return ctx;
}
