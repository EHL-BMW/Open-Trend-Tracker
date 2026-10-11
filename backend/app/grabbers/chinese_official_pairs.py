"""Build 20 Chinese OEM consecutive-version pairs from official release pages."""
from __future__ import annotations

import argparse
import csv
import json
import re
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from app.grabbers.bmw_official import TECHNOLOGY_DOMAINS, extract_features
from app.paths import BACKEND_DIR, EXTERNAL_DIR

DEFAULT_SEEDS = BACKEND_DIR / "chinese_model_pair_seeds.csv"
DEFAULT_FALLBACK = BACKEND_DIR / "chinese_official_fallback_evidence.json"
DEFAULT_OUTPUT = EXTERNAL_DIR / "chinese_official_20_pairs.csv"
ALLOWED_DOMAINS = {"nio.com", "lixiang.com"}


class TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.capture = False
        self.buffer: list[str] = []
        self.blocks: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "nav", "footer"}:
            self.skip += 1
        elif not self.skip and tag in {"h1", "h2", "h3", "p", "li"}:
            self.capture = True
            self.buffer = []

    def handle_data(self, data):
        if self.capture and not self.skip:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if tag in {"script", "style", "nav", "footer"} and self.skip:
            self.skip -= 1
        elif self.capture and tag in {"h1", "h2", "h3", "p", "li"}:
            text = re.sub(r"\s+", " ", " ".join(self.buffer)).strip()
            if text:
                self.blocks.append(text)
            self.capture = False
            self.buffer = []


def _official(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == domain or host.endswith("." + domain) for domain in ALLOWED_DOMAINS)


def fetch_blocks(url: str, timeout: int = 40) -> list[str]:
    if not _official(url):
        raise ValueError(f"not an allow-listed Chinese OEM official URL: {url}")
    request = Request(url, headers={"User-Agent": "OpenTrendTracker/0.1 official-source-research"})
    with urlopen(request, timeout=timeout) as response:
        final_url = response.geturl()
        if not _official(final_url):
            raise ValueError(f"official URL redirected outside allow-list: {final_url}")
        document = response.read().decode(response.headers.get_content_charset() or "utf-8", "replace")
    parser = TextParser()
    parser.feed(document)
    if not parser.blocks:
        raise ValueError(f"no article text extracted from {url}")
    return parser.blocks


def _feature_payload(blocks: list[str]) -> tuple[str, str, str]:
    features = extract_features(blocks, max_features=16)
    names = [feature.name for feature in features]
    categories = sorted({feature.category for feature in features})
    evidence = [{"name": feature.name, "category": feature.category, "evidence": feature.evidence}
                for feature in features]
    return (json.dumps(names, ensure_ascii=False), json.dumps(categories, ensure_ascii=False),
            json.dumps(evidence, ensure_ascii=False))


def load_fallback(path: Path | None) -> dict[str, list[str]]:
    if path is None:
        return {}
    with path.open(encoding="utf-8") as stream:
        payload = json.load(stream)
    if not isinstance(payload, dict) or not all(
        isinstance(url, str) and isinstance(blocks, list) and all(isinstance(block, str) for block in blocks)
        for url, blocks in payload.items()
    ):
        raise ValueError(f"invalid fallback evidence structure: {path}")
    return payload


def grab(
    seeds_path: Path = DEFAULT_SEEDS,
    limit_pairs: int = 20,
    delay: float = 0.15,
    fallback_path: Path | None = DEFAULT_FALLBACK,
) -> list[dict]:
    with seeds_path.open(encoding="utf-8-sig", newline="") as stream:
        seeds = list(csv.DictReader(stream))[:limit_pairs]
    if len(seeds) < limit_pairs:
        raise ValueError(f"requested {limit_pairs} pairs but manifest contains {len(seeds)}")
    fallback = load_fallback(fallback_path)
    cache: dict[str, tuple[list[str], str, str]] = {}
    rows = []
    retrieved = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    for seed in seeds:
        for order, prefix in ((1, "previous"), (2, "current")):
            url = seed[f"{prefix}_url"]
            if url not in cache:
                if cache and delay:
                    time.sleep(delay)
                try:
                    cache[url] = (fetch_blocks(url), "live_official_page", "ok")
                except Exception as error:
                    if url not in fallback:
                        raise RuntimeError(f"could not fetch {url} and no official fallback is available") from error
                    cache[url] = (
                        fallback[url],
                        "curated_official_page_fallback",
                        f"live fetch unavailable ({type(error).__name__}); used checked official-page evidence",
                    )
            blocks, source_mode, grab_status = cache[url]
            names, categories, evidence = _feature_payload(blocks)
            rows.append({
                "pair_id": seed["pair_id"], "brand": seed["brand"], "car_model": seed["car_model"],
                "version": seed[f"{prefix}_version"], "version_order": order,
                "release_date": seed[f"{prefix}_release_date"], "release_date_precision": "day",
                "newly_released_features": names, "feature_categories": categories,
                "feature_evidence": evidence,
                "cumulative_sales_year_1": "", "cumulative_sales_year_2": "",
                "cumulative_sales_year_3": "", "cumulative_sales_year_4": "",
                "sales_status": "official release page does not disclose version-level annual cumulative sales",
                "source_url": url, "source_mode": source_mode, "grab_status": grab_status,
                "retrieved_at": retrieved,
            })
    return rows


def write_csv(rows: list[dict], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=Path, default=DEFAULT_SEEDS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--fallback-evidence", type=Path, default=DEFAULT_FALLBACK)
    parser.add_argument("--pairs", type=int, default=20)
    parser.add_argument("--delay", type=float, default=0.15)
    args = parser.parse_args()
    rows = grab(args.seeds, args.pairs, max(0, args.delay), args.fallback_evidence)
    write_csv(rows, args.output)
    print(f"wrote {len(rows) // 2} official Chinese model pairs ({len(rows)} rows) to {args.output}")
    print(f"allowed categories: {', '.join(TECHNOLOGY_DOMAINS)}")


if __name__ == "__main__":
    main()
