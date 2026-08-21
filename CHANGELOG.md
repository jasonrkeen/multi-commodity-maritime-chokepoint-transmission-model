# Changelog

All notable changes are documented here. The project follows semantic versioning while it remains pre-1.0.

## [Unreleased]

## [0.6.0] - 2026-08-21

### Added

- An upstream × electric-grid × terminal enabling-availability chain for reassigned heavy-sour barrels.
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
