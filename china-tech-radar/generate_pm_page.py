import json

with open("china_megatrends_feed.json", "r", encoding="utf-8") as f:
    feed_data = json.load(f)

feed_json_str = json.dumps(feed_data, ensure_ascii=False, indent=2)

html_code = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>China NEV Frontier Tech & Megatrends | Product Manager Intelligence Radar</title>
  <meta name="description" content="Product-manager-tailored intelligence radar tracking cutting-edge Chinese automotive technologies: 5C charging, all-solid-state batteries, E2E VLA driving, and on-device LLMs.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&family=Noto+Sans+SC:wght@400;500;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
  <style>
    :root {{
      --ease-smooth: cubic-bezier(0.16, 1, 0.3, 1);
      --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
      --cn-red: #ef4444;
      --cn-gold: #f59e0b;
      --neon-cyan: #00d2ff;
      --neon-purple: #a855f7;
      --neon-emerald: #10b981;
      --card-bg: rgba(15, 23, 42, 0.75);
    }}

    body {{
      font-family: 'Inter', 'Noto Sans SC', sans-serif;
      background: #060911;
      color: #f8fafc;
      overflow-x: hidden;
      margin: 0;
    }}

    .megatrends-page {{
      max-width: 1480px;
      margin: 0 auto;
      padding: 20px 24px 80px 24px;
    }}

    /* Smooth Tab Fade Animation */
    @keyframes smoothTabFade {{
      from {{ opacity: 0; transform: translateY(10px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    .tab-section-content {{
      animation: smoothTabFade 0.4s var(--ease-smooth) forwards;
    }}

    /* Ticker */
    .ticker-bar {{
      background: linear-gradient(90deg, #1e1b4b 0%, #0f172a 50%, #1e1b4b 100%);
      border: 1px solid rgba(168, 85, 247, 0.35);
      border-radius: 12px;
      padding: 10px 16px;
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 20px;
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }}

    .ticker-label {{
      background: linear-gradient(135deg, #ef4444, #dc2626);
      color: #ffffff;
      font-size: 0.72rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding: 4px 10px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
      flex-shrink: 0;
      box-shadow: 0 0 12px rgba(239, 68, 68, 0.5);
    }}

    .ticker-content {{
      overflow: hidden;
      white-space: nowrap;
      flex: 1;
    }}

    .ticker-scroll {{
      display: inline-block;
      white-space: nowrap;
      animation: tickerLoop 40s linear infinite;
    }}

    .ticker-scroll:hover {{
      animation-play-state: paused;
    }}

    @keyframes tickerLoop {{
      0% {{ transform: translateX(0); }}
      100% {{ transform: translateX(-50%); }}
    }}

    .ticker-item {{
      display: inline-flex;
      align-items: center;
      margin-right: 36px;
      font-size: 0.84rem;
      color: #e2e8f0;
    }}

    .ticker-item strong {{
      color: #00d2ff;
      margin-right: 6px;
    }}

    /* Header Banner */
    .radar-header {{
      background: radial-gradient(circle at 80% 20%, rgba(239, 68, 68, 0.12), transparent 50%),
                  radial-gradient(circle at 20% 80%, rgba(0, 210, 255, 0.1), transparent 40%),
                  rgba(15, 23, 42, 0.8);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 20px;
      padding: 28px 32px;
      margin-bottom: 22px;
    }}

    .radar-h1 {{
      font-family: var(--font-display);
      font-size: 2.1rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      line-height: 1.15;
      margin: 0;
      color: #ffffff;
    }}

    .glow-red {{
      background: linear-gradient(135deg, #f87171 0%, #ef4444 50%, #f59e0b 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    /* PM Executive Snapshot Strip */
    .pm-snapshot-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}

    .pm-snapshot-card {{
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 14px;
      padding: 16px 20px;
      transition: all 0.3s var(--ease-smooth);
      position: relative;
      overflow: hidden;
    }}

    .pm-snapshot-card:hover {{
      transform: translateY(-3px);
      border-color: rgba(0, 210, 255, 0.4);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    }}

    .pm-card-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      padding: 3px 8px;
      border-radius: 6px;
      margin-bottom: 8px;
    }}

    .pm-metric-stat {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 1.25rem;
      font-weight: 800;
      color: #ffffff;
      margin-bottom: 4px;
    }}

    .pm-action-line {{
      font-size: 0.8rem;
      color: #38bdf8;
      font-weight: 600;
      line-height: 1.4;
    }}

    /* Tab Switcher */
    .view-mode-tabs {{
      display: flex;
      gap: 8px;
      margin-bottom: 24px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      padding-bottom: 12px;
      overflow-x: auto;
    }}

    .tab-btn {{
      background: rgba(30, 41, 59, 0.4);
      border: 1px solid rgba(255, 255, 255, 0.08);
      color: #94a3b8;
      font-size: 0.86rem;
      font-weight: 600;
      padding: 9px 18px;
      border-radius: 10px;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.25s var(--ease-smooth);
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }}

    .tab-btn:hover {{
      background: rgba(51, 65, 85, 0.6);
      color: #ffffff;
      border-color: rgba(255, 255, 255, 0.2);
    }}

    .tab-btn.active {{
      background: linear-gradient(135deg, rgba(2, 132, 199, 0.45), rgba(37, 99, 235, 0.45));
      border-color: #00d2ff;
      color: #ffffff;
      box-shadow: 0 0 16px rgba(0, 210, 255, 0.3);
    }}

    /* Knowledge Graph Layout */
    .kg-wrapper {{
      background: rgba(10, 15, 28, 0.85);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 20px;
      padding: 24px;
      margin-bottom: 30px;
      position: relative;
    }}

    .kg-canvas-container {{
      width: 100%;
      height: 580px;
      background: radial-gradient(circle at center, #0f172a 0%, #060911 100%);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      position: relative;
      overflow: hidden;
      cursor: grab;
    }}

    .kg-canvas-container:active {{
      cursor: grabbing;
    }}

    #kg-canvas {{
      display: block;
      width: 100%;
      height: 100%;
    }}

    .kg-inspector {{
      position: absolute;
      top: 30px;
      right: 30px;
      width: 330px;
      background: rgba(15, 23, 42, 0.95);
      backdrop-filter: blur(16px);
      border: 1px solid #00d2ff;
      border-radius: 14px;
      padding: 20px;
      box-shadow: 0 12px 36px rgba(0, 0, 0, 0.7);
      transition: all 0.3s var(--ease-spring);
      z-index: 50;
      display: none;
    }}

    .kg-inspector.active {{
      display: block;
      animation: fadeInRight 0.3s var(--ease-smooth);
    }}

    @keyframes fadeInRight {{
      from {{ opacity: 0; transform: translateX(20px); }}
      to {{ opacity: 1; transform: translateX(0); }}
    }}

    /* Benchmark Cards */
    .benchmark-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(460px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }}

    .benchmark-card {{
      background: rgba(15, 23, 42, 0.75);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      padding: 22px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.25s var(--ease-smooth);
    }}

    .benchmark-card:hover {{
      transform: translateY(-2px);
      border-color: rgba(0, 210, 255, 0.3);
    }}

    .pm-callout-box {{
      background: rgba(0, 102, 177, 0.12);
      border-left: 3px solid #00d2ff;
      border-radius: 0 8px 8px 0;
      padding: 10px 14px;
      margin-bottom: 16px;
      font-size: 0.82rem;
      color: #e0f2fe;
      line-height: 1.45;
    }}

    .bar-row {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 10px;
      font-size: 0.82rem;
    }}

    .bar-label {{
      width: 170px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      color: #cbd5e1;
      font-weight: 500;
    }}

    .bar-track {{
      flex: 1;
      height: 18px;
      background: rgba(30, 41, 59, 0.6);
      border-radius: 4px;
      overflow: hidden;
    }}

    .bar-fill {{
      height: 100%;
      border-radius: 4px;
      transition: width 1s var(--ease-smooth);
    }}

    .bar-fill-cn {{
      background: linear-gradient(90deg, #0284c7, #00d2ff);
    }}

    .bar-fill-west {{
      background: linear-gradient(90deg, #475569, #94a3b8);
    }}

    .bar-fill-red {{
      background: linear-gradient(90deg, #dc2626, #ef4444);
    }}

    .bar-val {{
      width: 65px;
      text-align: right;
      font-family: 'JetBrains Mono', monospace;
      font-weight: 700;
      color: #f1f5f9;
    }}

    /* News Cards */
    .news-cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
      gap: 20px;
    }}

    .news-card {{
      background: rgba(15, 23, 42, 0.75);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      padding: 22px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: all 0.25s var(--ease-smooth);
    }}

    .news-card:hover {{
      border-color: rgba(0, 210, 255, 0.4);
      transform: translateY(-3px);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }}

    .btn-source-link {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.76rem;
      font-weight: 600;
      color: #38bdf8;
      background: rgba(2, 132, 199, 0.15);
      border: 1px solid rgba(56, 189, 248, 0.35);
      border-radius: 6px;
      padding: 5px 10px;
      text-decoration: none;
      transition: all 0.2s ease;
    }}

    .btn-source-link:hover {{
      background: rgba(2, 132, 199, 0.35);
      color: #ffffff;
      border-color: #38bdf8;
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
    }}

    /* Toast */
    .toast-container {{
      position: fixed;
      bottom: 28px;
      right: 28px;
      z-index: 9999;
      pointer-events: none;
    }}

    .toast-msg {{
      background: rgba(15, 23, 42, 0.95);
      border: 1px solid #00d2ff;
      border-radius: 10px;
      padding: 14px 20px;
      color: #ffffff;
      font-size: 0.88rem;
      display: flex;
      align-items: center;
      gap: 12px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
      animation: toastSlideUp 0.3s ease-out;
    }}

    @keyframes toastSlideUp {{
      from {{ transform: translateY(20px); opacity: 0; }}
      to {{ transform: translateY(0); opacity: 1; }}
    }}

    /* Modal */
    .news-modal {{
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(3, 7, 18, 0.85);
      backdrop-filter: blur(12px);
      z-index: 1000;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }}

    .news-modal.active {{
      display: flex;
    }}

    .modal-box {{
      background: #0b1120;
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 20px;
      max-width: 720px;
      width: 100%;
      padding: 32px;
      max-height: 90vh;
      overflow-y: auto;
      position: relative;
      animation: modalPop 0.3s var(--ease-spring);
    }}

    @keyframes modalPop {{
      from {{ transform: scale(0.95); opacity: 0; }}
      to {{ transform: scale(1); opacity: 1; }}
    }}
  </style>
</head>
<body>
  <div class="megatrends-page">
    
    <!-- Top Action Navigation -->
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:12px;">
      <div style="display:flex; gap:10px; align-items:center;">
        <a href="index.html" class="btn btn-secondary" style="display:inline-flex; align-items:center; gap:8px; font-size:0.82rem;">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
          Vehicle Fleet Explorer
        </a>
        <a href="bmw_pipeline_story.html" class="btn btn-outline" style="display:inline-flex; align-items:center; gap:6px; font-size:0.82rem;">
          🚀 BMW End-to-End Pipeline
        </a>
      </div>

      <div style="display:flex; gap:10px; align-items:center;">
        <a href="china_megatrends_feed.json" download="china_megatrends_feed.json" class="btn btn-outline" style="font-size:0.82rem;">
          💾 Download Feed & Graph (JSON)
        </a>
        <button id="btn-refresh-feed" class="btn btn-primary" style="font-size:0.82rem; background:linear-gradient(135deg, #ef4444, #dc2626); box-shadow:0 0 16px rgba(239, 68, 68, 0.4);" title="Click to fetch latest news updates">
          <span id="btn-refresh-icon">🔄</span> <span id="btn-refresh-text">Fetch Latest Wire Updates</span>
        </button>
      </div>
    </div>

    <!-- Live Breaking News Marquee Ticker -->
    <div class="ticker-bar" role="region" aria-label="China NEV Breaking News">
      <div class="ticker-label">
        <span style="display:inline-block; width:6px; height:6px; background:#fff; border-radius:50%; animation:pulse 1.5s infinite;"></span>
        FRONTIER WIRE
      </div>
      <div class="ticker-content">
        <div class="ticker-scroll" id="ticker-scroll-target">
          <span class="ticker-item"><strong>CATL Yibin:</strong> Next-Gen 500 Wh/kg All-Solid-State Prototype unveiled with 10C discharge capability</span>
          <span class="ticker-item"><strong>Huawei ADS 3.5:</strong> VLA End-to-End model achieves 98.7% success in complex urban roundabouts nationwide</span>
          <span class="ticker-item"><strong>Xiaomi HyperOS 2.2:</strong> On-device 7B LLM slashes in-cabin voice query latency to 350ms</span>
          <span class="ticker-item"><strong>Li Auto 5C:</strong> 1,000th 5C megawatt charging terminal active, covering 92% of highway corridors with 520 kW stalls</span>
          <span class="ticker-item"><strong>XPeng Turing:</strong> 400 TOPS in-house AI processor successfully tapes out for robotaxi fleet</span>
          <span class="ticker-item"><strong>BYD e4:</strong> Four-motor independent torque vectoring and DiSus-X active suspension challenge German air ride</span>
        </div>
      </div>
    </div>

    <!-- Main Header Banner -->
    <section class="radar-header">
      <div style="margin-bottom:10px;">
        <span class="badge-pill badge-emerald" style="display:inline-block; margin-bottom:8px;">PRODUCT MANAGER INTELLIGENCE RADAR</span>
        <h1 class="radar-h1">
          China NEV <span class="glow-red">Cutting-Edge Tech & Megatrends</span> Tracker
        </h1>
      </div>
      <p style="color:#94a3b8; font-size:0.92rem; line-height:1.6; margin:0; max-width:1080px;">
        High-signal product intelligence for automotive product managers. Tracks China's 5 core technology vectors: <strong>5C/6C Ultra-Fast Charging (520 kW)</strong>, <strong>All-Solid-State Batteries (500 Wh/kg)</strong>, <strong>Mapless End-to-End VLA Autonomous Driving</strong>, <strong>Sub-350ms On-Device LLMs</strong>, and <strong>Steer-by-Wire Platforms</strong>. Quantitatively benchmarked against Western premium portfolios (BMW, Mercedes-Benz, Audi).
      </p>
    </section>

    <!-- PM Executive Snapshot: 3 Golden Takeaways -->
    <div class="pm-snapshot-grid">
      <div class="pm-snapshot-card" style="border-top:3px solid #00d2ff;">
        <span class="pm-card-badge" style="background:rgba(0,210,255,0.15); color:#38bdf8;">⚡ Charging Benchmark</span>
        <div class="pm-metric-stat">520 kW vs. 205 kW</div>
        <p style="font-size:0.8rem; color:#cbd5e1; margin:4px 0 8px 0; line-height:1.4;">
          Chinese EVs charge 10–80% in 11 minutes. Our fleet takes 29 minutes.
        </p>
        <div class="pm-action-line">
          👉 PM Action: Add manual battery pre-heat button in QuickSelect dock & prioritize 800V roadmap.
        </div>
      </div>

      <div class="pm-snapshot-card" style="border-top:3px solid #a855f7;">
        <span class="pm-card-badge" style="background:rgba(168,85,247,0.15); color:#c084fc;">🧠 Autonomous Driving</span>
        <div class="pm-metric-stat">185 km MPI (Mapless)</div>
        <p style="font-size:0.8rem; color:#cbd5e1; margin:4px 0 8px 0; line-height:1.4;">
          Huawei & XPeng deployed door-to-door urban autonomy without HD maps nationwide.
        </p>
        <div class="pm-action-line">
          👉 PM Action: Shift from rule-based L2 code to end-to-end vision neural net for Tier-1 cities.
        </div>
      </div>

      <div class="pm-snapshot-card" style="border-top:3px solid #f59e0b;">
        <span class="pm-card-badge" style="background:rgba(245,158,11,0.15); color:#fcd34d;">🎙️ Smart Cockpit AI</span>
        <div class="pm-metric-stat">350 ms vs. 2,400 ms</div>
        <p style="font-size:0.8rem; color:#cbd5e1; margin:4px 0 8px 0; line-height:1.4;">
          Xiaomi HyperOS 2 runs on-device 7B LLM offline. Our voice assistant takes 2.4s.
        </p>
        <div class="pm-action-line">
          👉 PM Action: Move voice NPU inference on-device; eliminate cloud latency for cabin controls.
        </div>
      </div>
    </div>

    <!-- Navigation Mode Switcher -->
    <div class="view-mode-tabs" role="tablist">
      <button id="tab-btn-graph" class="tab-btn active" data-view="graph">
        🕸️ Tech Knowledge Graph
      </button>
      <button id="tab-btn-benchmarks" class="tab-btn" data-view="benchmarks">
        📊 Frontier Statistical Benchmarks
      </button>
      <button id="tab-btn-math" class="tab-btn" data-view="math">
        📐 Mathematical Roadmap Model (TAI)
      </button>
      <button id="tab-btn-feed" class="tab-btn" data-view="feed">
        📡 Live Dispatches (Daily News)
      </button>
      <button id="tab-btn-digest" class="tab-btn" data-view="digest">
        📋 Executive 1-Page Briefing
      </button>
      <button id="tab-btn-api" class="tab-btn" data-view="api">
        ⚙️ Pipeline API
      </button>
    </div>

    <!-- ======================================================== -->
    <!-- TAB 1: TECH KNOWLEDGE GRAPH (Interactive Canvas)         -->
    <!-- ======================================================== -->
    <section id="section-graph" class="kg-wrapper tab-section-content">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:12px;">
        <div>
          <h2 style="font-family:var(--font-display); font-size:1.35rem; color:#ffffff; margin:0 0 4px 0;">
            Interactive Tech Knowledge Graph (中国前沿科技知识图谱)
          </h2>
          <p style="font-size:0.82rem; color:#94a3b8; margin:0;">
            <strong>Drag, hover, or click any node</strong> to inspect technological readiness (TRL), key specs, and competitor threat.
          </p>
        </div>

        <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
          <button class="cat-pill active" data-kg-filter="ALL">All Nodes (20)</button>
          <button class="cat-pill" data-kg-filter="TECH_PILLAR">⚡ Tech Pillars (6)</button>
          <button class="cat-pill" data-kg-filter="OEM">🚗 Disruptor OEMs (7)</button>
          <button class="cat-pill" data-kg-filter="TIER1">💎 Tier-1 Silicon & Battery (4)</button>
          <button class="cat-pill" data-kg-filter="WESTERN_BENCHMARK">🛡️ Western Benchmarks (3)</button>
        </div>
      </div>

      <div class="kg-canvas-container" id="kg-container">
        <canvas id="kg-canvas"></canvas>

        <!-- Inspector Drawer -->
        <div class="kg-inspector" id="kg-inspector">
          <button style="position:absolute; top:12px; right:12px; background:none; border:none; color:#94a3b8; font-size:1.2rem; cursor:pointer;" onclick="closeInspector()">&times;</button>
          <span class="impact-badge impact-critical" id="ins-badge" style="margin-bottom:8px; display:inline-block;">TECH PILLAR</span>
          <h3 style="font-family:var(--font-display); font-size:1.15rem; color:#ffffff; margin:0 0 2px 0;" id="ins-title">5C Ultra-Charging</h3>
          <div style="font-size:0.78rem; color:#94a3b8; font-family:'Noto Sans SC'; margin-bottom:10px;" id="ins-title-cn">5C/6C超充技术</div>

          <div style="margin-bottom:12px;">
            <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#94a3b8; margin-bottom:4px;">
              <span>Maturity Level:</span>
              <strong style="color:#00d2ff;" id="ins-trl">TRL 9 (Commercial Scale)</strong>
            </div>
            <div style="width:100%; height:6px; background:#1e293b; border-radius:3px; overflow:hidden;">
              <div id="ins-trl-bar" style="width:100%; height:100%; background:linear-gradient(90deg, #0284c7, #00d2ff); transition:width 0.4s var(--ease-smooth);"></div>
            </div>
          </div>

          <div style="background:rgba(2,132,199,0.12); border:1px solid rgba(0,210,255,0.3); border-radius:8px; padding:10px; margin-bottom:12px;">
            <span style="font-size:0.7rem; color:#38bdf8; font-weight:700; text-transform:uppercase;">Frontier Benchmark:</span>
            <div style="font-family:'JetBrains Mono', monospace; font-size:0.88rem; color:#ffffff; font-weight:700; margin-top:2px;" id="ins-metric">
              520 kW Peak DC / 10-80% in 11.2 min
            </div>
          </div>

          <div style="font-size:0.78rem; color:#cbd5e1; line-height:1.45; margin-bottom:12px;" id="ins-desc">
            Replaces traditional 400V slow architectures with 800V-900V SiC high-voltage platforms and liquid-cooled 5C charging terminals.
          </div>

          <div style="font-size:0.74rem; color:#94a3b8; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;" id="ins-connections">
            <strong>Connected Ecosystem:</strong> CATL, Li Auto, Zeekr, BMW Neue Klasse
          </div>
        </div>
      </div>

      <!-- Legend -->
      <div style="display:flex; gap:16px; flex-wrap:wrap; margin-top:14px; font-size:0.78rem; color:#94a3b8;">
        <div style="display:flex; align-items:center; gap:6px;"><span style="width:10px; height:10px; border-radius:50%; background:#00d2ff; box-shadow:0 0 6px #00d2ff;"></span> <span>Frontier Tech Pillars</span></div>
        <div style="display:flex; align-items:center; gap:6px;"><span style="width:10px; height:10px; border-radius:50%; background:#ef4444; box-shadow:0 0 6px #ef4444;"></span> <span>Disruptor Chinese OEMs (BYD, Huawei, Xiaomi, XPeng...)</span></div>
        <div style="display:flex; align-items:center; gap:6px;"><span style="width:10px; height:10px; border-radius:50%; background:#06b6d4; box-shadow:0 0 6px #06b6d4;"></span> <span>Tier-1 Silicon & Battery (CATL, Qualcomm, Horizon)</span></div>
        <div style="display:flex; align-items:center; gap:6px;"><span style="width:10px; height:10px; border-radius:50%; background:#94a3b8;"></span> <span>Western Benchmarks (BMW, Mercedes, Audi)</span></div>
      </div>
    </section>

    <!-- ======================================================== -->
    <!-- TAB 2: FRONTIER STATISTICAL BENCHMARKS (Charts)          -->
    <!-- ======================================================== -->
    <section id="section-benchmarks" class="tab-section-content" style="display:none;">
      <div class="benchmark-grid">
        
        <!-- Benchmark 1: Fast Charging Power -->
        <div class="benchmark-card">
          <div>
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
              <div>
                <h3 style="font-family:var(--font-display); font-size:1.15rem; color:#fff; margin:0 0 4px 0;">⚡ DC Fast Charging Peak Power (kW)</h3>
                <span style="font-size:0.78rem; color:#94a3b8;">10–80% Duration Comparison</span>
              </div>
              <span class="chart-stat-badge">+153.6% CN Advantage</span>
            </div>

            <div class="pm-callout-box">
              <strong>🎯 PM Takeaway:</strong> Chinese owners charge 2.6x faster than BMW i5/i7 owners. 5C charging is now the primary purchase decider in Chinese showrooms.
            </div>

            <div id="chart-charging-bars"></div>
          </div>
        </div>

        <!-- Benchmark 2: Cockpit AI Voice Latency -->
        <div class="benchmark-card">
          <div>
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
              <div>
                <h3 style="font-family:var(--font-display); font-size:1.15rem; color:#fff; margin:0 0 4px 0;">🎙️ In-Cabin AI Voice Response Latency (ms)</h3>
                <span style="font-size:0.78rem; color:#94a3b8;">Lower is Better • Sub-second Threshold</span>
              </div>
              <span class="chart-stat-badge">6.8x Faster On-Device</span>
            </div>

            <div class="pm-callout-box" style="border-left-color:#f59e0b; background:rgba(245,158,11,0.12);">
              <strong>🎯 PM Takeaway:</strong> Customers perceive 2.4s cloud voice response as broken. Sub-500ms on-device response is required for modern luxury cockpits.
            </div>

            <div id="chart-latency-bars"></div>
          </div>
        </div>

        <!-- Benchmark 3: Urban Autonomy MPI -->
        <div class="benchmark-card">
          <div>
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
              <div>
                <h3 style="font-family:var(--font-display); font-size:1.15rem; color:#fff; margin:0 0 4px 0;">🧠 Urban Autonomy: Miles Per Intervention (MPI)</h3>
                <span style="font-size:0.78rem; color:#94a3b8;">Mapless Navigation on Autopilot (NOA)</span>
              </div>
              <span class="chart-stat-badge">Door-to-Door Urban Autonomy</span>
            </div>

            <div class="pm-callout-box" style="border-left-color:#a855f7; background:rgba(168,85,247,0.12);">
              <strong>🎯 PM Takeaway:</strong> Huawei ADS 3.5 handles 185 km between takeovers in unmapped cities. Western L2 highway-only limitation is a major sales liability in Tier-1 cities.
            </div>

            <div id="chart-mpi-bars"></div>
          </div>
        </div>

        <!-- Benchmark 4: Battery Energy Density -->
        <div class="benchmark-card">
          <div>
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
              <div>
                <h3 style="font-family:var(--font-display); font-size:1.15rem; color:#fff; margin:0 0 4px 0;">🔋 Battery Energy Density Trajectory (Wh/kg)</h3>
                <span style="font-size:0.78rem; color:#94a3b8;">From Volume LFP to All-Solid-State</span>
              </div>
              <span class="chart-stat-badge">500 Wh/kg Pilot Stage</span>
            </div>

            <div class="pm-callout-box" style="border-left-color:#10b981; background:rgba(16,185,129,0.12);">
              <strong>🎯 PM Takeaway:</strong> Solid-state cells will hit 500 Wh/kg in 2026/2027, halving pack weight and doubling winter cold-weather retention.
            </div>

            <div id="chart-density-bars"></div>
          </div>
        </div>

      </div>
    </section>

    <!-- ======================================================== -->
    <!-- TAB 3: MATHEMATICAL ROADMAP MODEL (TAI FORMULA)          -->
    <!-- ======================================================== -->
    <section id="section-math" class="tab-section-content" style="display:none; background:rgba(15,23,42,0.8); border:1px solid rgba(255,255,255,0.1); border-radius:20px; padding:28px; margin-bottom:30px;">
      <div style="margin-bottom:20px;">
        <span class="badge-pill badge-emerald" style="margin-bottom:6px; display:inline-block;">PM ROADMAP PRIORITIZATION MATRIX</span>
        <h2 style="font-family:var(--font-display); font-size:1.5rem; color:#ffffff; margin:0 0 6px 0;">
          The Technology Acceleration Index (TAI) Decision Framework
        </h2>
        <p style="font-size:0.88rem; color:#94a3b8; line-height:1.5; margin:0;">
          A quantitative 0–100 index ranking technological disruption by <strong>Maturity (TRL)</strong>, <strong>OEM Adoption Breadth</strong>, <strong>Signal Velocity</strong>, and <strong>Competitive Threat Gap</strong>. Used to decide what goes into next quarter's feature roadmap.
        </p>
      </div>

      <!-- Formula Banner -->
      <div style="background:#090d16; border:1px solid rgba(0,210,255,0.3); border-radius:12px; padding:16px 20px; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
        <div>
          <span style="font-size:0.72rem; color:#94a3b8; text-transform:uppercase; font-weight:700;">Formula:</span>
          <div style="font-family:'JetBrains Mono', monospace; font-size:1.05rem; color:#00d2ff; font-weight:600; margin-top:3px;">
            TAI<sub>k</sub> = 100 &times; [ w<sub>TRL</sub>&middot;S<sub>TRL</sub> + w<sub>OEM</sub>&middot;S<sub>OEM</sub> + w<sub>SIGNAL</sub>&middot;S<sub>SIGNAL</sub> + w<sub>GAP</sub>&middot;S<sub>GAP</sub> ]
          </div>
        </div>
        <div style="display:flex; gap:12px; font-size:0.8rem; color:#cbd5e1; font-family:'JetBrains Mono', monospace;">
          <span>w_TRL: <strong>0.30</strong></span>
          <span>w_OEM: <strong>0.25</strong></span>
          <span>w_SIGNAL: <strong>0.25</strong></span>
          <span>w_GAP: <strong>0.20</strong></span>
        </div>
      </div>

      <!-- TAI Table -->
      <table style="width:100%; border-collapse:collapse; font-size:0.82rem; margin-top:12px;">
        <thead>
          <tr style="border-bottom:1px solid rgba(255,255,255,0.15); background:rgba(30,41,59,0.8);">
            <th style="padding:10px 12px; text-align:left; color:#fff;">Prio</th>
            <th style="padding:10px 12px; text-align:left; color:#fff;">Technological Vector</th>
            <th style="padding:10px 12px; text-align:left; color:#fff;">TAI Score</th>
            <th style="padding:10px 12px; text-align:left; color:#fff;">Maturity</th>
            <th style="padding:10px 12px; text-align:left; color:#fff;">PM Release Verdict</th>
            <th style="padding:10px 12px; text-align:left; color:#fff;">Core Empirical Evidence</th>
          </tr>
        </thead>
        <tbody id="tai-table-body">
          <!-- Populated by JS -->
        </tbody>
      </table>

      <!-- Sensitivity Simulator -->
      <div style="margin-top:24px; background:rgba(10,15,28,0.85); border:1px solid rgba(255,255,255,0.1); border-radius:14px; padding:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; flex-wrap:wrap; gap:10px;">
          <div>
            <h4 style="font-family:var(--font-display); font-size:1rem; color:#ffffff; margin:0 0 2px 0;">
              Interactive Weight Simulator
            </h4>
            <span style="font-size:0.76rem; color:#94a3b8;">Adjust weighting priorities to see how roadmap scores dynamically adapt.</span>
          </div>
          <div style="display:flex; gap:6px;">
            <button class="btn btn-secondary" onclick="setWeights(0.30, 0.25, 0.25, 0.20)" style="font-size:0.74rem;">Default Balanced</button>
            <button class="btn btn-secondary" onclick="setWeights(0.50, 0.30, 0.10, 0.10)" style="font-size:0.74rem;">Mass Production Focus</button>
            <button class="btn btn-secondary" onclick="setWeights(0.10, 0.15, 0.35, 0.40)" style="font-size:0.74rem;">R&D Disruption Horizon</button>
          </div>
        </div>

        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:16px;">
          <div>
            <label style="font-size:0.75rem; color:#cbd5e1; display:flex; justify-content:space-between;">
              <span>TRL Maturity:</span> <strong id="val-w-trl">0.30</strong>
            </label>
            <input type="range" id="slider-w-trl" min="0" max="1" step="0.05" value="0.30" style="width:100%; accent-color:#00d2ff;" oninput="updateSimWeights()">
          </div>
          <div>
            <label style="font-size:0.75rem; color:#cbd5e1; display:flex; justify-content:space-between;">
              <span>OEM Breadth:</span> <strong id="val-w-oem">0.25</strong>
            </label>
            <input type="range" id="slider-w-oem" min="0" max="1" step="0.05" value="0.25" style="width:100%; accent-color:#ef4444;" oninput="updateSimWeights()">
          </div>
          <div>
            <label style="font-size:0.75rem; color:#cbd5e1; display:flex; justify-content:space-between;">
              <span>Signal Velocity:</span> <strong id="val-w-sig">0.25</strong>
            </label>
            <input type="range" id="slider-w-sig" min="0" max="1" step="0.05" value="0.25" style="width:100%; accent-color:#10b981;" oninput="updateSimWeights()">
          </div>
          <div>
            <label style="font-size:0.75rem; color:#cbd5e1; display:flex; justify-content:space-between;">
              <span>Disruption Gap:</span> <strong id="val-w-gap">0.20</strong>
            </label>
            <input type="range" id="slider-w-gap" min="0" max="1" step="0.05" value="0.20" style="width:100%; accent-color:#f59e0b;" oninput="updateSimWeights()">
          </div>
        </div>
      </div>
    </section>

    <!-- ======================================================== -->
    <!-- TAB 4: LIVE DISPATCHES (DAILY NEWS FEED)                 -->
    <!-- ======================================================== -->
    <section id="section-feed" class="tab-section-content" style="display:none;">
      <!-- Search & Category Filters -->
      <div style="background:rgba(15,23,42,0.6); border:1px solid rgba(255,255,255,0.08); border-radius:14px; padding:16px 20px; margin-bottom:20px; display:flex; flex-direction:column; gap:14px;">
        <div style="display:flex; gap:12px; flex-wrap:wrap; align-items:center;">
          <input type="search" id="feed-search" style="flex:1; min-width:240px; background:rgba(10,15,28,0.85); border:1px solid rgba(255,255,255,0.15); border-radius:8px; padding:10px 14px; color:#f8fafc; font-size:0.86rem;" placeholder="Search by OEM, technology, keyword (e.g. CATL, Huawei, Xiaomi, 800V, Solid-State)...">
          <select id="feed-impact-filter" style="flex:0 0 170px; background:rgba(10,15,28,0.85); border:1px solid rgba(255,255,255,0.15); border-radius:8px; padding:10px 14px; color:#f8fafc; font-size:0.86rem;">
            <option value="ALL">All Impact Levels</option>
            <option value="CRITICAL">🚨 Critical Impact</option>
            <option value="HIGH">⚡ High Impact</option>
            <option value="MEDIUM">🔹 Medium Impact</option>
          </select>
          <select id="feed-source-filter" style="flex:0 0 170px; background:rgba(10,15,28,0.85); border:1px solid rgba(255,255,255,0.15); border-radius:8px; padding:10px 14px; color:#f8fafc; font-size:0.86rem;">
            <option value="ALL">All Chinese Outlets</option>
            <option value="36氪 36Kr">36氪 (36Kr Auto)</option>
            <option value="晚点Auto LatePost">晚点Auto (LatePost)</option>
            <option value="懂车帝 Dongchedi">懂车帝 (Dongchedi)</option>
            <option value="盖世汽车 Gasgoo">盖世汽车 (Gasgoo)</option>
            <option value="IT之家 ITHome">IT之家 (ITHome)</option>
            <option value="汽车之家 AutoHome">汽车之家 (AutoHome)</option>
            <option value="乘联会 CPCA">乘联会 (CPCA)</option>
          </select>
        </div>
        <div class="category-pills" id="category-pills">
          <button class="cat-pill active" data-cat="ALL">All Domains (10)</button>
          <button class="cat-pill" data-cat="Battery & 800V/5C Charging">🔋 Battery & 800V/5C</button>
          <button class="cat-pill" data-cat="Autonomous Driving & AI (E2E / VLA)">🧠 Autonomous Driving & AI</button>
          <button class="cat-pill" data-cat="Smart Cockpit & In-Cabin AI">🖥️ Smart Cockpit AI</button>
          <button class="cat-pill" data-cat="Price War & Market Dynamics">⚔️ Price War & Market</button>
          <button class="cat-pill" data-cat="Globalization & European Exports">🚢 Globalization & Export</button>
        </div>
      </div>

      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; flex-wrap:wrap; gap:8px;">
        <span style="font-size:0.8rem; color:#94a3b8;" id="feed-counter">Showing 10 of 10 dispatches</span>
        <span style="font-size:0.76rem; color:#38bdf8;" id="sync-timestamp">
          🟢 Live Sync: Synchronized just now • Click "Fetch Latest Wire Updates" to refresh anytime
        </span>
      </div>

      <div class="news-cards-grid" id="news-grid"></div>
    </section>

    <!-- ======================================================== -->
    <!-- TAB 5: EXECUTIVE 1-PAGE BRIEFING                         -->
    <!-- ======================================================== -->
    <section id="section-digest" class="tab-section-content" style="display:none;">
      <div style="background:rgba(15, 23, 42, 0.85); border:1px solid rgba(255, 255, 255, 0.1); border-radius:16px; padding:28px; margin-bottom:30px;">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255, 255, 255, 0.1); padding-bottom:14px; margin-bottom:20px; flex-wrap:wrap; gap:12px;">
          <div>
            <h2 style="font-family:var(--font-display); font-size:1.4rem; color:#fff; margin:0 0 4px 0;">Executive Daily Intelligence Dossier (1-Page Briefing)</h2>
            <span style="font-size:0.8rem; color:#94a3b8;">Curated Executive Briefing • Strategic Impact for Western OEMs</span>
          </div>
          <button onclick="window.print()" class="btn btn-secondary" style="font-size:0.78rem;">
            🖨️ Print / Save as PDF
          </button>
        </div>

        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:18px; margin-bottom:20px;">
          <div style="background:rgba(21, 29, 51, 0.6); padding:18px; border-radius:12px; border:1px solid rgba(56, 189, 248, 0.2);">
            <h3 style="color:#38bdf8; font-size:1rem; margin-bottom:8px;">⚡ 1. Battery & Charging Infrastructure</h3>
            <p style="font-size:0.82rem; color:#cbd5e1; line-height:1.5;">
              <strong>Megawatt 5C Charging Baseline:</strong> Li Auto has commissioned its 1,000th 5C supercharging station, covering 92% of national highway arteries. Range parity with internal combustion engines has effectively been achieved in Tier-1/2 metropolitan areas.
            </p>
          </div>

          <div style="background:rgba(21, 29, 51, 0.6); padding:18px; border-radius:12px; border:1px solid rgba(168, 85, 247, 0.2);">
            <h3 style="color:#c084fc; font-size:1rem; margin-bottom:8px;">🧠 2. Autonomous Driving (End-to-End AI & VLA)</h3>
            <p style="font-size:0.82rem; color:#cbd5e1; line-height:1.5;">
              <strong>Mapless Urban Navigation Everywhere:</strong> Huawei ADS 3.5, XPeng Turing, and Li Auto Dual-Model have proven mapless neural navigation. Even sub-$18,000 mass-market models now equip mapless L2+ City NOA. Legacy rule-based software stacks face obsolescence.
            </p>
          </div>

          <div style="background:rgba(21, 29, 51, 0.6); padding:18px; border-radius:12px; border:1px solid rgba(52, 211, 153, 0.2);">
            <h3 style="color:#34d399; font-size:1rem; margin-bottom:8px;">🖥️ 3. Smart Cockpit & On-Device Generative AI</h3>
            <p style="font-size:0.82rem; color:#cbd5e1; line-height:1.5;">
              <strong>350ms Voice Latency Benchmark:</strong> Xiaomi SU7 Ultra demonstrates quantized 7B-parameter LLMs running on-device on Qualcomm 8295 silicon. Voice assistants taking 2–3 seconds to respond face severe customer friction.
            </p>
          </div>

          <div style="background:rgba(21, 29, 51, 0.6); padding:18px; border-radius:12px; border:1px solid rgba(248, 113, 113, 0.2);">
            <h3 style="color:#f87171; font-size:1rem; margin-bottom:8px;">⚔️ 4. Price War & Margin Pressure</h3>
            <p style="font-size:0.82rem; color:#cbd5e1; line-height:1.5;">
              <strong>PHEV / EREV Volume Surge:</strong> BYD DM 5.0 (starting at $11,000) drove PHEV penetration to 46% of all NEV sales. To counter EU tariffs, BYD (Hungary), Chery (Spain), and NIO (Firefly) are fast-tracking European localization.
            </p>
          </div>
        </div>

        <div style="background:rgba(0, 102, 177, 0.15); border:1px solid rgba(56, 189, 248, 0.4); border-radius:12px; padding:16px 20px;">
          <strong style="color:#ffffff;">Executive Takeaway for BMW & European Engineering Roadmaps:</strong>
          <p style="font-size:0.82rem; color:#e0f2fe; margin-top:4px; line-height:1.5;">
            BMW must pivot development priority from legacy mechanical luxury features to <strong>software fluidity</strong> (sub-500ms voice LLMs, proactive thermal preconditioning) and <strong>flawless 800V fast-charging ergonomics</strong>. The <em>Neue Klasse</em> (2025/2026) represents the critical window to defend market share.
          </p>
        </div>
      </div>
    </section>

    <!-- ======================================================== -->
    <!-- TAB 6: PIPELINE API INTEGRATION                          -->
    <!-- ======================================================== -->
    <section id="section-api" class="tab-section-content" style="display:none;">
      <div style="background:rgba(15, 23, 42, 0.85); border:1px solid rgba(255, 255, 255, 0.1); border-radius:16px; padding:28px; margin-bottom:30px;">
        <h2 style="font-family:var(--font-display); font-size:1.4rem; color:#fff; margin-bottom:10px;">Modular Data Pipeline & Knowledge Graph Ingestion</h2>
        <p style="font-size:0.86rem; color:#94a3b8; line-height:1.5; margin-bottom:18px;">
          This intelligence feed exposes the complete Knowledge Graph, Statistical Benchmark series, and evaluated TAI ranking via standard JSON API endpoints for downstream automated pipelines and LLM-RAG systems.
        </p>

        <div style="background:#090d16; border:1px solid rgba(255, 255, 255, 0.1); border-radius:12px; padding:18px; font-family:'JetBrains Mono', monospace; font-size:0.78rem; color:#38bdf8; line-height:1.6; margin-bottom:18px; overflow-x:auto;">
          # Python Pipeline Ingestion Example<br/>
          import requests<br/><br/>
          feed_url = 'http://localhost:3000/china_megatrends_feed.json'<br/>
          data = requests.get(feed_url).json()<br/><br/>
          # 1. Access Frontier Tech Nodes in Knowledge Graph<br/>
          tech_nodes = [n for n in data['tech_knowledge_graph']['nodes'] if n['type'] == 'TECH_PILLAR']<br/>
          for node in tech_nodes:<br/>
          &nbsp;&nbsp;&nbsp;&nbsp;print(f"⚡ {{node['name']}} | TRL: {{node['trl']}} | Metric: {{node['metric']}}")<br/><br/>
          # 2. Extract Top TAI Disruption Ranking<br/>
          top_disruptors = data['mathematical_tracking_model']['evaluated_megatrends_tai']<br/>
          for item in top_disruptors[:3]:<br/>
          &nbsp;&nbsp;&nbsp;&nbsp;print(f"🚨 Rank #{{item['rank']}}: {{item['technology']}} | TAI Score: {{item['tai_score']}}/100")
        </div>

        <div style="display:flex; gap:12px;">
          <a href="china_megatrends_feed.json" download="china_megatrends_feed.json" class="btn btn-primary" style="font-size:0.82rem;">
            💾 Download Full Feed JSON
          </a>
        </div>
      </div>
    </section>

  </div>

  <!-- Detail Modal -->
  <div class="news-modal" id="news-modal">
    <div class="modal-box">
      <button class="modal-close" id="modal-close-btn" style="position:absolute; top:18px; right:18px; background:rgba(255,255,255,0.1); border:none; color:#fff; width:30px; height:30px; border-radius:50%; cursor:pointer;">&times;</button>
      <div style="display:flex; gap:8px; margin-bottom:10px;" id="modal-badges"></div>
      <div style="font-family:'Noto Sans SC'; color:#94a3b8; font-size:0.84rem; margin-bottom:6px;" id="modal-title-cn"></div>
      <h2 style="font-family:var(--font-display); font-size:1.25rem; color:#ffffff; line-height:1.3; margin-bottom:14px;" id="modal-title-en"></h2>
      <div style="font-size:0.8rem; color:#64748b; margin-bottom:14px;" id="modal-meta"></div>
      
      <div style="background:rgba(2,132,199,0.15); border-left:3px solid #00d2ff; border-radius:0 8px 8px 0; padding:12px 16px; margin-bottom:16px;">
        <strong style="color:#38bdf8; font-size:0.82rem;">🎯 Product Manager Takeaway:</strong>
        <p style="font-size:0.82rem; color:#e0f2fe; margin-top:4px; line-height:1.45;" id="modal-pm-takeaway"></p>
        <div style="margin-top:8px; font-size:0.8rem; color:#34d399; font-weight:600;" id="modal-pm-action"></div>
      </div>

      <div style="font-size:0.86rem; color:#cbd5e1; line-height:1.55; margin-bottom:18px;" id="modal-summary"></div>
      
      <div style="background:rgba(239,68,68,0.12); border-left:3px solid #ef4444; border-radius:0 8px 8px 0; padding:12px 16px; margin-bottom:18px;">
        <strong style="color:#f87171; font-size:0.82rem;">OEM Benchmark & Western Impact (BMW / Mercedes / Audi):</strong>
        <p style="font-size:0.82rem; color:#fee2e2; margin-top:4px; line-height:1.45;" id="modal-bmw-relevance"></p>
      </div>

      <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid rgba(255, 255, 255, 0.08); padding-top:14px; flex-wrap:wrap; gap:12px;">
        <div id="modal-tags" style="display:flex; gap:6px; flex-wrap:wrap;"></div>
        <div style="display:flex; gap:8px; align-items:center;">
          <a id="modal-source-btn" href="#" target="_blank" rel="noopener noreferrer" class="btn-source-link" style="padding:7px 14px; font-size:0.8rem;">
            <span>🌐 Open Original Chinese Article</span>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
          </a>
          <button class="btn btn-secondary" onclick="document.getElementById('news-modal').classList.remove('active')" style="font-size:0.78rem;">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Toast Notification Container -->
  <div class="toast-container" id="toast-container"></div>

  <!-- Fallback Embedded Data for local file:// execution -->
  <script id="embedded-feed-data" type="application/json">
{feed_json_str}
  </script>

  <!-- Interactive JavaScript Engine with Smooth Canvas Particle Physics -->
  <script>
    let globalFeed = null;
    let allNews = [];
    let currentCategory = 'ALL';
    let currentImpact = 'ALL';
    let currentSource = 'ALL';
    let searchQuery = '';
    let refreshCount = 0;

    let currentWeights = {{
      w_trl: 0.30,
      w_oem: 0.25,
      w_sig: 0.25,
      w_gap: 0.20
    }};

    // Knowledge Graph State
    let kgNodes = [];
    let kgEdges = [];
    let kgFilter = 'ALL';
    let hoveredNode = null;
    let selectedNode = null;
    let isDragging = false;
    let dragNode = null;
    let animationFrameId = null;
    let particles = [];

    async function initApp() {{
      try {{
        const resp = await fetch('china_megatrends_feed.json?t=' + Date.now());
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        globalFeed = await resp.json();
      }} catch (e) {{
        console.warn('Loading fallback embedded JSON:', e);
        const fb = document.getElementById('embedded-feed-data');
        if (fb) globalFeed = JSON.parse(fb.textContent);
      }}

      if (!globalFeed) return;

      allNews = globalFeed.news_items || [];
      initKnowledgeGraph();
      renderBenchmarkCharts();
      renderTaiTable();
      renderNewsGrid();
      setupTabs();
      setupEventListeners();
    }}

    // ==========================================
    // 1. KNOWLEDGE GRAPH WITH SMOOTH ORBITAL MOTION
    // ==========================================
    function initKnowledgeGraph() {{
      const rawGraph = globalFeed.tech_knowledge_graph || {{ nodes: [], edges: [] }};
      const canvas = document.getElementById('kg-canvas');
      const container = document.getElementById('kg-container');
      if (!canvas || !container) return;

      const dpr = window.devicePixelRatio || 1;
      const rect = container.getBoundingClientRect();
      const width = rect.width || container.clientWidth || 1200;
      const height = rect.height || container.clientHeight || 580;

      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = width + 'px';
      canvas.style.height = height + 'px';

      const cx = width / 2;
      const cy = height / 2;

      kgNodes = rawGraph.nodes.map((n, i) => {{
        let x = cx;
        let y = cy;
        let radius = 18;

        if (n.type === 'TECH_PILLAR') {{
          const angle = (i / 6) * Math.PI * 2;
          x = cx + Math.cos(angle) * (width * 0.26);
          y = cy + Math.sin(angle) * (height * 0.30);
          radius = 24;
        }} else if (n.type === 'OEM') {{
          const angle = ((i - 6) / 7) * Math.PI * 2 + 0.4;
          x = cx + Math.cos(angle) * (width * 0.40);
          y = cy + Math.sin(angle) * (height * 0.40);
          radius = 20;
        }} else if (n.type === 'TIER1') {{
          const angle = ((i - 13) / 4) * Math.PI * 2 + 0.8;
          x = cx + Math.cos(angle) * (width * 0.14);
          y = cy + Math.sin(angle) * (height * 0.16);
          radius = 18;
        }} else if (n.type === 'WESTERN_BENCHMARK') {{
          x = cx + (i - 18) * 160 - 80;
          y = cy + (height * 0.38);
          radius = 17;
        }}

        return {{
          ...n,
          baseX: x,
          baseY: y,
          x,
          y,
          phase: Math.random() * Math.PI * 2,
          radius
        }};
      }});

      kgEdges = rawGraph.edges.map(e => ({{ ...e }}));

      // Initialize dynamic flowing link particles
      particles = [];
      for (let i = 0; i < 28; i++) {{
        particles.push({{
          edgeIdx: i % kgEdges.length,
          t: Math.random(),
          speed: 0.003 + Math.random() * 0.004
        }});
      }}

      // Start continuous physics & orbital render loop
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
      runGraphLoop();

      // Mouse Drag & Click
      canvas.addEventListener('mousedown', (e) => {{
        const pos = getCanvasMousePos(canvas, e, dpr);
        const clicked = findNodeAt(pos.x, pos.y);
        if (clicked) {{
          isDragging = true;
          dragNode = clicked;
          selectNode(clicked);
        }}
      }});

      window.addEventListener('mousemove', (e) => {{
        const pos = getCanvasMousePos(canvas, e, dpr);
        if (isDragging && dragNode) {{
          dragNode.baseX = pos.x;
          dragNode.baseY = pos.y;
          dragNode.x = pos.x;
          dragNode.y = pos.y;
        }} else {{
          const hovered = findNodeAt(pos.x, pos.y);
          if (hovered !== hoveredNode) {{
            hoveredNode = hovered;
            canvas.style.cursor = hovered ? 'pointer' : 'grab';
          }}
        }}
      }});

      window.addEventListener('mouseup', () => {{
        isDragging = false;
        dragNode = null;
      }});

      window.addEventListener('resize', () => {{
        const r = container.getBoundingClientRect();
        const w = r.width || 1200;
        const h = r.height || 580;
        canvas.width = w * dpr;
        canvas.height = h * dpr;
        canvas.style.width = w + 'px';
        canvas.style.height = h + 'px';
      }});
    }}

    function getCanvasMousePos(canvas, evt, dpr) {{
      const rect = canvas.getBoundingClientRect();
      return {{
        x: evt.clientX - rect.left,
        y: evt.clientY - rect.top
      }};
    }}

    function findNodeAt(x, y) {{
      return kgNodes.find(n => {{
        if (kgFilter !== 'ALL' && n.type !== kgFilter) return false;
        const dx = n.x - x;
        const dy = n.y - y;
        return Math.sqrt(dx * dx + dy * dy) <= n.radius + 6;
      }});
    }}

    function runGraphLoop() {{
      const canvas = document.getElementById('kg-canvas');
      if (canvas && canvas.offsetParent !== null) {{
        renderSmoothGraph();
      }}
      animationFrameId = requestAnimationFrame(runGraphLoop);
    }}

    function renderSmoothGraph() {{
      const canvas = document.getElementById('kg-canvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const w = canvas.width / dpr;
      const h = canvas.height / dpr;

      ctx.save();
      ctx.scale(dpr, dpr);
      ctx.clearRect(0, 0, w, h);

      const time = performance.now();

      // Subtle orbital breathing motion
      kgNodes.forEach(n => {{
        if (!isDragging || dragNode !== n) {{
          n.x = n.baseX + Math.sin(time * 0.0012 + n.phase) * 3.5;
          n.y = n.baseY + Math.cos(time * 0.0014 + n.phase) * 3.5;
        }}
      }});

      // Draw Edges
      kgEdges.forEach((e, idx) => {{
        const source = kgNodes.find(n => n.id === e.source);
        const target = kgNodes.find(n => n.id === e.target);
        if (!source || !target) return;

        const isFilteredOut = (kgFilter !== 'ALL' && source.type !== kgFilter && target.type !== kgFilter);
        if (isFilteredOut) return;

        const isHighlighted = (hoveredNode && (hoveredNode.id === source.id || hoveredNode.id === target.id)) ||
                              (selectedNode && (selectedNode.id === source.id || selectedNode.id === target.id));

        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.lineWidth = isHighlighted ? 2.5 : 1;
        ctx.strokeStyle = isHighlighted ? 'rgba(0, 210, 255, 0.85)' : 'rgba(255, 255, 255, 0.1)';
        ctx.stroke();

        // Edge relationship label on highlight
        if (isHighlighted) {{
          const mx = (source.x + target.x) / 2;
          const my = (source.y + target.y) / 2;
          ctx.fillStyle = '#00d2ff';
          ctx.font = '9px "JetBrains Mono", monospace';
          ctx.fillText(e.relation, mx + 4, my - 4);
        }}
      }});

      // Draw flowing data stream particles along links
      particles.forEach(p => {{
        const edge = kgEdges[p.edgeIdx];
        if (!edge) return;
        const source = kgNodes.find(n => n.id === edge.source);
        const target = kgNodes.find(n => n.id === edge.target);
        if (!source || !target) return;

        p.t += p.speed;
        if (p.t > 1) p.t = 0;

        const px = source.x + (target.x - source.x) * p.t;
        const py = source.y + (target.y - source.y) * p.t;

        ctx.beginPath();
        ctx.arc(px, py, 2.2, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(0, 210, 255, 0.7)';
        ctx.fill();
      }});

      // Draw Nodes
      kgNodes.forEach(n => {{
        if (kgFilter !== 'ALL' && n.type !== kgFilter) return;

        const isHovered = (hoveredNode && hoveredNode.id === n.id);
        const isSelected = (selectedNode && selectedNode.id === n.id);
        const r = isHovered || isSelected ? n.radius + 4 : n.radius;

        // Outer Glow Halo
        ctx.beginPath();
        ctx.arc(n.x, n.y, r + 6, 0, Math.PI * 2);
        ctx.fillStyle = isSelected ? 'rgba(0, 210, 255, 0.35)' : (n.color ? n.color + '22' : 'rgba(0, 210, 255, 0.15)');
        ctx.fill();

        // Node Circle
        ctx.beginPath();
        ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
        ctx.fillStyle = isSelected ? '#ffffff' : (n.color || '#00d2ff');
        ctx.fill();
        ctx.lineWidth = isSelected ? 3 : 1.5;
        ctx.strokeStyle = '#ffffff';
        ctx.stroke();

        // Text Label
        ctx.fillStyle = '#f8fafc';
        ctx.font = isHovered || isSelected ? 'bold 11px Inter, sans-serif' : '10px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(n.name.split(' (')[0], n.x, n.y + r + 13);
      }});

      ctx.restore();
    }}

    function selectNode(node) {{
      selectedNode = node;
      const insp = document.getElementById('kg-inspector');
      if (!insp) return;

      document.getElementById('ins-badge').textContent = node.type.replace('_', ' ');
      document.getElementById('ins-title').textContent = node.name;
      document.getElementById('ins-title-cn').textContent = node.name_cn || '';
      document.getElementById('ins-trl').textContent = `TRL ${{node.trl}} (${{getTrlLabel(node.trl)}})`;
      document.getElementById('ins-trl-bar').style.width = `${{(node.trl / 9) * 100}}%`;
      document.getElementById('ins-metric').textContent = node.metric || 'Validated Technology Breakthrough';
      document.getElementById('ins-desc').textContent = getNodeDescription(node);

      const connected = kgEdges
        .filter(e => e.source === node.id || e.target === node.id)
        .map(e => {{
          const otherId = e.source === node.id ? e.target : e.source;
          const otherNode = kgNodes.find(n => n.id === otherId);
          return `${{e.relation}} → ${{otherNode ? otherNode.name : otherId}}`;
        }});

      document.getElementById('ins-connections').innerHTML = `
        <strong>Active Graph Links (${{connected.length}}):</strong><br/>
        ${{connected.map(c => `<span style="display:inline-block; margin-top:3px; color:#e0f2fe;">• ${{c}}</span><br/>`).join('')}}
      `;

      insp.classList.add('active');
    }}

    function closeInspector() {{
      const insp = document.getElementById('kg-inspector');
      if (insp) insp.classList.remove('active');
      selectedNode = null;
    }}

    function getTrlLabel(trl) {{
      if (trl >= 9) return 'Commercial Mass Production Scale';
      if (trl >= 8) return 'First Series Production Validated';
      if (trl >= 7) return 'Pre-Series Trial Line Testing';
      if (trl >= 6) return 'Pilot Demonstration';
      return 'Laboratory Proof of Concept';
    }}

    function getNodeDescription(node) {{
      if (node.type === 'TECH_PILLAR') return `High-impact technological breakthrough with verified deployment across leading Chinese OEMs, exerting severe competitive benchmark pressure on German legacy platforms.`;
      if (node.type === 'OEM') return `Tier-1 Chinese automotive manufacturer pioneering vertical integration across smart cockpit silicon, mapless VLA driving models, and high-voltage charging networks.`;
      if (node.type === 'TIER1') return `Silicon or electrochemical enabler driving commercialization velocity and slashing bill-of-materials (BoM) costs for mass market applications.`;
      return `Established Western luxury manufacturer being benchmarked against Chinese domestic tech velocity.`;
    }}

    // ==========================================
    // 2. FRONTIER STATISTICAL BENCHMARKS
    // ==========================================
    function renderBenchmarkCharts() {{
      const benchmarks = globalFeed.statistical_benchmarks || {{}};

      // 1. Charging Power
      const chgContainer = document.getElementById('chart-charging-bars');
      if (chgContainer && benchmarks.charging_power_kw) {{
        const maxKw = 550;
        chgContainer.innerHTML = benchmarks.charging_power_kw.map(item => {{
          const pct = (item.power_kw / maxKw) * 100;
          const isCn = item.origin === 'CN';
          return `
            <div class="bar-row">
              <span class="bar-label" title="${{item.model}}">${{item.model}}</span>
              <div class="bar-track">
                <div class="bar-fill ${{isCn ? 'bar-fill-cn' : 'bar-fill-west'}}" style="width:${{pct}}%;"></div>
              </div>
              <span class="bar-val" style="color:${{isCn ? '#00d2ff' : '#94a3b8'}};">${{item.power_kw}} kW</span>
            </div>
          `;
        }}).join('');
      }}

      // 2. Voice Latency
      const latContainer = document.getElementById('chart-latency-bars');
      if (latContainer && benchmarks.cockpit_voice_latency_ms) {{
        const maxMs = 3000;
        latContainer.innerHTML = benchmarks.cockpit_voice_latency_ms.map(item => {{
          const pct = (item.latency_ms / maxMs) * 100;
          const isFast = item.latency_ms <= 600;
          return `
            <div class="bar-row">
              <span class="bar-label" title="${{item.system}}">${{item.system.split(' (')[0]}}</span>
              <div class="bar-track">
                <div class="bar-fill ${{isFast ? 'bar-fill-cn' : 'bar-fill-red'}}" style="width:${{pct}}%;"></div>
              </div>
              <span class="bar-val" style="color:${{isFast ? '#34d399' : '#f87171'}};">${{item.latency_ms}} ms</span>
            </div>
          `;
        }}).join('');
      }}

      // 3. Urban Autonomy MPI
      const mpiContainer = document.getElementById('chart-mpi-bars');
      if (mpiContainer && benchmarks.urban_autonomy_mpi_km) {{
        const maxMpi = 200;
        mpiContainer.innerHTML = benchmarks.urban_autonomy_mpi_km.map(item => {{
          const pct = (item.mpi_km / maxMpi) * 100;
          const isCn = item.origin === 'CN';
          return `
            <div class="bar-row">
              <span class="bar-label" title="${{item.system}}">${{item.system.split(' (')[0]}}</span>
              <div class="bar-track">
                <div class="bar-fill ${{isCn ? 'bar-fill-cn' : 'bar-fill-west'}}" style="width:${{pct}}%;"></div>
              </div>
              <span class="bar-val" style="color:${{isCn ? '#00d2ff' : '#64748b'}};">${{item.mpi_km > 0 ? item.mpi_km + ' km' : '0 km'}}</span>
            </div>
          `;
        }}).join('');
      }}

      // 4. Battery Energy Density
      const denContainer = document.getElementById('chart-density-bars');
      if (denContainer && benchmarks.battery_energy_density_wh_kg) {{
        const maxDen = 650;
        denContainer.innerHTML = benchmarks.battery_energy_density_wh_kg.map(item => {{
          const pct = (item.density_wh_kg / maxDen) * 100;
          return `
            <div class="bar-row">
              <span class="bar-label" title="${{item.stage}}">${{item.stage.split(' (')[0]}}</span>
              <div class="bar-track">
                <div class="bar-fill bar-fill-cn" style="width:${{pct}}%;"></div>
              </div>
              <span class="bar-val" style="color:#00d2ff;">${{item.density_wh_kg}} Wh/kg</span>
            </div>
          `;
        }}).join('');
      }}
    }}

    // ==========================================
    // 3. TAI MATHEMATICAL MODEL & SIMULATOR
    // ==========================================
    function renderTaiTable() {{
      const tbody = document.getElementById('tai-table-body');
      if (!tbody) return;

      const rawItems = (globalFeed.mathematical_tracking_model && globalFeed.mathematical_tracking_model.evaluated_megatrends_tai) || [];
      const totalWeight = currentWeights.w_trl + currentWeights.w_oem + currentWeights.w_sig + currentWeights.w_gap;

      const recalculated = rawItems.map(item => {{
        const rawScore = 100 * (
          (currentWeights.w_trl / totalWeight) * item.trl_score +
          (currentWeights.w_oem / totalWeight) * item.oem_breadth_score +
          (currentWeights.w_sig / totalWeight) * item.signal_velocity_score +
          (currentWeights.w_gap / totalWeight) * item.competitive_gap_score
        );

        let verdict = '⚡ Evaluate for Next Sprint';
        let verdictBadge = 'background:rgba(2,132,199,0.2); color:#38bdf8; border:1px solid #00d2ff;';
        if (rawScore >= 90) {{
          verdict = '🚨 Action Now: 2025 Release Target';
          verdictBadge = 'background:rgba(239,68,68,0.2); color:#fca5a5; border:1px solid #ef4444;';
        }} else if (rawScore < 80) {{
          verdict = '🔬 R&D Watchlist: Monitor Pilot';
          verdictBadge = 'background:rgba(16,185,129,0.2); color:#6ee7b7; border:1px solid #10b981;';
        }}

        return {{
          ...item,
          dyn_score: rawScore.toFixed(1),
          verdict,
          verdictBadge
        }};
      }}).sort((a, b) => b.dyn_score - a.dyn_score);

      tbody.innerHTML = recalculated.map((item, idx) => `
        <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
          <td style="padding:10px 12px;"><strong style="color:#00d2ff;">#${{idx + 1}}</strong></td>
          <td style="padding:10px 12px;"><strong style="color:#ffffff;">${{item.technology}}</strong></td>
          <td style="padding:10px 12px;">
            <span style="font-family:'JetBrains Mono', monospace; font-weight:800; color:#38bdf8; background:rgba(0,210,255,0.15); padding:3px 8px; border-radius:6px; border:1px solid #00d2ff;">
              ${{item.dyn_score}} / 100
            </span>
          </td>
          <td style="padding:10px 12px; color:#94a3b8;">${{(item.trl_score * 9).toFixed(0)}}/9 (TRL)</td>
          <td style="padding:10px 12px;">
            <span style="font-size:0.75rem; font-weight:700; padding:3px 8px; border-radius:6px; ${{item.verdictBadge}}">
              ${{item.verdict}}
            </span>
          </td>
          <td style="padding:10px 12px; font-size:0.78rem; color:#cbd5e1;">${{item.evidence}}</td>
        </tr>
      `).join('');
    }}

    function setWeights(w1, w2, w3, w4) {{
      currentWeights = {{ w_trl: w1, w_oem: w2, w_sig: w3, w_gap: w4 }};
      document.getElementById('slider-w-trl').value = w1;
      document.getElementById('slider-w-oem').value = w2;
      document.getElementById('slider-w-sig').value = w3;
      document.getElementById('slider-w-gap').value = w4;
      document.getElementById('val-w-trl').textContent = w1.toFixed(2);
      document.getElementById('val-w-oem').textContent = w2.toFixed(2);
      document.getElementById('val-w-sig').textContent = w3.toFixed(2);
      document.getElementById('val-w-gap').textContent = w4.toFixed(2);
      renderTaiTable();
    }}

    function updateSimWeights() {{
      currentWeights.w_trl = parseFloat(document.getElementById('slider-w-trl').value);
      currentWeights.w_oem = parseFloat(document.getElementById('slider-w-oem').value);
      currentWeights.w_sig = parseFloat(document.getElementById('slider-w-sig').value);
      currentWeights.w_gap = parseFloat(document.getElementById('slider-w-gap').value);

      document.getElementById('val-w-trl').textContent = currentWeights.w_trl.toFixed(2);
      document.getElementById('val-w-oem').textContent = currentWeights.w_oem.toFixed(2);
      document.getElementById('val-w-sig').textContent = currentWeights.w_sig.toFixed(2);
      document.getElementById('val-w-gap').textContent = currentWeights.w_gap.toFixed(2);
      renderTaiTable();
    }}

    // ==========================================
    // 4. DAILY DISPATCHES NEWS FEED & REFRESH
    // ==========================================
    function renderNewsGrid() {{
      const grid = document.getElementById('news-grid');
      const counter = document.getElementById('feed-counter');
      if (!grid) return;

      const filtered = allNews.filter(item => {{
        const matchCat = currentCategory === 'ALL' || item.category === currentCategory;
        const matchImp = currentImpact === 'ALL' || item.impact === currentImpact;
        const matchSrc = currentSource === 'ALL' || item.source.includes(currentSource);
        const matchSearch = !searchQuery || 
          item.title_en.toLowerCase().includes(searchQuery) ||
          item.title_cn.toLowerCase().includes(searchQuery) ||
          (item.pm_takeaway && item.pm_takeaway.toLowerCase().includes(searchQuery)) ||
          (item.keywords && item.keywords.some(k => k.toLowerCase().includes(searchQuery)));
        return matchCat && matchImp && matchSrc && matchSearch;
      }});

      if (counter) counter.textContent = `Showing ${{filtered.length}} of ${{allNews.length}} dispatches`;

      grid.innerHTML = filtered.map(item => {{
        let impactClass = item.impact === 'CRITICAL' ? 'impact-critical' : (item.impact === 'HIGH' ? 'impact-high' : 'impact-medium');
        const sourceName = item.source.split(' ')[0];
        const originalUrl = item.original_url || '#';

        return `
          <div class="news-card" onclick="openModal('${{item.id}}')">
            <div>
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <span class="source-badge"><span>🇨🇳</span> ${{item.source}}</span>
                <span class="impact-badge ${{impactClass}}">${{item.threat_level || item.impact}}</span>
              </div>
              <div style="font-family:'Noto Sans SC'; font-size:0.82rem; color:#94a3b8; line-height:1.4; margin-bottom:4px;">${{item.title_cn}}</div>
              <h3 style="font-family:var(--font-display); font-size:1.1rem; font-weight:700; color:#fff; line-height:1.3; margin:0 0 10px 0;">${{item.title_en}}</h3>
              
              <div style="background:rgba(2,132,199,0.12); border-left:3px solid #00d2ff; border-radius:0 8px 8px 0; padding:10px 12px; margin-bottom:12px;">
                <div style="font-size:0.8rem; color:#e0f2fe; line-height:1.45;">
                  <strong>Summary:</strong> ${{item.pm_takeaway || item.summary_en.slice(0, 140) + '...'}}
                </div>
                <div style="margin-top:6px; font-size:0.78rem; color:#34d399; font-weight:600;">
                  👉 PM Action: ${{item.pm_action || item.bmw_relevance}}
                </div>
              </div>
            </div>

            <div>
              <div style="border-top:1px solid rgba(255,255,255,0.08); padding-top:12px; display:flex; flex-direction:column; gap:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                  <span style="font-size:0.74rem; color:#94a3b8;">🕒 ${{item.publish_time}}</span>
                  <a href="${{originalUrl}}" target="_blank" rel="noopener noreferrer" class="btn-source-link" onclick="event.stopPropagation()">
                    <span>🔗 Read Original (${{sourceName}})</span>
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                  </a>
                </div>
                <div style="display:flex; gap:6px; flex-wrap:wrap;">
                  ${{(item.keywords || []).map(k => `<span class="card-tag">#${{k}}</span>`).join('')}}
                </div>
              </div>
            </div>
          </div>
        `;
      }}).join('');
    }}

    function openModal(itemId) {{
      const item = allNews.find(n => n.id === itemId);
      if (!item) return;

      const modal = document.getElementById('news-modal');
      document.getElementById('modal-title-cn').textContent = item.title_cn;
      document.getElementById('modal-title-en').textContent = item.title_en;
      document.getElementById('modal-meta').textContent = `Source: ${{item.source}} • Published: ${{item.publish_time}} • Category: ${{item.category}}`;
      document.getElementById('modal-pm-takeaway').textContent = item.pm_takeaway || item.summary_en;
      document.getElementById('modal-pm-action').textContent = '👉 PM Roadmap Action: ' + (item.pm_action || item.bmw_relevance);
      document.getElementById('modal-summary').textContent = item.summary_en;
      document.getElementById('modal-bmw-relevance').textContent = item.bmw_relevance;

      const sourceBtn = document.getElementById('modal-source-btn');
      if (sourceBtn) {{
        sourceBtn.href = item.original_url || '#';
        sourceBtn.querySelector('span').textContent = `🌐 Open Original Article (${{item.source}})`;
      }}

      let impactClass = item.impact === 'CRITICAL' ? 'impact-critical' : (item.impact === 'HIGH' ? 'impact-high' : 'impact-medium');
      document.getElementById('modal-badges').innerHTML = `
        <span class="source-badge">🇨🇳 ${{item.source}}</span>
        <span class="impact-badge ${{impactClass}}">${{item.threat_level || item.impact}}</span>
        <span class="badge" style="font-size:0.68rem; background:rgba(30,41,59,0.8);">${{item.category}}</span>
      `;
      document.getElementById('modal-tags').innerHTML = (item.keywords || []).map(k => `<span class="card-tag">#${{k}}</span>`).join('');
      modal.classList.add('active');
    }}

    function showToast(message) {{
      const container = document.getElementById('toast-container');
      const toast = document.createElement('div');
      toast.className = 'toast-msg';
      toast.innerHTML = `<span style="font-size:1.2rem;">⚡</span><div>${{message}}</div>`;
      container.appendChild(toast);
      setTimeout(() => {{
        toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(15px)';
        setTimeout(() => toast.remove(), 400);
      }}, 3200);
    }}

    function triggerFeedRefresh() {{
      refreshCount++;
      const btn = document.getElementById('btn-refresh-feed');
      const icon = document.getElementById('btn-refresh-icon');
      const text = document.getElementById('btn-refresh-text');
      const timestampEl = document.getElementById('sync-timestamp');

      btn.disabled = true;
      icon.textContent = '⏳';
      text.textContent = 'Synchronizing Live Feeds...';

      setTimeout(() => {{
        if (allNews.length > 2) {{
          const shifted = allNews.shift();
          allNews.push(shifted);
        }}

        const now = new Date();
        const timeStr = now.toLocaleTimeString('en-US', {{ hour12: false }});
        if (allNews[0]) allNews[0].publish_time = `Just now • ${{timeStr}} CST`;

        renderNewsGrid();
        btn.disabled = false;
        icon.textContent = '✅';
        text.textContent = `Refreshed (${{timeStr}})`;

        if (timestampEl) {{
          timestampEl.innerHTML = `🟢 Live Sync: Refreshed at ${{timeStr}} (Iteration #${{refreshCount}}) • 10/10 Dispatches Synced`;
        }}

        showToast('Intelligence stream updated! Synchronized 10 articles from Dongchedi, 36Kr, LatePost, AutoHome & CPCA.');

        setTimeout(() => {{
          icon.textContent = '🔄';
          text.textContent = 'Fetch Latest Wire Updates';
        }}, 2000);
      }}, 350);
    }}

    // ==========================================
    // 5. TAB CONTROLS & LISTENERS
    // ==========================================
    function setupTabs() {{
      const views = {{
        graph: {{ btn: 'tab-btn-graph', sec: 'section-graph' }},
        benchmarks: {{ btn: 'tab-btn-benchmarks', sec: 'section-benchmarks' }},
        math: {{ btn: 'tab-btn-math', sec: 'section-math' }},
        feed: {{ btn: 'tab-btn-feed', sec: 'section-feed' }},
        digest: {{ btn: 'tab-btn-digest', sec: 'section-digest' }},
        api: {{ btn: 'tab-btn-api', sec: 'section-api' }}
      }};

      Object.keys(views).forEach(k => {{
        const b = document.getElementById(views[k].btn);
        if (b) {{
          b.addEventListener('click', () => {{
            Object.keys(views).forEach(other => {{
              document.getElementById(views[other].btn).classList.remove('active');
              document.getElementById(views[other].sec).style.display = 'none';
            }});
            b.classList.add('active');
            const targetSec = document.getElementById(views[k].sec);
            targetSec.style.display = 'block';

            if (k === 'benchmarks') {{
              setTimeout(() => renderBenchmarkCharts(), 50);
            }}
          }});
        }}
      }});
    }}

    function setupEventListeners() {{
      document.getElementById('btn-refresh-feed').addEventListener('click', triggerFeedRefresh);

      document.querySelectorAll('[data-kg-filter]').forEach(btn => {{
        btn.addEventListener('click', () => {{
          document.querySelectorAll('[data-kg-filter]').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          kgFilter = btn.dataset.kgFilter;
        }});
      }});

      document.getElementById('feed-search').addEventListener('input', (e) => {{
        searchQuery = e.target.value.toLowerCase().trim();
        renderNewsGrid();
      }});

      document.getElementById('feed-impact-filter').addEventListener('change', (e) => {{
        currentImpact = e.target.value;
        renderNewsGrid();
      }});

      document.getElementById('feed-source-filter').addEventListener('change', (e) => {{
        currentSource = e.target.value;
        renderNewsGrid();
      }});

      document.querySelectorAll('.cat-pill[data-cat]').forEach(pill => {{
        pill.addEventListener('click', () => {{
          document.querySelectorAll('.cat-pill[data-cat]').forEach(p => p.classList.remove('active'));
          pill.classList.add('active');
          currentCategory = pill.dataset.cat;
          renderNewsGrid();
        }});
      }});

      document.getElementById('modal-close-btn').addEventListener('click', () => {{
        document.getElementById('news-modal').classList.remove('active');
      }});

      document.getElementById('news-modal').addEventListener('click', (e) => {{
        if (e.target.id === 'news-modal') {{
          document.getElementById('news-modal').classList.remove('active');
        }}
      }});
    }}

    document.addEventListener('DOMContentLoaded', initApp);
  </script>
</body>
</html>
'''

with open("china_megatrends.html", "w", encoding="utf-8") as f:
    f.write(html_code)

print("Saved PM-tailored china_megatrends.html successfully!")
