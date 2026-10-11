import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { Footer } from "../components/layout/Footer";
import { NavBar } from "../components/layout/NavBar";
import { config } from "../config";
import {
  FEATURE_CATEGORIES,
  featureClusters,
  featureNewsMeta,
  type FeatureCategory,
  type FeatureCluster,
  type FeatureNewsItem,
} from "../content/featureNews";
import { DOMAIN_COLORS, fmtPct } from "../content/trendRadar";
import { usePageTitle } from "./usePageTitle";
import styles from "./FeatureTrendsPage.module.css";

interface SavedProblem {
  id: string;
  name: string;
  category: FeatureCategory;
  problem_statement: string;
  mention_count: number;
  affected_feature_ids: string[];
  possible_feature_ids: string[];
}

interface SavedProblemAnalysis {
  generated_at: string;
  problems: SavedProblem[];
}

function ProblemChart({
  analysis,
  selectedId,
  onSelect,
}: {
  analysis: SavedProblemAnalysis | null;
  selectedId: string | null;
  onSelect: (id: string | null) => void;
}) {
  const problems = analysis?.problems ?? [];
  if (!problems.length) {
    return (
      <section className={styles.problemChartEmpty}>
        <div><p className={styles.kicker}>Customer problems</p><h2>Upload feedback in AI Agent</h2></div>
        <p>The saved problem comparison will appear here and connect each problem to possible features.</p>
      </section>
    );
  }
  const maximum = Math.max(...problems.map((problem) => problem.mention_count), 1);
  const minimum = Math.min(...problems.map((problem) => problem.mention_count), maximum);
  const spread = Math.max(maximum - minimum, 1);
  const selected = problems.find((problem) => problem.id === selectedId) ?? null;
  return (
    <section className={styles.problemChartSection} aria-labelledby="problem-chart-title">
      <div className={styles.problemChartHeading}>
        <div><p className={styles.kicker}>Customer problem comparison</p><h2 id="problem-chart-title">Problem intensity and possible features</h2></div>
        {selected && <button type="button" className={styles.clearButton} onClick={() => onSelect(null)}>Show all features</button>}
      </div>
      <div className={styles.problemChart} role="group" aria-label="Problem mentions; select a bar to show possible features">
        {problems.map((problem) => {
          const ratio = problem.mention_count / maximum;
          const density = (problem.mention_count - minimum) / spread;
          return (
            <button
              type="button"
              key={problem.id}
              className={`${styles.problemColumn} ${selectedId === problem.id ? styles.problemColumnActive : ""}`}
              onClick={() => onSelect(selectedId === problem.id ? null : problem.id)}
              aria-pressed={selectedId === problem.id}
              title={`${problem.name}: ${problem.mention_count} mentions`}
            >
              <b>{problem.mention_count}</b>
              <span
                className={styles.problemBar}
                style={{
                  "--bar-height": `${Math.max(18, ratio * 100)}%`,
                  "--bar-density": `${Math.round(35 + density * 65)}%`,
                } as CSSProperties}
              />
              <span className={styles.problemBarLabel}>{problem.name}</span>
            </button>
          );
        })}
      </div>
      {selected && (
        <div className={styles.problemSelection} aria-live="polite">
          <div><b>{selected.name}</b><span>{selected.category} · {selected.mention_count} mentions</span></div>
          <div className={styles.possibleFeatures}>
            <span>Possible features</span>
            {selected.possible_feature_ids.map((id) => {
              const feature = featureClusters.find((item) => item.id === id);
              return <b key={id}>{feature?.label ?? id}</b>;
            })}
          </div>
        </div>
      )}
    </section>
  );
}

const CATEGORY_COLORS: Record<FeatureCategory, string> = {
  "Energy & Charging": DOMAIN_COLORS["Energy & Charging"] ?? "#38bdf8",
  "Driving Assistance": DOMAIN_COLORS["Driving Assistance"] ?? "#a78bfa",
  "Digital Cockpit & AI": DOMAIN_COLORS["Digital Cockpit & AI"] ?? "#fbbf24",
  "Connected Ecosystem": DOMAIN_COLORS["Connected Ecosystem"] ?? "#f472b6",
  "Smart Cabin": DOMAIN_COLORS["Smart Cabin"] ?? "#fb923c",
  "Vehicle Dynamics & Safety": DOMAIN_COLORS["Vehicle Dynamics & Safety"] ?? "#34d399",
  "Smart Exterior": DOMAIN_COLORS["Smart Exterior"] ?? "#94a3b8",
  "Market & Portfolio": "#ef4444",
};

function Sparkline({ values, color, label }: { values: number[]; color: string; label: string }) {
  if (!values.length) return <div className={styles.noTrend}>New item · no 12-week baseline yet</div>;
  const width = 260;
  const height = 68;
  const max = Math.max(...values, 1);
  const step = width / Math.max(values.length - 1, 1);
  const points = values
    .map((value, index) => `${index * step},${height - 5 - (value / max) * (height - 12)}`)
    .join(" ");
  const area = `0,${height - 4} ${points} ${width},${height - 4}`;
  return (
    <svg className={styles.sparkline} viewBox={`0 0 ${width} ${height}`} role="img" aria-label={label}>
      <polygon points={area} fill={color} opacity="0.13" />
      <polyline points={points} fill="none" stroke={color} strokeWidth="2.5" strokeLinejoin="round" />
    </svg>
  );
}

function TrendChart({ feature }: { feature: FeatureCluster }) {
  const values = feature.weeklyCounts;
  const width = 780;
  const height = 230;
  const padding = { left: 42, right: 14, top: 20, bottom: 36 };
  const color = CATEGORY_COLORS[feature.category];
  if (!values.length) {
    return <div className={styles.chartEmpty}>This signal is newly captured and does not yet have a 12-week history.</div>;
  }
  const max = Math.max(...values, 1);
  const plotW = width - padding.left - padding.right;
  const plotH = height - padding.top - padding.bottom;
  const x = (index: number) => padding.left + (index / Math.max(values.length - 1, 1)) * plotW;
  const y = (value: number) => padding.top + plotH - (value / max) * plotH;
  const line = values.map((value, index) => `${x(index)},${y(value)}`).join(" ");
  const area = `${padding.left},${padding.top + plotH} ${line} ${padding.left + plotW},${padding.top + plotH}`;
  const ticks = [0, Math.round(max / 2), max];
  return (
    <svg className={styles.detailChart} viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`${feature.label} weekly article trend`}>
      {ticks.map((tick) => (
        <g key={tick}>
          <line x1={padding.left} x2={width - padding.right} y1={y(tick)} y2={y(tick)} className={styles.chartGrid} />
          <text x={padding.left - 9} y={y(tick) + 4} textAnchor="end" className={styles.chartLabel}>
            {tick}
          </text>
        </g>
      ))}
      <polygon points={area} fill={color} opacity="0.14" />
      <polyline points={line} fill="none" stroke={color} strokeWidth="3" strokeLinejoin="round" strokeLinecap="round" />
      {values.map((value, index) => (
        <circle key={`${index}-${value}`} cx={x(index)} cy={y(value)} r="3.5" fill={color} />
      ))}
      <text x={padding.left} y={height - 9} className={styles.chartLabel}>12 weeks ago</text>
      <text x={width - padding.right} y={height - 9} textAnchor="end" className={styles.chartLabel}>Latest week</text>
    </svg>
  );
}

function NewsDetail({ item }: { item: FeatureNewsItem }) {
  return (
    <article className={styles.newsItem}>
      <div className={styles.newsMeta}>
        <span>{item.source}</span>
        <span>{item.publishedLabel ?? item.date}</span>
        {item.impact && <strong>{item.impact}</strong>}
      </div>
      <a href={item.url} target="_blank" rel="noreferrer" className={styles.newsTitle}>
        {item.title}
      </a>
      <div className={styles.brandChips}>
        {item.brands.map((brand) => <span key={brand}>{brand}</span>)}
      </div>
      {item.summary && <p>{item.summary}</p>}
      {item.bmwRelevance && (
        <div className={styles.detailCallout}>
          <b>BMW relevance</b>
          <span>{item.bmwRelevance}</span>
        </div>
      )}
      {item.pmAction && (
        <div className={styles.detailCallout}>
          <b>PM action</b>
          <span>{item.pmAction}</span>
        </div>
      )}
    </article>
  );
}

export function FeatureTrendsPage() {
  usePageTitle("Feature Radar");
  const allIds = useMemo(() => featureClusters.map((feature) => feature.id), []);
  const [enabledIds, setEnabledIds] = useState<Set<string>>(() => new Set(allIds));
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedProblemId, setSelectedProblemId] = useState<string | null>(null);
  const [problemAnalysis, setProblemAnalysis] = useState<SavedProblemAnalysis | null>(null);

  const selected = featureClusters.find((feature) => feature.id === selectedId) ?? null;
  const selectedProblem = problemAnalysis?.problems.find((problem) => problem.id === selectedProblemId) ?? null;
  const displayed = selectedProblem
    ? featureClusters.filter((feature) => selectedProblem.possible_feature_ids.includes(feature.id))
    : featureClusters.filter((feature) => enabledIds.has(feature.id));

  useEffect(() => {
    fetch(`${config.apiBaseUrl}/agent/problems`)
      .then((response) => response.ok ? response.json() : Promise.reject(new Error(`HTTP ${response.status}`)))
      .then((data: SavedProblemAnalysis) => setProblemAnalysis(data))
      .catch((error) => console.error("Failed to load saved problem analysis", error));
  }, []);

  useEffect(() => {
    if (!selected) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setSelectedId(null);
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [selected]);

  const setFeature = (id: string, checked: boolean) => {
    setEnabledIds((current) => {
      const next = new Set(current);
      if (checked) next.add(id);
      else next.delete(id);
      return next;
    });
  };

  const setCategory = (category: FeatureCategory, checked: boolean) => {
    setEnabledIds((current) => {
      const next = new Set(current);
      for (const feature of featureClusters.filter((item) => item.category === category)) {
        if (checked) next.add(feature.id);
        else next.delete(feature.id);
      }
      return next;
    });
  };

  const selectedNews = selected?.items ?? [];
  const problemsForFeature = (feature: FeatureCluster) => {
    const saved = problemAnalysis?.problems ?? [];
    return saved.filter((problem) => problem.possible_feature_ids.includes(feature.id)).slice(0, 3);
  };
  const selectedProblems = selected ? problemsForFeature(selected) : [];

  return (
    <>
      <NavBar mockMode={config.useMocks} />
      <main className={styles.page}>
        <header className={styles.hero}>
          <div>
            <p className={styles.eyebrow}>China intelligence · feature-level view</p>
            <h1>Feature Radar</h1>
            <p className={styles.lead}>
              Every captured item is labelled by vehicle brand, specific feature, and one of eight decision-ready categories.
              Activate only the signals you want to compare, then open a feature for its trend and evidence.
            </p>
          </div>
          <div className={styles.metaPanel}>
            <strong>{featureNewsMeta.itemCount}</strong><span>captured items</span>
            <strong>{featureNewsMeta.featureCount}</strong><span>feature labels</span>
            <strong>{featureNewsMeta.categoryCount}</strong><span>categories</span>
          </div>
        </header>

        <ProblemChart analysis={problemAnalysis} selectedId={selectedProblemId} onSelect={setSelectedProblemId} />

        <div className={styles.workspace}>
          <aside className={styles.filters} aria-label="Feature filters">
            <div className={styles.filterHeader}>
              <div><p className={styles.kicker}>Feature list</p><h2>Activate signals</h2></div>
              <span>{enabledIds.size}/{featureClusters.length}</span>
            </div>
            <div className={styles.filterActions}>
              <button type="button" onClick={() => setEnabledIds(new Set(allIds))}>All</button>
              <button type="button" onClick={() => setEnabledIds(new Set())}>None</button>
            </div>
            {FEATURE_CATEGORIES.map((category) => {
              const categoryFeatures = featureClusters.filter((feature) => feature.category === category);
              if (!categoryFeatures.length) return null;
              const checked = categoryFeatures.every((feature) => enabledIds.has(feature.id));
              const someChecked = categoryFeatures.some((feature) => enabledIds.has(feature.id));
              return (
                <section className={styles.filterGroup} key={category}>
                  <label className={styles.categoryToggle}>
                    <input
                      type="checkbox"
                      checked={checked}
                      ref={(input) => { if (input) input.indeterminate = someChecked && !checked; }}
                      onChange={(event) => setCategory(category, event.target.checked)}
                    />
                    <span className={styles.categoryDot} style={{ background: CATEGORY_COLORS[category] }} />
                    <b>{category}</b>
                  </label>
                  <div className={styles.featureToggles}>
                    {categoryFeatures.map((feature) => (
                      <label key={feature.id}>
                        <input
                          type="checkbox"
                          checked={enabledIds.has(feature.id)}
                          onChange={(event) => setFeature(feature.id, event.target.checked)}
                        />
                        <span>{feature.label}</span>
                      </label>
                    ))}
                  </div>
                </section>
              );
            })}
          </aside>

          <section className={styles.results} aria-live="polite">
            <div className={styles.resultsHeader}>
              <div>
                <p className={styles.kicker}>Feature trends</p>
                <h2>{selectedProblem ? `Possible features for ${selectedProblem.name}` : "All active signals"}</h2>
              </div>
              <span>{displayed.length} features · {problemAnalysis?.problems.length ?? 0} saved problems</span>
            </div>
            {displayed.length ? (
              <div className={styles.featureGrid}>
                {displayed.map((feature) => {
                  const color = CATEGORY_COLORS[feature.category];
                  const linkedProblems = problemsForFeature(feature);
                  return (
                    <button key={feature.id} type="button" className={styles.featureCard} onClick={() => setSelectedId(feature.id)}>
                      <div className={styles.cardTop}>
                        <span className={styles.categoryPill} style={{ "--category-color": color } as CSSProperties}>{feature.category}</span>
                        <span className={`${styles.signal} ${feature.signal === "Accelerating" ? styles.signalUp : ""}`}>{feature.signal}</span>
                      </div>
                      <Sparkline values={feature.weeklyCounts} color={color} label={`${feature.label} weekly trend`} />
                      <h3>{feature.brandCounts[0]?.brand ?? "Industry"}: {feature.label}</h3>
                      <div className={styles.cardProblemTags}>
                        {linkedProblems.map((problem) => (
                          <span key={problem.id}>{problem.name} · {problem.mention_count}</span>
                        ))}
                        {!linkedProblems.length && <span className={styles.problemTagMuted}>No linked customer problem</span>}
                      </div>
                      <p className={styles.cnLabel}>{feature.labelCn}</p>
                      <div className={styles.cardStats}>
                        <span><b>{feature.momentumPctChange === null ? "—" : fmtPct(feature.momentumPctChange)}</b> momentum</span>
                        <span><b>{feature.items.length}</b> related items</span>
                      </div>
                      <div className={styles.itemMetadata}>
                        <span className={styles.categoryBubble}><b>Category</b> {feature.category}</span>
                        {feature.brandCounts.slice(0, 3).map(({ brand, count }) => (
                          <span className={styles.brandTag} key={brand}><b>Brand</b> {brand} · {count}</span>
                        ))}
                      </div>
                      <span className={styles.openHint}>Open trend & evidence →</span>
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className={styles.emptyState}>
                <h3>No active features.</h3>
                <p>Enable features in the left panel to restore signals.</p>
              </div>
            )}
          </section>
        </div>
      </main>
      <Footer />

      {selected && (
        <div className={styles.modalBackdrop} role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setSelectedId(null); }}>
          <section className={styles.modal} role="dialog" aria-modal="true" aria-labelledby="feature-detail-title">
            <button type="button" className={styles.closeButton} onClick={() => setSelectedId(null)} aria-label="Close feature detail">×</button>
            <div className={styles.modalHeading}>
              <span className={styles.categoryPill} style={{ "--category-color": CATEGORY_COLORS[selected.category] } as CSSProperties}>{selected.category}</span>
              <h2 id="feature-detail-title">{selected.brandCounts[0]?.brand ?? "Industry"}: {selected.label}</h2>
              <p>{selected.labelCn}</p>
            </div>
            <div className={styles.detailStats}>
              <span><b>{selected.momentumPctChange === null ? "—" : fmtPct(selected.momentumPctChange)}</b> momentum</span>
              <span><b>{selected.volumeRecent}</b> recent articles</span>
              <span><b>{selected.breadthOutlets}</b> outlets</span>
              <span><b>{selectedNews.length}</b> captured evidence items</span>
            </div>
            <div className={styles.chartPanel}>
              <div><h3>12-week coverage trend</h3><p>Weekly article count for this specific feature label</p></div>
              <TrendChart feature={selected} />
            </div>
            {selectedProblems.length > 0 && (
              <div className={styles.linkedProblems}>
                <h3>Linked customer problems</h3>
                {selectedProblems.map((problem) => (
                  <div key={problem.id}>
                    <b>{problem.name}</b>
                    <span>{problem.problem_statement} · {problem.mention_count} mentions</span>
                  </div>
                ))}
              </div>
            )}
            <div className={styles.relatedHeader}>
              <div><h3>Related news & detail items</h3><p>All detected brands</p></div>
            </div>
            <div className={styles.newsList}>
              {selectedNews.map((item) => <NewsDetail key={item.id} item={item} />)}
            </div>
          </section>
        </div>
      )}
    </>
  );
}

