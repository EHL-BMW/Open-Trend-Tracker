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
  BMW_FEATURES,
  CANDIDATES,
  CUSTOMER,
  DATA_VERSION,
  DEFAULT_WEIGHTS,
  FEATURES,
  FORECAST_YEAR,
  LINES,
  POWERTRAINS,
  SALES,
  SIGNALS,
  TECHNOLOGIES,
  TRENDS,
  labelOf,
  type CustomerRecord,
  type FeatureRecord,
  type SalesRecord,
  type TrendRecord,
} from "./data";

const options = (list: [string, string][]) => list.map(([value, label]) => ({ value, label }));

export function buildCatalog(): Catalog {
  return {
    dataVersion: DATA_VERSION,
    forecastYear: FORECAST_YEAR,
    defaultWeights: DEFAULT_WEIGHTS,
    categories: {
      sales: {
        recordCount: SALES.length,
        filters: [
          { key: "line", label: "Line", options: options(LINES) },
          { key: "powertrain", label: "Powertrain", options: options(POWERTRAINS) },
        ],
      },
      customer: {
        recordCount: CUSTOMER.length,
        filters: [{ key: "signal", label: "Signal", options: options(SIGNALS) }],
      },
      features: {
        recordCount: FEATURES.length,
        filters: [{ key: "feature", label: "Feature", heading: "Existing BMW cars", options: options(BMW_FEATURES) }],
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

const salesLabel = (r: SalesRecord) => `${labelOf(LINES, r.line)} · ${r.powertrain} · signal ${r.v.toFixed(2)}`;
const customerLabel = (r: CustomerRecord) =>
  `${labelOf(SIGNALS, r.signal)} · ${r.market} · ${r.area} · ${r.v} mentions`;
const featureLabel = (r: FeatureRecord) => `${labelOf(BMW_FEATURES, r.feature)} · ${r.offer} · ${pc(r.v)} take rate`;
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
    praise: sum(rows.filter((r) => r.signal === "praise")),
  };
}

function phrase(key: WeightedKey, rows: WeightedRows[WeightedKey]): string {
  if (key === "sales") {
    const r = rows as SalesRecord[];
    return `sales signal across ${uniq(r.map((x) => labelOf(LINES, x.line))).join(", ")} (${uniq(r.map((x) => x.powertrain)).join(" and ")})`;
  }
  if (key === "customer") {
    const { pain, praise } = painPraise(rows as CustomerRecord[]);
    return pain >= praise ? `${pain} customer pain-point mentions` : `${praise} customer praise mentions`;
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
      ? SALES.filter((r) => has(f.sales.line, r.line) && has(f.sales.powertrain, r.powertrain))
      : [],
    customer: req.enabled.customer ? CUSTOMER.filter((r) => has(f.customer.signal, r.signal)) : [],
    trends: req.enabled.trends ? TRENDS.filter((r) => has(f.trends.technology, r.technology)) : [],
  };
  const featureRows = FEATURES.filter((r) => has(f.features.feature, r.feature));

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
    const { pain, praise } = painPraise(custRows);
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
            summary: `BMW already offers ${ownFeatures.map((r) => `${labelOf(BMW_FEATURES, r.feature)} (${r.offer}, ${pc(r.v)} take rate)`).join(", ")}.`,
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
          ? `${uniq((own as SalesRecord[]).map((r) => labelOf(LINES, r.line))).join(", ")} · ${uniq((own as SalesRecord[]).map((r) => r.powertrain)).join(" + ")}`
          : [pain && `${pain} pain-point mentions`, praise && `${praise} praise mentions`].filter(Boolean).join(" · ") +
            ` · ${uniq(custRows.map((r) => r.area)).join(", ")}`;
      specs.push({ category: key, label: CATEGORIES[key].chipLabel, text, kind: "evidence" });
    }
    if (ownFeatures.length) {
      specs.push({
        category: "features",
        label: CATEGORIES.features.chipLabel,
        text: ownFeatures
          .map((r) => `${labelOf(BMW_FEATURES, r.feature)} · ${r.offer} · ${pc(r.v)} take rate`)
          .join(" · "),
        kind: "context",
      });
    }
    const ownTrends = part("trends").own as TrendRecord[];
    if (req.enabled.trends && ownTrends.length) {
      specs.push({
        category: "trends",
        label: `${CATEGORIES.trends.chipLabel} ${FORECAST_YEAR}`,
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

const PREFIX = { sales: "S", customer: "C", features: "F", trends: "T" } as const;
const TABLES = { sales: SALES, customer: CUSTOMER, features: FEATURES, trends: TRENDS } as const;
function recordId(key: keyof typeof TABLES, record: object): string {
  const index = (TABLES[key] as object[]).indexOf(record);
  return `${PREFIX[key]}-${String(index + 1).padStart(2, "0")}`;
}
