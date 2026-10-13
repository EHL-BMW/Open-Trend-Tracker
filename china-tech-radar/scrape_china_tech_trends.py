"""
China EV-Tech Trend Radar — scraper + quantifier
================================================

What it does
------------
1. SCRAPE   For each technology topic (Chinese keyword query), pull articles from
            Google News (China edition, zh-CN), which aggregates Chinese outlets
            (新浪, 搜狐, 汽车之家, 36Kr, 东方财富, 盖世汽车, IT之家, ...).
            Queries are date-windowed (7-day windows, WEEKS back) so we get a real
            time series, not just "latest headlines". Saturated windows (>=100
            results, the feed cap) are re-split into daily windows.
            Closed windows are cached on disk -> daily re-runs only refetch the
            last ~2 weeks.

2. QUANTIFY Per topic:
            - volume        unique articles in the last 4 weeks
            - share_of_voice  volume / volume of all tracked topics (controls for
                            overall news-volume swings)
            - momentum      rate ratio: weekly rate last 4 wks / prior 8 wks
            - p_momentum    exact conditional binomial test of that rate ratio
                            (Poisson rate comparison; H0: rate unchanged)
            - mann_kendall  non-parametric monotonic-trend test over all weeks
                            (+ Sen's slope, robust articles/week trend)
            - breadth       number of distinct outlets in last 4 weeks
                            (diffusion: one outlet repeating vs. industry-wide)

3. LINK TO BMW  Each topic is mapped to one of the 8 BMW customer-feedback
            technology domains from our pipeline
            (bmw_ev_technology_domain_summary.csv). Exposure = complaints x
            avg severity of that domain, normalised 0-1.

            priority = 100 * (0.35 * attention_pct + 0.35 * momentum_pct
                              + 0.30 * bmw_exposure)

Output: china_tech_trends.json  +  china_tech_trends_data.js (for the web page)
        china_tech_trends_articles.csv (all scraped articles, for further analysis)

Usage:  python3 scrape_china_tech_trends.py            (incremental, uses cache)
        python3 scrape_china_tech_trends.py --no-cache (full refetch)
        python3 scrape_china_tech_trends.py --refresh-topic phone_car_eco
                                                    (reuse other topics and the saved date window)
"""

import csv
import argparse
import datetime as dt
import hashlib
import json
import math
import os
import re
import statistics
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from email.utils import parsedate_to_datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(HERE, "china_trends_cache")
WEEKS = 12            # history depth
RECENT_WEEKS = 4      # "recent" window for momentum
FEED_CAP = 100        # Google News RSS max items per query
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"

# Search for cross-device capabilities, not every vehicle announcement that happens to
# mention a cockpit OS. The vehicle context also keeps general IoT/accessory news out.
ECOSYSTEM_QUERY = (
    '("人车家全生态" OR "人车家生态" OR "车家互联" OR "车手互联" OR '
    '"生态域" OR "CarIoT" OR "车载生态配件" OR "车载智能配件" OR "智能生态配件" OR '
    '"车载配件生态" OR "手机车机互联" OR "跨端流转") 汽车'
)
ECOSYSTEM_QUERIES = (
    ECOSYSTEM_QUERY, '"HiCar" 车机', '"NIO Link" 汽车',
    '"鸿蒙座舱" 汽车', '"人车家" 汽车',
)
ECOSYSTEM_DISPLAY_QUERY = " OR ".join(f"({query})" for query in ECOSYSTEM_QUERIES)
ECOSYSTEM_HEADLINE = re.compile(
    r"车家互联|车手互联|生态域|CarIoT|车载生态配件|车载智能配件|"
    r"车载配件生态|手机车机互联|NIO\s*Link|\bHiCar\b",
    re.IGNORECASE,
)
ECOSYSTEM_CROSS_DEVICE = re.compile(r"跨端流转|设备能力共享|软硬件协同|跨设备互联|多设备协同")
ECOSYSTEM_COCKPIT_CAPABILITY = re.compile(
    r"多屏流转|跨端|互联|生态|交互|智能家居|车机体验|座舱体验|家庭智能座舱|一碰就连"
)
ECOSYSTEM_CAR_CONTEXT = re.compile(r"汽车|车机|车载|座舱|智能车|车企|车型")
ECOSYSTEM_SPAM = re.compile(r"\+FAQ|亚博|博彩|娱乐城", re.IGNORECASE)


def topic_headline_relevant(topic_id, title):
    """Keep only ecosystem headlines; the RSS search may match a term in the article body."""
    if topic_id != "phone_car_eco":
        return True
    return not ECOSYSTEM_SPAM.search(title) and bool(ECOSYSTEM_HEADLINE.search(title) or
                ("智能生态配件" in title and ECOSYSTEM_CAR_CONTEXT.search(title)) or
                ("人车家" in title and ECOSYSTEM_CAR_CONTEXT.search(title)) or
                ("鸿蒙座舱" in title and ECOSYSTEM_COCKPIT_CAPABILITY.search(title)) or
                (ECOSYSTEM_CROSS_DEVICE.search(title) and ECOSYSTEM_CAR_CONTEXT.search(title)))

# --------------------------------------------------------------------------
# Topic taxonomy: Chinese queries -> BMW customer-feedback domain
# --------------------------------------------------------------------------
TOPICS = [
    # id, English label, Chinese label, Google News query, BMW domain
    ("solid_state", "Solid-state batteries", "固态电池", '"固态电池"', "Energy & Charging"),
    ("sodium_ion", "Sodium-ion batteries", "钠离子电池", '"钠离子电池"', "Energy & Charging"),
    ("ultra_charging", "Megawatt / 5C ultra-charging", "兆瓦超充 / 5C", '"兆瓦超充" OR "兆瓦闪充" OR "5C超充" OR "6C电池"', "Energy & Charging"),
    ("hv_800v", "800V+ platforms & SiC", "800V高压 / 碳化硅", '"800V高压" OR "1000V高压" OR "碳化硅 电驱"', "Energy & Charging"),
    ("battery_swap", "Battery swapping", "换电", '"换电站" OR "换电网络"', "Energy & Charging"),
    ("v2g", "V2G / vehicle-grid interaction", "车网互动", '"车网互动" OR "V2G"', "Energy & Charging"),
    ("e2e_vla", "End-to-end / VLA driving models", "端到端 / VLA", '"端到端" 智驾 OR "VLA" 智驾 OR "世界模型" 智驾', "Driving Assistance"),
    ("urban_noa", "Urban NOA (city pilot)", "城市NOA", '"城市NOA" OR "城市领航"', "Driving Assistance"),
    ("l3_autonomy", "L3 conditional autonomy", "L3自动驾驶", '"L3" 自动驾驶 准入 OR "L3级" 自动驾驶', "Driving Assistance"),
    ("lidar", "Automotive LiDAR", "激光雷达", '"激光雷达" 汽车', "Driving Assistance"),
    ("robotaxi", "Robotaxi", "Robotaxi / 无人驾驶出租车", '"Robotaxi" OR "无人驾驶出租车"', "Driving Assistance"),
    ("adas_chips", "In-house ADAS chips", "智驾芯片", '"智驾芯片" OR "自研芯片" 汽车', "Driving Assistance"),
    ("cockpit_llm", "Cockpit LLMs & AI agents", "座舱大模型 / AI智能体", '"座舱大模型" OR "车载大模型" OR "AI智能体" 座舱', "Digital Cockpit & AI"),
    ("central_compute", "Central compute / cockpit-driving fusion", "舱驾一体 / 中央计算", '"舱驾一体" OR "中央计算平台" OR "中央集中式"', "Digital Cockpit & AI"),
    ("phone_car_eco", "Connected device & accessory ecosystems", "生态域 / 人车家 / 智能配件", ECOSYSTEM_DISPLAY_QUERY, "Connected Ecosystem"),
    ("ota", "OTA software updates", "OTA升级", '"OTA升级" 汽车 OR "OTA" 车型 升级', "Connected Ecosystem"),
    ("steer_by_wire", "Steer/brake-by-wire chassis", "线控转向 / 线控底盘", '"线控转向" OR "线控底盘" OR "线控制动"', "Vehicle Dynamics & Safety"),
    ("active_suspension", "Active suspension", "主动悬架", '"主动悬架" OR "全主动悬架"', "Vehicle Dynamics & Safety"),
    ("giga_casting", "Giga-casting", "一体化压铸", '"一体化压铸"', "Vehicle Dynamics & Safety"),
    ("smart_seats", "Smart cabin comfort (seats, climate)", "智能座椅 / 零重力", '"零重力座椅" OR "智能座椅" OR "座舱 舒适"', "Smart Cabin"),
    ("smart_lighting", "Smart exterior (lighting, doors)", "智能车灯 / 电动门", '"智能车灯" OR "投影大灯" OR "电动车门"', "Smart Exterior"),
]

# --------------------------------------------------------------------------
# HTTP + cache
# --------------------------------------------------------------------------
def fetch_rss(query, start, end, use_cache=True):
    """Return list of items for query in [start, end). Cached if window is closed."""
    full_q = f"{query} after:{start.isoformat()} before:{end.isoformat()}"
    key = hashlib.md5(full_q.encode()).hexdigest()
    path = os.path.join(CACHE_DIR, key + ".json")
    closed = end <= dt.date.today() - dt.timedelta(days=2)
    if use_cache and closed and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": full_q, "hl": "zh-CN", "gl": "CN", "ceid": "CN:zh-Hans"})
    raw = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            raw = urllib.request.urlopen(req, timeout=20).read()
            break
        except Exception as e:  # rate limit / transient
            time.sleep(2 * (attempt + 1))
    if raw is None:
        print(f"  ! failed: {full_q}", file=sys.stderr)
        return []

    items = []
    for it in ET.fromstring(raw).findall(".//item"):
        title = it.findtext("title") or ""
        source = it.findtext("source") or ""
        if source and title.endswith(" - " + source):
            title = title[: -len(" - " + source)]
        try:
            pub = parsedate_to_datetime(it.findtext("pubDate")).date().isoformat()
        except Exception:
            continue
        items.append({"title": title.strip(), "source": source.strip(),
                      "date": pub, "link": it.findtext("link") or ""})
    if closed:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False)
    time.sleep(0.4)
    return items


SITE_PARTITIONS = [
    "site:sina.com.cn",
    "site:sohu.com",
    "(site:autohome.com.cn OR site:dongchedi.com OR site:36kr.com OR site:gasgoo.com OR site:ithome.com)",
    "(site:eastmoney.com OR site:cls.cn OR site:stcn.com OR site:hexun.com OR site:yicai.com)",
    "-(site:sina.com.cn OR site:sohu.com OR site:autohome.com.cn OR site:dongchedi.com OR site:36kr.com OR site:gasgoo.com OR site:ithome.com OR site:eastmoney.com OR site:cls.cn OR site:stcn.com OR site:hexun.com OR site:yicai.com)"
]

KEYWORD_SUB_SPLITS = [
    "(汽车 OR 车企 OR 车型 OR 电池 OR 量产 OR 产业 OR 概念 OR 智驾 OR 科技)",
    "-(汽车 OR 车企 OR 车型 OR 电池 OR 量产 OR 产业 OR 概念 OR 智驾 OR 科技)"
]

def fetch_day_adaptive(query, day_start, day_end, use_cache):
    """
    Fetch all articles for a single day.
    If the base query hits the 100-item Google News feed quota,
    adaptively partition by domain cohorts and keyword splits to recover
    the full census without truncation.
    """
    base_items = fetch_rss(query, day_start, day_end, use_cache)
    if len(base_items) < FEED_CAP - 2:
        return base_items, False, 0  # Under quota, cleanly completed

    # Quota hit on this single day -> break through via site cohorts
    partitioned_items = []
    unresolved_sat = False
    for site_part in SITE_PARTITIONS:
        q_part = f"{query} {site_part}"
        p_items = fetch_rss(q_part, day_start, day_end, use_cache)
        if len(p_items) >= FEED_CAP - 2:
            # Sub-split by keyword qualifiers
            for kw in KEYWORD_SUB_SPLITS:
                q_kw = f"{q_part} {kw}"
                kw_items = fetch_rss(q_kw, day_start, day_end, use_cache)
                if len(kw_items) >= FEED_CAP - 2:
                    unresolved_sat = True
                partitioned_items.extend(kw_items)
        else:
            partitioned_items.extend(p_items)

    # De-duplicate articles retrieved across partitions
    seen = set()
    uniq_day = []
    for it in partitioned_items:
        k = (it["title"][:40], it["date"])
        if k not in seen:
            seen.add(k)
            uniq_day.append(it)

    recovered = max(0, len(uniq_day) - len(base_items))
    return uniq_day, unresolved_sat, recovered


def scrape_topic(topic, windows, use_cache):
    tid, _, _, query, _ = topic
    queries = ECOSYSTEM_QUERIES if tid == "phone_car_eco" else (query,)
    collected = []
    saturated_days = 0
    resolved_days = 0
    recovered_articles = 0

    for (start, end) in windows:
        for search_query in queries:
            items = fetch_rss(search_query, start, end, use_cache)
            if len(items) >= FEED_CAP - 2:  # Saturated weekly window -> split into days
                items = []
                d = start
                while d < end:
                    day_items, unres, rec = fetch_day_adaptive(search_query, d, d + dt.timedelta(days=1), use_cache)
                    if rec > 0:
                        resolved_days += 1
                        recovered_articles += rec
                    if unres:
                        saturated_days += 1
                    items.extend(day_items)
                    d += dt.timedelta(days=1)
            collected.extend(item for item in items if topic_headline_relevant(tid, item["title"]))

    if tid == "phone_car_eco":
        # Keep individually reviewed items from the earlier, broader news snapshot.
        # RSS search is ranked and does not reliably return the same older stories
        # after a query changes; retain only items still inside this run's window.
        reference_path = os.path.join(HERE, "ecosystem_reference_articles.csv")
        with open(reference_path, encoding="utf-8", newline="") as stream:
            for article in csv.DictReader(stream):
                date = dt.date.fromisoformat(article["date"])
                if windows[0][0] <= date < windows[-1][1]:
                    collected.append(article)

    # De-duplicate across windows
    seen, uniq = set(), []
    for a in collected:
        k = (a["title"][:40], a["date"])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(a)

    extra_info = []
    if resolved_days:
        extra_info.append(f"quota resolved on {resolved_days} peak day(s), +{recovered_articles} articles recovered")
    if saturated_days:
        extra_info.append(f"{saturated_days} days remained saturated")
    info_str = f"  ({'; '.join(extra_info)})" if extra_info else "  (0 quota hits)"

    print(f"  {tid:<18} {len(uniq):>5} articles{info_str}")
    return tid, uniq, saturated_days, resolved_days, recovered_articles

# --------------------------------------------------------------------------
# Statistics
# --------------------------------------------------------------------------
def binom_two_sided_p(k, n, p):
    """Exact two-sided binomial test (sum of outcomes no more likely than k)."""
    if n == 0:
        return 1.0
    def logpmf(i):
        return (math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
                + i * math.log(p) + (n - i) * math.log(1 - p))
    lk = logpmf(k)
    total = 0.0
    for i in range(n + 1):
        li = logpmf(i)
        if li <= lk + 1e-9:
            total += math.exp(li)
    return min(1.0, total)


def mann_kendall(x):
    n = len(x)
    s = sum((1 if x[j] > x[i] else -1 if x[j] < x[i] else 0)
            for i in range(n - 1) for j in range(i + 1, n))
    # tie correction
    counts = {}
    for v in x:
        counts[v] = counts.get(v, 0) + 1
    var = (n * (n - 1) * (2 * n + 5) - sum(t * (t - 1) * (2 * t + 5) for t in counts.values())) / 18
    if var <= 0:
        return 0, 0.0, 1.0
    z = (s - 1) / math.sqrt(var) if s > 0 else (s + 1) / math.sqrt(var) if s < 0 else 0.0
    p = math.erfc(abs(z) / math.sqrt(2))
    return s, z, p


def sens_slope(x):
    slopes = [(x[j] - x[i]) / (j - i) for i in range(len(x) - 1) for j in range(i + 1, len(x))]
    return statistics.median(slopes) if slopes else 0.0


def pct_rank(values, v):
    if len(values) <= 1:
        return 1.0
    below = sum(1 for x in values if x < v)
    equal = sum(1 for x in values if x == v)
    return (below + 0.5 * (equal - 1)) / (len(values) - 1)

# --------------------------------------------------------------------------
# BMW domain exposure (from our customer-feedback pipeline)
# --------------------------------------------------------------------------
def load_bmw_domains():
    path = os.path.join(HERE, "bmw_ev_technology_domain_summary.csv")
    doms = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            doms[r["technology_domain"]] = {
                "complaints": int(r["total_complaints"]),
                "share_pct": float(r["overall_share_pct"]),
                "avg_severity": float(r["avg_severity"]),
                "top_components": r["top_vfc_components"],
            }
    raw = {k: v["complaints"] * v["avg_severity"] for k, v in doms.items()}
    mx = max(raw.values())
    for k in doms:
        doms[k]["exposure"] = round(raw[k] / mx, 3)
    return doms


def load_previous_articles():
    """Reuse the other topics from the existing export when refreshing one query."""
    with open(os.path.join(HERE, "china_tech_trends.json"), encoding="utf-8") as stream:
        previous = json.load(stream)
    by_topic = {topic[0]: [] for topic in TOPICS}
    with open(os.path.join(HERE, "china_tech_trends_articles.csv"), encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["topic_id"] in by_topic:
                by_topic[row["topic_id"]].append({key: row[key] for key in ("date", "source", "title", "link")})
    return previous, by_topic

# --------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--refresh-topic", choices=[topic[0] for topic in TOPICS])
    args = parser.parse_args()
    use_cache = not args.no_cache
    os.makedirs(CACHE_DIR, exist_ok=True)
    previous, prior_articles = load_previous_articles() if args.refresh_topic else (None, None)
    today = dt.date.fromisoformat(previous["window"]["end"]) if previous else dt.date.today()
    end0 = today + dt.timedelta(days=1)
    # oldest -> newest 7-day windows
    windows = [(end0 - dt.timedelta(days=7 * (k + 1)), end0 - dt.timedelta(days=7 * k))
               for k in reversed(range(WEEKS))]
    if args.refresh_topic:
        print(f"Refreshing {args.refresh_topic} over {WEEKS} weeks ({windows[0][0]} -> {today}); reusing all other topics ...")
    else:
        print(f"Scraping {len(TOPICS)} topics x {WEEKS} weeks ({windows[0][0]} -> {today}) ...")

    if args.refresh_topic:
        prior_topics = {topic["id"]: topic for topic in previous["topics"]}
        def refresh_or_reuse(topic):
            tid = topic[0]
            if tid == args.refresh_topic:
                return scrape_topic(topic, windows, use_cache)
            old = prior_topics[tid]
            return (tid, prior_articles[tid], old.get("saturated_days", 0),
                    old.get("resolved_quota_days", 0), old.get("recovered_quota_articles", 0))
        results = [refresh_or_reuse(topic) for topic in TOPICS]
    else:
        with ThreadPoolExecutor(max_workers=4) as ex:
            results = list(ex.map(lambda t: scrape_topic(t, windows, use_cache), TOPICS))
    articles = {tid: arts for tid, arts, *rest in results}
    saturation = {tid: rest[0] for tid, arts, *rest in results}
    resolved_quota_days = {tid: rest[1] for tid, arts, *rest in results}
    recovered_quota_articles = {tid: rest[2] for tid, arts, *rest in results}

    bmw = load_bmw_domains()

    # weekly series
    def week_idx(date_str):
        d = dt.date.fromisoformat(date_str)
        for i, (s, e) in enumerate(windows):
            if s <= d < e:
                return i
        return None

    all_series = {}
    for (tid, *_rest) in TOPICS:
        series = [0] * WEEKS
        for a in articles[tid]:
            i = week_idx(a["date"])
            if i is not None:
                series[i] += 1
        all_series[tid] = series
    week_totals = [sum(s[i] for s in all_series.values()) for i in range(WEEKS)]

    # IMPORTANT: the news index keeps more recent articles than old ones, so raw
    # counts rise for *every* topic. We therefore measure each topic against the
    # basket of all OTHER tracked topics (relative share of voice). The common
    # index bias cancels out; what remains is genuine relative attention shift.
    rows = []
    for (tid, en, cn, query, domain) in TOPICS:
        series = all_series[tid]
        recent = sum(series[-RECENT_WEEKS:])
        prior = sum(series[:-RECENT_WEEKS])
        rest_recent = sum(week_totals[-RECENT_WEEKS:]) - recent
        rest_prior = sum(week_totals[:-RECENT_WEEKS]) - prior
        # relative rate ratio = (topic recent/prior) / (rest recent/prior), +0.5 smoothing
        momentum = ((recent + 0.5) / (prior + 0.5)) / ((rest_recent + 0.5) / (rest_prior + 0.5))
        # conditional binomial: given topic total, is its recent fraction different
        # from the basket's recent fraction?
        p0 = rest_recent / max(1, rest_recent + rest_prior)
        p_mom = binom_two_sided_p(recent, recent + prior, min(max(p0, 1e-6), 1 - 1e-6))
        share_series = [series[i] / week_totals[i] if week_totals[i] else 0 for i in range(WEEKS)]
        s, z, p_mk = mann_kendall(share_series)
        slope = sens_slope([v * 100 for v in share_series])  # pp of share per week
        recent_start = windows[-RECENT_WEEKS][0].isoformat()
        recent_arts = [a for a in articles[tid] if a["date"] >= recent_start]
        outlets = {}
        for a in recent_arts:
            outlets[a["source"]] = outlets.get(a["source"], 0) + 1
        headlines = sorted(recent_arts, key=lambda a: a["date"], reverse=True)[:6]
        rows.append({
            "id": tid, "label_en": en, "label_cn": cn, "query": query,
            "bmw_domain": domain,
            "weekly_counts": series,
            "weekly_share": [round(v, 4) for v in share_series],
            "volume_recent": recent, "volume_prior": prior,
            "momentum": round(momentum, 3),
            "momentum_pct_change": round((momentum - 1) * 100, 1),
            "p_momentum": round(p_mom, 5),
            "mk_z": round(z, 3), "mk_p": round(p_mk, 5),
            "sens_slope_share_pp_per_week": round(slope, 3),
            "breadth_outlets": len(outlets),
            "top_outlets": sorted(outlets.items(), key=lambda kv: -kv[1])[:5],
            "saturated_days": saturation[tid],
            "resolved_quota_days": resolved_quota_days[tid],
            "recovered_quota_articles": recovered_quota_articles[tid],
            "headlines": headlines,
        })

    total_recent = sum(r["volume_recent"] for r in rows) or 1
    vols = [r["volume_recent"] for r in rows]
    moms = [math.log(r["momentum"]) for r in rows]
    med_share = statistics.median([v / total_recent for v in vols])
    for r in rows:
        r["share_of_voice"] = round(r["volume_recent"] / total_recent, 4)
        r["attention_pct"] = round(pct_rank(vols, r["volume_recent"]), 3)
        r["momentum_pct"] = round(pct_rank(moms, math.log(r["momentum"])), 3)
        d = bmw.get(r["bmw_domain"], {"exposure": 0})
        r["bmw_exposure"] = d["exposure"]
        r["priority"] = round(100 * (0.35 * r["attention_pct"] + 0.35 * r["momentum_pct"]
                                     + 0.30 * r["bmw_exposure"]), 1)
        sig = r["p_momentum"] < 0.05
        if sig and r["momentum"] >= 1.25:
            r["signal"] = "Accelerating"
        elif sig and r["momentum"] <= 0.8:
            r["signal"] = "Cooling"
        else:
            r["signal"] = "Stable"
        high = r["share_of_voice"] >= med_share
        r["quadrant"] = ("Mainstreaming" if high and r["signal"] == "Accelerating" else
                         "Emerging" if r["signal"] == "Accelerating" else
                         "Established" if high else "Background")
    rows.sort(key=lambda r: -r["priority"])

    all_sources = {a["source"] for arts in articles.values() for a in arts}
    out = {
        "generated_at": previous["generated_at"] if previous else dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "window": {"start": windows[0][0].isoformat(), "end": today.isoformat(),
                   "weeks": WEEKS, "recent_weeks": RECENT_WEEKS,
                   "week_starts": [s.isoformat() for s, _ in windows]},
        "source": "Google News China edition (zh-CN), aggregating Chinese outlets",
        "totals": {"articles": sum(len(a) for a in articles.values()),
                   "outlets": len(all_sources), "topics": len(rows)},
        "bmw_domains": bmw,
        "method": {
            "momentum": f"Relative rate ratio: topic growth (last {RECENT_WEEKS} wks vs prior {WEEKS - RECENT_WEEKS}) divided by the growth of all other tracked topics. Cancels the news index's recency bias. 1.0 = growing in line with the basket.",
            "p_momentum": "Exact conditional binomial test: is the topic's recent fraction of articles different from the basket's recent fraction? (H0: no relative shift)",
            "trend": "Mann-Kendall monotonic trend test on the weekly share of voice; Sen's slope = robust share change (percentage points per week).",
            "breadth": f"Distinct outlets publishing on the topic in last {RECENT_WEEKS} weeks.",
            "exposure": "BMW domain complaints x avg severity (from bmw_ev_technology_domain_summary.csv), normalised 0-1.",
            "priority": "100 x (0.35 attention percentile + 0.35 momentum percentile + 0.30 BMW exposure).",
            "signal": "Accelerating: momentum >= 1.25 and p < 0.05; Cooling: momentum <= 0.8 and p < 0.05; else Stable.",
            "quota_resolution": "Adaptive multi-tier domain & keyword partitioning: when peak news days hit the Google News 100-item query quota, queries are dynamically partitioned across 5 media cohorts (Sina, Sohu, Auto specialists, Financial press, Remainder) and sub-split to recover the full census without truncation.",
        },
        "topics": rows,
    }

    with open(os.path.join(HERE, "china_tech_trends.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    with open(os.path.join(HERE, "china_tech_trends_data.js"), "w", encoding="utf-8") as f:
        f.write("window.CHINA_TRENDS = " + json.dumps(out, ensure_ascii=False) + ";\n")
    with open(os.path.join(HERE, "china_tech_trends_articles.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["topic_id", "bmw_domain", "date", "source", "title", "link"])
        dom = {t[0]: t[4] for t in TOPICS}
        for tid, arts in articles.items():
            for a in sorted(arts, key=lambda a: a["date"]):
                w.writerow([tid, dom[tid], a["date"], a["source"], a["title"], a["link"]])

    print(f"\nDone: {out['totals']['articles']} articles from {out['totals']['outlets']} outlets.")
    print(f"{'topic':<20}{'4wk':>6}{'Δ%':>8}{'p':>9}{'MK p':>8}{'outlets':>9}{'prio':>7}  signal")
    for r in rows:
        print(f"{r['id']:<20}{r['volume_recent']:>6}{r['momentum_pct_change']:>8}{r['p_momentum']:>9.3f}"
              f"{r['mk_p']:>8.3f}{r['breadth_outlets']:>9}{r['priority']:>7}  {r['signal']}")


if __name__ == "__main__":
    main()
