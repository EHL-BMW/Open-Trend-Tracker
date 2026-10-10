import type { FilterGroup } from "../../api/types";
import type { CategoryKey } from "../../domain/categories";
import { selectedValues } from "../../domain/settings";
import { usePlanner } from "../../state/PlannerContext";
import { CheckIcon } from "../common/Icons";
import styles from "./Inspector.module.css";

interface Props {
  categoryKey: CategoryKey;
  group: FilterGroup;
  disabled: boolean;
}

/** One filter group from the catalog as an iOS-style checklist. */
export function FilterGroupList({ categoryKey, group, disabled }: Props) {
  const { catalog, settings, dispatch } = usePlanner();
  const selected = selectedValues(settings, categoryKey, group.key);
  const title = group.heading ? `${group.heading} · ${group.label}` : group.label;
  const allOn = selected.length === group.options.length;

  return (
    <>
      <div className={styles.groupHead}>
        <span id={`fg-${categoryKey}-${group.key}`}>{title}</span>
        <button
          type="button"
          className="btn-link"
          disabled={disabled || allOn}
          onClick={() => dispatch({ type: "selectAll", category: categoryKey, group: group.key, catalog })}
        >
          Select All
        </button>
      </div>
      {group.options.length === 0 ? (
        <p className={styles.groupFoot}>No values for this filter in the database yet.</p>
      ) : (
        <div className={styles.group} role="group" aria-labelledby={`fg-${categoryKey}-${group.key}`}>
          {group.options.map((option) => {
            const checked = selected.includes(option.value);
            return (
              <button
                key={option.value}
                type="button"
                role="checkbox"
                aria-checked={checked}
                disabled={disabled}
                className={`${styles.row} ${styles.check}`}
                onClick={() =>
                  dispatch({ type: "toggleFilter", category: categoryKey, group: group.key, value: option.value })
                }
              >
                <span className={styles.grow}>{option.label}</span>
                <CheckIcon className={styles.tick} />
              </button>
            );
          })}
        </div>
      )}
    </>
  );
}
