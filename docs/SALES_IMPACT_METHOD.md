# Sales-impact identification method

## Estimand

For each feature, subcategory or category, the analysis asks:

> Among independently observed Chinese nameplate trajectories with a complete baseline and four post-launch years,
> what additional market-adjusted sales change is associated with adding the target item, conditional on the observed
> launch bundle and vehicle context?

This is an observational estimand, not a causal claim.

## Unit of analysis

The 200 valid source pairs are evidence rows, not necessarily independent statistical observations. Rows with the same
nameplate, powertrain, sales provider, baseline and four annual sales values are collapsed into one trajectory. Their
feature evidence is unioned and their source pair IDs remain in `independent_observations.csv` for audit.

Only trajectories with all four post-launch years are used in the balanced estimation panel. This prevents a changing
sample composition from being mistaken for a four-year trend.

## Outcome and model

For trajectory `i` and relative year `k`:

```text
y_i,k = log(vehicle_sales_i,k / vehicle_sales_i,baseline)
        - log(segment_market_k / segment_market_baseline)
```

The target indicator and outcome are each residualised against an intercept, powertrain, standardised log baseline
sales, non-target bundle size, calendar-year indicators, recorded quality flags and supported peer-item indicators.
The coefficient from the residual-on-residual regression is the target's conditional association, following the
Frisch-Waugh-Lovell partial-regression result.

Uncertainty uses a nameplate-clustered CR1 covariance calculation. The percentage estimate is `100 × (exp(beta) - 1)`.
Absolute units compare observed treated sales with the fitted target-off counterfactual for the same nameplate:
`observed_sales × (1 - exp(-beta))`.

## Publication gates

An item is published only when every one of Years 1–4 has:

- at least five treated and five control nameplates;
- at least ten nameplate clusters;
- residual target information of at least 0.5 after controls;
- at least eight residual degrees of freedom;
- maximum leverage below 0.8; and
- clustered log standard error no greater than 0.35.

If any year fails, the API returns no effect series and reports the reasons. Planner uses a labelled neutral placeholder
instead of converting an unidentified association into a sales-volume scenario.

## Interpretation and limitations

The model removes broad NEV/ICE market movement and observed differences in the launch bundle. It cannot remove omitted
price changes, incentives, availability, production constraints, distribution, brand strength or undocumented redesign
changes. One pre-launch baseline also prevents a credible pre-trend test. Strong causal claims would require a richer
monthly panel, prices and incentives, repeated pre-periods, and a defensible natural experiment or instrument.

The approach is informed by partial regression and modern staggered-treatment/event-study diagnostics, while remaining
deliberately more conservative than a structural automobile-demand model:

- Frisch-Waugh-Lovell partial regression: <https://arxiv.org/abs/2009.06621>
- Callaway and Sant'Anna, multiple-period difference-in-differences: <https://arxiv.org/abs/1803.09015>
- Sun and Abraham, event studies with heterogeneous treatment effects: <https://arxiv.org/abs/1804.05785>
- Berry, Levinsohn and Pakes, differentiated automobile demand: <https://www.its.caltech.edu/~mshum/gradio/papers/BerryLevinsohnPakes1995.pdf>
