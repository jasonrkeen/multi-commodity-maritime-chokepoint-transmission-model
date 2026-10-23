# Executed 0.9 depletion and release-timing study

**HYPOTHETICAL_0_9_EXECUTED_NOT_CALIBRATED.** All 3,997 frozen cases ran from clean commit `fda33bf216cc17d6787c0d3d121c197c190d284f`, using the previously hashed starting inputs: 719,460 daily rows and 11,991 horizon summaries. All parameter combinations are unique. The completed 0.8 outputs and package, original designs and 38 blocked historical replay decisions remain unchanged.

This outcome-informed follow-up describes one severe Suez/SUMED reference path: allocation/severity 1, 90-day disruption, 30-day recovery to 5%, no rerouting or replenishment. Stocks are reference-production days at 81.157 million barrels/day, not global demand coverage or verified usable inventories. No probability, calibration, business-loss, confidence-interval or historical-replay claim follows.

## Depletion thresholds

The 180-day gross gap G is **4.458968 production-days** (361.876503 million barrels). Unconstrained cumulative strategic release R ranges from **0.389500 to 4.400732 days** across the 36 rate/delay/ramp settings. For initial strategic stock S, the conditional commercial requirement is **C*(S)=G−min(S,R)**. With no strategic stock, C*=4.458968; with S at least R, C* ranges from **0.058236 to 4.069468**. These are algebraic boundaries within the specified mechanism, not empirically estimated inventory targets.

Below each R is the strategic exhaustion boundary at 180 days. C* at S≥R is the best commercial requirement achievable under that release schedule even with additional strategic stock. Shorter-horizon boundaries and every fixed-stock grid point are in boundaries.json; starting stocks remain based on 180 days.

| Daily release fraction | Delay (days) | Ramp (days) | R (production-days) | C* if S≥R (production-days) |
|---:|---:|---:|---:|---:|
| 0.005 | 0 | 1 | 0.603913 | 3.855056 |
| 0.005 | 0 | 7 | 0.574263 | 3.884705 |
| 0.005 | 0 | 14 | 0.539317 | 3.919651 |
| 0.005 | 7 | 1 | 0.568913 | 3.890056 |
| 0.005 | 7 | 7 | 0.539263 | 3.919705 |
| 0.005 | 7 | 14 | 0.504333 | 3.954635 |
| 0.005 | 14 | 1 | 0.533913 | 3.925056 |
| 0.005 | 14 | 7 | 0.504263 | 3.954705 |
| 0.005 | 14 | 14 | 0.469359 | 3.989609 |
| 0.005 | 30 | 1 | 0.453913 | 4.005056 |
| 0.005 | 30 | 7 | 0.424264 | 4.034705 |
| 0.005 | 30 | 14 | 0.389500 | 4.069468 |
| 0.01 | 0 | 1 | 1.138494 | 3.320475 |
| 0.01 | 0 | 7 | 1.079194 | 3.379774 |
| 0.01 | 0 | 14 | 1.009334 | 3.449634 |
| 0.01 | 7 | 1 | 1.068494 | 3.390475 |
| 0.01 | 7 | 7 | 1.009195 | 3.449774 |
| 0.01 | 7 | 14 | 0.939386 | 3.519582 |
| 0.01 | 14 | 1 | 0.998494 | 3.460475 |
| 0.01 | 14 | 7 | 0.939195 | 3.519774 |
| 0.01 | 14 | 14 | 0.869472 | 3.589496 |
| 0.01 | 30 | 1 | 0.838494 | 3.620475 |
| 0.01 | 30 | 7 | 0.779196 | 3.679772 |
| 0.01 | 30 | 14 | 0.709938 | 3.749031 |
| 0.05 | 0 | 1 | 4.400732 | 0.058236 |
| 0.05 | 0 | 7 | 4.211837 | 0.247132 |
| 0.05 | 0 | 14 | 3.987784 | 0.471185 |
| 0.05 | 7 | 1 | 4.090223 | 0.368745 |
| 0.05 | 7 | 7 | 3.901327 | 0.557641 |
| 0.05 | 7 | 14 | 3.677275 | 0.781694 |
| 0.05 | 14 | 1 | 3.779714 | 0.679255 |
| 0.05 | 14 | 7 | 3.590818 | 0.868150 |
| 0.05 | 14 | 14 | 3.366765 | 1.092203 |
| 0.05 | 30 | 1 | 3.069978 | 1.388990 |
| 0.05 | 30 | 7 | 2.881083 | 1.577886 |
| 0.05 | 30 | 14 | 2.657030 | 1.801939 |

## Depletion versus shortage

Counts below use the frozen 1e-10 normalized-unit tolerance. Initially empty stocks are excluded from positive-stock depletion. These counts describe the chosen grid, not probabilities. Event days are zero-based.

| Block | Cases | Positive commercial depletion by day 179 | Positive strategic depletion by day 179 | Positive cumulative shortage |
|---|---:|---:|---:|---:|
| F | 2916 | 1565 | 990 | 1889 |
| T | 1080 | 540 | 648 | 540 |
| N | 1 | 0 | 0 | 0 |

In the fixed-stock block, positive commercial depletion occurs on days **5–108** among cases that deplete; strategic depletion occurs on days **6–136**. Nondepletion is retained as null, not assigned a late event day.

The threshold-scaled block directly distinguishes exhaustion from shortage: all **180 beta=1 cases** reach commercial depletion within tolerance but none has positive cumulative shortage within tolerance. Each of beta=0, 0.5 and 0.99 has 180 shortage cases; beta=1.01 and 1.5 have none. Beta=0 begins empty and is not counted as positive-stock depletion. Strategic alpha=0.5, 0.99 and 1 cases reach depletion within tolerance; alpha>1 retains release-limited stock.

Floating-point boundary residues matter for interpretation: T has **584 raw-positive** cumulative shortage flags but **540 tolerance-positive** flags. The additional 44 raw positives are below the frozen threshold. Unrounded values and both flag types are retained; no trajectory state was snapped to zero. Tiny reversed matched deltas (around 1e-13 million barrels) are arithmetic residue, not evidence that delaying release reduces loss.

## Sampled ranges and endpoint cases

| Block | Horizon | Shortage range (million barrels) | Min representative | Max representative | Max ties |
|---|---:|---:|---|---|---:|
| ALL | 30 | 0.000000 to 108.000000 | F0037 | F0001 | 153 |
| ALL | 90 | 0.000000 to 324.000000 | F0055 | F0001 | 36 |
| ALL | 180 | 0.000000 to 361.876503 | F0057 | F0001 | 36 |
| F | 30 | 0.000000 to 108.000000 | F0037 | F0001 | 108 |
| F | 90 | 0.000000 to 324.000000 | F0055 | F0001 | 36 |
| F | 180 | 0.000000 to 361.876503 | F0057 | F0001 | 36 |
| T | 30 | 0.000000 to 108.000000 | T0002 | T0271 | 45 |
| T | 90 | 0.000000 to 308.194657 | T0003 | T0331 | 1 |
| T | 180 | 0.000000 to 346.071160 | T0005 | T0331 | 1 |
| N | 30 | 0.000000 to 0.000000 | N0001 | N0001 | 1 |
| N | 90 | 0.000000 to 0.000000 | N0001 | N0001 | 1 |
| N | 180 | 0.000000 to 0.000000 | N0001 | N0001 | 1 |

All exact endpoint ties for every metric are in ranges.json; complete inputs are in cases.json. Representative 180-day shortage endpoints are:

| Case | Block | Commercial days | Strategic days | Release fraction/day | Delay | Ramp | Alpha | Beta |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| F0001 | F | 0.000000 | 0.000000 | 0.005 | 0 | 1 | None | None |
| F0057 | F | 4.000000 | 0.500000 | 0.005 | 0 | 1 | None | None |
| T0331 | T | 0.000000 | 0.194750 | 0.005 | 30 | 14 | 0.5 | 0.0 |
| T0005 | T | 4.198582 | 0.301956 | 0.005 | 0 | 1 | 0.5 | 1.01 |
| N0001 | N | 0.000000 | 0.000000 | 0.0 | 0 | 7 | None | None |

F0001 is one of 36 overall maximum cases with no commercial or strategic stock, yielding 361.876503 million barrels of shortage. The null case has zero exposure; other zero-shortage endpoints have exposed flows but sufficient modeled buffers. Do not conflate these mechanisms.

## Release-timing and capacity comparisons

**42,174 matched pairs** were evaluated at three horizons (**126,522 pair-horizon records**). Fixed-stock comparisons hold every other physical input equal. The table gives all F-block release-factor comparisons at 180 days: higher-level minus lower-level cumulative shortage, in million barrels. Display-only rounding maps tiny signed residues to zero; raw values remain in the files.

| Factor | Lower → higher | Pairs | Minimum change | Maximum change |
|---|---|---:|---:|---:|
| release_fraction_per_day | 0.005 → 0.01 | 972 | -43.384972 | 0.000000 |
| release_fraction_per_day | 0.005 → 0.05 | 972 | -308.138473 | 0.000000 |
| release_fraction_per_day | 0.01 → 0.05 | 972 | -264.753501 | 0.000000 |
| release_delay_days | 0 → 7 | 729 | 0.000000 | 25.200000 |
| release_delay_days | 0 → 14 | 729 | 0.000000 | 50.400000 |
| release_delay_days | 0 → 30 | 729 | 0.000000 | 108.000000 |
| release_delay_days | 7 → 14 | 729 | 0.000000 | 25.200000 |
| release_delay_days | 7 → 30 | 729 | 0.000000 | 82.800000 |
| release_delay_days | 14 → 30 | 729 | 0.000000 | 57.600000 |
| release_ramp_days | 1 → 7 | 972 | 0.000000 | 15.330218 |
| release_ramp_days | 1 → 14 | 972 | 0.000000 | 33.513665 |
| release_ramp_days | 7 → 14 | 972 | 0.000000 | 18.183447 |

Concrete endpoint comparisons, with identical remaining physical inputs:

- **F1952→F2681:** delay 0→30 days adds **108.000000 million barrels** (4.726270→112.726270). Both have C=0, S=4.5 days, release fraction 0.05/day and ramp 1.
- **F2195→F2357:** ramp 1→14 days adds **33.513665 million barrels** (29.926270→63.439935). Both have C=0, S=4.5, release fraction 0.05/day and delay 7.
- **F0008→F1952:** release fraction 0.005→0.05/day reduces shortage by **308.138473 million barrels** (312.864743→4.726270). Both have C=0, S=4.5, delay 0 and ramp 1.

## Stock and normalized comparisons

Fixed commercial stocks 4→4.5 days reduce shortage by up to **37.248503 million barrels**; strategic stocks 4→4.5 reduce it by up to **32.522233 million barrels**, depending on release timing and commercial stock. Commercial 0→5 reduces shortage by 4.726270–361.876503 million barrels across the matched F cases. Strategic 0→5 reduces shortage by up to 357.150233 million barrels; it can be inert when commercial stocks already cover the gap.

T beta changes hold strategic stock and timing fixed, so they are commercial-stock-only contrasts. Beta 0.99→1 reduces shortage by **0.047263–3.460712 million barrels** across 180 matched pairs; beta 1→1.01 adds no shortage reduction beyond numerical residue. This confirms the algebraic boundary under this mechanism, not calibration against observations.

T alpha changes and T timing changes are **normalized multi-input contrasts**: materialized stock amounts change together. For example, alpha 0.99→1 changes shortage by about −3.571502 to 0 million barrels across 216 pairs, but cannot be interpreted as an isolated strategic-inventory effect because C=beta C*(S) changes as well. Alpha 1→1.01 has no further shortage benefit beyond numerical residue once the release requirement is covered. All pair labels, held-fixed design fields and flag transitions are retained in matched_pairs.jsonl.

## Validation, preservation and claim boundary

The 12 runner/reporting tests passed immediately before execution. The clean execution commit and source/runtime/input hashes are in run_manifest.json. Reporting checked every saved daily equation and stock balance, reconstructed all summary metrics/flags, and retained coverage and hash checks. A separate audit recomputed all 11,991 cumulative threshold identities using direct exponential/power expressions and checked all 126,522 matched records, including held-fixed inputs, labels and arithmetic. This establishes engineering consistency within the specified model, not independent economic validation.

No bounds, stock multipliers, equations or replay eligibility decisions were changed after viewing results. The original design/materialization documents retain historical status labels; this separate receipt records actual execution. Raw large outputs remain outside Git. The delivery package contains the full grid, summaries, boundary points, all endpoint ties and all comparisons, plus reproducible source and manifests.

The fixed path, aggregate reference-production stocks, analyst release capacities, no-replenishment assumption and simplified market mechanism remain material limitations. Stock adequacy under this path does not establish real operational adequacy. Commercial stock has no effect on the illustrative price proxy by construction; no business-loss or calibrated price claim is supported. All 38 historical windows remain blocked, and PR #6 remains draft and unmerged.

Final local verification passed all 89 repository tests (89.472 seconds) and the deterministic production smoke. No new full baseline-equivalence protocol was run.
