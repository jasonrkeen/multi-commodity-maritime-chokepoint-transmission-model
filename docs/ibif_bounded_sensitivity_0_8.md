# Bounded sensitivity design 0.8

Status: **SPECIFIED_NOT_EXECUTED**. This is a hypothetical physical diagnostic, not a historical replay, calibration, forecast, or business-impact validation. The 0.6 freeze and its 38 blocked decisions remain unchanged.

## Scope and reference quantities

Use a separate deterministic diagnostic harness, with production code at commit `8cd7eea2e051923468e3285ce0156b8925daaca0` as equation lineage only. The harness must be implemented, reviewed, tested and hashed before execution. It intentionally excludes replenishment and other production-model responses; results cannot be represented as production-model runs.

Reference production Q is 81.157 million barrels/day (2022 crude plus condensate); route references are Suez/SUMED 3.6 and Bab el-Mandeb 3.3 million barrels/day, retaining the source and compatibility limits documented in the 0.5–0.7 physical-input ledgers. For allocation a, exposed fraction q = a × route flow / Q. Allocation is an analyst scenario, not an estimated canal/pipeline split. Stocks are days of reference production, not global demand coverage. Never combine the two routes: serial overlap remains unresolved. Panama slots have no crude conversion here.

All unresolved input levels are analyst-selected stresses, not empirically credible intervals. Zero explicitly means a no-buffer/no-response counterfactual, never missing-data imputation. Legacy stock levels 35 commercial days and 10 strategic days are stress anchors only; intermediate 7 and 5 days are arbitrary. A 5% daily release rate means 4.05785 million barrels/day and is deliberately strong, with no demonstrated global deliverability. Sampled rerouting and severity limits are not verified physical maxima.

## Fixed case design

The accompanying CSV contains 689 cases, with unique case IDs and no historical origin. Cartesian products are fixed before any outcomes:

| Block | Factors | Cases |
|---|---|---:|
| A | Route/allocation: Suez 0, 0.5, 1; Bab 1. Severity 0.25, 0.5, 1; duration 7, 30, 90 days; recovery 0, 14, 30 days; rerouting 0, 0.5, 0.75. No stocks/releases. | 324 |
| B | Suez allocation 1, severity 1, duration 90, recovery 30, rerouting 0. Commercial stocks 0, 7, 35; strategic stocks 0, 5, 10; release 0, 0.01, 0.05 per day; delay 0, 14 days; ramp 1, 7 days. | 108 |
| C | Suez, recovery 30, ramp 7. Allocation 0, 1; severity 0.25, 1; duration 7, 90; rerouting 0, 0.75; commercial stocks 0, 35; strategic stocks 0, 10; release 0, 0.05; delay 0, 14. | 256 |
| N | Zero exposure, severity, stocks and releases. | 1 |

Duplicates across blocks are intentional implementation cross-checks, not independent observations. Run 180 integer days t=0 through 179, giving 124,020 daily case rows; summarize at 30, 90 and 180 days. There are no calendar dates, stochastic draws or scenario probabilities.

## Exact diagnostic equations

For severity s, duration D and recovery R: E(t)=s when t<D. Thereafter E(t)=0 if R=0, otherwise s exp[-ln(20)(t-D)/R]. Thus positive R reaches 5% of severity R days after the plateau boundary; it is neither a half-life nor an exact end date.

Rerouting r(t)=r_max[1-exp(-t/10)]. Gross gap G=q E(t)[1-r(t)]. Starting each day with stocks C and S, requested strategic release is zero before delay d, otherwise v[1-exp(-(t-d)/ramp)]. Actual L=min(G, requested release, S); update S'=S-L. Market gap M=G-L. Commercial draw B=min(M,C); update C'=C-B. Physical shortage U=M-B. Stocks never replenish.

No demand adaptation, substitution, external response, insurance, risk premium, opacity, dependencies or sensor effects are included. An optional illustrative price proxy is P=82[1+min(1.5,M/0.18)]. These legacy constants are uncalibrated; commercial stocks affect U but not this price proxy by construction. No expected losses, VaR or IBIF scores are calculated.

## Outputs and interpretation

For each horizon report mean/peak M and U, cumulative shortage Q×sum(U) in million barrels, cumulative stock draws, minimum/end stocks, and first depletion day (null if never depleted). If a stock begins at zero, first depletion day is zero; distinguish this from exhaustion of a positive initial stock. Optional proxy outputs are mean/peak P and cap-binding days. Preserve daily rows and hashes linking each result to case, design, harness and runtime.

Report the complete grid, block ranges and endpoint inputs, plus matched single-factor contrasts. Min/max are only sampled extrema, not certified continuous bounds. Do not average cases into an expected forecast, assign probabilities, fit Brent outcomes, calculate p-values/confidence intervals, or bootstrap dependent daily rows. Do not adjust bounds after inspecting outcomes without a new version. Unexamined combinations, unresolved mappings and simplified mechanics limit all conclusions.

## Execution gate

Before execution, pin and hash the separate harness and runtime, then test nonnegative stocks; daily G=L+B+U conservation; total draws no greater than initial stocks; zero-exposure zero-gap behavior; zero strategic stock preventing release; delay/recovery boundary behavior; identical results for duplicate parameter cases; and invariance of the price proxy to commercial stocks. Include a hand-calculated fixture with normalized-unit tolerance 1e-10. Reject invalid/nonfinite parameters rather than clipping them. Stop on any failure.

The design manifest freezes this specification, configuration and case list using UTF-8/LF SHA-256. Freezing a design is not execution evidence. Historical eligibility can change only through a separately authorized, versioned evidence review, never through favorable sensitivity results.
