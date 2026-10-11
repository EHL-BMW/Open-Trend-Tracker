import {
  createContext,
  useContext,
  useEffect,
  useReducer,
  useRef,
  useState,
  type Dispatch,
  type ReactNode,
} from "react";
import type { AnalysisRun, Catalog } from "../api/types";
import { settingsReducer, type Settings, type SettingsAction } from "../domain/settings";

interface PlannerState {
  catalog: Catalog;
  settings: Settings;
  dispatch: Dispatch<SettingsAction>;
  /** The run whose results are shown; kept here so it survives switching pages. */
  run: AnalysisRun | null;
  setRun: (run: AnalysisRun | null) => void;
}

const PlannerContext = createContext<PlannerState | null>(null);

/**
 * Holds the PM's settings once the catalog has arrived. Children only render with a catalog and
 * initialised settings, so components below never deal with "not loaded yet".
 * It sits above the routes, so settings and the current run persist across pages.
 */
export function PlannerProvider({ catalog, children }: { catalog: Catalog; children: ReactNode }) {
  const [settings, dispatch] = useReducer(settingsReducer, catalog, (c) =>
    settingsReducer(null, { type: "init", catalog: c }),
  );
  const [run, setRun] = useState<AnalysisRun | null>(null);

  // A refreshed catalog with a new data version invalidates selections; start from its defaults.
  const version = useRef(catalog.dataVersion);
  useEffect(() => {
    if (version.current === catalog.dataVersion) return;
    version.current = catalog.dataVersion;
    dispatch({ type: "reset", catalog });
  }, [catalog]);

  if (!settings) return null;
  return (
    <PlannerContext.Provider value={{ catalog, settings, dispatch, run, setRun }}>{children}</PlannerContext.Provider>
  );
}

// The hooks belong next to their provider; fast refresh falls back to a full reload for this file.
// eslint-disable-next-line react-refresh/only-export-components
export function usePlanner(): PlannerState {
  const ctx = useContext(PlannerContext);
  if (!ctx) throw new Error("usePlanner must be used inside <PlannerProvider>");
  return ctx;
}

/** Null while the catalog hasn't loaded (the provider isn't mounted yet). */
// eslint-disable-next-line react-refresh/only-export-components
export function usePlannerOptional(): PlannerState | null {
  return useContext(PlannerContext);
}
