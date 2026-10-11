import { useEffect, useRef, type CSSProperties } from "react";
import type { AnalysisRun, ContextItem, Contribution, Recommendation } from "../../api/types";
import { CATEGORIES, WEIGHTED_KEYS, categoryColor } from "../../domain/categories";
import { CloseIcon } from "../common/Icons";
import { ReasoningGraph } from "./ReasoningGraph";
import styles from "./Reasoning.module.css";

interface Props {
  run: AnalysisRun;
  recommendation: Recommendation | null;
  onClose: () => void;
}

const CONFIDENCE_LABEL = {
  "evidence-led": "Evidence-led",
  mixed: "Mixed",
  "assumption-led": "Assumption-led",
} as const;

/** Modal sheet that explains one recommendation, with the graph and every cited source. */
export function ReasoningSheet({ run, recommendation, onClose }: Props) {
  const dialog = useRef<HTMLDialogElement>(null);
  const body = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = dialog.current;
    if (!el) return;
    if (recommendation && !el.open) el.showModal();
    if (!recommendation && el.open) el.close();
    if (recommendation && body.current) body.current.scrollTop = 0;
  }, [recommendation]);

  // Native listener: covers Esc, the close button and backdrop clicks alike.
  const onCloseRef = useRef(onClose);
  onCloseRef.current = onClose;
  useEffect(() => {
    const el = dialog.current;
    if (!el) return;
    const handle = () => onCloseRef.current();
    el.addEventListener("close", handle);
    return () => el.removeEventListener("close", handle);
  }, []);

  return (
    <dialog
      ref={dialog}
      className={styles.dialog}
      aria-labelledby="sheet-title"
      onClick={(e) => {
        // A click on the dimmed backdrop lands on the dialog element itself.
        if (e.target === dialog.current) dialog.current?.close();
      }}
    >
      {recommendation && (
        <div ref={body} className={styles.sheet}>
          <SheetContent run={run} rec={recommendation} onClose={() => dialog.current?.close()} />
        </div>
      )}
    </dialog>
  );
}

function SheetContent({ run, rec, onClose }: { run: AnalysisRun; rec: Recommendation; onClose: () => void }) {
  const { reasoning } = rec;
  const cited = [...reasoning.contributions, ...reasoning.context].reduce((s, c) => s + c.records.length, 0);
  const contributions = [...reasoning.contributions].sort((a, b) => b.points - a.points);

  return (
    <>
      <div className={styles.head}>
        <span className={`${styles.rank} ${rec.rank === 1 ? styles.first : ""} num`}>{rec.rank}</span>
        <div className={styles.grow}>
          <span className="eyebrow">
            Recommendation {rec.rank} of {run.recommendations.length}
          </span>
          <h2 id="sheet-title">{rec.title}</h2>
        </div>
        <button type="button" className="icon-btn" onClick={onClose} aria-label="Close">
          <CloseIcon />
        </button>
      </div>

      <p className={styles.verdict}>{reasoning.verdict}</p>

      <div className={styles.kpis}>
        <div className={styles.kpi}>
          <span>Score</span>
          <b className="num">{rec.score.toFixed(1)}</b>
        </div>
        <div className={styles.kpi}>
          <span>{CONFIDENCE_LABEL[reasoning.confidence]}</span>
          <b className="num">{Math.round(reasoning.evidenceShare * 100)}% evidence</b>
          <div className={styles.split} aria-hidden="true">
            <div style={{ width: `${reasoning.evidenceShare * 100}%`, background: "var(--blue)" }} />
            <div style={{ width: `${(1 - reasoning.evidenceShare) * 100}%`, background: "var(--c-trends)" }} />
          </div>
        </div>
        <div className={styles.kpi}>
          <span>Sources cited</span>
          <b className="num">{cited} records</b>
        </div>
      </div>

      <h3 className={styles.h3}>How the rank was built</h3>
      <div className={styles.flowWrap}>
        <ReasoningGraph rec={rec} />
      </div>

      <h3 className={styles.h3}>Why, source by source</h3>
      <div className={styles.why}>
        {contributions.map((c) => (
          <WhyCard key={c.category} item={c} />
        ))}
        {reasoning.context.map((c) => (
          <WhyCard key={`ctx-${c.category}`} item={c} />
        ))}
      </div>

      <h3 className={styles.h3}>Signals to check</h3>
      <ul className={styles.flags}>
        {reasoning.flags.length === 0 ? (
          <li className={styles.ok}>No conflicting or missing signals.</li>
        ) : (
          reasoning.flags.map((f, i) => (
            <li key={i} className={styles[f.severity]}>
              {f.message}
            </li>
          ))
        )}
      </ul>

      <p className={styles.foot}>
        Reproducible: Run ID <code>{run.fingerprint}</code> · weights{" "}
        {WEIGHTED_KEYS.map(
          (k) =>
            `${CATEGORIES[k].name} ${run.request.enabled[k] ? `${Math.round(run.effectiveWeights[k] * 100)}%` : "off"}`,
        ).join(", ")}
        .
      </p>
    </>
  );
}

function WhyCard({ item }: { item: Contribution | ContextItem }) {
  const meta = CATEGORIES[item.category];
  const isContribution = "points" in item;
  return (
    <div
      className={`${styles.whyCard} ${meta.evidence ? "" : styles.assumptionCard}`}
      style={{ "--c": categoryColor(item.category) } as CSSProperties}
    >
      <div className={styles.whyTop}>
        <b>
          {meta.name} {!meta.evidence && <span className="tag-assume">Assumption</span>}
        </b>
        {isContribution ? (
          <span className={`${styles.calc} num`}>
            score {item.categoryScore.toFixed(0)} × {(item.weight * 100).toFixed(1)}% weight ={" "}
            <b>{item.points.toFixed(1)} pts</b>
          </span>
        ) : (
          <span className={styles.calc}>Context only · not weighted</span>
        )}
      </div>
      <p>{item.summary}</p>
      {item.records.length > 0 && (
        <div className={styles.cites}>
          {item.records.map((r) => (
            <span key={r.id} className={styles.cite}>
              <b>{r.id}</b> {r.label}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
