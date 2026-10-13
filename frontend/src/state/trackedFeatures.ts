import { useSyncExternalStore } from "react";

const KEY = "opentt.tracked-features.v1";
let tracked: string[] = read();
const listeners = new Set<() => void>();

function read(): string[] {
  if (typeof localStorage === "undefined") return [];
  try {
    const saved = JSON.parse(localStorage.getItem(KEY) ?? "[]");
    return Array.isArray(saved) ? saved.filter((id): id is string => typeof id === "string") : [];
  } catch {
    return [];
  }
}

function emit() {
  for (const listener of listeners) listener();
}

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

if (typeof window !== "undefined") {
  window.addEventListener("storage", (event) => {
    if (event.key !== KEY) return;
    tracked = read();
    emit();
  });
}

export function useTrackedFeatures() {
  return useSyncExternalStore(
    subscribe,
    () => tracked,
    () => [],
  );
}

export function toggleTrackedFeature(id: string) {
  tracked = tracked.includes(id) ? tracked.filter((item) => item !== id) : [...tracked, id];
  try {
    localStorage.setItem(KEY, JSON.stringify(tracked));
  } catch {
    /* Tracking still works for this session. */
  }
  emit();
}

export function legacyFeatureId(categoryId: string, name: string) {
  return `legacy:${categoryId}:${name}`;
}
