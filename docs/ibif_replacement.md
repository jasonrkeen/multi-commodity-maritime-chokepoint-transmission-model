# IBIF replacement 0.1.1

This is a **new, experimental replacement**, authorized on October 13, 2026.
It is not the unrecovered `chokepoint_ibif_integration_v0_2.zip` and does not
reproduce its undocumented implementation. The target base is public commit
`6c1cc646fa9486817fe5d8c9f1f6fdd9eadfa451` (model v0.6.0), not the separate
private v0.6.3 diagnostic package. The model version is deliberately unchanged.

## Use

```powershell
python main.py --scenario sensor_fused_hormuz --days 240 --simulations 200 --seed 20260812 --ibif
python main.py --scenario compound_hormuz_red_sea --days 240 --simulations 200 --seed 20260812 --ibif
```

Without `--ibif`, the adapter is neither imported nor called. With it, the
adapter reads the deterministic daily dataframe and commodity parameters only
after all pre-existing computations and reporting finish. It adds exactly
`ibif_assessment.json`, `ibif_assessment.csv`, and `ibif_assessment.md` in the
scenario output directory. Existing outputs, probability, sensor fusion,
Monte Carlo and calibration logic are untouched. Use fresh output directories
when comparing modes: disabling IBIF does not delete reports from an earlier run.

The adapter does not summarize the Monte Carlo distribution. Scores describe
the deterministic conditional scenario, not a probabilistic score distribution.
Invalid/incomplete data raises `ValueError`; because IBIF executes last, existing
model outputs may already exist after an IBIF failure. Check the process exit code.

## Explicit analyst assumptions

For a nonnegative value `x`, `S(x) = 100 * min(x, 1)`.
All peaks below are independently computed across the supplied horizon. A
combination of peaks is not a simultaneous observed condition. Ratios above one
are retained in raw outputs but capped when scoring. Units are fractions, not
percentage points. Probability must be constant and between zero and one.

| Dimension | Replacement formula |
|---|---|
| Exposure | Mean of S(peak active route weight) and S(peak supply loss) |
| Dependency | Mean of S(peak dependency-induced severity) and S(peak balanced supply loss) |
| Vulnerability | Mean of S(peak net market gap), S(peak physical shortage), and S(inventory depletion) |
| Transmission | Mean of S(peak direct disruption), S(peak dependency-induced severity), and S(peak lag state) |
| Impact | S(sum of daily total impact / horizon market-value scale / scale multiplier) |

Inventory depletion is `max(0, 1 - minimum inventory / initial inventory)`;
initial inventory equals initial commercial plus strategic reserve days from
commodity parameters. If initial inventory is zero, depletion is undefined:
omit it, average the two remaining vulnerability components, and report the gap.

The horizon market-value scale is `annual_market_value_usd * days / 365`.
The default scale multiplier is 1.0. Modeled exposure includes downstream
effects, so this normalization is **an arbitrary scoring reference, not an
economic loss fraction**. Saturation and the uncapped ratio are reported.

BCS = 0.20 E + 0.20 D + 0.20 V + 0.15 T + 0.25 I.
Risk pressure = scenario probability (0–1) * BCS (0–100).
The weights retain the historical conversation's proposed proportions; the
component formulas and normalization are newly specified replacement choices.
Overlapping components can double-count related mechanisms. No claim of
statistical independence, predictive validity, or cross-commodity comparability
is made. Scores are per commodity; there is no aggregate portfolio BCS.

Every record also reports equal-weight BCS, impact-heavy weights
(0.15, 0.15, 0.15, 0.15, 0.40), and half/double impact-scale BCS. These are
sensitivity checks, not optimized or empirically selected alternatives.

## Evidence and decision boundaries

Probability is the existing scenario prior; it is not inferred from the score.
The field `sensor_evidence_proxy` is an **experimental upstream sensor diagnostic**,
not a calibrated measure of evidence quality or reliability. Its existing field
name is retained for compatibility. When sensor fusion is active and scenario
sensor rows are available, the diagnostic is 100 times the horizon mean
of the smaller of daily sensor confidence and track-continuity confidence.
These upstream fields are scenario sensor-panel summaries repeated on commodity
rows; they are not independent commodity-specific observations. Inactive sensors
produce `null`, not an invented confidence value. Active sensors require finite
confidence fields in [0, 1]. Sensor source types are copied from input metadata;
labels are not independent source verification. `synthetic_demo` is explicitly
identified as a demonstration. The evidence proxy does not establish reliability
of priors, parameters, causal structure, business mapping, or the score itself.

The upstream model independently maximizes confidence and continuity across
chokepoints each day. Taking the minimum of those two maxima can combine different
sources: pairs `(0.9, 0.1)` and `(0.1, 0.9)` produce `0.9`, although each source's
paired minimum is `0.1`. This is a multi-source counterexample, not a measured
error in the bundled single-chokepoint demonstration. Source pairing cannot be
recovered from the aggregated daily fields.

The sensor panel also interpolates observations and extends them with up to
45 days of synthetic decay. Days without panel coverage contribute zeros to the
horizon mean. Consequently, the diagnostic mixes assumed quality, coverage,
decay and horizon length. A positive panel day is not necessarily an observed
day; a zero is not necessarily measured poor quality. Do not use this diagnostic
to rank evidence sources, validate probabilities or trigger decisions. A future
evidence metric requires matched source/chokepoint/day records, route relevance,
observed/interpolated/decayed/missing flags and separately reported coverage.
The current JSON/CSV field and generated report labels are unchanged by this
documentation correction; their values must be interpreted under these limits.

`analytic_confidence` remains null and `escalation_status` remains `UNASSESSED`.
Gross modeled exposure retains its original meaning: not realized financial
loss, organization-specific loss, or net GDP loss. There is no automated decision,
alert, evidence-ledger authentication, or claim that this implements the full
historical generic IBIF schema. Collection gaps are reported explicitly.

## Validation and release boundary

Run `python -m unittest discover -s tests -v` and the contributing-guide smoke
test. For equivalence, compare untouched, replacement-disabled, and
replacement-enabled runs separately for both named scenarios at 240 days,
200 simulations, seed 20260812, using identical inputs and dependencies.

Require identical pre-existing file inventories and byte-identical CSVs and
charts. Run metadata can differ only in `generated_at_utc`. PDF creation dates
may differ; compare all other metadata, extracted text, and every rendered page.
Verify the three new reports and no extra files, input/source integrity, and
record exact environment and source hashes. Timestamp exceptions must be
documented, not silently treated as byte identity. Any demonstrated equivalence
is bounded to those executions and does not establish calibration or historical
v0.2 equivalence. See the separate dated validation evidence for actual results.

Do not publish private v0.6.3 diagnostics or original archives with this patch.
Empirical score calibration, organizational exposure mapping, external
methodological review, operational thresholds, and prospective validation remain
future work. This candidate remains a draft, unmerged PR.

The first proposed calibration pilot uses public market outcomes, starting with
Brent prices. See the [draft specification](ibif_calibration_spec.md) and
[data-feasibility assessment](ibif_data_feasibility.md). This does not calibrate
business losses, BCS weights, sensor reliability or operational thresholds.

## Review corrections and source-only equivalence runner

Replacement 0.1.1 withholds the evidence proxy unless observation availability
is explicitly confirmed. The CLI checks whether the selected scenario has sensor
rows; API callers must pass `sensor_evidence_available=True` only when appropriate.
This establishes availability, not source validity or coverage. Unknown or absent
observations produce null even when sensor fusion is enabled. Initial inventory
sum overflow and imprecisely normalized weights are rejected.

The methodology remains provisional: independent peaks mix times, dimensions
reuse related mechanisms, and horizon market-value scaling is arbitrary. None of
these properties has been empirically corrected by the software review. Retain
UNASSESSED escalation and null overall analytic confidence pending independent
calibration. Sensor proxies are scenario-level summaries, not independent
commodity-specific evidence. Scores can vary with horizon length even when the
underlying disruption does not change; compare only consistent horizons/scales.

The source-only runner is `tools/validate_ibif_equivalence.py`. It snapshots the
actual candidate (including uncommitted, non-ignored files) rather than embedding
hashes of a historical candidate. It requires a clean separate baseline checkout
at the pinned commit, a fresh evidence directory outside both source trees, and
an unchanged source snapshot through the run. Failures remain active with
`python -O`; exceptions write FAIL instead of leaving a stale PASS.

Install the model requirements plus `pypdf` and `Pillow`; install Poppler's
`pdftoppm` on PATH. Then run:

```powershell
python tools/validate_ibif_equivalence.py --baseline C:/path/to/clean-baseline --candidate C:/path/to/candidate --output-dir C:/path/to/new-evidence
```

Defaults are both scenarios, all three modes, 240 days, 200 simulations,
seed 20260812. `--days 30 --simulations 0` provides a shorter integration check;
it is not the full protocol. Evidence records exact settings, package versions,
commands, exit codes, source hashes, output hashes, and timestamp exceptions.
PDFs are checked as normalized bytes, extracted text and rendered pixels.
Generated evidence belongs outside this source PR.

Six full runs at commit `729b19373bc812f3c0db3a399610c399550c480f`
validated replacement-0.1.1 at 240 days, 200 simulations, seed 20260812. All four
comparisons passed with timestamp-only exceptions, identical PDF text/pixels,
and exactly three added reports when enabled. Earlier 0.1.0 evidence at
`678ba6b` is separate. The later calibration documentation revision is not a new
full simulation run; no executable code or model-input change is included.
