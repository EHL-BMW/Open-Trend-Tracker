import json

with open('/Users/miao/Desktop/Hackathon/bmw_ev_technology_sentiment_pipeline.json') as f:
    data = json.load(f)

print(f"{'Domain':<28} | {'Likes':>5} | {'Friction':>8} | {'Total':>5} | {'Net Score':>9} | {'Ø Severity':>10}")
print("-" * 75)

for d in data['domains']:
    k = d['kpi_metrics']
    likes = k['likes_count']
    friction = k['complaints_count']
    tot = likes + friction
    net = ((likes - friction) / tot * 100) if tot > 0 else 0
    net_str = f"+{net:.1f}%" if net > 0 else f"{net:.1f}%"
    print(f"{d['domain_name']:<28} | {likes:>5} | {friction:>8} | {tot:>5} | {net_str:>9} | {k['avg_severity_score']:>10.2f}")
