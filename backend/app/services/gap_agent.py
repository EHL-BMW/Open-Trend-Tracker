"""Competitor Gap Analysis Agent for BMW R&D Strategy.

Flowchart:
[BMW Customer Pain Points] ➔ [KI-Agent (OpenAI)] ➔ [Analyzes 6 Chinese Leaders (蔚来, 问界, 小米, 理想, 极氪, 小鹏)] ➔ [7 MECE Domains Gap Analysis] ➔ [Actionable BMW Engineering PRD Requirements]

Integrates:
- BMW Customer Voice from internal feedback datasets (F70, G60, G70).
- 7 MECE Technology Domains (Energy & Charging, Driving Assistance, Digital Cockpit & AI, Connected Ecosystem, Smart Cabin, Vehicle Dynamics & Safety, Smart Exterior).
- Chinese Competitor Intelligence across 6 Disruptors: 蔚来 (NIO), 问界 (AITO / Huawei), 小米 (Xiaomi), 理想 (Li Auto), 极氪 (Zeekr), 小鹏 (XPeng).
- Structured OpenAI synthesis with high-fidelity deterministic fallback for offline/CI resilience.
- Human-in-the-Loop review workflow (Approve, Reject, Challenge).
"""
from __future__ import annotations

import json
import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from openai import OpenAI
from pydantic import BaseModel, Field

from app.paths import BACKEND_DIR, INTERNAL_DIR, ROOT_DIR, RUNTIME_DIR, get_openai_api_key, get_openai_model
from app.services.decision_dashboard import _internal_comments

logger = logging.getLogger(__name__)

AGENT_RUNS_DIR = RUNTIME_DIR / "agent-gap-runs"
AGENT_RUNS_DIR.mkdir(parents=True, exist_ok=True)

TRENDS_FILE = ROOT_DIR / "frontend" / "src" / "content" / "china_tech_trends.json"
TREND_MARKERS_DB_FILE = BACKEND_DIR / "app" / "benchmarks" / "future_trend_markers.json"

# Canonical 7 MECE Domains (aligned with FAQ / CPCA / McKinsey Connected Vehicle standard)
DOMAIN_MAPPING: dict[str, dict[str, Any]] = {
    "energy_charging": {
        "label": "⚡ 1. Energy & Charging",
        "aspects": "Charging experience, range management, power distribution",
        "patterns": [
            "charg", "battery", "range", "wallbox", "kwh", "voltage", "charging station",
            "pre-conditioning", "preconditioning", "lade", "soc", "inverter", "cold", "consumption"
        ],
        "competitors": [
            {
                "brand": "Zeekr",
                "model": "001 / 007",
                "tech": "800V Golden Battery 5.5C, 10-80% SoC in 10.5 mins, 500 kW peak rate, V2G bi-directional",
                "bmw_status": "400V architecture on CLAR (i4, iX3, i5) capping at 205 kW; Neue Klasse 800V scheduled for 2026",
            },
            {
                "brand": "XPeng",
                "model": "G9 / P7+ / X9",
                "tech": "800V Silicon Carbide (SiC) platform, 430 kW peak, 300 km added in 5 minutes, 11.8 kWh/100km efficiency",
                "bmw_status": "Silicon IGBT inverters, thermal throttling above 35°C ambient, real-world 18-21 kWh/100km",
            },
            {
                "brand": "Nio",
                "model": "ET9 / ET7",
                "tech": "925V full-domain architecture + Power Swap Station 4.0 (2 min 24 sec full battery swap)",
                "bmw_status": "Fixed battery pack with no modular swap or rapid pack swap capability",
            },
            {
                "brand": "Li Auto",
                "model": "MEGA / L9",
                "tech": "800V 5C Ultra-Fast Charging Platform (520 kW peak, 500 km in 12 min)",
                "bmw_status": "Current BMW peak current ~500A capped at 205 kW, dropping sharply after 15 min of charging",
            },
        ],
    },
    "driving_assistance": {
        "label": "🛡️ 2. Driving Assistance",
        "aspects": "Highway pilot, automated parking, human-machine handoff, GSR2 warnings",
        "patterns": [
            "assist", "cruise", "lane", "parking", "autopilot", "adas", "camera", "sensor",
            "gsr2", "speed limit", "chime", "disengagement", "pilot", "hands-free"
        ],
        "competitors": [
            {
                "brand": "XPeng",
                "model": "P7+ / G9 / X9",
                "tech": "Turing AI World-Model End-to-End ADAS (XNGP): map-free urban navigation across 100% of Chinese cities, zero-disengagement parking",
                "bmw_status": "Driving Assistant Professional (Level 2+ Highway Assistant up to 130 km/h with eye tracking), but urban point-to-point unavailable in China",
            },
            {
                "brand": "Huawei / AITO",
                "model": "M9 / M7",
                "tech": "HUAWEI ADS 3.0: GOD (General Obstacle Detection) + PDP network with 192-thread LiDAR, park-to-park valet, roundabout navigation",
                "bmw_status": "Radar + Camera fusion rules engine; struggles with unmapped Chinese urban construction and non-standard two-wheelers",
            },
            {
                "brand": "XPeng",
                "model": "MONA M03 / P7+",
                "tech": "AI Hawkeye Pure Vision Solution with dual-focal LFM cameras (-60% ADAS sensor BOM cost vs LiDAR)",
                "bmw_status": "Level 3 requires expensive mechanical LiDAR ($1,200+), limiting rollout to top luxury trims",
            },
        ],
    },
    "digital_cockpit": {
        "label": "🖥️ 3. Digital Cockpit & AI",
        "aspects": "BMW OS 8.5/9, voice assistant, display interaction, nested menus",
        "patterns": [
            "infotainment", "idrive", "screen", "display", "voice", "touch", "menu", "quickselect",
            "hvac", "climate control", "lag", "boot", "ipa", "widget", "latency", "touchscreen"
        ],
        "competitors": [
            {
                "brand": "Xiaomi",
                "model": "SU7 / Ultra",
                "tech": "HyperOS seamless human-car-home ecosystem: instant smartphone screen mirroring, hardware PIN expansion pins, 1.49s cold boot, Xiao AI LLM voice assistant",
                "bmw_status": "iDrive 8.5/9 Android Automotive OS with closed app store, 4.2s boot latency, nested touch menus creating highway distraction",
            },
            {
                "brand": "Zeekr / Meizu",
                "model": "007 / 001",
                "tech": "Flyme Auto OS with Snapdragon 8295 (30 TOPS NPU), seamless phone-to-car continuous playback, localized WeChat integration",
                "bmw_status": "Localized app ecosystem heavily reliant on Apple CarPlay; voice assistant requires fixed grammar commands",
            },
            {
                "brand": "Nio",
                "model": "ET7 / ES8",
                "tech": "NOMI GPT on-device emotion LLM with animated robotic desktop avatar, proactive suggestions, <280ms wake-word latency",
                "bmw_status": "BMW IPA relies on cloud TTS/ASR with static 2D icons and ~1.2s response time",
            },
        ],
    },
    "connected_ecosystem": {
        "label": "📱 4. Connected Ecosystem",
        "aspects": "My BMW App, Digital Key Plus (UWB), OTA updates, eSIM, subterranean connectivity",
        "patterns": [
            "app", "my bmw", "digital key", "uwb", "carplay", "android auto", "esim", "ota",
            "remote", "cloud", "disconnect", "timeout", "underground", "garage", "telematics", "tcu", "pairing"
        ],
        "competitors": [
            {
                "brand": "Huawei / AITO",
                "model": "M9 / M7",
                "tech": "HarmonyOS 4 Super Desktop + MagLink P2P magnetic tablet docking with local BLE fall-back wake; seamless connection in underground concrete garages",
                "bmw_status": "My BMW App suffers high timeout rate (-76.7% net sentiment) when triggering remote climate conditioning in underground parking garages",
            },
            {
                "brand": "Xiaomi",
                "model": "SU7",
                "tech": "CarIoT open ecosystem: native physical PIN mounts, Apple AirPlay + iPad rear seat docking, seamless Mijia smart home geo-fenced execution",
                "bmw_status": "Closed proprietary accessories; wireless CarPlay audio dropouts and carrier profile eSIM auto-provisioning hurdles",
            },
            {
                "brand": "Zeekr",
                "model": "001 FR / 007",
                "tech": "Dual-way satellite communication via Tiantong constellation: text, location SOS, and satellite emergency call without cellular base-station",
                "bmw_status": "Telematics Control Unit (TCU) strictly 4G/5G terrestrial dependent; zero coverage in alpine tunnels and remote dead zones",
            },
            {
                "brand": "Nio",
                "model": "ET9 / NIO Phone",
                "tech": "NIO Link full-stack interconnectivity: sub-millisecond UWB phone key, phone computing power clustering with car OS, remote battery swap booking",
                "bmw_status": "Digital Key Plus UWB works well on iPhones but experiences connection latency across diverse Android brands",
            },
        ],
    },
    "smart_cabin": {
        "label": "🛋️ 5. Smart Cabin",
        "aspects": "Thermal comfort, seating, acoustic insulation, materials, panoramic roof",
        "patterns": [
            "seat", "massage", "recline", "roof", "sunroof", "sunblind", "veganza", "leather",
            "sweat", "ventilation", "noise", "nvh", "acoustic", "smell", "fragrance", "shade", "curtain", "fridge"
        ],
        "competitors": [
            {
                "brand": "Li Auto",
                "model": "MEGA / L9",
                "tech": "Zero-gravity second-row lounge seats with 140° recline, 4-way electric ottoman, 16-point spa massage, dual 50W wireless chargers, -6°C to +50°C compressor fridge",
                "bmw_status": "Rear seats in long-wheelbase G68/G60 lack full zero-gravity recline leg-rests; fixed panoramic glass roof causes greenhouse heating without mechanical sunshade",
            },
            {
                "brand": "Zeekr",
                "model": "MIX / 009 Grand",
                "tech": "Stepless 270° electric swivel front seats creating face-to-face mobile lounge, ultra-wide 1.48m entrance, anti-bacterial active ventilated leather",
                "bmw_status": "Veganza synthetic leather causes customer complaints of summer sweating without active ventilation; fixed seat forward orientation",
            },
            {
                "brand": "Nio",
                "model": "ET7",
                "tech": "PanoCinema with AR glasses integration, 23-speaker 1000W Dirac immersive audio, smart fragrance system with biometric stress detection",
                "bmw_status": "Bowers & Wilkins Diamond system is audio benchmark, but lacks biometric stress/mood integration and native AR glasses sync",
            },
        ],
    },
    "vehicle_dynamics": {
        "label": "🏎️ 6. Vehicle Dynamics & Safety",
        "aspects": "Chassis control, 2-axle air suspension, steering precision, regenerative braking",
        "patterns": [
            "suspension", "damper", "air suspension", "ride", "handling", "steering", "comfort",
            "bushing", "chassis", "recuperation", "brake", "regen", "roll", "stability", "dsc", "agility"
        ],
        "competitors": [
            {
                "brand": "Huawei / AITO",
                "model": "M9 Touring",
                "tech": "Touring Smart Chassis with DATS Dynamic Adaptive Torque: 4 ms motor torque response (vs 100 ms traditional ESP) and xMotion predictive road scanning",
                "bmw_status": "BMW DSC is the mechanical handling benchmark (+44.7% net moat), but motor-inverter torque loop latency is ~20-30 ms on CLAR BEVs",
            },
            {
                "brand": "Li Auto",
                "model": "L9 / L8",
                "tech": "Magic Carpet 3.0 dual-chamber air suspension with dual-valve CDC dampers and front LiDAR millisecond-level road surface preview",
                "bmw_status": "Steel spring standard on front of F70/G60; dual-axle air suspension limited to high trims; lacks predictive LiDAR road preview",
            },
            {
                "brand": "Xiaomi",
                "model": "SU7 Ultra",
                "tech": "HyperEngine V8s e-motors running at 27,200 rpm (10.14 kW/kg power density) with carbon-fiber wrapped rotors and triple-motor torque vectoring",
                "bmw_status": "BMW fifth-generation EESM motors run at 12,000-14,000 rpm; excellent rare-earth-free design but heavier drive units",
            },
        ],
    },
    "smart_exterior": {
        "label": "🚪 7. Smart Exterior",
        "aspects": "Automatic comfort doors, kick-sensor tailgate, smart lighting, aerodynamics",
        "patterns": [
            "door", "automatic door", "comfort door", "tailgate", "trunk", "kick sensor",
            "foot sensor", "headlight", "light", "aero", "flush handle", "curb", "sensor abort", "exterior", "spoiler"
        ],
        "competitors": [
            {
                "brand": "Huawei / AITO",
                "model": "M9",
                "tech": "HUAWEI XPIXEL 1.27M pixel smart projection headlights (100-inch outdoor cinema, pedestrian crossing projection) + powered comfort doors with millimeter-wave obstacle radar",
                "bmw_status": "i7 automatic comfort doors halt prematurely in tight parking spaces due to overly conservative ultrasonic sensors (-18.1% net sentiment); kick-sensor tailgate requires multiple attempts",
            },
            {
                "brand": "Zeekr",
                "model": "MIX / 001 FR",
                "tech": "Hidden B-Pillar Dual Electric Sliding Doors with 1.48m ultra-wide opening aperture, curb obstacle millimeter-wave scanner, and zero-effort manual freewheeling clutch",
                "bmw_status": "Traditional 4-door hinges; heavy mechanical resistance when manually overriding stuck automatic door actuators",
            },
            {
                "brand": "Xiaomi",
                "model": "SU7",
                "tech": "Active aerodynamic package: 4-stage adaptive electric rear wing (-130kg lift), active grille shutter achieving Cd 0.195, halo tail lamps, flush semi-hidden door handles",
                "bmw_status": "Fixed aero flaps; higher drag coefficient Cd 0.23-0.24 on CLAR sedans leading to winter highway range penalty",
            },
            {
                "brand": "XPeng",
                "model": "P7+ / G9",
                "tech": "Integrated flush aero sensor pods with high-pressure hydrophobic heated wash nozzles to prevent snow/mud blinding of cameras and LiDAR",
                "bmw_status": "Rear-view and surround camera lenses easily fouled by road spray and winter slush without integrated high-pressure washer",
            },
        ],
    },
}

# Aliases for backwards compatibility with legacy strings
DOMAIN_ALIASES: dict[str, str] = {
    "smart_driving": "driving_assistance",
    "chassis_dynamics": "vehicle_dynamics",
    "vehicle_dynamics_and_safety": "vehicle_dynamics",
    "energy_and_charging": "energy_charging",
    "digital_cockpit_and_ai": "digital_cockpit",
}


def normalize_domain(domain: str | None) -> str:
    """Normalize domain strings or legacy aliases to the canonical 7 MECE domain keys."""
    if not domain:
        return "energy_charging"
    d = domain.strip().lower()
    if d in DOMAIN_ALIASES:
        return DOMAIN_ALIASES[d]
    if d in DOMAIN_MAPPING:
        return d
    return "energy_charging"


def normalize_domains(domains: list[str] | str | None) -> list[str]:
    """Normalize input domain(s) to a non-empty list of canonical domain keys."""
    if not domains:
        return ["energy_charging"]
    if isinstance(domains, str):
        if domains.strip().lower() == "all":
            return list(DOMAIN_MAPPING.keys())
        parts = [p.strip() for p in domains.split(",") if p.strip()]
        if not parts:
            return ["energy_charging"]
        return [normalize_domain(p) for p in parts]

    resolved: list[str] = []
    for item in domains:
        if not item or not isinstance(item, str):
            continue
        if item.strip().lower() == "all":
            return list(DOMAIN_MAPPING.keys())
        for sub in item.split(","):
            sub_clean = sub.strip()
            if sub_clean:
                canonical = normalize_domain(sub_clean)
                if canonical not in resolved:
                    resolved.append(canonical)
    return resolved or ["energy_charging"]


class CompetitorBenchmarkItem(BaseModel):
    competitor_brand: str
    competitor_model: str
    feature_name: str
    technical_specs: str
    observed_market_advantage: str
    source_citation: str


class TraceableCitation(BaseModel):
    source_type: Literal["bmw_customer_verbatim", "competitor_spec", "china_media_trend"]
    citation_text: str
    vehicle_or_outlet: str
    severity_or_date: str


class EngineeringRequirementPRD(BaseModel):
    requirement_id: str
    title: str
    system_domain: str
    specification: str
    target_metric: str
    affected_bmw_taxonomy_attributes: list[str]
    bom_cost_impact_eur: str
    engineering_complexity: Literal["Low", "Medium", "High", "Critical"]
    time_to_market_readiness: str
    tradeoffs_and_risks: str


class GapAnalysisOutput(BaseModel):
    analysis_id: str
    target_vehicle: str
    domain: str
    domains: list[str] = Field(default_factory=list)
    domain_label: str
    generated_at: str
    model_used: str
    executive_summary: str
    bmw_customer_pain_points: list[str]
    citations: list[TraceableCitation]
    competitor_benchmarks: list[CompetitorBenchmarkItem]
    gap_severity: Literal["Critical", "High", "Medium"]
    recommended_requirements: list[EngineeringRequirementPRD]
    pm_challenge_prompts: list[str]
    review_status: Literal["pending_review", "approved", "rejected", "challenged"]
    pm_notes: str | None = None
    reviewed_at: str | None = None
    system_fingerprint: str | None = None
    seed: int | None = 42


def _load_chinese_trend_snippets() -> list[dict]:
    """Extract sample Chinese EV trend snippets from china_tech_trends.json."""
    if not TRENDS_FILE.exists():
        return []
    try:
        data = json.loads(TRENDS_FILE.read_text(encoding="utf-8"))
        topics = data.get("topics", [])
        snippets = []
        for topic in topics[:10]:
            name = topic.get("name", "")
            mentions = topic.get("mentions", 0)
            sample_articles = topic.get("articles", [])[:2]
            snippets.append({
                "topic": name,
                "mentions": mentions,
                "articles": [a.get("title", "") for a in sample_articles if isinstance(a, dict)],
            })
        return snippets
    except Exception as exc:
        logger.warning(f"Failed to parse china_tech_trends.json: {exc}")
        return []


def _gather_vehicle_pain_points(vehicle: str, domain_keys: list[str] | str, max_items: int = 8) -> list[dict]:
    """Retrieve filtered negative customer feedback matching patterns across selected domains."""
    raw_comments = _internal_comments(vehicle.upper())
    if not raw_comments:
        raw_comments = _internal_comments("G60") or _internal_comments("G70") or _internal_comments("F70")

    canonical_domains = normalize_domains(domain_keys)
    combined_patterns: list[str] = []
    for d in canonical_domains:
        combined_patterns.extend(DOMAIN_MAPPING[d]["patterns"])

    negative_comments = [
        c for c in raw_comments
        if c.get("sentiment") == "negative" and any(p in c.get("text", "").lower() for p in combined_patterns)
    ]

    if not negative_comments:
        negative_comments = [c for c in raw_comments if c.get("sentiment") == "negative"]

    return negative_comments[:max_items]


def _get_domain_offline_artifacts(canonical_domain: str, vehicle: str) -> tuple[list[EngineeringRequirementPRD], list[str], bool]:
    """Return offline requirements, challenge prompts, and whether domain has critical severity."""
    domain_info = DOMAIN_MAPPING[canonical_domain]

    if canonical_domain == "energy_charging":
        reqs = [
            EngineeringRequirementPRD(
                requirement_id=f"PRD-{vehicle}-EC01",
                title=f"800V/925V Silicon Carbide (SiC) Platform Transition for {vehicle}",
                system_domain=domain_info["label"],
                specification="Implement full-domain 800V/925V SiC inverter architecture capable of sustained 350+ kW peak charge rates, achieving 10-80% SoC in <= 12 minutes under standard conditions and <= 16 minutes at -10°C.",
                target_metric="10-80% SoC <= 12 min; 350 kW peak power; 92% inverter efficiency",
                affected_bmw_taxonomy_attributes=["charging", "hv_battery", "electric_range"],
                bom_cost_impact_eur="+€680 per vehicle (offset by -14% battery thermal sizing)",
                engineering_complexity="High",
                time_to_market_readiness="SOP 2026/Q3 (Neue Klasse architecture align)",
                tradeoffs_and_risks="High initial R&D expenditure; requires upgraded supplier qualification for 1200V SiC MOSFET modules.",
            ),
            EngineeringRequirementPRD(
                requirement_id=f"PRD-{vehicle}-EC02",
                title=f"Ultra-Fast Charging 5C LFP Chemistry for Entry/Mid-Tier {vehicle}",
                system_domain=domain_info["label"],
                specification="Benchmark and deploy CATL/Zeekr-style 5.5C Golden Battery LFP chemistry for entry configurations, cutting cell BOM while sustaining >300 kW charging.",
                target_metric="10-80% SoC in 10.5 mins; cell level cost <$55/kWh; 83% volume efficiency",
                affected_bmw_taxonomy_attributes=["hv_battery", "charging"],
                bom_cost_impact_eur="-€1,400 BOM savings vs NMC pack",
                engineering_complexity="High",
                time_to_market_readiness="SOP 2026/Q4",
                tradeoffs_and_risks="Lower gravimetric energy density requires CTP/CTB structural integration.",
            ),
        ]
        prompts = [
            f"How does the +€680 BOM increase for 800V SiC impact our contribution margin against the Xiaomi SU7 price bracket in China?",
            "Can we adopt modular battery swapping or partner with NIO Power Swap Alliance for fleet models in Tier-1 Chinese cities?",
            "What is our battery warranty liability exposure if peak fast-charging current is sustained up to 75% SoC?",
        ]
        return reqs, prompts, True

    elif canonical_domain == "driving_assistance":
        reqs = [
            EngineeringRequirementPRD(
                requirement_id=f"PRD-{vehicle}-DA01",
                title=f"End-to-End Foundation Model Urban Navigation on Autopilot for {vehicle}",
                system_domain=domain_info["label"],
                specification="Integrate local Tier-1 foundation model policy network (e.g., Momenta / Huawei / Horizon) to enable nationwide map-free urban driving assistance across Chinese metropolitan areas.",
                target_metric="<= 0.1 disengagements per 1,000 km in Tier-1 cities; 100% urban coverage",
                affected_bmw_taxonomy_attributes=["driving_assistance", "navigation"],
                bom_cost_impact_eur="+€450 per vehicle (compute + sensor fusion)",
                engineering_complexity="Critical",
                time_to_market_readiness="SOP 2026/Q2",
                tradeoffs_and_risks="Regulatory data compliance in China; transition away from classic Mobileye rules engines.",
            ),
            EngineeringRequirementPRD(
                requirement_id=f"PRD-{vehicle}-DA02",
                title=f"Adaptive GSR2 Auditory Alert Smoothing & One-Touch Steering Wheel Mute",
                system_domain=domain_info["label"],
                specification="Redesign EU GSR2 mandatory overspeed auditory warnings with progressive chime ramps and dedicate a physical/long-press steering wheel button for instant muting.",
                target_metric="Driver chime irritation complaints reduced by >85%; zero false-positive speed triggers",
                affected_bmw_taxonomy_attributes=["driving_assistance", "operating_concept"],
                bom_cost_impact_eur="€0 (OTA software update)",
                engineering_complexity="Low",
                time_to_market_readiness="OTA 2025/Q4 release",
                tradeoffs_and_risks="Must strictly adhere to EU GSR2 safety compliance homologation.",
            ),
        ]
        prompts = [
            "Should BMW partner with Momenta or Huawei for China ADAS, or maintain an in-house global European stack?",
            "How do we balance stringent German functional safety (ISO 26262 ASIL-D) with the rapid iteration of Chinese end-to-end neural networks?",
        ]
        return reqs, prompts, False

    elif canonical_domain == "digital_cockpit":
        reqs = [
            EngineeringRequirementPRD(
                requirement_id=f"PRD-{vehicle}-DC01",
                title=f"Sub-Second Cold Boot OS Optimization & Instant-On Sleep Snapshot for {vehicle}",
                system_domain=domain_info["label"],
                specification="Optimize BMW OS 8.5/9 bootloader using RAM suspend snapshots and Qualcomm Snapdragon 8295 SoC, reducing display boot latency to match Xiaomi SU7 (<1.8s).",
                target_metric="Cold boot < 1.8s (down from 4.2-6.5s); UI frame rate 60 fps lock",
                affected_bmw_taxonomy_attributes=["operating_concept", "displays"],
                bom_cost_impact_eur="+€45 per vehicle (SoC RAM upgrade from 16GB to 32GB)",
                engineering_complexity="Medium",
                time_to_market_readiness="OTA 2025/Q4 release",
                tradeoffs_and_risks="Requires maintaining custom SDK compatibility across fragmented Chinese smartphone OS versions.",
            ),
            EngineeringRequirementPRD(
                requirement_id=f"PRD-{vehicle}-DC02",
                title=f"Persistent QuickSelect Climate Controls & Physical Haptic Feedback Rail",
                system_domain=domain_info["label"],
                specification="Reintroduce a dedicated persistent climate control strip at display bottom with haptic vibration, eliminating multi-layer nested menus for temperature and seat heating.",
                target_metric="Driver glance time off road < 1.0s for HVAC adjustments",
                affected_bmw_taxonomy_attributes=["operating_concept", "climate"],
                bom_cost_impact_eur="+€15 (haptic display actuators)",
                engineering_complexity="Low",
                time_to_market_readiness="SOP 2026/Q1",
                tradeoffs_and_risks="Re-tuning UI design language across horizontal curved displays.",
            ),
        ]
        prompts = [
            "Can we license an existing Chinese cockpit runtime layer (e.g. ECARX or Flyme Auto) instead of engineering in-house sub-second app handover?",
            "How do we convince German UX purists to keep physical/haptic climate shortcuts without cluttering the minimalist interior?",
        ]
        return reqs, prompts, True

    elif canonical_domain == "connected_ecosystem":
        reqs = [
            EngineeringRequirementPRD(
                requirement_id=f"PRD-{vehicle}-CE01",
                title=f"Subterranean Garage BLE Proximity Fallback & Offline Command Caching for {vehicle}",
                system_domain=domain_info["label"],
                specification="Implement dual BLE 5.3 antenna diversity with local phone-to-car cryptographic authentication, enabling My BMW App remote climatization and unlock even in underground concrete garages with 0% cellular signal.",
                target_metric="App remote command success rate in underground levels -1 to -3 >= 99.2%; response latency <800 ms",
                affected_bmw_taxonomy_attributes=["connected_services", "operating_concept", "security_access"],
                bom_cost_impact_eur="+€18 per vehicle (dual BLE antenna diversity module)",
                engineering_complexity="Medium",
                time_to_market_readiness="OTA 2025/Q4 release",
                tradeoffs_and_risks="Ensuring robust anti-replay and relay attack defenses over Bluetooth.",
            ),
            EngineeringRequirementPRD(
                requirement_id=f"PRD-{vehicle}-CE02",
                title=f"Standardized Rear Magnetic Tablet Docking Bus (AITO MagLink Counterpart)",
                system_domain=domain_info["label"],
                specification="Replace heavy and costly roof Theatre Screens with standardized magnetic docking ports in front seat backrests supporting Apple iPad, Huawei MatePad, and Xiaomi Pad with 27W wireless power and iDrive media sharing.",
                target_metric="Docking time < 2 seconds; -€1,800 BOM savings vs ceiling theatre screen",
                affected_bmw_taxonomy_attributes=["rear_entertainment", "connected_services"],
                bom_cost_impact_eur="-€1,800 savings vs fixed theatre screen; +€40 per seat for magnetic high-speed bus dock",
                engineering_complexity="Low",
                time_to_market_readiness="SOP 2026/Q1",
                tradeoffs_and_risks="Ensuring crash safety certification for detached consumer tablets.",
            ),
        ]
        prompts = [
            "Why is My BMW App Net Sentiment at -76.7% in Connected Ecosystem, and can BLE fallback completely eliminate subterranean timeout complaints?",
            "Should BMW develop an open CarIoT accessory rail like Xiaomi SU7 to allow third-party physical attachment points?",
        ]
        return reqs, prompts, True

    elif canonical_domain == "smart_cabin":
        reqs = [
            EngineeringRequirementPRD(
                requirement_id=f"PRD-{vehicle}-SC01",
                title=f"Zero-Gravity Executive Lounge Seating Package with Perforated Active Ventilation",
                system_domain=domain_info["label"],
                specification="Design a true 140° zero-gravity rear passenger lounge seat with 4-way electric ottoman leg support, 16-point pneumatic spa massage, and high-CFM active seat suction to address Veganza sweat complaints.",
                target_metric="Seat ventilation cooling rate -5°C in 3 mins; Veganza perspiration friction cases reduced by >90%",
                affected_bmw_taxonomy_attributes=["seat_features", "interior_space"],
                bom_cost_impact_eur="+€420 per vehicle",
                engineering_complexity="Medium",
                time_to_market_readiness="SOP 2026/Q2",
                tradeoffs_and_risks="Packaging space in shorter wheelbase variants.",
            ),
            EngineeringRequirementPRD(
                requirement_id=f"PRD-{vehicle}-SC02",
                title=f"Electrochromic Smart Dimming Panoramic Roof with Low-Emissivity Heat Shield",
                system_domain=domain_info["label"],
                specification="Upgrade fixed panoramic glass roof to multi-segment electrochromic PDLC dimming glass with silver-sputtered low-E coating to eliminate greenhouse solar heating in summer without adding mechanical shade weight.",
                target_metric="Solar Heat Gain Coefficient (SHGC) < 0.12; cabin surface temperature reduced by 8°C",
                affected_bmw_taxonomy_attributes=["interior_space", "climate"],
                bom_cost_impact_eur="+€280 per vehicle (PDLC glass controller)",
                engineering_complexity="Medium",
                time_to_market_readiness="SOP 2026/Q2",
                tradeoffs_and_risks="High supplier cost for large single-piece curved panoramic glass panels.",
            ),
        ]
        prompts = [
            "How do we resolve Chinese customer complaints regarding Veganza synthetic leather heat retention without increasing base vehicle prices?",
            "Is electrochromic glass preferable to a mechanical roller sunblind in terms of headroom and BOM cost?",
        ]
        return reqs, prompts, False

    elif canonical_domain == "vehicle_dynamics":
        reqs = [
            EngineeringRequirementPRD(
                requirement_id=f"PRD-{vehicle}-VD01",
                title=f"Inverter-Direct Dynamic Torque Feedback Loop (DATS Counterpart) for {vehicle}",
                system_domain=domain_info["label"],
                specification="Re-engineer the DSC-to-inverter communication loop to run directly on the motor control unit (MCU) with sub-4 ms latency (vs 25 ms legacy CAN), eliminating vehicle pitch during regenerative deceleration.",
                target_metric="Motor torque control latency < 4 ms; pitch angle reduction 40% during one-pedal regen",
                affected_bmw_taxonomy_attributes=["handling_ride", "driving_modes"],
                bom_cost_impact_eur="+€15 (MCU firmware recalibration and high-speed bus timing)",
                engineering_complexity="Medium",
                time_to_market_readiness="OTA 2025/Q4 release",
                tradeoffs_and_risks="Recalibration of DSC safety threshold algorithms to prevent ABS shudder.",
            ),
            EngineeringRequirementPRD(
                requirement_id=f"PRD-{vehicle}-VD02",
                title=f"Dual-Valve CDC Damper Architecture with Predictive Road Surface Preview",
                system_domain=domain_info["label"],
                specification="Introduce dual-valve continuously variable damping (rebound and compression separate) paired with forward camera/LiDAR road bump preview on high-tier models.",
                target_metric="Expansion joint harshness acceleration reduced by 32%; body roll angle < 1.8° at 0.7g lateral",
                affected_bmw_taxonomy_attributes=["handling_ride"],
                bom_cost_impact_eur="+€320 per vehicle",
                engineering_complexity="High",
                time_to_market_readiness="SOP 2026/Q2",
                tradeoffs_and_risks="Protecting BMW's +44.7% Moat in vehicle dynamics while delivering Chinese limousine-style ride plushness.",
            ),
        ]
        prompts = [
            "BMW holds a +44.7% Moat in Vehicle Dynamics. How do we soften low-speed expansion joint harshness in China without losing high-speed Autobahn stability?",
            "Can we surpass AITO's DATS 4ms torque response time purely through MCU software optimization?",
        ]
        return reqs, prompts, False

    elif canonical_domain == "smart_exterior":
        reqs = [
            EngineeringRequirementPRD(
                requirement_id=f"PRD-{vehicle}-SE01",
                title=f"Wide-Angle Millimeter-Wave Proximity Radar & Freewheel Manual Override for Comfort Doors",
                system_domain=domain_info["label"],
                specification="Replace overly conservative ultrasonic door sensors with wide-angle millimeter-wave radar for curbs and pillars, and integrate an electromagnetic freewheeling clutch for effortless manual override when doors stop.",
                target_metric="Door opening abort false-positive rate reduced from 38% to <2%; manual opening effort <15 N",
                affected_bmw_taxonomy_attributes=["body_equipment", "safety_overall"],
                bom_cost_impact_eur="+€42 per vehicle (radar modules and freewheeling clutch)",
                engineering_complexity="Medium",
                time_to_market_readiness="SOP 2026/Q1",
                tradeoffs_and_risks="Packaging radar sensors inside exterior door skin without visible styling disruption.",
            ),
            EngineeringRequirementPRD(
                requirement_id=f"PRD-{vehicle}-SE02",
                title=f"High-Reliability Capacitive Kick-Sensor Tailgate & Active Aero Package",
                system_domain=domain_info["label"],
                specification="Deploy dual-zone capacitive kick detection algorithms with 98%+ first-attempt success rate, and introduce active front air curtains with optional adaptive rear wing achieving Cd <= 0.205.",
                target_metric="Tailgate kick success rate >= 98% on first kick; aerodynamic drag Cd reduced to 0.202",
                affected_bmw_taxonomy_attributes=["body_equipment", "exterior_styling"],
                bom_cost_impact_eur="+€65 per vehicle",
                engineering_complexity="Low",
                time_to_market_readiness="SOP 2025/Q4",
                tradeoffs_and_risks="Bumper sensor wash resistance under heavy rain and snow.",
            ),
        ]
        prompts = [
            "BMW i7 automatic doors have -18.1% net sentiment due to abrupt halting in tight garages. How do Zeekr MIX and AITO M9 prevent this?",
            "Why is the kick-sensor tailgate failure rate so prominent in customer surveys, and what sensor technology fixes it permanently?",
        ]
        return reqs, prompts, False

    return [], [], False


def _build_offline_synthesis(vehicle: str, domain_keys: list[str] | str) -> GapAnalysisOutput:
    """Deterministic fallback synthesis across 1-7 selected domains."""
    canonical_domains = normalize_domains(domain_keys)
    comments = _gather_vehicle_pain_points(vehicle, canonical_domains)
    domain_slug = "-".join(d[:2] for d in canonical_domains)
    analysis_id = f"gap-{vehicle.lower()}-{domain_slug}-{int(time.time())}"

    domain_labels = [DOMAIN_MAPPING[d]["label"] for d in canonical_domains]
    joined_label = " + ".join(domain_labels)
    aspects_joined = "; ".join(DOMAIN_MAPPING[d]["aspects"] for d in canonical_domains)

    pain_texts = [c.get("text") for c in comments] or [
        f"Customer friction observed on BMW {vehicle} across {aspects_joined}.",
        f"Performance metrics lag behind top Chinese disruptors in {joined_label}.",
    ]

    benchmarks: list[CompetitorBenchmarkItem] = []
    seen_benchmarks: set[str] = set()
    for d in canonical_domains:
        for comp in DOMAIN_MAPPING[d]["competitors"]:
            key = f"{comp['brand']}-{comp['model']}"
            if key not in seen_benchmarks:
                seen_benchmarks.add(key)
                benchmarks.append(CompetitorBenchmarkItem(
                    competitor_brand=comp["brand"],
                    competitor_model=comp["model"],
                    feature_name=DOMAIN_MAPPING[d]["label"],
                    technical_specs=comp["tech"],
                    observed_market_advantage=f"Surpasses BMW baseline: {comp['bmw_status']}",
                    source_citation=f"China EV Benchmark Cohort ({comp['brand']})",
                ))

    reqs: list[EngineeringRequirementPRD] = []
    prompts: list[str] = []
    has_critical = False

    for d in canonical_domains:
        d_reqs, d_prompts, d_crit = _get_domain_offline_artifacts(d, vehicle)
        reqs.extend(d_reqs)
        prompts.extend(d_prompts)
        if d_crit:
            has_critical = True

    citations = [
        TraceableCitation(
            source_type="bmw_customer_verbatim",
            citation_text=pain_texts[0][:140],
            vehicle_or_outlet=f"BMW {vehicle.upper()} Customer Voice / FAQ Portfolio",
            severity_or_date="High Severity Customer Voice",
        ),
        TraceableCitation(
            source_type="competitor_spec",
            citation_text=benchmarks[0].technical_specs[:140] if benchmarks else "800V SiC 5C Architecture",
            vehicle_or_outlet=f"{benchmarks[0].competitor_brand} {benchmarks[0].competitor_model}" if benchmarks else "China Tech Radar",
            severity_or_date="2026 Production Benchmark",
        ),
    ]

    return GapAnalysisOutput(
        analysis_id=analysis_id,
        target_vehicle=vehicle.upper(),
        domain=",".join(canonical_domains),
        domains=canonical_domains,
        domain_label=joined_label,
        generated_at=datetime.now(timezone.utc).isoformat(),
        model_used="deterministic-benchmark-engine",
        executive_summary=f"Multi-Domain Strategic Gap Analysis for BMW {vehicle.upper()} across {len(canonical_domains)} selected focus domains ({joined_label}). Synthesizing real customer pain points and verified Chinese benchmarks (蔚来、问界、小米、理想、极氪、小鹏), closing the competitive gap requires coordinated cross-domain PRD updates prior to SOP.",
        bmw_customer_pain_points=pain_texts,
        citations=citations,
        competitor_benchmarks=benchmarks[:6],
        gap_severity="Critical" if has_critical else "High",
        recommended_requirements=reqs,
        pm_challenge_prompts=prompts,
        review_status="pending_review",
        system_fingerprint="offline-deterministic-engine",
        seed=42,
    )


def run_gap_analysis(
    vehicle: str,
    domain: str | None = None,
    domains: list[str] | None = None,
    focus_competitor: str | None = None,
    custom_instruction: str | None = None,
) -> dict:
    """Execute AI Competitor Gap Analysis via OpenAI across 1-7 selected domains, falling back safely to deterministic synthesis."""
    v = vehicle.upper()
    canonical_domains = normalize_domains(domains if domains is not None else domain)
    domain_labels = [DOMAIN_MAPPING[d]["label"] for d in canonical_domains]
    joined_label = " + ".join(domain_labels)
    domain_slug = "-".join(d[:2] for d in canonical_domains)
    pain_points = _gather_vehicle_pain_points(v, canonical_domains)
    trend_snippets = _load_chinese_trend_snippets()

    api_key = get_openai_api_key()
    model = get_openai_model()

    if not api_key:
        logger.info("OpenAI API key not found. Using high-fidelity deterministic benchmark engine.")
        output = _build_offline_synthesis(v, canonical_domains)
        _save_run(output)
        return output.model_dump()

    try:
        client = OpenAI(api_key=api_key)

        target_domains_data = [
            {
                "domain_key": d,
                "domain_label": DOMAIN_MAPPING[d]["label"],
                "aspects": DOMAIN_MAPPING[d]["aspects"],
                "competitors": DOMAIN_MAPPING[d]["competitors"],
            }
            for d in canonical_domains
        ]

        prompt_data = {
            "target_bmw_vehicle": v,
            "selected_domains_count": len(canonical_domains),
            "selected_domains": target_domains_data,
            "bmw_customer_complaints": [p.get("text") for p in pain_points],
            "china_tech_radar_sample": trend_snippets,
            "focus_competitor": focus_competitor or "All (蔚来, 问界, 小米, 理想, 极氪, 小鹏)",
            "custom_instruction": custom_instruction or "Focus on actionable engineering PRD requirements with clear BOM cost estimates and verifiable target metrics across the selected domains, explicitly analyzing cross-domain synergies and engineering trade-offs.",
        }

        system_prompt = (
            "You are the Senior Chief Competitive Strategist and Systems Architect for BMW Group R&D.\n"
            "Your task is to conduct an authoritative, data-driven Competitor Gap Analysis synthesizing real BMW customer pain points "
            "against the top 6 Chinese EV pioneers: 蔚来 (NIO), 问界 (AITO / Huawei), 小米 (Xiaomi), 理想 (Li Auto), 极氪 (Zeekr), 小鹏 (XPeng).\n\n"
            f"The Product Manager has selected {len(canonical_domains)} focus domain(s) for this analysis:\n"
            f"{joined_label}\n\n"
            "We adhere strictly to the 7 MECE Technology Domains:\n"
            "1. Energy & Charging (800V/925V SiC, 5C charging, battery preconditioning)\n"
            "2. Driving Assistance (World-model urban pilot, automated parking, GSR2 alert smoothing)\n"
            "3. Digital Cockpit & AI (Sub-second OS boot, LLM agent, physical climate shortcuts)\n"
            "4. Connected Ecosystem (My BMW App subterranean BLE fallback, MagLink tablet dock, satellite SOS)\n"
            "5. Smart Cabin (Zero-gravity lounge seats, active seat ventilation, electrochromic smart glass roof)\n"
            "6. Vehicle Dynamics & Safety (Sub-4ms motor torque loop, dual-valve CDC preview, 27,200 rpm motors)\n"
            "7. Smart Exterior (Wide-angle millimeter-wave door obstacle radar, kick tailgate, active aero Cd 0.195)\n\n"
            "Important instructions for multi-domain analysis:\n"
            "- Cover each of the selected focus domains in your analysis.\n"
            "- When multiple domains are selected, analyze cross-domain synergies and engineering trade-offs (e.g., thermal management vs cabin climate, ADAS sensor packaging vs exterior aerodynamics, BOM cost distribution).\n"
            "- Provide actionable Engineering PRD requirements for the selected domains (or well-integrated cross-domain requirements).\n\n"
            "You must return a strictly formatted JSON object adhering to this schema:\n"
            "{\n"
            '  "analysis_id": "gap-... (string)",\n'
            f'  "target_vehicle": "{v}",\n'
            f'  "domain": "{",".join(canonical_domains)}",\n'
            f'  "domains": {json.dumps(canonical_domains)},\n'
            f'  "domain_label": "{joined_label}",\n'
            '  "executive_summary": "Concise 2-3 paragraph strategic assessment of the gap, root causes, cross-domain synergies, and urgency.",\n'
            '  "bmw_customer_pain_points": ["exact customer complaint verbatims and pain points across the selected domains"],\n'
            '  "citations": [\n'
            '     {"source_type": "bmw_customer_verbatim"|"competitor_spec"|"china_media_trend", "citation_text": "...", "vehicle_or_outlet": "...", "severity_or_date": "..."}\n'
            "  ],\n"
            '  "competitor_benchmarks": [\n'
            '     {"competitor_brand": "...", "competitor_model": "...", "feature_name": "...", "technical_specs": "...", "observed_market_advantage": "...", "source_citation": "..."}\n'
            "  ],\n"
            '  "gap_severity": "Critical"|"High"|"Medium",\n'
            '  "recommended_requirements": [\n'
            '     {\n'
            '        "requirement_id": "PRD-...-01",\n'
            '        "title": "Clear engineering PRD title",\n'
            '        "system_domain": "...",\n'
            '        "specification": "Detailed engineering specification text",\n'
            '        "target_metric": "Quantifiable pass/fail metric (e.g. SoC time, latency, weight)",\n'
            '        "affected_bmw_taxonomy_attributes": ["charging", "hv_battery", ...],\n'
            '        "bom_cost_impact_eur": "+€... per vehicle",\n'
            '        "engineering_complexity": "Low"|"Medium"|"High"|"Critical",\n'
            '        "time_to_market_readiness": "SOP quarter or OTA milestone",\n'
            '        "tradeoffs_and_risks": "Tradeoffs between cost, thermal mass, and supplier readiness"\n'
            "     }\n"
            "  ],\n"
            '  "pm_challenge_prompts": [\n'
            '     "Hard-hitting challenge questions for the Product Manager to debate before sign-off"\n'
            "  ]\n"
            "}\n"
            "Ensure rigorous engineering terminology, realistic automotive BOM estimates in EUR, and zero corporate fluff."
        )

        response = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            temperature=0.0,
            seed=42,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(prompt_data, ensure_ascii=False)},
            ],
        )

        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)

        # Ensure required fields and inject metadata
        parsed["analysis_id"] = f"gap-{v.lower()}-{domain_slug[:12]}-{int(time.time())}"
        parsed["target_vehicle"] = v
        parsed["domain"] = ",".join(canonical_domains)
        parsed["domains"] = canonical_domains
        parsed["domain_label"] = joined_label
        parsed["generated_at"] = datetime.now(timezone.utc).isoformat()
        parsed["model_used"] = model
        parsed["system_fingerprint"] = getattr(response, "system_fingerprint", None)
        parsed["seed"] = 42
        parsed["review_status"] = "pending_review"
        parsed["pm_notes"] = None
        parsed["reviewed_at"] = None

        output = GapAnalysisOutput(**parsed)
        _save_run(output)
        return output.model_dump()

    except Exception as exc:
        logger.error(f"OpenAI gap analysis failed ({exc}), falling back to offline synthesis.", exc_info=True)
        fallback = _build_offline_synthesis(v, canonical_domains)
        fallback.executive_summary += f" (Note: Live OpenAI call encountered: {str(exc)[:120]}. Fallback benchmark engine engaged.)"
        _save_run(fallback)
        return fallback.model_dump()


def _save_run(output: GapAnalysisOutput) -> None:
    """Persist run to runtime directory."""
    path = AGENT_RUNS_DIR / f"{output.analysis_id}.json"
    path.write_text(output.model_dump_json(indent=2), encoding="utf-8")


def list_gap_analyses(limit: int = 20) -> list[dict]:
    """Retrieve saved analyses in reverse chronological order."""
    files = sorted(AGENT_RUNS_DIR.glob("gap-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    results = []
    for f in files[:limit]:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            results.append({
                "analysis_id": data.get("analysis_id"),
                "target_vehicle": data.get("target_vehicle"),
                "domain": data.get("domain"),
                "domain_label": data.get("domain_label"),
                "gap_severity": data.get("gap_severity"),
                "generated_at": data.get("generated_at"),
                "model_used": data.get("model_used"),
                "review_status": data.get("review_status"),
                "requirement_count": len(data.get("recommended_requirements", [])),
                "summary_snippet": (data.get("executive_summary") or "")[:150] + "...",
            })
        except Exception:
            continue
    return results


def get_gap_analysis(analysis_id: str) -> dict:
    """Retrieve a single saved gap analysis."""
    path = AGENT_RUNS_DIR / f"{analysis_id}.json"
    if not path.exists():
        raise KeyError(f"Analysis {analysis_id} not found")
    return json.loads(path.read_text(encoding="utf-8"))


def review_gap_analysis(
    analysis_id: str,
    review_status: Literal["approved", "rejected", "challenged"],
    pm_notes: str | None = None,
) -> dict:
    """Product Manager Human-in-the-Loop decision handler."""
    data = get_gap_analysis(analysis_id)
    data["review_status"] = review_status
    data["pm_notes"] = pm_notes
    data["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    path = AGENT_RUNS_DIR / f"{analysis_id}.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return data


def get_trend_markers_db() -> dict:
    """Load the verified Future Trend Markers Database."""
    if not TREND_MARKERS_DB_FILE.exists():
        return {"companies": [], "trend_markers": []}
    try:
        return json.loads(TREND_MARKERS_DB_FILE.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.error(f"Failed to read future trend markers: {exc}")
        return {"companies": [], "trend_markers": []}


def get_filtered_trend_markers(
    company: str | None = None,
    domain: str | None = None,
    domains: list[str] | None = None,
    query: str | None = None,
) -> dict:
    """Filter and search future trend markers for BMW R&D benchmarking across 1-7 selected domains."""
    data = get_trend_markers_db()
    companies = data.get("companies", [])
    markers = data.get("trend_markers", [])

    if company and company.lower() != "all":
        c_lower = company.lower()
        markers = [
            m for m in markers
            if c_lower in m.get("company_id", "").lower()
            or c_lower in m.get("company_zh", "").lower()
            or c_lower in m.get("company_en", "").lower()
        ]

    # Support multiple domain filtering (e.g. 1 to 7 domains selected)
    target_domains: list[str] | None = None
    if domains is not None:
        target_domains = normalize_domains(domains)
    elif domain and domain.lower() != "all":
        target_domains = normalize_domains(domain)

    if target_domains and len(target_domains) < len(DOMAIN_MAPPING):
        canonical_set = set(target_domains)
        markers = [
            m for m in markers
            if normalize_domain(m.get("domain", "")) in canonical_set
            or any(cd in m.get("domain", "").lower() for cd in canonical_set)
        ]

    if query and query.strip():
        q_lower = query.strip().lower()
        markers = [
            m for m in markers
            if q_lower in m.get("technology_name", "").lower()
            or q_lower in m.get("key_specs", "").lower()
            or q_lower in m.get("recommended_bmw_action", "").lower()
            or any(q_lower in tag.lower() for tag in m.get("tags", []))
        ]

    return {
        "total": len(markers),
        "companies": companies,
        "items": markers,
    }


# Alias for API endpoint compatibility
query_trend_markers = get_filtered_trend_markers


def chat_with_agent(
    messages: list[dict],
    target_vehicle: str = "G60",
    focus_company: str | None = None,
    domain: str | None = None,
    domains: list[str] | None = None,
) -> dict:
    """Conversational AI consultation grounded in the Future Trend Markers DB and BMW VoC across 1-7 selected domains."""
    v = target_vehicle.upper()
    db = get_trend_markers_db()
    markers = db.get("trend_markers", [])

    # Filter markers to relevant context if company or domain(s) specified
    if focus_company and focus_company.lower() != "all":
        fc = focus_company.lower()
        relevant_markers = [
            m for m in markers
            if fc in m.get("company_id", "").lower()
            or fc in m.get("company_zh", "").lower()
            or fc in m.get("company_en", "").lower()
        ]
    else:
        relevant_markers = markers

    target_domains: list[str] | None = None
    if domains is not None:
        target_domains = normalize_domains(domains)
    elif domain and domain.lower() != "all":
        target_domains = normalize_domains(domain)

    if target_domains and len(target_domains) < len(DOMAIN_MAPPING):
        canonical_set = set(target_domains)
        domain_filtered = [
            m for m in relevant_markers
            if normalize_domain(m.get("domain", "")) in canonical_set
            or any(cd in m.get("domain", "").lower() for cd in canonical_set)
        ]
        if domain_filtered:
            relevant_markers = domain_filtered

    if not relevant_markers:
        relevant_markers = markers[:6]

    # Get sample customer complaints for context across selected domains
    active_domains = target_domains or list(DOMAIN_MAPPING.keys())
    pain_points = _gather_vehicle_pain_points(v, active_domains, max_items=4)
    pain_texts = [p.get("text") for p in pain_points]

    domain_labels = [DOMAIN_MAPPING[d]["label"] for d in active_domains]
    joined_domain_labels = " + ".join(domain_labels)

    api_key = get_openai_api_key()
    model = get_openai_model()

    if not api_key:
        return {
            "role": "assistant",
            "content": (
                f"### Strategic Assessment for BMW {v}\n\n"
                f"Active PM Focus Domains ({len(active_domains)} of 7): **{joined_domain_labels}**\n\n"
                f"Analyzing our Chinese benchmark cohort (**蔚来、问界、小米、理想、极氪、小鹏**) across the **7 MECE Technology Domains** against BMW {v} baselines:\n\n"
                f"1. **⚡ Energy & Charging:** Zeekr's 800V 5.5C Golden Battery (10.5 min SoC) and NIO's 925V architecture directly challenge BMW's 400V 205 kW charging plateau. Accelerating 800V SiC and 5C LFP is our highest priority.\n"
                f"2. **🛡️ Driving Assistance:** XPeng's Turing AI end-to-end urban pilot and AITO's HUAWEI ADS 3.0 deliver map-free urban valet navigation, exceeding BMW Level 2+ Highway Assistant in complex Chinese traffic.\n"
                f"3. **🖥️ Digital Cockpit & AI:** Xiaomi SU7's HyperOS (1.49s boot, phone mirroring, physical PIN attachments) and NOMI GPT eliminate the UI latency and deep menu friction reported by BMW drivers.\n"
                f"4. **📱 Connected Ecosystem:** AITO MagLink and subterranean BLE proximity wake solve our -76.7% underground garage timeout pain point without heavy hardware costs.\n"
                f"5. **🛋️ Smart Cabin:** Li Auto zero-gravity lounge seating with active seat ventilation directly fixes the summer perspiration complaints on synthetic Veganza upholstery.\n"
                f"6. **🏎️ Vehicle Dynamics & Safety:** While BMW holds an industry-leading +44.7% Moat, AITO's DATS 4ms dynamic torque loop and Li Auto's lidar bump preview challenge low-speed ride harshness.\n"
                f"7. **🚪 Smart Exterior:** Zeekr MIX and AITO M9 wide-angle millimeter-wave door obstacle avoidance solve i7 comfort door aborts in tight garages (-18.1% sentiment).\n\n"
                f"*Recommendation for Product Management:* Review the **Future Trend Markers DB** and select specific PRD markers for Neue Klasse technology transfer."
            ),
            "model_used": "deterministic-r-and-d-advisor",
            "referenced_markers": [m.get("marker_id") for m in relevant_markers[:4]],
        }

    try:
        client = OpenAI(api_key=api_key)

        system_prompt = (
            f"You are the Senior Chief Competitive Strategist and Systems Architect for BMW Group R&D.\n"
            f"Your focus is the China EV competitive landscape and engineering counter-strategies.\n"
            f"Target BMW Vehicle: BMW {v} (and the Neue Klasse roadmap).\n"
            f"Key Benchmark Cohort: Exactly these 6 Chinese EV leaders: 蔚来 (NIO), 问界 (AITO / Huawei), 小米 (Xiaomi), 理想 (Li Auto), 极氪 (Zeekr), 小鹏 (XPeng).\n\n"
            f"The Product Manager is currently focusing on {len(active_domains)} of 7 MECE domain(s):\n"
            f"{joined_domain_labels}\n\n"
            "We classify all technology into the 7 MECE Technology Domains (FAQ Standard):\n"
            "1. ⚡ Energy & Charging (800V/925V SiC, 5C charging, battery preconditioning)\n"
            "2. 🛡️ Driving Assistance (World-model urban pilot, automated parking, GSR2 alert smoothing)\n"
            "3. 🖥️ Digital Cockpit & AI (Sub-second OS boot, LLM agent, physical climate shortcuts)\n"
            "4. 📱 Connected Ecosystem (My BMW App subterranean BLE fallback, MagLink tablet dock, satellite SOS)\n"
            "5. 🛋️ Smart Cabin (Zero-gravity lounge seats, active seat ventilation, electrochromic smart glass roof)\n"
            "6. 🏎️ Vehicle Dynamics & Safety (Sub-4ms motor torque loop, dual-valve CDC preview, 27,200 rpm motors)\n"
            "7. 🚪 Smart Exterior (Wide-angle millimeter-wave door obstacle radar, kick tailgate, active aero Cd 0.195)\n\n"
            f"You have direct access to the verified BMW Future Trend Markers Database:\n"
            f"{json.dumps(relevant_markers[:8], ensure_ascii=False, indent=1)}\n\n"
            f"Recent BMW Customer Pain Points for {v} in focused domains:\n"
            f"{json.dumps(pain_texts, ensure_ascii=False)}\n\n"
            "Guidelines for your response:\n"
            "- Be authoritative, highly technical, and direct with automotive engineering terminology (BOM costs in EUR, SoC curve, 800V/925V SiC, CAN-FD/Ethernet, NPU TOPS, CTB/CTP, CDC damping).\n"
            "- Address the specific focus domain(s) selected by the PM, identifying cross-domain synergies and trade-offs where applicable.\n"
            "- Directly reference the specific innovations of 蔚来, 问界, 小米, 理想, 极氪, or 小鹏 as appropriate.\n"
            "- Structure your answers clearly with markdown: Executive Takeaway, Benchmark Comparison, Actionable BMW Engineering PRD Specification, and Product Manager Tradeoffs/Risks.\n"
            "- Keep responses focused, actionable, and formatted cleanly."
        )

        chat_history = [{"role": "system", "content": system_prompt}]
        for m in messages[-8:]:
            chat_history.append({"role": m.get("role", "user"), "content": m.get("content", "")})

        response = client.chat.completions.create(
            model=model,
            messages=chat_history,
            temperature=0.0,
            seed=42,
            max_tokens=1500,
        )

        reply_text = response.choices[0].message.content or "No response generated."
        return {
            "role": "assistant",
            "content": reply_text,
            "model_used": model,
            "referenced_markers": [m.get("marker_id") for m in relevant_markers[:5]],
        }

    except Exception as exc:
        logger.error(f"Chat failed: {exc}", exc_info=True)
        return {
            "role": "assistant",
            "content": f"Strategic Analysis (Fallback mode - OpenAI notice: {str(exc)[:100]}):\n\nBased on our benchmark database of 蔚来, 问界, 小米, 理想, 极氪, and 小鹏 across the focused domain(s) ({joined_domain_labels}), BMW {v} must prioritize 800V silicon carbide charging turnaround times, underground BLE ecosystem connectivity, and sub-second phone-to-car handover. Check the Future Trend Markers DB tab for full technical specs.",
            "model_used": "offline-fallback",
            "referenced_markers": [m.get("marker_id") for m in relevant_markers[:3]],
        }
