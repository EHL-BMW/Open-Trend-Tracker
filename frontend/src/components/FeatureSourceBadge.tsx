import styles from "./FeatureSourceBadge.module.css";

/** Labels the evidence source, not the age or maturity of the technology. */
export function FeatureSourceBadge({ source }: { source: "legacy" | "news" }) {
  return (
    <span
      className={`${styles.badge} ${styles[source]}`}
      title={
        source === "legacy"
          ? "Identified in historical Chinese vehicle version pairs"
          : "Tracked through related Chinese news coverage"
      }
    >
      {source === "legacy" ? "Legacy feature" : "News feature"}
    </span>
  );
}
