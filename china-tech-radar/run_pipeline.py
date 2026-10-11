import json
import pandas as pd

print("=" * 80)
print("🚀 STARTING BMW EV/PHEV TECHNOLOGY SENTIMENT & COMPLAINT PIPELINE")
print("=" * 80)

# 1. Load Datasets
csv_file = "/Users/miao/Desktop/Hackathon/bmw_ev_technology_sentiment_pipeline.csv"
json_file = "/Users/miao/Desktop/Hackathon/bmw_ev_technology_sentiment_pipeline.json"

df = pd.read_csv(csv_file)
with open(json_file, "r", encoding="utf-8") as f:
    pipeline_kb = json.load(f)

meta = pipeline_kb["metadata"]
print(f"📦 Pipeline Version:        {meta['pipeline_version']}")
print(f"📊 Dataset Scope:            {meta['scope']}")
print(f"🔢 Total Feedback Analysiert: {meta['total_feedback_records']:,} Datensätze")
print(f"   ├─ Positive Lobstimmen:   {meta['total_likes_praise']:,} (Likes)")
print(f"   └─ Beanstandungen & UX:   {meta['total_complaints_friction']:,} (Defect + Diff. to Use + Wants)")
print("-" * 80)

# 2. Domain Sentiment & Friction Ranking
print("\n🏆 DOMAIN SENTIMENT RANKING (Net Sentiment Proxy: Likes vs Complaints)")
print(f"{'Domäne':<28} | {'Total':>5} | {'Likes':>5} | {'Friction':>8} | {'Net Score':>9} | {'Ø Severity':>10}")
print("-" * 80)

domain_stats = []
for dom in pipeline_kb["domains"]:
    kpi = dom["kpi_metrics"]
    net = kpi["net_sentiment_score"]
    net_str = f"+{net:.1f}%" if net > 0 else f"{net:.1f}%"
    domain_stats.append({
        "name": dom["domain_name"],
        "total": kpi["total_feedback_volume"],
        "likes": kpi["likes_count"],
        "friction": kpi["complaints_count"],
        "net": net,
        "net_str": net_str,
        "severity": kpi["avg_severity_score"]
    })

domain_stats.sort(key=lambda x: x["net"], reverse=True)
for d in domain_stats:
    flag = "🟢" if d["net"] > 0 else ("🟡" if d["net"] > -30 else "🔴")
    print(f"{flag} {d['name']:<25} | {d['total']:>5} | {d['likes']:>5} | {d['friction']:>8} | {d['net_str']:>9} | {d['severity']:>10.2f}")

# 3. Top Priority Engineering Action Items
print("\n" + "=" * 80)
print("🛠️ PRIORITY ENGINEERING BACKLOG (Gewichtung = Fälle × Severity-Score)")
print("=" * 80)

pain_points = df[df["sentiment_type"] == "PAIN_POINT"].copy()
pain_points["priority_index"] = pain_points["volume_count"] * pain_points["severity_weight"]
ranked_backlog = pain_points.sort_values(by="priority_index", ascending=False).head(10)

for idx, (_, row) in enumerate(ranked_backlog.iterrows(), 1):
    print(f"\n[PRIO {idx:02d}] {row['domain_name']} -> {row['component_vfc']}")
    print(f"         Volumen: {row['volume_count']} Fälle | Severity: {row['severity_weight']}/3 | Prio-Score: {row['priority_index']}")
    print(f"         Layer:   {row['system_layer']} | Feedback-Typ: {row['feedback_category']}")
    print(f"         O-Ton:   \"{row['verbatim_sample']}\"")
    print(f"         Action:  👉 {row['engineering_action']}")

# 4. Cohort Vulnerability Split
print("\n" + "=" * 80)
print("🚗 KOHORTEN-ANFÄLLIGKEIT (Wo treten die meisten Beanstandungen auf?)")
print("=" * 80)
cohort_totals = {"i5 BEV": 0, "i7 BEV": 0, "5er PHEV": 0, "7er PHEV": 0}
for dom in pipeline_kb["domains"]:
    c_dist = dom.get("cohort_complaint_distribution", {})
    cohort_totals["i5 BEV"] += c_dist.get("i5_bev", 0)
    cohort_totals["i7 BEV"] += c_dist.get("i7_bev", 0)
    cohort_totals["5er PHEV"] += c_dist.get("5er_phev", 0)
    cohort_totals["7er PHEV"] += c_dist.get("7er_phev", 0)

for c, val in sorted(cohort_totals.items(), key=lambda x: x[1], reverse=True):
    share = (val / meta['total_complaints_friction']) * 100
    bar = "█" * int(share / 2.5)
    print(f"{c:<10} : {val:>4} Beanstandungen ({share:>5.1f}%) {bar}")

print("\n" + "=" * 80)
print("✅ PIPELINE EXECUTION COMPLETED SUCCESSFULLY (Exit Code 0)")
print("=" * 80)
