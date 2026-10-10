# Open-Trend-Tracker

Decision support for BMW product managers. The backend (`backend/`, Python, uv) unifies internal and
external data into a per-vehicle tree. The frontend (`frontend/`, Vite + React) is a placeholder for now.
Details are in `backend/README.md`.

## No LLM API in the pipeline (current version)

The pipeline is deterministic and makes no LLM calls. Do not add an LLM SDK or API calls. The work that
needs judgement is done here in the chat session, by editing the files below. A later version will
automate it through an API.

## Regenerating the data structure after a data update

1. Run `cd backend && uv run python -m app.unify`.
2. Read `data/unified/coverage.json` → `unmapped_labels`, grouped by source.
3. Curate `backend/taxonomy.json`:
   - add each customer-facing raw label, exactly as printed, to the `aliases` of the right attribute;
   - if no attribute fits, add a new attribute with `id`, `name` and `aliases` to the best category;
   - each alias may appear under only one attribute (the mapper raises an error on duplicates);
   - leave labels that are not product attributes unmapped on purpose: `no_class_found`,
     `General enquiry: customer feedback`, paint/upholstery colours, wheel designs, legal notes.
4. Turn raw external material into `data/external/<name>.jsonl` records, following the format in
   `backend/app/external.py`:
   - technical PDFs → `metric` records with `competitor` set when the fact is about another vehicle;
   - social media or review text → `comment` records with `label` and `sentiment`;
   - keep `url` and a short quote in `text` so every record stays traceable.
5. Rerun `unify` and `uv run pytest`. Report what changed: newly mapped counts, new attributes, labels left unmapped.

## Conventions

- Raw data in `data/` is confidential and gitignored. Never commit it and never publish it.
- Every observation must keep a `RawRef` (file + locator) back to its source.
