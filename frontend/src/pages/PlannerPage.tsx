import { useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { ApiError, errorMessage } from "../api/client";
import { queryKeys, useCatalog, useOpenRun, useRunAnalysis } from "../api/queries";
import { StateMessage } from "../components/common/StateMessage";
import { TrendForecast } from "../components/forecast/TrendForecast";
import { HeroVideo, PLANNER_ID } from "../components/hero/HeroVideo";
import { Inspector, InspectorPlaceholder } from "../components/inspector/Inspector";
import { Footer } from "../components/layout/Footer";
import { NavBar } from "../components/layout/NavBar";
import { PlannerActions } from "../components/layout/PlannerActions";
import { Orbit, OrbitPlaceholder } from "../components/orbit/Orbit";
import { ReasoningSheet } from "../components/reasoning/ReasoningSheet";
import { Recommendations } from "../components/recommendations/Recommendations";
import { StickyResultsBar } from "../components/recommendations/StickyResultsBar";
import { RunHistory } from "../components/runs/RunHistory";
import { PlannerSteps, STEP_IDS } from "../components/steps/PlannerSteps";
import { config } from "../config";
import type { CategoryKey } from "../domain/categories";
import { requestKey, toRequest } from "../domain/settings";
import { activeCount } from "../domain/weights";
import { usePlannerOptional } from "../state/PlannerContext";
import { Link } from "react-router-dom";
import { ROUTES } from "../routes";
import { usePageTitle } from "./usePageTitle";
import styles from "./PlannerPage.module.css";

/** Start page: video intro, then the planner. Shows an empty frame until the catalog has loaded. */
export function PlannerPage() {
  usePageTitle("Planner");
  return usePlannerOptional() ? <Planner /> : <PlannerLoading />;
}

function PlannerLoading() {
  const catalog = useCatalog();
  return (
    <>
      <NavBar
        mockMode={config.useMocks}
        actions={<PlannerActions canReset={false} canRun={false} running={false} runHint="Waiting for data" />}
      />
      <HeroVideo />
      <main id={PLANNER_ID} className={styles.page}>
        <Intro>
          <PlannerSteps hasFreshResults={false} running={false} canRun={false} onRun={() => {}} />
        </Intro>
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
      <Footer />
    </>
  );
}

function Planner() {
  const planner = usePlannerOptional()!;
  const { catalog, settings, dispatch, run, setRun } = planner;
  const [selected, setSelected] = useState<CategoryKey | null>(null);
  const [reasoningId, setReasoningId] = useState<string | null>(null);
  const runAnalysis = useRunAnalysis();
  const openRun = useOpenRun();
  const queryClient = useQueryClient();
  /** Data version a run was rejected for as outdated; set while the new catalog loads, then the run retries once. */
  const retryAfterVersion = useRef<string | null>(null);

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
        // Bring the new Top 5 into view (they are below the fold); wait for them to render first.
        requestAnimationFrame(() => {
          const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
          document
            .getElementById(STEP_IDS.results)
            ?.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
        });
      },
      onError: (err) => {
        // The backend data changed while the page was open: load the new filters, then run again once.
        if (err instanceof ApiError && err.code === "stale_data_version" && retryAfterVersion.current === null) {
          retryAfterVersion.current = request.dataVersion;
          void queryClient.invalidateQueries({ queryKey: queryKeys.catalog });
        }
      },
    });
  }, [canRun, request, runAnalysis, setRun, queryClient]);

  // Once the refreshed catalog (new data version) has reset the settings, retry the rejected run.
  useEffect(() => {
    const rejected = retryAfterVersion.current;
    if (rejected === null || catalog.dataVersion === rejected || runAnalysis.isPending) return;
    retryAfterVersion.current = null;
    setRun(null);
    runAnalysis.reset();
    handleRun();
  }, [catalog.dataVersion, handleRun, runAnalysis, setRun]);

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
        actions={
          <PlannerActions
            canReset
            onReset={() => dispatch({ type: "reset", catalog })}
            canRun={canRun}
            running={runAnalysis.isPending}
            runHint={hasActiveSource ? "Run analysis (Ctrl/⌘ + Enter)" : "Switch on at least one weighted source"}
            onRun={handleRun}
          />
        }
      />
      <HeroVideo />
      <main id={PLANNER_ID} className={styles.page}>
        <Intro>
          <PlannerSteps
            hasFreshResults={run !== null && !stale}
            running={runAnalysis.isPending}
            canRun={canRun}
            onRun={handleRun}
          />
        </Intro>
        <div className={styles.grid}>
          <div className={styles.leftCol}>
            <Orbit selected={selected} onSelect={(key) => setSelected((cur) => (cur === key ? null : key))} />
            <TrendForecast />
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
      <Footer />
      {run && (
        <StickyResultsBar run={run} stale={stale} running={runAnalysis.isPending} canRun={canRun} onRun={handleRun} />
      )}
      {run && <ReasoningSheet run={run} recommendation={reasoningRec} onClose={() => setReasoningId(null)} />}
    </>
  );
}

function Intro({ children }: { children: ReactNode }) {
  return (
    <header className={styles.hero}>
      <h2>Plan your next series update.</h2>
      <p>Four steps from data to a traceable Top 5.</p>
      <div
        style={{
          marginTop: "12px",
          marginBottom: "16px",
          display: "inline-flex",
          alignItems: "center",
          gap: "10px",
          background: "color-mix(in srgb, var(--card) 90%, transparent)",
          border: "1px solid color-mix(in srgb, var(--blue) 35%, var(--sep))",
          padding: "8px 18px",
          borderRadius: "999px",
          fontSize: "13px",
          flexWrap: "wrap",
        }}
      >
        <span style={{ color: "var(--blue)", fontWeight: 600 }}>🤖 Live KI-Agent:</span>
        <span style={{ color: "var(--label-2)" }}>Deep-dive into Xiaomi, XPeng & Zeekr gaps with our</span>
        <Link to={ROUTES.agent} style={{ color: "var(--blue)", fontWeight: 600, textDecoration: "underline" }}>
          AI Gap Agent Cockpit →
        </Link>
      </div>
      {children}
    </header>
  );
}
