"""Raw label -> canonical attribute, using the curated aliases in taxonomy.json.

A label the taxonomy does not know stays unmapped and is reported in coverage.json, never dropped.
After a data update, the unmapped list is what gets curated into taxonomy.json (see CLAUDE.md).
"""
import json

from app.paths import TAXONOMY_FILE
from app.schema import Observation


def key(label: str) -> str:
    return " ".join(label.lower().split())


class Mapper:
    def __init__(self):
        tax = json.loads(TAXONOMY_FILE.read_text())
        self.categories = {c["id"]: c["name"] for c in tax["categories"]}
        self.attributes = {}  # id -> {name, category}
        self.aliases = {}     # label key -> attribute id
        for c in tax["categories"]:
            for a in c["attributes"]:
                self.attributes[a["id"]] = {"name": a["name"], "category": c["id"]}
                for alias in a["aliases"] + [a["id"], a["name"]]:
                    k = key(alias)
                    if self.aliases.get(k, a["id"]) != a["id"]:
                        raise ValueError(f"alias {alias!r} is listed under both {self.aliases[k]} and {a['id']}")
                    self.aliases[k] = a["id"]

    def apply(self, obs: list[Observation]) -> None:
        for o in obs:
            o.attribute = self.aliases.get(key(o.raw_label))
