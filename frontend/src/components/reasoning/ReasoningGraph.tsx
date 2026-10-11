import type { Contribution, Recommendation } from "../../api/types";
import { CATEGORIES, categoryColor } from "../../domain/categories";
import styles from "./Reasoning.module.css";

const W = 880;
const ROW = 30;
const GAP = 18;
const TOP = 36;
const truncate = (s: string, n: number) => (s.length > n ? `${s.slice(0, n - 1)}…` : s);

interface Laid {
  c: Contribution;
  cy: number;
  records: { id: string; label: string; share: number; y: number }[];
}

/** Reverse tree drawn left to right: source records → source × weight → recommendation. */
export function ReasoningGraph({ rec }: { rec: Recommendation }) {
  const contributions = rec.reasoning.contributions
    .filter((c) => c.records.length > 0)
    .sort((a, b) => b.points - a.points);

  let y = TOP;
  const laid: Laid[] = contributions.map((c) => {
    const h = Math.max(c.records.length * ROW, 60);
    const offset = (h - c.records.length * ROW) / 2;
    const item: Laid = {
      c,
      cy: y + h / 2,
      records: c.records.map((r, j) => ({ ...r, y: y + offset + j * ROW + ROW / 2 })),
    };
    y += h + GAP;
    return item;
  });
  const H = Math.max(y - GAP + 10, 170);
  const resY = (TOP + H - 10) / 2;

  return (
    <svg
      className={styles.flow}
      viewBox={`0 0 ${W} ${H}`}
      role="img"
      aria-label={`Reasoning graph from source records to ${rec.title}`}
    >
      {[
        [0, "Source records"],
        [400, "Source × weight"],
        [680, "Result"],
      ].map(([x, t]) => (
        <text key={t} x={x} y={14} fontSize={11} className={styles.muted} letterSpacing=".06em">
          {String(t).toUpperCase()}
        </text>
      ))}

      {laid.map(({ c, cy, records }) => {
        const color = categoryColor(c.category);
        const dashed = !CATEGORIES[c.category].evidence;
        return (
          <g key={c.category}>
            {records.map((r) => (
              <path
                key={`l-${r.id}`}
                d={`M330 ${r.y} C365 ${r.y} 365 ${cy} 400 ${cy}`}
                fill="none"
                style={{ stroke: color }}
                strokeOpacity={0.55}
                strokeWidth={1 + 5 * r.share}
              />
            ))}
            <path
              d={`M600 ${cy} C640 ${cy} 640 ${resY} 680 ${resY}`}
              fill="none"
              style={{ stroke: color }}
              strokeOpacity={0.7}
              strokeWidth={2 + c.points * 0.3}
              strokeDasharray={dashed ? "6 5" : undefined}
            />
            {records.map((r) => (
              <g key={`r-${r.id}`}>
                <title>{r.label}</title>
                <rect x={0} y={r.y - 12} width={330} height={24} rx={8} style={{ fill: "var(--card)" }} />
                <text x={10} y={r.y + 4} fontSize={11.5} className={`${styles.mono} ${styles.muted}`}>
                  {r.id}
                </text>
                <text x={62} y={r.y + 4} fontSize={12}>
                  {truncate(r.label, 46)}
                </text>
              </g>
            ))}
            <rect
              x={400}
              y={cy - 28}
              width={200}
              height={56}
              rx={14}
              style={{ fill: "var(--card)", stroke: color }}
              strokeWidth={1.5}
              strokeDasharray={dashed ? "5 4" : undefined}
            />
            <text x={414} y={cy - 6} fontSize={13.5} fontWeight={600}>
              {truncate(CATEGORIES[c.category].name, 24)}
            </text>
            <text x={414} y={cy + 13} fontSize={12} className={styles.muted}>
              {c.points.toFixed(1)} pts · {c.categoryScore.toFixed(0)} × {Math.round(c.weight * 100)}%
              {dashed ? " · assumption" : ""}
            </text>
          </g>
        );
      })}

      <rect x={680} y={resY - 56} width={200} height={112} rx={18} style={{ fill: "var(--blue)" }} />
      <text x={696} y={resY - 26} fontSize={12} style={{ fill: "#fff" }} opacity={0.85}>
        Recommendation
      </text>
      <text x={696} y={resY - 6} fontSize={13.5} fontWeight={600} style={{ fill: "#fff" }}>
        {truncate(rec.title, 26)}
      </text>
      <text x={696} y={resY + 34} fontSize={30} fontWeight={600} style={{ fill: "#fff" }}>
        {rec.score.toFixed(1)}
      </text>
      <text x={766} y={resY + 34} fontSize={12} style={{ fill: "#fff" }} opacity={0.85}>
        of 100
      </text>
    </svg>
  );
}
