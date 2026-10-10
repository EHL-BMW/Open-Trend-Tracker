"""Unified data model.

Two layers:
  Observation  - flat, one quantified fact taken from one raw record (internal or external).
                 Carries `raw` so every number can be traced back to file + row/page.
  VehicleNode  - the hierarchical view built from observations:
                 Vehicle -> Market -> Category -> Attribute -> Metric (-> obs_ids -> raw).
"""
from typing import Literal

from pydantic import BaseModel

Origin = Literal["internal", "external"]
Status = Literal["both", "internal_only", "external_only", "no_data"]


class RawRef(BaseModel):
    file: str     # path relative to the data folder (or a URL for web sources)
    locator: str  # where inside the file, e.g. "sheet=US_2025 row=107" or "page=12"


class Observation(BaseModel):
    id: str
    origin: Origin
    source: str                       # feedback | study_cn_eu | study_us | sales | options | ext:<name>
    vehicle: str                      # BMW e-code the fact is relevant to, e.g. "G60"
    market: str                       # EU | CN | US | RoW
    country: str | None = None
    competitor: str | None = None     # set when the fact describes a competitor, not the BMW vehicle
    raw_label: str                    # label exactly as in the source
    attribute: str | None = None      # canonical attribute id from taxonomy.json; None = not (yet) mapped
    metric: str                       # e.g. like, defect, study_mean_0_10, volume, option_price
    value: float
    unit: str                         # count | units | 0-10 | 1-7 | share | EUR | ...
    norm: float | None = None         # 0..1, higher = better for the customer; None if no natural scale
    period: str | None = None         # e.g. "2025", "2030F"
    text: str | None = None           # verbatim / quote, when there is one
    raw: RawRef


class MetricSummary(BaseModel):
    value: float
    unit: str
    norm: float | None
    n: int                 # number of observations aggregated
    sources: list[str]
    obs_ids: list[str]     # unified -> observation -> raw


class AttributeNode(BaseModel):
    id: str
    name: str
    status: Status         # which branches know about this attribute
    score: float | None    # mean norm over own (non-competitor) metrics
    sources: dict[str, int]
    features: dict[str, int]                         # raw labels that rolled up here -> count
    metrics: dict[str, MetricSummary]
    competitors: dict[str, dict[str, MetricSummary]]  # competitor -> metric -> summary


class CategoryNode(BaseModel):
    id: str
    name: str
    score: float | None
    attributes: dict[str, AttributeNode]


class MarketNode(BaseModel):
    market: str
    n_observations: int
    categories: dict[str, CategoryNode]
    unmapped: dict[str, int]   # raw labels no mapping could place -> count


class VehicleNode(BaseModel):
    vehicle: str
    line: str
    generated_at: str
    markets: dict[str, MarketNode]   # includes "ALL"
