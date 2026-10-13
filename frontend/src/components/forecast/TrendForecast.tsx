import { useState } from "react";
import { Link } from "react-router-dom";
import { errorMessage } from "../../api/client";
import { useImpactForecast } from "../../api/queries";
import type { ImpactForecast } from "../../api/types";
import { ROUTES } from "../../routes";
import { legacyFeatureId } from "../../state/trackedFeatures";
import { FeatureSourceBadge } from "../FeatureSourceBadge";
import { TrackButton } from "../TrackButton";
import { StateMessage } from "../common/StateMessage";
import styles from "./TrendForecast.module.css";

type Point = { year: number; impact: number };
type Row = { id: string; label: string; pairCount: number; points: Point[]; exploratory: boolean };
const signedPct = (value: number) => `${value >= 0 ? "+" : ""}${value.toFixed(1)}%`;

/** Historical pairs supply the sales evidence; news topics remain separate Planner filters. */
function legacyRows(data: ImpactForecast): Row[] {
  const strict = new Map(
    (data.exploratory?.items ?? [])
      .filter((item) => item.level === "feature" && item.panels.strict)
      .map((item) => [`${item.category}:${item.id}`, item.panels.strict!.by_year] as const),
  );
  return data.categories.flatMap((category) =>
    category.subcategories.flatMap((sub) =>
      sub.legacy_features.flatMap((feature) => {
        const direct = feature.impact_by_year;
        const comparison = strict.get(`${category.label}:${feature.name}`) ?? [];
        const points = (direct.length ? direct : comparison).map((point) => ({
          year: point.year,
          impact: point.impact_pct,
        }));
        return points.length
          ? [{ id: legacyFeatureId(category.id, feature.name), label: feature.name,
               pairCount: feature.pair_count, points, exploratory: direct.length === 0 }]
          : [];
      }),
    ),
  ).sort((a, b) => b.pairCount - a.pairCount || a.label.localeCompare(b.label));
}

function axisRange(values: number[]) {
  const lo = Math.min(0, Math.floor(Math.min(...values) / 5) * 5);
  let hi = Math.max(0, Math.ceil(Math.max(...values) / 5) * 5);
  if (hi - lo < 5) hi = lo + 5;
  return { lo, hi };
}

export function TrendForecast() {
  const [excluded, setExcluded] = useState<string[]>([]);
  const forecast = useImpactForecast();
  const data = forecast.data;
  const rows = data ? legacyRows(data) : [];
  const chart = { width: 300, height: 46, padX: 8, padY: 4 };
  const x = (year: number) => chart.padX + ((year - 1) / 3) * (chart.width - chart.padX * 2);
  const toggle = (id: string) => setExcluded((current) => current.includes(id) ? current.filter((item) => item !== id) : [...current, id]);

  return (
    <section className={`card ${styles.card}`} aria-labelledby="forecast-title">
      <div className={styles.head}>
        <div>
          <h3 id="forecast-title">Legacy feature sales evidence</h3>
          <p>Four-year comparisons from historical Chinese vehicle version pairs. Select the legacy features you want to compare.</p>
        </div>
        <div className={styles.legend}>
          <span><i className={styles.now} />Year 1</span>
          <span><i className={styles.fut} />Year 4</span>
          {data && <span>{data.isolated_feature_count}/{data.legacy_feature_count} independently estimated</span>}
        </div>
      </div>

      {forecast.isLoading ? (
        <StateMessage compact title="Loading historical feature evidence">Reading the paired vehicle records…</StateMessage>
      ) : forecast.isError ? (
        <StateMessage compact tone="error" title="Historical evidence unavailable">{errorMessage(forecast.error)}</StateMessage>
      ) : rows.length === 0 ? (
        <StateMessage compact title="No feature-level series available">The paired records do not currently support a four-year feature comparison.</StateMessage>
      ) : (
        <>
          {data?.isolated_feature_count === 0 && (
            <p className={styles.caution}>No legacy feature has an independently identified sales effect yet. The dashed lines below are exploratory launch-bundle associations, not sales forecasts.</p>
          )}
          <div className={styles.grid} role="group" aria-label="Historical legacy features">
            <span />
            <div className={styles.axis} aria-hidden="true">
              {[1, 2, 3, 4].map((year) => <span key={year} style={{ left: `${((year - 1) / 3) * 100}%` }}>Y{year}</span>)}
            </div>
            <span className={styles.latestHead}>Y4</span>
            {rows.map((row) => {
              const included = !excluded.includes(row.id);
              const first = row.points[0]!;
              const last = row.points.at(-1)!;
              const delta = last.impact - first.impact;
              const range = axisRange(row.points.map((point) => point.impact));
              const y = (impact: number) => chart.padY + ((range.hi - impact) / (range.hi - range.lo)) * (chart.height - chart.padY * 2);
              const points = row.points.map((point) => `${x(point.year)},${y(point.impact)}`).join(" ");
              const title = `${row.label}: ${row.points.map((point) => `Y${point.year} ${signedPct(point.impact)}`).join(", ")}`;
              return (
                <div
                  key={row.id}
                  className={`${styles.row} ${included ? "" : styles.off}`}
                  role="checkbox"
                  aria-checked={included}
                  aria-label={`Include ${row.label} in legacy feature comparison`}
                  tabIndex={0}
                  title={title}
                  onClick={() => toggle(row.id)}
                  onKeyDown={(event) => {
                    if (event.key === " " || event.key === "Enter") {
                      event.preventDefault();
                      toggle(row.id);
                    }
                  }}
                >
                  <span className={styles.name}>
                    <span className={styles.selection} aria-hidden="true">{included ? "✓" : ""}</span>
                    <strong>{row.label}</strong>
                    <span className={styles.rowActions}>
                      <FeatureSourceBadge source="legacy" />
                      <TrackButton id={row.id} label={row.label} compact />
                    </span>
                  </span>
                  <span className={styles.track}>
                    <svg viewBox={`0 0 ${chart.width} ${chart.height}`} aria-hidden="true">
                      <line className={styles.zero} x1="0" x2={chart.width} y1={y(0)} y2={y(0)} />
                      <polyline className={`${styles.seriesLine} ${row.exploratory ? styles.exploratoryLine : ""}`} points={points} />
                      {row.points.map((point, index) => (
                        <circle key={point.year} className={`${styles.seriesDot} ${index === 0 ? styles.seriesDotStart : ""} ${row.exploratory ? styles.exploratoryDot : ""}`} cx={x(point.year)} cy={y(point.impact)} r="3" />
                      ))}
                    </svg>
                  </span>
                  <span className={`${styles.delta} num ${row.exploratory ? styles.exploratoryDelta : ""}`}>
                    <b>{signedPct(last.impact)}</b>
                    {row.exploratory && <small>exploratory</small>}
                    <small>Δ {delta >= 0 ? "+" : ""}{delta.toFixed(1)} pp</small>
                  </span>
                </div>
              );
            })}
          </div>
        </>
      )}
      <p className={styles.foot}>
        These are historical legacy features. Exploratory lines may reflect other changes in the same launch bundle and are not scored as feature-level sales effects. Selecting a row controls this comparison only. <Link to={ROUTES.impactForecast}>See Impact Analysis →</Link>
      </p>
    </section>
  );
}
