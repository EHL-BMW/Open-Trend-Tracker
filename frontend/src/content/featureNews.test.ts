import { describe, expect, it } from "vitest";
import {
  FEATURE_CATEGORIES,
  brandStats,
  featureClusters,
  featureNewsItems,
  featureNewsMeta,
} from "./featureNews";

describe("feature news preprocessing", () => {
  it("labels every captured item with a feature category", () => {
    expect(featureNewsItems.length).toBeGreaterThan(100);
    for (const item of featureNewsItems) {
      expect(item.featureId).toBeTruthy();
      expect(item.featureLabel).toBeTruthy();
      expect(FEATURE_CATEGORIES).toContain(item.category);
      expect(item.brands).not.toContain("Industry / Multi-brand");
    }
  });

  it("keeps every item reachable from a feature cluster", () => {
    const clusteredIds = new Set(featureClusters.flatMap((feature) => feature.items.map((item) => item.id)));
    expect(clusteredIds.size).toBe(featureNewsItems.length);
    expect(featureNewsMeta.itemCount).toBe(featureNewsItems.length);
  });

  it("translates every Chinese headline and names OEMs", () => {
    for (const item of featureNewsItems.filter((news) => /[\u4e00-\u9fff]/.test(news.title))) {
      expect(item.titleEn).toBeTruthy();
    }

    expect(brandStats.length).toBeGreaterThan(5);
    expect(brandStats[0]?.count).toBeGreaterThan(0);
  });
});

