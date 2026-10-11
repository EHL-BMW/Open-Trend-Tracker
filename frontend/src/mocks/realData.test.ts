import { describe, expect, it } from "vitest";
import { createSettings, toRequest } from "../domain/settings";
import { buildCatalog, runAnalysis } from "./engine";
import raw from "./real-data.json";
import { CUSTOMER, PRODUCT, SALES, SALES_UNITS_TOTAL } from "./realData";

const catalog = buildCatalog();
const request = () => toRequest(createSettings(catalog), catalog, 5);
const sumFor = (c: string, signal: string) =>
  CUSTOMER.filter((r) => r.c === c && r.signal === signal).reduce((s, r) => s + r.v, 0);

describe("real Customer and Product data (china-tech-radar)", () => {
  it("counts each comment once per candidate and signal, matching the approved mapping", () => {
    expect(sumFor("c3", "pain")).toBe(80);
    expect(sumFor("c3", "wants")).toBe(29);
    expect(sumFor("c3", "praise")).toBe(53);
    expect(sumFor("c6", "praise")).toBe(270);
    expect(sumFor("c4", "pain")).toBe(98);
  });

  it("cites a real feedback ID and verbatim for every comment record", () => {
    for (const r of CUSTOMER.filter((x) => x.signal !== "praise")) {
      expect(r.sampleId).toMatch(/^[A-Z0-9]+-\d+/);
      expect(r.sample.length).toBeGreaterThan(0);
    }
  });

  it("offers catalogue features per powertrain", () => {
    const heatPump = PRODUCT.filter((r) => r.feature === "heat-pump");
    expect(heatPump.reduce((s, r) => s + r.count, 0)).toBe(51);
    expect(heatPump.every((r) => r.total > 0 && r.count <= r.total)).toBe(true);
  });

  it("drops product evidence when its area is switched off", () => {
    const req = request();
    req.filters.features.area = ["exterior"];
    const run = runAnalysis(req, "c", "2026-10-11T10:00:00Z");
    for (const rec of run.recommendations)
      for (const item of rec.reasoning.context)
        for (const record of item.records) expect(PRODUCT.find((p) => p.id === record.id)?.area).toBe("exterior");
  });

  it("exposes the new customer and product filters in the catalog", () => {
    expect(catalog.categories.customer.filters.map((g) => g.key)).toEqual(["signal", "domain"]);
    expect(catalog.categories.customer.filters[0]!.options.map((o) => o.value)).toEqual(["pain", "wants", "praise"]);
    expect(catalog.categories.features.filters.map((g) => g.key)).toEqual([
      "area",
      "interior",
      "exterior",
      "drive",
      "powertrain",
    ]);
    expect(catalog.categories.features.filters[0]!.options.map((o) => o.label)).toEqual([
      "Interior",
      "Exterior",
      "Powertrain & charging",
    ]);
  });

  it("marks well-praised candidates as keep and drops customer evidence when its domain is filtered out", () => {
    const run = runAnalysis(request(), "a", "2026-10-11T10:00:00Z");
    const handling = run.recommendations.find((r) => r.id === "c6");
    if (handling) expect(handling.keep).toBe(true);

    const req = request();
    req.filters.customer.domain = ["Smart Cabin"];
    const filtered = runAnalysis(req, "b", "2026-10-11T10:00:00Z");
    for (const rec of filtered.recommendations) {
      const customer = rec.reasoning.contributions.find((c) => c.category === "customer");
      for (const record of customer?.records ?? [])
        expect(CUSTOMER.find((x) => x.id === record.id)?.domain).toBe("Smart Cabin");
    }
  });
  it("derives Sales from catalogue units: each variant once per candidate, revenue = units × list price", () => {
    const catalog = (
      raw as { catalog: { europeUnits: number; basePriceEur: number; heatPump: string; rangeKm: number }[] }
    ).catalog;
    expect(SALES_UNITS_TOTAL).toBe(catalog.reduce((s, v) => s + v.europeUnits, 0));
    // Winter range: variants with a standard heat pump OR at least 500 km range, each counted once.
    const winter = catalog.filter((v) => v.heatPump === "Serienmäßig" || v.rangeKm >= 500);
    const c3 = SALES.filter((r) => r.c === "c3");
    expect(c3.reduce((s, r) => s + r.v, 0)).toBe(winter.reduce((s, v) => s + v.europeUnits, 0));
    expect(c3.reduce((s, r) => s + r.revenueEur, 0)).toBe(
      winter.reduce((s, v) => s + v.europeUnits * v.basePriceEur, 0),
    );
    // Candidates without a catalogue feature have no sales evidence.
    expect(SALES.some((r) => r.c === "c12" || r.c === "c13" || r.c === "c15")).toBe(false);
  });
});
