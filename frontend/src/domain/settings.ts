import type { AnalysisRequest, Catalog, FilterGroup, FilterSelection } from "../api/types";
import { CATEGORY_KEYS, WEIGHTED_KEYS, type CategoryKey, type WeightedKey } from "./categories";
import { normalizeWeights, rebalance, type Enabled, type Weights } from "./weights";

/** Everything the PM controls before running an analysis. */
export interface Settings {
  weights: Weights;
  enabled: Enabled;
  filters: Record<CategoryKey, FilterSelection>;
  /** Weights when the current slider drag started; avoids rounding drift while dragging. */
  dragBase: Weights | null;
}

export type SettingsAction =
  | { type: "init"; catalog: Catalog }
  | { type: "reset"; catalog: Catalog }
  | { type: "load"; catalog: Catalog; request: AnalysisRequest }
  | { type: "beginWeightDrag" }
  | { type: "endWeightDrag" }
  | { type: "setWeight"; key: WeightedKey; value: number }
  | { type: "setEnabled"; key: WeightedKey; enabled: boolean }
  | { type: "toggleFilter"; category: CategoryKey; group: string; value: string }
  | { type: "selectAll"; category: CategoryKey; group: string; catalog: Catalog };

const allEnabled = (): Enabled => Object.fromEntries(WEIGHTED_KEYS.map((k) => [k, true])) as Enabled;

/** Default: every option of every filter group selected ("everything on"). */
function allSelected(catalog: Catalog): Record<CategoryKey, FilterSelection> {
  return Object.fromEntries(
    CATEGORY_KEYS.map((key) => [
      key,
      Object.fromEntries(catalog.categories[key].filters.map((g) => [g.key, g.options.map((o) => o.value)])),
    ]),
  ) as Record<CategoryKey, FilterSelection>;
}

export function createSettings(catalog: Catalog): Settings {
  return {
    weights: normalizeWeights(catalog.defaultWeights),
    enabled: allEnabled(),
    filters: allSelected(catalog),
    dragBase: null,
  };
}

/** Restores the settings of a stored run, dropping values the current catalog no longer has. */
function fromRequest(catalog: Catalog, request: AnalysisRequest): Settings {
  const filters = allSelected(catalog);
  for (const key of CATEGORY_KEYS) {
    for (const group of catalog.categories[key].filters) {
      const stored = request.filters[key]?.[group.key];
      if (!stored) continue;
      const known = new Set(group.options.map((o) => o.value));
      filters[key][group.key] = stored.filter((v) => known.has(v));
    }
  }
  return {
    weights: normalizeWeights(request.weights),
    enabled: { ...request.enabled },
    filters,
    dragBase: null,
  };
}

export function settingsReducer(state: Settings | null, action: SettingsAction): Settings | null {
  switch (action.type) {
    case "init":
      return state ?? createSettings(action.catalog);
    case "reset":
      return createSettings(action.catalog);
    case "load":
      return fromRequest(action.catalog, action.request);
  }
  if (!state) return state;

  switch (action.type) {
    case "beginWeightDrag":
      return state.dragBase ? state : { ...state, dragBase: { ...state.weights } };
    case "endWeightDrag":
      return state.dragBase ? { ...state, dragBase: null } : state;
    case "setWeight":
      return {
        ...state,
        weights: rebalance(state.weights, state.enabled, action.key, action.value, state.dragBase ?? undefined),
      };
    case "setEnabled":
      return { ...state, enabled: { ...state.enabled, [action.key]: action.enabled } };
    case "toggleFilter": {
      const current = state.filters[action.category][action.group] ?? [];
      const next = current.includes(action.value)
        ? current.filter((v) => v !== action.value)
        : [...current, action.value];
      return withGroup(state, action.category, action.group, next);
    }
    case "selectAll": {
      const group = action.catalog.categories[action.category].filters.find((g) => g.key === action.group);
      return group
        ? withGroup(
            state,
            action.category,
            action.group,
            group.options.map((o) => o.value),
          )
        : state;
    }
  }
}

const withGroup = (state: Settings, category: CategoryKey, group: string, values: string[]): Settings => ({
  ...state,
  filters: { ...state.filters, [category]: { ...state.filters[category], [group]: values } },
});

/** The payload sent to POST /analyses. Arrays are sorted so equal settings give equal requests. */
export function toRequest(settings: Settings, catalog: Catalog, topN: number): AnalysisRequest {
  const filters = Object.fromEntries(
    CATEGORY_KEYS.map((key) => [
      key,
      Object.fromEntries(
        catalog.categories[key].filters.map((g) => [g.key, [...(settings.filters[key][g.key] ?? [])].sort()]),
      ),
    ]),
  ) as AnalysisRequest["filters"];
  return {
    dataVersion: catalog.dataVersion,
    topN,
    weights: { ...settings.weights },
    enabled: { ...settings.enabled },
    filters,
  };
}

/** Stable key for comparing two requests (e.g. "settings changed since the last run"). */
export function requestKey(request: AnalysisRequest): string {
  const sortedFilters = Object.fromEntries(
    CATEGORY_KEYS.map((key) => {
      const groups = request.filters[key] ?? {};
      return [
        key,
        Object.fromEntries(
          Object.keys(groups)
            .sort()
            .map((g) => [g, [...(groups[g] ?? [])].sort()]),
        ),
      ];
    }),
  );
  return JSON.stringify({
    d: request.dataVersion,
    n: request.topN,
    w: WEIGHTED_KEYS.map((k) => request.weights[k]),
    e: WEIGHTED_KEYS.map((k) => request.enabled[k]),
    f: sortedFilters,
  });
}

export const selectedValues = (settings: Settings, category: CategoryKey, group: string) =>
  settings.filters[category][group] ?? [];

/** Short description of a source's filter state for the orbit, e.g. "BEV" or "6 of 9 lines". */
export function filterSummary(groups: FilterGroup[], selection: FilterSelection): string {
  if (groups.length === 0) return "No filters";
  const parts = groups
    .map((g) => {
      const selected = selection[g.key] ?? [];
      if (selected.length === g.options.length) return null;
      if (selected.length === 0) return `No ${g.label.toLowerCase()}`;
      if (selected.length <= 2) {
        return g.options
          .filter((o) => selected.includes(o.value))
          .map((o) => o.label)
          .join(" + ");
      }
      return `${selected.length} of ${g.options.length} ${g.label.toLowerCase()}`;
    })
    .filter(Boolean);
  return parts.length ? parts.join(" · ") : "All data";
}

/** Groups in which nothing is selected; such a source contributes nothing. */
export const emptyGroups = (groups: FilterGroup[], selection: FilterSelection) =>
  groups.filter((g) => g.options.length > 0 && (selection[g.key] ?? []).length === 0);
