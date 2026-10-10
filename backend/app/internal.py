"""Internal branch: BMW-provided files -> Observations.

One reader per source format. Each observation keeps a RawRef (file + sheet/row or page),
so every unified number links back to the cell it came from.
"""
import logging
import re
from collections import defaultdict

import pandas as pd
from pypdf import PdfReader

from app.paths import DATA_DIR
from app.schema import Observation, RawRef

logging.getLogger("pypdf").setLevel(logging.ERROR)  # font-encoding warnings, irrelevant for the text we use

EU_COUNTRIES = {"AT", "BE", "CH", "CZ", "DE", "DK", "ES", "FI", "FR", "GB", "GR", "HU", "IE", "IT", "LT",
                "LU", "LV", "NL", "NO", "PL", "PT", "RO", "SE", "SI", "SK"}


def market_of(country: str) -> str:
    """Map an ISO country code onto the sales markets used by BMW: EU, CN, US, RoW."""
    if country in ("US", "CN"):
        return country
    return "EU" if country in EU_COUNTRIES else "RoW"


def _rel(path) -> str:
    return str(path.relative_to(DATA_DIR))


# --- customer feedback: one row per (verbatim, classification) ---------------------------

FEEDBACK_TYPES = {"Likes": "like", "Wants": "want", "Difficult to Use": "difficult_to_use", "Defect": "defect"}


def feedback() -> list[Observation]:
    out = []
    for f in sorted(DATA_DIR.glob("*_feedback_hackathon.xlsx")):
        df = pd.read_excel(f)
        label = df["Vfc level2 Name"].fillna("no_class_found")
        classified_ids = set(df.loc[label != "no_class_found", "ID"])
        for i, r in enumerate(df.to_dict("records")):
            lab = label.iat[i]
            # an unclassified row duplicates a verbatim already counted under a real label -> skip it;
            # a verbatim with no classification at all is kept as 'unclassified' (to be labelled later)
            if lab == "no_class_found" and r["ID"] in classified_ids:
                continue
            metric = "unclassified" if lab == "no_class_found" else FEEDBACK_TYPES.get(r["Feedback Type"], "mention")
            out.append(Observation(
                id=f"fb:{r['Derivate (e-code)']}:{i + 2}", origin="internal", source="feedback",
                vehicle=r["Derivate (e-code)"], market=market_of(r["Country"]), country=r["Country"],
                raw_label=lab, metric=metric, value=1, unit="count", text=r["Customer Feedback"],
                raw=RawRef(file=_rel(f), locator=f"sheet=Feedback_Explorer row={i + 2} id={r['ID']} "
                                                 f"channel={r['Source']} level3={r['Vfc level3 Name']}"),
            ))
    return out


# --- customer studies --------------------------------------------------------------------

STUDY_FILE = "F70_G60_G68_G70_customer_studies.xlsx"


def study_cn_eu() -> list[Observation]:
    """Mean satisfaction on a 0-10 scale; columns = (market, model), rows = attribute + 'Mean'."""
    f = DATA_DIR / STUDY_FILE
    df = pd.read_excel(f, sheet_name="CN_EU_2025", header=None)
    markets = df.iloc[1, 1:].ffill().map({"China": "CN", "EU": "EU"})
    models = df.iloc[2, 1:].map(lambda s: s.split()[-1])
    out, label = [], None
    for i in range(2, len(df)):
        if df.iat[i, 0] != "Mean":
            label = str(df.iat[i, 0]).strip()
            continue
        for j in markets.index:
            v = df.iat[i, j]
            if pd.notna(v):
                out.append(Observation(
                    id=f"st:cneu:{i + 1}:{j}", origin="internal", source="study_cn_eu",
                    vehicle=models[j], market=markets[j], raw_label=label, metric="study_mean_0_10",
                    value=float(v), unit="0-10", norm=float(v) / 10, period="2025",
                    raw=RawRef(file=STUDY_FILE, locator=f"sheet=CN_EU_2025 row={i + 1} col={j + 1}"),
                ))
    return out


US_SCALE = {"I Hate It": 1, "A Failure": 2, "Unsatisfactory": 3, "Satisfactory": 4,
            "Excellent": 5, "Delightful": 6, "I Love It": 7}


def study_us() -> list[Observation]:
    """7-point answer distribution per question -> mean (1-7) and bottom-3 share."""
    f = DATA_DIR / STUDY_FILE
    df = pd.read_excel(f, sheet_name="US_2025", header=None)
    models = {j: str(df.iat[0, j]).split()[-1] for j in (2, 3)}
    blocks = []  # (question, first excel row, {model: {answer: share}})
    for i in range(len(df)):
        c0 = df.iat[i, 0]
        if pd.isna(c0) or c0 == "Sample total":
            continue
        c0 = str(c0).strip()
        if c0 in US_SCALE:
            for j, model in models.items():
                if pd.notna(df.iat[i, j]):
                    blocks[-1][2][model][c0] = float(df.iat[i, j])
        else:
            blocks.append((c0, i + 1, defaultdict(dict)))
    out = []
    for question, row, dist in blocks:
        for model, shares in dist.items():
            total = sum(shares.values())
            if total == 0:
                continue
            mean = sum(US_SCALE[a] * s for a, s in shares.items()) / total
            bottom3 = sum(s for a, s in shares.items() if US_SCALE[a] <= 3) / total
            raw = RawRef(file=STUDY_FILE, locator=f"sheet=US_2025 rows={row}-{row + 8} model={model}")
            common = dict(origin="internal", source="study_us", vehicle=model, market="US",
                          raw_label=question, period="2025", raw=raw)
            out.append(Observation(id=f"st:us:{row}:{model}:mean", metric="study_mean_1_7", value=mean,
                                   unit="1-7", norm=(mean - 1) / 6, **common))
            out.append(Observation(id=f"st:us:{row}:{model}:bottom3", metric="study_bottom3_share",
                                   value=bottom3, unit="share", norm=1 - bottom3, **common))
    return out


# --- sales volumes -----------------------------------------------------------------------

SALES_FILE = "sales_volumes.xlsx"


def sales() -> list[Observation]:
    """Units per market and year. A sheet covering two models (G60_G68) is attributed to both."""
    out = []
    for sheet, df in pd.read_excel(DATA_DIR / SALES_FILE, sheet_name=None).items():
        vehicles = sheet.split("_")
        note = f"sheet {sheet} combines {' + '.join(vehicles)}" if len(vehicles) > 1 else None
        for i, r in enumerate(df.to_dict("records")):
            volumes = {c.removeprefix("volume_"): r[c] for c in df.columns if c.startswith("volume_")}
            for v in vehicles:
                common = dict(origin="internal", source="sales", vehicle=v, market=r["market_code"],
                              raw_label="sales_volume", text=note,
                              raw=RawRef(file=SALES_FILE, locator=f"sheet={sheet} row={i + 2}"))
                for year, units in volumes.items():
                    period = year if int(year) <= 2025 else f"{year}F"  # years after 2025 are forecasts
                    out.append(Observation(id=f"sa:{v}:{r['market_code']}:{year}", metric=f"volume_{period}",
                                           value=float(units), unit="units", period=period, **common))
                if volumes.get("2025") and "2030" in volumes:
                    out.append(Observation(id=f"sa:{v}:{r['market_code']}:growth", metric="growth_2025_2030F",
                                           value=volumes["2030"] / volumes["2025"] - 1, unit="share",
                                           period="2025-2030F", **common))
    return out


# --- option lists (German price-list PDFs, Germany, EUR incl. VAT) ------------------------
# In layout mode each table row is one text line: name, SA code, price, then one marker per model
# variant: ■ = standard, □ = optional, blank = not available.

SA_CODE = re.compile(r"^(?=.*\d)[0-9A-Z]{3}$")
PRICE = re.compile(r"^(\d{1,3}(?:\.\d{3})*|–),–$")
# lines that qualify the item above (a condition, a note, a wheel spec) rather than name a new item
CONTINUATION = re.compile(r"^(In Verbindung|Nur in Verbindung|Nicht in Verbindung|Hinweis|Für |– |\d+(,\d)? ?J\b)")


def option_rows(pdf) -> list[dict]:
    rows, current = [], None
    for page_no, page in enumerate(PdfReader(pdf).pages, start=1):
        for line in page.extract_text(extraction_mode="layout").splitlines():
            std, opt = line.count("■"), line.count("□")
            if not std + opt or ("Serienausstattung" in line and "Sonderausstattung" in line):  # legend
                continue
            cols = [c.strip() for c in re.split(r"\s{3,}", line.replace("■", " ").replace("□", " ")) if c.strip()]
            name = cols[0] if cols and not SA_CODE.match(cols[0]) and not PRICE.match(cols[0]) else ""
            if name and not CONTINUATION.match(name) and name != "Serienausstattung":
                current = name
            if current is None:
                continue
            price = next((c for c in cols if PRICE.match(c)), None)
            rows.append({"page": page_no, "name": current, "code": next((c for c in cols[1:] if SA_CODE.match(c)), None),
                         "price": None if price is None else float(price[:-2].replace(".", "").replace("–", "0")),
                         "standard": std, "optional": opt, "line": " ".join(cols)})
    return rows


def options() -> list[Observation]:
    out = []
    for pdf in sorted(DATA_DIR.glob("*_OptionList.PDF")):
        vehicle = pdf.name.split("_")[0]
        rows = option_rows(pdf)
        n_variants = max(r["standard"] + r["optional"] for r in rows)
        for i, r in enumerate(rows):
            common = dict(origin="internal", source="options", vehicle=vehicle, market="EU", country="DE",
                          raw_label=r["name"], text=r["line"],
                          raw=RawRef(file=_rel(pdf), locator=f"page={r['page']}" + (f" code={r['code']}" if r["code"] else "")))
            share = r["standard"] / n_variants
            out.append(Observation(id=f"op:{vehicle}:{i}:std", metric="standard_fitment", value=share,
                                   unit="share", norm=share, **common))
            if r["price"] is not None:
                out.append(Observation(id=f"op:{vehicle}:{i}:price", metric="option_price", value=r["price"],
                                       unit="EUR", **common))
    return out


def load() -> list[Observation]:
    return feedback() + study_cn_eu() + study_us() + sales() + options()
