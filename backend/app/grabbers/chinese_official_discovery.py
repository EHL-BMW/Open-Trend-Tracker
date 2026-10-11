"""Discover consecutive Chinese-OEM model announcement events from official sites.

True launch/update announcements are explicitly labelled.  When a requested
sample is larger than the official launch history, official articles that
mention the model are retained as labelled proxies rather than silently
presented as generations.  For each model, events are ordered by publication
date and adjacent announcements form a pair.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from app.grabbers.bmw_official import extract_features
from app.paths import EXTERNAL_DIR

DEFAULT_OUTPUT = EXTERNAL_DIR / "chinese_official_200_pairs.csv"
DEFAULT_EVENTS = EXTERNAL_DIR / "chinese_official_release_events.csv"

SOURCES = {
    "NIO": "https://www.nio.com/sitemap.xml",
    "XPENG": "https://www.xpeng.com/sitemap-global.xml",
    "Geely": "https://global.geely.com/sitemap.xml",
    "GWM": "https://www.gwm-global.com/news/company.html",
}
ALLOWED_DOMAINS = {"nio.com", "xpeng.com", "geely.com", "gwm-global.com"}
LAUNCH_RE = re.compile(
    r"\b(?:all[- ]new|new|launch(?:ed|es|ing)?|unveil(?:ed|s|ing)?|debut(?:ed|s|ing)?|"
    r"premier(?:e|ed|es|ing)?|upgrade(?:d|s)?|update(?:d|s)?|facelift|model year|edition|"
    r"rolls? out|introduc(?:e|ed|es|ing))\b",
    re.I,
)
DATE_RES = [
    re.compile(r"\b(20\d{2})[-/.](0?[1-9]|1[0-2])[-/.](0?[1-9]|[12]\d|3[01])\b"),
    re.compile(
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)"
        r"\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(20\d{2})\b",
        re.I,
    ),
]
MONTHS = {name.lower(): index for index, name in enumerate(
    "January February March April May June July August September October November December".split(), 1
)}


# Longest/specific aliases come first.  The output name is deliberately stable
# across regional naming variants so announcements can be paired.
MODEL_PATTERNS: dict[str, list[tuple[str, str]]] = {
    "NIO": [
        (r"\bONVO\s+L90\b", "ONVO L90"), (r"\bONVO\s+L60\b", "ONVO L60"),
        (r"\bfirefly\b", "firefly"), (r"\bET5\s*T\b", "NIO ET5T"),
        *[(rf"\b{model}\b", f"NIO {model}") for model in
          ("ET9", "ET7", "ET5", "ES8", "ES7", "ES6", "EC7", "EC6")],
    ],
    "XPENG": [
        (r"\bMONA\s+M03\b", "XPENG MONA M03"), (r"\bP7\+\b", "XPENG P7+"),
        *[(rf"\b{re.escape(model)}\b", f"XPENG {model}") for model in
          ("G9L", "P7i", "G3i", "X9", "G9", "G7", "G6", "G3", "P7", "P5")],
    ],
    "Geely": [
        (r"\bEX5\s+EM[- ]?i\b", "Geely EX5 EM-i"),
        (r"\bGalaxy\s+Starship\s+7\b", "Geely Galaxy Starship 7"),
        *[(rf"\bGalaxy\s+{model}\b", f"Geely Galaxy {model}") for model in
          ("M9", "E8", "E5", "L7", "L6")],
        *[(rf"\b{model}\b", f"Geely {model}") for model in
          ("Monjaro", "Coolray", "Cityray", "Starray", "Emgrand", "Okavango", "Preface", "Azkarra", "EX5", "EX2")],
        *[(rf"\bGeometry\s+{model}\b", f"Geely Geometry {model}") for model in ("A", "C", "E")],
    ],
    "GWM": [
        *[(rf"\bTANK\s+{model}\b", f"GWM TANK {model}") for model in ("700", "500", "400", "300")],
        *[(rf"\bHAVAL\s+{model}\b", f"GWM HAVAL {model}") for model in ("H9", "H7", "H6", "H5", "DARGO", "JOLION")],
        (r"\bJOLION\b", "GWM HAVAL JOLION"), (r"\bDARGO\b", "GWM HAVAL DARGO"),
        (r"\bORA\s+(?:GOOD\s+CAT|03)\b", "GWM ORA 03"), (r"\bORA\s+5\b", "GWM ORA 5"),
        *[(rf"\bWEY\s+{model}\b", f"GWM WEY {model}") for model in ("G9", "80", "07", "05", "03")],
        (r"\bKING\s*KONG\s+POER\b", "GWM King Kong POER"), (r"\b(?:GWM\s+)?POER\b", "GWM POER"),
    ],
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self._seen_title = False
        self.meta: dict[str, str] = {}
        self.blocks: list[str] = []
        self._capture = False
        self._skip = 0
        self._buffer: list[str] = []
        self._article_started = False
        self.visible_text: list[str] = []

    def handle_starttag(self, tag, attrs):
        attributes = {key.lower(): value or "" for key, value in attrs}
        if tag == "title" and not self._seen_title:
            self._in_title = True
        if tag == "meta":
            key = (attributes.get("property") or attributes.get("name") or "").lower()
            if key and attributes.get("content"):
                self.meta[key] = attributes["content"].strip()
        if tag in {"script", "style", "nav", "footer"}:
            self._skip += 1
        elif not self._skip and (tag == "h1" or self._article_started) and tag in {"h1", "h2", "h3", "p", "li"}:
            if tag == "h1":
                self._article_started = True
            self._capture = True
            self._buffer = []

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if not self._skip and data.strip():
            self.visible_text.append(data.strip())
        if self._capture and not self._skip:
            self._buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
            self._seen_title = True
        if tag in {"script", "style", "nav", "footer"} and self._skip:
            self._skip -= 1
        elif self._capture and tag in {"h1", "h2", "h3", "p", "li"}:
            value = re.sub(r"\s+", " ", " ".join(self._buffer)).strip()
            if value:
                self.blocks.append(value)
            self._capture = False
            self._buffer = []


@dataclass(frozen=True)
class Event:
    brand: str
    car_model: str
    release_date: str
    title: str
    url: str
    blocks: tuple[str, ...]
    event_type: str


def _official(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == domain or host.endswith("." + domain) for domain in ALLOWED_DOMAINS)


def _get(url: str, timeout: int = 35) -> str:
    if not _official(url):
        raise ValueError(f"not an allow-listed official URL: {url}")
    request = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    })
    context = ssl.create_default_context()
    with urlopen(request, timeout=timeout, context=context) as response:
        final = response.geturl()
        if not _official(final):
            raise ValueError(f"official URL redirected outside allow-list: {final}")
        return response.read().decode(response.headers.get_content_charset() or "utf-8", "replace")


def _locations(xml: str, base_url: str) -> list[str]:
    root = ElementTree.fromstring(xml)
    return [urljoin(base_url, element.text.strip()) for element in root.iter()
            if element.tag.endswith("loc") and element.text]


def discover_urls() -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for brand, source in SOURCES.items():
        document = _get(source)
        if source.endswith(".xml"):
            urls = _locations(document, source)
        else:
            # GWM's sitemap omits article detail URLs. Its server-rendered news
            # archive exposes 21 populated pages (older empty page numbers
            # repeat only the three hero links).
            documents = [document]
            for page in range(2, 22):
                try:
                    documents.append(_get(f"https://www.gwm-global.com/news/company-{page}.html"))
                except Exception:
                    continue
            urls = [urljoin(source, path) for page in documents
                    for path in re.findall(r'href=["\']([^"\']+/news/\d+\.html)["\']', page)]
        for url in dict.fromkeys(urls):
            if "/news/" in url and _official(url):
                found.append((brand, url))
    return found


def _date(parser: PageParser, url: str, text: str) -> str | None:
    candidates = [
        parser.meta.get("article:published_time", ""), parser.meta.get("date", ""),
        parser.meta.get("publishdate", ""), parser.meta.get("pubdate", ""),
        url, text[:1800], " ".join(parser.visible_text[:600]),
    ]
    for candidate in candidates:
        match = DATE_RES[0].search(candidate)
        if match:
            return f"{int(match[1]):04d}-{int(match[2]):02d}-{int(match[3]):02d}"
        match = DATE_RES[1].search(candidate)
        if match:
            return f"{int(match[3]):04d}-{MONTHS[match[1].lower()]:02d}-{int(match[2]):02d}"
    return None


def _models(brand: str, title: str, lead: str) -> list[str]:
    # PageParser starts at the article H1, excluding product navigation cards.
    haystack = f"{title} {lead[:2200]}"
    return [name for pattern, name in MODEL_PATTERNS[brand] if re.search(pattern, haystack, re.I)]


def fetch_events(item: tuple[str, str]) -> list[Event]:
    brand, url = item
    document = _get(url)
    parser = PageParser()
    parser.feed(document)
    title = re.sub(r"\s+", " ", parser.meta.get("og:title") or parser.title).strip()
    lead = " ".join(parser.blocks)
    date = _date(parser, url, lead)
    if not date:
        return []
    models = _models(brand, title, lead)
    if not models:
        return []
    blocks = tuple(parser.blocks[:120])
    event_type = ("official_release_update" if LAUNCH_RE.search(f"{title} {lead[:900]}")
                  else "official_article_model_mention_proxy")
    return [Event(brand, model, date, title, url, blocks, event_type) for model in models]


def discover_events(workers: int = 8) -> list[Event]:
    events: list[Event] = []
    urls = discover_urls()
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {pool.submit(fetch_events, item): item for item in urls}
        for future in as_completed(futures):
            try:
                events.extend(future.result())
            except Exception:
                # A single retired/blocked article must not invalidate the
                # reproducible set obtained from the remaining official pages.
                continue
    unique = {(event.brand, event.car_model, event.release_date, event.title): event for event in events}
    return sorted(unique.values(), key=lambda event: (event.car_model, event.release_date, event.title))


def build_pairs(events: list[Event], limit_pairs: int) -> list[tuple[Event, Event]]:
    grouped: dict[str, list[Event]] = {}
    for event in events:
        grouped.setdefault(event.car_model, []).append(event)
    pairs = [(previous, current) for model in sorted(grouped)
             for previous, current in zip(grouped[model], grouped[model][1:])]
    # Prefer broad model coverage, then fill with additional transitions.
    first: list[tuple[Event, Event]] = []
    rest: list[tuple[Event, Event]] = []
    seen: set[str] = set()
    for pair in pairs:
        target = first if pair[1].car_model not in seen else rest
        target.append(pair)
        seen.add(pair[1].car_model)
    # Put pairs with two explicit releases/updates first, followed by mixed and
    # proxy-only pairs.  Every retained pair is still adjacent in the complete
    # event history for that model.
    selected = sorted(first + rest, key=lambda pair: (
        -sum(event.event_type == "official_release_update" for event in pair),
        pair[1].car_model, pair[1].release_date,
    ))
    if len(selected) < limit_pairs:
        raise ValueError(f"only {len(selected)} consecutive official release pairs discovered; requested {limit_pairs}")
    return selected[:limit_pairs]


def _feature_payload(blocks: tuple[str, ...]) -> tuple[str, str, str]:
    features = extract_features(list(blocks), max_features=16)
    names = [feature.name for feature in features]
    categories = sorted({feature.category for feature in features})
    evidence = [{"name": feature.name, "category": feature.category, "evidence": feature.evidence}
                for feature in features]
    return tuple(json.dumps(value, ensure_ascii=False) for value in (names, categories, evidence))


def pair_rows(pairs: list[tuple[Event, Event]]) -> list[dict]:
    rows: list[dict] = []
    retrieved = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    for index, pair in enumerate(pairs, 1):
        pair_id = f"CN{index:03d}"
        for order, event in enumerate(pair, 1):
            names, categories, evidence = _feature_payload(event.blocks)
            rows.append({
                "pair_id": pair_id, "brand": event.brand, "car_model": event.car_model,
                "version": event.title, "version_order": order, "release_date": event.release_date,
                "release_date_precision": "day", "event_type": event.event_type,
                "pair_basis": ("consecutive_release_update" if all(
                    item.event_type == "official_release_update" for item in pair
                ) else "consecutive_official_article_mention_proxy"),
                "newly_released_features": names,
                "feature_categories": categories, "feature_evidence": evidence,
                "cumulative_sales_year_1": "", "cumulative_sales_year_2": "",
                "cumulative_sales_year_3": "", "cumulative_sales_year_4": "",
                "sales_status": "official announcement does not disclose version-level annual cumulative sales",
                "source_url": event.url, "source_mode": "live_official_page",
                "grab_status": "ok", "retrieved_at": retrieved,
            })
    return rows


def write_csv(rows: list[dict], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_events(events: list[Event], output: Path) -> None:
    rows = [{"brand": e.brand, "car_model": e.car_model, "release_date": e.release_date,
             "version": e.title, "event_type": e.event_type, "source_url": e.url} for e in events]
    write_csv(rows, output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=200)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--events-output", type=Path, default=DEFAULT_EVENTS)
    args = parser.parse_args()
    events = discover_events(args.workers)
    pairs = build_pairs(events, args.pairs)
    write_events(events, args.events_output)
    write_csv(pair_rows(pairs), args.output)
    print(f"discovered {len(events)} qualifying official events")
    print(f"wrote {len(pairs)} consecutive pairs ({len(pairs) * 2} rows) to {args.output}")


if __name__ == "__main__":
    main()
