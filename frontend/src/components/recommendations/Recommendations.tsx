import type { CSSProperties } from "react";
import type { AnalysisRun, Recommendation, Spec } from "../../api/types";
import { CATEGORIES, categoryColor } from "../../domain/categories";
import { RollingNumber } from "../common/RollingNumber";
import { StateMessage } from "../common/StateMessage";
import AnimatedTooltip from "../ui/animated-tooltip";
import GlowBorderCard from "../ui/glow-border-card";
import { STEP_IDS } from "../steps/PlannerSteps";
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
    <section id={STEP_IDS.results} className={styles.section} aria-labelledby="recs-title" aria-busy={running}>
      <p className={`eyebrow ${styles.step}`}>4 · Review</p>
      <h2 id="recs-title" className={styles.title}>
        Top recommendations
      </h2>
      <div className={styles.bar}>
        <p className={styles.sub}>Each one lists the specs and trend technologies that produced its rank.</p>
        {run && (
          <p className={styles.meta}>
            Run {formatTime(run.createdAt)} · Run ID{" "}
            <code title="The same settings and data always reproduce this exact Top 5. Find this run again in the run history.">
              {run.fingerprint}
            </code>
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

      {run && run.recommendations.length > 0 ? (
        <ol className={`${styles.items} ${stale || running ? styles.dimmed : ""}`}>
          {run.recommendations.map((rec) => (
            <RecommendationRow key={rec.id} rec={rec} onExplain={() => onExplain(rec.id)} />
          ))}
        </ol>
      ) : (
        <div className={`card ${styles.list}`}>
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
          ) : (
            <StateMessage title="No recommendations for these settings">
              Switch on more sources or select more filter values, then run again.
            </StateMessage>
          )}
        </div>
      )}
    </section>
  );
}

/** Calm blue glow for the top pick (Vengeance GlowBorderCard). */
const TOP_PICK_GLOW = [
  "#0071e3",
  "#2b8cff",
  "#5ac8fa",
  "#0a84ff",
  "#64d2ff",
  "#0071e3",
  "#3a7bd5",
  "#5ac8fa",
  "#2b8cff",
  "#0071e3",
];

function RecommendationRow({ rec, onExplain }: { rec: Recommendation; onExplain: () => void }) {
  const body = <RecommendationBody rec={rec} onExplain={onExplain} />;
  if (rec.rank !== 1) return <li className={`${styles.rec} ${styles.card}`}>{body}</li>;
  return (
    <li className={styles.featured}>
      <GlowBorderCard
        className={styles.glow}
        width="100%"
        aspectRatio="auto"
        borderRadius="22px"
        borderWidth="0.45em"
        blurAmount="0.7em"
        inset="-0.2em"
        animationDuration={7}
        gradientColors={TOP_PICK_GLOW}
      >
        <div className={styles.rec}>{body}</div>
      </GlowBorderCard>
    </li>
  );
}

function RecommendationBody({ rec, onExplain }: { rec: Recommendation; onExplain: () => void }) {
  return (
    <>
      <span className={`${styles.rank} ${rec.rank === 1 ? styles.first : ""} num`} aria-label={`Rank ${rec.rank}`}>
        {rec.rank}
      </span>
      <div className={styles.recTitle}>
        <h3>{rec.title}</h3>
        {rec.keep && <span className={`${styles.pill} ${styles.keep}`}>Keep · praised by customers</span>}
        {rec.assumptionShare > 0.005 && (
          <span className={`${styles.pill} ${styles.assume}`}>
            {Math.round(rec.assumptionShare * 100)}% from trends
          </span>
        )}
      </div>
      <div className={styles.side}>
        <span className={styles.score}>
          <b className="num">
            <RollingNumber value={rec.score} decimals={1} />
          </b>
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
    </>
  );
}

function SpecChip({ spec }: { spec: Spec }) {
  return (
    <li
      className={`${styles.spec} ${styles[spec.kind]}`}
      style={{ "--c": categoryColor(spec.category) } as CSSProperties}
    >
      <AnimatedTooltip content={chipHint(spec)} variant="indis" accentColor="var(--blue)" triggerClassName="">
        <b>{CATEGORIES[spec.category].chipLabel}</b>
      </AnimatedTooltip>
      <span>{spec.text}</span>
    </li>
  );
}

/** Plain-language meaning of each chip, shown in its tooltip. */
function chipHint(spec: Spec): string {
  if (spec.kind === "missing") return "No matching records in this source, so it adds nothing to the score.";
  switch (spec.category) {
    case "sales":
      return "Sales evidence: model lines and powertrains where this sells.";
    case "customer":
      return "Customer evidence: how often customers raise it as a pain point or praise it.";
    case "features":
      return "Product: what existing BMW cars already offer. Context only, not weighted.";
    case "trends":
      return "Trend forecast from China EV bestsellers. An assumption, not evidence.";
  }
}
