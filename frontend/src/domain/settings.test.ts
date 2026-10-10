import { describe, expect, it } from "vitest";
import { buildCatalog } from "../mocks/engine";
import { createSettings, emptyGroups, filterSummary, requestKey, settingsReducer, toRequest } from "./settings";

const catalog = buildCatalog();

describe("createSettings", () => {
  it("selects every filter value and uses the backend default weights", () => {
    const s = createSettings(catalog);
    expect(s.weights).toEqual({ sales: 45, customer: 35, trends: 20 });
    expect(s.filters.sales.powertrain).toEqual(["BEV", "PHEV"]);
    expect(s.filters.features.feature).toHaveLength(catalog.categories.features.filters[0]!.options.length);
  });
});

describe("settingsReducer", () => {
  it("toggles a filter value off and on", () => {
    let s = createSettings(catalog);
    s = settingsReducer(s, { type: "toggleFilter", category: "sales", group: "powertrain", value: "PHEV" })!;
    expect(s.filters.sales.powertrain).toEqual(["BEV"]);
    s = settingsReducer(s, { type: "toggleFilter", category: "sales", group: "powertrain", value: "PHEV" })!;
    expect(s.filters.sales.powertrain).toEqual(["BEV", "PHEV"]);
  });

  it("restores a stored run but drops values the catalog no longer knows", () => {
    const request = toRequest(createSettings(catalog), catalog, 5);
    request.filters.sales.line = ["i4", "retired-line"];
    request.enabled.trends = false;
    const s = settingsReducer(null, { type: "load", catalog, request })!;
    expect(s.filters.sales.line).toEqual(["i4"]);
    expect(s.enabled.trends).toBe(false);
  });
});

describe("toRequest / requestKey", () => {
  it("gives equal keys for equal settings regardless of selection order", () => {
    const a = createSettings(catalog);
    let b = settingsReducer(a, { type: "toggleFilter", category: "sales", group: "line", value: "i4" })!;
    b = settingsReducer(b, { type: "toggleFilter", category: "sales", group: "line", value: "i4" })!;
    expect(requestKey(toRequest(a, catalog, 5))).toBe(requestKey(toRequest(b, catalog, 5)));
  });

  it("changes the key when a weight changes", () => {
    const a = createSettings(catalog);
    const b = settingsReducer(a, { type: "setWeight", key: "sales", value: 60 })!;
    expect(requestKey(toRequest(a, catalog, 5))).not.toBe(requestKey(toRequest(b, catalog, 5)));
  });
});

describe("filterSummary / emptyGroups", () => {
  const groups = catalog.categories.sales.filters;

  it("summarises the filter state", () => {
    const s = createSettings(catalog);
    expect(filterSummary(groups, s.filters.sales)).toBe("All data");
    expect(filterSummary(groups, { ...s.filters.sales, powertrain: ["BEV"] })).toBe("BEV");
    expect(filterSummary(groups, { ...s.filters.sales, powertrain: [] })).toBe("No powertrain");
  });

  it("reports groups with nothing selected", () => {
    const s = createSettings(catalog);
    expect(emptyGroups(groups, { ...s.filters.sales, line: [] }).map((g) => g.key)).toEqual(["line"]);
  });
});
