/**
 * Mock implementation of the backend's analysis, ported from the HTML prototype. It produces
 * exactly what the real backend must return (see docs/API.md), so the UI can be built and
 * demoed before the backend exists. Deterministic: same request, same result.
 */
import type {
  AnalysisRequest,
  AnalysisRun,
  Catalog,
  ContextItem,
  Contribution,
  Flag,
  Recommendation,
  Spec,
} from "../api/types";
import { CATEGORIES, WEIGHTED_KEYS, type WeightedKey } from "../domain/categories";
import { requestKey } from "../domain/settings";
import { effectiveWeights } from "../domain/weights";
import {
  CANDIDATES,
  DATA_VERSION,
  DEFAULT_WEIGHTS,
  FORECAST_YEAR,
  POWERTRAINS,
  TECHNOLOGIES,
  TRENDS,
  labelOf,
  type TrendRecord,
} from "./data";
import {
  CATALOG_VARIANT_COUNT,
  CUSTOMER,
  CUSTOMER_COMMENT_COUNT,
  DOMAINS,
  PRAISE_ROW_COUNT,
  PRODUCT,
  PRODUCT_AREAS,
  PRODUCT_FEATURE_GROUPS,
  PRODUCT_POWERTRAINS,
  SALES,
  SALES_LINES,
  type SalesRecord,
  SIGNALS,
  type CustomerRecord,
  type ProductRecord,
} from "./realData";

const options = (list: [string, string][]) => list.map(([value, label]) => ({ value, label }));

export function buildCatalog(): Catalog {
  return {
    dataVersion: DATA_VERSION,
    forecastYear: FORECAST_YEAR,
    defaultWeights: DEFAULT_WEIGHTS,
    categories: {
      sales: {
        recordCount: CATALOG_VARIANT_COUNT,
        filters: [
          { key: "line", label: "Line", options: options(SALES_LINES) },
          { key: "powertrain", label: "Powertrain", options: options(POWERTRAINS) },
        ],
      },
      customer: {
        recordCount: CUSTOMER_COMMENT_COUNT + PRAISE_ROW_COUNT,
        filters: [
          { key: "signal", label: "Signal", options: options(SIGNALS) },
          { key: "domain", label: "Technology domain", options: options(DOMAINS) },
        ],
      },
      features: {
        recordCount: CATALOG_VARIANT_COUNT,
        filters: [
          { key: "area", label: "Area", heading: "BMW BEV/PHEV catalogue", options: options(PRODUCT_AREAS) },
          ...PRODUCT_FEATURE_GROUPS.map((g) => ({
            key: g.area,
            label: labelOf(PRODUCT_AREAS, g.area),
            heading: "Features",
            options: options(g.options),
            collapsible: true,
          })),
          { key: "powertrain", label: "Powertrain", options: options(PRODUCT_POWERTRAINS) },
        ],
      },
      trends: {
        recordCount: TRENDS.length,
        filters: [
          { key: "technology", label: "Technology", heading: "China EV market", options: options(TECHNOLOGIES) },
        ],
      },
    },
    trendForecast: TRENDS.map((t) => ({
      technology: t.technology,
      label: labelOf(TECHNOLOGIES, t.technology),
      currentShare: t.now,
      forecastShare: t.v,
    })),
  };
}

/* ---------- helpers ---------- */

const pc = (v: number) => `${Math.round(v * 100)}%`;
const uniq = (values: string[]) => [...new Set(values)];
const sum = (rows: { v: number }[]) => rows.reduce((s, r) => s + r.v, 0);
const has = (selection: string[] | undefined, value: string) => (selection ?? []).includes(value);

export function fingerprint(req: AnalysisRequest): string {
  const canon = requestKey(req);
  let h = 0x811c9dc5;
  for (let i = 0; i < canon.length; i++) {
    h ^= canon.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h.toString(16).padStart(8, "0");
}

const units = (n: number) => n.toLocaleString("en-US");
const euros = (v: number) => (v >= 1e9 ? `€${(v / 1e9).toFixed(1)} bn` : `€${Math.round(v / 1e6)} m`);
const salesTotals = (rows: SalesRecord[]) => ({
  units: rows.reduce((s, r) => s + r.v, 0),
  revenue: rows.reduce((s, r) => s + r.revenueEur, 0),
});
const salesLabel = (r: SalesRecord) =>
  `${r.model} · ${r.powertrain} · ${r.variants} ${r.variants === 1 ? "variant" : "variants"} · ${units(r.v)} units · ≈ ${euros(r.revenueEur)} est. revenue`;
const quote = (s: string, max = 90) => `“${s.length > max ? `${s.slice(0, max - 1)}…` : s}”`;
const customerLabel = (r: CustomerRecord) =>
  r.signal === "praise"
    ? `${r.component} · Praise · ${r.v} likes · e.g. ${quote(r.sample)}`
    : `${r.component} · ${labelOf(SIGNALS, r.signal)} · ${r.v} ${r.v === 1 ? "comment" : "comments"} · e.g. ${r.sampleId} ${quote(r.sample)}`;
const featureLabel = (r: ProductRecord) =>
  `${r.featureLabel} · on ${r.count} of ${r.total} BMW ${r.powertrain} variants (e.g. ${r.examples.join(", ")})`;
const trendLabel = (r: TrendRecord) =>
  `${labelOf(TECHNOLOGIES, r.technology)} · ${pc(r.now)} today → ${pc(r.v)} ${FORECAST_YEAR}`;

interface WeightedRows {
  sales: SalesRecord[];
  customer: CustomerRecord[];
  trends: TrendRecord[];
}

function painPraise(rows: CustomerRecord[]) {
  return {
    pain: sum(rows.filter((r) => r.signal === "pain")),
    wants: sum(rows.filter((r) => r.signal === "wants")),
    praise: sum(rows.filter((r) => r.signal === "praise")),
  };
}

function phrase(key: WeightedKey, rows: WeightedRows[WeightedKey]): string {
  if (key === "sales") {
    const r = rows as SalesRecord[];
    const t = salesTotals(r);
    return `${units(t.units)} units sold in Europe with ${uniq(r.flatMap((x) => x.features)).join(" / ")} (≈ ${euros(t.revenue)} est. revenue, units × list price)`;
  }
  if (key === "customer") {
    const { pain, wants, praise } = painPraise(rows as CustomerRecord[]);
    return pain + wants >= praise
      ? `${pain} customer pain points and ${wants} wants`
      : `${praise} customer praise mentions`;
  }
  return (rows as TrendRecord[])
    .map(
      (r) =>
        `forecast: ${pc(r.v)} of China EV bestsellers will offer ${labelOf(TECHNOLOGIES, r.technology)} by ${FORECAST_YEAR}, up from ${pc(r.now)} today`,
    )
    .join("; ");
}

const capitalize = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

/* ---------- analysis ---------- */

export function runAnalysis(req: AnalysisRequest, id: string, createdAt: string): AnalysisRun {
  const eff = effectiveWeights(req.weights, req.enabled);
  const f = req.filters;

  const rows: WeightedRows = {
    sales: req.enabled.sales
      ? SALES.filter((r) => has(f.sales.line, r.model) && has(f.sales.powertrain, r.powertrain))
      : [],
    customer: req.enabled.customer
      ? CUSTOMER.filter((r) => has(f.customer.signal, r.signal) && has(f.customer.domain, r.domain))
      : [],
    trends: req.enabled.trends ? TRENDS.filter((r) => has(f.trends.technology, r.technology)) : [],
  };
  // Two-level product filter: the area must be on and the feature selected within it.
  const featureRows = PRODUCT.filter(
    (r) =>
      has(f.features.area, r.area) && has(f.features[r.area], r.feature) && has(f.features.powertrain, r.powertrain),
  );

  const ids = Object.keys(CANDIDATES);
  const raw = Object.fromEntries(
    WEIGHTED_KEYS.map((k) => [k, Object.fromEntries(ids.map((id) => [id, sum(rows[k].filter((r) => r.c === id))]))]),
  ) as Record<WeightedKey, Record<string, number>>;
  const max = Object.fromEntries(WEIGHTED_KEYS.map((k) => [k, Math.max(0, ...Object.values(raw[k]))])) as Record<
    WeightedKey,
    number
  >;

  const rankText = (key: WeightedKey, id: string) => {
    const better = ids.filter((x) => (raw[key][x] ?? 0) > (raw[key][id] ?? 0)).length;
    return better === 0
      ? `the strongest of all ${ids.length} candidates`
      : `#${better + 1} of ${ids.length} candidates`;
  };

  const scored = ids.map((id) => {
    const parts = WEIGHTED_KEYS.map((key) => {
      const own = (rows[key] as { c: string; v: number }[]).filter((r) => r.c === id);
      const categoryScore = max[key] > 0 ? (100 * (raw[key][id] ?? 0)) / max[key] : 0;
      return { key, own, categoryScore, points: eff[key] * categoryScore };
    });
    const total = parts.reduce((s, p) => s + p.points, 0);
    return { id, parts, total };
  });

  // Ties broken by candidate id so the order never depends on runtime quirks.
  scored.sort((a, b) => b.total - a.total || a.id.localeCompare(b.id, "en", { numeric: true }));
  const top = scored.filter((s) => s.total > 0).slice(0, req.topN);

  const recommendations: Recommendation[] = top.map((s, i) => {
    const part = (k: WeightedKey) => s.parts.find((p) => p.key === k)!;
    const custRows = part("customer").own as CustomerRecord[];
    const { pain, wants, praise } = painPraise(custRows);
    const trendPoints = part("trends").points;
    const assumptionShare = s.total > 0 ? trendPoints / s.total : 0;
    const ownFeatures = featureRows.filter((r) => r.c === s.id);

    const contributions: Contribution[] = WEIGHTED_KEYS.filter((k) => req.enabled[k]).map((key) => {
      const p = part(key);
      const total = sum(p.own) || 1;
      const label = (r: unknown) =>
        key === "sales"
          ? salesLabel(r as SalesRecord)
          : key === "customer"
            ? customerLabel(r as CustomerRecord)
            : trendLabel(r as TrendRecord);
      return {
        category: key,
        points: round(p.points),
        categoryScore: round(p.categoryScore),
        weight: eff[key],
        summary: p.own.length
          ? `${capitalize(phrase(key, p.own as never))}: ${rankText(key, s.id)} in this source.`
          : "No matching records, so this source adds nothing.",
        records: p.own.map((r) => ({ id: recordId(key, r), label: label(r), share: r.v / total })),
      };
    });

    const context: ContextItem[] = ownFeatures.length
      ? [
          {
            category: "features",
            summary: `BMW already offers ${ownFeatures.map((r) => `${r.featureLabel} on ${r.count} of ${r.total} ${r.powertrain} variants`).join(", ")} (BMW BEV/PHEV catalogue).`,
            records: ownFeatures.map((r) => ({
              id: recordId("features", r),
              label: featureLabel(r),
              share: 1 / ownFeatures.length,
            })),
          },
        ]
      : [];

    const specs: Spec[] = [];
    for (const key of ["sales", "customer"] as const) {
      if (!req.enabled[key]) continue;
      const own = part(key).own;
      if (!own.length) {
        specs.push({ category: key, label: CATEGORIES[key].chipLabel, text: "No evidence", kind: "missing" });
        continue;
      }
      const text =
        key === "sales"
          ? `${units(salesTotals(own as SalesRecord[]).units)} units · ≈ ${euros(salesTotals(own as SalesRecord[]).revenue)} · ${uniq(
              (own as SalesRecord[]).map((r) => r.model),
            )
              .slice(0, 4)
              .join(", ")}${uniq((own as SalesRecord[]).map((r) => r.model)).length > 4 ? " …" : ""}`
          : [pain && `${pain} pain points`, wants && `${wants} wants`, praise && `${praise} praise`]
              .filter(Boolean)
              .join(" · ") + ` · ${uniq(custRows.map((r) => r.domain)).join(", ")}`;
      specs.push({ category: key, label: CATEGORIES[key].chipLabel, text, kind: "evidence" });
    }
    if (ownFeatures.length) {
      specs.push({
        category: "features",
        label: CATEGORIES.features.chipLabel,
        text: ownFeatures.map((r) => `${r.featureLabel} · ${r.count}/${r.total} ${r.powertrain}`).join(" · "),
        kind: "context",
      });
    }
    const ownTrends = part("trends").own as TrendRecord[];
    if (req.enabled.trends && ownTrends.length) {
      specs.push({
        category: "trends",
        label: CATEGORIES.trends.chipLabel,
        text: ownTrends
          .map((r) => `${labelOf(TECHNOLOGIES, r.technology)} · ${pc(r.now)} → ${pc(r.v)} by ${FORECAST_YEAR}`)
          .join(" · "),
        kind: "assumption",
      });
    }

    const drivers = s.parts.filter((p) => p.points > 0).sort((a, b) => b.points - a.points);
    const lead = drivers[0]!;
    const others = drivers.slice(1);
    let verdict = `Ranks #${i + 1} with ${s.total.toFixed(1)} of 100. The biggest driver is ${CATEGORIES[lead.key].name} (${lead.points.toFixed(1)} pts): ${phrase(lead.key, lead.own as never)}, ${rankText(lead.key, s.id)}.`;
    if (others.length) {
      const list = others
        .map((p) => `${CATEGORIES[p.key].name} (${p.points.toFixed(1)} pts)`)
        .join(", ")
        .replace(/, ([^,]*)$/, " and $1");
      verdict += ` Also supported by ${list}.`;
    }
    verdict +=
      assumptionShare > 0.005
        ? ` ${pc(assumptionShare)} of the score rests on trend assumptions.`
        : " The score rests entirely on evidence.";

    const flags: Flag[] = [];
    if (pain && praise)
      flags.push({
        severity: "warning",
        message: `Mixed customer signal: praised ${praise} times, criticised ${pain} times. Check which markets disagree before changing it.`,
      });
    if (praise > pain)
      flags.push({
        severity: "ok",
        message: "Customers praise this. Protect it in the next update rather than replacing it.",
      });
    for (const key of ["sales", "customer"] as const) {
      if (req.enabled[key] && !part(key).own.length)
        flags.push({
          severity: "warning",
          message: `No ${CATEGORIES[key].name} evidence supports this recommendation.`,
        });
    }
    if (assumptionShare > 0.3)
      flags.push({
        severity: "warning",
        message: "More than 30% of the score comes from trends. Treat it as a hypothesis to validate.",
      });
    if (ownTrends.length)
      flags.push({
        severity: "info",
        message: `The ${FORECAST_YEAR} trend forecast extrapolates today's China EV bestsellers. Preferences differ by climate, use and culture, so validate it for other markets.`,
      });

    return {
      id: s.id,
      rank: i + 1,
      title: CANDIDATES[s.id] ?? s.id,
      score: round(s.total),
      keep: praise > pain,
      assumptionShare,
      specs,
      reasoning: {
        verdict,
        confidence: assumptionShare < 0.2 ? "evidence-led" : assumptionShare < 0.5 ? "mixed" : "assumption-led",
        evidenceShare: 1 - assumptionShare,
        contributions,
        context,
        flags,
      },
    };
  });

  return {
    id,
    createdAt,
    fingerprint: fingerprint(req),
    dataVersion: DATA_VERSION,
    request: req,
    effectiveWeights: eff,
    recommendations,
  };
}

const round = (v: number) => Math.round(v * 10) / 10;

const PREFIX = { trends: "T" } as const;
const TABLES = { trends: TRENDS } as const;
function recordId(key: "sales" | "customer" | "features" | "trends", record: object): string {
  // Real Customer and Product records carry their own stable id (C-.., P-..).
  if (key !== "trends") return (record as { id: string }).id;
  const index = (TABLES[key] as object[]).indexOf(record);
  return `${PREFIX[key]}-${String(index + 1).padStart(2, "0")}`;
}
