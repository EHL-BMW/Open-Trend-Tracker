import type { ImpactCategory, ImpactExploratory, ImpactForecast, ImpactSubcategory } from "../api/types";

type SalesPoint = ImpactCategory["impact_by_year"][number];
export type DemoSales = { points: SalesPoint[]; basis: string; identified: boolean };

// Existing planning assumptions from backend/app/analysis/official_sales.py.
// These fill the demo view when the historical sample has no feature-level curve.
const categoryPrior: Record<string, number> = {
  "Energy & Charging": 4.0,
  "Driving Assistance": 3.6,
  "Digital Cockpit & AI": 3.0,
  "Vehicle Dynamics": 2.7,
  "Smart Cabin": 2.3,
  "Connected Ecosystem": 1.8,
  "Smart Exterior": 1.2,
  "General & Services": 0.8,
};
const saturation = [0.5, 0.72, 0.88, 1];

function planningScenario(category: ImpactCategory, label: string): DemoSales {
  const name = label.toLowerCase();
  const highValue = ["lidar", "autonomous", "driver assistance", "automated", "parking", "aeb", "aes", "charging", "battery", "electric range", "range of", "artificial intelligence", "voice assistant"];
  const presentation = ["paint", "colour", "color", "wheel design", "trim", "appearance"];
  const multiplier = highValue.some((word) => name.includes(word)) ? 1.15 : presentation.some((word) => name.includes(word)) ? 0.8 : 1;
  const year4 = (categoryPrior[category.label] ?? 1) * multiplier;
  return {
    points: saturation.map((factor, index) => ({ year: index + 1, impact_pct: Number((year4 * factor).toFixed(1)) })),
    basis: "Illustrative category prior × feature multiplier × four-year adoption curve; no feature-level sales effect was identified.",
    identified: false,
  };
}

function exploratorySeries(data: ImpactExploratory | null | undefined, id: string, category: string): DemoSales | null {
  const item = data?.items.find((entry) => entry.level === "feature" && entry.id === id && entry.category === category);
  const panel = item?.panels.strict ?? item?.panels.broad;
  if (!panel?.by_year.length) return null;
  return {
    points: panel.by_year.map((point) => ({ year: point.year, impact_pct: point.impact_pct })),
    basis: `Demo assumption: assign the ${item?.panels.strict ? "strict" : "broad"}-panel launch-bundle association to this feature. Other changes in the same vehicle launch may explain part of it.`,
    identified: false,
  };
}

export function legacyDemoSales(data: ImpactForecast | undefined, category: ImpactCategory, feature: ImpactSubcategory["legacy_features"][number]): DemoSales {
  if (feature.impact_by_year.length) return { points: feature.impact_by_year, basis: "Market-adjusted feature-level estimate from Chinese vehicle version pairs.", identified: true };
  return exploratorySeries(data?.exploratory, feature.name, category.label) ?? planningScenario(category, feature.name);
}
