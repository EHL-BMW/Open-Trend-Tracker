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
  /** Optional: show the group collapsed (expandable) in the source settings panel. */
  collapsible: z.boolean().optional(),
});

export const categoryCatalogSchema = z.object({
  recordCount: z.number().int().nonnegative(),
  filters: z.array(filterGroupSchema),
});

export const technologyForecastSchema = z.object({
  /** Matches an option value of the Trends "technology" filter group. */
  technology: z.string().min(1),
  label: z.string(),
  /** Signed sales impact as a decimal (for example -0.12 means -12%). */
  currentShare: z.number(),
  forecastShare: z.number(),
  impactByYear: z
    .array(
      z.object({
        year: z.number().int().min(1).max(4),
        impact: z.number(),
        pairs: z.number().int().nonnegative(),
      }),
    )
    .optional(),
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
  impactCoverage: z
    .object({
      validPairCount: z.number().int().nonnegative(),
      collectionTarget: z.number().int().positive(),
      independentObservationCount: z.number().int().nonnegative().optional(),
      completeObservationCount: z.number().int().nonnegative().optional(),
      independentNameplateCount: z.number().int().nonnegative().optional(),
      completeNameplateCount: z.number().int().nonnegative().optional(),
    })
    .optional(),
  /** Optional wording for the trend chart; the frontend falls back to the China EV adoption copy. */
  trendForecastLabels: z
    .object({ title: z.string(), description: z.string(), current: z.string(), forecast: z.string() })
    .optional(),
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
  /** Optional link to the source: a news article, an AI Agent problem, or another OpenTT page. */
  url: z.string().optional(),
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
  /** Customers praise it: protect rather than change. Always false while the source is the problem list. */
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

/* ---------- GET /forecast/impact-taxonomy ---------- */

const impactPointSchema = z.object({
  year: z.number().int().min(1).max(4),
  impact_pct: z.number(),
  lower_pct: z.number().optional(),
  upper_pct: z.number().optional(),
  pairs: z.number().int().optional(),
  incremental_units: z.number().int().optional(),
  lower_units: z.number().int().optional(),
  upper_units: z.number().int().optional(),
  observations: z.number().int().nonnegative().optional(),
  nameplates: z.number().int().nonnegative().optional(),
});

const legacyImpactFeatureSchema = z.object({
  name: z.string(),
  category: z.string(),
  subcategory: z.string().optional(),
  models: z.array(z.string()),
  pair_count: z.number().int().nonnegative(),
  independent_count: z.number().int().nonnegative(),
  independent_nameplates: z.number().int().nonnegative(),
  identification_status: z.string(),
  identification_reason: z.string(),
  impact_by_year: z.array(impactPointSchema),
});

const newsImpactFeatureSchema = z.object({
  id: z.string(),
  label: z.string(),
  label_cn: z.string(),
  category: z.string(),
  priority: z.number().nullable(),
  signal: z.string().nullable(),
  momentum_pct_change: z.number().nullable(),
  volume_recent: z.number(),
  breadth_outlets: z.number(),
  headline: z.string(),
  headline_url: z.string(),
});

const impactSubcategorySchema = z.object({
  id: z.string(),
  label: z.string(),
  pair_count: z.number().int().nonnegative().optional(),
  independent_count: z.number().int().nonnegative(),
  independent_nameplates: z.number().int().nonnegative(),
  identification_status: z.string(),
  identification_reason: z.string(),
  impact_by_year: z.array(impactPointSchema).nullable(),
  legacy_features: z.array(legacyImpactFeatureSchema),
  news_features: z.array(newsImpactFeatureSchema),
});

const impactCategorySchema = z.object({
  id: z.string(),
  label: z.string(),
  pair_count: z.number().int().nonnegative().optional(),
  independent_count: z.number().int().nonnegative(),
  independent_nameplates: z.number().int().nonnegative(),
  identification_status: z.string(),
  identification_reason: z.string(),
  impact_by_year: z.array(impactPointSchema),
  subcategories: z.array(impactSubcategorySchema),
});

const exploratoryPointSchema = z.object({
  year: z.number().int().min(1).max(4),
  impact_pct: z.number(),
  lower_pct: z.number(),
  upper_pct: z.number(),
  excludes_zero: z.boolean(),
});

const exploratoryPanelEstimateSchema = z.object({
  nameplates_with: z.number().int().nonnegative(),
  nameplates_without: z.number().int().nonnegative(),
  by_year: z.array(exploratoryPointSchema),
});

/** Bundle-level associations: exploratory, never part of the gated values above. */
const exploratorySchema = z.object({
  panels: z.array(
    z.object({
      id: z.enum(["strict", "broad"]),
      label: z.string(),
      nameplates: z.number().int().nonnegative(),
      description: z.string(),
    }),
  ),
  items: z.array(
    z.object({
      level: z.enum(["category", "subcategory", "feature"]),
      id: z.string(),
      label: z.string(),
      category: z.string(),
      subcategory: z.string(),
      direction: z.enum(["up", "down", "mixed", "single_panel"]),
      panels: z.object({
        strict: exploratoryPanelEstimateSchema.optional(),
        broad: exploratoryPanelEstimateSchema.optional(),
      }),
    }),
  ),
  estimate_count: z.number().int().nonnegative(),
  excludes_zero_count: z.number().int().nonnegative(),
  method: z.string(),
  caveat: z.string(),
});

export const impactForecastSchema = z.object({
  title: z.string(),
  as_of: z.string(),
  horizon_years: z.array(z.number().int()),
  categories: z.array(impactCategorySchema),
  legacy_feature_count: z.number().int(),
  isolated_feature_count: z.number().int().nonnegative(),
  news_feature_count: z.number().int(),
  valid_pair_count: z.number().int().nonnegative(),
  collection_target: z.number().int().positive(),
  independent_observation_count: z.number().int().nonnegative(),
  complete_observation_count: z.number().int().nonnegative(),
  independent_nameplate_count: z.number().int().nonnegative(),
  complete_nameplate_count: z.number().int().nonnegative(),
  method: z.string(),
  status: z.string(),
  caveat: z.string(),
  source_plot: z.string(),
  exploratory: exploratorySchema.nullable().optional(),
});

export const apiErrorBodySchema = z.object({
  error: z.object({
    code: z.string(),
    message: z.string(),
    details: z.unknown().optional(),
  }),
});
