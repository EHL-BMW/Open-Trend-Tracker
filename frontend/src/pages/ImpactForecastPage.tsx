import { useEffect, useState, type CSSProperties } from "react";
import { useImpactForecast } from "../api/queries";
import type { ImpactCategory, ImpactExploratory } from "../api/types";
import { errorMessage } from "../api/client";
import { StateMessage } from "../components/common/StateMessage";
import { ExploratoryBundle, PanelToggle, type PanelId } from "../components/forecast/ExploratoryBundle";
import { Footer } from "../components/layout/Footer";
import { NavBar } from "../components/layout/NavBar";
import { TrackButton } from "../components/TrackButton";
import { config } from "../config";
import { featureClusters } from "../content/featureNews";
import { FeatureCard, type SavedProblemAnalysis } from "./FeatureTrendsPage";
import { legacyFeatureId } from "../state/trackedFeatures";
import { usePageTitle } from "./usePageTitle";
import styles from "./ImpactForecastPage.module.css";

const CATEGORY_COLORS = ["#0066b1", "#7b61a8", "#dc7b22", "#087e8b", "#c24c63", "#39805d", "#88743c"];
const colorAt = (index: number) => CATEGORY_COLORS[index % CATEGORY_COLORS.length]!;

type ImpactPoint = ImpactCategory["impact_by_year"][number];

function lastPoint(points: ImpactPoint[]) {
  return points.at(-1)!;
}

const signed = (value: number, digits = 1) => `${value >= 0 ? "+" : ""}${value.toFixed(digits)}%`;
const signedUnits = (value: number) => `${value >= 0 ? "+" : ""}${Math.round(value).toLocaleString()} vehicles`;

/** Latest estimate of a series, or a note when it did not pass the identification gates. */
const latestText = (points: ImpactPoint[]) =>
  points.length
    ? `${signedUnits(lastPoint(points).incremental_units ?? 0)} per nameplate (${signed(lastPoint(points).impact_pct)}) in year ${lastPoint(points).year}`
    : "effect not independently identified";

/** Exploratory points of one item in one panel, in the shape the charts draw. */
type ExploratoryLookup = (level: "category" | "subcategory" | "feature", id: string) => ImpactPoint[];

function exploratoryLookup(data: ImpactExploratory | null | undefined, panel: PanelId): ExploratoryLookup {
  const byKey = new Map((data?.items ?? []).map((item) => [`${item.level}:${item.id}`, item.panels[panel]]));
  return (level, id) => {
    const estimate = byKey.get(`${level}:${id}`);
    return (estimate?.by_year ?? []).map((point) => ({ ...point, nameplates: estimate!.nameplates_with }));
  };
}

// Exploratory intervals can reach thousands of percent; the axis stops here and the band is clipped.
const AXIS_MIN = -100;
const AXIS_MAX = 400;
const clamp = (value: number) => Math.min(AXIS_MAX, Math.max(AXIS_MIN, value));

/** Value range of a plot. It always includes zero because effects can be negative. */
function valueRange(raw: number[]) {
  if (!raw.length) return { lo: -1, hi: 1 };
  const values = raw.map(clamp);
  const lo = Math.min(0, ...values);
  const hi = Math.max(0, ...values);
  return hi - lo < 1 ? { lo, hi: lo + 1 } : { lo, hi };
}

function CategoryPlot({
  categories,
  seriesFor,
  dashed,
  selectedId,
  onSelect,
}: {
  categories: ImpactCategory[];
  seriesFor: (category: ImpactCategory) => ImpactPoint[];
  dashed: boolean;
  selectedId: string;
  onSelect: (id: string) => void;
}) {
  const width = 520;
  const height = 360;
  const pad = { left: 54, right: 58, top: 24, bottom: 48 };
  const { lo, hi } = valueRange(categories.flatMap((category) => seriesFor(category).map((point) => point.impact_pct)));
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
        const series = seriesFor(category);
        if (!series.length) return null;
        const color = colorAt(index);
        const points = series.map((point) => `${x(point.year)},${y(point.impact_pct)}`).join(" ");
        const selected = category.id === selectedId;
        const end = lastPoint(series);
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
              strokeDasharray={dashed ? "9 6" : undefined}
              strokeLinejoin="round"
              strokeLinecap="round"
            />
            {series.map((point) => (
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

function ImpactChart({
  points,
  lo,
  hi,
  color,
  dashed,
}: {
  points: ImpactPoint[];
  lo: number;
  hi: number;
  color: string;
  dashed: boolean;
}) {
  const width = 360;
  const height = 112;
  const pad = { left: 34, right: 10, top: 8, bottom: 20 };
  const x = (year: number) => pad.left + ((year - 1) / 3) * (width - pad.left - pad.right);
  const y = (value: number) =>
    pad.top + ((hi - Math.min(hi, Math.max(lo, value))) / (hi - lo)) * (height - pad.top - pad.bottom);
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
      <polyline
        points={line}
        fill="none"
        stroke={color}
        strokeWidth="2.5"
        strokeDasharray={dashed ? "6 4" : undefined}
        strokeLinejoin="round"
      />
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
  trackId,
  exploratory = false,
}: {
  title: string;
  meta: string;
  points: ImpactPoint[];
  range: { lo: number; hi: number };
  color: string;
  level: "subcategory" | "feature";
  trackId?: string;
  exploratory?: boolean;
}) {
  const last = lastPoint(points);
  const missingYears = [1, 2, 3, 4].filter((year) => !points.some((point) => point.year === year));
  if (exploratory) {
    return (
      <article
        className={`${styles.featureCard} ${styles.exploratoryCard} ${level === "subcategory" ? styles.subcategoryCard : ""}`}
      >
        <div className={styles.featureTop}>
          <div>
            <strong>{title}</strong>
            <span>{meta}</span>
          </div>
          <div className={styles.impactValue}>
            <b>{signed(last.impact_pct, 0)}</b>
            <span>
              Y{last.year} · 95% {signed(last.lower_pct ?? last.impact_pct, 0)} to{" "}
              {signed(last.upper_pct ?? last.impact_pct, 0)}
              {last.nameplates ? ` · ${last.nameplates} nameplates with it` : ""}
            </span>
          </div>
        </div>
        <ImpactChart points={points} lo={range.lo} hi={range.hi} color={color} dashed />
        {trackId && <TrackButton id={trackId} label={title} />}
      </article>
    );
  }
  return (
    <article className={`${styles.featureCard} ${level === "subcategory" ? styles.subcategoryCard : ""}`}>
      <div className={styles.featureTop}>
        <div>
          <strong>{title}</strong>
          <span>{meta}</span>
        </div>
        <div className={styles.impactValue}>
          <b>{signedUnits(last.incremental_units ?? 0)}</b>
          <span>
            {signed(last.impact_pct, 1)} · Y{last.year}
            {last.lower_units !== undefined && last.upper_units !== undefined
              ? ` · 95% range ${last.lower_units.toLocaleString()} to ${last.upper_units.toLocaleString()}`
              : ""}
            {last.nameplates ? ` · ${last.nameplates} nameplates` : ""}
          </span>
        </div>
      </div>
      <ImpactChart points={points} lo={range.lo} hi={range.hi} color={color} dashed={false} />
      {missingYears.length > 0 && (
        <p className={styles.missingYears}>
          Y{missingYears.join(", Y")} unavailable: each year needs observed sales from at least five pairs in this group
          and five comparison pairs.
        </p>
      )}
      {trackId && <TrackButton id={trackId} label={title} />}
    </article>
  );
}

function LegacyFeaturePanel({
  category,
  color,
  explore,
  panelLabel,
}: {
  category: ImpactCategory;
  color: string;
  explore: ExploratoryLookup;
  panelLabel: string;
}) {
  const groups = category.subcategories.filter((sub) => sub.impact_by_year || sub.legacy_features.length);
  const series = groups.flatMap((sub) => [
    sub.impact_by_year ?? explore("subcategory", sub.id),
    ...sub.legacy_features.map((feature) =>
      feature.impact_by_year.length ? feature.impact_by_year : explore("feature", feature.name),
    ),
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
          <p>
            Balanced independent panel · conditional event-study effect · band = clustered 95% interval. Dashed cards
            are exploratory launch-bundle associations ({panelLabel} panel), shown where no gated effect exists.
          </p>
        </div>
      </div>
      {groups.length ? (
        <div className={styles.featureList}>
          {groups.map((sub) => (
            <div key={sub.id}>
              {sub.impact_by_year ? (
                <ImpactCard
                  title={sub.label}
                  meta={`Subcategory · ${plural(sub.independent_nameplates, "independent nameplate")}`}
                  points={sub.impact_by_year}
                  range={range}
                  color={color}
                  level="subcategory"
                />
              ) : explore("subcategory", sub.id).length ? (
                <ImpactCard
                  title={sub.label}
                  meta={`Subcategory · exploratory · not identified: ${sub.identification_reason}`}
                  points={explore("subcategory", sub.id)}
                  range={range}
                  color={color}
                  level="subcategory"
                  exploratory
                />
              ) : (
                <p className={styles.emptyEvidence}>
                  {sub.label}: {sub.identification_reason} (
                  {plural(sub.independent_nameplates, "independent nameplate")}).
                </p>
              )}
              {sub.legacy_features.map((feature) =>
                feature.impact_by_year.length ? (
                  <ImpactCard
                    key={feature.name}
                    title={feature.name}
                    meta={`Feature · ${plural(feature.independent_nameplates, "independent nameplate")}`}
                    points={feature.impact_by_year}
                    range={range}
                    color={color}
                    level="feature"
                    trackId={legacyFeatureId(category.id, feature.name)}
                  />
                ) : explore("feature", feature.name).length ? (
                  <ImpactCard
                    key={feature.name}
                    title={feature.name}
                    meta={`Feature · exploratory · not identified: ${feature.identification_reason}`}
                    points={explore("feature", feature.name)}
                    range={range}
                    color={color}
                    level="feature"
                    trackId={legacyFeatureId(category.id, feature.name)}
                    exploratory
                  />
                ) : (
                  <div key={feature.name}>
                    <p className={styles.emptyEvidence}>
                      {feature.name}: {feature.identification_reason} (
                      {plural(feature.independent_nameplates, "independent nameplate")}).
                    </p>
                    <TrackButton id={legacyFeatureId(category.id, feature.name)} label={feature.name} />
                  </div>
                ),
              )}
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
  usePageTitle("Impact Analysis");
  const forecast = useImpactForecast();
  const [selectedId, setSelectedId] = useState("");
  const [panelId, setPanelId] = useState<PanelId>("strict");
  const [problems, setProblems] = useState<SavedProblemAnalysis | null>(null);
  useEffect(() => {
    fetch(`${config.apiBaseUrl}/agent/problems`)
      .then((response) => (response.ok ? response.json() : null))
      .then(setProblems)
      .catch(() => setProblems(null));
  }, []);
  const categories = forecast.data?.categories ?? [];
  const selected = categories.find((category) => category.id === selectedId) ?? categories[0];
  const activeId = selected?.id ?? "";
  const selectedIndex = categories.findIndex((category) => category.id === activeId);
  const selectedColor = colorAt(Math.max(selectedIndex, 0));
  const exploratory = forecast.data?.exploratory;
  const explore = exploratoryLookup(exploratory, panelId);
  const panelLabel = exploratory?.panels.find((panel) => panel.id === panelId)?.label ?? "";
  // Gated estimates win; exploratory lines are drawn only while no category passes the gates.
  const gated = categories.some((category) => category.impact_by_year.length);
  const showExploratory = !gated && categories.some((category) => explore("category", category.label).length);
  const seriesFor = (category: ImpactCategory) =>
    showExploratory ? explore("category", category.label) : category.impact_by_year;

  return (
    <>
      <NavBar mockMode={config.useMocks} />
      <main className={styles.page}>
        <header className={styles.hero}>
          <div>
            <p className={styles.eyebrow}>Portfolio planning · Sales change, years 1–4 after launch</p>
            <h1>Impact Analysis</h1>
            <p className={styles.lead}>
              Estimates appear only when independent nameplates separate a feature from market movement and its launch
              bundle. Unidentified effects stay unavailable instead of becoming an unsupported sales claim.
            </p>
          </div>
          {forecast.data && (
            <div className={styles.stats} aria-label="Forecast data coverage">
              <div>
                <b>{forecast.data.categories.length}</b>
                <span>categories</span>
              </div>
              <div>
                <b>
                  {forecast.data.complete_nameplate_count}/{forecast.data.independent_nameplate_count}
                </b>
                <span>complete / independent nameplates</span>
              </div>
              <div>
                <b>{forecast.data.isolated_feature_count}</b>
                <span>identified features</span>
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
            <div className={styles.workspace} style={{ "--category-color": selectedColor } as CSSProperties}>
              <section className={styles.panel} aria-labelledby="category-forecast-title">
                <div className={styles.panelHeading}>
                  <span className={styles.step}>1</span>
                  <div>
                    <h2 id="category-forecast-title">Category sales impact</h2>
                    <p>
                      {selected && showExploratory && seriesFor(selected).length
                        ? `${selected.label} · exploratory ${signed(lastPoint(seriesFor(selected)).impact_pct, 0)} in year ${lastPoint(seriesFor(selected)).year} (${panelLabel} panel)`
                        : selected
                          ? `${selected.label} · ${latestText(selected.impact_by_year)}`
                          : "Market-adjusted sales change vs pairs without the category · click a line to explore"}
                    </p>
                  </div>
                </div>
                {showExploratory && exploratory && (
                  <div className={styles.exploratoryNote}>
                    <span className={styles.exploratoryBadge}>Exploratory</span>
                    <p>
                      No effect passes the publication gates. Dashed lines are launch-bundle associations: launches that
                      included the category vs launches that did not. Not causal; see the caveats below.
                    </p>
                    <PanelToggle data={exploratory} panelId={panelId} onChange={setPanelId} />
                  </div>
                )}
                {gated || showExploratory ? (
                  <CategoryPlot
                    categories={categories}
                    seriesFor={seriesFor}
                    dashed={showExploratory}
                    selectedId={activeId}
                    onSelect={setSelectedId}
                  />
                ) : (
                  <StateMessage compact title="No four-year effect passes the evidence gates">
                    All {forecast.data.valid_pair_count} complete trim pairs were used, then repeated sales trajectories
                    were collapsed. The balanced analysis has {forecast.data.complete_observation_count} independent
                    trajectories across {forecast.data.complete_nameplate_count} nameplates—insufficient to separate a
                    feature from its launch bundle with acceptable uncertainty.
                  </StateMessage>
                )}
                <div className={styles.legend}>
                  {categories.map((category, index) => (
                    <button
                      key={category.id}
                      type="button"
                      className={category.id === activeId ? styles.legendActive : ""}
                      aria-pressed={category.id === activeId}
                      onClick={() => setSelectedId(category.id)}
                      style={{ "--category-color": colorAt(index) } as CSSProperties}
                    >
                      <i />
                      {category.label}
                      <b>
                        {seriesFor(category).length
                          ? `${signed(lastPoint(seriesFor(category)).impact_pct, 0)} · Y${lastPoint(seriesFor(category)).year}`
                          : "n/a"}
                      </b>
                    </button>
                  ))}
                </div>
              </section>

              {selected && (
                <LegacyFeaturePanel
                  category={selected}
                  color={selectedColor}
                  explore={explore}
                  panelLabel={panelLabel}
                />
              )}
              {selected && <NewsFeaturePanel category={selected} problems={problems} />}
            </div>

            {exploratory && (
              <ExploratoryBundle
                data={exploratory}
                selectedCategory={selected?.label}
                panelId={panelId}
                onPanelChange={setPanelId}
              />
            )}

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
