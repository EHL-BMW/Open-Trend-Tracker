import { useEffect, useRef, useState } from "react";
import { ContentPage } from "./ContentPage";
import styles from "./AgentPage.module.css";

interface AgentStatus {
  configured: boolean;
  model: string;
  provider: string;
  domains: string[];
  domain_options: { key: string; label: string }[];
}

interface BenchmarkCompany {
  id: string;
  name_zh: string;
  name_en: string;
  tagline: string;
  flagship_models: string[];
  core_moat: string;
}

interface TrendMarker {
  marker_id: string;
  company_id: string;
  company_zh: string;
  company_en: string;
  domain: string;
  domain_label: string;
  technology_name: string;
  key_specs: string;
  bmw_current_status: string;
  bmw_transfer_feasibility: "Critical" | "High" | "Medium";
  recommended_bmw_action: string;
  estimated_bom_impact: string;
  target_models: string[];
  tags: string[];
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  referenced_markers?: string[];
}

interface GapAnalysisOutput {
  analysis_id: string;
  target_vehicle: string;
  domain: string;
  domains?: string[];
  domain_label: string;
  generated_at: string;
  model_used: string;
  executive_summary: string;
  bmw_customer_pain_points: string[];
  citations: {
    source_type: string;
    citation_text: string;
    vehicle_or_outlet: string;
    severity_or_date: string;
  }[];
  competitor_benchmarks: {
    competitor_brand: string;
    competitor_model: string;
    feature_name: string;
    technical_specs: string;
    observed_market_advantage: string;
    source_citation: string;
  }[];
  gap_severity: "Critical" | "High" | "Medium";
  recommended_requirements: {
    requirement_id: string;
    title: string;
    system_domain: string;
    specification: string;
    target_metric: string;
    affected_bmw_taxonomy_attributes: string[];
    bom_cost_impact_eur: string;
    engineering_complexity: "Low" | "Medium" | "High" | "Critical";
    time_to_market_readiness: string;
    tradeoffs_and_risks: string;
  }[];
  pm_challenge_prompts: string[];
  review_status: "pending_review" | "approved" | "rejected" | "challenged";
  pm_notes?: string | null;
  reviewed_at?: string | null;
  system_fingerprint?: string | null;
  seed?: number | null;
}

export const MECE_DOMAINS = [
  { key: "energy_charging", label: "⚡ 1. Energy & Charging", aspect: "Charging experience, range management, power distribution" },
  { key: "driving_assistance", label: "🛡️ 2. Driving Assistance", aspect: "Highway pilot, automated parking, human-machine handoff" },
  { key: "digital_cockpit", label: "🖥️ 3. Digital Cockpit & AI", aspect: "BMW OS 8.5/9, voice assistant, display interaction" },
  { key: "connected_ecosystem", label: "📱 4. Connected Ecosystem", aspect: "My BMW App, Digital Key Plus (UWB), OTA, subterranean BLE" },
  { key: "smart_cabin", label: "🛋️ 5. Smart Cabin", aspect: "Thermal comfort, seating, acoustic insulation, materials" },
  { key: "vehicle_dynamics", label: "🏎️ 6. Vehicle Dynamics & Safety", aspect: "Chassis control, 2-axle air suspension, steering precision" },
  { key: "smart_exterior", label: "🚪 7. Smart Exterior", aspect: "Automatic comfort doors, kick-sensor tailgate, smart lighting" },
];

const QUICK_PROMPTS = [
  {
    label: "📱 Xiaomi HyperOS vs G60",
    text: "How should BMW 5 Series (G60) counter Xiaomi SU7's HyperOS phone-car integration and 1.49s boot time?",
  },
  {
    label: "⚡ Zeekr 5.5C Golden Battery vs BMW 800V",
    text: "Compare Zeekr's 800V 5.5C Golden Battery (10.5 min SoC) against BMW's 400V CLAR and Neue Klasse roadmap.",
  },
  {
    label: "📶 AITO MagLink & Garage BLE Link",
    text: "How does AITO MagLink and offline BLE caching solve BMW's -76.7% Connected Ecosystem underground garage timeouts?",
  },
  {
    label: "🚪 Zeekr MIX & AITO Doors vs i7 Comfort Doors",
    text: "BMW i7 automatic doors halt in tight parking spots (-18.1% sentiment). How do Zeekr MIX and AITO solve exterior door obstacles and kick tailgates?",
  },
  {
    label: "🧠 XPeng Turing AI vs Driving Assistant",
    text: "How does XPeng's Turing AI end-to-end map-free ADAS challenge BMW Level 2+ Highway Assistant in China?",
  },
  {
    label: "🛋️ Li Auto Lounge Seats & NIO 925V for i7",
    text: "Draft an engineering PRD for BMW i7 (G70) adopting Li Auto zero-gravity lounge seating and NIO 900V SiC architecture.",
  },
  {
    label: "🏎️ AITO DATS & Li Auto Magic Carpet Dynamics",
    text: "BMW holds a +44.7% Moat in Vehicle Dynamics. How should Neue Klasse counter AITO DATS (4ms torque loop) and Li Auto lidar bump preview?",
  },
  {
    label: "🔋 Ultra-Fast 5C LFP on Entry BMWs",
    text: "Evaluate adopting 800V 5C LFP batteries on entry BMW models (F70, iX1) to cut €1,400 BOM cost while beating Tesla in charging speed.",
  },
];

export function AgentPage() {
  const [activeTab, setActiveTab] = useState<"chat" | "database" | "gap_analysis">("chat");
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null);

  // Future Trend Markers DB state
  const [companies, setCompanies] = useState<BenchmarkCompany[]>([]);
  const [markers, setMarkers] = useState<TrendMarker[]>([]);
  const [selectedCompanyFilter, setSelectedCompanyFilter] = useState<string>("all");
  const [dbSearchQuery, setDbSearchQuery] = useState("");
  const [selectedDbDomains, setSelectedDbDomains] = useState<string[]>(["all"]);

  // Chat State
  const [chatVehicle, setChatVehicle] = useState("G60");
  const [chatCompany, setChatCompany] = useState("All");
  const [selectedChatDomains, setSelectedChatDomains] = useState<string[]>(["all"]);
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "### Welcome to the BMW R&D Strategic Cockpit\n\nI am your **Chief Competitive Strategist & Systems Architect**. I have full real-time access to our **Future Trend Markers Database** benchmarking China's top 6 EV pioneers across all **7 MECE Technology Domains** (Energy & Charging, Driving Assistance, Digital Cockpit & AI, Connected Ecosystem, Smart Cabin, Vehicle Dynamics & Safety, Smart Exterior):\n\n* **蔚来 (NIO)** — Full-Domain 925V & Power Swap Station 4.0\n* **问界 (AITO / Huawei)** — HarmonyOS MagLink & HUAWEI ADS 3.0 End-to-End\n* **小米 (Xiaomi)** — HyperOS Seamless Ecosystem & 27,200 rpm Motors\n* **理想 (Li Auto)** — Magic Carpet 3.0 Suspension & Zero-Gravity Living Room\n* **极氪 (Zeekr)** — 800V 5.5C Golden Battery (10.5 min SoC) & Snapdragon 8295\n* **小鹏 (XPeng)** — Turing AI World-Model ADAS & 11.8 kWh/100km Efficiency\n\nAsk me any strategic counter-measure, trade-off analysis, or PRD specification below.",
    },
  ]);
  const [chatLoading, setChatLoading] = useState(false);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Gap Analysis Generator State (supports 1 to 7 MECE domains)
  const [runs, setRuns] = useState<any[]>([]);
  const [activeAnalysis, setActiveAnalysis] = useState<GapAnalysisOutput | null>(null);
  const [gapLoading, setGapLoading] = useState(false);
  const [gapVehicle, setGapVehicle] = useState("G60");
  const [selectedGapDomains, setSelectedGapDomains] = useState<string[]>(["energy_charging"]);
  const [gapCompetitor, setGapCompetitor] = useState("All");
  const [customGapPrompt, setCustomGapPrompt] = useState("");
  const [pmNotes, setPmNotes] = useState("");
  const [reviewLoading, setReviewLoading] = useState(false);
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);

  // Initial data load
  useEffect(() => {
    fetch("/api/v1/agent/status")
      .then((r) => r.json())
      .then((data: AgentStatus) => setAgentStatus(data))
      .catch((err) => console.error("Failed to load agent status", err));

    loadTrendMarkers();
    loadRuns();
  }, []);

  useEffect(() => {
    if (activeTab === "chat") {
      chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatMessages, activeTab]);

  const loadTrendMarkers = async (company?: string, domainsList?: string[], q?: string) => {
    try {
      const params = new URLSearchParams();
      const targetCompany = company !== undefined ? company : selectedCompanyFilter;
      if (targetCompany && targetCompany !== "all") params.append("company", targetCompany);

      const targetDomains = domainsList !== undefined ? domainsList : selectedDbDomains;
      if (targetDomains && !targetDomains.includes("all") && targetDomains.length > 0) {
        targetDomains.forEach((d) => params.append("domains", d));
      }

      const query = q !== undefined ? q : dbSearchQuery;
      if (query && query.trim()) params.append("q", query.trim());

      const res = await fetch(`/api/v1/agent/trend-markers?${params.toString()}`);
      const data = await res.json();
      setCompanies(data.companies || []);
      setMarkers(data.items || []);
    } catch (err) {
      console.error("Failed to load trend markers", err);
    }
  };

  const loadRuns = async () => {
    try {
      const res = await fetch("/api/v1/agent/gap-analyses");
      const data = await res.json();
      if (data.items && data.items.length > 0) {
        setRuns(data.items);
        loadAnalysis(data.items[0].analysis_id);
      }
    } catch (err) {
      console.error("Failed to load gap analyses", err);
    }
  };

  const loadAnalysis = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/agent/gap-analyses/${encodeURIComponent(id)}`);
      const data: GapAnalysisOutput = await res.json();
      setActiveAnalysis(data);
      setPmNotes(data.pm_notes || "");
    } catch (err) {
      console.error("Failed to fetch analysis", err);
    }
  };

  const toggleGapDomain = (key: string) => {
    setSelectedGapDomains((prev) => {
      if (prev.includes(key)) {
        if (prev.length <= 1) return prev; // Keep at least 1 domain selected
        return prev.filter((d) => d !== key);
      } else {
        return [...prev, key];
      }
    });
  };

  const handleSelectAllGapDomains = () => {
    setSelectedGapDomains(MECE_DOMAINS.map((d) => d.key));
  };

  const handleResetGapDomains = () => {
    setSelectedGapDomains(["energy_charging"]);
  };

  const toggleChatDomain = (key: string) => {
    setSelectedChatDomains((prev) => {
      if (key === "all") return ["all"];
      const withoutAll = prev.filter((d) => d !== "all");
      if (withoutAll.includes(key)) {
        const remaining = withoutAll.filter((d) => d !== key);
        return remaining.length === 0 ? ["all"] : remaining;
      } else {
        return [...withoutAll, key];
      }
    });
  };

  const toggleDbDomain = (key: string) => {
    let next: string[];
    if (key === "all") {
      next = ["all"];
    } else {
      const withoutAll = selectedDbDomains.filter((d) => d !== "all");
      if (withoutAll.includes(key)) {
        const remaining = withoutAll.filter((d) => d !== key);
        next = remaining.length === 0 ? ["all"] : remaining;
      } else {
        next = [...withoutAll, key];
      }
    }
    setSelectedDbDomains(next);
    loadTrendMarkers(selectedCompanyFilter, next, dbSearchQuery);
  };

  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend || chatInput).trim();
    if (!text || chatLoading) return;

    const newMessages: ChatMessage[] = [...chatMessages, { role: "user", content: text }];
    setChatMessages(newMessages);
    setChatInput("");
    setChatLoading(true);

    try {
      const res = await fetch("/api/v1/agent/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: newMessages.map((m) => ({ role: m.role, content: m.content })),
          vehicle: chatVehicle,
          focus_company: chatCompany === "All" ? null : chatCompany,
          domains: selectedChatDomains.includes("all") ? null : selectedChatDomains,
        }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const reply = await res.json();
      setChatMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: reply.content,
          referenced_markers: reply.referenced_markers || [],
        },
      ]);
    } catch (err) {
      console.error("Chat failed", err);
      setChatMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Encountered a connection error while consulting the AI R&D engine. Please verify the backend status.",
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleAskMarkerInChat = (marker: TrendMarker) => {
    setActiveTab("chat");
    setChatVehicle(marker.target_models[0]?.split(" ")[0] || "G60");
    setChatCompany(marker.company_id);
    setSelectedChatDomains([marker.domain]);
    const prompt = `Explain how BMW should adopt "${marker.technology_name}" from ${marker.company_zh} (${marker.company_en}) for BMW ${marker.target_models.join(", ")}, including BOM impact (${marker.estimated_bom_impact}) and engineering risks.`;
    handleSendMessage(prompt);
  };

  const handleRunGapAnalysis = async () => {
    setGapLoading(true);
    setActionFeedback(null);
    try {
      const res = await fetch("/api/v1/agent/gap-analysis", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          vehicle: gapVehicle,
          domains: selectedGapDomains,
          focus_competitor: gapCompetitor === "All" ? null : gapCompetitor,
          custom_instruction: customGapPrompt.trim() || null,
        }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: GapAnalysisOutput = await res.json();
      setActiveAnalysis(data);
      setPmNotes("");
      setActionFeedback("Gap analysis successfully generated!");
      loadRuns();
    } catch (err) {
      console.error("Gap analysis failed", err);
      setActionFeedback("Analysis failed. Please check backend.");
    } finally {
      setGapLoading(false);
    }
  };

  const handleReviewDecision = async (status: "approved" | "rejected" | "challenged") => {
    if (!activeAnalysis) return;
    setReviewLoading(true);
    try {
      const res = await fetch(`/api/v1/agent/gap-analyses/${activeAnalysis.analysis_id}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          status,
          pm_notes: pmNotes.trim() || null,
        }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const updated: GapAnalysisOutput = await res.json();
      setActiveAnalysis(updated);
      setActionFeedback(`Review status updated: ${status.toUpperCase()}`);
      loadRuns();
    } catch (err) {
      console.error("Failed to update review", err);
      setActionFeedback("Failed to update decision.");
    } finally {
      setReviewLoading(false);
    }
  };

  return (
    <ContentPage
      eyebrow="Open-Trend-Tracker • AI Competitor Intelligence"
      title="AI Competitor Gap Agent"
      lead={
        <span>
          Benchmarking China's 6 Future EV Disruptors (<b>蔚来、问界、小米、理想、极氪、小鹏</b>) to formulate
          actionable BMW engineering PRDs and portfolio counter-strategies.
        </span>
      }
    >
      <div className={styles.pageWrap}>
        {/* Top Status & Cohort Bar */}
        <div className={styles.topStatusBar}>
          <div className={styles.statusPill}>
            <span className={`${styles.statusDot} ${agentStatus?.configured ? "" : styles.offline}`} />
            <span>
              <b>KI-Agent Engine:</b>{" "}
              {agentStatus?.configured ? `${agentStatus.provider} (${agentStatus.model})` : "Deterministic Mode"}
            </span>
          </div>

          <div className={styles.benchmarkSummaryPill}>
            <span>Benchmark Cohort: <b>蔚来 • 问界 • 小米 • 理想 • 极氪 • 小鹏</b></span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className={styles.tabNav}>
        <button
          className={`${styles.tabBtn} ${activeTab === "chat" ? styles.tabBtnActive : ""}`}
          onClick={() => setActiveTab("chat")}
        >
          <span>💬 AI R&D Chat</span>
        </button>

        <button
          className={`${styles.tabBtn} ${activeTab === "database" ? styles.tabBtnActive : ""}`}
          onClick={() => setActiveTab("database")}
        >
          <span>📊 Future Trend Markers DB</span>
          <span className={styles.tabCountBadge}>{markers.length}</span>
        </button>

        <button
          className={`${styles.tabBtn} ${activeTab === "gap_analysis" ? styles.tabBtnActive : ""}`}
          onClick={() => setActiveTab("gap_analysis")}
        >
          <span>📋 Deep Gap PRD & Review</span>
        </button>

      </nav>

      {/* ====================================================================
          TAB 1: AI R&D CHAT
          ==================================================================== */}
      {activeTab === "chat" && (
        <section className={styles.chatContainer}>
          {/* Header Controls */}
          <div className={styles.chatHeaderBar}>
            <div className={styles.chatConfigRow}>
              <span style={{ fontSize: "12.5px", fontWeight: 600, color: "var(--label-2)" }}>Target Vehicle:</span>
              <select
                className={styles.chatSelect}
                value={chatVehicle}
                onChange={(e) => setChatVehicle(e.target.value)}
              >
                <option value="G60">BMW 5 Series / i5 (G60)</option>
                <option value="G70">BMW 7 Series / i7 (G70)</option>
                <option value="F70">BMW 1 Series (F70)</option>
                <option value="G45">BMW X3 / iX3 (G45)</option>
              </select>

              <span style={{ fontSize: "12.5px", fontWeight: 600, color: "var(--label-2)", marginLeft: "8px" }}>
                Benchmark Focus:
              </span>
              <select
                className={styles.chatSelect}
                value={chatCompany}
                onChange={(e) => setChatCompany(e.target.value)}
              >
                <option value="All">All 6 Disruptors (蔚来、问界、小米、理想、极氪、小鹏)</option>
                <option value="nio">蔚来 (NIO)</option>
                <option value="aito">问界 (AITO / Huawei)</option>
                <option value="xiaomi">小米 (Xiaomi EV)</option>
                <option value="li_auto">理想 (Li Auto)</option>
                <option value="zeekr">极氪 (Zeekr)</option>
                <option value="xpeng">小鹏 (XPeng)</option>
              </select>
            </div>

            <button
              style={{
                background: "transparent",
                border: "none",
                color: "var(--label-2)",
                fontSize: "12px",
                cursor: "pointer",
                textDecoration: "underline",
              }}
              onClick={() =>
                setChatMessages([
                  {
                    role: "assistant",
                    content: "Conversation history reset. How can I assist your BMW R&D portfolio planning?",
                  },
                ])
              }
            >
              Reset Chat
            </button>
          </div>

          {/* Multi-Domain Focus Bar for Chat */}
          <div style={{ padding: "8px 20px", display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap", borderBottom: "1px solid color-mix(in srgb, var(--sep) 50%, transparent)", background: "color-mix(in srgb, var(--bg) 30%, transparent)" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--label-2)", whiteSpace: "nowrap" }}>
              Focus Domains ({selectedChatDomains.includes("all") ? "All 7" : `${selectedChatDomains.length} of 7`}):
            </span>
            <button
              type="button"
              className={`${styles.filterChip} ${selectedChatDomains.includes("all") ? styles.filterChipActive : ""}`}
              onClick={() => toggleChatDomain("all")}
            >
              All 7 Domains
            </button>
            {MECE_DOMAINS.map((dom) => {
              const isActive = selectedChatDomains.includes(dom.key);
              return (
                <button
                  key={dom.key}
                  type="button"
                  className={`${styles.filterChip} ${isActive ? styles.filterChipActive : ""}`}
                  onClick={() => toggleChatDomain(dom.key)}
                  title={dom.aspect}
                >
                  {dom.label}
                </button>
              );
            })}
          </div>

          {/* Quick Prompt Chips */}
          <div className={styles.chatQuickChips}>
            {QUICK_PROMPTS.map((chip, idx) => (
              <button
                key={idx}
                className={styles.quickChip}
                onClick={() => handleSendMessage(chip.text)}
                disabled={chatLoading}
              >
                {chip.label}
              </button>
            ))}
          </div>

          {/* Chat Message Stream */}
          <div className={styles.chatStream}>
            {chatMessages.map((msg, idx) => (
              <div
                key={idx}
                className={`${styles.messageRow} ${msg.role === "user" ? styles.userRow : styles.aiRow}`}
              >
                <div className={`${styles.avatarPill} ${msg.role === "user" ? styles.avatarUser : styles.avatarAi}`}>
                  {msg.role === "user" ? "PM" : "BMW"}
                </div>
                <div className={`${styles.messageBubble} ${msg.role === "user" ? styles.bubbleUser : styles.bubbleAi}`}>
                  <div style={{ whiteSpace: "pre-wrap" }}>{msg.content}</div>

                  {msg.referenced_markers && msg.referenced_markers.length > 0 && (
                    <div className={styles.chatMarkersRef}>
                      <span>Referenced Trend Markers:</span>
                      {msg.referenced_markers.map((mid) => (
                        <span key={mid} className={styles.chatMarkerBadge}>
                          🏷️ {mid}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {chatLoading && (
              <div className={`${styles.messageRow} ${styles.aiRow}`}>
                <div className={`${styles.avatarPill} ${styles.avatarAi}`}>BMW</div>
                <div className={`${styles.messageBubble} ${styles.bubbleAi}`}>
                  <span style={{ color: "var(--label-2)" }}>Synthesizing strategy against China benchmark DB...</span>
                </div>
              </div>
            )}
            <div ref={chatBottomRef} />
          </div>

          {/* Chat Input Bar */}
          <div className={styles.chatInputStation}>
            <textarea
              className={styles.chatTextarea}
              placeholder="Ask how BMW should counter 蔚来、问界、小米、理想、极氪、小鹏 or request PRD drafting..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              rows={2}
            />
            <button
              className={styles.sendBtn}
              onClick={() => handleSendMessage()}
              disabled={chatLoading || !chatInput.trim()}
            >
              Send
            </button>
          </div>
        </section>
      )}

      {/* ====================================================================
          TAB 2: FUTURE TREND MARKERS DATABASE EXPLORER
          ==================================================================== */}
      {activeTab === "database" && (
        <section className={styles.dbContainer}>
          {/* Company Cards Banner */}
          <div className={styles.companyGrid}>
            <div
              className={`${styles.companyCard} ${selectedCompanyFilter === "all" ? styles.companyCardActive : ""}`}
              onClick={() => {
                setSelectedCompanyFilter("all");
                loadTrendMarkers("all", selectedDbDomains, dbSearchQuery);
              }}
            >
              <div className={styles.companyHeader}>
                <span className={styles.companyNameZh}>全部标杆</span>
                <span className={styles.companyNameEn}>All 6 Disruptors</span>
              </div>
              <div className={styles.companyMoat}>Complete technology baseline dataset across all vehicle systems.</div>
              <div className={styles.companyModels}>{markers.length} Trend Markers</div>
            </div>

            {companies.map((comp) => (
              <div
                key={comp.id}
                className={`${styles.companyCard} ${selectedCompanyFilter === comp.id ? styles.companyCardActive : ""}`}
                onClick={() => {
                  const newFilter = selectedCompanyFilter === comp.id ? "all" : comp.id;
                  setSelectedCompanyFilter(newFilter);
                  loadTrendMarkers(newFilter, selectedDbDomains, dbSearchQuery);
                }}
              >
                <div className={styles.companyHeader}>
                  <span className={styles.companyNameZh}>{comp.name_zh}</span>
                  <span className={styles.companyNameEn}>{comp.name_en}</span>
                </div>
                <div className={styles.companyMoat}>{comp.core_moat}</div>
                <div className={styles.companyModels}>Models: {comp.flagship_models.slice(0, 3).join(", ")}</div>
              </div>
            ))}
          </div>

          {/* Search Bar */}
          <div className={styles.dbFilterBar}>
            <input
              type="text"
              className={styles.dbSearchInput}
              placeholder="Search trend markers (e.g. 800V SiC, HyperOS, Golden Battery, MagLink, LFP, LiDAR)..."
              value={dbSearchQuery}
              onChange={(e) => {
                setDbSearchQuery(e.target.value);
                loadTrendMarkers(selectedCompanyFilter, selectedDbDomains, e.target.value);
              }}
            />
          </div>

          {/* Multi-Domain Filter Chips for Database */}
          <div className={styles.multiDomainChipBar}>
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--label-2)", marginRight: "4px" }}>
              Filter by Domain ({selectedDbDomains.includes("all") ? "All 7" : `${selectedDbDomains.length} of 7`}):
            </span>
            <button
              type="button"
              className={`${styles.filterChip} ${selectedDbDomains.includes("all") ? styles.filterChipActive : ""}`}
              onClick={() => toggleDbDomain("all")}
            >
              All 7 Domains ({markers.length})
            </button>
            {MECE_DOMAINS.map((dom) => {
              const isActive = selectedDbDomains.includes(dom.key);
              return (
                <button
                  key={dom.key}
                  type="button"
                  className={`${styles.filterChip} ${isActive ? styles.filterChipActive : ""}`}
                  onClick={() => toggleDbDomain(dom.key)}
                  title={dom.aspect}
                >
                  {dom.label}
                </button>
              );
            })}
          </div>

          {/* Marker Cards Grid */}
          <div className={styles.markerGrid}>
            {markers.map((marker) => (
              <div key={marker.marker_id} className={styles.markerCard}>
                <div className={styles.markerTop}>
                  <div>
                    <span className={styles.markerId}>{marker.marker_id} • {marker.domain_label}</span>
                    <h3 className={styles.markerTitle}>{marker.technology_name}</h3>
                  </div>
                  <span className={styles.companyTag}>
                    {marker.company_zh} ({marker.company_en})
                  </span>
                </div>

                <div className={styles.markerSpecs}>
                  <b>Benchmark Specs:</b> {marker.key_specs}
                </div>

                <div className={styles.markerBmwStatus}>
                  <b>Current BMW Baseline:</b> {marker.bmw_current_status}
                </div>

                <div className={styles.markerActionBox}>
                  <span className={styles.actionHeading}>Recommended BMW R&D Action</span>
                  <div className={styles.actionDesc}>{marker.recommended_bmw_action}</div>
                </div>

                <div className={styles.markerFooter}>
                  <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                    <span
                      className={`${styles.bomBadge} ${
                        marker.estimated_bom_impact.includes("-") ? styles.bomCostDown : styles.bomCostUp
                      }`}
                    >
                      BOM: {marker.estimated_bom_impact}
                    </span>
                    <span style={{ fontSize: "11.5px", color: "var(--label-2)" }}>
                      Feasibility: <b>{marker.bmw_transfer_feasibility}</b>
                    </span>
                  </div>

                  <button
                    className={styles.askMarkerBtn}
                    onClick={() => handleAskMarkerInChat(marker)}
                  >
                    💬 Discuss in Chat →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* ====================================================================
          TAB 3: DEEP GAP PRD & REVIEW
          ==================================================================== */}
      {activeTab === "gap_analysis" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          {/* Stepper Card */}
          <section className={styles.flowchartCard}>
            <div className={styles.flowchartHeader}>
              <span>Strategic Agent Architecture Flow</span>
              <span>Traceability: VoC ➔ Intelligence ➔ PRD</span>
            </div>
            <div className={styles.flowSteps}>
              <div className={styles.flowStep}>
                <span className={styles.stepNum}>Step 1</span>
                <div className={styles.stepTitle}>BMW Customer Voice</div>
                <div className={styles.stepDesc}>Internal feedback datasets (G60, G70, F70).</div>
              </div>
              <div className={styles.flowStep}>
                <span className={styles.stepNum}>Step 2</span>
                <div className={styles.stepTitle}>KI-Agent Reasoning</div>
                <div className={styles.stepDesc}>OpenAI GPT-4o-mini structured analysis.</div>
              </div>
              <div className={styles.flowStep}>
                <span className={styles.stepNum}>Step 3</span>
                <div className={styles.stepTitle}>China 6 Benchmarks</div>
                <div className={styles.stepDesc}>蔚来、问界、小米、理想、极氪、小鹏.</div>
              </div>
              <div className={styles.flowStep}>
                <span className={styles.stepNum}>Step 4</span>
                <div className={styles.stepTitle}>Gap Severity & PRD</div>
                <div className={styles.stepDesc}>BOM cost deltas, target pass metrics, SOP quarter.</div>
              </div>
              <div className={styles.flowStep}>
                <span className={styles.stepNum}>Step 5</span>
                <div className={styles.stepTitle}>PM Sign-off</div>
                <div className={styles.stepDesc}>Human-in-the-loop Approve, Challenge, or Reject.</div>
              </div>
            </div>
          </section>

          {/* Trigger Station */}
          <section className={styles.controlStation}>
            <div className={styles.controlGrid}>
              <div className={styles.controlField}>
                <label className={styles.controlLabel} htmlFor="gap-vehicle-select">Target BMW Vehicle</label>
                <select
                  id="gap-vehicle-select"
                  className={styles.selectInput}
                  value={gapVehicle}
                  onChange={(e) => setGapVehicle(e.target.value)}
                >
                  <option value="G60">BMW 5 Series / i5 (G60)</option>
                  <option value="G70">BMW 7 Series / i7 (G70)</option>
                  <option value="F70">BMW 1 Series (F70)</option>
                  <option value="G45">BMW X3 / iX3 (G45)</option>
                </select>
              </div>

              <div className={styles.controlField}>
                <label className={styles.controlLabel} htmlFor="gap-competitor-select">Competitor Focus</label>
                <select
                  id="gap-competitor-select"
                  className={styles.selectInput}
                  value={gapCompetitor}
                  onChange={(e) => setGapCompetitor(e.target.value)}
                >
                  <option value="All">All 6 Disruptors (蔚来、问界、小米、理想、极氪、小鹏)</option>
                  <option value="Xiaomi">小米 (Xiaomi SU7)</option>
                  <option value="Zeekr">极氪 (Zeekr 001/007)</option>
                  <option value="Nio">蔚来 (NIO 900V/Swap)</option>
                  <option value="AITO">问界 (AITO / Huawei)</option>
                  <option value="Li Auto">理想 (Li Auto MEGA/L9)</option>
                  <option value="XPeng">小鹏 (XPeng Turing AI)</option>
                </select>
              </div>

              <div className={styles.controlField}>
                <label className={styles.controlLabel} htmlFor="gap-custom-instruction">Custom PM Guidance</label>
                <input
                  id="gap-custom-instruction"
                  type="text"
                  className={styles.textInput}
                  placeholder="e.g. Focus on BOM under €700 and Q3 2026 SOP"
                  value={customGapPrompt}
                  onChange={(e) => setCustomGapPrompt(e.target.value)}
                />
              </div>

              {/* Multi-Domain Interactive Selector (Select 1-7 Domains) */}
              <div className={styles.domainSelectorBlock}>
                <div className={styles.domainSelectorHeader}>
                  <div>
                    <label className={styles.controlLabel}>
                      Focus Engineering Domains (Select 1 to 7 MECE Domains)
                    </label>
                    <div className={styles.domainSelectorSub}>
                      Active Selection: <b>{selectedGapDomains.length} of 7</b> domains
                      {selectedGapDomains.length === 7 ? " — Full 360° Systems Architecture" : selectedGapDomains.length > 1 ? " — Multi-Domain Synergies & Trade-offs" : " — Focused Domain Deep-Dive"}
                    </div>
                  </div>
                  <div className={styles.domainActionGroup}>
                    <button
                      type="button"
                      className={styles.domainQuickBtn}
                      onClick={handleSelectAllGapDomains}
                    >
                      ✓ Select All (7)
                    </button>
                    <button
                      type="button"
                      className={styles.domainQuickBtn}
                      onClick={handleResetGapDomains}
                    >
                      Reset (1)
                    </button>
                  </div>
                </div>

                <div className={styles.domainPillGrid}>
                  {MECE_DOMAINS.map((dom) => {
                    const isSelected = selectedGapDomains.includes(dom.key);
                    return (
                      <button
                        key={dom.key}
                        type="button"
                        className={`${styles.domainPill} ${isSelected ? styles.domainPillActive : ""}`}
                        onClick={() => toggleGapDomain(dom.key)}
                        title={dom.aspect}
                      >
                        <span className={styles.domainPillCheck}>
                          {isSelected ? "✓" : "+"}
                        </span>
                        <span className={styles.domainPillLabel}>{dom.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            <div className={styles.actionRow}>
              <button
                className={styles.primaryBtn}
                onClick={handleRunGapAnalysis}
                disabled={gapLoading}
              >
                {gapLoading ? "Synthesizing with KI-Agent..." : `Run AI Gap Analysis (${selectedGapDomains.length} Domain${selectedGapDomains.length > 1 ? "s" : ""})`}
              </button>

              {actionFeedback && (
                <span style={{ fontSize: "13px", color: actionFeedback.includes("failed") ? "var(--red)" : "var(--green)" }}>
                  {actionFeedback}
                </span>
              )}
            </div>
          </section>

          {/* History Pills */}
          {runs.length > 0 && (
            <div className={styles.historyBar}>
              <span className={styles.historyLabel}>Previous Analyses:</span>
              {runs.map((r) => (
                <button
                  key={r.analysis_id}
                  className={`${styles.historyPill} ${activeAnalysis?.analysis_id === r.analysis_id ? styles.activePill : ""}`}
                  onClick={() => loadAnalysis(r.analysis_id)}
                >
                  <span>{r.target_vehicle} • {r.domain_label?.includes("+") ? `${r.domain_label.split("+").length} Domains` : r.domain_label?.split(" ")[0]}</span>
                  <span style={{
                    color: r.review_status === "approved" ? "var(--green)" : r.review_status === "challenged" ? "var(--amber)" : "var(--label-2)",
                    fontSize: "11px",
                  }}>
                    [{r.review_status}]
                  </span>
                </button>
              ))}
            </div>
          )}

          {/* Active Run Card */}
          {activeAnalysis && (
            <section className={styles.analysisCard}>
              <div className={styles.summaryHeader}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
                    <span className={`${styles.severityBadge} ${
                      activeAnalysis.gap_severity === "Critical"
                        ? styles.sevCritical
                        : activeAnalysis.gap_severity === "High"
                        ? styles.sevHigh
                        : styles.sevMedium
                    }`}>
                      ● {activeAnalysis.gap_severity} Gap
                    </span>
                    <span className={`${styles.reviewBadge} ${
                      activeAnalysis.review_status === "approved"
                        ? styles.statusApproved
                        : activeAnalysis.review_status === "rejected"
                        ? styles.statusRejected
                        : activeAnalysis.review_status === "challenged"
                        ? styles.statusChallenged
                        : styles.statusPending
                    }`}>
                      Status: {activeAnalysis.review_status.replace("_", " ")}
                    </span>
                  </div>
                  <h2 style={{ fontSize: "20px", fontWeight: "700", color: "var(--label)", margin: 0 }}>
                    BMW {activeAnalysis.target_vehicle} ➔ {activeAnalysis.domain_label}
                  </h2>
                </div>
                <div style={{ fontSize: "12px", color: "var(--label-2)", textAlign: "right" }}>
                  ID: <code>{activeAnalysis.analysis_id}</code><br />
                  <span>Audit Fingerprint: <code>seed={activeAnalysis.seed ?? 42}</code> {activeAnalysis.system_fingerprint ? `• ${activeAnalysis.system_fingerprint}` : ""}</span><br />
                  Generated: {new Date(activeAnalysis.generated_at).toLocaleString()}
                </div>
              </div>

              <div className={styles.execSummaryText}>
                <b>Executive Briefing:</b> {activeAnalysis.executive_summary}
              </div>

              {/* Evidence Grid */}
              <div className={styles.evidenceGrid}>
                <div className={styles.evidenceSection}>
                  <div className={styles.sectionTitle}>Cited BMW Customer Pain Points (VoC)</div>
                  <div className={styles.quoteList}>
                    {activeAnalysis.bmw_customer_pain_points.slice(0, 3).map((text, idx) => (
                      <div key={idx} className={styles.quoteItem}>
                        "{text}"
                      </div>
                    ))}
                  </div>
                </div>

                <div className={styles.evidenceSection}>
                  <div className={styles.sectionTitle}>Chinese Competitor Benchmarks</div>
                  <div className={styles.quoteList}>
                    {activeAnalysis.competitor_benchmarks.map((bench, idx) => (
                      <div key={idx} className={styles.benchmarkCard}>
                        <div className={styles.benchmarkTop}>
                          <span className={styles.compBrand}>{bench.competitor_brand} {bench.competitor_model}</span>
                        </div>
                        <div className={styles.compSpecs}><b>Specs:</b> {bench.technical_specs}</div>
                        <div className={styles.compAdvantage}><b>Market Delta:</b> {bench.observed_market_advantage}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* PRD Requirements */}
              <div className={styles.requirementsSection}>
                <div className={styles.sectionTitle} style={{ fontSize: "16px" }}>
                  Derived Actionable Engineering Requirements (PRD)
                </div>

                {activeAnalysis.recommended_requirements.map((req) => (
                  <div key={req.requirement_id} className={styles.prdCard}>
                    <div className={styles.prdHeader}>
                      <div className={styles.prdTitleArea}>
                        <span className={styles.prdId}>{req.requirement_id} • {req.system_domain}</span>
                        <span className={styles.prdTitle}>{req.title}</span>
                      </div>
                      <span className={styles.prdBomBadge}>BOM Impact: {req.bom_cost_impact_eur}</span>
                    </div>

                    <div className={styles.prdSpec}><b>Specification:</b> {req.specification}</div>
                    <div className={styles.metricBox}><b>Target Metric:</b> {req.target_metric}</div>
                    <div className={styles.prdMetaRow}>
                      <div><b>Affected Taxonomy:</b> {req.affected_bmw_taxonomy_attributes.join(", ")}</div>
                      <div><b>Timeline:</b> {req.time_to_market_readiness}</div>
                    </div>
                  </div>
                ))}
              </div>

              {/* PM Challenge Prompts */}
              <div className={styles.challengeSection}>
                <div className={styles.challengeTitle}>Product Manager Challenge Prompts</div>
                <ul className={styles.challengeList}>
                  {activeAnalysis.pm_challenge_prompts.map((q, idx) => (
                    <li key={idx}><b>Q{idx + 1}:</b> {q}</li>
                  ))}
                </ul>
              </div>

              {/* Review Station */}
              <div className={styles.reviewStation}>
                <div className={styles.reviewHeader}>
                  <div className={styles.reviewTitle}>Human-in-the-Loop Decision Station</div>
                  <div style={{ fontSize: "12px", color: "var(--label-2)" }}>
                    {activeAnalysis.reviewed_at
                      ? `Last reviewed: ${new Date(activeAnalysis.reviewed_at).toLocaleString()}`
                      : "Awaiting Product Manager sign-off"}
                  </div>
                </div>

                <textarea
                  className={styles.notesArea}
                  placeholder="Add Product Manager engineering review feedback, budget caveats, or technical objections..."
                  value={pmNotes}
                  onChange={(e) => setPmNotes(e.target.value)}
                />

                <div className={styles.reviewActions}>
                  <button
                    className={styles.btnApprove}
                    disabled={reviewLoading}
                    onClick={() => handleReviewDecision("approved")}
                  >
                    ✓ Approve PRD for SOP
                  </button>

                  <button
                    className={styles.btnChallenge}
                    disabled={reviewLoading}
                    onClick={() => handleReviewDecision("challenged")}
                  >
                    ⚡ Challenge & Request Revisions
                  </button>

                  <button
                    className={styles.btnReject}
                    disabled={reviewLoading}
                    onClick={() => handleReviewDecision("rejected")}
                  >
                    ✕ Reject Proposal
                  </button>
                </div>
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  </ContentPage>
);
}


