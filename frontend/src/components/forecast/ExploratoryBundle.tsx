import type { ImpactExploratory } from "../../api/types";
import styles from "./ExploratoryBundle.module.css";

export type PanelId = ImpactExploratory["panels"][number]["id"];
type Item = ImpactExploratory["items"][number];

const signed = (value: number) => `${value >= 0 ? "+" : "−"}${Math.abs(Math.round(value))}%`;

const DIRECTION: Record<Item["direction"], { text: string; className: string }> = {
  up: { text: "↑ both panels", className: styles.up! },
  down: { text: "↓ both panels", className: styles.down! },
  mixed: { text: "panels disagree", className: styles.mixed! },
  single_panel: { text: "broad panel only", className: styles.mixed! },
};

const ROW_CLASS: Record<Item["level"], string> = {
  category: styles.categoryRow!,
  subcategory: styles.subRow!,
  feature: styles.featureRow!,
};

function YearCell({ item, panel, year }: { item: Item; panel: PanelId; year: number }) {
  const point = item.panels[panel]?.by_year.find((p) => p.year === year);
  if (!point) return <td className={styles.none}>—</td>;
  const tone = point.excludes_zero ? (point.impact_pct > 0 ? styles.up : styles.down) : "";
  return (
    <td className={`${styles.value} ${tone}`}>
      <b>{signed(point.impact_pct)}</b>
      <span>
        {signed(point.lower_pct)} to {signed(point.upper_pct)}
      </span>
    </td>
  );
}

export function PanelToggle({
  data,
  panelId,
  onChange,
}: {
  data: ImpactExploratory;
  panelId: PanelId;
  onChange: (id: PanelId) => void;
}) {
  return (
    <div className={styles.toggle} role="group" aria-label="Exploratory sample">
      {data.panels.map((p) => (
        <button key={p.id} type="button" aria-pressed={p.id === panelId} onClick={() => onChange(p.id)}>
          {p.label} · {p.nameplates} nameplates
        </button>
      ))}
    </div>
  );
}

/** Bundle-level associations, kept visually and semantically apart from the gated estimates. */
export function ExploratoryBundle({
  data,
  selectedCategory,
  panelId,
  onPanelChange,
}: {
  data: ImpactExploratory;
  selectedCategory?: string;
  panelId: PanelId;
  onPanelChange: (id: PanelId) => void;
}) {
  const panel = data.panels.find((p) => p.id === panelId)!;
  const expectedByChance = Math.round(data.estimate_count * 0.05);

  return (
    <section className={styles.section} aria-labelledby="exploratory-title">
      <div className={styles.heading}>
        <span className={styles.badge}>Exploratory</span>
        <div>
          <h2 id="exploratory-title">Launch-bundle associations</h2>
          <p>
            Not publication-grade · launches that included the item vs launches that did not · market-adjusted sales
            change with clustered 95% interval
          </p>
        </div>
      </div>

      <p className={styles.caveat}>{data.caveat}</p>

      <div className={styles.controls}>
        <PanelToggle data={data} panelId={panelId} onChange={onPanelChange} />
        <span>{panel.description}.</span>
      </div>

      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th scope="col">Item</th>
              <th scope="col">Nameplates with / without</th>
              {[1, 2, 3, 4].map((year) => (
                <th key={year} scope="col">
                  Year {year}
                </th>
              ))}
              <th scope="col">Direction</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((item) => {
              const estimate = item.panels[panelId];
              const direction = DIRECTION[item.direction];
              return (
                <tr
                  key={`${item.level}-${item.id}`}
                  className={`${ROW_CLASS[item.level]} ${item.category === selectedCategory ? styles.selected : ""}`}
                >
                  <th scope="row">{item.label}</th>
                  <td className={styles.count}>
                    {estimate ? `${estimate.nameplates_with} / ${estimate.nameplates_without}` : "too few"}
                  </td>
                  {[1, 2, 3, 4].map((year) => (
                    <YearCell key={year} item={item} panel={panelId} year={year} />
                  ))}
                  <td className={`${styles.direction} ${direction.className}`}>{direction.text}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p className={styles.footnote}>
        Coloured values have an interval that excludes zero: {data.excludes_zero_count} of {data.estimate_count}{" "}
        estimates across both panels, where about {expectedByChance} would by chance alone. {data.method}.
      </p>
    </section>
  );
}
