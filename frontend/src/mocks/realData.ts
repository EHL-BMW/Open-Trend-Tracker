/**
 * Real Customer, Product and Sales data for the demo backend, from the china-tech-radar module
 * (refresh with `npm run sync:real-data`). Trends stays demo data (see ./data.ts).
 *
 * Customer: bmw_ev_technology_domain_records.csv (individual comments: pain points and wants)
 *           + bmw_ev_technology_sentiment_pipeline.csv (aggregated praise).
 * Product:  bmw_ev_phev_catalog.csv (53 BMW BEV/PHEV variants, public ADAC catalogue data).
 * Sales:    same catalogue: Europe units per variant and list price (revenue = units × list price, an estimate).
 */
import raw from "./real-data.json";

interface RawComment {
  id: string;
  cohort: string;
  powertrain: string;
  country: string;
  type: string;
  domain: string;
  component: string;
  verbatim: string;
}
interface RawPraise {
  domain: string;
  component: string;
  volume: number;
  sample: string;
}
interface RawVariant {
  model: string;
  variant: string;
  powertrain: string;
  europeUnits: number;
  basePriceEur: number;
  heatPump: string;
  dcChargingKw: number;
  headUpDisplay: string;
  audioSystem: string;
  rangeKm: number;
  drivetrain: string;
  accel0to100: number;
  towingKg: number;
  interior: string;
  exterior: string;
  assistance: string;
  highlights: string;
}

const data = raw as { customer: RawComment[]; praise: RawPraise[]; catalog: RawVariant[] };

/* ---------- Approved mapping: candidate → customer components ---------- */

/** Order matters: a comment tagged with several components counts once, for the first match. */
const CUSTOMER_COMPONENTS: Record<string, string[]> = {
  c2: ["Rear seat entertainment"],
  c3: ["Electric Range", "High voltage battery, preconditioning"],
  c4: [
    "Public charging / external providers",
    "Charge high-voltage battery",
    "Charging cable",
    "High-voltage charging power socket",
    "Route optimized for charging",
  ],
  c5: ["Vehicle, climatization", "Air conditioning, setting", "Blower function"],
  c6: ["Handling / Riding", "Drive, driving dynamics and chassis, overall technology", "My Modes / driving experience"],
  c7: ["Head-Up Display"],
  c9: [
    "Highway assistant",
    "Driver assistance, automated driving, overall technology",
    "Steering and lane guide assist",
  ],
  c10: ["Seats", "Seating, ventilate / heat", "Seat memory", "Interior comfort"],
  c11: ["Trunk lid, open / close", "non-contact trunk lid opening", "Luggage compartment", "Frunk"],
  c12: ["Intelligent Personal Assistant"],
  c14: ["Parking Assistant", "Park Distance Control (PDC)"],
  c16: ["Panorama glass roof", "Sun protection"],
};

export type CustomerSignal = "pain" | "wants" | "praise";

export const SIGNALS: [CustomerSignal, string][] = [
  ["pain", "Pain points"],
  ["wants", "Wants"],
  ["praise", "Praise"],
];

/** Defect and Difficult to Use are pain points; Wants are unmet wishes. */
const signalOf = (type: string): CustomerSignal | null =>
  type === "Defect" || type === "Difficult to Use" ? "pain" : type === "Wants" ? "wants" : null;

export interface CustomerRecord {
  id: string;
  c: string;
  /** Comments (pain / wants) or likes (praise) for this candidate, component and signal. */
  v: number;
  signal: CustomerSignal;
  domain: string;
  component: string;
  /** Example comment: its feedback ID (not for aggregated praise) and verbatim. */
  sampleId?: string;
  sample: string;
}

/**
 * Example comment for a record: one whose text actually mentions the component (comments often
 * cover several topics), otherwise the shortest one. Deterministic for the same data.
 */
function pickExample(comments: RawComment[], component: string): RawComment | undefined {
  const words = component
    .toLowerCase()
    .split(/[^a-z]+/)
    .filter((w) => w.length >= 4 && !["overall", "technology", "vehicle", "setting"].includes(w));
  const mentions = comments.filter((r) => words.some((w) => r.verbatim.toLowerCase().includes(w)));
  const pool = mentions.length ? mentions : comments;
  return [...pool].sort((a, b) => a.verbatim.length - b.verbatim.length || a.id.localeCompare(b.id))[0];
}

function buildCustomer(): CustomerRecord[] {
  const out: CustomerRecord[] = [];
  for (const [c, components] of Object.entries(CUSTOMER_COMPONENTS)) {
    const seen = new Set<string>();
    for (const component of components) {
      for (const [signal] of SIGNALS) {
        if (signal === "praise") continue;
        const comments = data.customer
          .filter((r) => r.component === component && signalOf(r.type) === signal && !seen.has(`${r.id}|${signal}`))
          .sort((a, b) => a.id.localeCompare(b.id, "en", { numeric: true }));
        const ids = [...new Set(comments.map((r) => r.id))];
        ids.forEach((id) => seen.add(`${id}|${signal}`));
        const first = pickExample(comments, component);
        if (!first) continue;
        out.push({
          id: "",
          c,
          v: ids.length,
          signal,
          domain: first.domain,
          component,
          sampleId: first.id,
          sample: first.verbatim,
        });
      }
      for (const p of data.praise.filter((r) => r.component === component && r.volume > 0)) {
        out.push({ id: "", c, v: p.volume, signal: "praise", domain: p.domain, component, sample: p.sample });
      }
    }
  }
  return out.map((r, i) => ({ ...r, id: `C-${String(i + 1).padStart(2, "0")}` }));
}

export const CUSTOMER: CustomerRecord[] = buildCustomer();

/** All eight technology domains present in the customer data, most comments first. */
export const DOMAINS: [string, string][] = Object.entries(
  data.customer.reduce<Record<string, number>>((m, r) => ((m[r.domain] = (m[r.domain] ?? 0) + 1), m), {}),
)
  .sort((a, b) => b[1] - a[1])
  .map(([d]) => [d, d]);

/** Distinct comments in the customer file (one comment can be tagged with several components). */
export const CUSTOMER_COMMENT_COUNT = new Set(data.customer.map((r) => r.id)).size;
export const PRAISE_ROW_COUNT = data.praise.length;

/* ---------- Product taxonomy: area → features (and the approved candidate links) ---------- */

export type ProductArea = "interior" | "exterior" | "drive";

/** Interior includes cockpit and driver assistance (operated from the cabin); drive covers powertrain, charging, chassis. */
export const PRODUCT_AREAS: [ProductArea, string][] = [
  ["interior", "Interior"],
  ["exterior", "Exterior"],
  ["drive", "Powertrain & charging"],
];

interface ProductFeature {
  key: string;
  label: string;
  area: ProductArea;
  /** Linked recommendation candidate (approved mapping); unlinked features are filters only. */
  c?: string;
  offers: (v: RawVariant) => boolean;
}

const PRODUCT_FEATURES: ProductFeature[] = [
  // Interior (incl. cockpit and assistance)
  {
    key: "comfort-seats",
    label: "Massage / comfort / climate seats",
    area: "interior",
    c: "c10",
    offers: (v) => /Massage|Komfortsitz|aktiver Klimatisierung/i.test(v.highlights),
  },
  {
    key: "panorama",
    label: "Panorama glass roof",
    area: "interior",
    c: "c16",
    offers: (v) => /Panorama/i.test(v.highlights),
  },
  {
    key: "auto-climate",
    label: "Automatic climate control",
    area: "interior",
    c: "c5",
    offers: (v) => /Klimaautomatik/i.test(v.highlights),
  },
  {
    key: "theatre-screen",
    label: "BMW Theatre Screen",
    area: "interior",
    c: "c2",
    offers: (v) => /Theatre Screen/i.test(v.highlights),
  },
  {
    key: "lounge-seat",
    label: "Executive Lounge seat with recline",
    area: "interior",
    c: "c8",
    offers: (v) => /Liegefunktion/i.test(v.highlights),
  },
  {
    key: "cooled-cupholder",
    label: "Cooled cupholder",
    area: "interior",
    c: "c1",
    offers: (v) => /kühlbar/i.test(v.highlights),
  },
  {
    key: "hud",
    label: "Head-up display",
    area: "interior",
    c: "c7",
    offers: (v) => /head-up|hud/i.test(v.headUpDisplay),
  },
  {
    key: "driving-pro",
    label: "Driving Assistant Professional",
    area: "interior",
    c: "c9",
    offers: (v) => /Autobahnassistent|Driving Assistant Professional/i.test(v.highlights),
  },
  {
    key: "parking-pro",
    label: "Parking Assistant Professional",
    area: "interior",
    c: "c14",
    offers: (v) => /Parking Assistant Professional/i.test(v.highlights),
  },
  {
    key: "surround-view",
    label: "Surround View / 3D View",
    area: "interior",
    c: "c14",
    offers: (v) => /Surround View|3D View|360/i.test(v.assistance),
  },
  {
    key: "curved-display",
    label: "BMW Curved Display",
    area: "interior",
    offers: (v) => /Curved Display/i.test(v.highlights),
  },
  {
    key: "os9",
    label: "BMW Operating System 9",
    area: "interior",
    offers: (v) => /Operating System 9|OS 9/i.test(v.highlights),
  },
  {
    key: "premium-audio",
    label: "Premium audio (Harman Kardon / Bowers & Wilkins)",
    area: "interior",
    offers: (v) => /Harman|Bowers/i.test(v.audioSystem + " " + v.interior),
  },
  {
    key: "ambient",
    label: "Ambient light / Interaction Bar",
    area: "interior",
    offers: (v) => /Ambiente|Interaction Bar/i.test(v.highlights),
  },
  {
    key: "vegan",
    label: "Vegan / sustainable materials",
    area: "interior",
    offers: (v) => /vegan|Veganza|recycel/i.test(v.interior),
  },
  { key: "rear-bench", label: "Rear bench 40:20:40", area: "interior", offers: (v) => /40:20:40/i.test(v.highlights) },
  {
    key: "gaming",
    label: "In-car gaming / streaming",
    area: "interior",
    offers: (v) => /Gaming|AirConsole|Streaming/i.test(v.highlights),
  },
  // Exterior
  {
    key: "auto-tailgate",
    label: "Automatic tailgate",
    area: "exterior",
    c: "c11",
    offers: (v) => /Heckklappe/i.test(v.highlights),
  },
  {
    key: "iconic-glow",
    label: "BMW kidney grille Iconic Glow",
    area: "exterior",
    offers: (v) => /Iconic Glow/i.test(v.highlights),
  },
  {
    key: "adaptive-led",
    label: "Adaptive LED / matrix / laser lights",
    area: "exterior",
    offers: (v) => /Adaptive LED|Matrix|Laser/i.test(v.exterior),
  },
  {
    key: "m-sport",
    label: "M Sport package / Shadow Line",
    area: "exterior",
    offers: (v) => /Shadow Line|M Sportpaket/i.test(v.exterior),
  },
  {
    key: "wheels-20",
    label: "Wheels 20 inch or larger",
    area: "exterior",
    offers: (v) => /\b2[0-3] Zoll/i.test(v.exterior),
  },
  {
    key: "aero",
    label: "Aerodynamics / flush door handles",
    area: "exterior",
    offers: (v) => /Aero|bündig|cW/i.test(v.exterior),
  },
  { key: "towing", label: "Towing capacity 1,500 kg or more", area: "exterior", offers: (v) => v.towingKg >= 1500 },
  // Powertrain & charging
  {
    key: "heat-pump",
    label: "Heat pump (standard)",
    area: "drive",
    c: "c3",
    offers: (v) => v.heatPump === "Serienmäßig",
  },
  { key: "range-500", label: "Range 500 km or more (WLTP)", area: "drive", c: "c3", offers: (v) => v.rangeKm >= 500 },
  { key: "dc-150", label: "DC charging ≥ 150 kW", area: "drive", c: "c4", offers: (v) => v.dcChargingKw >= 150 },
  {
    key: "active-steering",
    label: "Active / sport steering",
    area: "drive",
    c: "c6",
    offers: (v) => /Integral-Aktivlenkung|Sportlenkung|Hinterachslenkung/i.test(v.highlights),
  },
  { key: "awd", label: "All-wheel drive", area: "drive", offers: (v) => v.drivetrain === "AWD" },
  {
    key: "quick-accel",
    label: "0–100 km/h in under 5 s",
    area: "drive",
    offers: (v) => v.accel0to100 > 0 && v.accel0to100 < 5,
  },
];

/** Feature options per area, for the two-level filter. */
export const PRODUCT_FEATURE_GROUPS: { area: ProductArea; options: [string, string][] }[] = PRODUCT_AREAS.map(
  ([area]) => ({
    area,
    options: PRODUCT_FEATURES.filter((f) => f.area === area).map((f) => [f.key, f.label] as [string, string]),
  }),
);

/** Number of catalogue variants offering a feature (for documentation and tests). */
export const productCoverage = (key: string) => {
  const feature = PRODUCT_FEATURES.find((f) => f.key === key);
  return feature ? data.catalog.filter(feature.offers).length : 0;
};

export const PRODUCT_POWERTRAINS: [string, string][] = [
  ["BEV", "BEV"],
  ["PHEV", "PHEV"],
];
export const CATALOG_VARIANT_COUNT = data.catalog.length;

export interface ProductRecord {
  id: string;
  c: string;
  /** Share of this powertrain's variants that offer the feature (0–1). */
  v: number;
  feature: string;
  featureLabel: string;
  area: ProductArea;
  powertrain: string;
  count: number;
  total: number;
  examples: string[];
}

function buildProduct(): ProductRecord[] {
  const out: ProductRecord[] = [];
  for (const f of PRODUCT_FEATURES) {
    if (!f.c) continue; // unlinked features only filter; they have no recommendation to support
    for (const [powertrain] of PRODUCT_POWERTRAINS) {
      const variants = data.catalog.filter((v) => v.powertrain === powertrain);
      const offering = variants.filter(f.offers);
      if (offering.length === 0) continue;
      out.push({
        id: "",
        c: f.c,
        v: offering.length / variants.length,
        feature: f.key,
        featureLabel: f.label,
        area: f.area,
        powertrain,
        count: offering.length,
        total: variants.length,
        examples: [...new Set(offering.map((v) => v.model))].slice(0, 3),
      });
    }
  }
  return out.map((r, i) => ({ ...r, id: `P-${String(i + 1).padStart(2, "0")}` }));
}

export const PRODUCT: ProductRecord[] = buildProduct();

/* ---------- Sales: Europe units of the variants that carry a candidate's linked feature ---------- */

/** Model lines in the catalogue, most units first (the Sales "Line" filter). */
export const SALES_LINES: [string, string][] = Object.entries(
  data.catalog.reduce<Record<string, number>>((m, v) => ((m[v.model] = (m[v.model] ?? 0) + v.europeUnits), m), {}),
)
  .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
  .map(([model]) => [model, model]);

export interface SalesRecord {
  id: string;
  c: string;
  /** Europe units sold of this model and powertrain with the candidate's feature (the Sales signal). */
  v: number;
  model: string;
  powertrain: string;
  variants: number;
  /** Units × list price, in EUR: an estimate, list prices exclude options and discounts. */
  revenueEur: number;
  /** Linked catalogue features these variants carry. */
  features: string[];
}

/**
 * Rule: a candidate's sales exposure is the Europe volume of the BMW variants that carry one of its linked
 * catalogue features today (the buyers it concerns). Each variant counts once per candidate.
 */
function buildSales(): SalesRecord[] {
  const out: SalesRecord[] = [];
  const candidates = [...new Set(PRODUCT_FEATURES.flatMap((f) => (f.c ? [f.c] : [])))];
  for (const c of candidates) {
    const linked = PRODUCT_FEATURES.filter((f) => f.c === c);
    const groups = new Map<string, { variants: RawVariant[]; features: Set<string> }>();
    for (const v of data.catalog) {
      const has = linked.filter((f) => f.offers(v));
      if (has.length === 0) continue;
      const key = v.model + "|" + v.powertrain;
      const g = groups.get(key) ?? { variants: [], features: new Set<string>() };
      g.variants.push(v);
      has.forEach((f) => g.features.add(f.label));
      groups.set(key, g);
    }
    // Highest volume first, so the biggest buyer groups lead the reasoning.
    const units = (g: { variants: RawVariant[] }) => g.variants.reduce((sum, v) => sum + v.europeUnits, 0);
    for (const [key, g] of [...groups].sort((a, b) => units(b[1]) - units(a[1]) || a[0].localeCompare(b[0]))) {
      const [model, powertrain] = key.split("|") as [string, string];
      out.push({
        id: "",
        c,
        v: g.variants.reduce((sum, v) => sum + v.europeUnits, 0),
        model,
        powertrain,
        variants: g.variants.length,
        revenueEur: g.variants.reduce((sum, v) => sum + v.europeUnits * v.basePriceEur, 0),
        features: [...g.features],
      });
    }
  }
  return out.map((r, i) => ({ ...r, id: `S-${String(i + 1).padStart(2, "0")}` }));
}

export const SALES: SalesRecord[] = buildSales();
export const SALES_UNITS_TOTAL = data.catalog.reduce((sum, v) => sum + v.europeUnits, 0);
