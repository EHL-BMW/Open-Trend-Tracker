import { useId, useRef, useState } from "react";
import {
  DOMAIN_COLORS,
  fmtP,
  fmtPct,
  SHORT_TOPIC_NAMES,
  trendRadarData,
  type BmwDomainStat,
} from "../content/trendRadar";
import { HEADLINE_EN, SOURCE_EN } from "../content/translations";
import { HEADLINE_NOTES } from "../content/headlineNotes";
import { TrackButton } from "../components/TrackButton";
import { ContentPage } from "./ContentPage";
import styles from "./NewsletterPage.module.css";

interface TopicAnnotations {
  basis: "headline";
  items: Array<{ link: string; title_en: string; feature_summary: string }>;
}

function Sparkline({
  data,
  color,
  width = 104,
  height = 26,
}: {
  data: number[];
  color: string;
  width?: number;
  height?: number;
}) {
  const max = Math.max(...data, 0.001);
  const step = width / Math.max(data.length - 1, 1);
  const points = data
    .map((v, i) => `${(i * step).toFixed(1)},${(height - 2 - (v / max) * (height - 4)).toFixed(1)}`)
    .join(" ");
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} aria-hidden="true">
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="1.6"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function NewsletterPage() {
  const [openTopicId, setOpenTopicId] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [annotationsByTopic, setAnnotationsByTopic] = useState<Record<string, TopicAnnotations>>({});
  const [annotationErrors, setAnnotationErrors] = useState<Record<string, string>>({});
  const loadingTopics = useRef(new Set<string>());
  const mapSvgId = useId();

  const loadAnnotations = async (topicId: string) => {
    if (annotationsByTopic[topicId] || loadingTopics.current.has(topicId)) return;
    const topic = trendRadarData.topics.find((item) => item.id === topicId);
    loadingTopics.current.add(topicId);
    try {
      const response = await fetch(`/api/v1/news/annotations/${encodeURIComponent(topicId)}`, { method: "POST" });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail ?? `HTTP ${response.status}`);
      setAnnotationsByTopic((current) => ({ ...current, [topicId]: result as TopicAnnotations }));
      setAnnotationErrors((current) => {
        const next = { ...current };
        delete next[topicId];
        return next;
      });
    } catch (error) {
      if (!topic?.headlines.every((headline) => HEADLINE_NOTES[topicId]?.[headline.title])) {
        setAnnotationErrors((current) => ({
          ...current,
          [topicId]: error instanceof Error ? error.message : "Could not generate news annotations",
        }));
      }
    } finally {
      loadingTopics.current.delete(topicId);
    }
  };

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage((current) => (current === msg ? null : current));
    }, 4500);
  };

  const handleOpenTopic = (id: string) => {
    setOpenTopicId(id);
    const el = document.getElementById(`topic-${id}`);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      const res = await fetch("/api/refresh-trends", { method: "POST" });
      const result = await res.json();
      if (res.ok) {
        window.location.reload();
      } else {
        showToast(result.detail ?? `Trend refresh failed (HTTP ${res.status}).`);
      }
    } catch {
      showToast("Could not reach the trend refresh service. Check that the backend is running.");
    } finally {
      setIsRefreshing(false);
    }
  };

  const { generated_at, window: win, totals, topics, bmw_domains, method } = trendRadarData;

  // Top 3 signals: priority among accelerating movers
  const accelerating = topics.filter((t) => t.signal === "Accelerating");
  const topSignals = (accelerating.length >= 3 ? accelerating : topics).slice(0, 3);

  // SVG Trend Map geometry
  const W = 1100;
  const H = 420;
  const P = { l: 56, r: 24, t: 24, b: 40 };
  const rawXs = topics.map((t) => Math.log10(t.volume_recent + 1));
  const rawYs = topics.map((t) => Math.log2(t.momentum));
  const xMin = Math.min(...rawXs) - 0.1;
  const xMax = Math.max(...rawXs) + 0.1;
  const yAbs = Math.max(1, ...rawYs.map(Math.abs)) * 1.15;
  const calcX = (v: number) => P.l + ((v - xMin) / (xMax - xMin)) * (W - P.l - P.r);
  const calcY = (v: number) => P.t + ((yAbs - v) / (2 * yAbs)) * (H - P.t - P.b);

  const placedLabels: { x: number; y: number; w: number }[] = [];
  const getLabelPos = (cx: number, cy: number, r: number, text: string) => {
    const w = text.length * 6.6;
    const h = 14;
    const right = cx < W * 0.78;
    const x0 = right ? cx + r + 6 : cx - r - 6 - w;
    let y = cy + 4;
    for (let k = 0; k < 8; k++) {
      const hit = placedLabels.some((b) => x0 < b.x + b.w && x0 + w > b.x && Math.abs(y - b.y) < h);
      if (!hit) break;
      y += (k % 2 ? -1 : 1) * h * (k + 1);
    }
    placedLabels.push({ x: x0, y, w });
    return { x: right ? cx + r + 6 : cx - r - 6, y, anchor: (right ? "start" : "end") as "start" | "end" };
  };

  const mapTopics = topics
    .map((t, idx) => ({
      topic: t,
      cx: calcX(rawXs[idx] ?? 0),
      cy: calcY(rawYs[idx] ?? 0),
      isSignificant: t.signal !== "Stable",
    }))
    .sort((a, b) => (a.topic.signal === "Stable" ? 1 : 0) - (b.topic.signal === "Stable" ? 1 : 0));

  const usedDomains = Array.from(new Set(topics.map((t) => t.bmw_domain)));

  return (
    <ContentPage
      eyebrow="Newsletter · China Tech Intelligence"
      title="China EV-Tech Trend Radar"
      lead="Which technologies Chinese media is covering, how fast coverage is growing, and how each one maps to BMW customer pain."
    >
      <div className={styles.headerWrap}>
        <div className={styles.metaRow}>
          <span>
            Last scrape <b>{generated_at}</b>
          </span>
          <span>
            <b>{totals.articles.toLocaleString()}</b> articles
          </span>
          <span>
            <b>{totals.outlets}</b> Chinese outlets
          </span>
          <span>
            <b>{totals.topics}</b> tech topics
          </span>
          <span>
            <b>{win.weeks}</b> weeks ({win.start} → {win.end})
          </span>
        </div>
        <button
          type="button"
          className={styles.rescrapeBtn}
          onClick={handleRefresh}
          disabled={isRefreshing}
          aria-label="Re-scrape now"
        >
          {isRefreshing ? "↻ Scraping…" : "↻ Re-scrape now"}
        </button>
      </div>

      {/* 1. Top 3 Signals */}
      <section className={styles.section} aria-labelledby="top-signals-heading">
        <div className={styles.sectionHead}>
          <div>
            <h2 id="top-signals-heading">Top 3 signals</h2>
            <div className={styles.hint}>Highest priority score among topics with statistically significant growth</div>
          </div>
        </div>
        <div className={styles.signals}>
          {topSignals.map((t, idx) => {
            const dom: Partial<BmwDomainStat> = bmw_domains[t.bmw_domain] ?? {};
            const isUp = t.momentum_pct_change >= 0;
            return (
              <article
                key={t.id}
                className={styles.signalCard}
                onClick={() => handleOpenTopic(t.id)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    handleOpenTopic(t.id);
                  }
                }}
              >
                <div className={styles.signalRank}>
                  #{idx + 1} · PRIORITY {t.priority.toFixed(1)}
                </div>
                <div className={styles.signalName}>
                  {t.label_en}
                  <span className={styles.cn}>{t.label_cn}</span>
                </div>
                <div className={`${styles.signalBig} ${isUp ? styles.up : styles.down}`}>
                  {fmtPct(t.momentum_pct_change)}
                </div>
                <div className={styles.signalFacts}>
                  relative share of voice, last {win.recent_weeks} wks vs prior {win.weeks - win.recent_weeks} (
                  {fmtP(t.p_momentum)})
                  <br />
                  {t.volume_recent} articles · {t.breadth_outlets} outlets
                </div>
                <div className={styles.signalBmw}>
                  <div className={styles.bmwDomainLabel}>
                    <span
                      className={styles.bmwDomainDot}
                      style={{ backgroundColor: DOMAIN_COLORS[t.bmw_domain] || "#94a3b8" }}
                    />
                    Linked BMW domain: <b>{t.bmw_domain}</b>
                  </div>
                  <div className={styles.signalBmwSub}>
                    {dom.complaints ?? "–"} customer complaints · top: {(dom.top_components || "").split(";")[0]}
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      </section>

      {/* 2. Trend Map */}
      <section className={styles.section} aria-labelledby="trend-map-heading">
        <div className={styles.sectionHead}>
          <div>
            <h2 id="trend-map-heading">Trend map</h2>
            <div className={styles.hint}>
              Right = more coverage · Up = gaining share · Size = BMW customer pain · Only significant moves are
              labelled (hover for the rest)
            </div>
          </div>
        </div>
        <div className={styles.mapCard}>
          <svg className={styles.mapSvg} viewBox={`0 0 ${W} ${H}`} role="img" aria-labelledby={`${mapSvgId}-title`}>
            <title id={`${mapSvgId}-title`}>China EV-Tech Trend Radar Quadrant Map</title>
            {/* Axis Lines and Ticks */}
            {[-1, 0, 1]
              .filter((v) => Math.abs(v) <= yAbs)
              .map((v) => (
                <g key={`ytick-${v}`}>
                  <text x={P.l - 10} y={calcY(v) + 4} fontSize="10.5" fill="currentColor" opacity={0.4} textAnchor="end">
                    {v === 0 ? "0%" : fmtPct((2 ** v - 1) * 100)}
                  </text>
                  {v === 0 && (
                    <line
                      x1={P.l}
                      x2={W - P.r}
                      y1={calcY(0)}
                      y2={calcY(0)}
                      stroke="currentColor"
                      strokeOpacity={0.16}
                      strokeDasharray="4 4"
                    />
                  )}
                </g>
              ))}

            {[10, 30, 100, 300, 1000]
              .filter((v) => Math.log10(v + 1) >= xMin && Math.log10(v + 1) <= xMax)
              .map((v) => (
                <text
                  key={`xtick-${v}`}
                  x={calcX(Math.log10(v + 1))}
                  y={H - P.b + 20}
                  fontSize="10.5"
                  fill="currentColor"
                  opacity={0.4}
                  textAnchor="middle"
                >
                  {v}
                </text>
              ))}

            {/* Quadrant Markers */}
            <text x={P.l + 6} y={P.t + 10} fontSize="10" fill="currentColor" opacity={0.3} fontWeight="700" letterSpacing="1.5">
              EMERGING
            </text>
            <text x={W - P.r - 6} y={P.t + 10} fontSize="10" fill="currentColor" opacity={0.3} fontWeight="700" letterSpacing="1.5" textAnchor="end">
              MAINSTREAMING
            </text>
            <text x={P.l + 6} y={H - P.b - 8} fontSize="10" fill="currentColor" opacity={0.3} fontWeight="700" letterSpacing="1.5">
              FADING
            </text>
            <text x={W - P.r - 6} y={H - P.b - 8} fontSize="10" fill="currentColor" opacity={0.3} fontWeight="700" letterSpacing="1.5" textAnchor="end">
              COOLING
            </text>

            {/* Topic Bubbles */}
            {mapTopics.map(({ topic: t, cx, cy, isSignificant }) => {
              const r = 5 + t.bmw_exposure * 7;
              const color = DOMAIN_COLORS[t.bmw_domain] || "#94a3b8";
              const shortName = SHORT_TOPIC_NAMES[t.id] || t.label_en;
              const labelPos = isSignificant
                ? getLabelPos(cx, cy, r, shortName)
                : {
                    x: cx < W * 0.78 ? cx + r + 6 : cx - r - 6,
                    y: cy + 4,
                    anchor: (cx < W * 0.78 ? "start" : "end") as "start" | "end",
                  };

              return (
                <g
                  key={t.id}
                  className={styles.mapPoint}
                  onClick={() => handleOpenTopic(t.id)}
                  style={{ cursor: "pointer" }}
                >
                  <circle
                    className={styles.mapDot}
                    cx={cx}
                    cy={cy}
                    r={r}
                    fill={color}
                    fillOpacity={isSignificant ? 0.9 : 0.22}
                    stroke={color}
                    strokeOpacity={isSignificant ? 1 : 0.5}
                    strokeWidth="1.2"
                  >
                    <title>{`${t.label_en}: ${t.volume_recent} articles, ${fmtPct(t.momentum_pct_change)} (${fmtP(t.p_momentum)})`}</title>
                  </circle>
                  <text
                    className={isSignificant ? undefined : styles.mapHl}
                    x={labelPos.x}
                    y={labelPos.y}
                    textAnchor={labelPos.anchor}
                    fontSize="11.5"
                    fill="currentColor"
                    opacity={isSignificant ? 0.95 : 0.5}
                    fontWeight={isSignificant ? 600 : 400}
                  >
                    {shortName}
                  </text>
                </g>
              );
            })}
          </svg>

          {/* Domain Legend */}
          <div className={styles.legend}>
            {usedDomains.map((domainName) => (
              <span key={domainName} className={styles.legendItem}>
                <i
                  className={styles.legendDot}
                  style={{ backgroundColor: DOMAIN_COLORS[domainName] || "#94a3b8" }}
                />
                {domainName}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* 3. All topics ranked by priority */}
      <section className={styles.section} aria-labelledby="all-topics-heading">
        <div className={styles.sectionHead}>
          <div>
            <h2 id="all-topics-heading">All topics, ranked by priority</h2>
            <div className={styles.hint}>Click a row to see headlines (with source links), statistics, and the BMW link</div>
          </div>
        </div>
        <div className={styles.tableCard}>
          <div className={styles.thead}>
            <span>#</span>
            <span>Technology</span>
            <span>BMW domain</span>
            <span>{win.weeks}-wk share</span>
            <span style={{ textAlign: "right" }}>4 wks</span>
            <span style={{ textAlign: "right" }}>Δ</span>
            <span>Signal</span>
            <span style={{ textAlign: "right" }}>Outlets</span>
            <span>Priority</span>
          </div>

          {topics.map((t, idx) => {
            const color = DOMAIN_COLORS[t.bmw_domain] || "#94a3b8";
            const dom: Partial<BmwDomainStat> = bmw_domains[t.bmw_domain] ?? {};
            const delta = t.momentum_pct_change;
            const isOpen = openTopicId === t.id;

            return (
              <details
                key={t.id}
                id={`topic-${t.id}`}
                className={styles.topicDetails}
                open={isOpen}
                onToggle={(e) => {
                  const target = e.currentTarget;
                  if (target.open) {
                    setOpenTopicId(t.id);
                    void loadAnnotations(t.id);
                  } else if (openTopicId === t.id) {
                    setOpenTopicId(null);
                  }
                }}
              >
                <summary className={styles.topicRow}>
                  <span className={`${styles.mono} ${styles.hint}`}>{idx + 1}</span>
                  <div>
                    <b>{t.label_en}</b>
                    <br />
                    <span className={styles.cn}>{t.label_cn}</span>
                    <span className={styles.topicTrack}><TrackButton id={t.id} label={t.label_en} compact /></span>
                  </div>
                  <span className={`${styles.domBadge} ${styles.hideSm}`}>
                    <i className={styles.domBadgeDot} style={{ backgroundColor: color }} />
                    {t.bmw_domain}
                  </span>
                  <span className={styles.hideSm}>
                    <Sparkline data={t.weekly_share} color={color} />
                  </span>
                  <span className={styles.numRight}>{t.volume_recent}</span>
                  <span
                    className={styles.numRight}
                    style={{ color: delta >= 0 ? "var(--green)" : "var(--danger)" }}
                  >
                    {fmtPct(delta)}
                  </span>
                  <span>
                    <span className={`${styles.pill} ${styles[t.signal]}`}>{t.signal}</span>
                  </span>
                  <span className={`${styles.numRight} ${styles.hideSm}`}>{t.breadth_outlets}</span>
                  <span className={styles.hideSm}>
                    <div className={styles.prioBarWrap}>
                      <div className={styles.prioBar}>
                        <div className={styles.prioBarFill} style={{ width: `${Math.min(t.priority, 100)}%` }} />
                      </div>
                      <span className={`${styles.mono} ${styles.hint}`}>{t.priority.toFixed(1)}</span>
                    </div>
                  </span>
                </summary>

                <div className={styles.topicDetailPanel}>
                  <div>
                    <h3 className={styles.detailHeading}>Latest Chinese headlines</h3>
                    <p className={styles.headlineHint}>Hover or focus a headline for a feature-focused AI note.</p>
                    {annotationErrors[t.id] && <p className={styles.annotationError}>{annotationErrors[t.id]}</p>}
                    {t.headlines.length > 0 ? (
                      <ul className={styles.headlineList}>
                        {t.headlines.map((h, hIdx) => {
                          const annotation = annotationsByTopic[t.id]?.items[hIdx];
                          const note = HEADLINE_NOTES[t.id]?.[h.title];
                          const translated = annotation?.title_en ?? note?.titleEn ?? HEADLINE_EN[h.title];
                          return (
                            <li key={h.link} className={styles.headlineItem}>
                              <div className={styles.headlineTitleRow}>
                                <a href={h.link} target="_blank" rel="noopener noreferrer" className={styles.headlineLink}>
                                  {h.title} ↗
                                </a>
                                <button
                                  type="button"
                                  className={styles.summaryTrigger}
                                  aria-label={`Feature summary for ${h.title}`}
                                  aria-describedby={`summary-${t.id}-${hIdx}`}
                                >ⓘ</button>
                              </div>
                              <div className={styles.headlineTranslation}>
                                EN · {translated ?? (annotationErrors[t.id] ? "Translation unavailable" : "Generating translation…")}
                              </div>
                              <div className={styles.headlineMeta}>{SOURCE_EN[h.source] ?? h.source} · {h.date}</div>
                              <div id={`summary-${t.id}-${hIdx}`} className={styles.headlineTooltip} role="tooltip">
                                <b>AI feature summary · based on headline</b>
                                <p>{annotation?.feature_summary ?? note?.featureSummary ?? (annotationErrors[t.id]
                                  ? "Summary unavailable until the AI service is configured."
                                  : "Generating a feature-focused summary…")}</p>
                              </div>
                            </li>
                          );
                        })}
                      </ul>
                    ) : (
                      <div className={styles.hint}>No articles in the recent window.</div>
                    )}
                  </div>

                  <div>
                    <h3 className={styles.detailHeading}>Statistics</h3>
                    <div className={styles.statLine}>
                      Relative rate ratio <b>{t.momentum.toFixed(2)}×</b> vs. basket ({fmtP(t.p_momentum)})
                      <br />
                      Mann-Kendall share trend z = <b>{t.mk_z.toFixed(2)}</b> ({fmtP(t.mk_p)})
                      <br />
                      Sen&apos;s slope <b>{t.sens_slope_share_pp_per_week > 0 ? "+" : ""}{t.sens_slope_share_pp_per_week}</b> pp share/week
                      <br />
                      Share of voice <b>{(t.share_of_voice * 100).toFixed(1)}%</b> · Quadrant <b>{t.quadrant}</b>
                      {t.resolved_quota_days ? (
                        <>
                          <br />
                          <span style={{ color: "#38bdf8", fontSize: "12px" }}>
                            ⚡ <b>Feed Quota Resolved:</b> {t.resolved_quota_days} peak day(s) adaptively partitioned across 5 media cohorts (+{t.recovered_quota_articles} unique articles recovered beyond 100-item ceiling)
                          </span>
                        </>
                      ) : t.saturated_days ? (
                        <>
                          <br />
                          <span style={{ color: "#fbbf24", fontSize: "12px" }}>
                            ⚠ {t.saturated_days} day(s) hit 100-item cap; lower bound
                          </span>
                        </>
                      ) : null}
                    </div>

                    <h3 className={styles.detailHeading} style={{ marginTop: "16px" }}>
                      Top outlets
                    </h3>
                    <div className={styles.statLine}>
                      {t.top_outlets.length > 0
                        ? t.top_outlets.map(([outlet, count]) => `${SOURCE_EN[outlet] ?? outlet} (${count})`).join(" · ")
                        : "–"}
                    </div>

                    <h3 className={styles.detailHeading} style={{ marginTop: "16px" }}>
                      BMW link
                    </h3>
                    <div className={styles.statLine}>
                      <b>{t.bmw_domain}</b>: {dom.complaints ?? "–"} complaints, avg severity {dom.avg_severity ?? "–"}
                      <br />
                      {dom.top_components || ""}
                    </div>

                    <h3 className={styles.detailHeading} style={{ marginTop: "16px" }}>
                      Query
                    </h3>
                    <div className={styles.queryBox}>{t.query}</div>
                  </div>
                </div>
              </details>
            );
          })}
        </div>
      </section>

      {/* 4. Methodology */}
      <section className={styles.section} aria-labelledby="method-heading">
        <details className={styles.methodDetails}>
          <summary className={styles.methodSummary}>
            <span id="method-heading">How the numbers are computed ▸</span>
          </summary>
          <ol className={styles.methodList}>
            <li>
              <b>Scrape</b>: one Chinese keyword query per topic, run against {trendRadarData.source} in {win.weeks} consecutive 7-day windows. Peak days hitting feed limits are adaptively partitioned across 5 media cohorts (Sina, Sohu, Auto specialists, Financial press, Remainder) to recover the full census without truncation.
            </li>
            <li>
              <b>Momentum</b>: {method.momentum} <b>Significance</b>: {method.p_momentum}
            </li>
            <li>
              <b>Trend</b>: {method.trend} <b>Breadth</b>: {method.breadth}
            </li>
            <li>
              <b>BMW exposure</b>: {method.exposure}
            </li>
            <li>
              <b>Priority</b>: {method.priority} <b>Signal</b>: {method.signal}
            </li>
            <li>
              <b>Quota resolution</b>: {method.quota_resolution || "Adaptive multi-tier domain & keyword partitioning"}
            </li>
            <li>
              <b>Raw data</b>: <code>china_tech_trends_articles.csv</code> · <code>china_tech_trends.json</code> · re-run with <code>python3 scrape_china_tech_trends.py</code>
            </li>
            <li>
              <b>Caveat</b>: measures media attention, not technical maturity. Read it as a signal of forward market direction.
            </li>
          </ol>
        </details>
      </section>

      {/* Toast Notification */}
      <div className={`${styles.toast} ${toastMessage ? styles.show : ""}`} role="status">
        {toastMessage}
      </div>
    </ContentPage>
  );
}
