"""Seed reproducible four-year benchmark pairs.

These are historical China nameplate updates with a complete 2020 baseline and
2021-2025 annual series.  They are kept separate from the live discovery rows so
the page can be rebuilt while collection continues toward 100 valid pairs.

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
    "Wuling Hongguang Mini EV": "https://en.wikipedia.org/wiki/Wuling_Hongguang_Mini_EV",
    "XPeng G3": "https://en.wikipedia.org/wiki/XPeng_G3",
    "Neta V": "https://en.wikipedia.org/wiki/Neta_V",
    "Baojun RS-3": "https://en.wikipedia.org/wiki/Baojun_RS-3",
    "Chery Tiggo 7": "https://en.wikipedia.org/wiki/Chery_Tiggo_7",
    "Buick Envision": "https://en.wikipedia.org/wiki/Buick_Envision",
    "Lynk & Co 05": "https://en.wikipedia.org/wiki/Lynk_%26_Co_05",
    "Exeed TX": "https://en.wikipedia.org/wiki/Exeed_TX",
    "Geely Jiaji": "https://en.wikipedia.org/wiki/Geely_Jiaji",
}

NAMEPLATE_LAUNCH = {
    "Aion S": "2019-04", "Aion V": "2020-06", "BYD Han": "2020-07", "BYD Qin": "2013-12",
    "BYD Song Plus": "2020-09", "BYD Song Pro": "2019-07", "BYD Tang": "2015-06",
    "Geely Binyue": "2018-08", "Geely Boyue": "2016-03", "Lynk & Co 03": "2018-10",
    "NIO ES6": "2019-06", "NIO ES8": "2018-06", "Haval H6": "2011-08",
    "Roewe i5": "2018-03", "XPeng P7": "2020-04",
    "Wuling Hongguang Mini EV": "2020-07", "XPeng G3": "2018-12",
    "Neta V": "2020-11", "Baojun RS-3": "2019-10", "Chery Tiggo 7": "2016-03",
    "Buick Envision": "2014-10", "Lynk & Co 05": "2020-05",
    "Exeed TX": "2019-04", "Geely Jiaji": "2019-03",
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
    "Wuling Hongguang Mini EV": [127651, 395451, 404823, 237863, 261141, 424983],
    "XPeng G3": [11691, 29721, 17336, 5301, 813, 35],
    "Neta V": [3033, 49646, 71158, 35327, 2638, 11],
    "Baojun RS-3": [66587, 18202, 2642, 307, 1, 3],
    "Chery Tiggo 7": [64991, 91331, 53659, 52686, 56556, 45594],
    "Buick Envision": [167880, 146476, 130181, 143054, 118471, 166894],
    "Lynk & Co 05": [32502, 22538, 8995, 3264, 819, 77],
    "Exeed TX": [13482, 37154, 53441, 34447, 34104, 12304],
    "Geely Jiaji": [28772, 12178, 6933, 2669, 1847, 959],
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

# Additional documented 2021 trims and updates. Each row is a distinct
# previous/current version pair. Feature evidence is specific to the cited
# launch source rather than inferred from the annual sales movement.
CURATED_UPDATES = [
    {
        "brand": "Wuling", "model": "Wuling Hongguang Mini EV", "powertrain": "NEV",
        "previous": "Hongguang Mini EV base range", "current": "Mini EV Macaron Fashion (120 km)",
        "launch": "2021-04-08", "source": "https://www.sohu.com/a/459689687_115333",
        "features": [
            ("Three Macaron colors with optional contrast roof", "Exterior color personalization", "exterior_personalization", "Smart Exterior", "Launch coverage documents three exclusive colors and two roof choices"),
            ("Driver airbag and pedestrian warning added as standard", "Expanded active and passive safety", "passive_safety", "Smart Cabin", "Macaron launch added standard driver protection and low-speed warning equipment"),
        ],
    },
    {
        "brand": "Wuling", "model": "Wuling Hongguang Mini EV", "powertrain": "NEV",
        "previous": "Hongguang Mini EV base range", "current": "Mini EV Macaron Luxury (170 km)",
        "launch": "2021-04-08", "source": "https://www.sohu.com/a/459689687_115333",
        "features": [
            ("170 km single-charge range", "Longer-range battery", "battery_range", "Energy & Charging", "The Luxury version is the documented 170 km Macaron configuration"),
            ("Three Macaron colors with optional contrast roof", "Exterior color personalization", "exterior_personalization", "Smart Exterior", "Launch coverage documents three exclusive colors and two roof choices"),
        ],
    },
    *[
        {
            "brand": "XPeng", "model": "XPeng G3", "powertrain": "NEV",
            "previous": "XPeng G3", "current": f"XPeng G3i {trim}", "launch": "2021-07-09",
            "source": "https://cnevpost.com/2021/07/09/xpeng-g3i-goes-on-sale-with-prices-starting-at-about-23100/",
            "features": [
                (f"{range_km} km NEDC range", "Longer-range battery", "battery_range", "Energy & Charging", f"The launch lists the {trim} in the {range_km} km range family"),
                ("X Robot Face light-bar fascia and hidden door handles", "Lighting and exterior redesign", "lighting_visibility", "Smart Exterior", "The G3i launch documents the P7/P5-style light bar and hidden handles"),
                *(([("XPILOT 2.5 assisted-driving hardware", "Advanced driver assistance", "assisted_driving", "Driving Assistance", "N trims include the documented XPILOT 2.5 assistance package")]) if trim.endswith("N") else []),
            ],
        }
        for trim, range_km in (("460G", 460), ("460N", 460), ("520G", 520), ("520N", 520))
    ],
    *[
        {
            "brand": "Neta", "model": "Neta V", "powertrain": "NEV", "previous": "Neta V",
            "current": f"Neta V Pro {trim}", "launch": "2021-11-03",
            "source": "https://carnewschina.com/2021/11/04/neta-v-pro-launched-at-11990-with-a-401km-range/",
            "features": [
                ("401 km NEDC range from a 38.54 kWh battery", "Longer-range battery", "battery_range", "Energy & Charging", "Both V Pro versions use the documented 401 km battery configuration"),
                ("Qihoo 360 in-vehicle cybersecurity protection", "Connected-vehicle security", "software_lifecycle", "Connected Ecosystem", "The V Pro launch identifies the Qihoo 360 safety protection system"),
            ],
        }
        for trim in ("Long Endurance Smart Fun", "Long Endurance Smart Enjoy")
    ],
    *[
        {
            "brand": "Baojun", "model": "Baojun RS-3", "powertrain": "ICE", "previous": "RS-3 1.5L",
            "current": f"RS-3 1.5T {trim}", "launch": "2021-01",
            "source": "https://en.wikipedia.org/wiki/Baojun_RS-3",
            "features": [
                ("145 hp 1.5-litre turbo engine", "Turbocharged powertrain upgrade", "powertrain_performance", "Vehicle Dynamics", "The 2021 model-year source documents the 1.5T engine on these trims"),
                ("Continuously variable automatic transmission", "Powertrain calibration update", "powertrain_performance", "Vehicle Dynamics", "The turbo engine is documented with a continuously variable transmission"),
            ],
        }
        for trim in ("Smart Lofty", "Smart Elite", "Smart Luxury")
    ],
    {
        "brand": "Chery", "model": "Chery Tiggo 7", "powertrain": "ICE",
        "previous": "second-generation Tiggo 7", "current": "Tiggo 7 Plus 1.5T mild hybrid",
        "launch": "2021-09-27", "source": "https://en.wikipedia.org/wiki/Chery_Tiggo_7",
        "features": [
            ("48-volt mild-hybrid powertrain", "New hybrid system", "hybrid_powertrain", "Energy & Charging", "The 2021 Plus launch introduced a documented 48-volt mild-hybrid option"),
            ("Lion 4.0 infotainment with CarLife and CarPlay", "New infotainment OS", "cockpit_intelligence", "Digital Cockpit & AI", "The updated dashboard runs Chery Lion 4.0 with phone integration"),
        ],
    },
    {
        "brand": "Chery", "model": "Chery Tiggo 7", "powertrain": "ICE",
        "previous": "second-generation Tiggo 7", "current": "Tiggo 7 Plus 1.6T",
        "launch": "2021-09-27", "source": "https://en.wikipedia.org/wiki/Chery_Tiggo_7",
        "features": [
            ("1.6-litre turbo powertrain", "Turbocharged powertrain upgrade", "powertrain_performance", "Vehicle Dynamics", "The Plus range includes the documented 1.6-litre turbo engine"),
            ("Lion 4.0 infotainment with CarLife and CarPlay", "New infotainment OS", "cockpit_intelligence", "Digital Cockpit & AI", "The updated dashboard runs Chery Lion 4.0 with phone integration"),
        ],
    },
    *[
        {
            "brand": "Buick", "model": "Buick Envision", "powertrain": "ICE", "previous": "Envision S",
            "current": f"Envision Plus {variant}", "launch": "2021-06-19",
            "source": "https://news.gm.com.cn/en/home.detail.html/Pages/news/cn/en/2021/Jun/0619-buick.html",
            "features": [
                (seat_detail, "Flexible three-row seating", "seating_comfort", "Smart Cabin", seat_evidence),
                ("2.0T engine with nine-speed transmission and 48V mild hybrid", "New hybrid system", "hybrid_powertrain", "Energy & Charging", "GM documents the 48V mild-hybrid powertrain across the Envision Plus range"),
                *(([("FlexRide adaptive damping and intelligent AWD", "Adaptive suspension and AWD", "ride_body_control", "Vehicle Dynamics", "The Avenir source lists FlexRide, continuous damping control and intelligent AWD")]) if variant == "Avenir" else []),
            ],
        }
        for variant, seat_detail, seat_evidence in (
            ("five-seat", "Five-seat cabin with up to 1,712 L cargo capacity", "GM documents five-seat availability and the maximum cargo volume"),
            ("seven-seat", "Three-row seven-seat cabin", "GM documents a seven-seat layout for larger families"),
            ("Avenir", "Diamond-perforated leather seating", "GM documents quilted and embroidered leather for the Avenir trim"),
        )
    ],
    {
        "brand": "Lynk & Co", "model": "Lynk & Co 05", "powertrain": "ICE", "previous": "Lynk & Co 05",
        "current": "Lynk & Co 05+", "launch": "2021-08-06", "source": "https://en.wikipedia.org/wiki/Lynk_%26_Co_05",
        "features": [
            ("265 hp and 380 Nm 2.0-litre turbo engine", "Higher-output performance powertrain", "powertrain_performance", "Vehicle Dynamics", "The 05+ source documents the higher-output engine tune"),
            ("Aisin eight-speed transmission with four-wheel drive", "Performance AWD system", "ride_body_control", "Vehicle Dynamics", "The 05+ source documents the transmission and four-wheel drive"),
        ],
    },
    {
        "brand": "Exeed", "model": "Exeed TX", "powertrain": "ICE", "previous": "TXL pre-facelift",
        "current": "2021 Exeed TXL facelift", "launch": "2021-01", "source": "https://en.wikipedia.org/wiki/Exeed_TX",
        "features": [
            ("Integrated instrument and multimedia displays", "Larger or extra displays", "displays_hmi", "Digital Cockpit & AI", "The facelift source documents integrated digital instrument and center displays"),
            ("Restyled bumpers and vertical LED daytime running lights", "Lighting and exterior redesign", "lighting_visibility", "Smart Exterior", "The facelift source documents the new bumper and vertical DRLs"),
        ],
    },
    {
        "brand": "Exeed", "model": "Exeed TX", "powertrain": "ICE", "previous": "2021 Exeed TXL facelift",
        "current": "Exeed Lingyun 400T", "launch": "2021-08-27", "source": "https://en.wikipedia.org/wiki/Exeed_TX",
        "features": [
            ("400T performance powertrain package", "Turbocharged powertrain upgrade", "powertrain_performance", "Vehicle Dynamics", "The cited launch chronology identifies the Lingyun 400T version"),
            ("Lingyun model identity and trim package", "Ownership and trim package", "ownership_services", "General & Services", "The source documents the additional Lingyun name and 400T launch"),
        ],
    },
    {
        "brand": "Geely", "model": "Geely Jiaji", "powertrain": "ICE", "previous": "Geely Jiaji",
        "current": "Jiaji Platinum Edition", "launch": "2021-09-26", "source": "https://en.wikipedia.org/wiki/Geely_Jiaji",
        "features": [
            ("Redesigned Platinum Edition grille", "Exterior design personalization", "exterior_personalization", "Smart Exterior", "The Platinum Edition source documents a redesigned grille"),
            ("1.8-litre turbo with seven-speed dual-clutch transmission", "Powertrain calibration update", "powertrain_performance", "Vehicle Dynamics", "The launch source documents the 1.8T and 7DCT combination"),
        ],
    },
]


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _write(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
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

    for index, update in enumerate(CURATED_UPDATES, len(UPDATES) + 1):
        pair_id = f"FY{index:03d}"
        pairs.append({
            "pair_id": pair_id, "brand": update["brand"], "car_model": update["model"],
            "powertrain": update["powertrain"], "change_type": "historical_update",
            "nameplate_launch": NAMEPLATE_LAUNCH[update["model"]],
            "previous_version": update["previous"], "previous_launch": "2020-01-01",
            "current_version": update["current"], "current_launch": update["launch"],
            "source_url": update["source"],
        })
        for detail, feature, subcategory, category, evidence in update["features"]:
            features.append({
                "pair_id": pair_id, "detail": detail, "feature": feature,
                "subcategory": subcategory, "category": category, "evidence": evidence,
                "source_url": update["source"],
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
    return {
        "seed_pairs": len(UPDATES) + len(CURATED_UPDATES),
        "seed_features": len(UPDATES) * 2 + sum(len(update["features"]) for update in CURATED_UPDATES),
        "sales_rows": len(SALES) * 6,
    }


if __name__ == "__main__":
    print(sync())
