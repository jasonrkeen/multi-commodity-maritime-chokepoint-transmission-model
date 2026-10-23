# Inventory depletion and release timing design 0.9

Status: **SPECIFIED_NOT_EXECUTED**. This is a separately versioned, outcome-informed follow-up to completed study 0.8, not an independent validation sample or a preregistration made before seeing 0.8. It does not amend the completed 689 cases, their results, the 0.6 replay rules, or any of the 38 blocked historical windows.

## Question and fixed mechanism

Study 0.8's maximum unbuffered loss was 4.458968 reference-production days, below every positive commercial and strategic stock level sampled. This follow-up asks where smaller stocks exhaust, how release rate/delay/ramp move the boundary, and whether additional strategic stock is unusable within the horizon because release capacity is limiting.

Keep the 0.8 diagnostic equations and units exactly: Q=81.157 million barrels/day, Suez/SUMED reference flow=3.6 million barrels/day, allocation=1, severity=1, disruption duration=90 days, recovery to 5%=30 days, rerouting=0. Days are integer 0–179; summaries use 30, 90 and 180 days. No replenishment, demand response, overlap, historical dates, probabilities or calibration is added. Do not combine routes. This deliberately conditions on one severe reference path; conclusions do not generalize to other paths or actual usable inventories.

## Frozen finite case design

Cross three release fractions of reference production per day (0.005, 0.01, 0.05), four delays (0, 7, 14, 30 days), and three ramps (1, 7, 14 days): 36 timing settings. The rate levels imply 0.405785, 0.811570 and 4.057850 million barrels/day, respectively; these are analyst stresses, not established deliverability estimates.

| Block | Stock design at each timing setting | Cases |
|---|---|---:|
| F | Commercial and strategic stocks independently take 0, 0.25, 0.5, 1, 2, 3, 4, 4.5, 5 reference-production days | 2,916 |
| T | Strategic stock = alpha times its unconstrained cumulative release requirement, alpha = 0.5, 0.99, 1, 1.01, 1.5; commercial stock = beta times the residual cumulative gap, beta = 0, 0.5, 0.99, 1, 1.01, 1.5 | 1,080 |
| N | Zero allocation and severity, stocks and release rate; delay 0, ramp 7 | 1 |

Total: **3,997 cases**, **719,460 daily rows**, **11,991 horizon summaries**. Keep duplicates with distinct IDs for accounting checks, never as independent observations. The frozen case table stores either physical stock days or threshold multipliers explicitly; multipliers must not be interpreted as stock days. T rows have null physical stock fields until deterministic materialization. No simulations or numerical T-row materialization were performed when this specification was frozen.

## Deterministic threshold definitions

For each timing setting, form the frozen gross-gap path G(t), and the requested release path A(t), both independent of inventories. For horizon H define:

- G_H = sum over t=0,...,H-1 of G(t), in reference-production days.
- R_H = sum of min(G(t), A(t)) over the same days. This is the release requirement with unlimited strategic stock, not an assumed inventory observation.
- With initial strategic stock S, cumulative actual release is min(S, R_H) because there is no replenishment and no other draw. The commercial stock required to avoid cumulative shortage is C_H(S)=G_H-min(S,R_H).

Materialize every T row using H=180: S=alpha R_180; C=beta C_180(S). Do not recompute starting inventories at shorter summary horizons. Thresholds at H=30 and H=90 are diagnostic outputs only. Freeze this algebraic mapping now; no searching for favorable outcomes, adaptive bisection, fitted thresholds, or output-driven refinement is permitted. Record materialized values at full precision and hash the materialized input table before executing case trajectories. R_180 and C_180(S) must be positive for all specified T settings; otherwise stop instead of silently collapsing the design.

Threshold equality means stock can reach zero on its final required draw while cumulative shortage remains zero. It must not be called failure merely because stock depleted. S>R_H is release-capacity-limited residual stock, not evidence that further stock has practical value. Initial emptiness, positive-stock depletion, and positive shortage are separate flags. For validation and classification, use an absolute 1e-10 tolerance in normalized stock/gap units; retain unrounded raw values, exact zero flags, and tolerance-based flags separately. Never alter dynamic equations by snapping or clipping residuals for presentation.

## Outputs and comparisons fixed before execution

Retain all 0.8 daily and horizon metrics, case identities and source/runtime hashes. Add cumulative gross gap, unconstrained cumulative release, actual release, strategic residual above/below requirement, C_H(S), commercial stock minus C_H(S), cumulative unmet production-days, and cumulative shortage in million barrels. Report depletion day (initially empty separately), first positive-shortage day, number of shortage days, and residual stock. Report raw and tolerance-based classification fields, with null day values where the event never occurs.

For every timing setting, show the joint commercial/strategic stock boundary and the F-grid points on either side; no interpolated empirical confidence band. Provide sampled ranges, all endpoint ties and their complete inputs for every block/horizon. Any optional price proxy remains illustrative and commercial-stock-invariant; no claim of calibrated prices or business losses follows.

Matched-factor rules:

1. F block: all unordered distinct levels of one numeric factor, holding every other physical input fixed. Report higher minus lower. This is the primary analysis of timing and capacity effects.
2. T block: compare alpha levels only at fixed timing and beta **as normalized design contrasts**, because changing alpha changes both S and materialized C; do not label these single-physical-factor effects. Compare beta levels at fixed timing and alpha as commercial-stock-only contrasts. Timing comparisons at fixed multipliers also alter physical stocks and must be labeled normalized multi-input comparisons, not isolated timing effects.
3. Do not match across blocks, select pairs by outcome, weight cases into expectations, calculate p-values or confidence intervals, or pool duplicates as independent observations. Retain zero effects. Document pair identities and all held-fixed fields.

## Implementation and execution gate

This turn specifies the study only. Before a later run, implement a separately versioned loader/materializer and runner; the 0.8 harness, loader pins, cases and outputs remain unchanged. Preserve the 0.8 equations through tests against its existing fixtures, while adding 0.9 fields outside the original module.

Required tests: exact case count/schema/unique IDs; frozen hash verification; units and multipliers; null physical fields rejected until materialized; deterministic materialization; zero-case invariance; conservation and stock budgets; timing boundary conventions (release zero on delay day); duplicate agreement; no overwrite and incomplete-output safeguards. Validate the cumulative identities above independently of the simulation loop. Test just-below/equal/just-above thresholds, a positive stock that exhausts before a later shortage, equality depletion without shortage, and release-limited unused inventory. Verify T-case shorter-horizon summaries retain their 180-day starting inventories. Test matching labels so normalized multi-input contrasts cannot be presented as single-factor physical effects.

Stop if any identity, fixture, coverage or hash check fails. Record implementation commit, source/runtime/test evidence and materialized-input hashes before execution; retain partial failed outputs distinctly. New grids or mechanism changes require a new version. No historical replay eligibility, public-data mapping or calibration status changes follow from specifying or executing this study.
