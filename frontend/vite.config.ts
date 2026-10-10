import { rmSync } from "node:fs";
import { resolve } from "node:path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { loadEnv, type Plugin } from "vite";
import { defineConfig } from "vitest/config";

// The MSW service worker lives in public/ for development; production bundles must not ship it.
function dropMockWorker(enabled: boolean): Plugin {
  return {
    name: "drop-mock-worker",
    apply: "build",
    closeBundle() {
      if (enabled) rmSync(resolve(__dirname, "dist/mockServiceWorker.js"), { force: true });
    },
  };
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const backend = env.VITE_DEV_BACKEND_URL;

  return {
    plugins: [react(), tailwindcss(), dropMockWorker(env.VITE_USE_MOCKS !== "true")],
    resolve: { alias: { "@": resolve(__dirname, "src") } },
    server: {
      port: 5173,
      proxy: backend ? { "/api": { target: backend, changeOrigin: true } } : undefined,
    },
    test: {
      environment: "jsdom",
      setupFiles: ["./src/test/setup.ts"],
      css: { modules: { classNameStrategy: "non-scoped" } },
      restoreMocks: true,
    },
  };
});
