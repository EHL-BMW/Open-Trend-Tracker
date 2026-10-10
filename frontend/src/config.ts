export const config = {
  apiBaseUrl: (import.meta.env.VITE_API_BASE_URL ?? "/api/v1").replace(/\/$/, ""),
  useMocks: import.meta.env.VITE_USE_MOCKS === "true",
  requestTimeoutMs: 20_000,
  /** The PM interview asked for a Top 5; the backend is told explicitly so it never guesses. */
  topN: 5,
  /** Full-screen intro video. Drop the files into public/media/ or point these at a CDN. */
  hero: {
    videoUrl: import.meta.env.VITE_HERO_VIDEO_URL ?? "/media/hero.mp4",
    posterUrl: import.meta.env.VITE_HERO_POSTER_URL ?? "/media/hero-poster.jpg",
  },
} as const;
