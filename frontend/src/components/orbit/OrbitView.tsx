import type { CSSProperties } from "react";
import { CATEGORIES, CATEGORY_KEYS, categoryColor, type CategoryKey } from "../../domain/categories";
import { STEP_IDS } from "../steps/PlannerSteps";
import styles from "./Orbit.module.css";

export interface OrbitNodeModel {
  key: CategoryKey;
  /** Text inside the ring: "45%", "Off", "Filter" or "–" while loading. */
  value: string;
  /** Ring fill 0–1. */
  progress: number;
  sub: string;
  off: boolean;
  ariaLabel: string;
}

interface Props {
  nodes: OrbitNodeModel[];
  selected: CategoryKey | null;
  onSelect?: (key: CategoryKey) => void;
  centerSub: string;
  headerRight: string;
  disabled?: boolean;
}

const RING_R = 44;
const RING_C = 2 * Math.PI * RING_R;
// SVG viewBox is 1000 × 656; the ellipse centre matches the orbit box centre.
const VB_W = 1000;
const VB_H = 656;
const CX = VB_W / 2;
const CY = VB_H / 2;

/** The "product management universe": sources orbit Product Management, as on the slide. */
export function OrbitView({ nodes, selected, onSelect, centerSub, headerRight, disabled }: Props) {
  return (
    <section id={STEP_IDS.sources} className={`card ${styles.stage}`} aria-label="Step 1: choose sources">
      <div className={styles.head}>
        <span className="eyebrow">1 · Choose sources</span>
        <span className="eyebrow">{headerRight}</span>
      </div>
      <div className={styles.orbit}>
        <svg viewBox={`0 0 ${VB_W} ${VB_H}`} preserveAspectRatio="none" aria-hidden="true">
          {nodes.map((n) => {
            const meta = CATEGORIES[n.key];
            if (!meta.weighted || n.off || n.progress <= 0) return null;
            const x2 = (meta.orbit.x / 100) * VB_W;
            const y2 = (meta.orbit.y / 100) * VB_H;
            // Spokes start outside the centre label so they never cross the text.
            return (
              <line
                key={n.key}
                x1={CX + (x2 - CX) * 0.6}
                y1={CY + (y2 - CY) * 0.6}
                x2={x2}
                y2={y2}
                stroke={categoryColor(n.key)}
                strokeOpacity={0.45}
                strokeWidth={1.5 + n.progress * 14}
                strokeLinecap="round"
                strokeDasharray={meta.evidence ? undefined : "2 9"}
              />
            );
          })}
          <ellipse
            cx={CX}
            cy={CY}
            rx={250}
            ry={205}
            fill="none"
            stroke="var(--orbit)"
            strokeWidth={1.5}
            vectorEffect="non-scaling-stroke"
          />
        </svg>
        <div className={styles.center}>
          <b>
            Product
            <br />
            Management
          </b>
          <span>{centerSub}</span>
        </div>
        {CATEGORY_KEYS.map((key) => {
          const n = nodes.find((x) => x.key === key);
          if (!n) return null;
          const meta = CATEGORIES[key];
          const classes = [
            styles.node,
            meta.evidence ? "" : styles.assumption,
            n.off ? styles.off : "",
            selected === key ? styles.selected : "",
          ].join(" ");
          return (
            <button
              key={key}
              type="button"
              className={classes}
              style={
                {
                  left: `${meta.orbit.x}%`,
                  top: `${meta.orbit.y}%`,
                  "--c": categoryColor(key),
                } as CSSProperties
              }
              onClick={() => onSelect?.(key)}
              aria-pressed={selected === key}
              aria-label={n.ariaLabel}
              disabled={disabled}
            >
              <span className={styles.ring}>
                <svg viewBox="0 0 100 100" aria-hidden="true">
                  <circle className={styles.disc} cx="50" cy="50" r="50" />
                  <circle className={styles.track} cx="50" cy="50" r={RING_R} />
                  <circle
                    className={styles.prog}
                    cx="50"
                    cy="50"
                    r={RING_R}
                    strokeDasharray={`${n.progress * RING_C} ${RING_C}`}
                    style={{ opacity: n.progress > 0 ? 1 : 0 }}
                  />
                </svg>
                <span className={`${styles.val} num`}>{n.value}</span>
              </span>
              <span className={`${styles.lbl} ${styles[meta.orbit.label]}`}>
                {meta.name}
                <small>{n.sub}</small>
              </span>
            </button>
          );
        })}
      </div>
      <div className={styles.legend}>
        <span>
          <i />
          Evidence
        </span>
        <span>
          <i className={styles.dash} />
          Assumption
        </span>
        <span>Ring = effective weight</span>
      </div>
    </section>
  );
}
