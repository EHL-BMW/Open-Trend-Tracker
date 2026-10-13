import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useImpactForecast } from "../api/queries";
import type { ImpactCategory } from "../api/types";
import { TrackButton } from "../components/TrackButton";
import { Footer } from "../components/layout/Footer";
import { NavBar } from "../components/layout/NavBar";
import { config } from "../config";
import { FEATURE_EXPLANATIONS } from "../content/featureExplanations";
import { FEATURE_CATEGORIES, featureClusters, type FeatureCluster } from "../content/featureNews";
import { HEADLINE_NOTES } from "../content/headlineNotes";
import { DOMAIN_COLORS, fmtPct, trendRadarData } from "../content/trendRadar";
import { ROUTES } from "../routes";
import { legacyFeatureId, useTrackedFeatures } from "../state/trackedFeatures";
import type { SavedProblemAnalysis } from "./FeatureTrendsPage";
import { usePageTitle } from "./usePageTitle";
import styles from "./TrackedFeaturesPage.module.css";

type LegacyFeature = ImpactCategory["subcategories"][number]["legacy_features"][number];
type SavedEntry =
  | { id: string; kind: "news"; feature: FeatureCluster }
  | {
      id: string;
      kind: "legacy";
      category: ImpactCategory;
      feature: LegacyFeature;
    }
  | { id: string; kind: "pending"; label: string };

function salesForNews(featureId: string, forecast: ImpactCategory[]) {
  const matched = forecast
    .flatMap((category) => category.subcategories.map((sub) => ({ category, sub })))
    .find(({ sub }) => sub.news_features.some((item) => item.id === featureId));
  return {
    points: matched?.sub.impact_by_year ?? matched?.category.impact_by_year ?? [],
    label: matched?.sub.impact_by_year ? `${matched.sub.label} proxy` : "category proxy",
    category: matched?.category,
    subcategory: matched?.sub,
  };
}

function MiniTrend({ feature }: { feature: FeatureCluster }) {
  const values = feature.weeklyCounts;
  if (!values.length) return <p className={styles.muted}>No 12-week history yet</p>;
  const high = Math.max(...values, 1);
  const points = values
    .map((value, index) => `${(index / Math.max(values.length - 1, 1)) * 300},${70 - (value / high) * 62}`)
    .join(" ");
  return (
    <svg
      className={styles.trendChart}
      viewBox="0 0 300 76"
      role="img"
      aria-label={`${feature.label} article counts over 12 weeks`}
    >
      <polygon points={`0,76 ${points} 300,76`} fill="currentColor" opacity="0.12" />
      <polyline points={points} fill="none" stroke="currentColor" strokeWidth="3" strokeLinejoin="round" />
    </svg>
  );
}

function NewsOverview({ feature }: { feature: FeatureCluster }) {
  return (
    <article className={styles.card}>
      <div className={styles.cardHead}>
        <span
          className={styles.category}
          style={{ "--category-color": DOMAIN_COLORS[feature.category] ?? "#0066b1" } as React.CSSProperties}
        >
          {feature.category}
        </span>
        <TrackButton id={feature.id} label={feature.label} compact />
      </div>
      <h2>{feature.label}</h2>
      <p className={styles.chinese}>{feature.labelCn}</p>
      {FEATURE_EXPLANATIONS[feature.id] && (
        <div className={styles.reportIntro}>
          <b>What it is · AI-generated explanation</b>
          <p>{FEATURE_EXPLANATIONS[feature.id]}</p>
        </div>
      )}
      <div className={styles.reportFacts}>
        <span>
          <b>{feature.momentumPctChange === null ? "—" : fmtPct(feature.momentumPctChange)}</b> momentum
        </span>
        <span>
          <b>{feature.volumeRecent}</b> recent articles
        </span>
        <span>
          <b>{feature.breadthOutlets}</b> outlets
        </span>
        <span>
          <b>{feature.items.length}</b> evidence items
        </span>
      </div>
    </article>
  );
}

function NewsEvidence({ feature, problems }: { feature: FeatureCluster; problems: SavedProblemAnalysis | null }) {
  const linkedProblems =
    problems?.problems.filter((problem) => problem.possible_feature_ids.includes(feature.id)) ?? [];
  return (
    <section className={styles.reportSection}>
      <div className={styles.section}>
        <h3>OEMs in related news</h3>
        <div className={styles.chips}>
          {feature.brandCounts.length ? (
            feature.brandCounts.map(({ brand, count }) => (
              <span key={brand}>
                {brand} · {count}
              </span>
            ))
          ) : (
            <span>No OEM named</span>
          )}
        </div>
      </div>
      {linkedProblems.length > 0 && (
        <div className={styles.section}>
          <h3>Linked customer problems</h3>
          <div className={styles.problemDetails}>
            {linkedProblems.map((problem) => (
              <div key={problem.id}>
                <b>
                  {problem.name} · {problem.mention_count} mentions
                </b>
                <small>
                  {problem.category} · {problem.severity}
                </small>
                <p>{problem.problem_statement}</p>
                {problem.evidence[0] && <blockquote>“{problem.evidence[0].quote}”</blockquote>}
              </div>
            ))}
          </div>
        </div>
      )}
      <div className={styles.section}>
        <h3>Related news · {feature.items.length}</h3>
        <div className={styles.news}>
          {feature.items.map((item) => (
            <div key={item.id}>
              <a href={item.url} target="_blank" rel="noreferrer">
                {item.title} ↗
              </a>
              {item.titleEn && <span className={styles.newsTranslation}>EN · {item.titleEn}</span>}
              <small>
                {item.sourceEn ?? item.source} · {item.date}
              </small>
              {(HEADLINE_NOTES[feature.id]?.[item.title]?.featureSummary ?? item.summary) && (
                <p>{HEADLINE_NOTES[feature.id]?.[item.title]?.featureSummary ?? item.summary}</p>
              )}
            </div>
          ))}
        </div>
      </div>
      <Link className={styles.sourceLink} to={ROUTES.featureTrends}>
        Explore in Feature Radar →
      </Link>
    </section>
  );
}

function LegacyOverview({ category, feature, id }: { category: ImpactCategory; feature: LegacyFeature; id: string }) {
  return (
    <article className={styles.card}>
      <div className={styles.cardHead}>
        <span className={styles.category}>{category.label}</span>
        <TrackButton id={id} label={feature.name} compact />
      </div>
      <h2>{feature.name}</h2>
      <p className={styles.muted}>Feature identified in Chinese vehicle version pairs</p>
      <div className={styles.reportFacts}>
        <span>
          <b>{feature.pair_count}</b> paired records
        </span>
        <span>
          <b>{feature.models.length}</b> models
        </span>
        <span>
          <b>{feature.impact_by_year.length}/4</b> years estimated
        </span>
      </div>
    </article>
  );
}

function LegacyEvidence({ feature }: { feature: LegacyFeature }) {
  return (
    <section className={styles.reportSection}>
      <div className={styles.section}>
        <h3>Models in the sales sample</h3>
        <div className={styles.chips}>
          {feature.models.map((model) => (
            <span key={model}>{model}</span>
          ))}
        </div>
      </div>
      <p className={styles.muted}>A matching news trend has not been linked to this historical feature.</p>
      <Link className={styles.sourceLink} to={ROUTES.impactForecast}>
        Explore in Sales Impact Forecast →
      </Link>
    </section>
  );
}

function PendingCard({ id, label }: { id: string; label: string }) {
  return (
    <article className={styles.card}>
      <div className={styles.cardHead}>
        <span className={styles.category}>Pending data</span>
        <TrackButton id={id} label={label} compact />
      </div>
      <h2>{label}</h2>
      <p className={styles.muted}>This feature is tracked. Its latest source data is not available right now.</p>
    </article>
  );
}

function ReportPreview({
  entry,
  forecast,
  onOpen,
}: {
  entry: SavedEntry;
  forecast: ImpactCategory[];
  onOpen: () => void;
}) {
  const label =
    entry.kind === "news" ? entry.feature.label : entry.kind === "legacy" ? entry.feature.name : entry.label;
  const category =
    entry.kind === "news" ? entry.feature.category : entry.kind === "legacy" ? entry.category.label : "Pending data";
  const points =
    entry.kind === "news"
      ? salesForNews(entry.id, forecast).points
      : entry.kind === "legacy"
        ? entry.feature.impact_by_year
        : [];
  const latest = points.at(-1);
  return (
    <article className={styles.previewCard}>
      <button type="button" className={styles.previewOpen} onClick={onOpen} aria-label={`Open report for ${label}`}>
        <span
          className={styles.category}
          style={{ "--category-color": DOMAIN_COLORS[category] ?? "#0066b1" } as React.CSSProperties}
        >
          {category}
        </span>
        <h2>{label}</h2>
        {entry.kind === "news" && (
          <>
            <p className={styles.chinese}>{entry.feature.labelCn}</p>
            <MiniTrend feature={entry.feature} />
            <div className={styles.previewStats}>
              <span>
                {entry.feature.signal} ·{" "}
                {entry.feature.momentumPctChange === null ? "—" : fmtPct(entry.feature.momentumPctChange)} momentum
              </span>
              <span>{entry.feature.items.length} news items</span>
            </div>
          </>
        )}
        {entry.kind === "legacy" && (
          <p className={styles.muted}>
            {entry.feature.pair_count} Chinese vehicle version pairs · {entry.feature.models.length} models
          </p>
        )}
        <div className={styles.previewImpact}>
          <span>Sales impact</span>
          <b>
            {latest
              ? `${latest.impact_pct >= 0 ? "+" : ""}${latest.impact_pct.toFixed(1)}% · Y${latest.year}`
              : "No estimate yet"}
          </b>
          <small>{points.length}/4 years available · observational</small>
        </div>
        <span className={styles.openReport}>Open full report →</span>
      </button>
      <div className={styles.previewTrack}>
        <TrackButton id={entry.id} label={label} compact />
      </div>
    </article>
  );
}

function CoverageReport({ feature }: { feature: FeatureCluster }) {
  const values = feature.weeklyCounts;
  const width = 760,
    height = 220,
    left = 42,
    right = 16,
    top = 16,
    bottom = 35;
  const max = Math.max(...values, 1);
  const x = (index: number) => left + (index / Math.max(values.length - 1, 1)) * (width - left - right);
  const y = (value: number) => top + (1 - value / max) * (height - top - bottom);
  const points = values.map((value, index) => `${x(index)},${y(value)}`).join(" ");
  return (
    <section className={styles.reportSection}>
      <h3>12-week coverage trend</h3>
      <p>Weekly article counts for this feature in the Chinese news feed.</p>
      {values.length ? (
        <svg
          className={styles.reportChart}
          viewBox={`0 0 ${width} ${height}`}
          role="img"
          aria-label={`${feature.label}: weekly news coverage over 12 weeks`}
        >
          {[0, Math.round(max / 2), max].map((tick) => (
            <g key={tick}>
              <line x1={left} x2={width - right} y1={y(tick)} y2={y(tick)} className={styles.gridLine} />
              <text x={left - 10} y={y(tick) + 4} textAnchor="end">
                {tick}
              </text>
            </g>
          ))}
          <polygon
            points={`${left},${y(0)} ${points} ${x(values.length - 1)},${y(0)}`}
            fill="var(--blue)"
            opacity="0.12"
          />
          <polyline points={points} fill="none" stroke="var(--blue)" strokeWidth="3" strokeLinejoin="round" />
          {values.map((value, index) => (
            <circle key={index} cx={x(index)} cy={y(value)} r="4" fill="var(--blue)" />
          ))}
          <text x={left} y={height - 5}>
            12 weeks ago
          </text>
          <text x={width - right} y={height - 5} textAnchor="end">
            Latest week
          </text>
        </svg>
      ) : (
        <p>No 12-week coverage history is available for this feature.</p>
      )}
      <div className={styles.reportFacts}>
        <span>
          <b>{feature.volumeRecent}</b> recent articles
        </span>
        <span>
          <b>{feature.breadthOutlets}</b> outlets
        </span>
        <span>
          <b>{feature.momentumPctChange === null ? "—" : fmtPct(feature.momentumPctChange)}</b> momentum
        </span>
        <span>
          <b>{feature.priority?.toFixed(1) ?? "—"}</b> priority
        </span>
      </div>
    </section>
  );
}

function NewsSignalReport({ feature }: { feature: FeatureCluster }) {
  const topic = trendRadarData.topics.find((item) => item.id === feature.id);
  if (!topic) return null;
  return (
    <section className={styles.reportSection}>
      <h3>News signal & sources</h3>
      <p>How this feature appears across the monitored Chinese news window.</p>
      <div className={styles.reportFacts}>
        <span>
          <b>{(topic.share_of_voice * 100).toFixed(1)}%</b> share of voice
        </span>
        <span>
          <b>{topic.signal}</b> signal
        </span>
        <span>
          <b>{topic.breadth_outlets}</b> outlets
        </span>
        <span>
          <b>{topic.priority.toFixed(1)}</b> priority
        </span>
      </div>
      <h4>Top outlets</h4>
      <div className={styles.chips}>
        {topic.top_outlets.map(([name, count]) => (
          <span key={name}>
            {name} · {count}
          </span>
        ))}
      </div>
      <h4>Search query</h4>
      <code className={styles.query}>{topic.query}</code>
      <p className={styles.dataNote}>
        Momentum compares recent coverage with the earlier part of the 12-week window. These figures describe media
        attention, not product adoption.
      </p>
      <Link className={styles.sourceLink} to={ROUTES.newsletter}>
        Open Newsletter →
      </Link>
    </section>
  );
}

function SalesReport({
  points,
  label,
  pairCount,
}: {
  points: ImpactCategory["impact_by_year"];
  label: string;
  pairCount?: number;
}) {
  const width = 760,
    height = 240,
    left = 54,
    right = 25,
    top = 20,
    bottom = 35;
  const values = points.flatMap((point) => [
    point.impact_pct,
    point.lower_pct ?? point.impact_pct,
    point.upper_pct ?? point.impact_pct,
  ]);
  const lo = Math.min(0, ...values),
    hi = Math.max(0, ...values);
  const spread = Math.max(hi - lo, 1);
  const x = (year: number) => left + ((year - 1) / 3) * (width - left - right);
  const y = (value: number) => top + ((hi - value) / spread) * (height - top - bottom);
  const line = points.map((point) => `${x(point.year)},${y(point.impact_pct)}`).join(" ");
  const band = [
    ...points.map((point) => `${x(point.year)},${y(point.upper_pct ?? point.impact_pct)}`),
    ...[...points].reverse().map((point) => `${x(point.year)},${y(point.lower_pct ?? point.impact_pct)}`),
  ].join(" ");
  return (
    <section className={styles.reportSection}>
      <h3>Sales impact · years 1–4</h3>
      <p>
        {label}. Market-adjusted association from Chinese vehicle version pairs. This is an estimate, not a measured
        causal lift for this feature.
      </p>
      {pairCount !== undefined && <p>{pairCount} paired vehicle records mention this feature or subcategory.</p>}
      {points.length ? (
        <>
          <svg
            className={styles.reportChart}
            viewBox={`0 0 ${width} ${height}`}
            role="img"
            aria-label={`Sales impact: ${points.length} of four years have estimates`}
          >
            {[lo, 0, hi]
              .filter((v, i, a) => a.indexOf(v) === i)
              .map((tick) => (
                <g key={tick}>
                  <line x1={left} x2={width - right} y1={y(tick)} y2={y(tick)} className={styles.gridLine} />
                  <text x={left - 8} y={y(tick) + 4} textAnchor="end">
                    {tick.toFixed(1)}%
                  </text>
                </g>
              ))}
            {band && <polygon points={band} fill="var(--blue)" opacity="0.15" />}
            <polyline points={line} fill="none" stroke="var(--blue)" strokeWidth="3" />
            {points.map((point) => (
              <circle key={point.year} cx={x(point.year)} cy={y(point.impact_pct)} r="5" fill="var(--blue)" />
            ))}
            {[1, 2, 3, 4].map((year) => (
              <text key={year} x={x(year)} y={height - 5} textAnchor="middle">
                Y{year}
              </text>
            ))}
          </svg>
          <div className={styles.salesTable} role="table" aria-label="Sales impact by year">
            <div role="row">
              <b>Year</b>
              <b>Estimate</b>
              <b>95% interval</b>
              <b>Pairs</b>
            </div>
            {[1, 2, 3, 4].map((year) => {
              const point = points.find((item) => item.year === year);
              return (
                <div role="row" key={year}>
                  <span>Y{year}</span>
                  <strong>
                    {point ? `${point.impact_pct >= 0 ? "+" : ""}${point.impact_pct.toFixed(1)}%` : "Not available"}
                  </strong>
                  <span>
                    {point?.lower_pct !== undefined && point.upper_pct !== undefined
                      ? `${point.lower_pct.toFixed(1)}% to ${point.upper_pct.toFixed(1)}%`
                      : "—"}
                  </span>
                  <span>{point?.pairs ?? "—"}</span>
                </div>
              );
            })}
          </div>
          {points.length < 4 && (
            <p className={styles.dataNote}>
              Only {points.length} year{points.length === 1 ? "" : "s"} of paired sales evidence{" "}
              {points.length === 1 ? "is" : "are"} available. The remaining years are shown as unavailable.
            </p>
          )}
        </>
      ) : (
        <p>No sales estimate is available for this feature yet.</p>
      )}
    </section>
  );
}

export function TrackedFeaturesPage() {
  usePageTitle("My Features");
  const tracked = useTrackedFeatures();
  const forecast = useImpactForecast();
  const [oem, setOem] = useState<string | null>(null);
  const [category, setCategory] = useState<string | null>(null);
  const [problems, setProblems] = useState<SavedProblemAnalysis | null>(null);
  const [reportId, setReportId] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${config.apiBaseUrl}/agent/problems`)
      .then((response) => (response.ok ? (response.json() as Promise<SavedProblemAnalysis>) : null))
      .then(setProblems)
      .catch(() => setProblems(null));
  }, []);

  const categories = forecast.data?.categories ?? [];
  const legacy = categories.flatMap((cat) =>
    cat.subcategories.flatMap((sub) =>
      sub.legacy_features.map((feature) => ({
        id: legacyFeatureId(cat.id, feature.name),
        kind: "legacy" as const,
        category: cat,
        feature,
      })),
    ),
  );
  const entries = tracked.flatMap<SavedEntry>((id) => {
    const feature = featureClusters.find((item) => item.id === id);
    if (feature) return [{ id, kind: "news" as const, feature }];
    const item = legacy.find((candidate) => candidate.id === id);
    return item
      ? [item]
      : [{ id, kind: "pending", label: id.startsWith("legacy:") ? id.split(":").slice(2).join(":") : id }];
  });
  const brands = [
    ...new Set(
      entries.flatMap((entry) => (entry.kind === "news" ? entry.feature.brandCounts.map((item) => item.brand) : [])),
    ),
  ].sort();
  const usedCategories = [
    ...new Set(
      entries.map((entry) =>
        entry.kind === "news"
          ? entry.feature.category
          : entry.kind === "legacy"
            ? entry.category.label
            : "Pending data",
      ),
    ),
  ];
  const orderedCategories = [
    ...FEATURE_CATEGORIES.filter((item) => usedCategories.includes(item)),
    ...usedCategories.filter((item) => !FEATURE_CATEGORIES.includes(item as (typeof FEATURE_CATEGORIES)[number])),
  ];
  const displayed = entries.filter((entry) => {
    const entryCategory =
      entry.kind === "news" ? entry.feature.category : entry.kind === "legacy" ? entry.category.label : "Pending data";
    return (
      (!category || category === entryCategory) &&
      (!oem || (entry.kind === "news" && entry.feature.brandCounts.some((item) => item.brand === oem)))
    );
  });
  const reportEntry = entries.find((entry) => entry.id === reportId);
  const reportSales = reportEntry?.kind === "news" ? salesForNews(reportEntry.id, categories) : null;

  useEffect(() => {
    if (reportId && !reportEntry) setReportId(null);
  }, [reportId, reportEntry]);

  useEffect(() => {
    if (!reportEntry) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setReportId(null);
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [reportEntry]);

  return (
    <>
      <NavBar mockMode={config.useMocks} />
      <main className={styles.page}>
        <header className={styles.hero}>
          <p className={styles.eyebrow}>Your watchlist · across OpenTT</p>
          <h1>My Features</h1>
          <p>
            Track a feature from Newsletter, Feature Radar, Sales Impact Forecast or Planner. Its evidence is collected
            here and refreshes with the demo data.
          </p>
          <strong>{entries.length} tracked features</strong>
        </header>
        {tracked.length > 0 && (
          <div className={styles.filters}>
            <div className={styles.filterRow}>
              <b>OEM</b>
              <button className={!oem ? styles.selected : ""} onClick={() => setOem(null)}>
                All OEMs
              </button>
              {brands.map((brand) => (
                <button key={brand} className={oem === brand ? styles.selected : ""} onClick={() => setOem(brand)}>
                  {brand}{" "}
                  {
                    entries.filter(
                      (entry) =>
                        entry.kind === "news" && entry.feature.brandCounts.some((item) => item.brand === brand),
                    ).length
                  }
                </button>
              ))}
            </div>
            <div className={styles.filterRow}>
              <b>Category</b>
              <button className={!category ? styles.selected : ""} onClick={() => setCategory(null)}>
                All categories
              </button>
              {orderedCategories.map((item) => (
                <button
                  key={item}
                  className={category === item ? styles.selected : ""}
                  onClick={() => setCategory(item)}
                >
                  {item}
                </button>
              ))}
            </div>
          </div>
        )}
        {!tracked.length ? (
          <div className={styles.empty}>
            <h2>No tracked features yet</h2>
            <p>Open a feature card and click Track to build your watchlist.</p>
            <Link to={ROUTES.featureTrends}>Explore Feature Radar →</Link>
          </div>
        ) : !displayed.length ? (
          <div className={styles.empty}>
            <h2>No features match these filters</h2>
            <button
              onClick={() => {
                setOem(null);
                setCategory(null);
              }}
            >
              Clear filters
            </button>
          </div>
        ) : (
          <div className={styles.grid}>
            {displayed.map((entry) => (
              <ReportPreview key={entry.id} entry={entry} forecast={categories} onOpen={() => setReportId(entry.id)} />
            ))}
          </div>
        )}
      </main>
      <Footer />
      {reportEntry && (
        <div
          className={styles.reportBackdrop}
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) setReportId(null);
          }}
        >
          <section
            className={styles.report}
            role="dialog"
            aria-modal="true"
            aria-label={`${reportEntry.kind === "news" ? reportEntry.feature.label : reportEntry.kind === "legacy" ? reportEntry.feature.name : reportEntry.label} report`}
          >
            <button
              className={styles.closeReport}
              type="button"
              onClick={() => setReportId(null)}
              aria-label="Close report"
            >
              ×
            </button>
            <p className={styles.eyebrow}>Tracked feature · full report</p>
            {reportEntry.kind === "news" ? (
              <>
                <NewsOverview feature={reportEntry.feature} />
                <CoverageReport feature={reportEntry.feature} />
                {reportSales && (
                  <SalesReport
                    points={reportSales.points}
                    label={`${reportSales.label}${reportSales.subcategory ? ` · ${reportSales.subcategory.label}` : ""}`}
                    pairCount={reportSales.subcategory?.pair_count ?? reportSales.category?.pair_count}
                  />
                )}
                <NewsSignalReport feature={reportEntry.feature} />
                <NewsEvidence feature={reportEntry.feature} problems={problems} />
              </>
            ) : reportEntry.kind === "legacy" ? (
              <>
                <LegacyOverview id={reportEntry.id} category={reportEntry.category} feature={reportEntry.feature} />
                <SalesReport
                  points={reportEntry.feature.impact_by_year}
                  label="Direct feature-level estimate"
                  pairCount={reportEntry.feature.pair_count}
                />
                <LegacyEvidence feature={reportEntry.feature} />
              </>
            ) : (
              <PendingCard id={reportEntry.id} label={reportEntry.label} />
            )}
          </section>
        </div>
      )}
    </>
  );
}
