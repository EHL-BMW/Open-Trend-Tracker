"""Grab launch data from official BMW Group PressClub pages.

The extractor is intentionally deterministic: no LLM or third-party search API is
used.  Every output row retains its official URL and short evidence snippets.

Run from ``backend/``::

    uv run python -m app.grabbers.bmw_official --limit 20

Optionally provide an official annual model-sales export with columns
``model,year,units`` using ``--sales-csv``.  The grabber never estimates missing
model sales; unavailable cumulative values remain null.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from app.paths import EXTERNAL_DIR


ALLOWED_HOST = "www.press.bmwgroup.com"
DEFAULT_OUTPUT = EXTERNAL_DIR / "bmw_official_first_20.json"

# The eight domains are copied verbatim from the supplied BMW methodology PDF.
TECHNOLOGY_DOMAINS: dict[str, tuple[str, ...]] = {
    "Vehicle Dynamics": (
        "chassis", "suspension", "steering", "brake", "braking", "powertrain",
        "driving dynamics", "agility", "ride comfort", "all-wheel drive", "xdrive",
    ),
    "Smart Cabin": (
        "seat", "cabin", "interior", "comfort", "climate", "acoustic", "spaciousness",
        "passenger", "upholstery", "panoramic roof", "luggage", "heating",
    ),
    "Smart Exterior": (
        "exterior", "headlight", "rear light", "lighting", "door", "body", "kidney grille",
        "iconic glow", "aerodynamic", "wheel", "design language",
    ),
    "Digital Cockpit & AI": (
        "display", "idrive", "operating system", "voice", "personal assistant", "artificial intelligence",
        "infotainment", "gaming", "quickselect", "head-up", "augmented view", "theatre screen",
        "steering wheel", "control panel",
    ),
    "Driving Assistance": (
        "driver assistance", "driving assistance", "parking", "automated driving", "automated parking",
        "cruise control", "lane", "manoeuvre assistant", "highway assistant", "collision warning",
    ),
    "Energy & Charging": (
        "charging", "battery", "electric range", "range of", "efficiency", "recuperation",
        "edrive", "kilowatt-hour", "kwh", "plug-in hybrid",
    ),
    "General & Services": (
        "owner's manual", "owners manual", "dealer", "service", "warranty", "maintenance",
        "roadside assistance", "delivery experience",
    ),
    "Connected Ecosystem": (
        "connecteddrive", "connected", "smartphone", "my bmw app", "remote service", "remote function",
        "carplay", "android auto", "over-the-air", "software upgrade", "5g", "personal esim",
    ),
}

NOVELTY = re.compile(
    r"\b(new|newly|first(?:-ever| time)?|debut|introduc(?:e|ed|es|ing)|innovative|innovation|"
    r"now (?:offers|available|features)|making its debut|for the first time|latest-generation|"
    r"enhanced|upgraded|redesigned|revised)\b",
    re.I,
)


@dataclass(frozen=True)
class Seed:
    model: str
    url: str
    variant_pattern: str


SEEDS = (
    Seed(
        "BMW 5 Series",
        "https://www.press.bmwgroup.com/global/article/detail/T0416261EN/the-new-bmw-5-series-sedan?language=en",
        r"BMW\s+((?:i5\s+(?:eDrive\d+|M\d+)(?:\s+xDrive)?|M5(?:\s+Touring)?|5\d{2}[a-z]?(?:\s+xDrive)?))",
    ),
    Seed(
        "BMW 7 Series",
        "https://www.press.bmwgroup.com/global/article/detail/T0380173EN/the-new-bmw-7-series?language=en",
        r"BMW\s+((?:i7\s+(?:eDrive\d+|xDrive\d+|M\d+)(?:\s+xDrive)?|M7\d{2}[a-z]?(?:\s+xDrive)?|7\d{2}[a-z]?(?:\s+xDrive)?))",
    ),
    Seed(
        "BMW X1",
        "https://www.press.bmwgroup.com/global/article/detail/T0393974EN/the-all-new-bmw-x1-and-the-first-ever-bmw-ix1?language=en",
        r"BMW\s+((?:iX1\s+(?:eDrive|xDrive)\d+|X1\s+(?:(?:sDrive|xDrive)\d+[a-z]?|M\d+[a-z]?\s+xDrive)))",
    ),
    Seed(
        "BMW X3",
        "https://www.press.bmwgroup.com/global/article/detail/T0442377EN/the-new-bmw-x3?language=en",
        r"BMW\s+(X3\s+(?:\d{2}[a-z]?|M\d+)\s+xDrive)",
    ),
)


class ArticleParser(HTMLParser):
    """Small PressClub-specific parser; keeps text only from the article block."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_article = False
        self.article_depth = 0
        self.capture_tag: str | None = None
        self.capture_class = ""
        self.buffer: list[str] = []
        self.title = ""
        self.published_text = ""
        self.blocks: list[str] = []

    @staticmethod
    def _attrs(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {k: v or "" for k, v in attrs}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = self._attrs(attrs)
        classes = values.get("class", "").split()
        if tag == "div" and "article-detail" in classes and not self.in_article:
            self.in_article = True
            self.article_depth = 1
            return
        if not self.in_article:
            return
        if tag == "div":
            self.article_depth += 1
        if tag in {"h1", "h2", "h3", "h4", "h5", "p", "li", "strong", "span"}:
            self.capture_tag = tag
            self.capture_class = values.get("class", "")
            self.buffer = []

    def handle_data(self, data: str) -> None:
        if self.in_article and self.capture_tag:
            self.buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if not self.in_article:
            return
        if self.capture_tag == tag:
            text = clean_text(" ".join(self.buffer))
            if text:
                if tag == "h1" and not self.title:
                    self.title = text
                elif tag == "span" and "date" in self.capture_class.split() and not self.published_text:
                    self.published_text = text
                elif tag in {"h2", "h3", "h4", "p", "li", "strong"}:
                    self.blocks.append(text)
            self.capture_tag = None
            self.capture_class = ""
            self.buffer = []
        if tag == "div":
            self.article_depth -= 1
            if self.article_depth == 0:
                self.in_article = False


@dataclass
class Feature:
    name: str
    category: str
    evidence: str


@dataclass
class VehicleVersion:
    car_model: str
    version: str
    release_date: str
    release_date_precision: str
    newly_released_features: list[Feature]
    cumulative_sales_after_years: dict[str, int | None]
    sales_status: str
    source_url: str
    source_title: str
    retrieved_at: str


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def fetch(url: str, timeout: int = 30) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise ValueError(f"refusing non-official URL: {url}")
    request = Request(url, headers={"User-Agent": "OpenTrendTracker/0.1 official-source-research"})
    with urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get_content_type()
        if response.status != 200 or content_type != "text/html":
            raise RuntimeError(f"unexpected response for {url}: {response.status} {content_type}")
        return response.read().decode(response.headers.get_content_charset() or "utf-8", "replace")


def parse_article(document: str) -> ArticleParser:
    parser = ArticleParser()
    parser.feed(document)
    if not parser.title or not parser.blocks:
        raise ValueError("BMW PressClub article structure was not recognised")
    return parser


def published_date(raw: str) -> str:
    # Example: Wed May 24 14:00:00 CEST 2023.  The timezone abbreviation is
    # intentionally ignored; only the publication calendar date is needed.
    match = re.search(r"\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+([A-Z][a-z]{2}\s+\d{1,2}).*?(\d{4})\b", raw)
    if not match:
        raise ValueError(f"unrecognised publication date: {raw!r}")
    return datetime.strptime(f"{match.group(1)} {match.group(2)}", "%b %d %Y").date().isoformat()


def release_date(blocks: Iterable[str], fallback: str) -> tuple[str, str]:
    text = " ".join(blocks)
    patterns = (
        (r"(?:market|sales) launch[^.]{0,100}?\b(?:in|from|starting in)\s+"
         r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d{2})",
         "month"),
        (r"market launch[^.]{0,100}?\b(first|second|third|fourth) quarter of (20\d{2})", "quarter"),
    )
    for pattern, precision in patterns:
        match = re.search(pattern, text, re.I)
        if not match:
            continue
        if precision == "month":
            month = datetime.strptime(match.group(1), "%B").month
            return f"{match.group(2)}-{month:02d}", precision
        quarter = {"first": 1, "second": 2, "third": 3, "fourth": 4}[match.group(1).lower()]
        return f"{match.group(2)}-Q{quarter}", precision
    return fallback, "publication_day_fallback"


def versions(text: str, seed: Seed) -> list[str]:
    found = []
    for match in re.finditer(seed.variant_pattern, text, re.I):
        value = clean_text(match.group(1))
        # Restore official BMW casing from the first occurrence while deduplicating case-insensitively.
        if value.casefold() not in {v.casefold() for v in found}:
            found.append(value)
    # BMW sometimes shortens an electric M version later in the article
    # ("i5 M60") even though its official launch name is "i5 M60 xDrive".
    # Do not apply this to combustion names such as 520d / 520d xDrive,
    # which are genuinely separate versions.
    full_electric_m = {v.casefold()[:-7] for v in found if re.match(r"i\w+\s+M\d+\s+xDrive$", v, re.I)}
    return [v for v in found if v.casefold() not in full_electric_m]


def sentences(blocks: Iterable[str]) -> Iterable[str]:
    for block in blocks:
        for sentence in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", block):
            sentence = clean_text(sentence)
            if 30 <= len(sentence) <= 600:
                yield sentence


def classify_feature(sentence: str) -> str | None:
    lowered = sentence.casefold()
    scored = {
        domain: sum(1 for keyword in keywords if keyword.casefold() in lowered)
        for domain, keywords in TECHNOLOGY_DOMAINS.items()
    }
    best = max(scored, key=scored.get)
    return best if scored[best] else None


def extract_features(blocks: Iterable[str], max_features: int = 12) -> list[Feature]:
    features: list[Feature] = []
    seen: set[str] = set()
    for sentence in sentences(blocks):
        category = classify_feature(sentence)
        if not category or not NOVELTY.search(sentence):
            continue
        evidence = sentence[:400]
        key = re.sub(r"\W+", " ", evidence.casefold())[:180]
        if key in seen:
            continue
        seen.add(key)
        # Evidence is deliberately retained verbatim; name is a compact UI label.
        name = re.sub(r"^(?:The|A|An)\s+", "", sentence).split(".", 1)[0][:180].strip(" ;:")
        features.append(Feature(name=name, category=category, evidence=evidence))
        if len(features) >= max_features:
            break
    return features


def load_sales(path: Path | None) -> dict[str, dict[int, int]]:
    if path is None:
        return {}
    totals: dict[str, dict[int, int]] = {}
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        required = {"model", "year", "units"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"sales CSV requires columns {sorted(required)}")
        for row in reader:
            model, year, units = clean_text(row["model"]), int(row["year"]), int(row["units"])
            if units < 0:
                raise ValueError("sales units cannot be negative")
            annual = totals.setdefault(model.casefold(), {})
            annual[year] = annual.get(year, 0) + units
    return totals


def cumulative_sales(model: str, release: str, sales: dict[str, dict[int, int]]) -> tuple[dict[str, int | None], str]:
    result: dict[str, int | None] = {f"year_{n}": None for n in range(1, 6)}
    annual = sales.get(model.casefold())
    if not annual:
        return result, "not published at model/version level on the launch page"
    release_year = int(release[:4])
    running = 0
    for n in range(1, 6):
        year = release_year + n - 1
        if year not in annual:
            return result, f"official sales input is incomplete at {year}; later cumulative values remain null"
        running += annual[year]
        result[f"year_{n}"] = running
    return result, "computed from supplied official annual model sales"


def grab(
    seeds: Iterable[Seed] = SEEDS,
    *,
    limit: int = 20,
    sales_csv: Path | None = None,
    delay_seconds: float = 0.25,
) -> list[VehicleVersion]:
    sales = load_sales(sales_csv)
    rows: list[VehicleVersion] = []
    retrieved = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    for index, seed in enumerate(seeds):
        if index and delay_seconds:
            time.sleep(delay_seconds)
        article = parse_article(fetch(seed.url))
        body = " ".join(article.blocks)
        variants = versions(body, seed)
        if len(variants) < 2:  # explicit user requirement
            continue
        remaining = limit - len(rows)
        if remaining < 2:
            break  # never leave a model with only one version in the capped output
        variants = variants[:remaining]
        published = published_date(article.published_text)
        launch, precision = release_date(article.blocks, published)
        features = extract_features(article.blocks)
        cumulative, status = cumulative_sales(seed.model, launch, sales)
        for variant in variants:
            rows.append(VehicleVersion(
                car_model=seed.model,
                version=f"BMW {variant}",
                release_date=launch,
                release_date_precision=precision,
                newly_released_features=features,
                cumulative_sales_after_years=cumulative.copy(),
                sales_status=status,
                source_url=seed.url,
                source_title=article.title,
                retrieved_at=retrieved,
            ))
        if len(rows) >= limit:
            return rows
    return rows


def write_json(rows: Iterable[VehicleVersion], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "source_policy": "official BMW Group PressClub only",
        "allowed_feature_categories": list(TECHNOLOGY_DOMAINS),
        "items": [asdict(row) for row in rows],
    }
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(rows: Iterable[VehicleVersion], output: Path) -> None:
    """Write one flat CSV row per version while preserving nested feature evidence."""
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "car_model", "version", "release_date", "release_date_precision",
        "newly_released_features", "feature_categories", "feature_evidence",
        "cumulative_sales_year_1", "cumulative_sales_year_2", "cumulative_sales_year_3",
        "cumulative_sales_year_4", "cumulative_sales_year_5", "sales_status",
        "source_url", "source_title", "retrieved_at",
    ]
    with output.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            features = [asdict(feature) for feature in row.newly_released_features]
            writer.writerow({
                "car_model": row.car_model,
                "version": row.version,
                "release_date": row.release_date,
                "release_date_precision": row.release_date_precision,
                "newly_released_features": json.dumps(
                    [feature["name"] for feature in features], ensure_ascii=False
                ),
                "feature_categories": json.dumps(
                    sorted({feature["category"] for feature in features}), ensure_ascii=False
                ),
                "feature_evidence": json.dumps(features, ensure_ascii=False),
                **{
                    f"cumulative_sales_year_{n}": row.cumulative_sales_after_years[f"year_{n}"]
                    for n in range(1, 6)
                },
                "sales_status": row.sales_status,
                "source_url": row.source_url,
                "source_title": row.source_title,
                "retrieved_at": row.retrieved_at,
            })


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=20, help="maximum version-level records (default: 20)")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--sales-csv", type=Path, help="official annual model sales: model,year,units")
    parser.add_argument("--delay", type=float, default=0.25, help="delay between official-site requests")
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")
    rows = grab(limit=args.limit, sales_csv=args.sales_csv, delay_seconds=max(0, args.delay))
    write_json(rows, args.output)
    csv_output = args.output.with_suffix(".csv")
    write_csv(rows, csv_output)
    print(f"wrote {len(rows)} official BMW version records to {args.output} and {csv_output}")
    if len(rows) < args.limit:
        print(f"warning: only {len(rows)} records met the minimum-two-versions rule")


if __name__ == "__main__":
    main()
