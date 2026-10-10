import { CATEGORIES, CATEGORY_KEYS, WEIGHTED_KEYS, isWeightedKey, type CategoryKey } from "../../domain/categories";
import { filterSummary } from "../../domain/settings";
import { activeCount, effectiveWeights } from "../../domain/weights";
import { usePlanner } from "../../state/PlannerContext";
import { OrbitView, type OrbitNodeModel } from "./OrbitView";

const pct = (x: number) => `${Math.round(x * 100)}%`;

export function Orbit({ selected, onSelect }: { selected: CategoryKey | null; onSelect: (key: CategoryKey) => void }) {
  const { catalog, settings } = usePlanner();
  const eff = effectiveWeights(settings.weights, settings.enabled);

  const nodes: OrbitNodeModel[] = CATEGORY_KEYS.map((key) => {
    const name = CATEGORIES[key].name;
    const summary = filterSummary(catalog.categories[key].filters, settings.filters[key]);
    if (!isWeightedKey(key)) {
      return {
        key,
        value: "Filter",
        progress: 0,
        sub: summary,
        off: false,
        ariaLabel: `${name}: filters only, not weighted. Edit filters.`,
      };
    }
    const on = settings.enabled[key];
    return {
      key,
      value: on ? pct(eff[key]) : "Off",
      progress: on ? eff[key] : 0,
      sub: on ? summary : `Frozen at ${settings.weights[key]}%`,
      off: !on,
      ariaLabel: `${name}: ${on ? `${pct(eff[key])} effective weight` : "switched off"}. Edit.`,
    };
  });

  const records = CATEGORY_KEYS.reduce((s, k) => s + catalog.categories[k].recordCount, 0);

  return (
    <OrbitView
      nodes={nodes}
      selected={selected}
      onSelect={onSelect}
      centerSub={`${activeCount(settings.enabled)} of ${WEIGHTED_KEYS.length} weighted sources on`}
      headerRight={`${records.toLocaleString()} records available`}
    />
  );
}

/** Same layout while the catalog is loading, with nothing filled in. */
export function OrbitPlaceholder({ message }: { message: string }) {
  const nodes: OrbitNodeModel[] = CATEGORY_KEYS.map((key) => ({
    key,
    value: "–",
    progress: 0,
    sub: "",
    off: true,
    ariaLabel: `${CATEGORIES[key].name}: not loaded`,
  }));
  return <OrbitView nodes={nodes} selected={null} centerSub={message} headerRight="" disabled />;
}
