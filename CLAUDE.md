<!-- entire-graph:begin -->
This repo has the entire-graph code graph installed. Before exploring code with
grep/find/whole-file reads, read .entire/graph-agent.md — resolution-first guidance
for using graph retrieval, focused source inspection, and verification.
@.entire/graph-agent.md
<!-- entire-graph:end -->

# Open-Trend-Tracker

Decision support for BMW product managers. The backend (`backend/`, Python, uv) unifies internal and
external data into a per-vehicle tree. The frontend (`frontend/`, Vite + React + TypeScript) is the PM planner; its API contract is `docs/API.md`.
Details are in `backend/README.md`.

## No LLM API in the pipeline (current version)

The pipeline is deterministic and makes no LLM calls. Do not add an LLM SDK or API calls. The work that
needs judgement is done here in the chat session, by editing the files below. A later version will
automate it through an API.

## Regenerating the data structure after a data update

1. New files go to `data/internal/` or `data/external/`. A new external format needs a small reader in
   `backend/app/external.py` (see `ev_market` for a table example). Then run `cd backend && uv run python -m app.unify`.
2. Read `data/unified/coverage.json` → `unmapped_labels`, grouped by source.
3. Curate `backend/taxonomy.json`:
   - add each customer-facing raw label, exactly as printed, to the `aliases` of the right attribute;
   - for free-text feature phrases, add a distinctive substring to `keywords` instead (the longest matching keyword
     wins). Then check `mapped_by: keyword` results for wrong matches and fix them with a longer keyword;
   - if no attribute fits, add a new attribute with `id`, `name` and `aliases` to the best category;
   - each alias may appear under only one attribute (the mapper raises an error on duplicates);
   - leave labels that are not product attributes unmapped on purpose: `no_class_found`,
     `General enquiry: customer feedback`, bare colour names (e.g. "Schwarz", "Mokka"), legal notes.
4. Turn raw external material into `data/external/<name>.jsonl` records, following the format in
   `backend/app/external.py`:
   - technical PDFs → `metric` records with `competitor` set when the fact is about another vehicle;
   - social media or review text → `comment` records with `label` and `sentiment`;
   - keep `url` and a short quote in `text` so every record stays traceable.
5. Bump `version` in `taxonomy.json` if the structure changed. Before regenerating a new version, move the old
   output to `data/unified_v<N>` so the two can be compared.
6. Rerun `unify` and `uv run pytest`. Report what changed: newly mapped counts, new attributes, labels left unmapped.

## Recommendation pipeline

`uv run python -m app.pipeline` runs steps 1-7 (see `backend/README.md`). Steps 3-4 use SYNTHETIC data
from `backend/app/dummy.py`. Never present those numbers as real, and replace them when real feeds arrive.
`backend/engineering_filter.csv` holds DUMMY engineer labels: engineers edit `feasible` on/off.
Figures are PDF only.

## Conventions

- Raw data in `data/` is confidential and gitignored. Never commit it and never publish it.
- Every observation must keep a `RawRef` (file + locator) back to its source.
