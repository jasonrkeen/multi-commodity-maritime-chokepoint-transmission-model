# Standalone sensitivity harness for design 0.8

The standard-library-only `diagnostics.sensitivity` module implements the frozen 0.8 equations without importing or changing the production model. This is engineering implementation and fixture testing, not historical validation or calibration. The full 689-case study has not been executed as part of this implementation.

## Verification and future execution

From the repository root:

```text
python -m unittest discover -s tests -p test_sensitivity.py -v
python -m diagnostics.sensitivity --output outputs/sensitivity-input-check
```

The default command verifies the original design and replay manifests against independent SHA-256 pins in the harness, verifies every listed frozen file, validates all 689 cases, and records case/source/runtime fingerprints. It does not simulate cases. Use a new output directory each time; existing directories are rejected. Paths to frozen inputs resolve relative to the repository, independent of the calling directory; output paths resolve relative to the calling directory.

After the test gate passes, a future explicit execution is available with:

```text
python -m diagnostics.sensitivity --execute --output outputs/sensitivity-run
```

This produces daily CSV, per-case/horizon JSON summaries, and a run manifest. JSON preserves null depletion days; stock depletion is measured at the end of each zero-based day, with initially empty stocks separately flagged. Cumulative draws are in reference-production days; cumulative shortage is in million barrels. Price columns are optional in the scientific design but are always emitted by this harness as an illustrative, uncalibrated proxy.

An execution starts with `INCOMPLETE` status and is marked complete only after all cases, summaries and output hashes are written. On error, leave the partial directory for diagnosis and use a fresh directory for a retry. Never present incomplete files as a successful study. The manifest records the harness canonical-text hash, case hashes, both original manifest pins, Python version, platform and interpreter executable hash. It does not certify an independently audited runtime or economic validity. The unchanged input design remains labeled not-run; any future run status belongs only in its separate output manifest.

## Engineering tests and claim boundary

Fixtures cover hand-calculated shortage/draw accounting to 1e-10, daily conservation, stock budgets and nonnegativity, release delay/ramp and exhaustion, recovery/abrupt-end and rerouting boundaries, zero exposure/reserves, unchanged price under commercial-stock changes, duplicate-case equality, deterministic repetition, summary horizons/depletion/cap behavior, invalid and nonfinite inputs, tamper rejection, default no-execution behavior, overwrite refusal, and complete/incomplete writer states. Writer tests run a three-day fixture, not the study.

All 689 input rows are loaded and validated, but tests simulate only engineering fixtures and a duplicate pair. Test success is not a sensitivity result, baseline equivalence, evidence for analyst bounds, or permission to change the 38 frozen blocked replay decisions. No fixed input, production-model code or production data is changed.

The harness supplies daily and per-case outputs. Full-grid block-range/endpoint and matched-factor reporting remains a downstream analysis step after a separately identified study run. Do not infer expected values, confidence intervals, calibrated probabilities, historical forecasts or business impacts from these outputs. Preserve all interpretation limits in the frozen specification.

## Implementation validation

Local validation on October 22, 2026 passed all 57 repository tests (13 new diagnostic tests; 29.585 seconds) and the existing deterministic 30-day production smoke test. The verification-only CLI successfully checked both frozen manifests and all 689 design rows. These checks left all 38 historical replay decisions unchanged. CI independently runs the complete suite and smoke test across its five environments. The writer fixture's executed status applies only to its temporary three-day test, not the full study.
