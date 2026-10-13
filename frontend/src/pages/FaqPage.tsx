import { useState } from "react";
import { ContentPage } from "./ContentPage";
import styles from "./FaqPage.module.css";
import { impactFaqs } from "./faqImpact";

type CategoryFilter = "all" | "catalog" | "cleaning" | "domains" | "math" | "backlog" | "impactData" | "impactMath";

interface FaqItem {
  id: string;
  category: CategoryFilter;
  question: string;
  content: React.ReactNode;
}

export function FaqPage() {
  const [filter, setFilter] = useState<CategoryFilter>("all");

  const faqs: FaqItem[] = [
    // Phase 1: Catalog
    {
      id: "catalog-models",
      category: "catalog",
      question: "Which BMW vehicles and option lists are tracked in the baseline catalog?",
      content: (
        <>
          <p>
            The project began with an exhaustive census of all battery-electric (BEV) and plug-in hybrid (PHEV) vehicles produced by BMW for Europe and global markets. Leveraging official ADAC specifications and BMW price equipment lists, technical metrics and equipment codes were inventoried across <strong>Interior, Exterior, and Driver Assistance</strong>:
          </p>
          <ul>
            <li><strong>53 Total Models:</strong> 28 pure BEVs (iX1, i4, i5, i7, iX) and 25 PHEVs (225xe, 330e, 530e, 550e, 750e, M760e, X1–X5 xDrive PHEVs).</li>
            <li><strong>Battery Spectrum:</strong> From 14.9 kWh (225xe) to 105.2 kWh (iX xDrive50 long-range SAV).</li>
            <li><strong>Range Spectrum:</strong> 283 km to 630 km official WLTP range.</li>
            <li><strong>Interior Attributes:</strong> BMW Curved Display (12.3&quot; + 14.9&quot;), BMW Interaction Bar, Veganza synthetic leather vs. Leather Merino, Bowers &amp; Wilkins Diamond Surround Sound, Panoramadach Sky Lounge, 31.3&quot; Theatre Screen (i7).</li>
            <li><strong>Exterior Attributes:</strong> BMW Kidney Grille Iconic Glow, Adaptive LED / Matrix headlights, flush door handles, automatic comfort doors (i7), non-contact kick-sensor tailgate.</li>
            <li><strong>Driver Assistance:</strong> Highway Assistant (Hands-free L2+ up to 130 km/h with eye-tracking lane changes), Parking Assistant Professional (smartphone remote control).</li>
          </ul>
        </>
      ),
    },
    {
      id: "catalog-options",
      category: "catalog",
      question: "How does OpenTT represent optional packages versus standard equipment?",
      content: (
        <>
          <p>
            Every option code from official PDF option lists (e.g. <code>5AU Driving Assistant Professional</code>, <code>5DW Parking Assistant Professional</code>, <code>3DN Iconic Glow</code>) is indexed as a discrete capability with its price list reference. In the Planner, Features / Engineering options act as strict architectural filters, ensuring the model never recommends a feature without verifying whether it already exists as standard or optional equipment on the current model series.
          </p>
        </>
      ),
    },

    // Phase 2: Cleaning Funnel
    {
      id: "funnel-ice",
      category: "cleaning",
      question: "How was the dataset cleaned to isolate electric vehicle pain points from combustion noise?",
      content: (
        <>
          <p>
            Customer studies originally contained thousands of internal combustion engine (ICE) survey entries. Mixing exhaust pipe, diesel particle filter, or traditional gearbox feedback with EV architectures would severely distort product decisions. We built an empirical cohort intersection funnel to filter the data:
          </p>
          <div className={styles.funnelGrid}>
            <div className={styles.funnelBox}>
              <div className={styles.statLabel}>Total Survey Pool</div>
              <div className={styles.funnelVal}>9,695 Records</div>
              <div className={styles.statSub}>Raw G60 5 Series &amp; G70 7 Series feedback</div>
            </div>
            <div className={styles.funnelArrow}>➔</div>
            <div className={`${styles.funnelBox} ${styles.eliminated}`}>
              <div className={styles.statLabel} style={{ color: "var(--danger)" }}>Eliminated Pure ICE</div>
              <div className={styles.funnelVal} style={{ color: "var(--danger)" }}>-5,724 Cases</div>
              <div className={styles.statSub}>520i, 520d, 740i etc. 100% excluded</div>
            </div>
            <div className={styles.funnelArrow}>➔</div>
            <div className={`${styles.funnelBox} ${styles.accepted}`}>
              <div className={styles.statLabel} style={{ color: "var(--green)" }}>Verified Electrified Cohort</div>
              <div className={styles.funnelVal} style={{ color: "var(--green)" }}>16 Models / 3,971 Cases</div>
              <div className={styles.statSub}>Pure i5, i7, 5er PHEV &amp; 7er PHEV cases</div>
            </div>
          </div>
          <p>
            The resulting 3,971 customer cases break down across four electrified model cohorts:
          </p>
          <ul>
            <li><strong>i5 BEV (G60 / G61):</strong> 1,763 cases across 6 matched models (eDrive40 &amp; M60 Sedan and Touring).</li>
            <li><strong>i7 BEV (G70):</strong> 1,347 cases across 3 matched models (eDrive50, xDrive60, M70).</li>
            <li><strong>5 Series PHEV (G60):</strong> 474 cases across 5 matched models (530e, 550e Sedan &amp; Touring).</li>
            <li><strong>7 Series PHEV (G70):</strong> 387 cases across 2 matched models (750e, M760e xDrive).</li>
          </ul>
        </>
      ),
    },
    {
      id: "funnel-f70",
      category: "cleaning",
      question: "Why was the F70 (1 Series) excluded from the electrified study cohort?",
      content: (
        <>
          <p>
            The F70 customer study files predominantly consist of entry-level combustion models with 48V mild hybrid systems. Because they lack high-voltage battery architecture, DC fast charging, and dedicated EV thermal management, including them would dilute the statistical power of battery range, cold charging curves, and digital ecosystem analyses.
          </p>
        </>
      ),
    },

    // Phase 3: 7 Domains
    {
      id: "domains-mece",
      category: "domains",
      question: "What are the 7 Technology Domains and why are they MECE?",
      content: (
        <>
          <p>
            Classification follows internationally recognized automotive benchmark standards (CPCA, Dongchedi, McKinsey Connected Vehicle). The 7 domains are <strong>strictly MECE</strong> (Mutually Exclusive, Collectively Exhaustive), creating unambiguous boundaries between physical chassis hardware, in-cabin software, high-voltage powertrains, and off-board connectivity:
          </p>
          <div className={styles.domainGrid}>
            <div className={styles.domainCard}>
              <div className={styles.domainHead}>
                <span className={`${styles.domainBadge} ${styles.neg}`}>Prio 1 Backlog</span>
                <span className={styles.statSub}>16.65% Cases</span>
              </div>
              <div className={styles.domainTitle}>⚡ 1. Energy &amp; Charging</div>
              <div className={styles.domainAspect}>Charging experience, range management, power distribution</div>
              <div className={styles.domainStats}>
                <span>Likes: <strong>125</strong></span>
                <span>Friction: <strong>315</strong></span>
                <span>Net: <strong style={{ color: "var(--danger)" }}>-43.2%</strong></span>
              </div>
              <p className={styles.domainNotes}>
                <strong>Core Friction:</strong> Up to 35% winter range reduction; cold-battery charging throttling down to 60 kW on third-party chargers due to late battery pre-conditioning.
              </p>
            </div>

            <div className={styles.domainCard}>
              <div className={styles.domainHead}>
                <span className={`${styles.domainBadge} ${styles.mid}`}>Lowest Defect Rate</span>
                <span className={styles.statSub}>8.14% Cases</span>
              </div>
              <div className={styles.domainTitle}>🛡️ 2. Driving Assistance</div>
              <div className={styles.domainAspect}>Highway pilot, automated parking, human-machine handoff</div>
              <div className={styles.domainStats}>
                <span>Likes: <strong>68</strong></span>
                <span>Friction: <strong>154</strong></span>
                <span>Net: <strong style={{ color: "var(--danger)" }}>-38.7%</strong></span>
              </div>
              <p className={styles.domainNotes}>
                <strong>Core Insight:</strong> Extremely low technical defect rate (only 11% defects); negative ratings stem almost exclusively from EU GSR2 regulatory overspeed warning chimes.
              </p>
            </div>

            <div className={styles.domainCard}>
              <div className={styles.domainHead}>
                <span className={`${styles.domainBadge} ${styles.neg}`}>Highest Severity (2.03)</span>
                <span className={styles.statSub}>15.64% Cases</span>
              </div>
              <div className={styles.domainTitle}>🖥️ 3. Digital Cockpit &amp; AI</div>
              <div className={styles.domainAspect}>BMW OS 8.5/9, voice assistant, display interaction</div>
              <div className={styles.domainStats}>
                <span>Likes: <strong>153</strong></span>
                <span>Friction: <strong>296</strong></span>
                <span>Net: <strong style={{ color: "var(--danger)" }}>-31.8%</strong></span>
              </div>
              <p className={styles.domainNotes}>
                <strong>Core Friction:</strong> Removal of physical climate buttons; nested touchscreen menus create distraction during highway driving.
              </p>
            </div>

            <div className={styles.domainCard}>
              <div className={styles.domainHead}>
                <span className={`${styles.domainBadge} ${styles.neg}`}>Critical Friction (-76.7%)</span>
                <span className={styles.statSub}>11.21% Cases</span>
              </div>
              <div className={styles.domainTitle}>📱 4. Connected Ecosystem</div>
              <div className={styles.domainAspect}>My BMW App, Digital Key Plus (UWB), OTA updates, eSIM</div>
              <div className={styles.domainStats}>
                <span>Likes: <strong>28</strong></span>
                <span>Friction: <strong>212</strong></span>
                <span>Net: <strong style={{ color: "var(--danger)" }}>-76.7%</strong></span>
              </div>
              <p className={styles.domainNotes}>
                <strong>Core Friction:</strong> High timeout rate when triggering remote climate conditioning in underground parking garages; occasional wireless Apple CarPlay disconnects.
              </p>
            </div>

            <div className={styles.domainCard}>
              <div className={styles.domainHead}>
                <span className={`${styles.domainBadge} ${styles.mid}`}>Highest Volume (17.28%)</span>
                <span className={styles.statSub}>327 Cases</span>
              </div>
              <div className={styles.domainTitle}>🛋️ 5. Smart Cabin</div>
              <div className={styles.domainAspect}>Thermal comfort, seating, acoustic insulation, materials</div>
              <div className={styles.domainStats}>
                <span>Likes: <strong>257</strong></span>
                <span>Friction: <strong>327</strong></span>
                <span>Net: <strong style={{ color: "#d97706" }}>-12.0%</strong></span>
              </div>
              <p className={styles.domainNotes}>
                <strong>Core Friction:</strong> Veganza synthetic leather feels warm and sweaty in summer without active seat ventilation; panoramic glass roof warms cabin without mechanical shade.
              </p>
            </div>

            <div className={styles.domainCard}>
              <div className={styles.domainHead}>
                <span className={`${styles.domainBadge} ${styles.pos}`}>Brand Moat (+44.7%)</span>
                <span className={styles.statSub}>Top Score 9.95/10</span>
              </div>
              <div className={styles.domainTitle}>🏎️ 6. Vehicle Dynamics &amp; Safety</div>
              <div className={styles.domainAspect}>Chassis control, 2-axle air suspension, steering precision</div>
              <div className={styles.domainStats}>
                <span>Likes: <strong>630</strong></span>
                <span>Friction: <strong>241</strong></span>
                <span>Net: <strong style={{ color: "var(--green)" }}>+44.7%</strong></span>
              </div>
              <p className={styles.domainNotes}>
                <strong>Core Strength:</strong> The only positively rated domain in the entire electrified portfolio! Industry-leading steering feel, air suspension stability, and recuperation blending.
              </p>
            </div>

            <div className={styles.domainCard}>
              <div className={styles.domainHead}>
                <span className={`${styles.domainBadge} ${styles.mid}`}>High Severity (2.07)</span>
                <span className={styles.statSub}>17.07% Cases</span>
              </div>
              <div className={styles.domainTitle}>🚪 7. Smart Exterior</div>
              <div className={styles.domainAspect}>Automatic doors, kick-sensor tailgate, smart lighting</div>
              <div className={styles.domainStats}>
                <span>Likes: <strong>224</strong></span>
                <span>Friction: <strong>323</strong></span>
                <span>Net: <strong style={{ color: "#d97706" }}>-18.1%</strong></span>
              </div>
              <p className={styles.domainNotes}>
                <strong>Core Friction:</strong> i7 automatic comfort doors halt prematurely in tight parking spaces due to over-sensitive obstacle sensors; tailgate kick sensor requires repeated attempts.
              </p>
            </div>
          </div>
        </>
      ),
    },

    // Phase 4: Math & Analytics
    {
      id: "math-formulas",
      category: "math",
      question: "How are Net Sentiment and weighted domain severity mathematically calculated?",
      content: (
        <>
          <p>
            To prevent high-volume domains (such as Smart Cabin) from drowning out specialized technical friction (such as Connected Ecosystem), OpenTT applies two standardized mathematical formulas:
          </p>
          <div className={styles.formulaBox}>
            <code>Net Sentiment (%) = (Positive Feedback - Negative Friction) / (Positive + Negative) × 100</code>
          </div>
          <p>
            This normalizes sentiment between -100% (pure customer frustration) and +100% (unanimous customer praise).
          </p>
          <div className={styles.formulaBox}>
            <code>Weighted Severity = (Defect Count × Defect Severity Score + General Complaints × 1.0) / Total Cases</code>
          </div>
          <p>
            Defects carry a higher penalty than general subjective complaints, ensuring engineering safety risks and component failures are elevated above styling preferences.
          </p>
        </>
      ),
    },

    // Phase 5: Backlog & Strategy
    {
      id: "backlog-priorities",
      category: "backlog",
      question: "What are the Top 5 concrete engineering requirements derived for the successor vehicle?",
      content: (
        <>
          <p>
            By bridging verified customer pain with Chinese OEM competitive benchmarks (from the China EV-Tech Trend Radar), the pipeline produces 5 strategic product requirements for the PM:
          </p>
          <div className={styles.backlogList}>
            <div className={styles.backlogItem}>
              <div className={styles.backlogNum}>1</div>
              <div className={styles.backlogContent}>
                <h4>800V Architecture &amp; Predictive Cold Pre-Conditioning</h4>
                <p>
                  Eliminate cold-weather 60 kW charging drop-offs and match Chinese 800V/5C leaders (Zeekr, XPeng) by automating battery heating prior to arriving at any navigation-selected DC charger.
                </p>
              </div>
            </div>

            <div className={styles.backlogItem}>
              <div className={styles.backlogNum}>2</div>
              <div className={styles.backlogContent}>
                <h4>Physical Climate Quick-Keys &amp; Sub-Second Voice AI</h4>
                <p>
                  Restore physical haptic shortcut keys for defrost, seat heating, and temperature adjustment, complemented by local on-device voice execution to eliminate multi-layer touchscreen distraction.
                </p>
              </div>
            </div>

            <div className={styles.backlogItem}>
              <div className={styles.backlogNum}>3</div>
              <div className={styles.backlogContent}>
                <h4>UWB Extended Antenna Array &amp; Bluetooth Fallback Daemon</h4>
                <p>
                  Address Connected Ecosystem (-76.7% Net) by adding a dual-band local Bluetooth fallback protocol for the My BMW App so remote pre-climatization executes reliably in signal-deprived underground garages.
                </p>
              </div>
            </div>

            <div className={styles.backlogItem}>
              <div className={styles.backlogNum}>4</div>
              <div className={styles.backlogContent}>
                <h4>Electrochromic Smart Glass Roof &amp; Perforated Ventilated Veganza</h4>
                <p>
                  Resolve Smart Cabin summer heat complaints by introducing electrochromic tinting (eliminating the need for a mechanical roller blind) and standard perforated seat ventilation for vegan leather trims.
                </p>
              </div>
            </div>

            <div className={styles.backlogItem}>
              <div className={styles.backlogNum}>5</div>
              <div className={styles.backlogContent}>
                <h4>Ultrasonic + Camera Obstacle Sensor Fusion for Comfort Doors</h4>
                <p>
                  Recalibrate the i7 automatic door opening algorithm with multi-sensor fusion to prevent false obstacle stops in multi-story parking structures while maintaining tight obstacle safety buffers.
                </p>
              </div>
            </div>
          </div>
        </>
      ),
    },
    {
      id: "dream-bmw-car",
      category: "backlog",
      question: "Can we find the 'Dream BMW Car' that has the best baselines for everything?",
      content: (
        <>
          <p>
            When comparing the 53 BMW EV/PHEV models across range, battery capacity, fast charging, acceleration, towing, and customer satisfaction, data proves that <strong>no single production car holds the best baseline for everything</strong>:
          </p>
          <ul>
            <li><strong>Range &amp; Battery Leader:</strong> <code>iX xDrive50</code> (630 km WLTP, 105.2 kWh, 2,500 kg towing).</li>
            <li><strong>Acceleration &amp; Sports Dynamics Leader:</strong> <code>i4 M50 xDrive</code> (3.9s 0–100 km/h, 544 PS, 205 kW DC).</li>
            <li><strong>Digital Ergonomics &amp; ADAS Leader:</strong> <code>i5 M60 / eDrive40</code> (Level 2+ gaze-confirmed Highway Assistant, Interaction Bar).</li>
            <li><strong>Ultra-Luxury Acoustic Leader:</strong> <code>i7 xDrive60</code> (Bowers &amp; Wilkins Diamond 4D 1,615W, 31.3&quot; Theatre Screen).</li>
            <li><strong>Cargo &amp; Touring Versatility Leader:</strong> <code>i5 Touring</code> (570–1,700 L flat cargo deck, cW 0.23 aero).</li>
          </ul>
          <p>
            In automotive product management, the <strong>&quot;Dream BMW Car&quot;</strong> is therefore defined as the <strong>Pareto-Optimal Successor Blueprint</strong> (the target vehicle for 2028–2030):
          </p>
          <div style={{ background: "var(--fill)", padding: "16px 20px", borderRadius: "14px", border: "1px solid var(--sep)", margin: "14px 0" }}>
            <strong style={{ color: "var(--blue)" }}>The Synthesized Concept: BMW i5 M-Sport Touring 800V Hyper-GT</strong>
            <ul style={{ marginTop: "10px", marginBottom: "4px" }}>
              <li><strong>Pack &amp; Range:</strong> 105.2 kWh pack from the iX tuned to 650+ km WLTP in the aerodynamic Touring body.</li>
              <li><strong>Charging:</strong> 800V SiC architecture delivering 300 kW peak DC (10–80% in 18 minutes, resolving the -43.2% cold charging deficit).</li>
              <li><strong>Chassis:</strong> 2-axle air suspension + 3.2° rear-wheel steering from the i7 (preserving the +44.7% dynamics moat).</li>
              <li><strong>Controls:</strong> Haptic quick-keys for climate/defrost + local on-device Voice AI (resolving touchscreen distraction).</li>
              <li><strong>Connectivity:</strong> Dual-band UWB + local Bluetooth fallback daemon (resolving -76.7% underground garage app timeouts).</li>
              <li><strong>Materials:</strong> Electrochromic dimming glass roof + perforated ventilated Veganza (resolving cabin summer heat).</li>
            </ul>
          </div>
          <p>
            Detailed multi-criteria trade-off code and documentation are available in <code>docs/DREAM_CAR_SYNTHESIS.md</code>.
          </p>
        </>
      ),
    },

    // Integration
    {
      id: "integration-planner",
      category: "all",
      question: "How does the PM use the Planner with this pipeline?",
      content: (
        <>
          <p>
            The PM retains full decision sovereignty (Human-in-the-Loop):
          </p>
          <ul>
            <li><strong>Slider Weights:</strong> The PM adjusts the balance between historical sales volume impact, customer pain severity, and external market trends.</li>
            <li><strong>Audit Trail:</strong> Every recommendation links directly back to its source verbatim ID, study rating, or Chinese OEM benchmark.</li>
            <li><strong>Approval Workflow:</strong> The PM can approve, reject with justification, or challenge any AI-derived requirement before it enters the final Product Requirements Document (PRD).</li>
          </ul>
        </>
      ),
    },
    ...impactFaqs,
  ];

  // a tab's own questions first, then the general ones
  const filteredFaqs =
    filter === "all"
      ? faqs
      : [...faqs.filter((f) => f.category === filter), ...faqs.filter((f) => f.category === "all")];

  return (
    <ContentPage
      eyebrow="Methodology &amp; Pipeline Story"
      title="FAQ"
      lead="The engineering decisions, data cleaning pipelines, and sentiment analytics powering Open-Trend-Tracker."
    >
      <div className={styles.heroMeta}>
        <span className={styles.heroBadge}>BMW Group · Hackathon Methodology</span>
        <span><b>53</b> models inventoried</span>
        <span><b>3,971</b> verified EV cases</span>
        <span><b>7</b> MECE technology domains</span>
      </div>

      {/* Stats Banner */}
      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>Total Models</div>
          <div className={styles.statVal} style={{ color: "var(--blue)" }}>53</div>
          <div className={styles.statSub}>28 BEVs &amp; 25 PHEVs across entire BMW portfolio</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>Cleaned EV Cohort</div>
          <div className={styles.statVal} style={{ color: "var(--green)" }}>3,971</div>
          <div className={styles.statSub}>Verified cases (5,724 ICE combustion records excluded)</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>Brand Moat Domain</div>
          <div className={styles.statVal} style={{ color: "var(--green)" }}>+44.7%</div>
          <div className={styles.statSub}>Vehicle Dynamics Net Sentiment (9.95/10 satisfaction)</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>Critical Pain Point</div>
          <div className={styles.statVal} style={{ color: "var(--danger)" }}>-76.7%</div>
          <div className={styles.statSub}>Connected Ecosystem (remote app timeouts &amp; CarPlay)</div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className={styles.filterRow} role="tablist" aria-label="FAQ categories">
        <button
          type="button"
          className={`${styles.filterBtn} ${filter === "all" ? styles.active : ""}`}
          onClick={() => setFilter("all")}
        >
          All Questions ({faqs.length})
        </button>
        <button
          type="button"
          className={`${styles.filterBtn} ${filter === "catalog" ? styles.active : ""}`}
          onClick={() => setFilter("catalog")}
        >
          Phase 1: Catalog (53 Models)
        </button>
        <button
          type="button"
          className={`${styles.filterBtn} ${filter === "cleaning" ? styles.active : ""}`}
          onClick={() => setFilter("cleaning")}
        >
          Phase 2: Cleaning Funnel
        </button>
        <button
          type="button"
          className={`${styles.filterBtn} ${filter === "domains" ? styles.active : ""}`}
          onClick={() => setFilter("domains")}
        >
          Phase 3: 7 Tech Domains
        </button>
        <button
          type="button"
          className={`${styles.filterBtn} ${filter === "math" ? styles.active : ""}`}
          onClick={() => setFilter("math")}
        >
          Phase 4: Sentiment Math
        </button>
        <button
          type="button"
          className={`${styles.filterBtn} ${filter === "backlog" ? styles.active : ""}`}
          onClick={() => setFilter("backlog")}
        >
          Phase 5: Engineering Backlog
        </button>
        <button
          type="button"
          className={`${styles.filterBtn} ${filter === "impactData" ? styles.active : ""}`}
          onClick={() => setFilter("impactData")}
        >
          Impact 1: Data Collection
        </button>
        <button
          type="button"
          className={`${styles.filterBtn} ${filter === "impactMath" ? styles.active : ""}`}
          onClick={() => setFilter("impactMath")}
        >
          Impact 2: Analysis &amp; Calculation
        </button>
      </div>

      {/* Accordion FAQ List */}
      <div className={styles.accordionList}>
        {filteredFaqs.map((faq, index) => (
          <details key={faq.id} className={styles.detailsCard} open={index === 0 ? true : undefined}>
            <summary className={styles.summaryRow}>
              <span>{faq.question}</span>
              <svg
                className={styles.summaryIcon}
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </summary>
            <div className={styles.panelContent}>
              {faq.content}
            </div>
          </details>
        ))}
      </div>
    </ContentPage>
  );
}
