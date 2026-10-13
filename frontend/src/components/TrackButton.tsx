import { toggleTrackedFeature, useTrackedFeatures } from "../state/trackedFeatures";
import styles from "./TrackButton.module.css";

let clearFeedback: (() => void) | undefined;

function animateToMyFeatures(source: HTMLElement) {
  clearFeedback?.();

  const visible = (element: Element) => {
    const rect = element.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0 && getComputedStyle(element).visibility !== "hidden";
  };
  const destination =
    [...document.querySelectorAll<HTMLElement>("[data-track-destination]")].find(visible) ??
    [...document.querySelectorAll<HTMLElement>("[data-track-menu]")].find(visible);
  const destinationRect = destination?.getBoundingClientRect();
  const sourceRect = source.getBoundingClientRect();
  const reducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;
  const hint = document.createElement("div");
  hint.className = styles.arrival ?? "";
  hint.setAttribute("role", "status");
  hint.textContent = destination?.hasAttribute("data-track-menu")
    ? "Added · Open menu → My Features"
    : "Added · Find it in My Features";
  const targetX = destinationRect ? destinationRect.left + destinationRect.width / 2 : window.innerWidth - 135;
  const targetY = destinationRect ? destinationRect.bottom + 16 : 70;
  hint.style.left = `${Math.max(110, Math.min(window.innerWidth - 110, targetX))}px`;
  hint.style.top = `${targetY}px`;

  let flight: HTMLDivElement | undefined;
  const timers: { flight?: ReturnType<typeof setTimeout>; hint?: ReturnType<typeof setTimeout>; frame?: number } = {};
  const showHint = () => {
    flight?.remove();
    flight = undefined;
    document.body.append(hint);
    timers.hint = setTimeout(() => {
      hint.remove();
      clearFeedback = undefined;
    }, 2500);
  };
  clearFeedback = () => {
    if (timers.frame !== undefined) cancelAnimationFrame(timers.frame);
    if (timers.flight !== undefined) clearTimeout(timers.flight);
    if (timers.hint !== undefined) clearTimeout(timers.hint);
    flight?.remove();
    hint.remove();
  };

  if (reducedMotion || !destinationRect || sourceRect.width === 0) {
    showHint();
    return;
  }

  flight = document.createElement("div");
  flight.className = styles.flight ?? "";
  flight.setAttribute("aria-hidden", "true");
  flight.textContent = "✓ Tracked";
  flight.style.left = `${sourceRect.left + sourceRect.width / 2}px`;
  flight.style.top = `${sourceRect.top + sourceRect.height / 2}px`;
  document.body.append(flight);
  timers.frame = requestAnimationFrame(() => {
    if (!flight) return;
    flight.style.left = `${targetX}px`;
    flight.style.top = `${destinationRect.top + destinationRect.height / 2}px`;
    flight.style.opacity = "0.35";
    flight.style.transform = "translate(-50%, -50%) scale(0.7)";
  });
  timers.flight = setTimeout(showHint, 640);
}

export function TrackButton({ id, label, compact = false }: { id: string; label: string; compact?: boolean }) {
  const active = useTrackedFeatures().includes(id);
  return (
    <button
      type="button"
      className={`${styles.button} ${active ? styles.active : ""} ${compact ? styles.compact : ""}`}
      aria-pressed={active}
      aria-label={`${active ? "Stop tracking" : "Track"} ${label}`}
      onKeyDown={(event) => event.stopPropagation()}
      onClick={(event) => {
        event.preventDefault();
        event.stopPropagation();
        toggleTrackedFeature(id);
        if (!active) animateToMyFeatures(event.currentTarget);
      }}
    >
      <span aria-hidden="true">{active ? "✓" : "+"}</span> {active ? "Tracking" : "Track"}
    </button>
  );
}
