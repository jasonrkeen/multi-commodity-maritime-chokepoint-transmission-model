# GitHub readiness audit — v0.6.0

Audit date: 2026-08-21

## Outcome

The v0.6.0 source tree is suitable for public review as a focused feature branch. It adds source-country enabling availability for reassigned heavy-sour barrels while preserving neutral defaults and the existing deterministic baseline. Third-party packet schemas, signal taxonomies, correspondence, and derived private diagnostics are excluded.

## Completed controls

| Area | Control | Status |
| --- | --- | --- |
| Reproducibility | Curated model inputs, tests, requirements, and run commands included | Pass |
| Continuous integration | Python 3.11–3.14 matrix, minimum-dependency job, and deterministic smoke run | Pass |
| Licensing | MIT license and copyright attribution | Pass |
| Citation | `CITATION.cff` with author, version, release date, and keywords | Pass |
| Contribution governance | Contribution guide, issue forms, and pull-request template | Pass |
| Security | Private reporting policy and sensitive-content rules | Pass |
| Dependency maintenance | Monthly Python and GitHub Actions update checks | Pass |
| Repository hygiene | Environments, secrets, outputs, caches, editor files, and build artifacts ignored | Pass |
| Sensitive-content scan | No third-party packet schema, taxonomy, correspondence, or derived diagnostic included | Pass |
| Large-file scan | No file larger than 5 MB in the release tree | Pass |
| Baseline preservation | Availability factors default to `1.0`; existing scenario outputs remain unchanged | Pass |
| Model regression | All 26 unit tests passed | Pass |
| Runtime smoke test | 30-day deterministic sensor-fusion scenario completed | Pass |

## Deliberately excluded

- Generated CSV, JSON, PDF, and PNG run outputs
- Raw or licensed source datasets
- Private correspondence and practitioner identities
- Third-party packet schemas, signal taxonomies, packet-derived fixtures, and transformed diagnostics
- Operational sensor feeds and non-public vessel tracks
- Credentials, local environments, caches, and temporary renders

## Actions before release

1. Open a focused v0.6.0 feature pull request.
2. Require the full CI matrix and minimum-dependency job to pass.
3. Review the USGS and Reuters source-register additions.
4. Confirm the pull-request diff contains no third-party packet schema, signal taxonomy, correspondence, or derived diagnostic.
5. Tag the merged, validated commit as `v0.6.0` only after explicit release approval.
