# OpenTT – Series Improvement Planner

Tool for BMW product managers to improve an existing model series. The PM chooses which sources inform the decision
(Sales, Customer, Trends / Competition, Features / Engineering), sets their weights and filters, and gets a Top 5 of
recommendations with a traceable reasoning back to the source records.

```
Open-Trend-Tracker/
├── frontend/            React + TypeScript + Vite app
├── docs/PLANNER.md      this guide
├── docs/API.md          API contract the backend has to implement
└── prototype/           original HTML click-prototype
```

The original click-prototype is kept for reference: [`prototype/pm-weighting-mvp.html`](../prototype/pm-weighting-mvp.html).

## How it works

1. **Load**: on start the frontend calls `GET /api/v1/catalog`. Until it answers, the UI shows an empty frame. Filter
   values (lines, powertrains, signals, BMW features, China EV technologies), default weights and the trend forecast
   all come from the backend.
2. **Choose**: the PM clicks a source in the orbit to switch it on or off, set its weight (weights always add up to
   100%; Features / Engineering only filters and is never weighted) or toggle filter values.
3. **Run**: _Run analysis_ (or Ctrl/⌘ + Enter) sends weights, on/off states and filter selections to
   `POST /api/v1/analyses`. The backend scores, stores the run and returns the Top 5 with specs, reasoning, graph data
   and flags. If settings change afterwards, the results are marked outdated until the next run.
4. **Explain**: _Show reasoning_ opens a sheet with the verdict, evidence vs. assumption split, the reasoning graph
   (source records → source × weight → result), every cited record and the signals to check.
5. **Audit**: the run history lists stored runs; _Open_ restores a run's settings and results.

## Frontend

Requirements: Node 20+.

```bash
cd frontend
npm install
npm run dev            # http://localhost:5173 against the built-in mock backend
```

| Command               | What it does                                                              |
| --------------------- | ------------------------------------------------------------------------- |
| `npm run dev`         | Dev server with the mock backend (MSW in the browser), no backend needed  |
| `npm run dev:backend` | Dev server proxying `/api` to `VITE_DEV_BACKEND_URL` (see `.env.backend`) |
| `npm run build`       | Type-check and production build to `dist/` (mocks are not included)       |
| `npm test`            | Unit, component and integration tests (Vitest + Testing Library + MSW)    |
| `npm run lint`        | ESLint                                                                    |
| `npm run format`      | Prettier                                                                  |

### Configuration

| Variable               | Default   | Purpose                                                    |
| ---------------------- | --------- | ---------------------------------------------------------- |
| `VITE_API_BASE_URL`    | `/api/v1` | Base path or absolute URL of the API (build time)          |
| `VITE_USE_MOCKS`       | `false`   | `true` serves the API from the in-browser mock backend     |
| `VITE_DEV_BACKEND_URL` | –         | Dev server only: target for the `/api` proxy               |
| `BACKEND_URL`          | –         | Docker only: where nginx forwards `/api/` (runtime, no rebuild) |

### Pages and navigation

| Path            | Page                                                                        |
| --------------- | --------------------------------------------------------------------------- |
| `/`             | Planner: video intro, sources, weights, recommendations and run history    |
| `/how-it-works` | The method explained for PMs                                                |
| `/faq`          | Placeholder, content to come                                                |
| `/newsletter`   | Placeholder, content to come                                                |

The header follows bmw.de: BMW roundel at the far left, the main links next to it (underlined on the active page),
page actions on the right, and a menu button below 900 px width. Routes are defined in `frontend/src/routes.ts`; add
a page there and in `src/pages/ContentPageRoutes.tsx`. Settings and the current run survive switching pages. Deep
links work in production because nginx falls back to `index.html`.

The roundel files in `frontend/public/brand/` are the official 2020 BMW logo from Wikimedia Commons
(`BMW_logo_(white).svg`, `BMW_logo_(gray).svg`), used unchanged. They are public domain copyright-wise but a BMW
trademark: fine for this internal BMW challenge project, not for presenting OpenTT publicly as an official BMW product.

### Intro video

The page opens with a full-screen intro video; the planner starts below it. The video is fixed:

- `frontend/public/media/hero.mp4`: "BMW M3 Driving on Scenic Street at Dusk" by CALI_ MEDIA _ on Pexels
  (https://www.pexels.com/video/30604039/), 1920×1080, muted loop.
- `frontend/public/media/hero-poster.jpg`: still frame of the same clip, shown before the video loads.

Licence: [Pexels License](https://www.pexels.com/license/), free to use and modify, no attribution required; the clip
may not be sold unaltered. It is not official BMW footage. The video can be paused (button bottom right) and does not
autoplay for users who prefer reduced motion.

### UI components (Vengeance UI)

A few animated components come from [Vengeance UI](https://www.vengenceui.com) (MIT, © Ashutoshx7), copied into
`frontend/src/components/ui/` the shadcn way (we own the code; licence in `LICENSE-vengeance-ui.txt`):

| Component         | Used for                                          |
| ----------------- | ------------------------------------------------- |
| Stagger Text      | "OpenTT" headline and tagline reveal in the intro |
| Animated Button   | "Run analysis" in the header                      |
| Animated Number   | Rolling weight percentage and recommendation scores |
| Glow Border Card  | The top-ranked recommendation                     |
| Animated Tooltip  | Explanations on the evidence chips                |

They need Tailwind CSS v4 (loaded without its CSS reset, so the rest of the app keeps its CSS-Modules styling) and
framer-motion. Motion follows the OS "reduce motion" setting. To add another component, copy it from the site into
`src/components/ui/` and import `cn` from `@/lib/utils`.

### Docker

```bash
cd frontend
docker build -t planner-frontend .
docker run -p 8080:8080 -e BACKEND_URL=http://host.docker.internal:8000 planner-frontend
```

nginx serves the static build, forwards `/api/` to `BACKEND_URL` (same-origin, so no CORS setup is needed), caches
hashed assets for a year and exposes `/healthz`.

### Structure

```
frontend/src/
├── api/          schemas.ts (zod contract), client.ts (fetch, timeouts, errors), endpoints.ts, queries.ts (TanStack Query)
├── domain/       categories.ts (the 4 fixed sources), weights.ts (rebalancing), settings.ts (state → request)
├── state/        PlannerContext.tsx (catalog + settings for the component tree)
├── components/   orbit, inspector, forecast, recommendations, reasoning, runs, layout, common
├── mocks/        mock backend: data.ts, engine.ts (reference scoring), handlers.ts (MSW)
└── styles/       global.css (design tokens, light and dark)
```

## Backend

Not built yet. Implement [`docs/API.md`](API.md); [`frontend/src/mocks/engine.ts`](../frontend/src/mocks/engine.ts) is a working reference for the
scoring, reasoning texts and flags. Switch the frontend over with `npm run dev:backend` (or `VITE_USE_MOCKS=false`).
