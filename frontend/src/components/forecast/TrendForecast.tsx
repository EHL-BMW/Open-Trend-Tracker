import { TREND_TECHNOLOGY_GROUP } from "../../domain/categories";
import { selectedValues } from "../../domain/settings";
import { usePlanner } from "../../state/PlannerContext";
import { StateMessage } from "../common/StateMessage";
import styles from "./TrendForecast.module.css";

const pct = (x: number) => Math.round(x * 100);
const TICKS = [0, 25, 50, 75, 100];

/** Every technology from the backend forecast: share today vs. forecast year. Rows toggle the filter. */
export function TrendForecast() {
  const { catalog, settings, dispatch } = usePlanner();
  const { trendForecast, forecastYear } = catalog;
  const techGroup = catalog.categories.trends.filters.find((g) => g.key === TREND_TECHNOLOGY_GROUP);
  const selected = selectedValues(settings, "trends", TREND_TECHNOLOGY_GROUP);
  const enabled = settings.enabled.trends;
  const toggleable = enabled && Boolean(techGroup);
  const rows = [...trendForecast].sort((a, b) => b.forecastShare - a.forecastShare || a.label.localeCompare(b.label));

  const toggle = (technology: string) =>
    dispatch({ type: "toggleFilter", category: "trends", group: TREND_TECHNOLOGY_GROUP, value: technology });

  return (
    <section className={`card ${styles.card}`} aria-labelledby="forecast-title">
      <div className={styles.head}>
        <div>
          <h3 id="forecast-title">Technology forecast</h3>
          <p>
            Share of sampled China EV bestsellers offering each technology, today and estimated for {forecastYear}.
            {toggleable && " Click a row to include or exclude it."}
          </p>
        </div>
        <div className={styles.legend}>
          <span>
            <i className={styles.now} />
            Today
          </span>
          <span>
            <i className={styles.fut} />
            {forecastYear} forecast
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
            {TICKS.map((t) => (
              <span key={t} style={{ left: `${t}%` }}>
                {t}%
              </span>
            ))}
          </div>
          <span />
          {rows.map((r) => {
            const included = enabled && (!techGroup || selected.includes(r.technology));
            const delta = pct(r.forecastShare) - pct(r.currentShare);
            const from = Math.min(r.currentShare, r.forecastShare);
            return (
              <div
                key={r.technology}
                className={`${styles.row} ${included ? "" : styles.off}`}
                role={toggleable ? "checkbox" : undefined}
                aria-checked={toggleable ? included : undefined}
                tabIndex={toggleable ? 0 : undefined}
                title={`${r.label}: ${pct(r.currentShare)}% today, ${pct(r.forecastShare)}% by ${forecastYear}`}
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
                    style={{ left: `${from * 100}%`, width: `${Math.abs(r.forecastShare - r.currentShare) * 100}%` }}
                  />
                  <span className={`${styles.dot} ${styles.now}`} style={{ left: `${r.currentShare * 100}%` }} />
                  <span className={`${styles.dot} ${styles.fut}`} style={{ left: `${r.forecastShare * 100}%` }} />
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
