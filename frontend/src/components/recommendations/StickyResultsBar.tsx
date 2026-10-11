import { useEffect, useState } from "react";
import type { AnalysisRun } from "../../api/types";
import { FOOTER_ID } from "../layout/Footer";
import { STEP_IDS } from "../steps/PlannerSteps";
import styles from "./StickyResultsBar.module.css";

interface Props {
  run: AnalysisRun;
  stale: boolean;
  running: boolean;
  canRun: boolean;
  onRun: () => void;
}

const HEADER_HEIGHT = 78;

/**
 * Slim bar fixed to the bottom while scrolling through the results: Top 5 at a glance plus Run.
 * Appears once the results heading has scrolled under the header; hides when the footer is in view.
 */
export function StickyResultsBar({ run, stale, running, canRun, onRun }: Props) {
  const [pastHeading, setPastHeading] = useState(false);
  const [footerVisible, setFooterVisible] = useState(false);

  // Position-based (not intersection events), so fast jumps past the heading are caught too.
  // Two cheap measurements per scroll event; React skips re-renders when nothing changes.
  useEffect(() => {
    const update = () => {
      const heading = document.getElementById("recs-title");
      const footer = document.getElementById(FOOTER_ID);
      setPastHeading(Boolean(heading && heading.getBoundingClientRect().bottom < HEADER_HEIGHT));
      setFooterVisible(Boolean(footer && footer.getBoundingClientRect().top < window.innerHeight));
    };
    update();
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    return () => {
      window.removeEventListener("scroll", update);
      window.removeEventListener("resize", update);
    };
  }, []);

  const visible = pastHeading && !footerVisible && run.recommendations.length > 0;
  const [first, ...rest] = run.recommendations;

  const backToResults = () => {
    const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    document.getElementById(STEP_IDS.results)?.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
  };

  return (
    <div className={`${styles.bar} ${visible ? styles.visible : ""}`} aria-hidden={!visible}>
      <div className={styles.inner}>
        <button
          type="button"
          className={styles.summary}
          onClick={backToResults}
          title="Back to the Top 5"
          tabIndex={visible ? undefined : -1}
        >
          <span className={styles.label}>Top 5</span>
          {first && (
            <span className={styles.first}>
              <span className={styles.rank}>1</span>
              <span className={styles.title}>{first.title}</span>
              <span className={`${styles.score} num`}>{first.score.toFixed(1)}</span>
            </span>
          )}
          <span className={styles.rest}>
            {rest.map((r) => (
              <span key={r.id} className={styles.restItem}>
                <span className={styles.restRank}>{r.rank}</span>
                {r.title}
              </span>
            ))}
          </span>
        </button>
        {stale && <span className={styles.stale}>Settings changed</span>}
        <button
          type="button"
          className={`btn-primary ${styles.run}`}
          onClick={onRun}
          disabled={!canRun || running}
          tabIndex={visible ? undefined : -1}
        >
          {running && <span className="spinner" aria-hidden="true" />}
          {running ? "Running…" : stale ? "Run again" : "Run analysis"}
        </button>
      </div>
    </div>
  );
}
