import { describe, expect, it } from "vitest";
import { createSettings, toRequest } from "../domain/settings";
import { buildCatalog, runAnalysis } from "./engine";

const catalog = buildCatalog();
const baseRequest = () => toRequest(createSettings(catalog), catalog, 5);

describe("mock analysis engine", () => {
  it("is deterministic: same request, same ranking and fingerprint", () => {
    const a = runAnalysis(baseRequest(), "a", "2026-10-11T10:00:00Z");
    const b = runAnalysis(baseRequest(), "b", "2026-10-11T11:00:00Z");
    expect(a.fingerprint).toBe(b.fingerprint);
    expect(a.recommendations.map((r) => r.title)).toEqual(b.recommendations.map((r) => r.title));
  });

  it("returns the requested Top N with ranks and reasoning", () => {
    const run = runAnalysis(baseRequest(), "a", "2026-10-11T10:00:00Z");
    expect(run.recommendations).toHaveLength(5);
    expect(run.recommendations.map((r) => r.rank)).toEqual([1, 2, 3, 4, 5]);
    for (const rec of run.recommendations) {
      expect(rec.reasoning.verdict).toMatch(/^Ranks #\d/);
      expect(rec.reasoning.contributions.length).toBeGreaterThan(0);
    }
  });

  it("never weights Features / Engineering", () => {
    const run = runAnalysis(baseRequest(), "a", "2026-10-11T10:00:00Z");
    for (const rec of run.recommendations) {
      expect(rec.reasoning.contributions.map((c) => c.category)).not.toContain("features");
    }
  });

  it("drops a switched-off source from the score", () => {
    const req = baseRequest();
    req.enabled.trends = false;
    const run = runAnalysis(req, "a", "2026-10-11T10:00:00Z");
    expect(run.effectiveWeights.trends).toBe(0);
    for (const rec of run.recommendations) expect(rec.assumptionShare).toBe(0);
  });
});
