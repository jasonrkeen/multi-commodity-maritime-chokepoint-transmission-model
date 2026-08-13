## Purpose

Describe the model, data-governance, validation, or documentation problem addressed.

## Mechanism and assumptions

Identify the physical or economic mechanism affected. List changed assumptions and distinguish public evidence from analyst judgment.

## Validation

- [ ] `python -m unittest discover -s tests -v` passes.
- [ ] A deterministic smoke scenario passes.
- [ ] New or changed behavior has test coverage.
- [ ] `CHANGELOG.md` is updated when the change is user-visible.
- [ ] No generated outputs, credentials, private correspondence, restricted data, or operational sensor feeds are included.

## Result interpretation

Explain any material change to exposure, price, inventory, demand, dependency, or lagged-impact outputs. Comparator bands must remain diagnostic unless the methodology change is explicit.
