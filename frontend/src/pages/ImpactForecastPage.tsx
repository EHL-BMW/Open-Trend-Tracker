import { useEffect, useState, type CSSProperties } from "react";
import { useImpactForecast } from "../api/queries";
import type { ImpactCategory } from "../api/types";
import { errorMessage } from "../api/client";
import { StateMessage } from "../components/common/StateMessage";
import { Footer } from "../components/layout/Footer";
import { NavBar } from "../components/layout/NavBar";
import { config } from "../config";
import { featureClusters } from "../content/featureNews";
import { FeatureCard, type SavedProblemAnalysis } from "./FeatureTrendsPage";
import { usePageTitle } from "./usePageTitle";
import styles from "./ImpactForecastPage.module.css";

const CATEGORY_COLORS = ["#0066b1", "#7b61a8", "#dc7b22", "#087e8b", "#c24c63", "#39805d", "#88743c"];
const colorAt = (index: number) => CATEGORY_COLORS[index % CATEGORY_COLORS.length]!;

type ImpactPoint = ImpactCategory["impact_by_year"][number];

function lastPoint(points: ImpactPoint[]) {
  return points.at(-1)!;
}

const signed = (value: number, digits = 1) => `${value >= 0 ? "+" : ""}${value.toFixed(digits)}%`;

/** Latest estimate of a series, or a note when the category has too few pairs for one. */
const latestText = (points: ImpactPoint[]) =>
  points.length
    ? `${signed(lastPoint(points).impact_pct)} in year ${lastPoint(points).year}`
    : "too few pairs for an estimate";

/** Value range of a plot. It always includes zero because effects can be negative. */
function valueRange(values: number[]) {
  const lo = Math.min(0, ...values);
  const hi = Math.max(0, ...values);
  return hi - lo < 1 ? { lo, hi: lo + 1 } : { lo, hi };
}

function CategoryPlot({
  categories,
  selectedId,
  onSelect,
  compact,
}: {
  categories: ImpactCategory[];
  selectedId: string;
  onSelect: (id: string) => void;
  compact: boolean;
}) {
  const width = compact ? 520 : 820;
  const height = compact ? 360 : 330;
  const pad = { left: 54, right: 58, top: 24, bottom: 48 };
  const { lo, hi } = valueRange(
    categories.flatMap((category) => category.impact_by_year.map((point) => point.impact_pct)),
  );
  const x = (year: number) => pad.left + ((year - 1) / 3) * (width - pad.left - pad.right);
  const y = (value: number) => pad.top + ((hi - value) / (hi - lo)) * (height - pad.top - pad.bottom);
  const ticks = Array.from({ length: 5 }, (_, index) => lo + ((hi - lo) / 4) * index);

  return (
    <svg
      className={styles.linePlot}
      viewBox={`0 0 ${width} ${height}`}
      role="group"
      aria-label="Category sales impact by year after launch. Select a category line to see its features."
    >
      {ticks.map((tick) => (
        <g key={tick}>
          <line x1={pad.left} x2={width - pad.right} y1={y(tick)} y2={y(tick)} className={styles.gridLine} />
          <text x={pad.left - 10} y={y(tick) + 4} textAnchor="end" className={styles.axisLabel}>
            {tick.toFixed(1)}%
          </text>
        </g>
      ))}
      <line x1={pad.left} x2={width - pad.right} y1={y(0)} y2={y(0)} className={styles.zeroLine} />
      {[1, 2, 3, 4].map((year) => (
        <text key={year} x={x(year)} y={height - 15} textAnchor="middle" className={styles.axisLabel}>
          Year {year}
        </text>
      ))}
      {categories.map((category, index) => {
        if (!category.impact_by_year.length) return null;
        const color = colorAt(index);
        const points = category.impact_by_year.map((point) => `${x(point.year)},${y(point.impact_pct)}`).join(" ");
        const selected = category.id === selectedId;
        const end = lastPoint(category.impact_by_year);
        return (
          <g
            key={category.id}
            className={`${styles.categoryLine} ${selectedId && !selected ? styles.categoryLineDimmed : ""}`}
            role="button"
            tabIndex={0}
            aria-pressed={selected}
            aria-label={`${category.label}: ${signed(end.impact_pct)} in year ${end.year}`}
            onClick={() => onSelect(category.id)}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                onSelect(category.id);
              }
            }}
          >
            <polyline points={points} className={styles.hitLine} />
            <polyline
              points={points}
              fill="none"
              stroke={color}
              strokeWidth={selected ? 4.5 : 3}
              strokeLinejoin="round"
              strokeLinecap="round"
            />
            {category.impact_by_year.map((point) => (
              <circle key={point.year} cx={x(point.year)} cy={y(point.impact_pct)} r={selected ? 5 : 4} fill={color} />
            ))}
            {selected && (
              <text x={x(end.year) + 10} y={y(end.impact_pct) + 4} className={styles.endLabel} fill={color}>
                {signed(end.impact_pct)}
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}

function ImpactChart({ points, lo, hi, color }: { points: ImpactPoint[]; lo: number; hi: number; color: string }) {
  const width = 360;
  const height = 112;
  const pad = { left: 34, right: 10, top: 8, bottom: 20 };
  const x = (year: number) => pad.left + ((year - 1) / 3) * (width - pad.left - pad.right);
  const y = (value: number) => pad.top + ((hi - value) / (hi - lo)) * (height - pad.top - pad.bottom);
  const line = points.map((point) => `${x(point.year)},${y(point.impact_pct)}`).join(" ");
  const band = [
    ...points.map((point) => `${x(point.year)},${y(point.upper_pct ?? point.impact_pct)}`),
    ...[...points].reverse().map((point) => `${x(point.year)},${y(point.lower_pct ?? point.impact_pct)}`),
  ].join(" ");

  return (
    <svg className={styles.featurePlot} viewBox={`0 0 ${width} ${height}`} aria-hidden="true">
      {[lo, (lo + hi) / 2, hi].map((tick) => (
        <g key={tick}>
          <line x1={pad.left} x2={width - pad.right} y1={y(tick)} y2={y(tick)} className={styles.gridLine} />
          <text x={pad.left - 6} y={y(tick) + 3} textAnchor="end" className={styles.axisLabel}>
            {tick.toFixed(0)}%
          </text>
        </g>
      ))}
      <line x1={pad.left} x2={width - pad.right} y1={y(0)} y2={y(0)} className={styles.zeroLine} />
      {[1, 2, 3, 4].map((year) => (
        <text key={year} x={x(year)} y={height - 4} textAnchor="middle" className={styles.axisLabel}>
          Y{year}
        </text>
      ))}
      <polygon points={band} fill={color} fillOpacity={0.16} />
      <polyline points={line} fill="none" stroke={color} strokeWidth="2.5" strokeLinejoin="round" />
      {points.map((point) => (
        <circle key={point.year} cx={x(point.year)} cy={y(point.impact_pct)} r="3" fill={color} />
      ))}
    </svg>
  );
}

function ImpactCard({
  title,
  meta,
  points,
  range,
  color,
  level,
}: {
  title: string;
  meta: string;
  points: ImpactPoint[];
  range: { lo: number; hi: number };
  color: string;
  level: "subcategory" | "feature";
}) {
  const last = lastPoint(points);
  return (
    <article className={`${styles.featureCard} ${level === "subcategory" ? styles.subcategoryCard : ""}`}>
      <div className={styles.featureTop}>
        <div>
          <strong>{title}</strong>
          <span>{meta}</span>
        </div>
        <div className={styles.impactValue}>
          <b>{signed(last.impact_pct, 1)}</b>
          <span>
            {last.lower_pct?.toFixed(1)} to {last.upper_pct?.toFixed(1)}% · Y{last.year}
            {last.pairs ? ` · n=${last.pairs}` : ""}
          </span>
        </div>
      </div>
      <ImpactChart points={points} lo={range.lo} hi={range.hi} color={color} />
    </article>
  );
}

function LegacyFeaturePanel({ category, color }: { category: ImpactCategory; color: string }) {
  const groups = category.subcategories.filter((sub) => sub.impact_by_year || sub.legacy_features.length);
  const series = groups.flatMap((sub) => [
    sub.impact_by_year ?? [],
    ...sub.legacy_features.map((f) => f.impact_by_year),
  ]);
  const range = valueRange(
    series.flat().flatMap((point) => [point.lower_pct ?? point.impact_pct, point.upper_pct ?? point.impact_pct]),
  );
  const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;

  return (
    <section className={styles.panel} aria-labelledby="legacy-title">
      <div className={styles.panelHeading}>
        <span className={styles.step}>2</span>
        <div>
          <h2 id="legacy-title">Subcategories and features</h2>
          <p>Chinese version pairs · market-adjusted sales change vs pairs without it · band = 95% interval</p>
        </div>
      </div>
      {groups.length ? (
        <div className={styles.featureList}>
          {groups.map((sub) => (
            <div key={sub.id}>
              {sub.impact_by_year ? (
                <ImpactCard
                  title={sub.label}
                  meta={`Subcategory · ${plural(sub.pair_count ?? 0, "pair")}`}
                  points={sub.impact_by_year}
                  range={range}
                  color={color}
                  level="subcategory"
                />
              ) : (
                <p className={styles.emptyEvidence}>
                  {sub.label}: too few pairs for a subcategory estimate ({plural(sub.pair_count ?? 0, "pair")}).
                </p>
              )}
              {sub.legacy_features.map((feature) => (
                <ImpactCard
                  key={feature.name}
                  title={feature.name}
                  meta={`Feature · ${plural(feature.models.length, "model")} · ${plural(feature.pair_count, "pair")}`}
                  points={feature.impact_by_year}
                  range={range}
                  color={color}
                  level="feature"
                />
              ))}
            </div>
          ))}
        </div>
      ) : (
        <p className={styles.emptyEvidence}>
          No Chinese version pair in this category yet, so no feature-level sales effect is estimated.
        </p>
      )}
    </section>
  );
}

function NewsFeaturePanel({ category, problems }: { category: ImpactCategory; problems: SavedProblemAnalysis | null }) {
  const ids = new Set(
    category.subcategories.flatMap((subcategory) => subcategory.news_features.map((feature) => feature.id)),
  );
  const features = featureClusters.filter((feature) => ids.has(feature.id));

  return (
    <section className={styles.panel} aria-labelledby="news-title">
      <div className={styles.panelHeading}>
        <span className={styles.step}>3</span>
        <div>
          <h2 id="news-title">New features in the news</h2>
          <p>Market signal, not causal lift · sorted by priority</p>
        </div>
      </div>
      {features.length ? (
        <div className={styles.newsList}>
          {features.map((feature) => (
            <FeatureCard key={feature.id} feature={feature} analysis={problems} />
          ))}
        </div>
      ) : (
        <p className={styles.emptyEvidence}>No recent news feature is mapped to this category.</p>
      )}
    </section>
  );
}

export function ImpactForecastPage() {
  usePageTitle("Sales Impact Forecast");
  const forecast = useImpactForecast();
  const [selectedId, setSelectedId] = useState("");
  const [problems, setProblems] = useState<SavedProblemAnalysis | null>(null);
  useEffect(() => {
    fetch(`${config.apiBaseUrl}/agent/problems`)
      .then((response) => (response.ok ? response.json() : null))
      .then(setProblems)
      .catch(() => setProblems(null));
  }, []);
  const categories = forecast.data?.categories ?? [];
  const selectedIndex = categories.findIndex((category) => category.id === selectedId);
  const selected = categories.find((category) => category.id === selectedId);
  const selectedColor = colorAt(Math.max(selectedIndex, 0));

  return (
    <>
      <NavBar mockMode={config.useMocks} />
      <main className={styles.page}>
        <header className={styles.hero}>
          <div>
            <p className={styles.eyebrow}>Portfolio planning · Sales change, years 1–4 after launch</p>
            <h1>Sales Impact Forecast</h1>
            <p className={styles.lead}>
              Start with the category outlook. Click a category line to see the subcategories and features from Chinese
              version pairs behind its estimate, and the newest related features detected in the news.
            </p>
          </div>
          {forecast.data && (
            <div className={styles.stats} aria-label="Forecast data coverage">
              <div>
                <b>{forecast.data.categories.length}</b>
                <span>categories</span>
              </div>
              <div>
                <b>{forecast.data.valid_pair_count}/{forecast.data.collection_target}</b>
                <span>valid 4-year pairs</span>
              </div>
              <div>
                <b>{forecast.data.legacy_feature_count}</b>
                <span>estimated features</span>
              </div>
              <div>
                <b>{forecast.data.news_feature_count}</b>
                <span>news signals</span>
              </div>
            </div>
          )}
        </header>

        {forecast.isLoading && <StateMessage title="Loading sales-impact estimates…" />}
        {forecast.isError && (
          <StateMessage
            tone="error"
            title="Forecast unavailable"
            action={
              <button type="button" onClick={() => void forecast.refetch()}>
                Try again
              </button>
            }
          >
            {errorMessage(forecast.error)}
          </StateMessage>
        )}

        {forecast.data && (
          <>
            <div
              className={`${styles.workspace} ${selected ? styles.workspaceOpen : ""}`}
              style={{ "--category-color": selectedColor } as CSSProperties}
            >
              <section className={styles.panel} aria-labelledby="category-forecast-title">
                <div className={styles.panelHeading}>
                  {selected && <span className={styles.step}>1</span>}
                  <div>
                    <h2 id="category-forecast-title">Category sales impact</h2>
                    <p>
                      {selected
                        ? `${selected.label} · ${latestText(selected.impact_by_year)}`
                        : "Market-adjusted sales change vs pairs without the category · click a line to explore"}
                    </p>
                  </div>
                  {selected && (
                    <button type="button" className={styles.clearButton} onClick={() => setSelectedId("")}>
                      All categories
                    </button>
                  )}
                </div>
                <CategoryPlot
                  categories={categories}
                  selectedId={selectedId}
                  onSelect={(id) => setSelectedId(id === selectedId ? "" : id)}
                  compact={Boolean(selected)}
                />
                <div className={styles.legend}>
                  {categories.map((category, index) => (
                    <button
                      key={category.id}
                      type="button"
                      className={category.id === selectedId ? styles.legendActive : ""}
                      aria-pressed={category.id === selectedId}
                      onClick={() => setSelectedId(category.id === selectedId ? "" : category.id)}
                      style={{ "--category-color": colorAt(index) } as CSSProperties}
                    >
                      <i />
                      {category.label}
                      <b>
                        {category.impact_by_year.length
                          ? `${signed(lastPoint(category.impact_by_year).impact_pct)} · Y${lastPoint(category.impact_by_year).year}`
                          : "n/a"}
                      </b>
                    </button>
                  ))}
                </div>
              </section>

              {selected && <LegacyFeaturePanel category={selected} color={selectedColor} />}
              {selected && <NewsFeaturePanel category={selected} problems={problems} />}
            </div>

            <aside className={styles.methodNote}>
              <div>
                <b>How to read this</b>
                <span>{forecast.data.method}.</span>
              </div>
              <p>{forecast.data.caveat}</p>
            </aside>
          </>
        )}
      </main>
      <Footer />
    </>
  );
}
