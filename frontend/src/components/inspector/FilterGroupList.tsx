import { useState } from "react";
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

/** One filter group from the catalog as an iOS-style checklist; collapsible when the backend marks it so. */
export function FilterGroupList({ categoryKey, group, disabled }: Props) {
  const { catalog, settings, dispatch } = usePlanner();
  const [open, setOpen] = useState(!group.collapsible);
  const selected = selectedValues(settings, categoryKey, group.key);
  const title = group.heading ? `${group.heading} · ${group.label}` : group.label;
  const allOn = selected.length === group.options.length;
  const labelId = `fg-${categoryKey}-${group.key}`;
  const listId = `${labelId}-list`;

  return (
    <>
      <div className={styles.groupHead}>
        {group.collapsible ? (
          <button
            type="button"
            className={styles.collapse}
            aria-expanded={open}
            aria-controls={listId}
            onClick={() => setOpen((o) => !o)}
          >
            <svg className={styles.chevron} width="12" height="12" viewBox="0 0 12 12" aria-hidden="true">
              <path
                d="M4 2.5l3.5 3.5L4 9.5"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
              />
            </svg>
            <span id={labelId}>{title}</span>
            <span className={styles.count}>
              {selected.length}/{group.options.length}
            </span>
          </button>
        ) : (
          <span id={labelId}>{title}</span>
        )}
        <button
          type="button"
          className="btn-link"
          disabled={disabled || allOn}
          onClick={() => dispatch({ type: "selectAll", category: categoryKey, group: group.key, catalog })}
        >
          Select all
        </button>
      </div>
      {!open ? null : group.options.length === 0 ? (
        <p className={styles.groupFoot}>No values for this filter in the database yet.</p>
      ) : (
        <div id={listId} className={styles.group} role="group" aria-labelledby={labelId}>
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
