/**
 * The four sources are fixed in the frontend. What lives inside them (filter groups, values,
 * record counts, default weights, trend forecast) comes from the backend catalog.
 */
export const CATEGORY_KEYS = ["sales", "customer", "features", "trends"] as const;
export type CategoryKey = (typeof CATEGORY_KEYS)[number];

/** Sources that carry a weight. Features / Engineering only filters and is shown as context. */
export const WEIGHTED_KEYS = ["sales", "customer", "trends"] as const;
export type WeightedKey = (typeof WEIGHTED_KEYS)[number];

export type LabelPlacement = "left" | "right" | "below";

export interface CategoryMeta {
  key: CategoryKey;
  name: string;
  /** Short label used on recommendation chips. */
  chipLabel: string;
  /** CSS custom property holding the category colour. */
  colorVar: string;
  weighted: boolean;
  /** False for sources whose contribution is a future assumption rather than evidence. */
  evidence: boolean;
  description: string;
  /** Position on the orbit ellipse in % of the orbit box, following the PM universe slide. */
  orbit: { x: number; y: number; label: LabelPlacement };
}

export const CATEGORIES: Record<CategoryKey, CategoryMeta> = {
  sales: {
    key: "sales",
    name: "Sales",
    chipLabel: "Sales",
    colorVar: "--c-sales",
    weighted: true,
    evidence: true,
    description: "Units and option take rates by model line and powertrain.",
    orbit: { x: 71.7, y: 34.8, label: "right" },
  },
  trends: {
    key: "trends",
    name: "Trends / Competition",
    chipLabel: "Trend",
    colorVar: "--c-trends",
    weighted: true,
    evidence: false,
    description:
      "What the bestselling Chinese EVs offer today, and a forecast of how widespread each technology will be. Always an assumption, not evidence.",
    orbit: { x: 62.5, y: 77.1, label: "below" },
  },
  customer: {
    key: "customer",
    name: "Customer",
    chipLabel: "Customer",
    colorVar: "--c-customer",
    weighted: true,
    evidence: true,
    description: "Pain points and praise from customer verbatims and the customer study.",
    orbit: { x: 37.5, y: 77.1, label: "below" },
  },
  features: {
    key: "features",
    name: "Features / Engineering",
    chipLabel: "BMW today",
    colorVar: "--c-features",
    weighted: false,
    evidence: true,
    description:
      "Features available on existing BMW cars today. Filters only: shown as context, not part of the weighting.",
    orbit: { x: 28.3, y: 34.8, label: "left" },
  },
};

/** Order in which sources appear in lists (orbit order follows the slide). */
export const CATEGORY_ORDER: CategoryKey[] = ["sales", "customer", "trends", "features"];

/** Filter group in the Trends catalog whose values match the trend forecast entries. */
export const TREND_TECHNOLOGY_GROUP = "technology";

export const isWeightedKey = (key: CategoryKey): key is WeightedKey =>
  (WEIGHTED_KEYS as readonly string[]).includes(key);

export const categoryColor = (key: CategoryKey) => `var(${CATEGORIES[key].colorVar})`;
