import { delay, http, HttpResponse } from "msw";
import { apiUrl } from "../api/client";
import { analysisRequestSchema } from "../api/schemas";
import type { AnalysisRun, AnalysisRunSummary } from "../api/types";
import { DATA_VERSION } from "./data";
import { buildCatalog, runAnalysis } from "./engine";

/** In-memory run store, standing in for the backend database. */
const db = { runs: [] as AnalysisRun[] };
export const resetMockDb = () => {
  db.runs = [];
};

const latency = (ms: number) => delay(import.meta.env.MODE === "test" ? 0 : ms);

const error = (status: number, code: string, message: string, details?: unknown) =>
  HttpResponse.json({ error: { code, message, details } }, { status });

const summarize = (run: AnalysisRun): AnalysisRunSummary => ({
  id: run.id,
  createdAt: run.createdAt,
  fingerprint: run.fingerprint,
  effectiveWeights: run.effectiveWeights,
  enabled: run.request.enabled,
  topTitles: run.recommendations.map((r) => r.title),
});

export const handlers = [
  http.get(apiUrl("/catalog"), async () => {
    await latency(400);
    return HttpResponse.json(buildCatalog());
  }),

  http.get(apiUrl("/forecast/impact-taxonomy"), () =>
    HttpResponse.json({
      title: "Historical sales evidence",
      as_of: "",
      horizon_years: [1, 2, 3, 4],
      categories: [],
      legacy_feature_count: 0,
      isolated_feature_count: 0,
      news_feature_count: 0,
      valid_pair_count: 0,
      collection_target: 200,
      independent_observation_count: 0,
      complete_observation_count: 0,
      independent_nameplate_count: 0,
      complete_nameplate_count: 0,
      method: "Mock mode has no paired vehicle sample.",
      status: "unavailable",
      caveat: "Historical sales evidence requires the backend data.",
      source_plot: "",
    }),
  ),

  http.post(apiUrl("/analyses"), async ({ request }) => {
    await latency(700);
    const parsed = analysisRequestSchema.safeParse(await request.json().catch(() => null));
    if (!parsed.success) return error(400, "invalid_request", "The analysis request is invalid.", parsed.error.issues);
    if (parsed.data.dataVersion !== DATA_VERSION) {
      return error(409, "stale_data_version", "The data was updated. Reload the page to get the latest filters.");
    }
    const run = runAnalysis(parsed.data, crypto.randomUUID(), new Date().toISOString());
    db.runs.unshift(run);
    return HttpResponse.json(run, { status: 201 });
  }),

  http.get(apiUrl("/analyses"), async ({ request }) => {
    await latency(250);
    const limit = Math.min(100, Math.max(1, Number(new URL(request.url).searchParams.get("limit")) || 20));
    return HttpResponse.json({ items: db.runs.slice(0, limit).map(summarize) });
  }),

  http.get(apiUrl("/analyses/:id"), async ({ params }) => {
    await latency(250);
    const run = db.runs.find((r) => r.id === params.id);
    return run ? HttpResponse.json(run) : error(404, "not_found", "That run doesn't exist.");
  }),
];
