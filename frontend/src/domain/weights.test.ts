import { describe, expect, it } from "vitest";
import { apportion, effectiveWeights, normalizeWeights, rebalance, type Enabled, type Weights } from "./weights";

const total = (w: Weights) => w.sales + w.customer + w.trends;
const allOn: Enabled = { sales: true, customer: true, trends: true };

describe("apportion", () => {
  it("splits proportionally into integers with the exact total", () => {
    expect(apportion([1, 1, 1], 100)).toEqual([34, 33, 33]);
    expect(apportion([0, 0], 10)).toEqual([5, 5]);
    expect(apportion([], 100)).toEqual([]);
  });
});

describe("normalizeWeights", () => {
  it("scales backend defaults to integers summing to 100", () => {
    expect(normalizeWeights({ sales: 0.45, customer: 0.35, trends: 0.2 })).toEqual({
      sales: 45,
      customer: 35,
      trends: 20,
    });
    expect(total(normalizeWeights({ sales: 1, customer: 1, trends: 1 }))).toBe(100);
  });

  it("falls back to an equal split when nothing usable arrives", () => {
    expect(normalizeWeights(undefined)).toEqual({ sales: 34, customer: 33, trends: 33 });
  });
});

describe("rebalance", () => {
  const w: Weights = { sales: 45, customer: 35, trends: 20 };

  it("keeps the sum at 100 and scales the others proportionally", () => {
    const next = rebalance(w, allOn, "sales", 70);
    expect(next.sales).toBe(70);
    expect(total(next)).toBe(100);
    expect(next.customer).toBeGreaterThan(next.trends);
  });

  it("leaves switched-off sources frozen", () => {
    const enabled = { ...allOn, trends: false };
    const next = rebalance(w, enabled, "sales", 60);
    expect(next.trends).toBe(20);
    expect(next).toEqual({ sales: 60, customer: 20, trends: 20 });
  });

  it("gives the whole budget to the only active source", () => {
    const next = rebalance(w, { sales: true, customer: false, trends: false }, "sales", 10);
    expect(next.sales).toBe(45);
  });

  it("ignores changes to a switched-off source", () => {
    expect(rebalance(w, { ...allOn, sales: false }, "sales", 90)).toBe(w);
  });

  it("does not drift when dragging from the same base", () => {
    let current = w;
    for (const v of [80, 10, 100, 0, 45]) current = rebalance(current, allOn, "sales", v, w);
    expect(current).toEqual(w);
  });
});

describe("effectiveWeights", () => {
  it("re-normalises active sources and zeroes switched-off ones", () => {
    const eff = effectiveWeights({ sales: 45, customer: 35, trends: 20 }, { ...allOn, trends: false });
    expect(eff.trends).toBe(0);
    expect(eff.sales).toBeCloseTo(45 / 80);
    expect(eff.sales + eff.customer).toBeCloseTo(1);
  });
});
