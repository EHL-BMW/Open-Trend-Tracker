import styles from "./Inspector.module.css";

interface Props {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
}

/** iOS-style switch on a native checkbox, so keyboard and screen readers work unchanged. */
export function Switch({ checked, onChange, label }: Props) {
  return (
    <label className={styles.switch}>
      <input
        type="checkbox"
        role="switch"
        checked={checked}
        aria-label={label}
        onChange={(e) => onChange(e.target.checked)}
      />
      <span aria-hidden="true" />
    </label>
  );
}
