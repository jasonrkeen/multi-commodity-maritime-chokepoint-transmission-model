# Frozen sensitivity study 0.8: executed results

Status: **HYPOTHETICAL_DIAGNOSTIC_EXECUTED_NOT_CALIBRATED**. Executed October 22, 2026 using the harness at `2d466655267b86e9921c59782fd86606e1cd7b8f`, Python 3.14.4 on Windows. This is a separate simplified physical diagnostic, not a production-model run, historical replay, calibrated forecast or business-impact estimate.

All 689 frozen cases ran for 180 days: 124,020 daily records and 2,067 horizon summaries. There are 657 unique parameter combinations and 32 repeated case rows; duplicates agree exactly and are not independent observations. Both original frozen manifests and all 38 blocked replay decisions remain unchanged. The original design file retains its historical not-run label; execution status is recorded separately here and in the output manifest.

## Sampled ranges

Gap and shortage percentages use the fixed 81.157 million-barrel/day reference-production denominator. They are not shares of world demand. The following are sampled extrema, not confidence intervals or certified continuous bounds. No probabilities or across-case expected values are assigned.

| Block | Horizon (days) | Mean market gap (% reference production) | Mean physical shortage (%) | Cumulative shortage (million barrels) | Mean illustrative price proxy ($/bbl) |
|---|---:|---:|---:|---:|---:|
| ALL | 30 | 0.000 to 4.436 | 0.000 to 4.436 | 0.000 to 108.000 | 82.000 to 102.208 |
| ALL | 90 | 0.000 to 4.436 | 0.000 to 4.436 | 0.000 to 324.000 | 82.000 to 102.208 |
| ALL | 180 | 0.000 to 2.477 | 0.000 to 2.477 | 0.000 to 361.877 | 82.000 to 93.285 |
| A | 30 | 0.000 to 4.436 | 0.000 to 4.436 | 0.000 to 108.000 | 82.000 to 102.208 |
| A | 90 | 0.000 to 4.436 | 0.000 to 4.436 | 0.000 to 324.000 | 82.000 to 102.208 |
| A | 180 | 0.000 to 2.477 | 0.000 to 2.477 | 0.000 to 361.877 | 82.000 to 93.285 |
| B | 30 | 0.194 to 4.436 | 0.000 to 4.436 | 0.000 to 108.000 | 82.884 to 102.208 |
| B | 90 | 0.065 to 4.436 | 0.000 to 4.436 | 0.000 to 324.000 | 82.295 to 102.208 |
| B | 180 | 0.032 to 2.477 | 0.000 to 2.477 | 0.000 to 361.877 | 82.147 to 93.285 |
| C | 30 | 0.000 to 4.436 | 0.000 to 4.436 | 0.000 to 108.000 | 82.000 to 102.208 |
| C | 90 | 0.000 to 4.436 | 0.000 to 4.436 | 0.000 to 324.000 | 82.000 to 102.208 |
| C | 180 | 0.000 to 2.477 | 0.000 to 2.477 | 0.000 to 361.877 | 82.000 to 93.285 |
| N | 30 | 0.000 to 0.000 | 0.000 to 0.000 | 0.000 to 0.000 | 82.000 to 82.000 |
| N | 90 | 0.000 to 0.000 | 0.000 to 0.000 | 0.000 to 0.000 | 82.000 to 82.000 |
| N | 180 | 0.000 to 0.000 | 0.000 to 0.000 | 0.000 to 0.000 | 82.000 to 82.000 |

Blocks: A varies route/disruption/rerouting without stocks; B varies stocks/releases under a fixed severe Suez/SUMED shock; C combines corner settings; N is the null case. The peak proxy spans $82.000–$102.208/bbl overall at every horizon. Every B case peaks at $102.208/bbl, and no price cap binds. This follows from release and rerouting both starting at zero on day 0. Commercial stocks do not enter the price equation; their unchanged proxy is by construction, not evidence about real price formation.

## Endpoint cases

The table gives the first case ID in frozen order at each cumulative-shortage endpoint, and counts every exact tie. All tied IDs for all reported metrics are preserved in `ranges.json`; complete endpoint inputs are recoverable from `cases.json` and the frozen CSV. Display rounding does not define ties.

| Block | Horizon | Minimum case | Minimum ties | Maximum case | Maximum ties |
|---|---:|---|---:|---|---:|
| ALL | 30 | A0001 | 346 | A0226 | 32 |
| ALL | 90 | A0001 | 346 | A0235 | 29 |
| ALL | 180 | A0001 | 346 | A0241 | 27 |
| A | 30 | A0001 | 81 | A0226 | 6 |
| A | 90 | A0001 | 81 | A0235 | 3 |
| A | 180 | A0001 | 81 | A0241 | 1 |
| B | 30 | B0037 | 72 | B0001 | 20 |
| B | 90 | B0037 | 72 | B0001 | 20 |
| B | 180 | B0037 | 72 | B0001 | 20 |
| C | 30 | C0001 | 192 | C0225 | 6 |
| C | 90 | C0001 | 192 | C0225 | 6 |
| C | 180 | C0001 | 192 | C0225 | 6 |
| N | 30 | N0001 | 1 | N0001 | 1 |
| N | 90 | N0001 | 1 | N0001 | 1 |
| N | 180 | N0001 | 1 | N0001 | 1 |

**A0241** is the unique block-A maximum at 180 days: Suez/SUMED reference flow 3.6 million barrels/day; allocation 1; severity 1; duration 90 days; recovery to 5% in 30 days; rerouting 0; both inventories and release rate 0; release delay 0 and ramp 7 days (inactive). Its cumulative shortage is **361.876503 million barrels**, mean market/physical gap **2.477205%**, and mean proxy **$93.285044/bbl**. There are 27 tied cases at the overall shortage maximum, including B0001 and C0225; these ties do not provide independent corroboration.

**A0226** represents the 30-day maximum (108 million barrels): the same full allocation/severity and zero stocks/rerouting, with duration 30 and abrupt recovery. **A0235** represents the 90-day maximum (324 million barrels), with duration 90 and abrupt recovery. A0001 is a zero-allocation minimum; N0001 explicitly has zero allocation and severity. Zero-shortage endpoints also occur with sufficient hypothetical stocks and should not be conflated with zero exposure.

**B0021** represents the minimum block-B mean market gap at 180 days: commercial stock 0, strategic stock 5 production-days, daily release fraction 0.05, delay 0, ramp 1; other shock settings match A0241. Its mean gap is **0.032353%**, cumulative shortage **4.726270 million barrels**, and mean proxy **$82.147388/bbl**. B0033 (10 strategic days) gives the same result. The peak proxy remains unchanged because release is zero on day 0.

## Matched-factor comparisons

Method: all unordered pairs of distinct factor levels within each block, holding every other modeled input identical. Numeric deltas are higher-level minus lower-level; the route contrast is Suez/SUMED minus Bab el-Mandeb. This yields **3,076 pairs**, each evaluated at three horizons (**9,228 pair-horizon records**). All pairs are retained, including inert zero-exposure/release combinations. Matching/reporting details were specified for this analysis, not claimed as a separately preregistered statistical test. No cross-block matching or across-pair averages are used.

Below are all 180-day factor-level comparison groups. Values are the minimum and maximum paired change in cumulative physical shortage, in million barrels. Negative values mean lower modeled shortage. Full deltas and endpoint pair IDs for every metric and horizon are in `matched_pairs.json` and `matched_ranges.json`.

| Block | Factor | Lower → higher | Pairs | Shortage change (million barrels) |
|---|---|---|---:|---:|
| A | route_reference | bab → suez_sumed | 81 | 0.429 to 30.156 |
| A | allocation | 0.0 → 0.5 | 81 | 2.573 to 180.938 |
| A | allocation | 0.0 → 1.0 | 81 | 5.146 to 361.877 |
| A | allocation | 0.5 → 1.0 | 81 | 2.573 to 180.938 |
| C | allocation | 0.0 → 1.0 | 128 | 0.000 to 361.877 |
| A | severity | 0.25 → 0.5 | 108 | 0.000 to 90.469 |
| A | severity | 0.25 → 1.0 | 108 | 0.000 to 271.407 |
| A | severity | 0.5 → 1.0 | 108 | 0.000 to 180.938 |
| C | severity | 0.25 → 1.0 | 128 | 0.000 to 271.407 |
| A | duration_days | 7 → 30 | 108 | 0.000 to 82.800 |
| A | duration_days | 7 → 90 | 108 | 0.000 to 298.800 |
| A | duration_days | 30 → 90 | 108 | 0.000 to 216.000 |
| C | duration_days | 7 → 90 | 128 | 0.000 to 298.795 |
| A | recovery_to_5pct_days | 0 → 14 | 108 | 0.000 to 18.688 |
| A | recovery_to_5pct_days | 0 → 30 | 108 | 0.000 to 37.881 |
| A | recovery_to_5pct_days | 14 → 30 | 108 | 0.000 to 19.193 |
| A | reroute_fraction | 0.0 → 0.5 | 108 | -162.024 to 0.000 |
| A | reroute_fraction | 0.0 → 0.75 | 108 | -243.037 to 0.000 |
| A | reroute_fraction | 0.5 → 0.75 | 108 | -81.012 to 0.000 |
| C | reroute_fraction | 0.0 → 0.75 | 128 | -243.037 to 0.000 |
| B | commercial_production_days | 0.0 → 7.0 | 36 | -361.877 to -4.726 |
| B | commercial_production_days | 0.0 → 35.0 | 36 | -361.877 to -4.726 |
| B | commercial_production_days | 7.0 → 35.0 | 36 | 0.000 to 0.000 |
| C | commercial_production_days | 0.0 → 35.0 | 128 | -361.877 to 0.000 |
| B | strategic_production_days | 0.0 → 5.0 | 36 | -357.150 to 0.000 |
| B | strategic_production_days | 0.0 → 10.0 | 36 | -357.150 to 0.000 |
| B | strategic_production_days | 5.0 → 10.0 | 36 | 0.000 to 0.000 |
| C | strategic_production_days | 0.0 → 10.0 | 128 | -341.820 to 0.000 |
| B | release_fraction_per_day | 0.0 → 0.01 | 36 | -92.397 to 0.000 |
| B | release_fraction_per_day | 0.0 → 0.05 | 36 | -357.150 to 0.000 |
| B | release_fraction_per_day | 0.01 → 0.05 | 36 | -264.754 to 0.000 |
| C | release_fraction_per_day | 0.0 → 0.05 | 128 | -341.820 to 0.000 |
| B | release_delay_days | 0 → 14 | 54 | 0.000 to 50.400 |
| C | release_delay_days | 0 → 14 | 128 | 0.000 to 50.400 |
| B | release_ramp_days | 1 → 7 | 54 | 0.000 to 15.330 |

## Interpretation and limits

- The maximum unbuffered loss equals **4.458968 production-days**. The smallest positive commercial level is 7 days and strategic level is 5 days. No positive stock exhausts anywhere in this run. Thus commercial 7→35 and strategic 5→10 changes are inert; this grid cannot identify a depletion threshold or validate usable inventory mappings.
- In block B, commercial 0→7 days reduces cumulative shortage by 4.726–361.877 million barrels while leaving the market gap and price proxy unchanged. Strategic 0→5 days can reduce shortage by up to 357.150 million barrels, conditional on release rate and timing; adding stock with zero release has no effect.
- A release delay of 0→14 days adds up to 50.400 million barrels of shortage; a slower ramp of 1→7 days adds up to 15.330 million barrels in block B. These are modeled timing effects under selected assumptions, not empirically estimated emergency-release performance.
- In block A, rerouting 0→0.75 reduces cumulative shortage by up to 243.037 million barrels. Raising severity 0.25→1 adds up to 271.407 million barrels; duration 7→90 adds up to 298.800 million barrels. Zero effects in some pairs reflect zero allocation, inactive release or sufficient buffers, not universal insensitivity.
- Analyst choices remain unresolved inputs: exposure allocation, usable stocks, deliverability, future severity/duration/recovery and rerouting. This run does not supply new public evidence for them. Route references are never added together; Panama remains excluded. The frozen grid is not extended or tuned after seeing results.
- Share with caveats as an engineering sensitivity readout only. Next decisions should concern whether a separately versioned study is needed around depletion thresholds and response timing; do not revise this frozen grid or promote it into calibration.

## Reproducibility and validation

The 13 harness tests passed immediately before execution. The postprocessor checks every saved daily balance and stock transition, every summary metric against the saved daily rows, all duplicate parameter results, coverage, output hashes and frozen-input provenance. It does not import the harness summary routine. An independent geometric-series check reproduces the maximum: 3.6 × [90 + (1 − exp(−ln(20) × 90/30)) / (1 − exp(−ln(20)/30))] = 361.87650286556914 million barrels. This verifies arithmetic, not economic realism.

Use fresh output directories; the commands refuse overwrites:

```text
python -m unittest discover -s tests -p test_sensitivity.py -v
python -m diagnostics.sensitivity --execute --output outputs/sensitivity-run
python -m diagnostics.sensitivity_report --run outputs/sensitivity-run --output outputs/sensitivity-analysis
```

The local delivery package contains the full daily grid, summaries, all ranges and ties, matched comparisons, inputs, source code and manifests. Large generated outputs are intentionally not committed to Git. The compact repository receipt records their hashes; no numerical business-loss or historical replay claim follows from these files.

The final local repository suite passed all 62 tests (28.689 seconds), including five reporting tests; the deterministic production smoke also passed. No new full baseline-equivalence run was performed.
