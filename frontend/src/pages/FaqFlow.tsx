import styles from "./FaqPage.module.css";

interface Step {
  title: string;
  detail?: string;
  tone?: "accent" | "warn";
}

/** Vertical flow chart; an array inside `steps` is drawn as parallel branches. */
export function Flow({ steps, label }: { steps: (Step | Step[])[]; label: string }) {
  const box = (step: Step) => (
    <div
      key={step.title}
      className={`${styles.flowStep} ${step.tone === "accent" ? styles.flowAccent : ""} ${
        step.tone === "warn" ? styles.flowWarn : ""
      }`}
    >
      <div className={styles.flowTitle}>{step.title}</div>
      {step.detail && <div className={styles.flowDetail}>{step.detail}</div>}
    </div>
  );
  return (
    <div className={styles.flow} role="img" aria-label={label}>
      {steps.map((step, index) => (
        <div key={index} className={styles.flowRow}>
          {index > 0 && (
            <div className={styles.flowArrow} aria-hidden="true">
              ↓
            </div>
          )}
          {Array.isArray(step) ? <div className={styles.flowBranch}>{step.map(box)}</div> : box(step)}
        </div>
      ))}
    </div>
  );
}
