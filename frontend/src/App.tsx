import { useCallback, useEffect, useMemo, useState } from "react";
import { errorMessage } from "./api/client";
import { useCatalog, useOpenRun, useRunAnalysis } from "./api/queries";
import type { AnalysisRun } from "./api/types";
import { StateMessage } from "./components/common/StateMessage";
import { TrendForecast } from "./components/forecast/TrendForecast";
import { Inspector, InspectorPlaceholder } from "./components/inspector/Inspector";
import { HeroVideo, PLANNER_ID } from "./components/hero/HeroVideo";
import { NavBar } from "./components/layout/NavBar";
import { Orbit, OrbitPlaceholder } from "./components/orbit/Orbit";
import { ReasoningSheet } from "./components/reasoning/ReasoningSheet";
import { Recommendations } from "./components/recommendations/Recommendations";
import { RunHistory } from "./components/runs/RunHistory";
import { config } from "./config";
import type { CategoryKey } from "./domain/categories";
import { requestKey, toRequest } from "./domain/settings";
import { activeCount } from "./domain/weights";
import { PlannerProvider, usePlanner } from "./state/PlannerContext";
import styles from "./App.module.css";

export function App() {
  const catalog = useCatalog();

  if (catalog.data) {
    return (
      <PlannerProvider catalog={catalog.data}>
        <Planner />
      </PlannerProvider>
    );
  }

  // Nothing is known before the catalog arrives: show the empty frame, never made-up values.
  return (
    <>
      <NavBar mockMode={config.useMocks} canReset={false} canRun={false} running={false} runHint="Waiting for data" />
      <HeroVideo />
      <main id={PLANNER_ID} className={styles.page}>
        <Hero />
        {catalog.isError ? (
          <div className="card">
            <StateMessage
              tone="error"
              title="Couldn't load the data"
              action={
                <button type="button" className="btn-primary" onClick={() => void catalog.refetch()}>
                  Try again
                </button>
              }
            >
              {errorMessage(catalog.error)}
            </StateMessage>
          </div>
        ) : (
          <div className={styles.grid}>
            <OrbitPlaceholder message="Loading sources…" />
            <InspectorPlaceholder />
          </div>
        )}
      </main>
    </>
  );
}

function Planner() {
  const { catalog, settings, dispatch } = usePlanner();
  const [selected, setSelected] = useState<CategoryKey | null>(null);
  const [run, setRun] = useState<AnalysisRun | null>(null);
  const [reasoningId, setReasoningId] = useState<string | null>(null);
  const runAnalysis = useRunAnalysis();
  const openRun = useOpenRun();

  const request = useMemo(() => toRequest(settings, catalog, config.topN), [settings, catalog]);
  const stale = run !== null && requestKey(request) !== requestKey(run.request);
  const hasActiveSource = activeCount(settings.enabled) > 0;
  const canRun = hasActiveSource && !runAnalysis.isPending;

  const handleRun = useCallback(() => {
    if (!canRun) return;
    runAnalysis.mutate(request, {
      onSuccess: (result) => {
        setReasoningId(null);
        setRun(result);
      },
    });
  }, [canRun, request, runAnalysis]);

  const handleOpenRun = (id: string) => {
    openRun.mutate(id, {
      onSuccess: (stored) => {
        dispatch({ type: "load", catalog, request: stored.request });
        setReasoningId(null);
        setRun(stored);
        runAnalysis.reset();
      },
    });
  };

  // ⌘/Ctrl + Enter runs the analysis; Esc closes the source editor.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        handleRun();
      } else if (e.key === "Escape" && !document.querySelector("dialog[open]")) {
        setSelected(null);
      }
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [handleRun]);

  const reasoningRec = run?.recommendations.find((r) => r.id === reasoningId) ?? null;
  const runError = runAnalysis.isError
    ? `The analysis failed: ${errorMessage(runAnalysis.error)}`
    : openRun.isError
      ? `Couldn't open that run: ${errorMessage(openRun.error)}`
      : null;

  return (
    <>
      <NavBar
        mockMode={config.useMocks}
        canReset
        onReset={() => dispatch({ type: "reset", catalog })}
        canRun={canRun}
        running={runAnalysis.isPending}
        runHint={hasActiveSource ? "Run analysis (Ctrl/⌘ + Enter)" : "Switch on at least one weighted source"}
        onRun={handleRun}
      />
      <HeroVideo />
      <main id={PLANNER_ID} className={styles.page}>
        <Hero />
        <div className={styles.grid}>
          <div className={styles.leftCol}>
            <Orbit selected={selected} onSelect={(key) => setSelected((cur) => (cur === key ? null : key))} />
            {selected === "trends" && <TrendForecast />}
          </div>
          <Inspector selected={selected} onSelect={setSelected} />
        </div>

        <Recommendations
          run={run}
          stale={stale}
          running={runAnalysis.isPending}
          error={runError}
          canRun={canRun}
          onRun={handleRun}
          onExplain={setReasoningId}
        />

        <RunHistory
          currentRunId={run?.id ?? null}
          openingId={openRun.isPending ? (openRun.variables ?? null) : null}
          onOpen={handleOpenRun}
        />
      </main>
      {run && <ReasoningSheet run={run} recommendation={reasoningRec} onClose={() => setReasoningId(null)} />}
    </>
  );
}

function Hero() {
  return (
    <header className={styles.hero}>
      <h2>The product management universe.</h2>
      <p>
        Choose what informs the decision. Tap a source to switch it on or off, tune its weight, or refine its filters.
      </p>
    </header>
  );
}
