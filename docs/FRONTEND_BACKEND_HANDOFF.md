# Frontend/backend handoff

This is the integration contract for the forecast and customer-input pages. All data acquisition,
preprocessing, mapping, forecast math, price assumptions, BMW comparison logic, and plot generation live
in `backend/`. The frontend should fetch the API and render the returned values; it should not duplicate
the formulas.

## Start the application

Terminal 1:

```bash
cd backend
uv sync
uv run python -m app.unify
uv run uvicorn app.api:app --reload
```

Terminal 2:

```bash
cd frontend
npm install
npm run dev
```

The Vite server proxies `/api` to `http://127.0.0.1:8000`. Interactive API documentation is available at
`http://127.0.0.1:8000/docs`.

## Architecture and ownership

| Responsibility | Backend owner | Frontend responsibility |
|---|---|---|
| Official web acquisition | `app/grabbers/` | none |
| Raw BMW/external preprocessing | `app/internal.py`, `app/external.py` | none |
| Taxonomy mapping and traceability | `app/mapping.py`, `app/unify.py` | show returned labels/evidence |
| Feature-impact forecast | `app/analysis/official_sales.py` | select features and render series |
| BMW 2030–2033 forecast | `app/services/forecast.py` | call endpoint and display values |
| Option-price forecast | `app/services/forecast.py` | display values and caveat |
| BMW feature comparison for engineering | `app/services/forecast.py` | review/edit in a future workflow |
| Customer document processing | `app/services/customer_input.py` | upload and show returned rows |
| Customer complaint figure | generated in backend runtime storage | display `figure_url` |
| Static pipeline/report plots | `app/plots.py`, `app/analysis/` | link or display generated artifacts |

Example backend-generated plots are committed in `backend/examples/plots/`.

## Forecast page APIs

### `GET /api/forecast/catalog`

Use this once when the page loads. It returns:

- `features[]`: name, category, independent pair/model coverage, and `estimate`, `lower`, `upper` arrays
  for years 1–4 after launch;
- `bmw_sales_history`: available model and market choices plus 2024, 2025, and 2030 values;
- `horizon_years`, method, status, and caveat.

The feature impacts are planning scenarios. They use category priors, feature multipliers, adoption
saturation, and uncertainty based on independent-pair coverage. They are not causal estimates.

### `GET /api/forecast/sales`

Parameters:

- `model` — exact key from `bmw_sales_history`, for example `G60/G68`;
- `market` — exact model-market key, normally `Global`, `EU`, `CN`, `US`, or `RoW`;
- `feature` — repeat this parameter for every selected catalog feature.

Example:

```bash
curl -G http://127.0.0.1:8000/api/forecast/sales \
  --data-urlencode 'model=G60/G68' \
  --data-urlencode 'market=Global' \
  --data-urlencode 'feature=900V system + 102 kWh battery' \
  --data-urlencode 'feature=World-model ADAS + point-to-point navigation'
```

Important response fields:

- `years`: `[2030, 2031, 2032, 2033]`;
- `baseline`: continuation of the selected series' 2025–2030 CAGR;
- `estimate`, `lower`, `upper`: sales with selected feature impacts;
- `impact`: combined feature uplift in percentage points;
- `selected_features`, `status`, `caveat`.

Do not recalculate these arrays in the frontend.

### `GET /api/forecast/prices/{vehicle}`

Optional parameters are `target_year` (default `2030`) and `annual_rate` as a decimal (default `0.025`).
The backend groups positive BMW option-list prices by canonical feature, uses the median current price,
and compounds the explicit annual rate from 2026. Missing prices are not invented.

```bash
curl 'http://127.0.0.1:8000/api/forecast/prices/G60?target_year=2030&annual_rate=0.025'
```

Use `items[].forecast_price_eur` on the forecast page and always show `caveat`: this is an option-price
reference scenario, not a supplier cost, BOM, margin, or transaction-price forecast.

## BMW comparison as engineering input

### `GET /api/engineering/features/{vehicle}`

Currently supported catalog vehicles are `G60` and `G70`. Each canonical feature has:

- `availability`: `standard`, `optional`, or `not_listed`;
- `standard_share` and `optional_share` from catalog variant markers;
- `engineering_input`: `true` when the feature is optional or not listed;
- `sources`: option-list PDF/page evidence.

This endpoint turns the existing BMW comparison into structured engineering review input. It does **not**
claim that `not_listed` means technically infeasible. The engineer remains responsible for feasibility.

## Customer input: document → complaint data + figure

### `POST /api/customer-input/process`

Send multipart form data with field name `document`. Supported types are `.txt`, `.md`, `.csv`, `.json`,
`.pdf`, and `.docx`; the limit is 10 MB.

```bash
curl -F 'document=@customer_feedback.docx' \
  http://127.0.0.1:8000/api/customer-input/process
```

The response contains:

- `complaints[]`: traceable statement, sentiment, taxonomy feature/category, and mapping method;
- `sentiment_counts` and `feature_counts`;
- `figure_url`: a backend-generated PNG, for example
  `/api/artifacts/customer-input/<document_id>/complaints.png`;
- method and caveat.

The processor is deterministic: sentence splitting, transparent keyword sentiment rules, and the shared
taxonomy mapper. Keep `Unclassified` rows visible so a product manager can review them; do not silently
discard them.

## Existing evidence APIs

- `GET /api/vehicles`
- `GET /api/vehicles/{code}`
- `GET /api/vehicles/{code}/markets/{market}`
- `GET /api/observations/{id}`
- `GET /api/observations?vehicle=G60&attribute=touchscreen&market=US`
- `GET /api/coverage`

An attribute's observation IDs link the summarized tree back to the original file, sheet/row, or PDF page.

## Data refresh commands

Run only the jobs needed for the changed source:

```bash
cd backend

# Unified BMW/internal/external evidence
uv run python -m app.unify

# Ranked recommendation pipeline and its PDFs
uv run python -m app.pipeline

# Refresh official Chinese predecessor/successor pairs
uv run python -m app.grabbers.chinese_official_pairs

# Rebuild version comparison, feature forecast, PNG, and PDF artifacts
uv run python -m app.analysis.official_sales ../data/external/chinese_official_20_pairs.csv \
  --output-dir ../data/analysis/chinese

# Rebuild the standalone interactive forecast example
uv run python -m app.analysis.interactive_feature_plot
```

The input and generated `data/` directory remains gitignored because it contains provided/private datasets.
Code, editable manifests, tests, documentation, and small example plot outputs are versioned.

## Error handling

- `404`: unknown model, market, feature, vehicle, or missing BMW price/catalog evidence;
- `422`: invalid price assumptions or unsupported/malformed customer document;
- `503`: required forecast/unified input has not been generated locally.

The frontend should display the API `detail` field. Do not substitute zero for unavailable data.

## Verification

```bash
cd backend && uv run pytest
cd frontend && npm run build
```

The backend tests cover raw-to-unified traceability, option parsing, forecast calculations, price scenarios,
engineering comparison, DOCX/text complaint processing, and generated complaint plots.
