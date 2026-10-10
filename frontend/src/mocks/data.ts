/**
 * Mock database: invented example data in the shape the real backend will hold.
 * Nothing here is shipped in production builds; it only feeds the MSW mock backend.
 */

export const DATA_VERSION = "mock-2026-10-v3";
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

export const LINES: [string, string][] = [
  ["1-series", "1 Series"],
  ["3-series", "3 Series"],
  ["5-series", "5 Series"],
  ["x1", "X1"],
  ["x3", "X3"],
  ["x5", "X5"],
  ["i4", "i4"],
  ["i5", "i5"],
  ["ix", "iX"],
];

export const POWERTRAINS: [string, string][] = [
  ["BEV", "BEV"],
  ["PHEV", "PHEV"],
];

export const SIGNALS: [string, string][] = [
  ["pain", "Pain points"],
  ["praise", "Praise"],
];

export const BMW_FEATURES: [string, string][] = [
  ["heat-pump", "Heat pump"],
  ["hpc-charging", "High-power DC charging"],
  ["touch-climate", "Touch climate panel"],
  ["adaptive-m-suspension", "Adaptive M suspension"],
  ["head-up-display", "Head-up display"],
  ["driving-assistant-pro", "Driving Assistant Professional"],
  ["comfort-seats", "Comfort seats"],
  ["auto-tailgate", "Automatic tailgate"],
  ["theatre-screen", "Theatre Screen"],
  ["parking-assistant-pro", "Parking Assistant Professional"],
  ["personal-assistant", "Intelligent Personal Assistant"],
  ["panorama-roof", "Panorama glass roof"],
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

export interface SalesRecord {
  c: string;
  v: number;
  line: string;
  powertrain: string;
}
export interface CustomerRecord {
  c: string;
  v: number;
  signal: string;
  market: string;
  area: string;
}
export interface FeatureRecord {
  c: string;
  v: number;
  feature: string;
  offer: string;
}
/** v = forecast share by FORECAST_YEAR (used for ranking); now = share today. */
export interface TrendRecord {
  c: string;
  v: number;
  now: number;
  technology: string;
}

const S = (c: string, v: number, line: string, powertrain: string): SalesRecord => ({ c, v, line, powertrain });
const C = (c: string, v: number, signal: string, market: string, area: string): CustomerRecord => ({
  c,
  v,
  signal,
  market,
  area,
});

export const SALES: SalesRecord[] = [
  S("c3", 0.8, "i4", "BEV"),
  S("c3", 0.9, "ix", "BEV"),
  S("c3", 0.6, "i5", "BEV"),
  S("c3", 0.3, "x5", "PHEV"),
  S("c4", 0.7, "i4", "BEV"),
  S("c4", 0.5, "i5", "BEV"),
  S("c4", 0.8, "ix", "BEV"),
  S("c1", 0.6, "ix", "BEV"),
  S("c1", 0.4, "x5", "PHEV"),
  S("c2", 0.7, "5-series", "PHEV"),
  S("c2", 0.5, "i5", "BEV"),
  S("c5", 0.3, "3-series", "PHEV"),
  S("c5", 0.2, "x1", "PHEV"),
  S("c6", 0.6, "3-series", "PHEV"),
  S("c6", 0.7, "i4", "BEV"),
  S("c6", 0.3, "x3", "PHEV"),
  S("c7", 0.5, "x3", "PHEV"),
  S("c7", 0.4, "i4", "BEV"),
  S("c8", 0.6, "5-series", "PHEV"),
  S("c8", 0.4, "ix", "BEV"),
  S("c9", 0.6, "i5", "BEV"),
  S("c9", 0.4, "x5", "PHEV"),
  S("c10", 0.5, "5-series", "PHEV"),
  S("c10", 0.4, "x5", "PHEV"),
  S("c11", 0.3, "x1", "PHEV"),
  S("c11", 0.2, "1-series", "PHEV"),
  S("c12", 0.3, "i5", "BEV"),
  S("c16", 0.4, "ix", "BEV"),
  S("c16", 0.3, "x5", "PHEV"),
];

export const CUSTOMER: CustomerRecord[] = [
  C("c5", 42, "pain", "DE", "Interior"),
  C("c5", 30, "pain", "US", "Interior"),
  C("c5", 12, "pain", "CN", "Interior"),
  C("c3", 55, "pain", "DE", "Powertrain"),
  C("c3", 25, "pain", "US", "Powertrain"),
  C("c3", 18, "pain", "CN", "Powertrain"),
  C("c4", 28, "pain", "DE", "Powertrain"),
  C("c4", 20, "pain", "CN", "Powertrain"),
  C("c6", 60, "praise", "DE", "Powertrain"),
  C("c6", 40, "praise", "US", "Powertrain"),
  C("c10", 35, "praise", "DE", "Interior"),
  C("c10", 30, "praise", "US", "Interior"),
  C("c10", 20, "praise", "CN", "Interior"),
  C("c1", 15, "pain", "CN", "Interior"),
  C("c2", 22, "pain", "CN", "Interior"),
  C("c2", 8, "pain", "US", "Interior"),
  C("c7", 18, "praise", "DE", "Assistance"),
  C("c7", 14, "pain", "US", "Assistance"),
  C("c8", 25, "pain", "CN", "Interior"),
  C("c9", 26, "pain", "US", "Assistance"),
  C("c9", 12, "pain", "DE", "Assistance"),
  C("c11", 16, "pain", "DE", "Exterior"),
  C("c11", 10, "pain", "US", "Exterior"),
  C("c12", 24, "pain", "CN", "Interior"),
  C("c12", 11, "pain", "DE", "Interior"),
  C("c14", 9, "pain", "CN", "Assistance"),
  C("c16", 12, "praise", "DE", "Interior"),
];

/** v = take rate on existing BMW cars (context only, never weighted). */
export const FEATURES: FeatureRecord[] = [
  { c: "c3", v: 0.64, feature: "heat-pump", offer: "Standard on BEV" },
  { c: "c4", v: 0.58, feature: "hpc-charging", offer: "Standard on BEV" },
  { c: "c5", v: 0.92, feature: "touch-climate", offer: "Standard" },
  { c: "c6", v: 0.31, feature: "adaptive-m-suspension", offer: "Option" },
  { c: "c7", v: 0.44, feature: "head-up-display", offer: "Option" },
  { c: "c9", v: 0.27, feature: "driving-assistant-pro", offer: "Option" },
  { c: "c10", v: 0.38, feature: "comfort-seats", offer: "Option" },
  { c: "c11", v: 0.71, feature: "auto-tailgate", offer: "Standard" },
  { c: "c2", v: 0.06, feature: "theatre-screen", offer: "Option (7 Series only)" },
  { c: "c14", v: 0.22, feature: "parking-assistant-pro", offer: "Option" },
  { c: "c12", v: 0.81, feature: "personal-assistant", offer: "Standard" },
  { c: "c16", v: 0.35, feature: "panorama-roof", offer: "Option" },
];

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
