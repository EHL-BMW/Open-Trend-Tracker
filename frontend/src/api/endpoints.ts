import { request } from "./client";
import { analysisRunSchema, catalogSchema, impactForecastSchema, runListSchema } from "./schemas";
import type { AnalysisRequest } from "./types";

export const api = {
  /** Filter groups and values per source, default weights and the trend forecast. */
  getCatalog: (signal?: AbortSignal) => request("/catalog", catalogSchema, { signal }),

  /** Runs the analysis on the backend and stores it as a run (audit trail). */
  runAnalysis: (body: AnalysisRequest) => request("/analyses", analysisRunSchema, { method: "POST", body }),

  /** Most recent runs first. */
  listRuns: (limit: number, signal?: AbortSignal) => request(`/analyses?limit=${limit}`, runListSchema, { signal }),

  getRun: (id: string, signal?: AbortSignal) =>
    request(`/analyses/${encodeURIComponent(id)}`, analysisRunSchema, { signal }),

  getImpactForecast: (signal?: AbortSignal) => request("/forecast/impact-taxonomy", impactForecastSchema, { signal }),
};
