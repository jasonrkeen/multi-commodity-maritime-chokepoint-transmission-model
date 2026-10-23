# 0.9 loader and threshold calculations

Status: **INPUTS_MATERIALIZED_STUDY_NOT_EXECUTED**. The separate `diagnostics.depletion_inputs` module loads and validates the frozen 3,997-case design and calculates starting stocks from its fixed threshold formulas. It contains no study trajectory runner and does not modify the 0.8 harness or results.

The default command verifies the independent 0.9 manifest pin, all design files, all 21 preserved prior-file hashes, exact schema, unique IDs, block counts and nullable-field meanings. Empty T-block stock cells remain null in the frozen design. They become numerical physical stocks only in the separately written materialized-input file; multipliers are never treated as stock days.

```text
python -m diagnostics.depletion_inputs
python -m unittest discover -s tests -p test_depletion_inputs.py -v
python -m diagnostics.depletion_inputs --materialize-output outputs/depletion-inputs
```

Use a new output directory. A materialization starts with an INCOMPLETE manifest and writes INPUTS_MATERIALIZED_STUDY_NOT_EXECUTED only after all inputs are written and hashed. It records source, frozen-design and interpreter hashes plus Python/platform details. Existing directories, partial input sets, duplicate identities and wrong block counts are rejected. This operation forms only exogenous gross-gap/requested-release paths and starting inputs; it does not generate the 719,460 study trajectory rows or estimate depletion outcomes for the study.

Each materialized record retains the complete original design row and separately stores physical commercial/strategic stocks and the fixed 180-day materialization horizon. Thirty- and ninety-day boundary diagnostics reuse those starting stocks. Raw margins and exact equality flags remain separate from the specified 1e-10 classification tolerance; no state values are snapped or clipped.

The calculation uses R_H=sum(min(G(t),A(t))) and C_H(S)=sum(G(t))-min(S,R_H), with S=alpha R_180 and C=beta C_180(S) for T rows. A zero R_180 or C_180(S) stops T materialization. Numeric inputs must be finite and nonnegative, bounded fractions must be within [0,1], and timing values must be valid integers. Release remains zero on the delay day. Rerouting stays fixed at zero.

The contrast classifier enforces within-block single-design-factor comparisons. F comparisons and T beta comparisons are labeled single-physical-factor. T alpha and timing comparisons are labeled normalized-multi-input because physical starting stocks can change together. Identical, cross-block and multi-design-factor pairs are rejected.

Tests include all-row materialization, frozen-file tampering, hand-calculated release timing, an independent geometric gross-gap sum, and cumulative identities checked against nine small engineering fixtures using the unchanged 0.8 equation implementation. Fixtures bracket both thresholds at 0.99, 1 and 1.01; they cover equality depletion without shortage, exhaustion before a later shortage, release-limited unused stock, initially empty/null cases, duplicate inputs, shorter-horizon preservation, nonfinite/invalid inputs, overwrite refusal and incomplete-write status. These fixtures are engineering checks, not execution of the 0.9 study or validation of its economic assumptions.

The local materialization completed all 3,997 input records. Its compact receipt is `calibration_inventory/depletion_materialization_receipt_0_9.json`; the full generated input table remains outside Git. The completed 0.8 output hashes and delivery ZIP were checked unchanged, and all 38 historical replay decisions remain frozen.

Local validation passed all 77 repository tests (15 new loader/threshold tests; 38.019 seconds) and the deterministic production smoke. A separate calculation using ordinary sums and direct exponential/power expressions matched all saved starting-stock values within 1e-10, covering all 36 timing settings. The input table is not a study result, and no new baseline-equivalence or calibration claim follows from these engineering checks.

Remaining before a study run: implement and test a separate 0.9 trajectory runner and reporting layer, verify the saved input hash on load, retain initially-empty versus positive-stock-depletion and raw/tolerance shortage flags, and pin the runner commit/runtime and test evidence. No study execution is performed or implied by this input-preparation phase. The frozen original specification retains its original not-materialized status as historical metadata.
