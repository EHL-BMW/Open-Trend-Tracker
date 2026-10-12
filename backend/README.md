# Backend: unified input processor

Turns heterogeneous vehicle data into one hierarchical, quantified structure per vehicle.
This version uses no LLM API: parsing is rule-based and mapping is hand-curated.

```
data/internal/ (xlsx, PDF)         ─┐
                                     ├─► Observations ─► taxonomy.json mapping ─► Vehicle tree (data/unified/)
data/external/ (jsonl, market csv) ──┘   (flat, raw-linked)                         + report.html + FastAPI
```

## Feature recommendation pipeline (main flow)

```bash
cd backend
uv run python -m app.pipeline        # writes data/pipeline/*.csv and data/pipeline/plots/*.pdf
```

| step | input | output (CSV + one PDF per step) |
|---|---|---|
| 1 existing features | option-list PDFs, incl. package contents | car, item, feature, category, standard/optional share, price |
| 2 comments | customer feedback | feature, category, sentiment, source comment; per car: need share, comment score |
| 3 external trends | **SYNTHETIC** (`app/dummy.py`) | month, feature, popularity (0-100), sales |
| 4 news | **SYNTHETIC** | date, feature, headline, impact (−1..+1) |
| 5 forecast | 3 + 4 | 12-month popularity and sales growth per feature |
| 6 engineering filter | `backend/engineering_filter.csv` (manual on/off, DUMMY labels) | feasible yes/no |
| 7 recommendation | 1, 2, 5, 6 | ranked feature list per car (F70, G60, G70) |

**Feature** = a taxonomy attribute; **category** = its taxonomy category (49 features). Outcome categories
(overall impression, quality, value & brand, market) are not features and are left out.

**Forecast (step 5)**, per feature, 12 months ahead:
- sales growth = log-linear trend of the last 24 months of sales + 5 % × recent news impact;
- popularity = mean(linear popularity trend, current popularity × (1 + sales growth)) + 10 points × recent news impact;
- recent news impact = Σ impact × exp(−age / 6 months), over the last 12 months.

**Score (step 7)** = Σ weight × component. Each component is scaled 0-1 across the feasible features:

| component | weight | meaning |
|---|---|---|
| trend | 0.25 | forecast popularity change |
| market | 0.25 | ½ current popularity + ½ sales growth forecast |
| comment | 0.30 | need share (want + difficult + defect) / mentions × √(relative volume) |
| gap | 0.20 | 0 = standard on every variant, 0.5 = optional, 0.75 = not listed, 0.5 = car has no option list |

Features the engineering filter switches off are not scored. They are listed as excluded.
The synthetic data (steps 3-4) is regenerated only when `data/external/synthetic/` is missing; delete it to regenerate.
Replace it with the partner's real feeds in the same columns.

## Unified data structure (raw-linked, for drill-down)

## Run

```bash
cd backend
uv sync
uv run python -m app.unify           # rebuild data/unified/ (incl. report.html)
open ../data/unified/report.html     # check the results in a browser
uv run uvicorn app.api:app --reload  # API, http://127.0.0.1:8000/docs
uv run pytest
```

The planner `/api/v1` contract, forecast/customer-input endpoints, response fields, and example calls
are documented in [`../docs/FRONTEND_BACKEND_HANDOFF.md`](../docs/FRONTEND_BACKEND_HANDOFF.md).

The API now keeps business logic in backend services:

- `GET /api/forecast/catalog` and `/api/forecast/sales` for the forecast page;
- `GET /api/forecast/prices/{vehicle}` for transparent option-price scenarios;
- `GET /api/engineering/features/{vehicle}` for the BMW catalog comparison as engineering input;
- `POST /api/customer-input/process` for document-to-complaint processing and a backend-generated figure.
- `GET /api/decision-dashboard/{vehicle}` joins Chinese-derived features, quantified comments, and
  four-year sales-impact trends; `POST /api/decision-dashboard/overrides` stores manual PM edits.

## Updating after new data

1. Put new internal files in `data/internal/` and external files in `data/external/`.
2. Run `uv run python -m app.unify`. `coverage.json` and the report list the labels that are still unmapped.
3. Curate those labels into the structure. For now this is done in a Claude Code chat session (see `../CLAUDE.md`):
   - add raw labels as aliases (exact labels) or keywords (free-text phrases) in `taxonomy.json`, or add a new attribute when nothing fits;
   - turn raw external material (PDFs, social-media dumps, comments without a label) into labelled JSONL records.
4. Run `unify` again and check the report (keyword matches are flagged `mapped_by: keyword`, so they are easy to review).
5. Bump `version` in `taxonomy.json` when the structure changes. Each output records the version it was built with.

Later, step 3 becomes an automated API step. It will write the same two kinds of files, so nothing else changes.

## Data model (`app/schema.py`)

**Observation**: one quantified fact from one raw record.
`vehicle, market, raw_label → attribute, metric, value, unit, norm (0..1, higher = better), raw (file + locator)`

**Vehicle tree**: `Vehicle → Market (EU/CN/US/RoW/ALL) → Category → Attribute → Metric`

- Every attribute has a `status`: `both | internal_only | external_only | no_data`. An `external_only` attribute is something only outside sources know about.
- `competitors` holds external facts about competitor vehicles, per attribute.
- `features` lists the raw labels that rolled up into the attribute.
- `unmapped` keeps every label the taxonomy cannot place yet. Nothing is dropped.
- `score` is the mean `norm` of the attribute's own metrics. A category score is the mean of its attribute scores.

**Raw ↔ unified link**: each `MetricSummary.obs_ids` → `observations.jsonl` → `raw.file` + `raw.locator`
(`GET /api/observations/{id}`). The reverse direction is `GET /api/observations?vehicle=&attribute=&market=`.

## Sources and metrics

| source | metrics | norm |
|---|---|---|
| feedback | like / want / difficult_to_use / defect / mention / unclassified (count) | via derived `feedback_balance` = likes / (likes + difficult + defects) |
| study_cn_eu | study_mean_0_10 | value / 10 |
| study_us | study_mean_1_7, study_bottom3_share | (mean−1)/6, 1 − share |
| sales | volume_2024, volume_2025, volume_2030F (units), growth_2025_2030F | – |
| options (rule-based PDF parse: ■ standard / □ optional per variant) | option_price (EUR), standard_fitment (share) | share |
| ext:ev_market_eu (EV/PHEV market table) | per powertrain: wltp_range, dc_charging_power, charging_time_10_80, base_price, power, accel_0_100, top_speed, battery_capacity, consumption, heat_pump_standard, towing_capacity, frunk/trunk_volume; ev_phev_sales_eu; has_feature | percentile within segment + powertrain, oriented so that higher = better |
| ext:* (JSONL) | whatever the record states | as given |

## External input (`app/external.py`)

### Official BMW website grabber

The deterministic BMW PressClub grabber creates a traceable first-check dataset with one row per model
version. It keeps only model families with at least two detected versions and limits feature categories to
the eight technology domains in `BMW_Technology_Domains_Ranking_and_Methodology.pdf`.

```bash
cd backend
uv run python -m app.grabbers.bmw_official --limit 20
```

Outputs: `data/external/bmw_official_first_20.json` and `.csv`. Each record contains the car model, version, release
date, newly released features with category and evidence, cumulative sales after years 1-5, and the official
source URL. BMW launch pages generally do not publish annual model-level sales, so sales remain null instead
of being estimated. To populate them from an official export, pass a CSV with `model,year,units`:

```bash
uv run python -m app.grabbers.bmw_official --limit 20 --sales-csv official_bmw_model_sales.csv
```

Analyze consecutive versions and feature/sales associations after the CSV has official sales values:

```bash
uv run python -m app.analysis.official_sales ../data/external/bmw_official_first_20.csv
```

This writes `data/analysis/version_sales_differences.csv` (year 1-4 absolute and percentage differences
versus the previous version), `feature_sales_associations.csv` (mean/median differences and positive-share
by newly added feature), a JSON summary, and PNG/PDF plots in `data/analysis/plots/`. Add an integer
`version_order` column when release dates alone
do not define the intended sequence. Feature results are observational associations, not proof of causation.

For the Chinese-OEM cohort, grab 20 explicit predecessor/successor pairs (40 rows) from official NIO and
Li Auto releases, then analyze them:

```bash
uv run python -m app.grabbers.chinese_official_pairs
uv run python -m app.analysis.official_sales ../data/external/chinese_official_20_pairs.csv \
  --output-dir ../data/analysis/chinese
```

The editable pair manifest is `backend/chinese_model_pair_seeds.csv`. `pair_id` keeps overlapping update
chains separate. NIO pages are fetched live. Li Auto's investor-relations host can reject non-browser HTTP
clients, so the grabber falls back to short, checked evidence from those same official pages and marks the
affected rows as `curated_official_page_fallback`. Official launch releases rarely disclose version-level
annual cumulative sales, so those fields remain blank until an official delivery export is joined.

When sales are unavailable, the analysis also writes `feature_catalog_by_category.csv`,
`feature_sales_impact_4_year_forecast.csv`, and a four-year scenario plot. Feature wording is standardized
into general archetypes and aggregated across all model pairs. The forecast is a market-wide planning
estimate, not a sales-fitted or causal model. It uses editable category priors, a feature multiplier, a
50%/72%/88%/100% adoption-saturation curve over years 1-4, and 35%-60% uncertainty based on independent-pair
coverage. When real version-level sales are added, use the observational association outputs above instead
of treating the scenario priors as measured impact.

Generate the interactive Plotly view for the older keyword-extracted 200-pair file (superseded by the
Chinese version pairs below, which feed the Impact tab):

```bash
uv run python -m app.analysis.interactive_feature_plot
```

The result is `data/analysis/chinese_200/plots/interactive_feature_impact.html`. It stacks category and
feature trajectories with years 1-4 on the x-axis and cumulative-sales improvement on the y-axis. Category
and feature buttons independently control visibility; every line includes its uncertainty band. A third,
separate figure uses `data/internal/sales_volumes.xlsx` to estimate BMW sales for 2030-2033. Choose a model,
market, and multiple features; the baseline extends the selected history's 2025-2030 CAGR and the feature
scenario applies the same additive impact rates and uncertainty ranges used in the feature plot.

**Chinese version pairs (Impact tab).** Curated in this chat session, not grabbed: the pipeline stays
deterministic. `data/external/chinese_pairs/` holds four CSVs, every row with a source URL:

- `pairs.csv`: one version change per row (`pair_id, brand, car_model, powertrain, change_type,
  nameplate_launch, previous_version, previous_launch, current_version, current_launch, source_url`).
  `nameplate_launch` is the line's first China launch. A nameplate first sold after February of the
  baseline year is retained with a `partial_baseline` quality flag. Pairs are taken from
  all Chinese brands, newest launch first, back in time year by year. Only launches whose first full
  sales year is complete are used.
- `features.csv`: what the current version added (`pair_id, detail, feature, subcategory, category,
  evidence, source_url`). `detail` is the OEM's own wording (e.g. "Shenxing 4C LFP battery"), `feature`
  the shared name used across brands (e.g. "4C+ fast-charging battery"), `subcategory` an id from
  `SUBCATEGORIES` in `app/analysis/chinese_pairs.py`, and `category` one of the 8 technology domains.
- `model_sales.csv`: annual China sales per nameplate (`car_model, year, units, series, source, url, note`).
  `series` names the source series (e.g. `gasgoo_wholesale`, `yiche_registrations`): a year compared with a
  baseline from a different series is marked `series_break` and not estimated.
- `market_sales.csv`: CPCA annual passenger-car retail, total and NEV, for the market adjustment.

```bash
uv run python -m app.analysis.four_year_seeds  # reproducible first 30 complete four-year pairs
uv run python -m app.analysis.chinese_pairs
```

This writes `data/analysis/chinese_pairs/`: `pair_sales.csv` (baseline and year 1-4 sales, raw and
market-adjusted change, `observed` / `missing_sales` / `not_yet_observable`, plus per-year quality flags
for a partial baseline or successor overlap), `feature_log.csv`,
`impact.csv` (per feature, subcategory and category: mean market-adjusted change of pairs that added it
minus pairs that did not, per year, with a 95% interval and n) and `plots/impact_by_subcategory.pdf`.
Year 1 is the launch year for a January-March launch, otherwise the next calendar year; the baseline is
the year before the launch year. A valid four-year pair has a numeric baseline and all four annual sales
comparisons. An item needs 5 pairs with sales in a year (and 5 without it) to get an estimate. The
results are observational associations, not causal effects; nameplate totals can include successor
updates and source-table provider changes. To extend the sample, add the next older
pairs (and their features and sales) to the CSVs and rerun. Newer pairs can be added once their first
sales year is complete.

**EV/PHEV market table** (`top_500_ev_phev_europe*.csv`, `;`-separated). BMW rows that are our vehicles become the vehicle's own
external facts: G60 = 5er/i5 Limousine (the Touring is G61, so it is excluded), G70 = 7er/i7. Non-BMW-Group rows in the same segment
become competitors: F70 → C-segment, G60 → E, G70 → F. Feature phrases are kept, except those that only restate a spec column.

**JSONL contract**: `data/external/*.jsonl`, one record per line:

- `comment`: `source, vehicle, country|market, text, label, sentiment (like|want|difficult_to_use|defect|mention), url, retrieved_at`
- `metric`: `source, vehicle, market, competitor?, label, metric, value, unit, norm?, text?, url, retrieved_at`

See `examples/external_sample.jsonl`, which the tests use; it is not real data.

## Known data gaps

- No customer feedback from China. In China, G68 is covered only by the study.
- Sales for G60 and G68 come from a single combined sheet, so both vehicles carry the same numbers (noted in `text`).
- F70 has no US sales and no option list.
- Option lists are German PDFs (EU/DE prices). Bare colour names are left unmapped on purpose. Wheels, trims and paint packages map by keyword.
- About 1,180 feedback verbatims have no classification in the source (`no_class_found`). They are kept and can be labelled later.
