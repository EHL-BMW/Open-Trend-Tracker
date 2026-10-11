"""External branch: files in data/external/ -> Observations.

Two readers: the generic JSONL contract below, and an adapter for the European EV/PHEV market table.

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
import re
from pathlib import Path

import pandas as pd

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


# --- European EV/PHEV market table (top_500_ev_phev_europe*.csv) --------------------------
# One row per model variant: Europe sales, price, specs, and German feature lists.
# BMW rows of our vehicles become the vehicle's own external facts; non-BMW-Group rows in the
# same segment become its competitors. Spec metrics are split by powertrain (e.g. wltp_range_bev) and
# get a norm = percentile within segment and powertrain, so a PHEV is never ranked against a BEV.

OUR_VEHICLES = {  # vehicle -> segment, and which BMW rows are that vehicle (model, required word in variant)
    "F70": {"segment": "C-Segment", "rows": []},  # 1 Series is ICE only: competitors, no own row
    "G60": {"segment": "E-Segment", "rows": [("5er", "Limousine"), ("i5", "Limousine")]},  # Touring = G61
    "G70": {"segment": "F-Segment", "rows": [("7er", ""), ("i7", "")]},
}
BMW_GROUP = {"BMW", "MINI", "Rolls-Royce"}

# column -> (attribute label, metric, unit, higher_is_better); the label goes through taxonomy.json
SPECS = {
    "europe_sales_units": ("sales_volume", "ev_phev_sales_eu", "units", None),
    "base_price_eur": ("Value for money", "base_price", "EUR", False),
    "battery_capacity_kwh": ("High-voltage battery", "battery_capacity", "kWh", True),
    "electric_range_wltp_km": ("Electric range", "wltp_range", "km", True),
    "power_kw": ("Powertrain & acceleration", "power", "kW", True),
    "accel_0_100_s": ("Powertrain & acceleration", "accel_0_100", "s", False),
    "top_speed_kmh": ("Powertrain & acceleration", "top_speed", "km/h", True),
    "dc_charging_kw": ("Charging experience", "dc_charging_power", "kW", True),
    "charging_time_10_80_min": ("Charging experience", "charging_time_10_80", "min", False),
    "efficiency": ("Energy & fuel efficiency", "consumption", "kWh/100km", False),
    "heat_pump": ("Energy & fuel efficiency", "heat_pump_standard", "flag", True),
    "towing_capacity_kg": ("Versatility & towing", "towing_capacity", "kg", True),
    "frunk_liters": ("Luggage & cargo", "frunk_volume", "L", True),
    "trunk_liters": ("Luggage & cargo", "trunk_volume", "L", True),
}
FEATURE_COLUMNS = ["audio_system", "head_up_display", "unique_selling_points", "interior_highlights",
                   "exterior_highlights", "driver_assistance"]
# feature phrases that only restate a spec column above (the number is already captured there)
RESTATEMENT = re.compile(r"^(Offizielle WLTP-Reichweite|Optimierter Energieverbrauch|Fortschrittlicher \w+-Antriebsstrang"
                         r"|Schnellladung mit bis zu|Schnellladefähigkeit mit bis zu|Bis zu [\d.,\s-]+ ?kg Anhängelast"
                         r"|Bis zu [\d.,]+ km|Reichweitenstarke Batterie|Bis zu \d+ km WLTP|Bis zu [\d.]+ kg)")


def _number(value) -> float | None:
    """'16.9 kWh/100km' -> 16.9, '854 – 2.158 L (...)' -> 854, 'Serienmäßig' -> 1, 0 / NaN -> None."""
    if isinstance(value, str):
        if value in ("Serienmäßig", "Optional"):
            return 1.0 if value == "Serienmäßig" else 0.0
        m = re.match(r"\s*([\d.]+(?:,\d+)?)", value)
        if not m:
            return None
        text = m.group(1)
        return float(text.replace(".", "").replace(",", ".")) if "," in text or re.fullmatch(r"\d{1,3}(\.\d{3})+", text) \
            else float(text)
    return None if pd.isna(value) else float(value)


def ev_market(path: Path) -> list[Observation]:
    df = pd.read_csv(path, sep=";")
    for col in SPECS:
        df[col] = df[col].map(_number)
    # a 10-80 % time only means something with DC fast charging (the table lists one even for PHEVs without DC)
    df.loc[(df["charging_time_10_80_min"] == 0) | (df["dc_charging_kw"] == 0), "charging_time_10_80_min"] = None
    norms = {}  # column -> per-row percentile within segment, oriented so higher = better
    for col, (_, _, _, higher) in SPECS.items():
        if higher is not None:
            norms[col] = df.groupby(["segment", "powertrain"])[col].rank(pct=True, ascending=higher)

    out = []
    for i, r in df.iterrows():
        own = [v for v, cfg in OUR_VEHICLES.items() if r["brand"] == "BMW"
               and any(r["model"] == m and word in r["variant"] for m, word in cfg["rows"])]
        rivals = [] if r["brand"] in BMW_GROUP else \
            [v for v, cfg in OUR_VEHICLES.items() if cfg["segment"] == r["segment"]]
        name = f"{r['brand']} {r['model']}"
        for vehicle, competitor in [(v, None) for v in own] + [(v, name) for v in rivals]:
            common = dict(origin="external", source="ext:ev_market_eu", vehicle=vehicle, market="EU",
                          competitor=competitor)
            ref = lambda col: RawRef(file=_rel(path), locator=f"row={i + 2} col={col} url={r['adac_url']}")
            for col, (label, metric, unit, _) in SPECS.items():
                if pd.notna(r[col]):
                    norm = norms[col][i] if col in norms and pd.notna(norms[col][i]) else None
                    if col != "europe_sales_units":  # sales add up across powertrains, specs do not
                        metric = f"{metric}_{r['powertrain'].lower()}"
                    out.append(Observation(id=f"ev:{r['rank']}:{vehicle}:{col}", raw_label=label, metric=metric,
                                           value=r[col], unit=unit, norm=norm, text=f"{name} {r['variant']}",
                                           raw=ref(col), **common))
            for col in FEATURE_COLUMNS:
                items = [s.strip() for s in str(r[col]).split("|")] if pd.notna(r[col]) else []
                for k, item in enumerate(items):
                    if item and not RESTATEMENT.match(item) and "kein " not in item:
                        out.append(Observation(id=f"ev:{r['rank']}:{vehicle}:{col}:{k}", raw_label=item,
                                               metric="has_feature", value=1, unit="flag",
                                               text=f"{name} {r['variant']}: {item}", raw=ref(col), **common))
    return out


def load(folder: Path = EXTERNAL_DIR) -> list[Observation]:
    out = [o for path in sorted(folder.glob("*.jsonl")) for o in jsonl(path)]
    for path in sorted(folder.glob("top_500_ev_phev_europe*.csv")):
        out += ev_market(path)
    return out
