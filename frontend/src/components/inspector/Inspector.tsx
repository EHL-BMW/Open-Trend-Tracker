import type { CSSProperties } from "react";
import { CATEGORIES, CATEGORY_ORDER, categoryColor, isWeightedKey, type CategoryKey } from "../../domain/categories";
import { emptyGroups } from "../../domain/settings";
import { activeCount, effectiveWeights } from "../../domain/weights";
import { usePlanner } from "../../state/PlannerContext";
import { CloseIcon } from "../common/Icons";
import { StateMessage } from "../common/StateMessage";
import { FilterGroupList } from "./FilterGroupList";
import { Switch } from "./Switch";
import { WeightSlider } from "./WeightSlider";
import styles from "./Inspector.module.css";

interface Props {
  selected: CategoryKey | null;
  onSelect: (key: CategoryKey | null) => void;
}

export function Inspector({ selected, onSelect }: Props) {
  return (
    <aside className={`card ${styles.inspector}`} aria-live="polite" aria-label="Source settings">
      {selected ? (
        <CategoryEditor categoryKey={selected} onClose={() => onSelect(null)} />
      ) : (
        <WeightOverview onSelect={onSelect} />
      )}
    </aside>
  );
}

function WeightOverview({ onSelect }: { onSelect: (key: CategoryKey) => void }) {
  const { catalog, settings } = usePlanner();
  const eff = effectiveWeights(settings.weights, settings.enabled);
  const d = catalog.defaultWeights;

  return (
    <>
      <div className={styles.head}>
        <h2>Weights</h2>
      </div>
      <p className={styles.sub}>
        Always 100% in total. Moving one source rebalances the others. A source switched off keeps its weight frozen and
        leaves the analysis.
      </p>
      <div className={styles.groupHead}>
        <span>Effective share</span>
      </div>
      <div className={styles.group}>
        {CATEGORY_ORDER.map((key) => {
          const weighted = isWeightedKey(key);
          const share = weighted ? eff[key] : 0;
          const value = !weighted ? "Filter" : settings.enabled[key] ? `${(share * 100).toFixed(1)}%` : "Off";
          return (
            <button
              key={key}
              type="button"
              className={styles.ovRow}
              style={{ "--c": categoryColor(key) } as CSSProperties}
              onClick={() => onSelect(key)}
            >
              <span className={styles.dot} />
              <span>
                <span>{CATEGORIES[key].name}</span>
                <span className={styles.barMini}>
                  <span style={{ width: `${share * 100}%` }} />
                </span>
              </span>
              <span className={`${styles.ovValue} num`}>
                {value} <span className={styles.chev}>›</span>
              </span>
            </button>
          );
        })}
      </div>
      <p className={styles.groupFoot}>
        Defaults from the backend: Sales {d.sales} / Customer {d.customer} / Trends {d.trends}. Features / Engineering
        only filters and is not weighted.
      </p>
    </>
  );
}

function CategoryEditor({ categoryKey, onClose }: { categoryKey: CategoryKey; onClose: () => void }) {
  const { catalog, settings, dispatch } = usePlanner();
  const meta = CATEGORIES[categoryKey];
  const { filters, recordCount } = catalog.categories[categoryKey];
  const weighted = isWeightedKey(categoryKey);
  const on = weighted ? settings.enabled[categoryKey] : true;
  const eff = effectiveWeights(settings.weights, settings.enabled);
  const empty = emptyGroups(filters, settings.filters[categoryKey]);
  const onlyActive = weighted && on && activeCount(settings.enabled) <= 1;

  return (
    <div style={{ "--c": categoryColor(categoryKey) } as CSSProperties} className={styles.editor}>
      <div className={styles.head}>
        <span className={styles.dot} />
        <h2 id="inspector-title">
          {meta.name} {!meta.evidence && <span className="tag-assume">Assumption</span>}
        </h2>
        <button type="button" className="icon-btn" onClick={onClose} aria-label="Back to all weights">
          <CloseIcon />
        </button>
      </div>
      <p className={styles.sub}>{meta.description}</p>

      {weighted ? (
        <>
          <div className={styles.groupHead}>
            <span>Source</span>
          </div>
          <div className={styles.group}>
            <div className={styles.row}>
              <span className={styles.grow}>Include in analysis</span>
              <Switch
                checked={on}
                label={`Include ${meta.name} in analysis`}
                onChange={(enabled) => dispatch({ type: "setEnabled", key: categoryKey, enabled })}
              />
            </div>
          </div>
          <p className={styles.groupFoot}>{recordCount.toLocaleString()} source records available.</p>

          <div className={styles.groupHead}>
            <span>Weight</span>
          </div>
          <div className={styles.group}>
            <WeightSlider
              categoryKey={categoryKey}
              label={meta.name}
              effective={eff[categoryKey]}
              disabled={!on || onlyActive}
            />
          </div>
          <p className={styles.groupFoot}>
            {!on
              ? `Switched off. Weight stays frozen at ${settings.weights[categoryKey]}% and the source leaves the analysis.`
              : onlyActive
                ? "The only source switched on carries the whole analysis."
                : "Other active sources rebalance as you drag."}
          </p>
        </>
      ) : (
        <p className={styles.groupFoot}>
          {recordCount.toLocaleString()} source records, shown as context and not weighted.
        </p>
      )}

      {filters.length === 0 ? (
        <StateMessage compact title="No filters yet">
          The backend didn&apos;t send any filter values for this source.
        </StateMessage>
      ) : (
        filters.map((group) => (
          <FilterGroupList key={group.key} categoryKey={categoryKey} group={group} disabled={!on} />
        ))
      )}

      {on && empty.length > 0 && (
        <div className={styles.warn} role="status">
          Nothing selected in {empty.map((g) => g.label).join(", ")}. This source won&apos;t contribute.
        </div>
      )}
    </div>
  );
}

export function InspectorPlaceholder() {
  return (
    <aside className={`card ${styles.inspector}`} aria-busy="true" aria-label="Source settings">
      <div className={`skeleton ${styles.skTitle}`} />
      <div className={`skeleton ${styles.skLine}`} />
      <div className={`skeleton ${styles.skLine}`} style={{ width: "70%" }} />
      <div className={`skeleton ${styles.skBlock}`} />
    </aside>
  );
}
