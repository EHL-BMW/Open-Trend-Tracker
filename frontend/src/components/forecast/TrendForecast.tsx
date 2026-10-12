import { TREND_TECHNOLOGY_GROUP } from "../../domain/categories";
import { selectedValues } from "../../domain/settings";
import { usePlanner } from "../../state/PlannerContext";
import { StateMessage } from "../common/StateMessage";
import styles from "./TrendForecast.module.css";

const pct = (x: number, digits = 0) => Number((x * 100).toFixed(digits));
const signedPct = (x: number, digits = 1) => `${x >= 0 ? "+" : ""}${pct(x, digits)}%`;

/** Signed range in steps of 5 percentage points, always including zero. */
function axisRange(values: number[]) {
  let lo = Math.min(0, Math.floor(Math.min(...values) * 20) / 20);
  let hi = Math.max(0, Math.ceil(Math.max(...values) * 20) / 20);
  if (hi - lo < 0.05) hi = lo + 0.05;
  return { lo, hi };
}

const seriesOf = (row: { currentShare: number; forecastShare: number; impactByYear?: { year: number; impact: number; pairs: number }[] }) =>
  row.impactByYear?.length
    ? row.impactByYear
    : [
        { year: 1, impact: row.currentShare, pairs: 0 },
        { year: 4, impact: row.forecastShare, pairs: 0 },
      ];

/** Every technology from the backend forecast: share today vs. forecast year. Rows toggle the filter. */
export function TrendForecast() {
  const { catalog, settings, dispatch } = usePlanner();
  const { trendForecast, forecastYear } = catalog;
  const labels = catalog.trendForecastLabels ?? {
    title: "Technology forecast",
    description: `Share of sampled China EV bestsellers offering each technology, today and estimated for ${forecastYear}.`,
    current: "Today",
    forecast: `${forecastYear} forecast`,
  };
  const techGroup = catalog.categories.trends.filters.find((g) => g.key === TREND_TECHNOLOGY_GROUP);
  const selected = selectedValues(settings, "trends", TREND_TECHNOLOGY_GROUP);
  const enabled = settings.enabled.trends;
  const toggleable = enabled && Boolean(techGroup);
  const rows = [...trendForecast].sort((a, b) => b.forecastShare - a.forecastShare || a.label.localeCompare(b.label));
  const values = rows.flatMap((row) => seriesOf(row).map((point) => point.impact));
  const range = axisRange(values.length ? values : [0]);
  const chart = { width: 300, height: 46, padX: 8, padY: 4 };
  const x = (year: number) => chart.padX + ((year - 1) / 3) * (chart.width - chart.padX * 2);
  const y = (impact: number) =>
    chart.padY + ((range.hi - impact) / (range.hi - range.lo)) * (chart.height - chart.padY * 2);

  const toggle = (technology: string) =>
    dispatch({ type: "toggleFilter", category: "trends", group: TREND_TECHNOLOGY_GROUP, value: technology });

  return (
    <section className={`card ${styles.card}`} aria-labelledby="forecast-title">
      <div className={styles.head}>
        <div>
          <h3 id="forecast-title">{labels.title}</h3>
          <p>
            {labels.description}
            {toggleable && " Click a row to include or exclude it."}
          </p>
        </div>
        <div className={styles.legend}>
          <span>
            <i className={styles.now} />
            Year 1
          </span>
          <span>
            <i className={styles.fut} />
            Year 4
          </span>
          <span>{catalog.impactCoverage ? `${catalog.impactCoverage.validPairCount}/${catalog.impactCoverage.collectionTarget} valid pairs` : "pp = percentage points"}</span>
        </div>
      </div>

      {rows.length === 0 ? (
        <StateMessage compact title="No forecast yet">
          The backend hasn&apos;t provided technology forecasts.
        </StateMessage>
      ) : (
        <div className={styles.grid} role="group" aria-label="Technologies">
          <span />
          <div className={styles.axis} aria-hidden="true">
            {[1, 2, 3, 4].map((year) => (
              <span key={year} style={{ left: `${((year - 1) / 3) * 100}%` }}>
                Y{year}
              </span>
            ))}
          </div>
          <span className={styles.latestHead}>Y4</span>
          {rows.map((r) => {
            const included = enabled && (!techGroup || selected.includes(r.technology));
            const series = seriesOf(r);
            const first = series[0]!;
            const last = series.at(-1)!;
            const delta = last.impact - first.impact;
            const points = series.map((point) => `${x(point.year)},${y(point.impact)}`).join(" ");
            const title = `${r.label}: ${series.map((point) => `Y${point.year} ${signedPct(point.impact)}`).join(", ")}`;
            return (
              <div
                key={r.technology}
                className={`${styles.row} ${included ? "" : styles.off}`}
                role={toggleable ? "checkbox" : undefined}
                aria-checked={toggleable ? included : undefined}
                tabIndex={toggleable ? 0 : undefined}
                title={title}
                onClick={toggleable ? () => toggle(r.technology) : undefined}
                onKeyDown={
                  toggleable
                    ? (e) => {
                        if (e.key === " " || e.key === "Enter") {
                          e.preventDefault();
                          toggle(r.technology);
                        }
                      }
                    : undefined
                }
              >
                <span className={styles.name}>{r.label}</span>
                <span className={styles.track}>
                  <svg viewBox={`0 0 ${chart.width} ${chart.height}`} preserveAspectRatio="none" aria-hidden="true">
                    <line className={styles.zero} x1="0" x2={chart.width} y1={y(0)} y2={y(0)} />
                    <polyline className={styles.seriesLine} points={points} />
                    {series.map((point, index) => (
                      <circle
                        key={point.year}
                        className={`${styles.seriesDot} ${index === 0 ? styles.seriesDotStart : ""}`}
                        cx={x(point.year)}
                        cy={y(point.impact)}
                        r="3"
                      />
                    ))}
                  </svg>
                </span>
                <span className={`${styles.delta} num`}>
                  <b>{signedPct(last.impact)}</b>
                  <small>Δ {delta >= 0 ? "+" : ""}{pct(delta, 1)} pp</small>
                </span>
              </div>
            );
          })}
        </div>
      )}
      <p className={styles.foot}>Observational sales associations. Sorted and ranked by Year 4 impact; click a row to include or exclude the feature.</p>
    </section>
  );
}
