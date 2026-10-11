import type { z } from "zod";
import type {
  analysisRequestSchema,
  analysisRunSchema,
  analysisRunSummarySchema,
  catalogSchema,
  categoryCatalogSchema,
  contextItemSchema,
  contributionSchema,
  filterGroupSchema,
  filterSelectionSchema,
  flagSchema,
  recommendationSchema,
  sourceRecordSchema,
  specSchema,
  technologyForecastSchema,
  impactForecastSchema,
} from "./schemas";

export type Catalog = z.infer<typeof catalogSchema>;
export type CategoryCatalog = z.infer<typeof categoryCatalogSchema>;
export type FilterGroup = z.infer<typeof filterGroupSchema>;
export type TechnologyForecast = z.infer<typeof technologyForecastSchema>;
export type FilterSelection = z.infer<typeof filterSelectionSchema>;
export type AnalysisRequest = z.infer<typeof analysisRequestSchema>;
export type Spec = z.infer<typeof specSchema>;
export type SourceRecord = z.infer<typeof sourceRecordSchema>;
export type Contribution = z.infer<typeof contributionSchema>;
export type ContextItem = z.infer<typeof contextItemSchema>;
export type Flag = z.infer<typeof flagSchema>;
export type Recommendation = z.infer<typeof recommendationSchema>;
export type AnalysisRun = z.infer<typeof analysisRunSchema>;
export type AnalysisRunSummary = z.infer<typeof analysisRunSummarySchema>;
export type ImpactForecast = z.infer<typeof impactForecastSchema>;
export type ImpactCategory = ImpactForecast["categories"][number];
export type ImpactSubcategory = ImpactCategory["subcategories"][number];
