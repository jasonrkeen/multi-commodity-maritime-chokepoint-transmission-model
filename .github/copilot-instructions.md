# Copilot instructions: Multi-Commodity Maritime Chokepoint Transmission Model

## Purpose
OSINT-informed model of immediate and lagged economic transmission from maritime chokepoint disruptions across crude oil, LNG, fertilizer, and helium.

## Tech stack
- Python; dependencies in `requirements.txt`
- Key libraries: `numpy`, `pandas`, `matplotlib`

## Folder structure
- `.github/` (5 files)
- `data/` (12 files)
- `docs/` (2 files)
- `maritime_chokepoint/` (7 files)
- `tests/` (1 files)
- `.gitattributes`
- `CHANGELOG.md`
- `CITATION.cff`
- `CONTRIBUTING.md`
- `README.md`
- `RELEASE_CHECKLIST.md`
- `SECURITY.md`
- `main.py`
- `requirements.txt`

## Setup, run, test
Commands documented in README.md (referenced files exist):
```bash
python -m venv .venv
pip install -r requirements.txt
python main.py --scenario compound_hormuz_red_sea --days 240 --simulations 200
python main.py --scenario sensor_fused_hormuz --days 240 --simulations 200
python main.py --scenario sensor_fused_hormuz --days 240 --simulations 200 --seed 20260811 --compare-scenarios --calibration
python main.py --scenario compound_hormuz_red_sea_ecological --days 240 --simulations 200 --seed 20260812
python main.py --scenario compound_hormuz_red_sea --days 240 --simulations 0 --calibration --calibration-levels 0.9 1.0 1.1
python main.py --scenario hormuz_30d_severe --days 240 --simulations 0
python -m unittest discover -s tests -v
```
- Tests: 1 Python test file(s) under `tests/`; framework appears to be unittest. Add/update tests with any logic change.
- CI workflows exist in `.github/workflows/`; keep them passing.

## Conventions observed
- Functions use type hints; keep annotating new code.
- Uses `dataclasses` for structured config/results.
- Random seeds are set for reproducibility (Monte Carlo/simulation); keep seeded, deterministic runs.
- Public data sources referenced: EIA, World Bank.
- Write paths relative to the repo root (no absolute local paths).

## Output artifacts
- Charts are generated with matplotlib.

## Guardrails
- Never commit secrets, API keys, tokens, or `.env` files.
- Do not commit large raw datasets or binaries; keep data fetched or documented with its source.
- Keep analysis source-backed: cite data sources and assumptions; label scenario/forecast outputs as model estimates, not facts.
- Synthetic data must stay synthetic; never introduce real personal or sensitive records.
- Preserve reproducibility: no unseeded randomness, no hidden manual steps.
