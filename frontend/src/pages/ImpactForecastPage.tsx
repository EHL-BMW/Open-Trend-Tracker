import { useState, type CSSProperties } from "react";
import { useImpactForecast } from "../api/queries";
import type { ImpactCategory } from "../api/types";
import { errorMessage } from "../api/client";
import { StateMessage } from "../components/common/StateMessage";
import { Footer } from "../components/layout/Footer";
import { NavBar } from "../components/layout/NavBar";
import { config } from "../config";
import { usePageTitle } from "./usePageTitle";
import styles from "./ImpactForecastPage.module.css";

const CATEGORY_COLORS = ["#0066b1", "#7b61a8", "#dc7b22", "#087e8b", "#c24c63", "#39805d", "#88743c"];
const colorAt = (index: number) => CATEGORY_COLORS[index % CATEGORY_COLORS.length]!;

type ImpactPoint = ImpactCategory["impact_by_year"][number];
type LegacyFeature = ImpactCategory["subcategories"][number]["legacy_features"][number];

function lastPoint(points: ImpactPoint[]) {
  return points.at(-1)!;
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
  const max = Math.max(...categories.flatMap((category) => category.impact_by_year.map((point) => point.impact_pct)), 1);
  const x = (year: number) => pad.left + ((year - 1) / 3) * (width - pad.left - pad.right);
  const y = (value: number) => pad.top + (1 - value / max) * (height - pad.top - pad.bottom);
  const ticks = Array.from({ length: 5 }, (_, index) => (max / 4) * index);

  return (
    <svg
      className={styles.linePlot}
      viewBox={`0 0 ${width} ${height}`}
      role="group"
      aria-label="Four-year category sales impact scenario. Select a category line to see its features."
    >
      {ticks.map((tick) => (
        <g key={tick}>
          <line x1={pad.left} x2={width - pad.right} y1={y(tick)} y2={y(tick)} className={styles.gridLine} />
          <text x={pad.left - 10} y={y(tick) + 4} textAnchor="end" className={styles.axisLabel}>
            {tick.toFixed(1)}%
          </text>
        </g>
      ))}
      {[1, 2, 3, 4].map((year) => (
        <text key={year} x={x(year)} y={height - 15} textAnchor="middle" className={styles.axisLabel}>
          Year {year}
        </text>
      ))}
      {categories.map((category, index) => {
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
            aria-label={`${category.label}: +${end.impact_pct.toFixed(1)}% by year 4`}
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
                +{end.impact_pct.toFixed(1)}%
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}

function FeatureImpactChart({ feature, max, color }: { feature: LegacyFeature; max: number; color: string }) {
  const width = 360;
  const height = 112;
  const pad = { left: 34, right: 10, top: 8, bottom: 20 };
  const points = feature.impact_by_year;
  const x = (year: number) => pad.left + ((year - 1) / 3) * (width - pad.left - pad.right);
  const y = (value: number) => pad.top + (1 - value / max) * (height - pad.top - pad.bottom);
  const line = points.map((point) => `${x(point.year)},${y(point.impact_pct)}`).join(" ");
  const band = [
    ...points.map((point) => `${x(point.year)},${y(point.upper_pct ?? point.impact_pct)}`),
    ...[...points].reverse().map((point) => `${x(point.year)},${y(point.lower_pct ?? point.impact_pct)}`),
  ].join(" ");

  return (
    <svg className={styles.featurePlot} viewBox={`0 0 ${width} ${height}`} aria-hidden="true">
      {[0, max / 2, max].map((tick) => (
        <g key={tick}>
          <line x1={pad.left} x2={width - pad.right} y1={y(tick)} y2={y(tick)} className={styles.gridLine} />
          <text x={pad.left - 6} y={y(tick) + 3} textAnchor="end" className={styles.axisLabel}>
            {tick.toFixed(1)}%
          </text>
        </g>
      ))}
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

function LegacyFeaturePanel({ category, color }: { category: ImpactCategory; color: string }) {
  const features = category.subcategories.flatMap((subcategory) =>
    subcategory.legacy_features.map((feature) => ({ feature, subcategory: subcategory.label })),
  );
  const max = Math.ceil(
    Math.max(
      ...features.flatMap(({ feature }) => feature.impact_by_year.map((point) => point.upper_pct ?? point.impact_pct)),
      1,
    ),
  );

  return (
    <section className={styles.panel} aria-labelledby="legacy-title">
      <div className={styles.panelHeading}>
        <span className={styles.step}>2</span>
        <div>
          <h2 id="legacy-title">Legacy features</h2>
          <p>Chinese-200 sales impact · shaded band = uncertainty range</p>
        </div>
      </div>
      {features.length ? (
        <div className={styles.featureList}>
          {features.map(({ feature, subcategory }) => {
            const last = lastPoint(feature.impact_by_year);
            return (
              <article className={styles.featureCard} key={feature.name}>
                <div className={styles.featureTop}>
                  <div>
                    <strong>{feature.name}</strong>
                    <span>
                      {subcategory} · {feature.models.length} model{feature.models.length === 1 ? "" : "s"} ·{" "}
                      {feature.pair_count} pair{feature.pair_count === 1 ? "" : "s"}
                    </span>
                  </div>
                  <div className={styles.impactValue}>
                    <b>+{last.impact_pct.toFixed(2)}%</b>
                    <span>
                      {last.lower_pct?.toFixed(2)}–{last.upper_pct?.toFixed(2)}% · Y4
                    </span>
                  </div>
                </div>
                <FeatureImpactChart feature={feature} max={max} color={color} />
              </article>
            );
          })}
        </div>
      ) : (
        <p className={styles.emptyEvidence}>
          No comparable Chinese-200 feature in this category yet, so no feature-level sales effect is modeled.
        </p>
      )}
    </section>
  );
}

function NewsFeaturePanel({ category }: { category: ImpactCategory }) {
  const news = category.subcategories
    .flatMap((subcategory) => subcategory.news_features.map((feature) => ({ feature, subcategory: subcategory.label })))
    .sort((a, b) => (b.feature.priority ?? 0) - (a.feature.priority ?? 0));

  return (
    <section className={styles.panel} aria-labelledby="news-title">
      <div className={styles.panelHeading}>
        <span className={styles.step}>3</span>
        <div>
          <h2 id="news-title">New features in the news</h2>
          <p>Market signal, not causal lift · sorted by priority</p>
        </div>
      </div>
      {news.length ? (
        <div className={styles.newsList}>
          {news.map(({ feature, subcategory }) => (
            <article className={styles.newsFeature} key={feature.id}>
              <div className={styles.newsFeatureTop}>
                <strong>{feature.label}</strong>
                <span data-signal={feature.signal?.toLowerCase() ?? "tracked"}>{feature.signal ?? "Tracked"}</span>
              </div>
              <p>
                {feature.label_cn} · {subcategory} · priority {feature.priority?.toFixed(1) ?? "—"} ·{" "}
                {feature.volume_recent.toLocaleString()} recent articles
              </p>
              {feature.headline && (
                <a href={feature.headline_url} target="_blank" rel="noreferrer">
                  {feature.headline}
                </a>
              )}
            </article>
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
            <p className={styles.eyebrow}>Portfolio planning · Four-year scenario</p>
            <h1>Sales Impact Forecast</h1>
            <p className={styles.lead}>
              Start with the category outlook. Click a category line to see the Chinese-200 features behind its estimate
              and the newest related features detected in the news.
            </p>
          </div>
          {forecast.data && (
            <div className={styles.stats} aria-label="Forecast data coverage">
              <div>
                <b>{forecast.data.categories.length}</b>
                <span>categories</span>
              </div>
              <div>
                <b>{forecast.data.legacy_feature_count}</b>
                <span>legacy features</span>
              </div>
              <div>
                <b>{forecast.data.news_feature_count}</b>
                <span>news signals</span>
              </div>
            </div>
          )}
        </header>

        {forecast.isLoading && <StateMessage title="Loading sales-impact scenarios…" />}
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
                        ? `${selected.label} · +${lastPoint(selected.impact_by_year).impact_pct.toFixed(1)}% by year 4`
                        : "Four-year cumulative uplift scenario · click a line to explore"}
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
                      <b>+{lastPoint(category.impact_by_year).impact_pct.toFixed(1)}%</b>
                    </button>
                  ))}
                </div>
              </section>

              {selected && <LegacyFeaturePanel category={selected} color={selectedColor} />}
              {selected && <NewsFeaturePanel category={selected} />}
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
