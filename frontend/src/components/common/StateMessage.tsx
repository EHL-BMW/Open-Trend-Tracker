import type { ReactNode } from "react";
import styles from "./StateMessage.module.css";

interface Props {
  title: string;
  children?: ReactNode;
  tone?: "neutral" | "error";
  action?: ReactNode;
  compact?: boolean;
}

/** Empty, error and "nothing yet" states share one calm layout. */
export function StateMessage({ title, children, tone = "neutral", action, compact }: Props) {
  return (
    <div
      className={`${styles.root} ${compact ? styles.compact : ""} ${tone === "error" ? styles.error : ""}`}
      role={tone === "error" ? "alert" : undefined}
    >
      <p className={styles.title}>{title}</p>
      {children && <p className={styles.body}>{children}</p>}
      {action && <div className={styles.action}>{action}</div>}
    </div>
  );
}
