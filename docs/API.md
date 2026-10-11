# OpenTT – API contract (v1)

The frontend is a pure client: it loads the filter catalog, sends the PM's weights and filter selections, and renders
what the backend computes (ranking, reasoning, graph data, flags). **All scoring happens in the backend.**

- Base path: `/api/v1` (the frontend calls it same-origin; in Docker, nginx proxies `/api/` to the backend).
- JSON only, UTF-8. Shares are floats `0–1`; weights in requests are integer percentages.
- Source of truth for shapes: [`frontend/src/api/schemas.ts`](../frontend/src/api/schemas.ts) (zod). The frontend
  validates every response against it and shows an error instead of rendering data that breaks the contract.
- A working reference implementation of every endpoint, including the scoring and reasoning texts, lives in
  [`frontend/src/mocks/engine.ts`](../frontend/src/mocks/engine.ts). The real-data implementation is
  [`backend/app/services/planner.py`](../backend/app/services/planner.py) (see `docs/FRONTEND_BACKEND_HANDOFF.md`).

## Fixed vocabulary

| Category key | Name in UI             | Weighted | Evidence or assumption |
| ------------ | ---------------------- | -------- | ---------------------- |
| `sales`      | Sales                  | yes      | evidence               |
| `customer`   | Customer               | yes      | evidence               |
| `trends`     | Trends / Competition   | yes      | assumption             |
| `features`   | Features / Engineering | **no**   | context only           |

The four categories are fixed in the frontend. Everything inside them (filter groups, values, labels) comes from
`GET /catalog`.

## Errors

Any non-2xx response should carry:

```json
{ "error": { "code": "stale_data_version", "message": "The data was updated. Reload the page.", "details": {} } }
```

`message` is shown to the PM as is, so write it for humans. Codes the frontend expects: `invalid_request` (400),
`not_found` (404), `stale_data_version` (409). 5xx and network failures are retried twice for reads.

---

## `GET /catalog`

Everything the PM can choose from. Called once on page load; the UI stays empty until it arrives.

```jsonc
{
  "dataVersion": "2026-10-11T08:00Z", // changes whenever the underlying data changes
  "forecastYear": 2030,
  "defaultWeights": { "sales": 45, "customer": 35, "trends": 20 }, // any positive numbers; normalised to 100
  "categories": {
    "sales": {
      "recordCount": 29,
      "filters": [
        { "key": "line", "label": "Line", "options": [{ "value": "i4", "label": "i4" } /* … */] },
        { "key": "powertrain", "label": "Powertrain", "options": [{ "value": "BEV", "label": "BEV" }, { "value": "PHEV", "label": "PHEV" }] }
      ]
    },
    "customer": {
      "recordCount": 27,
      "filters": [{ "key": "signal", "label": "Signal", "options": [{ "value": "pain", "label": "Pain points" }, { "value": "praise", "label": "Praise" }] }]
    },
    "features": {
      "recordCount": 12,
      "filters": [{ "key": "feature", "label": "Feature", "heading": "Existing BMW cars", "options": [{ "value": "heat-pump", "label": "Heat pump" } /* … */] }]
    },
    "trends": {
      "recordCount": 14,
      "filters": [{ "key": "technology", "label": "Technology", "heading": "China EV market", "options": [{ "value": "800v-charging", "label": "800V fast charging" } /* … */] }]
    }
  },
  "trendForecast": [
    // one entry per technology; `technology` must match an option value of trends → technology
    { "technology": "800v-charging", "label": "800V fast charging", "currentShare": 0.71, "forecastShare": 0.88 }
  ]
}
```

Notes

- Filter groups and their `key`s are free to change; the frontend renders whatever arrives. Only the Trends group
  `technology` has a special meaning (it links the forecast chart to the filter).
- `heading` is optional and shown above the group.
- `collapsible` is optional (`true` = the group starts collapsed and can be expanded, e.g. the product areas).
- `trendForecastLabels` is optional: `{ "title", "description", "current", "forecast" }` relabels the trend chart
  (default: technology share today vs. `forecastYear`). The axis scales to the largest value.
- A category with `"filters": []` renders an empty state.

## `POST /analyses`

Runs the analysis and **stores it** (audit trail). Sent when the PM clicks *Run analysis*.

Request

```jsonc
{
  "dataVersion": "2026-10-11T08:00Z", // from the catalog; reply 409 stale_data_version if it no longer matches
  "topN": 5,
  "weights": { "sales": 45, "customer": 35, "trends": 20 }, // integers, always sum to 100 (switched-off ones keep their frozen value)
  "enabled": { "sales": true, "customer": true, "trends": true },
  "filters": {
    // selected option values per group; every group of the catalog is present; [] = nothing selected
    "sales": { "line": ["i4", "i5", "ix"], "powertrain": ["BEV"] },
    "customer": { "signal": ["pain", "praise"] },
    "features": { "feature": ["heat-pump", "head-up-display"] },
    "trends": { "technology": ["800v-charging", "ar-hud"] }
  }
}
```

Scoring rules the UI assumes

- Effective weight of a weighted source = `weight / sum(weights of enabled sources)`; disabled sources get 0.
- `features` never contributes points; its matching records are returned as `context`.
- Deterministic: the same request on the same `dataVersion` must give the same ranking and the same `fingerprint`.
  Break ties deterministically (e.g. by candidate id).
- Return at most `topN` recommendations with a score > 0, ranked 1…N.

Response `201` – an **AnalysisRun**

```jsonc
{
  "id": "4b0c…", // opaque
  "createdAt": "2026-10-11T09:14:03Z",
  "fingerprint": "3359a40f", // hash of the normalised request + dataVersion
  "dataVersion": "2026-10-11T08:00Z",
  "request": { /* the request as received */ },
  "effectiveWeights": { "sales": 0.45, "customer": 0.35, "trends": 0.2 },
  "recommendations": [
    {
      "id": "c3",
      "rank": 1,
      "title": "Real-world winter range",
      "score": 99.3, // 0–100 = sum of contribution points
      "keep": false, // true when customers mainly praise it ("protect, don't change")
      "assumptionShare": 0.2, // share of the score coming from trends
      "specs": [
        // the combination that produced the rank; shown as chips. kind: evidence | assumption | context | missing
        // (the frontend shows its own source name as the chip label; `label` is informational)
        { "category": "sales", "label": "Sales", "text": "i4, iX, i5 · BEV", "kind": "evidence" },
        { "category": "customer", "label": "Customer", "text": "98 pain-point mentions · Powertrain", "kind": "evidence" },
        { "category": "features", "label": "Product", "text": "Heat pump · Standard on BEV · 64% take rate", "kind": "context" },
        { "category": "trends", "label": "Trends", "text": "Heat-pump thermal management · 66% → 90% by 2030", "kind": "assumption" }
      ],
      "reasoning": {
        "verdict": "Ranks #1 with 99.3 of 100. The biggest driver is Sales (45.0 pts): …", // one or two plain sentences
        "confidence": "mixed", // evidence-led | mixed | assumption-led
        "evidenceShare": 0.8,
        "contributions": [
          // one per enabled weighted source (also when it has no records: then points 0, records [])
          {
            "category": "sales",
            "points": 45.0, // categoryScore × weight
            "categoryScore": 100, // 0–100 within this source, relative to the best candidate
            "weight": 0.45, // effective weight
            "summary": "Sales signal across i4, iX, i5 (BEV): the strongest of all 16 candidates in this source.",
            "records": [
              // cited source records; share (0–1) = this record's part of the source signal, drives line thickness
              // url (optional) links the record to its source: a news article, an AI Agent problem, an OpenTT page
              { "id": "S-01", "label": "i4 · BEV · signal 0.80", "share": 0.35, "url": "/sales-impact-forecast" }
            ]
          }
        ],
        "context": [
          { "category": "features", "summary": "BMW already offers Heat pump (Standard on BEV, 64% take rate).", "records": [ /* … */ ] }
        ],
        "flags": [
          // severity: ok | info | warning
          { "severity": "info", "message": "The 2030 trend forecast extrapolates today's China EV bestsellers. …" }
        ]
      }
    }
  ]
}
```

The frontend draws the reasoning graph only from `contributions[].records` and `points`; there is no separate graph
payload.

## `GET /analyses?limit=20`

Most recent runs first.

```jsonc
{
  "items": [
    {
      "id": "4b0c…",
      "createdAt": "2026-10-11T09:14:03Z",
      "fingerprint": "3359a40f",
      "effectiveWeights": { "sales": 0.45, "customer": 0.35, "trends": 0.2 },
      "enabled": { "sales": true, "customer": true, "trends": true },
      "topTitles": ["Real-world winter range", "Steering & handling feel" /* … */]
    }
  ]
}
```

## `GET /analyses/{id}`

The full **AnalysisRun** as returned by `POST /analyses`. Used to reopen a run: the frontend restores its weights
and filters (dropping values no longer in the catalog) and shows its results. `404 not_found` if unknown.

## Not covered yet

- Authentication: none. When added, the frontend client (`frontend/src/api/client.ts`) is the single place to attach
  a token or rely on cookies; the PM's identity should then be stored with each run for the audit trail.
- PM decisions per recommendation (accept / change / reject / defer) are not part of v1.
