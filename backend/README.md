# Backend: unified input processor

Turns heterogeneous vehicle data into one hierarchical, quantified structure per vehicle.
This version uses no LLM API: parsing is rule-based and mapping is hand-curated.

```
internal files (data/*.xlsx, *.PDF) ─┐
                                     ├─► Observations ─► taxonomy.json mapping ─► Vehicle tree (data/unified/)
external records (data/external/)  ──┘   (flat, raw-linked)                         + report.html + FastAPI
```

## Run

```bash
cd backend
uv sync
uv run python -m app.unify           # rebuild data/unified/ (incl. report.html)
open ../data/unified/report.html     # check the results in a browser
uv run uvicorn app.api:app --reload  # API, http://127.0.0.1:8000/docs
uv run pytest
```

## Updating after new data

1. Put new internal files in `data/` or external records in `data/external/*.jsonl`.
2. Run `uv run python -m app.unify`. `coverage.json` and the report list the labels that are still unmapped.
3. Curate those labels into the structure. For now this is done in a Claude Code chat session (see `../CLAUDE.md`):
   - add raw labels as aliases in `taxonomy.json`, or add a new attribute when nothing fits;
   - turn raw external material (PDFs, social-media dumps, comments without a label) into labelled JSONL records.
4. Run `unify` again and check the report.

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
| ext:* | whatever the record states | as given |

## External input format (`app/external.py`)

`data/external/*.jsonl`, one record per line:

- `comment`: `source, vehicle, country|market, text, label, sentiment (like|want|difficult_to_use|defect|mention), url, retrieved_at`
- `metric`: `source, vehicle, market, competitor?, label, metric, value, unit, norm?, text?, url, retrieved_at`

See `examples/external_sample.jsonl`, which the tests use; it is not real data.

## Known data gaps

- No customer feedback from China. In China, G68 is covered only by the study.
- Sales for G60 and G68 come from a single combined sheet, so both vehicles carry the same numbers (noted in `text`).
- F70 has no US sales and no option list.
- Option lists are German PDFs (EU/DE prices). Paint, upholstery colours and individual wheel designs are left unmapped on purpose.
- About 1,180 feedback verbatims have no classification in the source (`no_class_found`). They are kept and can be labelled later.
