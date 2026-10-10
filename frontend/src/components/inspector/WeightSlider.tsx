import type { CSSProperties } from "react";
import type { WeightedKey } from "../../domain/categories";
import { usePlanner } from "../../state/PlannerContext";
import { RollingNumber } from "../common/RollingNumber";
import styles from "./Inspector.module.css";

interface Props {
  categoryKey: WeightedKey;
  label: string;
  effective: number;
  disabled: boolean;
}

export function WeightSlider({ categoryKey, label, effective, disabled }: Props) {
  const { settings, dispatch } = usePlanner();
  const value = settings.weights[categoryKey];
  const on = settings.enabled[categoryKey];
  const begin = () => dispatch({ type: "beginWeightDrag" });
  const end = () => dispatch({ type: "endWeightDrag" });

  return (
    <div className={styles.sliderWrap}>
      <div className={styles.sliderTop}>
        <b className="num">
          <RollingNumber value={value} suffix="%" />
        </b>
        <small>{on ? `${(effective * 100).toFixed(1)}% effective` : "Frozen"}</small>
      </div>
      <input
        type="range"
        min={0}
        max={100}
        step={1}
        value={value}
        disabled={disabled}
        aria-label={`${label} weight`}
        aria-valuetext={`${value}%`}
        style={{ "--p": `${value}%` } as CSSProperties}
        onPointerDown={begin}
        onKeyDown={begin}
        onPointerUp={end}
        onKeyUp={end}
        onBlur={end}
        onChange={(e) => dispatch({ type: "setWeight", key: categoryKey, value: Number(e.target.value) })}
      />
    </div>
  );
}
