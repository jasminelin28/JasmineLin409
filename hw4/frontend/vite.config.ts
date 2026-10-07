import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// proxy api + product images to the fastapi backend during development
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // allow serving files when the dev server is launched via a short (8.3) path
    fs: { strict: false },
    proxy: {
      "/api": "http://127.0.0.1:8000",
      "/images": "http://127.0.0.1:8000",
    },
  },
  // `vite preview` serves the built output (no file watcher) - more stable here
  preview: {
    port: 5173,
    proxy: {
      "/api": "http://127.0.0.1:8000",
      "/images": "http://127.0.0.1:8000",
    },
  },
});
