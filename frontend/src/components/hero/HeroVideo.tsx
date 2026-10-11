import { useEffect, useRef, useState } from "react";
import { config } from "../../config";
import TextAnimation from "../ui/stagger-text";
import styles from "./HeroVideo.module.css";

export const HERO_ID = "intro";
export const PLANNER_ID = "planner";

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
 * Full-screen intro with a looping background video, like a brand landing page. The planner
 * starts below it. Without a video file (or with reduced motion) the poster / a dark surface shows.
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
        <p className={styles.eyebrow}>Open Trend Tracker · Product Management</p>
        <h1 id="hero-title" className={styles.title} aria-label="OpenTT, Open Trend Tracker">
          <span aria-hidden="true">
            <TextAnimation divideBy="letter">OpenTT</TextAnimation>
          </span>
        </h1>
        <p className={styles.tagline}>
          <TextAnimation delay={0.35}>Series Improvement Planner</TextAnimation>
        </p>
        <p className={styles.lead}>
          Weigh sales, customer voices and market trends, and get the improvements that matter most for the next update
          of an existing series. Every recommendation traced back to its source.
        </p>
        <TrustPoints />
        <div className={styles.actions}>
          <a className={styles.cta} href={`#${PLANNER_ID}`}>
            Open the planner
          </a>
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

      <a className={styles.scrollCue} href={`#${PLANNER_ID}`} aria-label="Scroll to the planner">
        <svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M6 9l6 6 6-6"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </a>
    </section>
  );
}

/** Why PMs can rely on the output: evidence first, traceable, reproducible. */
function TrustPoints() {
  const points = [
    {
      icon: <CheckIcon />,
      title: "Evidence first",
      text: "Built on real sales and customer data. Trend forecasts are always marked as assumptions, never hidden.",
    },
    {
      icon: <SourceIcon />,
      title: "Traceable to the source",
      text: "Every recommendation links back to the exact records behind it.",
    },
    {
      icon: <HashIcon />,
      title: "Reproducible",
      text: "Same inputs, same Top 5. Every run is stored with a Run ID for audit.",
    },
  ];
  return (
    <section className={styles.trust} aria-labelledby="trust-claim">
      <p id="trust-claim" className={styles.claim}>
        Decisions you can defend.
      </p>
      <ul className={styles.points}>
        {points.map((p) => (
          <li key={p.title} className={styles.point}>
            <span className={styles.pointIcon} aria-hidden="true">
              {p.icon}
            </span>
            <span>
              <span className={styles.pointTitle}>{p.title}</span>
              <span className={styles.pointText}>{p.text}</span>
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}

function CheckIcon() {
  return (
    <svg
      width="15"
      height="15"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.6"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M5 12.5l4.5 4.5L19 7.5" />
    </svg>
  );
}

function SourceIcon() {
  return (
    <svg
      width="15"
      height="15"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M6 4v9a4 4 0 0 0 4 4h8" />
      <path d="M14 13l4 4-4 4" />
    </svg>
  );
}

function HashIcon() {
  return (
    <svg
      width="15"
      height="15"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.2"
      strokeLinecap="round"
    >
      <path d="M9 4L7 20M17 4l-2 16M4 9h16M3.5 15h16" />
    </svg>
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
