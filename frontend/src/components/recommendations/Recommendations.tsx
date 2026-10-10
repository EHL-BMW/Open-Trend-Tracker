import type { CSSProperties } from "react";
import type { AnalysisRun, Recommendation, Spec } from "../../api/types";
import { categoryColor } from "../../domain/categories";
import { StateMessage } from "../common/StateMessage";
import styles from "./Recommendations.module.css";

interface Props {
  run: AnalysisRun | null;
  stale: boolean;
  running: boolean;
  error: string | null;
  canRun: boolean;
  onRun: () => void;
  onExplain: (recommendationId: string) => void;
}

const formatTime = (iso: string) => new Date(iso).toLocaleString([], { dateStyle: "medium", timeStyle: "short" });

export function Recommendations({ run, stale, running, error, canRun, onRun, onExplain }: Props) {
  return (
    <section aria-labelledby="recs-title" aria-busy={running}>
      <h2 id="recs-title" className={styles.title}>
        Top recommendations
      </h2>
      <div className={styles.bar}>
        <p className={styles.sub}>Each one lists the specs and trend technologies that produced its rank.</p>
        {run && (
          <p className={styles.meta}>
            Run {formatTime(run.createdAt)} · fingerprint <code>{run.fingerprint}</code> · data{" "}
            <code>{run.dataVersion}</code>
          </p>
        )}
      </div>

      {error && (
        <div className={styles.error} role="alert">
          <span>{error}</span>
          <button type="button" className="btn-link" onClick={onRun} disabled={!canRun || running}>
            Try again
          </button>
        </div>
      )}

      {run && stale && !running && (
        <div className={styles.stale} role="status">
          <span>Settings changed since this run. Run the analysis again to update the ranking.</span>
          <button type="button" className="btn-tinted" onClick={onRun} disabled={!canRun}>
            Run again
          </button>
        </div>
      )}

      <div className={`card ${styles.list} ${run && (stale || running) ? styles.dimmed : ""}`}>
        {!run ? (
          <StateMessage
            title={running ? "Running analysis…" : "No analysis yet"}
            action={
              !running && (
                <button type="button" className="btn-primary" onClick={onRun} disabled={!canRun}>
                  Run analysis
                </button>
              )
            }
          >
            Choose sources, weights and filters above, then run the analysis to get the Top 5 with their reasoning.
          </StateMessage>
        ) : run.recommendations.length === 0 ? (
          <StateMessage title="No recommendations for these settings">
            Switch on more sources or select more filter values, then run again.
          </StateMessage>
        ) : (
          <ol className={styles.items}>
            {run.recommendations.map((rec) => (
              <RecommendationRow key={rec.id} rec={rec} onExplain={() => onExplain(rec.id)} />
            ))}
          </ol>
        )}
      </div>
    </section>
  );
}

function RecommendationRow({ rec, onExplain }: { rec: Recommendation; onExplain: () => void }) {
  return (
    <li className={styles.rec}>
      <span className={`${styles.rank} ${rec.rank === 1 ? styles.first : ""} num`} aria-label={`Rank ${rec.rank}`}>
        {rec.rank}
      </span>
      <div className={styles.recTitle}>
        <h3>{rec.title}</h3>
        {rec.keep && <span className={`${styles.pill} ${styles.keep}`}>Keep</span>}
        {rec.assumptionShare > 0.005 && (
          <span className={`${styles.pill} ${styles.assume}`}>{Math.round(rec.assumptionShare * 100)}% assumption</span>
        )}
      </div>
      <div className={styles.side}>
        <span className={styles.score}>
          <b className="num">{rec.score.toFixed(1)}</b>
          <small>/ 100</small>
        </span>
        <button type="button" className="btn-tinted" onClick={onExplain} aria-label={`Show reasoning for ${rec.title}`}>
          Show reasoning
        </button>
      </div>
      <ul className={styles.specs} aria-label="What produced this rank">
        {rec.specs.map((spec, i) => (
          <SpecChip key={`${spec.category}-${i}`} spec={spec} />
        ))}
      </ul>
    </li>
  );
}

function SpecChip({ spec }: { spec: Spec }) {
  return (
    <li
      className={`${styles.spec} ${styles[spec.kind]}`}
      style={{ "--c": categoryColor(spec.category) } as CSSProperties}
    >
      <b>{spec.label}</b>
      <span>{spec.text}</span>
    </li>
  );
}
