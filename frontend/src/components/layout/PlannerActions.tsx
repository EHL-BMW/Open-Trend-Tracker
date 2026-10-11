import AnimatedButton from "../ui/animated-button";
import styles from "./PlannerActions.module.css";

interface Props {
  canReset: boolean;
  onReset?: () => void;
  canRun: boolean;
  running: boolean;
  runHint?: string;
  onRun?: () => void;
}

/** Reset + Run analysis for the planner page, shown on the right of the nav bar. */
export function PlannerActions({ canReset, onReset, canRun, running, runHint, onRun }: Props) {
  return (
    <>
      <button type="button" className={`btn-link ${styles.reset}`} onClick={onReset} disabled={!canReset}>
        Reset
      </button>
      <AnimatedButton
        type="button"
        className={styles.run}
        onClick={onRun}
        disabled={!canRun || running}
        title={runHint}
        aria-keyshortcuts="Control+Enter Meta+Enter"
      >
        {running && <span className="spinner" aria-hidden="true" />}
        {running ? "Running…" : "Run analysis"}
      </AnimatedButton>
    </>
  );
}
