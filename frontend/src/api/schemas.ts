/**
 * The API contract between frontend and backend. These schemas validate every response at
 * runtime, and the TypeScript types in ./types.ts are inferred from them.
 * Human-readable version for the backend team: docs/API.md.
 */
import { z } from "zod";
import { CATEGORY_KEYS, WEIGHTED_KEYS } from "../domain/categories";

export const categoryKeySchema = z.enum(CATEGORY_KEYS);
export const weightedKeySchema = z.enum(WEIGHTED_KEYS);

const share = z.number().min(0).max(1);

const weightsSchema = z.object({
  sales: z.number(),
  customer: z.number(),
  trends: z.number(),
});

const enabledSchema = z.object({
  sales: z.boolean(),
  customer: z.boolean(),
  trends: z.boolean(),
});

/* ---------- GET /catalog ---------- */

export const filterOptionSchema = z.object({
  value: z.string().min(1),
  label: z.string(),
});

export const filterGroupSchema = z.object({
  key: z.string().min(1),
  label: z.string(),
  /** Optional heading shown above the group, e.g. "China EV market". */
  heading: z.string().optional(),
  options: z.array(filterOptionSchema),
});

export const categoryCatalogSchema = z.object({
  recordCount: z.number().int().nonnegative(),
  filters: z.array(filterGroupSchema),
});

export const technologyForecastSchema = z.object({
  /** Matches an option value of the Trends "technology" filter group. */
  technology: z.string().min(1),
  label: z.string(),
  currentShare: share,
  forecastShare: share,
});

export const catalogSchema = z.object({
  dataVersion: z.string(),
  forecastYear: z.number().int(),
  defaultWeights: weightsSchema,
  categories: z.object({
    sales: categoryCatalogSchema,
    customer: categoryCatalogSchema,
    features: categoryCatalogSchema,
    trends: categoryCatalogSchema,
  }),
  trendForecast: z.array(technologyForecastSchema),
});

/* ---------- POST /analyses (request) ---------- */

/** Selected option values per filter group key. An empty array means nothing selected. */
export const filterSelectionSchema = z.record(z.string(), z.array(z.string()));

export const analysisRequestSchema = z.object({
  dataVersion: z.string(),
  topN: z.number().int().min(1).max(20),
  /** Integer percentages over the weighted sources; always sum to 100 (frozen ones included). */
  weights: weightsSchema,
  enabled: enabledSchema,
  filters: z.object({
    sales: filterSelectionSchema,
    customer: filterSelectionSchema,
    features: filterSelectionSchema,
    trends: filterSelectionSchema,
  }),
});

/* ---------- Analysis run (response) ---------- */

export const specSchema = z.object({
  category: categoryKeySchema,
  label: z.string(),
  text: z.string(),
  kind: z.enum(["evidence", "assumption", "context", "missing"]),
});

export const sourceRecordSchema = z.object({
  id: z.string(),
  label: z.string(),
  /** Share of this source's signal for the recommendation (0–1); drives line thickness. */
  share,
});

export const contributionSchema = z.object({
  category: weightedKeySchema,
  points: z.number(),
  categoryScore: z.number(),
  /** Effective weight 0–1. */
  weight: share,
  summary: z.string(),
  records: z.array(sourceRecordSchema),
});

export const contextItemSchema = z.object({
  category: categoryKeySchema,
  summary: z.string(),
  records: z.array(sourceRecordSchema),
});

export const flagSchema = z.object({
  severity: z.enum(["ok", "info", "warning"]),
  message: z.string(),
});

export const reasoningSchema = z.object({
  verdict: z.string(),
  confidence: z.enum(["evidence-led", "mixed", "assumption-led"]),
  evidenceShare: share,
  contributions: z.array(contributionSchema),
  context: z.array(contextItemSchema),
  flags: z.array(flagSchema),
});

export const recommendationSchema = z.object({
  id: z.string(),
  rank: z.number().int().min(1),
  title: z.string(),
  score: z.number(),
  /** Customers praise it: protect rather than change. */
  keep: z.boolean(),
  assumptionShare: share,
  specs: z.array(specSchema),
  reasoning: reasoningSchema,
});

export const analysisRunSchema = z.object({
  id: z.string(),
  createdAt: z.string(),
  fingerprint: z.string(),
  dataVersion: z.string(),
  request: analysisRequestSchema,
  effectiveWeights: weightsSchema,
  recommendations: z.array(recommendationSchema),
});

export const analysisRunSummarySchema = z.object({
  id: z.string(),
  createdAt: z.string(),
  fingerprint: z.string(),
  effectiveWeights: weightsSchema,
  enabled: enabledSchema,
  topTitles: z.array(z.string()),
});

export const runListSchema = z.object({
  items: z.array(analysisRunSummarySchema),
});

export const apiErrorBodySchema = z.object({
  error: z.object({
    code: z.string(),
    message: z.string(),
    details: z.unknown().optional(),
  }),
});
