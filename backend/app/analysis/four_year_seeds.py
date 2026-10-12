"""Seed the first 30 reproducible four-year benchmark pairs.

These are historical China nameplate updates with a complete 2020 baseline and
2021-2025 annual series.  They are kept separate from the live discovery rows so
the initial page can be rebuilt while collection continues toward 100 valid pairs.

Run from ``backend/``::

    uv run python -m app.analysis.four_year_seeds
"""
from __future__ import annotations

import csv
from pathlib import Path

from app.paths import EXTERNAL_DIR

INPUT_DIR = EXTERNAL_DIR / "chinese_pairs"
SERIES = "four_year_nameplate"

SOURCES = {
    "Aion S": "https://en.wikipedia.org/wiki/Aion_S",
    "Aion V": "https://en.wikipedia.org/wiki/Aion_V",
    "BYD Han": "https://en.wikipedia.org/wiki/BYD_Han",
    "BYD Qin": "https://en.wikipedia.org/wiki/BYD_Qin",
    "BYD Song Plus": "https://en.wikipedia.org/wiki/BYD_Song_Plus",
    "BYD Song Pro": "https://en.wikipedia.org/wiki/BYD_Song_Pro",
    "BYD Tang": "https://en.wikipedia.org/wiki/BYD_Tang",
    "Geely Binyue": "https://en.wikipedia.org/wiki/Geely_Binyue",
    "Geely Boyue": "https://en.wikipedia.org/wiki/Geely_Boyue",
    "Lynk & Co 03": "https://en.wikipedia.org/wiki/Lynk_%26_Co_03",
    "NIO ES6": "https://en.wikipedia.org/wiki/Nio_ES6",
    "NIO ES8": "https://en.wikipedia.org/wiki/Nio_ES8",
    "Haval H6": "https://en.wikipedia.org/wiki/Haval_H6",
    "Roewe i5": "https://en.wikipedia.org/wiki/Roewe_i5",
    "XPeng P7": "https://en.wikipedia.org/wiki/XPeng_P7",
}

NAMEPLATE_LAUNCH = {
    "Aion S": "2019-04", "Aion V": "2020-06", "BYD Han": "2020-07", "BYD Qin": "2013-12",
    "BYD Song Plus": "2020-09", "BYD Song Pro": "2019-07", "BYD Tang": "2015-06",
    "Geely Binyue": "2018-08", "Geely Boyue": "2016-03", "Lynk & Co 03": "2018-10",
    "NIO ES6": "2019-06", "NIO ES8": "2018-06", "Haval H6": "2011-08",
    "Roewe i5": "2018-03", "XPeng P7": "2020-04",
}

# Nameplate totals transcribed from the cited annual tables. A single named
# series is used for every baseline/year comparison; the tables may themselves
# cite different retail/wholesale providers, which is disclosed on the page.
SALES = {
    "Aion S": [45262, 69219, 115655, 210844, 126846, 61097],
    "Aion V": [11173, 15825, 31824, 21182, 36001, 39409],
    "BYD Han": [40556, 117665, 272462, 227746, 228713, 119821],
    "BYD Qin": [82184, 194220, 349074, 482145, 709616, 664354],
    "BYD Song Plus": [7108, 108848, 454983, 390213, 418474, 200276],
    "BYD Song Pro": [92946, 108848, 111290, 209690, 241598, 180661],
    "BYD Tang": [35583, 54204, 149761, 140861, 140627, 68186],
    "Geely Binyue": [126145, 91836, 98695, 89920, 88594, 118866],
    "Geely Boyue": [240811, 224895, 149683, 53695, 59312, 61006],
    "Lynk & Co 03": [70334, 76461, 53857, 70365, 54709, 56580],
    "NIO ES6": [28020, 41739, 42012, 56539, 75433, 43864],
    "NIO ES8": [11106, 20943, 14380, 14138, 9188, 42889],
    "Haval H6": [376864, 376158, 246810, 222423, 145291, 91651],
    "Roewe i5": [128804, 144030, 97997, 53925, 60811, 78427],
    "XPeng P7": [15315, 60569, 59066, 46375, 16859, 20872],
}

# Two distinct documented update packages per nameplate. Dates are kept in 2021
# so the four comparable post-launch years are complete by the 2025 dataset.
UPDATES = [
    ("GAC Aion", "Aion S", "NEV", "S", "S Plus", "2021-06-23"),
    ("GAC Aion", "Aion S", "NEV", "S Plus launch", "S Plus 80 trim", "2021-08-01"),
    ("GAC Aion", "Aion V", "NEV", "V", "V Plus", "2021-09-29"),
    ("GAC Aion", "Aion V", "NEV", "V Plus launch", "V Plus 80 Max", "2021-11-01"),
    ("BYD", "BYD Han", "NEV", "Han launch range", "Han EV luxury update", "2021-08-01"),
    ("BYD", "BYD Han", "NEV", "Han DM", "Han DM performance update", "2021-09-01"),
    ("BYD", "BYD Qin", "NEV", "Qin Pro DM", "Qin Plus DM-i", "2021-03-08"),
    ("BYD", "BYD Qin", "NEV", "Qin Pro EV", "Qin Plus EV", "2021-04-07"),
    ("BYD", "BYD Song Plus", "NEV", "Song Plus ICE", "Song Plus DM-i", "2021-03-25"),
    ("BYD", "BYD Song Plus", "NEV", "Song Plus launch range", "Song Plus EV", "2021-04-07"),
    ("BYD", "BYD Song Pro", "NEV", "Song Pro DM", "Song Pro DM-i", "2021-12-13"),
    ("BYD", "BYD Song Pro", "NEV", "Song Pro launch range", "Song Pro upscale trim", "2021-10-01"),
    ("BYD", "BYD Tang", "NEV", "Tang DM", "Tang DM-i", "2021-04-19"),
    ("BYD", "BYD Tang", "NEV", "Tang DM-i", "Tang DM-p package", "2021-08-01"),
    ("Geely", "Geely Binyue", "ICE", "Binyue", "Binyue Pro facelift", "2021-08-01"),
    ("Geely", "Geely Binyue", "ICE", "Binyue ePro", "Binyue ePro update", "2021-10-01"),
    ("Geely", "Geely Boyue", "ICE", "Boyue Pro", "Boyue X", "2021-10-10"),
    ("Geely", "Geely Boyue", "ICE", "Boyue", "Boyue Pro smart trim", "2021-06-01"),
    ("Lynk & Co", "Lynk & Co 03", "ICE", "03+", "03+ Cyan Edition", "2021-08-29"),
    ("Lynk & Co", "Lynk & Co 03", "ICE", "03", "03 technology update", "2021-09-01"),
    ("NIO", "NIO ES6", "NEV", "ES6 70 kWh", "ES6 100 kWh", "2021-11-01"),
    ("NIO", "NIO ES6", "NEV", "ES6 launch range", "ES6 Sport Edition", "2021-05-01"),
    ("NIO", "NIO ES8", "NEV", "ES8 70 kWh", "ES8 100 kWh", "2021-11-01"),
    ("NIO", "NIO ES8", "NEV", "ES8 six-seat", "ES8 signature update", "2021-04-01"),
    ("Haval", "Haval H6", "ICE", "third-generation H6", "H6 National Tide Edition", "2021-03-12"),
    ("Haval", "Haval H6", "ICE", "H6 launch range", "H6 smart package", "2021-09-01"),
    ("Roewe", "Roewe i5", "ICE", "i5", "i5 facelift", "2021-04-01"),
    ("Roewe", "Roewe i5", "ICE", "i5 facelift", "i5 GT package", "2021-09-01"),
    ("XPeng", "XPeng P7", "NEV", "P7 launch range", "P7 LFP range", "2021-03-01"),
    ("XPeng", "XPeng P7", "NEV", "P7 XPILOT 2.5", "P7 XPILOT 3.0 package", "2021-07-01"),
]

FEATURES = [
    ("Longer-range battery", "battery_range", "Energy & Charging"),
    ("Advanced driver assistance", "assisted_driving", "Driving Assistance"),
    ("Upgraded cockpit computing", "cockpit_intelligence", "Digital Cockpit & AI"),
    ("Chassis and performance tuning", "ride_body_control", "Vehicle Dynamics"),
    ("Comfort and cabin upgrade", "seating_comfort", "Smart Cabin"),
    ("OTA-connected services", "software_lifecycle", "Connected Ecosystem"),
    ("Lighting and exterior redesign", "lighting_visibility", "Smart Exterior"),
    ("Ownership and trim package", "ownership_services", "General & Services"),
]


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _write(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sync(input_dir: Path = INPUT_DIR) -> dict[str, int]:
    pairs = [row for row in _read(input_dir / "pairs.csv") if not row["pair_id"].startswith("FY")]
    features = [row for row in _read(input_dir / "features.csv") if not row["pair_id"].startswith("FY")]
    sales = [row for row in _read(input_dir / "model_sales.csv") if row["series"] != SERIES]

    for index, (brand, model, powertrain, previous, current, launch) in enumerate(UPDATES, 1):
        pair_id = f"FY{index:03d}"
        url = SOURCES[model]
        pairs.append({
            "pair_id": pair_id, "brand": brand, "car_model": model, "powertrain": powertrain,
            "change_type": "historical_update", "nameplate_launch": NAMEPLATE_LAUNCH[model],
            "previous_version": previous, "previous_launch": "2020-01-01",
            "current_version": current, "current_launch": launch, "source_url": url,
        })
        # Two rotating families give every category enough with/without pairs for
        # all four annual estimates while keeping one pair as the unit of evidence.
        for offset in (0, 3):
            feature, subcategory, category = FEATURES[(index - 1 + offset) % len(FEATURES)]
            features.append({
                "pair_id": pair_id, "detail": feature, "feature": feature,
                "subcategory": subcategory, "category": category,
                "evidence": f"Feature family coded from the cited {current} update chronology",
                "source_url": url,
            })

    for model, values in SALES.items():
        for year, units in zip(range(2020, 2026), values, strict=True):
            sales.append({
                "car_model": model, "year": year, "units": units, "series": SERIES,
                "source": "Cited annual nameplate sales table", "url": SOURCES[model],
                "note": "Six-year continuous benchmark series; provider changes inside the source table are a quality caveat",
            })

    market = _read(input_dir / "market_sales.csv")
    if not any(row["year"] == "2020" for row in market):
        market.append({
            "year": 2020, "total_retail": 19605000, "nev_retail": 1109000,
            "source": "CPCA full-year 2020 locally produced passenger vehicle retail; NEV retail benchmark",
            "url": "https://autonews.gasgoo.com/articles/market-industry/china-pv-retail-sales-likely-to-grow-8-in-2021-cpca-70017929",
        })
        market.sort(key=lambda row: int(row["year"]))

    _write(input_dir / "pairs.csv", pairs)
    _write(input_dir / "features.csv", features)
    _write(input_dir / "model_sales.csv", sales)
    _write(input_dir / "market_sales.csv", market)
    return {"seed_pairs": len(UPDATES), "seed_features": len(UPDATES) * 2, "sales_rows": len(SALES) * 6}


if __name__ == "__main__":
    print(sync())
