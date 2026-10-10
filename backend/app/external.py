"""External branch: records in data/external/*.jsonl -> Observations.

This JSONL format is the contract. Raw external material (technical PDFs, social media dumps, ...)
is first turned into it, for now in a chat session (see CLAUDE.md), later by an automated step.
One record per line, two types:

  {"type": "comment", "source": "reddit", "vehicle": "G60", "country": "DE",            # or "market": "EU"
   "label": "Apple CarPlay", "sentiment": "defect", "text": "...", "url": "...", "retrieved_at": "2026-10-01"}
  {"type": "metric",  "source": "spec_sheet", "vehicle": "G60", "market": "EU",
   "competitor": "Mercedes-Benz E-Class", "label": "DC charging power", "metric": "max_dc_charging_power",
   "value": 0, "unit": "kW", "norm": null, "text": "quote", "url": "...", "retrieved_at": "..."}

sentiment: like | want | difficult_to_use | defect | mention. A comment without a label is kept but
counts as unmapped until it is labelled.
"""
import json
from pathlib import Path

from app.internal import market_of
from app.paths import DATA_DIR, EXTERNAL_DIR
from app.schema import Observation, RawRef


def _rel(path: Path) -> str:
    return str(path.relative_to(DATA_DIR)) if path.is_relative_to(DATA_DIR) else str(path)


def jsonl(path: Path) -> list[Observation]:
    out = []
    for n, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        r = json.loads(line)
        common = dict(
            id=f"ext:{path.stem}:{n}", origin="external", source=f"ext:{r['source']}", vehicle=r["vehicle"],
            market=r.get("market") or market_of(r.get("country")), country=r.get("country"),
            competitor=r.get("competitor"), raw_label=r.get("label") or "", period=r.get("retrieved_at"),
            text=r.get("text"),
            raw=RawRef(file=_rel(path), locator=f"line={n}" + (f" url={r['url']}" if r.get("url") else "")),
        )
        if r["type"] == "comment":
            out.append(Observation(metric=r.get("sentiment") or "mention", value=1, unit="count", **common))
        else:
            out.append(Observation(metric=r["metric"], value=r["value"], unit=r["unit"], norm=r.get("norm"),
                                   **common))
    return out


def load(folder: Path = EXTERNAL_DIR) -> list[Observation]:
    return [o for path in sorted(folder.glob("*.jsonl")) for o in jsonl(path)]
