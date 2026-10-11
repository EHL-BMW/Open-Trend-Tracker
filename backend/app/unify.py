"""Unified input processor: both branches -> observations -> hierarchical, quantified tree per vehicle.

    uv run python -m app.unify

Writes to data/unified/:
    <VEHICLE>.json         Vehicle -> Market (+ALL) -> Category -> Attribute -> Metric, with obs_ids
    observations.jsonl     every observation with its RawRef (the raw <-> unified link)
    coverage.json          per source: mapped vs unmapped, and the unmapped labels to curate next
    report.html            human-readable view of all of the above, open in a browser
"""
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

from app import external, internal, report
from app.mapping import Mapper
from app.paths import EXTERNAL_DIR, UNIFIED_DIR
from app.schema import AttributeNode, CategoryNode, MarketNode, MetricSummary, Observation, VehicleNode

LINES = {"F70": "BMW 1 Series", "G60": "BMW 5 Series", "G68": "BMW 5 Series Long Wheelbase (China)",
         "G70": "BMW 7 Series"}
ADDITIVE_UNITS = {"count", "units"}  # summed when aggregating; everything else is averaged


def summarize(obs: list[Observation]) -> dict[str, MetricSummary]:
    groups = defaultdict(list)
    for o in obs:
        groups[o.metric].append(o)
    out = {}
    for metric, g in sorted(groups.items()):
        values = [o.value for o in g]
        norms = [o.norm for o in g if o.norm is not None]
        out[metric] = MetricSummary(
            value=sum(values) if g[0].unit in ADDITIVE_UNITS else mean(values), unit=g[0].unit,
            norm=mean(norms) if norms else None, n=len(g), sources=sorted({o.source for o in g}),
            obs_ids=[o.id for o in g])
    # derived: share of positive among polar feedback mentions (internal feedback + external comments)
    likes = out["like"].value if "like" in out else 0
    negatives = sum(out[m].value for m in ("difficult_to_use", "defect") if m in out)
    if likes + negatives:
        balance = likes / (likes + negatives)
        out["feedback_balance"] = MetricSummary(
            value=balance, unit="share", norm=balance, n=int(likes + negatives),
            sources=sorted({s for m in ("like", "difficult_to_use", "defect") if m in out for s in out[m].sources}),
            obs_ids=[])  # derived: evidence sits in like / difficult_to_use / defect
    return out


def attribute_node(attr_id: str, info: dict, obs: list[Observation]) -> AttributeNode:
    own = [o for o in obs if o.competitor is None]
    metrics = summarize(own)
    by_competitor = defaultdict(list)
    for o in obs:
        if o.competitor:
            by_competitor[o.competitor].append(o)
    origins = {o.origin for o in obs}
    status = ("both" if len(origins) == 2 else "internal_only" if origins == {"internal"}
              else "external_only" if origins == {"external"} else "no_data")
    norms = [m.norm for m in metrics.values() if m.norm is not None]
    return AttributeNode(
        id=attr_id, name=info["name"], status=status,
        score=mean(norms) if norms else None, sources=dict(Counter(o.source for o in obs)),
        features=dict(Counter(o.raw_label for o in obs).most_common()), metrics=metrics,
        competitors={c: summarize(g) for c, g in sorted(by_competitor.items())})


def market_node(market: str, obs: list[Observation], mapper: Mapper) -> MarketNode:
    by_attr = defaultdict(list)
    for o in obs:
        if o.attribute:
            by_attr[o.attribute].append(o)
    categories = {}
    for cat_id, cat_name in mapper.categories.items():
        attrs = {a: attribute_node(a, info, by_attr.get(a, []))
                 for a, info in mapper.attributes.items() if info["category"] == cat_id}
        scores = [a.score for a in attrs.values() if a.score is not None]
        categories[cat_id] = CategoryNode(id=cat_id, name=cat_name, score=mean(scores) if scores else None,
                                          attributes=attrs)
    unmapped = Counter(o.raw_label or "(unlabelled comment)" for o in obs if not o.attribute)
    return MarketNode(market=market, n_observations=len(obs), categories=categories,
                      unmapped=dict(unmapped.most_common()))


def build(obs: list[Observation], mapper: Mapper) -> dict[str, VehicleNode]:
    by_vehicle = defaultdict(list)
    for o in obs:
        by_vehicle[o.vehicle].append(o)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    trees = {}
    for v, vobs in sorted(by_vehicle.items()):
        markets = {m: market_node(m, [o for o in vobs if o.market == m], mapper)
                   for m in sorted({o.market for o in vobs})}
        markets["ALL"] = market_node("ALL", vobs, mapper)
        trees[v] = VehicleNode(vehicle=v, line=LINES.get(v, v), taxonomy_version=mapper.version, generated_at=now,
                               markets=markets)
    return trees


def collect(external_dir: Path = EXTERNAL_DIR) -> tuple[list[Observation], Mapper]:
    mapper = Mapper()
    obs = internal.load() + external.load(external_dir)
    mapper.apply(obs)
    return obs, mapper


def coverage(obs: list[Observation], mapper: Mapper) -> dict:
    return {
        "taxonomy_version": mapper.version,
        "observations": len(obs),
        "by_source": dict(Counter(o.source for o in obs)),
        "mapped_by_alias": dict(Counter(o.source for o in obs if o.mapped_by == "alias")),
        "mapped_by_keyword": dict(Counter(o.source for o in obs if o.mapped_by == "keyword")),
        "unmapped": dict(Counter(o.source for o in obs if not o.attribute)),
        "unmapped_labels": {src: dict(Counter(o.raw_label or "(unlabelled comment)" for o in obs
                                              if o.source == src and not o.attribute).most_common())
                            for src in sorted({o.source for o in obs if not o.attribute})},
    }


def main() -> None:
    obs, mapper = collect()
    UNIFIED_DIR.mkdir(parents=True, exist_ok=True)
    trees = build(obs, mapper)
    for v, tree in trees.items():
        (UNIFIED_DIR / f"{v}.json").write_text(tree.model_dump_json(indent=1))
    with open(UNIFIED_DIR / "observations.jsonl", "w") as f:
        for o in obs:
            f.write(o.model_dump_json() + "\n")
    cov = coverage(obs, mapper)
    (UNIFIED_DIR / "coverage.json").write_text(json.dumps(cov, indent=1, ensure_ascii=False))
    report.write(UNIFIED_DIR / "report.html", trees, obs, cov)
    print(f"{cov['observations']} observations -> {UNIFIED_DIR}")
    print("alias:   ", cov["mapped_by_alias"])
    print("keyword: ", cov["mapped_by_keyword"])
    print("unmapped:", cov["unmapped"])


if __name__ == "__main__":
    main()
