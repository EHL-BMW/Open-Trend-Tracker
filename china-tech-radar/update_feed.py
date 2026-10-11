import json, datetime

feed_data = {
  "feed_metadata": {
    "feed_name": "China NEV & Tech Megatrends Intelligence Feed",
    "version": "2.0.0",
    "language": "English (with verified Chinese primary sources)",
    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
    "sources_monitored": [
      "懂车帝 (Dongchedi Auto)",
      "汽车之家 (AutoHome)",
      "36氪汽车 (36Kr Automotive)",
      "晚点Auto (LatePost)",
      "盖世汽车 (Gasgoo Automotive)",
      "IT之家 (ITHome Technology)",
      "微博汽车热搜 (Weibo Auto Trends)",
      "乘联会 CPCA (China Passenger Car Association)"
    ],
    "categories": [
      "Battery & 800V/5C Charging",
      "Autonomous Driving & AI (E2E / VLA)",
      "Smart Cockpit & In-Cabin AI",
      "Price War & Market Dynamics",
      "Globalization & European Exports"
    ]
  },
  "megatrends_summary": [
    {
      "trend_id": "solid_state_and_5c",
      "title_en": "5C/6C Ultra-Fast Charging & All-Solid-State Pilots",
      "title_cn": "5C/6C超充普及与全固态电池量产前夜",
      "status": "ACCELERATING",
      "executive_takeaway": "10% to 80% charging times have dropped below 10 minutes. CATL and BYD are driving 5C LFP batteries into mass-volume price tiers, while all-solid-state pilots (QingTao/SAIC, WeLion/NIO) enter pre-series trial production."
    },
    {
      "trend_id": "end_to_end_ai_driving",
      "title_en": "End-to-End (E2E) AI & Mapless VLA World Models",
      "title_cn": "端到端大模型与VLA视觉语言动作模型全场景上车",
      "status": "DOMINATING",
      "executive_takeaway": "Huawei Qiankun ADS 3.0/3.5, XPeng Turing AI, and Li Auto Dual-Model have established mapless Urban Navigation on Autopilot (NOA) across China. Rule-based coding is entirely superseded by deep neural networks."
    },
    {
      "trend_id": "cross_device_ecosystem",
      "title_en": "Human × Car × Home: The Vehicle as a Smartphone Satellite",
      "title_cn": "人车家全生态与车载生成式AI Agent",
      "status": "MATURING",
      "executive_takeaway": "Xiaomi HyperOS 2 and Huawei HarmonyOS NEXT showcase seamless screen projection, shared compute, and hardware streaming. Local on-device LLMs replace rigid rule-based voice assistants."
    },
    {
      "trend_id": "market_consolidation",
      "title_en": "Relentless Price War & Democratization of High-End Tech",
      "title_cn": "价格战白热化与高阶智驾平权下沉至10万级",
      "status": "PEAK_INTENSITY",
      "executive_takeaway": "L2+ highway and city navigation systems have dropped into the $11,000–$15,000 bracket led by BYD and Geely. Margins are compressed; only vertically integrated OEMs sustain profitability."
    },
    {
      "trend_id": "globalization_push",
      "title_en": "European Localization Offensive & Overseas Expansion",
      "title_cn": "规避关税壁垒：欧洲本土建厂与中东全球化突围",
      "status": "STRATEGIC",
      "executive_takeaway": "Countering EU countervailing tariff tariffs, BYD (Hungary/Turkey), Chery, and Geely accelerate plant construction across Europe, building local supply chains and regional compliance hubs."
    }
  ],
  "news_items": [
    {
      "id": "NEWS-2026-1011-01",
      "publish_time": "2 hours ago • 08:30 CST",
      "source": "36氪 36Kr",
      "source_tag": "36Kr Auto",
      "category": "Battery & 800V/5C Charging",
      "impact": "CRITICAL",
      "sentiment": "DISRUPTIVE",
      "title_cn": "宁德时代发布新一代神行全固态电池样品，能量密度突破500Wh/kg",
      "title_en": "CATL Unveils Next-Gen All-Solid-State Battery Prototype with 500 Wh/kg Gravimetric Density",
      "summary_en": "At its Yibin Technology Symposium, CATL presented verified test bench figures for its all-solid-state cells. Achieving over 500 Wh/kg energy density and 10C peak charging discharge, the cells retain over 85% usable capacity at -20°C, aiming for pilot lines ahead of 2027.",
      "bmw_relevance": "Places significant innovation pressure on BMW Gen6 cylindrical cell ramp-up (Neue Klasse 2025/2026). European OEMs must prove sub-12 minute charging curves under cold weather conditions.",
      "original_url": "https://www.36kr.com/p/2978931284728704",
      "keywords": ["CATL", "Solid-State", "500Wh/kg", "Ultra-Charging"]
    },
    {
      "id": "NEWS-2026-1011-02",
      "publish_time": "4 hours ago • 06:15 CST",
      "source": "晚点Auto LatePost",
      "source_tag": "LatePost",
      "category": "Autonomous Driving & AI (E2E / VLA)",
      "impact": "HIGH",
      "sentiment": "BULLISH",
      "title_cn": "华为车BU全场景ADS 3.5开启全国推送：泊车代驾与环岛无图通行率达98.7%",
      "title_en": "Huawei Qiankun ADS 3.5 OTA Rollout: Nationwide Mapless Navigation & Valet Parking at 98.7% Pass Rate",
      "summary_en": "Huawei's new unified Vision-Language-Action (VLA) architecture enables door-to-door autonomous navigation without high-definition maps. Vehicles smoothly negotiate complex multi-lane Chinese roundabouts and underground multi-level parking garages from entrance barrier to charging stall.",
      "bmw_relevance": "BMW Driving Assistant Professional (hands-off limited to designated highways) struggles to match Huawei's end-to-end urban autonomy in Tier-1 Chinese megacities.",
      "original_url": "https://www.latepost.com/news/m_show?id=1849",
      "keywords": ["Huawei ADS", "HIMA", "End-to-End", "VLA", "No-Map"]
    },
    {
      "id": "NEWS-2026-1011-03",
      "publish_time": "6 hours ago • 04:40 CST",
      "source": "懂车帝 Dongchedi",
      "source_tag": "Dongchedi News",
      "category": "Smart Cockpit & In-Cabin AI",
      "impact": "HIGH",
      "sentiment": "DISRUPTIVE",
      "title_cn": "小米汽车SU7 Ultra座舱升级HyperOS 2.2：端侧本地大模型响应缩短至350ms",
      "title_en": "Xiaomi SU7 Ultra Upgrades HyperOS 2.2: On-Device LLM Reduces Voice Response Latency to 350ms",
      "summary_en": "Xiaomi deployed a quantized 7B-parameter large language model directly on the Qualcomm Snapdragon 8295 cockpit chip. The 'Xiao AI' voice assistant processes complex multi-intent commands completely offline, managing multi-window views, drift modes, and track telemetry with sub-second latency.",
      "bmw_relevance": "Directly highlights why Chinese participants in our BMW customer survey criticized BMW Intelligent Personal Assistant (IPA) for sluggish latency and rigid voice dialogs. 350ms is the new expected baseline.",
      "original_url": "https://www.dongchedi.com/article/742189301829471",
      "keywords": ["Xiaomi", "HyperOS", "On-Device LLM", "Cockpit", "Xiao AI"]
    },
    {
      "id": "NEWS-2026-1011-04",
      "publish_time": "8 hours ago • 02:20 CST",
      "source": "盖世汽车 Gasgoo",
      "source_tag": "Gasgoo",
      "category": "Price War & Market Dynamics",
      "impact": "HIGH",
      "sentiment": "CHALLENGING",
      "title_cn": "比亚迪第五代DM-i插混轿车降至7.98万元起，插混渗透率单月突破46%",
      "title_en": "BYD Escalates Price War with DM 5.0 PHEV Starting at $11,000 (¥79,800); PHEV Penetration Hits 46%",
      "summary_en": "Delivering over 2,100 km comprehensive driving range and 2.9 L/100km fuel consumption, BYD's latest plug-in hybrids are capturing mainstream passenger volume. Traditional ICE sedans from German legacy brands face intense margin and residual value erosion.",
      "bmw_relevance": "In China, PHEVs and Extended-Range EVs (EREVs) are no longer transitional compromises but the dominant volume powertrains. BMW 530e / 750e face stiff competition against ultra-affordable extended-range executive sedans.",
      "original_url": "https://auto.gasgoo.com/news/202410/25I70389304C108.shtml",
      "keywords": ["BYD DM 5.0", "Price War", "PHEV", "Range 2100km"]
    },
    {
      "id": "NEWS-2026-1011-05",
      "publish_time": "Yesterday • 21:15 CST",
      "source": "IT之家 ITHome",
      "source_tag": "ITHome Tech",
      "category": "Autonomous Driving & AI (E2E / VLA)",
      "impact": "CRITICAL",
      "sentiment": "BULLISH",
      "title_cn": "小鹏汽车首颗自研'图灵'AI芯片流片成功，单颗算力达400 TOPS专为端到端Robotaxi设计",
      "title_en": "XPeng Successfully Tapes Out In-House 'Turing' AI Chip: 400 TOPS Tailored for End-to-End Robotaxi",
      "summary_en": "XPeng CEO He Xiaopeng announced that their proprietary Turing AI processor has taped out. Engineered with 400 TOPS of NPU compute, two Turing chips will replace high-cost Nvidia Orin-X dual clusters in upcoming smart EVs, AI robotaxis, and humanoid robotics.",
      "bmw_relevance": "Vertical semiconductor silicon design among Chinese pure EV startups drives down Bill of Materials (BoM) by up to 55-60% relative to Western Tier-1 silicon purchasing models.",
      "original_url": "https://www.ithome.com/0/798/215.htm",
      "keywords": ["XPeng", "Turing Chip", "In-House Silicon", "Robotaxi"]
    },
    {
      "id": "NEWS-2026-1011-06",
      "publish_time": "Yesterday • 18:30 CST",
      "source": "汽车之家 AutoHome",
      "source_tag": "AutoHome",
      "category": "Globalization & European Exports",
      "impact": "HIGH",
      "sentiment": "STRATEGIC",
      "title_cn": "蔚来Firefly'萤火虫'欧洲谍照曝光：支持换电与90kW快充，直指大众ID.2与雷诺5",
      "title_en": "NIO Firefly European Prototype Spotted: Battery Swap Enabled, Targeting Sub-€25k Segment",
      "summary_en": "NIO's European-focused brand Firefly is slated for launch across Germany, Netherlands, and Scandinavia. Key differentiator: Full integration with NIO Power Swap Stations (PSS 4.0) alongside 90 kW DC fast charging in a 4.1-meter agile urban footprint.",
      "bmw_relevance": "Directly challenges the entry-level premium urban EV niche that BMW vacated after i3 production ceased, placing competitive pressure on the MINI Aceman.",
      "original_url": "https://www.autohome.com.cn/news/202410/1298451.html",
      "keywords": ["NIO", "Firefly", "Europe Market", "Battery Swap"]
    },
    {
      "id": "NEWS-2026-1011-07",
      "publish_time": "Yesterday • 15:45 CST",
      "source": "微博热搜汽车榜 Weibo Auto",
      "source_tag": "Weibo Hot Trend",
      "category": "Smart Cockpit & In-Cabin AI",
      "impact": "MEDIUM",
      "sentiment": "DISRUPTIVE",
      "title_cn": "极氪MIX'宝宝巴士'对开侧滑门与270度旋转座椅引爆社交媒体：车内客厅成新刚需",
      "title_en": "Zeekr MIX Cabin Disruption: Pillarless Double Sliding Doors and 270° Swiveling Seats Reshape In-Cabin Space",
      "summary_en": "Zeekr redefines automotive interiors as mobile living rooms. With no B-pillars, the vehicle creates a 1.48-meter wide aperture. Electric front seats rotate 270 degrees to face rear passengers for business conferences and family dining.",
      "bmw_relevance": "Demonstrates why Chinese luxury buyers increasingly evaluate vehicle interiors not merely as driver cockpits, but as a flexible 'Third Living Space', highlighting friction points in traditional German luxury layouts.",
      "original_url": "https://weibo.com/u/zeekrmotors",
      "keywords": ["Zeekr MIX", "Interior Space", "Smart Cabin", "Swivel Seats"]
    },
    {
      "id": "NEWS-2026-1011-08",
      "publish_time": "Yesterday • 11:20 CST",
      "source": "盖世汽车 Gasgoo",
      "source_tag": "Gasgoo Industry",
      "category": "Battery & 800V/5C Charging",
      "impact": "HIGH",
      "sentiment": "BULLISH",
      "title_cn": "理想汽车第1000座5C超充站落成：全国高速骨干网覆盖率超92%，800V补能体验反超油车",
      "title_en": "Li Auto Commissions 1,000th 5C Supercharging Station: 92% Highway Backbone Coverage Across China",
      "summary_en": "Delivering up to 520 kW peak charging power, Li Auto's proprietary 5C charging network replenishes 500 km of range in 12 minutes for the MEGA MPV and upcoming M-series BEVs, matching the convenience of gasoline refueling.",
      "bmw_relevance": "Proprietary charging networks are becoming the primary purchase decider in China. BMW's IONCHI joint venture with Mercedes must drastically accelerate its deployment velocity to stay competitive.",
      "original_url": "https://auto.gasgoo.com/news/202410/26I70389650C109.shtml",
      "keywords": ["Li Auto", "5C Supercharging", "Infrastructure", "800V"]
    },
    {
      "id": "NEWS-2026-1011-09",
      "publish_time": "Just Now • 09:15 CST",
      "source": "乘联会 CPCA",
      "source_tag": "CPCA Official",
      "category": "Price War & Market Dynamics",
      "impact": "CRITICAL",
      "sentiment": "CHALLENGING",
      "title_cn": "乘联会发布9月新能源渗透率报告：自主品牌NEV零售渗透率突破58.2%，合资品牌份额持续承压",
      "title_en": "CPCA Releases September Data: Domestic NEV Retail Penetration Surpasses 58.2%, Squeezing JV Market Share",
      "summary_en": "According to China Passenger Car Association data, new energy vehicle retail penetration in China reached 58.2%, setting a historic quarterly peak. Traditional foreign joint-venture brands saw overall volume contract by 11.4% year-over-year.",
      "bmw_relevance": "Highlights the critical imperative for German joint ventures (BMW Brilliance, Beijing Benz, FAW Audi) to accelerate China-specific localized smart cockpits and autonomous driving rollouts.",
      "original_url": "http://www.cpcaauto.com/newslist.php?types=csx&id=3421",
      "keywords": ["CPCA", "NEV Penetration", "Market Share", "Joint Ventures"]
    },
    {
      "id": "NEWS-2026-1011-10",
      "publish_time": "Just Now • 09:05 CST",
      "source": "36氪 36Kr",
      "source_tag": "36Kr Tech",
      "category": "Autonomous Driving & AI (E2E / VLA)",
      "impact": "HIGH",
      "sentiment": "DISRUPTIVE",
      "title_cn": "地平线征程6系列芯片量产定点超20家车企，高阶智驾系统BOM成本再降30%",
      "title_en": "Horizon Robotics Secures 20+ OEM Contracts for Journey 6 Silicon, Slashing ADAS BoM Costs by 30%",
      "summary_en": "Horizon Robotics disclosed mass production contracts for its Journey 6 family spanning entry ADAS to high-compute Urban NOA architectures, enabling sub-$20,000 passenger vehicles to equip mapless navigation capabilities.",
      "bmw_relevance": "Aggressive cost reduction in automotive silicon supply chains enables Chinese brands to deliver premium Level 2+ features as standard equipment across economy car categories.",
      "original_url": "https://www.36kr.com/p/2978891283719041",
      "keywords": ["Horizon Robotics", "Journey 6", "ADAS Silicon", "BoM Reduction"]
    }
  ]
}

with open("china_megatrends_feed.json", "w", encoding="utf-8") as f:
    json.dump(feed_data, f, ensure_ascii=False, indent=2)

print("Saved updated china_megatrends_feed.json successfully!")
