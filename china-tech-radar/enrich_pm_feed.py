import json

with open("china_megatrends_feed.json", "r", encoding="utf-8") as f:
    feed = json.load(f)

# PM Simplified items
pm_updates = {
    "NEWS-2026-1011-01": {
        "pm_takeaway": "CATL demonstrated 500 Wh/kg all-solid-state cells with 10C discharge, targeting pre-series lines before 2027.",
        "pm_action": "Evaluate Gen6 solid-state roadmap to prevent 2x energy density obsolescence by 2027.",
        "threat_level": "CRITICAL R&D THREAT"
    },
    "NEWS-2026-1011-02": {
        "pm_takeaway": "Huawei deployed ADS 3.5 VLA nationwide without HD maps, handling roundabouts and multi-level parking garages at 98.7% success.",
        "pm_action": "Prioritize mapless end-to-end urban navigation in China; highway-only L2 is no longer competitive.",
        "threat_level": "IMMEDIATE COMPETITIVE THREAT"
    },
    "NEWS-2026-1011-03": {
        "pm_takeaway": "Xiaomi deployed an on-device 7B LLM on Snapdragon 8295, cutting voice latency to 350ms offline.",
        "pm_action": "Cut BMW IPA voice response latency below 500ms via on-device NPU; eliminate 2.4s cloud roundtrips.",
        "threat_level": "CORE UX FRICTION POINT"
    },
    "NEWS-2026-1011-04": {
        "pm_takeaway": "BYD dropped DM 5.0 PHEVs with 2,100 km range to $11,000, driving national PHEV penetration to 46%.",
        "pm_action": "Reposition PHEVs as long-range electrics, not compliance hybrids; address price compression.",
        "threat_level": "VOLUME & MARGIN EROSION"
    },
    "NEWS-2026-1011-05": {
        "pm_takeaway": "XPeng taped out in-house 400 TOPS 'Turing' AI processor, replacing expensive dual Nvidia Orin-X clusters.",
        "pm_action": "Audit ADAS silicon BoM costs; vertical silicon integration allows Chinese OEMs to undercut Tier-1 pricing.",
        "threat_level": "SUPPLY CHAIN & BOM THREAT"
    },
    "NEWS-2026-1011-06": {
        "pm_takeaway": "NIO Firefly sub-€25k compact EV spotted testing in Europe with battery swap and 90kW DC charging.",
        "pm_action": "Accelerate entry-level premium urban EV portfolio (MINI Aceman / compact iX1) to defend European home turf.",
        "threat_level": "EUROPEAN HOMELAND THREAT"
    },
    "NEWS-2026-1011-07": {
        "pm_takeaway": "Zeekr MIX features pillarless double sliding doors and 270° swiveling lounge seats, transforming cabin into mobile living room.",
        "pm_action": "Shift cabin design focus from driver cockpit to 'Third Living Space' modularity for luxury segments.",
        "threat_level": "INTERIOR ARCHITECTURE SHIFT"
    },
    "NEWS-2026-1011-08": {
        "pm_takeaway": "Li Auto active with 1,000 5C superchargers (520 kW) covering 92% of highways, delivering 500 km in 12 min.",
        "pm_action": "Accelerate IONCHI charging joint venture; proprietary 5C infrastructure is the primary purchase decider.",
        "threat_level": "INFRASTRUCTURE ECOSYSTEM"
    },
    "NEWS-2026-1011-09": {
        "pm_takeaway": "China NEV retail penetration reached 58.2%, with joint-venture brand sales contracting 11.4% year-over-year.",
        "pm_action": "Speed up China-specific localized software releases; Western brand premium alone cannot sustain market share.",
        "threat_level": "MARKET SHARE CONTRACTION"
    },
    "NEWS-2026-1011-10": {
        "pm_takeaway": "Horizon Robotics secured 20+ OEM contracts for Journey 6 silicon, cutting L2+ ADAS BoM by 30%.",
        "pm_action": "Standardize Level 2+ navigation on base models; premium ADAS feature surcharges face customer resistance.",
        "threat_level": "FEATURE DEMOCRATIZATION"
    }
}

for item in feed["news_items"]:
    item_id = item["id"]
    if item_id in pm_updates:
        item["pm_takeaway"] = pm_updates[item_id]["pm_takeaway"]
        item["pm_action"] = pm_updates[item_id]["pm_action"]
        item["threat_level"] = pm_updates[item_id]["threat_level"]

with open("china_megatrends_feed.json", "w", encoding="utf-8") as f:
    json.dump(feed, f, ensure_ascii=False, indent=2)

print("Enriched china_megatrends_feed.json with PM takeaways successfully!")
