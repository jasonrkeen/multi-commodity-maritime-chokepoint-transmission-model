# Contributing

Contributions that improve transparency, reproducibility, validation, or physical-market realism are welcome.

## Development setup

1. Create and activate a virtual environment.
2. Install dependencies with `python -m pip install -r requirements.txt`.
3. Run `python -m unittest discover -s tests -v` before opening a pull request.
4. Run a deterministic smoke test with `python main.py --scenario sensor_fused_hormuz --days 30 --simulations 0`.

## Pull requests

- Keep each pull request focused on one model, data-governance, or documentation concern.
- Explain the physical or economic mechanism affected and identify any changed assumptions.
- Add or update tests when behavior changes.
- Update `CHANGELOG.md` for user-visible changes.
- Do not commit generated outputs, raw licensed data, credentials, private correspondence, or operational sensor feeds.
- Cite public evidence in `data/input/source_register.csv`; label analyst assumptions explicitly.

Model outputs should not be tuned to force agreement with comparator bands. Calibration diagnostics must remain non-driving unless a methodology change is proposed and reviewed transparently.
