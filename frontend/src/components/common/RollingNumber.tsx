import { AnimatedNumber } from "../ui/animated-number";
import styles from "./RollingNumber.module.css";

interface Props {
  value: number;
  /** Digits after the decimal point (Vengeance's AnimatedNumber only rolls whole numbers). */
  decimals?: 0 | 1;
  suffix?: string;
  className?: string;
}

/**
 * Rolling digits (Vengeance UI AnimatedNumber). The digit strips contain every digit 0–9, so they are
 * hidden from assistive tech and the real value is provided as text instead.
 */
export function RollingNumber({ value, decimals = 0, suffix = "", className }: Props) {
  const rounded = Number(value.toFixed(decimals));
  const whole = Math.trunc(rounded);
  const tenths = Math.round(Math.abs(rounded - whole) * 10);
  const text = `${rounded.toFixed(decimals)}${suffix}`;

  return (
    <span className={`${styles.root} ${className ?? ""}`}>
      <span className="visually-hidden">{text}</span>
      <span className={styles.digits} aria-hidden="true">
        <AnimatedNumber value={whole} />
        {decimals === 1 && (
          <>
            .<AnimatedNumber value={tenths} />
          </>
        )}
        {suffix}
      </span>
    </span>
  );
}
