import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { useImpactForecast } from "../api/queries";
import type { ImpactCategory, ImpactSubcategory } from "../api/types";
import { errorMessage } from "../api/client";
import { StateMessage } from "../components/common/StateMessage";
import { Footer } from "../components/layout/Footer";
import { NavBar } from "../components/layout/NavBar";
import { config } from "../config";
import { usePageTitle } from "./usePageTitle";
import styles from "./ImpactForecastPage.module.css";

const CATEGORY_COLORS = ["#0066b1", "#7b61a8", "#dc7b22", "#087e8b", "#c24c63", "#39805d", "#88743c"];

function valueAt(points: Array<{ year: number; impact_pct: number }> | null, year: number) {
  return points?.find((point) => point.year === year)?.impact_pct ?? null;
}

function CategoryPlot({ categories }: { categories: ImpactCategory[] }) {
  const width = 820;
  const height = 330;
  const pad = { left: 54, right: 24, top: 24, bottom: 48 };
  const max = Math.max(
    ...categories.flatMap((category) => category.impact_by_year.map((point) => point.impact_pct)),
    1,
  );
  const x = (year: number) => pad.left + ((year - 1) / 3) * (width - pad.left - pad.right);
  const y = (value: number) => pad.top + (1 - value / max) * (height - pad.top - pad.bottom);
  const ticks = Array.from({ length: 5 }, (_, index) => (max / 4) * index);

  return (
    <svg
      className={styles.linePlot}
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label="Four-year category sales impact scenario"
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
        const color = CATEGORY_COLORS[index % CATEGORY_COLORS.length];
        const points = category.impact_by_year.map((point) => `${x(point.year)},${y(point.impact_pct)}`).join(" ");
        return (
          <g key={category.id}>
            <polyline
              points={points}
              fill="none"
              stroke={color}
              strokeWidth="3"
              strokeLinejoin="round"
              strokeLinecap="round"
            />
            {category.impact_by_year.map((point) => (
              <circle key={point.year} cx={x(point.year)} cy={y(point.impact_pct)} r="4" fill={color} />
            ))}
          </g>
        );
      })}
    </svg>
  );
}

function SubcategoryPlot({
  category,
  year,
  selectedId,
  onSelect,
}: {
  category: ImpactCategory;
  year: number;
  selectedId: string;
  onSelect: (id: string) => void;
}) {
  const maximum = Math.max(
    valueAt(category.impact_by_year, year) ?? 1,
    ...category.subcategories.map((subcategory) => valueAt(subcategory.impact_by_year, year) ?? 0),
  );
  return (
    <div className={styles.barPlot} role="group" aria-label={`${category.label} subcategory impact in year ${year}`}>
      {category.subcategories.map((subcategory) => {
        const value = valueAt(subcategory.impact_by_year, year);
        return (
          <button
            key={subcategory.id}
            type="button"
            className={`${styles.barRow} ${selectedId === subcategory.id ? styles.barRowActive : ""}`}
            onClick={() => onSelect(subcategory.id)}
            aria-pressed={selectedId === subcategory.id}
          >
            <span className={styles.barLabel}>{subcategory.label}</span>
            <span className={`${styles.barTrack} ${value === null ? styles.barTrackUnmodeled : ""}`}>
              {value !== null && (
                <span
                  className={styles.barFill}
                  style={{ "--bar-width": `${(value / maximum) * 100}%` } as CSSProperties}
                />
              )}
            </span>
            <strong>{value === null ? "Signal only" : `+${value.toFixed(2)}%`}</strong>
          </button>
        );
      })}
      <div className={styles.categoryBenchmark}>
        <span>Category benchmark</span>
        <b>+{valueAt(category.impact_by_year, year)?.toFixed(2)}%</b>
      </div>
    </div>
  );
}

function EvidenceCard({ subcategory, selected }: { subcategory: ImpactSubcategory; selected: boolean }) {
  return (
    <article
      id={`subcategory-${subcategory.id}`}
      className={`${styles.evidenceCard} ${selected ? styles.evidenceCardSelected : ""}`}
    >
      <div className={styles.evidenceHeader}>
        <div>
          <p>Subcategory</p>
          <h3>{subcategory.label}</h3>
        </div>
        <span>
          {subcategory.legacy_features.length} legacy · {subcategory.news_features.length} recent
        </span>
      </div>
      <div className={styles.evidenceColumns}>
        <section>
          <div className={styles.columnHeading}>
            <b>Chinese-200 legacy features</b>
            <span>Impact evidence</span>
          </div>
          {subcategory.legacy_features.length ? (
            subcategory.legacy_features.map((feature) => {
              const last = feature.impact_by_year.at(-1)!;
              return (
                <div className={styles.legacyFeature} key={feature.name}>
                  <div>
                    <strong>{feature.name}</strong>
                    <span>
                      {feature.models.join(", ")} · {feature.pair_count} pair{feature.pair_count === 1 ? "" : "s"}
                    </span>
                  </div>
                  <div className={styles.impactValue}>
                    <b>+{last.impact_pct.toFixed(2)}%</b>
                    <span>
                      {last.lower_pct?.toFixed(2)}–{last.upper_pct?.toFixed(2)}%
                    </span>
                  </div>
                </div>
              );
            })
          ) : (
            <p className={styles.emptyEvidence}>
              No comparable legacy feature yet, so no subcategory sales effect is modeled.
            </p>
          )}
        </section>
        <section>
          <div className={styles.columnHeading}>
            <b>Recent news features</b>
            <span>Market signal, not causal lift</span>
          </div>
          {subcategory.news_features.length ? (
            subcategory.news_features.map((feature) => (
              <div className={styles.newsFeature} key={feature.id}>
                <div className={styles.newsFeatureTop}>
                  <strong>{feature.label}</strong>
                  <span>{feature.signal ?? "Tracked"}</span>
                </div>
                <p>
                  {feature.label_cn} · priority {feature.priority?.toFixed(1) ?? "—"} ·{" "}
                  {feature.volume_recent.toLocaleString()} recent articles
                </p>
                {feature.headline && (
                  <a href={feature.headline_url} target="_blank" rel="noreferrer">
                    {feature.headline}
                  </a>
                )}
              </div>
            ))
          ) : (
            <p className={styles.emptyEvidence}>No recent news feature is mapped to this subcategory.</p>
          )}
        </section>
      </div>
    </article>
  );
}

export function ImpactForecastPage() {
  usePageTitle("Sales Impact Forecast");
  const forecast = useImpactForecast();
  const [selectedCategoryId, setSelectedCategoryId] = useState("");
  const [selectedSubcategoryId, setSelectedSubcategoryId] = useState("");
  const [year, setYear] = useState(4);
  const categories = forecast.data?.categories ?? [];
  const selectedCategory = categories.find((category) => category.id === selectedCategoryId) ?? categories[0];

  useEffect(() => {
    if (!selectedCategory) return;
    setSelectedCategoryId(selectedCategory.id);
    setSelectedSubcategoryId((current) =>
      selectedCategory.subcategories.some((item) => item.id === current)
        ? current
        : (selectedCategory.subcategories[0]?.id ?? ""),
    );
  }, [selectedCategory]);

  const categoryColor = useMemo(() => {
    const index = Math.max(
      categories.findIndex((category) => category.id === selectedCategory?.id),
      0,
    );
    return CATEGORY_COLORS[index % CATEGORY_COLORS.length];
  }, [categories, selectedCategory]);

  const chooseSubcategory = (id: string) => {
    setSelectedSubcategoryId(id);
    window.setTimeout(
      () => document.getElementById(`subcategory-${id}`)?.scrollIntoView({ behavior: "smooth", block: "center" }),
      0,
    );
  };

  return (
    <>
      <NavBar mockMode={config.useMocks} />
      <main className={styles.page}>
        <header className={styles.hero}>
          <div>
            <p className={styles.eyebrow}>Portfolio planning · Four-year scenario</p>
            <h1>Sales Impact Forecast</h1>
            <p className={styles.lead}>
              See how broad technology categories translate into subcategory scenarios, the exact Chinese-200 features
              behind the estimate, and the newest related signals detected in the news.
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

        {forecast.data && selectedCategory && (
          <>
            <section className={styles.categorySection} aria-labelledby="category-forecast-title">
              <div className={styles.sectionHeading}>
                <div>
                  <p className={styles.kicker}>Category outlook</p>
                  <h2 id="category-forecast-title">Four-year cumulative sales-uplift scenario</h2>
                </div>
                <span>Years after release</span>
              </div>
              <CategoryPlot categories={categories} />
              <div className={styles.legend}>
                {categories.map((category, index) => (
                  <button
                    key={category.id}
                    type="button"
                    className={selectedCategory.id === category.id ? styles.legendActive : ""}
                    onClick={() => setSelectedCategoryId(category.id)}
                    style={{ "--category-color": CATEGORY_COLORS[index % CATEGORY_COLORS.length] } as CSSProperties}
                  >
                    <i />
                    {category.label}
                    <b>+{valueAt(category.impact_by_year, 4)?.toFixed(1)}%</b>
                  </button>
                ))}
              </div>
            </section>

            <section
              className={styles.subcategorySection}
              style={{ "--category-color": categoryColor } as CSSProperties}
              aria-labelledby="subcategory-title"
            >
              <div className={styles.sectionHeading}>
                <div>
                  <p className={styles.kicker}>{selectedCategory.label}</p>
                  <h2 id="subcategory-title">Subcategory impact and evidence</h2>
                </div>
                <div className={styles.yearPicker} aria-label="Forecast horizon">
                  {[1, 2, 3, 4].map((item) => (
                    <button
                      key={item}
                      type="button"
                      className={year === item ? styles.yearActive : ""}
                      onClick={() => setYear(item)}
                    >
                      Y{item}
                    </button>
                  ))}
                </div>
              </div>
              <p className={styles.sectionIntro}>
                Bars use the mean of mapped legacy feature scenarios. “Signal only” means the subcategory is visible in
                current news but has no comparable Chinese-200 feature from which to estimate sales impact.
              </p>
              <SubcategoryPlot
                category={selectedCategory}
                year={year}
                selectedId={selectedSubcategoryId}
                onSelect={chooseSubcategory}
              />
            </section>

            <section className={styles.evidenceSection} aria-label="Feature evidence by subcategory">
              {selectedCategory.subcategories.map((subcategory) => (
                <EvidenceCard
                  key={subcategory.id}
                  subcategory={subcategory}
                  selected={subcategory.id === selectedSubcategoryId}
                />
              ))}
            </section>

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
