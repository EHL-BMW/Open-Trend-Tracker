/**
 * Mock database: invented example data in the shape the real backend will hold.
 * Nothing here is shipped in production builds; it only feeds the MSW mock backend.
 */

/** Customer, Product and Sales come from real data (./realData.ts); Trends below stays invented. */
export const DATA_VERSION = "demo-2026-10-v5";
export const FORECAST_YEAR = 2030;
export const DEFAULT_WEIGHTS = { sales: 45, customer: 35, trends: 20 };

export const CANDIDATES: Record<string, string> = {
  c1: "Rear-seat cool box",
  c2: "Fold-down rear screens",
  c3: "Real-world winter range",
  c4: "Faster charging stops",
  c5: "Physical climate controls",
  c6: "Steering & handling feel",
  c7: "Head-up display as standard",
  c8: "Reclining rear lounge seats",
  c9: "Hands-free highway assist",
  c10: "Seat comfort",
  c11: "Wider cargo opening",
  c12: "Conversational AI assistant",
  c13: "Vehicle-to-load power outlet",
  c14: "Automated valet parking",
  c15: "In-car robot companion",
  c16: "Panoramic smart-glass roof",
};
export const POWERTRAINS: [string, string][] = [
  ["BEV", "BEV"],
  ["PHEV", "PHEV"],
];

export const TECHNOLOGIES: [string, string][] = [
  ["rear-fridge", "Rear fridge"],
  ["rear-screens", "Rear entertainment screens"],
  ["zero-gravity-seats", "Zero-gravity rear seats"],
  ["800v-charging", "800V fast charging"],
  ["urban-assisted-driving", "Urban assisted driving"],
  ["ar-hud", "AR head-up display"],
  ["heat-pump-thermal", "Heat-pump thermal management"],
  ["llm-voice-assistant", "LLM voice assistant"],
  ["vehicle-to-load", "Vehicle-to-load"],
  ["automated-valet-parking", "Automated valet parking"],
  ["robot-companion", "In-car robot companion"],
  ["smart-glass-roof", "Smart-glass roof"],
  ["steer-by-wire", "Steer-by-wire"],
  ["solid-state-battery", "Solid-state battery"],
];
/** v = forecast share by FORECAST_YEAR (used for ranking); now = share today. */
export interface TrendRecord {
  c: string;
  v: number;
  now: number;
  technology: string;
}

export const TRENDS: TrendRecord[] = [
  { c: "c1", v: 0.7, now: 0.62, technology: "rear-fridge" },
  { c: "c2", v: 0.68, now: 0.55, technology: "rear-screens" },
  { c: "c8", v: 0.6, now: 0.48, technology: "zero-gravity-seats" },
  { c: "c4", v: 0.88, now: 0.71, technology: "800v-charging" },
  { c: "c9", v: 0.85, now: 0.58, technology: "urban-assisted-driving" },
  { c: "c7", v: 0.66, now: 0.44, technology: "ar-hud" },
  { c: "c3", v: 0.9, now: 0.66, technology: "heat-pump-thermal" },
  { c: "c12", v: 0.92, now: 0.52, technology: "llm-voice-assistant" },
  { c: "c13", v: 0.64, now: 0.47, technology: "vehicle-to-load" },
  { c: "c14", v: 0.58, now: 0.23, technology: "automated-valet-parking" },
  { c: "c15", v: 0.25, now: 0.06, technology: "robot-companion" },
  { c: "c16", v: 0.55, now: 0.31, technology: "smart-glass-roof" },
  { c: "c6", v: 0.3, now: 0.04, technology: "steer-by-wire" },
  { c: "c3", v: 0.35, now: 0.01, technology: "solid-state-battery" },
];

export const labelOf = (list: [string, string][], value: string) => list.find(([v]) => v === value)?.[1] ?? value;
