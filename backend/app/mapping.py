"""Raw label -> canonical attribute, using the curated taxonomy.json.

1. alias:   the label equals one of an attribute's aliases (case- and whitespace-insensitive).
2. keyword: otherwise, the label contains one of an attribute's keywords; the longest matching
            keyword wins, ties go to the attribute listed first. Meant for free-text feature lists.
A label matching neither stays unmapped and is reported in coverage.json, never dropped.
"""
import json

from app.paths import TAXONOMY_FILE
from app.schema import Observation


def key(label: str) -> str:
    return " ".join(label.lower().split())


class Mapper:
    def __init__(self):
        tax = json.loads(TAXONOMY_FILE.read_text())
        self.version = tax["version"]
        self.categories = {c["id"]: c["name"] for c in tax["categories"]}
        self.attributes = {}  # id -> {name, category}
        self.aliases = {}     # label key -> attribute id
        self.keywords = []    # (keyword, attribute id), in taxonomy order
        for c in tax["categories"]:
            for a in c["attributes"]:
                self.attributes[a["id"]] = {"name": a["name"], "category": c["id"]}
                for alias in a["aliases"] + [a["id"], a["name"]]:
                    k = key(alias)
                    if self.aliases.get(k, a["id"]) != a["id"]:
                        raise ValueError(f"alias {alias!r} is listed under both {self.aliases[k]} and {a['id']}")
                    self.aliases[k] = a["id"]
                self.keywords += [(key(kw), a["id"]) for kw in a.get("keywords", [])]

    def lookup(self, label: str) -> tuple[str | None, str | None]:
        k = key(label)
        if k in self.aliases:
            return self.aliases[k], "alias"
        hits = [(kw, attr) for kw, attr in self.keywords if kw in k]
        if hits:
            return max(hits, key=lambda h: len(h[0]))[1], "keyword"  # max keeps the first of equal lengths
        return None, None

    def apply(self, obs: list[Observation]) -> None:
        for o in obs:
            o.attribute, o.mapped_by = self.lookup(o.raw_label)
