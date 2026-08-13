# GitHub readiness audit — v0.5.0

Audit date: 2026-08-12

## Outcome

The v0.5.0 source tree is ready to initialize and publish as a public GitHub repository. This feature release adds crude-market segmentation, confidence-weighted undeclared activity, and a conditional ecological branch while preserving source-only public packaging.

## Completed controls

| Area | Control | Status |
| --- | --- | --- |
| Reproducibility | Curated model inputs, tests, requirements, and run commands included | Pass |
| Continuous integration | Unit-test matrix for Python 3.11–3.14 plus deterministic smoke run | Pass |
| Licensing | MIT license and copyright attribution | Pass |
| Citation | `CITATION.cff` with author, version, release date, and keywords | Pass |
| Contribution governance | Contribution guide, issue forms, and pull-request template | Pass |
| Security | Private reporting policy and sensitive-content rules | Pass |
| Dependency maintenance | Monthly Python and GitHub Actions update checks | Pass |
| Repository hygiene | Environments, secrets, outputs, caches, editor files, and build artifacts ignored | Pass |
| Sensitive-content scan | No credential patterns or named private correspondence found | Pass |
| Large-file scan | No file larger than 5 MB in the release tree | Pass |
| Model regression | All 24 unit tests passed | Pass |
| Runtime smoke test | 30-day deterministic sensor-fusion scenario completed | Pass |

## Deliberately excluded

- Generated CSV, JSON, PDF, and PNG run outputs
- Raw or licensed source datasets
- Private correspondence and practitioner identities
- Operational sensor feeds and non-public vessel tracks
- Credentials, local environments, caches, and temporary renders

## Actions after repository creation

1. Set the default branch to `main`.
2. Enable GitHub Actions and Dependabot alerts.
3. Enable private vulnerability reporting.
4. Protect `main` and require the CI workflow before merge.
5. Add the repository URL to `CITATION.cff` after the final URL exists.
6. Tag the validated commit as `v0.5.0` and publish the changelog section as the release notes.
