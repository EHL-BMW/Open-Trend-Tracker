/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Base path or URL of the backend API, e.g. "/api/v1" or "https://planner.example.com/api/v1". */
  readonly VITE_API_BASE_URL?: string;
  /** "true" runs the app against the in-browser mock backend (MSW). */
  readonly VITE_USE_MOCKS?: string;
  /** Dev server only: where /api is proxied to when mocks are off. */
  readonly VITE_DEV_BACKEND_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
