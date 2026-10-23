# Separate 0.9 trajectory runner and reporting layer

Implementation-phase status: **IMPLEMENTED_AND_FIXTURE_TESTED_STUDY_NOT_EXECUTED**. That phase used small temporary engineering runs only. The subsequent authorized full run is recorded separately in [executed 0.9 results](ibif_depletion_results_0_9.md). Completed 0.8 study files, the original 0.9 design and materialized inputs, and historical replay decisions remain unchanged.

## Input verification and execution boundary

`diagnostics.depletion_runner` validates the saved materialization manifest against an independently pinned receipt, checks source and input hashes, and compares every saved input with deterministic materialization of the frozen design. Verification is the default and does not simulate any cases:

```text
python -m unittest discover -s tests -p test_depletion_runner.py -v
python -m diagnostics.depletion_runner --inputs outputs/depletion-inputs --output outputs/depletion-verification
```

Use the existing saved input directory and a new output directory. The original local directory is `outputs/depletion-0.9-inputs-v1` in the parent workspace, outside the repository; supply its path explicitly. Never silently regenerate inputs after a mismatch. Numerical recomputation is exact against the saved inputs; a platform difference that changes starting values fails verification rather than selecting a new input table.

A later authorized full run would add `--execute` and use another new output directory. This implementation turn does not invoke that option on the frozen study. A future run must use the committed, tested source and record its hashes/runtime. The manifest records Git HEAD and whether the worktree was dirty separately, so an uncommitted source hash cannot be mistaken for the contents of HEAD.

The runner uses the unchanged 0.8 equation functions through a separate internal case conversion; it preserves real F/T/N block labels in summaries. It does not modify the production model. Inputs are copied into each run directory and hashed. It writes daily CSV and horizon summaries, checks daily equations/stock balances, validates cumulative threshold identities and duplicate agreement, and only then marks a run complete. Failures retain INCOMPLETE status; existing output directories are rejected.

## Reporting contract

The reporting command requires a completed 0.9 run with matching source/input/output hashes:

```text
python -m diagnostics.depletion_report --run outputs/depletion-run --output outputs/depletion-report
```

It audits one case's saved daily rows at a time, checking equations independently of the trajectory loop and recomputing summaries and flags with the summary implementation. It rejects missing/extra cases or days, altered outputs, source mismatches, incorrect summaries and incomplete runs. It creates:

- `REPORT.md`: plain-language sampled ranges and endpoint representatives, with limitations.
- `ranges.json`: all block/horizon metric extrema and exact tied case IDs, null counts and boolean flag counts.
- `cases.json`: complete original and physical materialized inputs.
- `boundaries.json`: every grid point, timing setting and conditional boundary C_H(S), at each horizon, retaining 180-day starting stocks.
- `matched_pairs.jsonl`: all permitted pairs, all held-fixed design fields, endpoint IDs, deltas and flag transitions.
- `matched_ranges.json`: delta extrema, representative endpoint pairs and tie counts; every tied pair remains recoverable from the complete JSONL.
- `report_manifest.json`: completion status, lineage and output hashes.

F comparisons and T beta comparisons are single-physical-factor; T alpha/timing comparisons are normalized multi-input contrasts. No cross-block matching, probabilities, case weighting or confidence intervals are introduced. Null event days stay null; their differences are not silently changed to zero. Duplicate cases are retained, not treated as independent observations.

Initially empty stock is distinct from subsequent positive-stock depletion. Raw and 1e-10 tolerance event flags remain separate. Equality depletion need not cause shortage. A cumulative shortage may exceed tolerance even when each daily shortage is below tolerance; cumulative positivity and daily shortage counts deliberately measure different quantities. Values are not snapped to thresholds.

## Engineering validation and limits

Fixtures cover saved-input/receipt tampering, the default no-execution behavior, no-overwrite protection, daily equations and cumulative identities, initially empty stocks, equality depletion, tolerance flags, duplicate agreement, complete and failed runner/report states, all reporting outputs and contrast labels, and altered summaries even after their hashes are recomputed. Fixture end-to-end runs contain five cases, not the frozen 3,997-case study. The real CLI was used in verification-only mode against all saved inputs.

The reporting layer is implementation-tested, not validated against real commodity outcomes. It introduces no new baseline-equivalence, calibration, inventory-adequacy or historical-replay claim. Full execution and inspection of the actual study report remain separate work.

Local validation passed all 89 repository tests (12 new runner/reporting tests; 38.267 seconds) and the deterministic production smoke. The completed 0.8 daily/summary outputs and ZIP hashes, saved 0.9 input hash, frozen design and prior replay files were checked unchanged. No full 0.9 daily or summary output was produced.
