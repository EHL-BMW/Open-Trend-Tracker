import { CheckIcon } from "../common/Icons";
import styles from "./PlannerSteps.module.css";

export const STEP_IDS = { sources: "step-sources", settings: "step-settings", results: "results" } as const;

interface Props {
  /** A run exists and matches the current settings. */
  hasFreshResults: boolean;
  running: boolean;
  canRun: boolean;
  onRun: () => void;
}

const scrollTo = (id: string) => {
  const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
  document.getElementById(id)?.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
};

/** Guided flow: ① Sources → ② Weights & filters → ③ Run → ④ Review, with live status. */
export function PlannerSteps({ hasFreshResults, running, canRun, onRun }: Props) {
  const steps = [
    { n: 1, label: "Choose sources", hint: "Switch sources on or off", go: () => scrollTo(STEP_IDS.sources) },
    { n: 2, label: "Set weights & filters", hint: "Tune what counts", go: () => scrollTo(STEP_IDS.settings) },
    { n: 3, label: "Run the analysis", hint: running ? "Running…" : "Get the Top 5", go: onRun, isRun: true },
    { n: 4, label: "Review the Top 5", hint: "With reasoning", go: () => scrollTo(STEP_IDS.results) },
  ];
  // Before a run (or after settings changed) step 3 is next; with fresh results step 4 is.
  const current = hasFreshResults ? 4 : 3;

  return (
    <nav aria-label="Planner steps">
      <ol className={styles.steps}>
        {steps.map((s) => {
          const done = s.n < current && hasFreshResults;
          const state = done ? styles.done : s.n === current ? styles.current : "";
          return (
            <li key={s.n}>
              <button
                type="button"
                className={`${styles.step} ${state}`}
                onClick={s.go}
                disabled={s.isRun ? !canRun || running : false}
                aria-current={s.n === current ? "step" : undefined}
              >
                <span className={styles.badge} aria-hidden="true">
                  {s.isRun && running ? (
                    <span className="spinner" />
                  ) : done ? (
                    <CheckIcon className={styles.check} />
                  ) : (
                    s.n
                  )}
                </span>
                <span className={styles.text}>
                  <span className={styles.label}>{s.label}</span>
                  <span className={styles.hint}>{s.hint}</span>
                </span>
              </button>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
