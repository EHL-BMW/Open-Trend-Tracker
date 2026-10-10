import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// /api is served by the FastAPI backend (uvicorn on :8000)
export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": "http://127.0.0.1:8000" } },
});
