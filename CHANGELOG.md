# Changelog

All notable changes are documented here. The project follows semantic versioning while it remains pre-1.0.

## [Unreleased]

- Implement separate 0.9 trajectory and reporting modules with input provenance,
  raw/tolerance event flags, complete boundary/pair outputs and fixture tests.
  Verify actual inputs without running the study; preserve all prior freezes.

- Implement separate 0.9 input loading, threshold materialization and contrast
  classification with boundary-identity tests. Hash all 3,997 starting inputs;
  do not run the study or change completed 0.8 outputs and replay decisions.

- Specify separate depletion/timing study 0.9 with 3,997 fixed and threshold-scaled
  cases, explicit contrast rules and an execution gate. Preserve completed 0.8
  results and all frozen historical replay decisions; do not execute the new study.

- Execute the unchanged 689-case hypothetical study; report ranges, endpoint
  cases and 3,076 matched-factor pairs with independent output reconciliation.
  No positive stock exhausts in this grid; no calibration or replay eligibility changes.

- Implement an isolated standard-library sensitivity harness with frozen-file
  verification, provenance, stock-accounting fixtures and fail-closed output status.
  Preserve the original study design and all historical replay decisions.

- Investigate the Panama schedule discrepancy with two digest-verified later
  archive witnesses; specify and hash 689 hypothetical sensitivity cases.
  No sensitivity execution or changes to frozen historical replay decisions.

- Assess 12 public-data gaps; authenticate four additional archive payloads,
  identify Panama November7 schedule conflict, and preserve all frozen replay blocks.


- Freeze historical construction rules and 38 blocked replay decisions in 0.6;
  recover digest-verified EI/EIA/DOE archive witnesses. Global usable stocks and
  other execution gates remain unresolved; no fitting or runtime changes.


- Specify unconditional background calendar comparators (16 origins, 32 windows),
  retaining prior strict exclusions as diagnostics; all executions remain NOT_RUN.
- Recover matched 2022 crude/condensate exposure candidates and dated US SPR
  physical constraints, with explicit source-custody and publication-date gaps.

- Adopt a uniform two-day publication lag and explicit ALFRED baseline channel;
  audit nine prices and 27 stock selections, including two earlier weekly releases.
- Document equation-compatible exposure/inventory mappings and reject regional,
  commodity and canal/pipeline substitutions lacking evidence.
- Fix the quarterly 2021-2024 control universe before expanded screening; all
  32 windows fail the broad incident/restriction rule, including maintenance.
  No replay bundles or numerical global buffer mappings are approved.

- Recover dated Brent vintages and regional exposure/inventory facts; complete
  the existing control exclusions under an explicit incident-free draft rule.
  At that revision global mappings and publication-cutoff policy were unapproved;
  see the subsequent policy 0.4 decisions above.

- Populate a retrospective event/control feasibility inventory and per-origin
  input-availability audit; all replay cases remain unaccepted pending input recovery.

- Clarify the IBIF sensor field as an experimental upstream diagnostic with
  source-pairing, interpolation and coverage limits; numerical behavior is unchanged.
- Add a draft public-market calibration specification, event-ledger template and
  source-backed feasibility assessment. No fitting or empirical validation claimed.
- Review fixes (replacement-0.1.1): withhold sensor proxies without confirmed
  scenario sensor-row availability; reject inventory-sum overflow and imprecise weight sums.
- Add a source-only, fail-closed three-way equivalence runner and regression tests.

- Add an opt-in `--ibif` reporting layer labeled `replacement-0.1.0`.
  This is a new implementation, not the unrecovered historical IBIF v0.2.
  Per-commodity heuristic scores, source limitations, sensitivity comparisons,
  and collection gaps are exported as JSON, CSV and Markdown after existing
  model work completes. No operational thresholds or analytic-confidence
  claims are supplied. See `docs/ibif_replacement.md`.

## [0.6.0] - 2026-08-21

### Added

- An upstream Ã— electric-grid Ã— terminal enabling-availability chain for reassigned heavy-sour barrels.
- Daily and summary fields separating nominal reassignment, enabling availability, and effective reassignment.
- Public USGS and Reuters source-register entries supporting the source-country infrastructure-fragility mechanism.
- Two regression tests covering the availability chain and backward-compatible input defaults, bringing the suite to 26 tests.

### Changed

- Widened supported pandas versions to include the tested 3.x series while retaining pandas 2.1 compatibility.
- Added a Python 3.11 CI job that exercises the declared minimum NumPy, pandas, and Matplotlib versions.
- Configured Dependabot to preserve compatible dependency ranges and widen them only when necessary.
- Legacy v0.5 crude-market structure files default missing availability fields to the neutral value `1.0`.

### Governance

- The availability factors are explicit analyst assumptions and default to a neutral baseline.
- Effective reassignment affects only the regional grade gap and is never counted as new global supply.
- No third-party practitioner packet, packet schema, signal taxonomy, correspondence, or packet-derived diagnostic is included in the public release.

## [0.5.0] - 2026-08-12

### Added

- A regional medium/heavy-sour crude proxy with explicit grade-compatibility and logistics basis.
- Segmented purchasing channels that distinguish true demand response from apparent benchmark-market withdrawal.
- Conservation treatment for reassigned heavy-sour barrels: regional relief without new global supply.
- Sensor confidence fields for detection recall, identity resolution, AIS staleness, and validation maturity.
- A separate conditional ecological scenario with desalination, fisheries/coastal-livelihood, and remediation paths.
- Crude-segmentation and ecological charts, two ecological output tables, and two new executive-brief pages when applicable.
- Five regression tests for the new mechanisms, bringing the suite to 24 tests.

### Governance

- Private practitioner discussion informs hypotheses only; no private claims are presented as public evidence.
- Crude segmentation and ecological values are explicitly labeled analyst assumptions pending public calibration.
- Ecological exposure is excluded from core commodity totals and activates only in the named conditional branch.

## [0.4.1] - 2026-08-11

### Added

- GitHub Actions CI across Python 3.11, 3.12, 3.13, and 3.14.
- MIT license, citation metadata, contribution guidance, security policy, and release checklist.
- Repository-level secret and generated-output exclusions.

### Changed

- Public distribution is source-first: generated scenario outputs, temporary renders, caches, and local environments are excluded.
- Documentation now distinguishes reproducible model configuration from private or raw source material.

### Model integrity

- No equations, baseline assumptions, scenario probabilities, or calibrated outputs changed from 0.4.0.
- The 19-test model suite remains the release gate.

## [0.4.0] - 2026-08-11

### Added

- Explicit pipeline bypass, emergency stock releases, and external supply response.
- Strategic-stock depletion accounting and structural-supply counterfactuals.
- Brent price-contribution decomposition and market-balance reporting.

## [0.3.0] - 2026-08-11

### Added

- Diagnostic calibration sensitivity, scenario comparison, and Brent target-band coverage.

## [0.2.0] - 2026-08-10

### Added

- Dynamic demand, chokepoint dependency transmission, sensor fusion, fertilizer seasonality, and helium reserve treatment.
