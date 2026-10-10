import { useEffect, useState } from "react";
import { HERO_ID } from "../hero/HeroVideo";
import AnimatedButton from "../ui/animated-button";
import styles from "./NavBar.module.css";

interface Props {
  mockMode: boolean;
  canReset: boolean;
  onReset?: () => void;
  canRun: boolean;
  running: boolean;
  runHint?: string;
  onRun?: () => void;
}

/** True while the intro video is still visible under the 52px nav bar. */
function useOverHero() {
  const [over, setOver] = useState(false);
  useEffect(() => {
    const hero = document.getElementById(HERO_ID);
    if (!hero || typeof IntersectionObserver === "undefined") return;
    // Edge-adjacent counts as "intersecting" with a zero-height overlap; require visible pixels.
    const observer = new IntersectionObserver(
      ([entry]) => setOver(Boolean(entry?.isIntersecting && entry.intersectionRect.height > 0)),
      { rootMargin: "-52px 0px 0px 0px", threshold: [0, 0.01] },
    );
    observer.observe(hero);
    return () => observer.disconnect();
  }, []);
  return over;
}

export function NavBar({ mockMode, canReset, onReset, canRun, running, runHint, onRun }: Props) {
  const overHero = useOverHero();

  return (
    <nav className={`${styles.nav} ${overHero ? styles.overHero : ""}`} aria-label="Main">
      <div className={styles.inner}>
        <div className={styles.title}>
          OpenTT
          <span className={styles.subtitle}>Series Improvement Planner</span>
          {mockMode && (
            <span className={styles.badge} title="Running against the built-in mock backend">
              Mock backend
            </span>
          )}
        </div>
        <button type="button" className={`btn-link ${styles.reset}`} onClick={onReset} disabled={!canReset}>
          Reset
        </button>
        <AnimatedButton
          type="button"
          className={styles.run}
          onClick={onRun}
          disabled={!canRun || running}
          title={runHint}
          aria-keyshortcuts="Control+Enter Meta+Enter"
        >
          {running && <span className="spinner" aria-hidden="true" />}
          {running ? "Running…" : "Run analysis"}
        </AnimatedButton>
      </div>
    </nav>
  );
}
