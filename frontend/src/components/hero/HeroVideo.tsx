import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { config } from "../../config";
import { ROUTES } from "../../routes";
import TextAnimation from "../ui/stagger-text";
import styles from "./HeroVideo.module.css";

export const HERO_ID = "intro";

const prefersReducedMotion = () =>
  typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches === true;

/** play() returns a promise in modern browsers, nothing in some older ones, and may throw. */
const safePlay = (el: HTMLVideoElement): Promise<void> => {
  try {
    return Promise.resolve(el.play());
  } catch (err) {
    return Promise.reject(err);
  }
};

/**
 * Full-screen intro with a looping background video, like a brand landing page: the home page.
 * Without a video file (or with reduced motion) the poster / a dark surface shows.
 */
export function HeroVideo() {
  const video = useRef<HTMLVideoElement>(null);
  const [reduced] = useState(prefersReducedMotion);
  const [playing, setPlaying] = useState(!reduced);
  const [failed, setFailed] = useState(false);

  // Pause when the intro is scrolled out of view; there's no reason to decode video nobody sees.
  useEffect(() => {
    const el = video.current;
    if (!el || failed || typeof IntersectionObserver === "undefined") return;
    const observer = new IntersectionObserver(([entry]) => {
      if (!entry) return;
      if (!entry.isIntersecting) el.pause();
      else if (playing) void safePlay(el).catch(() => setPlaying(false));
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, [playing, failed]);

  const togglePlayback = () => {
    const el = video.current;
    if (!el) return;
    if (playing) {
      el.pause();
      setPlaying(false);
    } else {
      void safePlay(el).then(
        () => setPlaying(true),
        () => setPlaying(false),
      );
    }
  };

  return (
    <section
      id={HERO_ID}
      className={styles.hero}
      aria-labelledby="hero-title"
      style={{ backgroundImage: `url("${config.hero.posterUrl}")` }}
    >
      {!failed && (
        <video
          ref={video}
          className={styles.video}
          src={config.hero.videoUrl}
          poster={config.hero.posterUrl}
          autoPlay={!reduced}
          muted
          loop
          playsInline
          preload="metadata"
          aria-hidden="true"
          tabIndex={-1}
          onError={() => setFailed(true)}
        />
      )}
      <div className={styles.scrim} aria-hidden="true" />

      <div className={styles.content}>
        <p className={styles.eyebrow}>Open Trend Tracker · BMW Product Management</p>
        <h1 id="hero-title" className={styles.title} aria-label="OpenTT, Open Trend Tracker">
          <span aria-hidden="true">
            <TextAnimation divideBy="letter">OpenTT</TextAnimation>
          </span>
        </h1>
        <p className={styles.tagline}>
          <TextAnimation delay={0.35}>From China feature trends to BMW customer value</TextAnimation>
        </p>
        <p className={styles.lead}>
          OpenTT continuously discovers emerging vehicle features in China and connects them to real BMW customer
          problems. It then uses historical vehicle and sales data to estimate which opportunities have the greatest
          potential to improve customer experience and grow revenue.
        </p>
        <TrustPoints />
        <div className={styles.actions}>
          <Link className={styles.cta} to={ROUTES.planner}>
            Open the planner
          </Link>
          <Link className={styles.ctaSecondary} to={ROUTES.featureTrends}>
            Explore Feature Radar
          </Link>
        </div>
      </div>

      {!failed && (
        <button
          type="button"
          className={styles.playback}
          onClick={togglePlayback}
          aria-label={playing ? "Pause background video" : "Play background video"}
        >
          {playing ? <PauseIcon /> : <PlayIcon />}
        </button>
      )}
    </section>
  );
}

/** Short trust claim above the call to action. */
function TrustPoints() {
  return (
    <section className={styles.trust} aria-labelledby="trust-claim">
      <p id="trust-claim" className={styles.claim}>
        Decisions you can defend.
      </p>
    </section>
  );
}

function PauseIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true">
      <rect x="3" y="2" width="3" height="10" rx="1" fill="currentColor" />
      <rect x="8" y="2" width="3" height="10" rx="1" fill="currentColor" />
    </svg>
  );
}

function PlayIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true">
      <path d="M4 2.5v9l7.5-4.5z" fill="currentColor" />
    </svg>
  );
}
