import { WEIGHTED_KEYS, type WeightedKey } from "./categories";

export type Weights = Record<WeightedKey, number>;
export type Enabled = Record<WeightedKey, boolean>;

const clamp = (v: number, min: number, max: number) => Math.min(max, Math.max(min, v));

/**
 * Splits `total` across `parts` proportionally into integers that add up to exactly `total`
 * (largest remainder method; ties go to the earlier part so the result is deterministic).
 */
export function apportion(parts: number[], total: number): number[] {
  if (parts.length === 0) return [];
  const sum = parts.reduce((s, p) => s + p, 0);
  const raw = parts.map((p) => (sum > 0 ? (total * p) / sum : total / parts.length));
  const result = raw.map(Math.floor);
  let left = total - result.reduce((s, v) => s + v, 0);
  raw
    .map((r, i) => ({ frac: r - Math.floor(r), i }))
    .sort((a, b) => b.frac - a.frac || a.i - b.i)
    .forEach(({ i }) => {
      if (left > 0) {
        result[i] = (result[i] ?? 0) + 1;
        left--;
      }
    });
  return result;
}

/** Turns backend default weights into integers that sum to 100. */
export function normalizeWeights(input: Partial<Weights> | undefined): Weights {
  const parts = WEIGHTED_KEYS.map((k) => Math.max(0, Number(input?.[k]) || 0));
  const values = apportion(parts, 100);
  return Object.fromEntries(WEIGHTED_KEYS.map((k, i) => [k, values[i] ?? 0])) as Weights;
}

/**
 * Sets one weight and rebalances the other *active* sources so all weights still sum to 100.
 * Switched-off sources keep their (frozen) weight. `base` is the weight state when the drag
 * started, so repeated slider events do not accumulate rounding drift.
 */
export function rebalance(
  weights: Weights,
  enabled: Enabled,
  key: WeightedKey,
  value: number,
  base: Weights = weights,
): Weights {
  if (!enabled[key]) return weights;
  const frozen = WEIGHTED_KEYS.filter((k) => !enabled[k]).reduce((s, k) => s + weights[k], 0);
  const budget = 100 - frozen;
  const others = WEIGHTED_KEYS.filter((k) => enabled[k] && k !== key);
  const next = { ...weights };

  if (others.length === 0) {
    next[key] = budget;
    return next;
  }

  const v = clamp(Math.round(value), 0, budget);
  const shares = apportion(
    others.map((k) => base[k]),
    budget - v,
  );
  next[key] = v;
  others.forEach((k, i) => (next[k] = shares[i] ?? 0));
  return next;
}

/** Share each source actually gets: active weights re-normalised, switched-off sources 0. */
export function effectiveWeights(weights: Weights, enabled: Enabled): Weights {
  const activeSum = WEIGHTED_KEYS.filter((k) => enabled[k]).reduce((s, k) => s + weights[k], 0);
  return Object.fromEntries(
    WEIGHTED_KEYS.map((k) => [k, enabled[k] && activeSum > 0 ? weights[k] / activeSum : 0]),
  ) as Weights;
}

export const activeCount = (enabled: Enabled) => WEIGHTED_KEYS.filter((k) => enabled[k]).length;
