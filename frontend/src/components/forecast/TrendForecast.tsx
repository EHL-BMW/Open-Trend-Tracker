import { TREND_TECHNOLOGY_GROUP } from "../../domain/categories";
import { selectedValues } from "../../domain/settings";
import { usePlanner } from "../../state/PlannerContext";
import { StateMessage } from "../common/StateMessage";
import styles from "./TrendForecast.module.css";

const pct = (x: number, digits = 0) => Number((x * 100).toFixed(digits));
/** Axis end in steps of 5 percentage points, so small uplifts are not squeezed into a 0–100% axis. */
const axisMax = (values: number[]) => Math.min(1, Math.max(0.05, Math.ceil(Math.max(0, ...values) * 20) / 20));

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
  const max = axisMax(rows.flatMap((r) => [r.currentShare, r.forecastShare]));
  const digits = max < 0.2 ? 1 : 0;
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((t) => t * max);

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
            {labels.current}
          </span>
          <span>
            <i className={styles.fut} />
            {labels.forecast}
          </span>
          <span>pp = percentage points</span>
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
            {ticks.map((t) => (
              <span key={t} style={{ left: `${(t / max) * 100}%` }}>
                {pct(t, digits)}%
              </span>
            ))}
          </div>
          <span />
          {rows.map((r) => {
            const included = enabled && (!techGroup || selected.includes(r.technology));
            const delta = Number((pct(r.forecastShare, digits) - pct(r.currentShare, digits)).toFixed(digits));
            const from = Math.min(r.currentShare, r.forecastShare);
            return (
              <div
                key={r.technology}
                className={`${styles.row} ${included ? "" : styles.off}`}
                role={toggleable ? "checkbox" : undefined}
                aria-checked={toggleable ? included : undefined}
                tabIndex={toggleable ? 0 : undefined}
                title={`${r.label}: ${pct(r.currentShare, digits)}% ${labels.current}, ${pct(r.forecastShare, digits)}% ${labels.forecast}`}
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
                  <span
                    className={styles.line}
                    style={{
                      left: `${(from / max) * 100}%`,
                      width: `${(Math.abs(r.forecastShare - r.currentShare) / max) * 100}%`,
                    }}
                  />
                  <span
                    className={`${styles.dot} ${styles.now}`}
                    style={{ left: `${(r.currentShare / max) * 100}%` }}
                  />
                  <span
                    className={`${styles.dot} ${styles.fut}`}
                    style={{ left: `${(r.forecastShare / max) * 100}%` }}
                  />
                </span>
                <span className={`${styles.delta} num`}>
                  {delta >= 0 ? "+" : "−"}
                  {Math.abs(delta)} pp
                </span>
              </div>
            );
          })}
        </div>
      )}
      <p className={styles.foot}>Forecasts are assumptions. Sorted by forecast; the ranking uses the forecast value.</p>
    </section>
  );
}
