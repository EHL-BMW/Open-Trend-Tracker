import styles from "./NavBar.module.css";

interface Props {
  mockMode: boolean;
  canReset: boolean;
  onReset?: () => void;
  canRun: boolean;
  running: boolean;
  runHint?: string;
  onRun?: () => void;
}

export function NavBar({ mockMode, canReset, onReset, canRun, running, runHint, onRun }: Props) {
  return (
    <nav className={styles.nav} aria-label="Main">
      <div className={styles.inner}>
        <div className={styles.title}>
          Series Improvement Planner
          {mockMode && (
            <span className={styles.badge} title="Running against the built-in mock backend">
              Mock backend
            </span>
          )}
        </div>
        <button type="button" className="btn-link" onClick={onReset} disabled={!canReset}>
          Reset
        </button>
        <button
          type="button"
          className="btn-primary"
          onClick={onRun}
          disabled={!canRun || running}
          title={runHint}
          aria-keyshortcuts="Control+Enter Meta+Enter"
        >
          {running && <span className="spinner" aria-hidden="true" />}
          {running ? "Running…" : "Run analysis"}
        </button>
      </div>
    </nav>
  );
}
