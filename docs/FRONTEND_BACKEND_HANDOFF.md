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

Terminal 2 (Node.js ≥ 20):

```bash
cd frontend
npm ci
npm run dev:backend
```

Open `http://localhost:5173`. `dev:backend` proxies `/api` to `http://localhost:8000`; plain `npm run dev` runs the
planner on the invented MSW mock data instead. Interactive API documentation is available at
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
| Final decision dashboard | `app/services/decision_dashboard.py` | edit the PM override layer |
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

## Planner (final page): `/api/v1`

The OpenTT planner in `frontend/` is the final page. Its contract is [`docs/API.md`](API.md); the backend implements
it in `app/services/planner.py` on real data, replacing the 16 invented mock candidates:

| Planner source | Backend data | Kind |
|---|---|---|
| candidates | the 13 selected Chinese-derived features (`forecast_catalog()`) | — |
| Customer | keyword-quantified F70/G60/G70 feedback: pain = negative, praise = positive mentions | evidence |
| Trends / Competition | sales-impact trend per feature, year 1 → year 4 after launch | assumption |
| Sales | BMW 2030 volume per line and market × conservative (lower-bound) year-4 uplift | scenario, marked as assumption |
| Product | G60/G70 option-list availability of the matching taxonomy attributes (`BMW_ATTRIBUTES`) | context only |

There is no observed sales response to these features yet (`comparisons_with_sales: 0` in the Chinese analysis), so
every Sales chip is marked `assumption` and each recommendation carries a flag saying so. `assumptionShare` is the
trends share, as the contract defines it.

The PM modifies the result in the interface: switch sources on or off, change weights, filter lines, markets,
feedback vehicles, signals and individual Chinese features, then run. Every run is stored in
`data/runtime/planner-runs/` and can be reopened from the run history.

`catalog.trendForecastLabels` (optional) relabels the trend chart; the backend uses it to show year 1 / year 4
sales uplift instead of the mock's "share of bestsellers" wording.

## Decision dashboard data (PM override layer)

### `GET /api/decision-dashboard/{vehicle}`

The same evidence as a flat per-vehicle table, for exports or a future editing view. It replaces dummy feature rows with the selected
Chinese-derived features and joins three evidence layers into every row:

- Chinese source-pair and model coverage;
- quantified customer comments: mentions, mention rate, positive/negative counts, need share, net sentiment,
  and traceable examples;
- sales-impact trend: estimate and uncertainty for years 1–4 after release.

Without a query parameter, comments come from the selected BMW vehicle's internal feedback workbook. To
build the page from an uploaded document, process it first and pass the returned ID:

```bash
curl 'http://127.0.0.1:8000/api/decision-dashboard/G60?document_id=<document_id>'
```

The first five features are selected by default. The PM-editable fields are `display_name`, `selected`,
`priority`, `engineering_status`, and `note`.

### `POST /api/decision-dashboard/overrides`

Save one feature's manual settings:

```json
{
  "vehicle": "G60",
  "feature": "Charging + battery-swap station network",
  "display_name": "Fast charging ecosystem",
  "selected": true,
  "priority": 1,
  "engineering_status": "approved",
  "note": "Include in the concept review."
}
```

`engineering_status` is `review`, `approved`, or `rejected`. Overrides are stored in
`data/runtime/decision-dashboard-overrides.json`. They change the PM presentation layer only; source
features, comments, and forecast evidence remain unchanged.

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

The processed response is also stored at `data/runtime/customer-input/<document_id>/result.json`, allowing
the final decision dashboard to reuse the document-derived comments.

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
cd frontend && npm test && npm run build
```

The backend tests cover raw-to-unified traceability, option parsing, forecast calculations, price scenarios,
engineering comparison, DOCX/text complaint processing, and generated complaint plots.
