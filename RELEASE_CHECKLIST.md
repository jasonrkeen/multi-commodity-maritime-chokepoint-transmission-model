# Release checklist

## Model and tests

- [ ] Confirm the package version, changelog version, and citation version agree.
- [ ] Run `python -m unittest discover -s tests -v`.
- [ ] Run the documented sensor and compound scenarios with a fixed seed.
- [ ] Review all changed assumptions and source-register entries.
- [ ] Confirm calibration remains diagnostic and does not overwrite baseline inputs.

## Repository hygiene

- [ ] Confirm generated outputs, temporary files, environments, and editor settings are ignored.
- [ ] Scan tracked content for credentials, tokens, private correspondence, and non-public data.
- [ ] Confirm every distributable input is public, synthetic, or clearly labeled as an analyst assumption.
- [ ] Review the diff for accidental large or binary files.

## GitHub release

- [ ] Require CI to pass on the release commit.
- [ ] Tag the release as `v0.5.0`.
- [ ] Use the corresponding changelog section as release notes.
- [ ] Attach only deliberate release artifacts.
- [ ] Verify the repository description and topics describe the model as research software, not a forecast service.
