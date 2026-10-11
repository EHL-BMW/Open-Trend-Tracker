import { useCallback, useSyncExternalStore } from "react";

export type ThemePreference = "system" | "light" | "dark";

export const THEME_STORAGE_KEY = "opentt-theme";
const listeners = new Set<() => void>();

function read(): ThemePreference {
  try {
    const v = localStorage.getItem(THEME_STORAGE_KEY);
    return v === "light" || v === "dark" ? v : "system";
  } catch {
    return "system";
  }
}

/** "system" removes the override so the OS setting (prefers-color-scheme) decides. */
function apply(pref: ThemePreference) {
  const root = document.documentElement;
  if (pref === "system") delete root.dataset.theme;
  else root.dataset.theme = pref;
}

function setPreference(pref: ThemePreference) {
  try {
    if (pref === "system") localStorage.removeItem(THEME_STORAGE_KEY);
    else localStorage.setItem(THEME_STORAGE_KEY, pref);
  } catch {
    // Storage may be blocked (private mode, policy); the choice still applies for this visit.
  }
  apply(pref);
  listeners.forEach((l) => l());
}

const subscribe = (listener: () => void) => {
  listeners.add(listener);
  return () => listeners.delete(listener);
};

// Fall back to the attribute so the choice survives even when storage is blocked.
const snapshot = (): ThemePreference => {
  const attr = document.documentElement.dataset.theme;
  return attr === "light" || attr === "dark" ? attr : read();
};

/** Appearance preference shared by every component; index.html applies it before first paint. */
export function useThemePreference() {
  const preference = useSyncExternalStore(subscribe, snapshot, () => "system" as const);
  const set = useCallback((pref: ThemePreference) => setPreference(pref), []);
  return { preference, setPreference: set };
}
