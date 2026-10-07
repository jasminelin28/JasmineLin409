// floating chat bubble in the bottom-right; talks to the backend agent
import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { api, type ChatMessage, type PageContext, type Product } from "../api";
import { useAuth } from "../auth";
import { useChatResults } from "../chatResults";
import danImg from "../assets/handsome-dan.svg";

const GREETING: ChatMessage = {
  role: "assistant",
  content:
    "Hi, I'm Handsome Dan, your Campus Customs shopping helper. Tell me what " +
    "Yale merch you're after - a style, color, team, or college - and I'll " +
    "find it, with honest prices and stock.",
};

export function FloatingChat() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { setResults } = useChatResults();

  // figure out the page context so "do you have this in pink?" knows the item.
  // when on /products/:id (not the grid), pass that product id along.
  const pageContext = (): PageContext => {
    const match = location.pathname.match(/^\/products\/(.+)$/);
    return { path: location.pathname, product_id: match ? match[1] : undefined };
  };
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([GREETING]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // load saved history when a logged-in user opens the chat
  useEffect(() => {
    if (!open || !user) return;
    api
      .chat_history()
      .then((res) => {
        if (res.messages.length > 0) setMessages(res.messages);
      })
      .catch(() => {
        /* no history yet is fine */
      });
  }, [open, user]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages, sending, open]);

  const openProduct = (p: Product) => {
    setOpen(false);
    navigate(`/products/${p.product_id}`);
  };

  const send = async () => {
    const text = input.trim();
    if (!text || sending) return;
    setError(null);
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setSending(true);
    try {
      const res = await api.chat(text, pageContext());
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.reply, products: res.products },
      ]);
      // push the agent's matches onto the page as product cards and show them
      if (res.products.length > 0) {
        setResults(res.products, text);
        navigate("/products");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setSending(false);
    }
  };

  return (
    <>
      {open && (
        <div className="fab-chat">
          <div className="chat-header">
            <img className="chat-dan" src={danImg} alt="Handsome Dan" />
            Ask Dan
            <button
              className="chat-min"
              onClick={() => setOpen(false)}
              aria-label="Minimize chat"
            >
              &minus;
            </button>
          </div>

          <>
              {!user && (
                <div className="chat-guest-note">
                  Chatting as a guest.{" "}
                  <button
                    className="linklike"
                    onClick={() => { setOpen(false); navigate("/login"); }}
                  >
                    Log in
                  </button>{" "}
                  to save your history.
                </div>
              )}
              <div className="chat-messages" ref={scrollRef}>
                {messages.map((m, i) => (
                  <div key={i} className={`bubble ${m.role}`}>
                    <div className="bubble-text">{m.content}</div>
                    {m.products && m.products.length > 0 && (
                      <div className="bubble-products">
                        {m.products.slice(0, 4).map((p) => (
                          <button
                            key={p.product_id}
                            className="mini-product"
                            onClick={() => openProduct(p)}
                            title={p.name}
                          >
                            <img src={p.image_url} alt={p.name} />
                            <span>${p.price.toFixed(2)}</span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
                {sending && (
                  <div className="bubble assistant">
                    <div className="bubble-text typing">Looking that up...</div>
                  </div>
                )}
              </div>

              {error && <div className="chat-error">{error}</div>}

              <div className="chat-input">
                <textarea
                  rows={2}
                  value={input}
                  placeholder="Ask about merch, price, or sizes..."
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      void send();
                    }
                  }}
                />
                <button onClick={() => void send()} disabled={sending || !input.trim()}>
                  Send
                </button>
              </div>
          </>
        </div>
      )}

      <button
        className="fab-launcher"
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? "Close chat" : "Ask Dan"}
        title="Ask Dan"
      >
        <img src={danImg} alt="Handsome Dan" />
        <span>{open ? "Close" : "Ask Dan"}</span>
      </button>
    </>
  );
}
