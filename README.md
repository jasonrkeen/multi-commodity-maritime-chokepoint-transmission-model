# Multi-Commodity Maritime Chokepoint Transmission Model

Version 0.6.0 is a transparent scenario, Monte Carlo, structural-balancing, market-segmentation, and calibration-diagnostic model for estimating how maritime chokepoint disruption transmits through **crude oil, LNG, fertilizer, and helium**.

The model combines physical-flow stress, pipeline bypass, emergency stock releases, external supply response, dynamic demand, crude-grade mismatch, segmented purchasing channels, route dependencies, inventory, sensor confidence, delayed downstream effects, and a separate conditional ecological branch. Dollar results are modeled **gross economic exposure**, not net GDP loss, firm valuation, or realized damages.

Version 0.6.0 adds an enabling-availability chain for reassigned heavy-sour barrels. Nominal reassignment is discounted by upstream, electric-grid, and terminal availability before it can reduce the regional grade gap. The three factors default to 100%, so existing scenario results remain unchanged until a source-country fragility assumption is explicitly configured. This public release contains no third-party practitioner packet, packet schema, signal taxonomy, or packet-derived diagnostic.

## What changed in version 0.6

- Reassigned heavy-sour supply is multiplied by upstream, grid, and terminal availability before reducing the regional sour gap.
- Daily and summary outputs report enabling availability and effective reassignment separately from nominal reassignment.
- Legacy v0.5 crude-market structure files receive neutral `1.0` defaults for all three availability fields.
- Public USGS and Reuters reporting provides event and infrastructure context; availability values remain explicit analyst assumptions.
- Two regression tests enforce the enabling chain and backward-compatible defaults, bringing the release gate to 26 tests.

## What changed in version 0.5

- Brent and a regional medium/heavy-sour proxy now follow separate price paths.
- Grade compatibility, sour-market concentration, reassigned heavy-sour barrels, and route friction determine the modeled basis spread.
- True consumption reduction is separated from apparent benchmark-market withdrawal into discounted or insulated channels.
- Reassigned barrels can reduce a regional grade gap but are never counted as new global supply.
- Undeclared activity is confidence-weighted using detection recall, identity resolution, AIS staleness, radar-wake persistence, and backtest maturity.
- A conditional ecological scenario adds independently governed desalination, fisheries/coastal-livelihood, and remediation clocks; its exposure is reported separately from the commodity total.
- Five new regression tests bring the release gate to 24 tests.

## What changed in version 0.4.1

- Added GitHub Actions continuous integration across Python 3.11 through 3.14.
- Added MIT licensing, citation metadata, contribution guidance, a security policy, and a release checklist.
- Expanded ignore rules for generated outputs, credentials, local environments, caches, and editor files.
- Shifted the public repository artifact to a source-first distribution; scenario outputs remain reproducible locally.
- No model equations, assumptions, scenario priors, or validated v0.4.0 results changed.

## What changed in version 0.4

- Commodity- and scenario-specific pipeline bypass is separated from ordinary maritime rerouting.
- Emergency stock releases are explicit market flows with start, ramp, duration, and decay parameters.
- A release depletes the modeled strategic stock and cannot be counted again as automatic inventory cover.
- External non-chokepoint supply response ramps separately from bypass and emergency stocks.
- Brent stress is decomposed into residual physical-gap, base scenario-risk, and sensor-opacity contributions.
- New counterfactuals show prices without structural offsets and without any structural or demand balancing.
- The calibration grid now varies the structural-supply layer instead of commercial inventory that did not bind in the validated sensor scenario.
- The executive brief adds a fourth page for structural-flow and price-contribution attribution.

## What changed in version 0.3

- Monte Carlo output now reports the share of crude-price simulations below, within, and above the independent Brent comparator band.
- A deterministic scenario-comparison table places physical exposure, lag structure, priors, weighted exposure, demand moderation, and Brent diagnostics side by side.
- An optional four-factor sensitivity grid varies crude demand elasticity, demand adjustment speed, structural supply offsets, and scenario risk premium.
- Calibration results are diagnostic only: the closest combination is reported, but baseline assumptions are never overwritten automatically.
- Aggregate `TOTAL` price fields are blank because crude, LNG, fertilizer, and helium prices use incompatible units.

## What changed in version 0.2

- Dynamic demand destruction replaces a static demand-offset assumption.
- Scenario paths have editable prior probabilities and non-driving Brent validation bands.
- A dependency matrix propagates stress from Hormuz to Bab el-Mandeb and Suez.
- Bab el-Mandeb and Suez are separated operationally but grouped for physical exposure to prevent simple serial-route double-counting.
- An optional sensor-fusion scenario blends AIS, SAR, ballast movement, thermal anomalies, and radar-wake confidence into the daily physical state.
- The SAR-minus-AIS discrepancy becomes an undeclared-activity/opacity signal rather than being treated as missing flow.
- Fertilizer has a separate 150-day seasonal channel from missed delivery/application to later harvest exposure.
- Helium commercial inventory is explicitly separated from a **zero-day strategic reserve** assumption.
- The executive brief now includes demand balance, target-band validation, dependency severity, and sensor diagnostics.

The mapping from practitioner-informed questions to implementation is documented in `docs/model_refinement_notes.md`. Private input informed the model architecture but is not presented as public evidence or attributed without permission.

## Transmission architecture

### 1. Direct and dependent chokepoint stress

Each scenario supplies direct disruption paths. The dependency matrix adds lagged spillover:

```text
dependent_severity(target,t)
  = severity(source,t-lag) × transmission_weight(source,target)
```

Direct and transmitted severity are combined with a bounded union. This lets a Hormuz-only event create later pressure at Bab el-Mandeb and Suez through rerouting, congestion, insurance, and security spillover.

### 2. Commodity route loss

```text
route_loss(i,j,t)
  = route_share(i,j)
  × disruption_severity(j,t)
  × [1 - reroute_capacity(i,j,t)]
  × [1 - substitution(i,t)]
```

Nodes in the same serial `route_group` use the maximum loss rather than a sum. Losses across distinct route groups use a bounded union.

### 3. Structural market balancing

Gross route loss is reduced by distinct, non-additive flows before demand and
pricing are calculated:

```text
structural_supply_offset
  = pipeline_bypass
    + emergency_stock_release
    + external_supply_response

balanced_supply_loss
  = max(gross_route_loss - structural_supply_offset, 0)
```

Each flow has its own scenario- and commodity-specific timing. Emergency stock
releases are limited by the remaining strategic stock. Hormuz pipeline capacity
is represented here rather than in the generic maritime-rerouting parameter.

### 4. Dynamic demand response

Demand is now a state variable:

```text
net_market_gap(i,t) = max(balanced_supply_loss - demand_reduction_state, 0)

price_shock(i,t)
  = min(price_cap,
        net_market_gap / short_run_adjustment_elasticity
        × market_tightness
        + market_risk_premium)

demand_target(i,t)
  = min(max_demand_reduction,
        price_shock × demand_price_elasticity
        + policy_demand_reduction)
```

The demand state adjusts gradually and has a separate recovery half-life. This allows a disruption to price below a static supply-gap reading when consumption, rationing, fuel availability, or government measures reduce demand.

Scenarios may also begin with an editable preconditioned demand reduction. This represents adaptation that occurs while conflict risk is building before the modeled disruption day rather than assuming the market first reacts at day zero.

The capped price shock is decomposed proportionally into physical-gap, base
risk-premium, and sensor-opacity contributions. This preserves exact
reconciliation even if a commodity price cap binds.

### 5. Immediate impact

```text
immediate_impact
  = exposed commodity spend repricing
    + rerouting cost
    + war-risk insurance cost
```

Repricing is a gross exposure/transfer measure, not a pure global welfare loss.

### 6. Inventory and strategic reserves

Emergency releases draw from the strategic stock according to the explicit
market-balancing schedule. The remaining net physical deficit then draws
commercial inventory; any residual becomes a physical shortage. Strategic
stocks are not drawn a second time. Helium has editable commercial inventory
but no strategic reserve or emergency-release flow in the baseline.

### 7. Lagged and seasonal impact

```text
regular_lag_target
  = delayed_price_shock × downstream_input_cost_share
    + delayed_shortage × availability_multiplier

fertilizer_seasonal_target
  = balanced_supply_loss(t-150 days) × seasonal_transmission_multiplier
```

An adaptive state converts those targets into daily downstream economic exposure. The fertilizer channel is intended to represent the fact that missed application may not appear in economic data until later crop outcomes.

### 8. Sensor/model feedback

The included `sensor_fused_hormuz` scenario is a **synthetic demonstration**, not operational or practitioner-supplied data.

- AIS provides declared identity, heading, and movement.
- SAR receives greater weight in estimating physical passage.
- SAR traffic above declared AIS traffic creates a dark/undeclared-activity index.
- Detection recall and backtest status scale confidence in the physical observation.
- Identity resolution and time since the last AIS fix determine track-continuity confidence.
- Radar-wake persistence modifies detection confidence without substituting for backtesting.
- Ballast repositioning and thermal anomalies contribute forward-risk context.
- The physical-flow estimate and opacity premium update the quantitative path together.

This design avoids a key selection problem: an AIS-only disruption estimate can overstate closure when non-declaring vessels continue to move.

### 9. Crude grade and market-channel segmentation

The crude path distinguishes the global Brent proxy from a regional sour-complex proxy:

```text
sour_gap
  = loss_after_structural_offsets / sour_dependent_market_share
    × (1 - alternative_grade_compatibility)
    - effective_reassigned_heavy_sour_share

effective_reassigned_heavy_sour_share
  = reassigned_heavy_sour_share
    × upstream_availability_share
    × grid_availability_share
    × terminal_availability_share

regional_sour_price = brent_proxy + grade_and_logistics_basis
```

Segmented purchasing channels reduce the price shock experienced by participating buyers and create an apparent withdrawal from the benchmark market. That channel shift is reported separately from true consumption reduction. Only effectively available reassigned barrels affect the regional sour gap; they do not reduce the global physical deficit.

### 10. Conditional ecological transmission

The `compound_hormuz_red_sea_ecological` branch activates ecological incident severity explicitly. Independent adaptive lags model desalination continuity, fisheries/coastal livelihoods, and remediation. These low-confidence externalities are written to separate outputs and excluded from the core commodity exposure total.

## Included chokepoints

- Strait of Hormuz
- Bab el-Mandeb
- Suez Canal/SUMED
- Strait of Malacca
- Panama Canal

## Included scenarios

- `hormuz_30d_severe`
- `red_sea_60d_diversion`
- `compound_hormuz_red_sea`
- `multi_node_stress`
- `sensor_fused_hormuz`
- `compound_hormuz_red_sea_ecological`

Scenario events live in `data/input/scenarios.csv`. Probabilities, market-risk premiums, policy-demand assumptions, and Brent validation bands live in `data/input/scenario_catalog.csv`.

Brent bands are **comparators only**. They do not drive the price function. A model result outside the band is preserved as a calibration diagnostic rather than forced to fit.

## Quick start

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py --scenario compound_hormuz_red_sea --days 240 --simulations 200
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python main.py --scenario compound_hormuz_red_sea --days 240 --simulations 200
```

Run the sensor demonstration:

```bash
python main.py --scenario sensor_fused_hormuz --days 240 --simulations 200
```

Run the comparison and calibration diagnostics:

```powershell
python main.py --scenario sensor_fused_hormuz --days 240 --simulations 200 --seed 20260811 --compare-scenarios --calibration
```

Run the explicit ecological branch:

```powershell
python main.py --scenario compound_hormuz_red_sea_ecological --days 240 --simulations 200 --seed 20260812
```

The default calibration levels are `0.75`, `1.0`, and `1.25`, producing an
81-run full-factorial deterministic grid. Override them when a faster or more
focused diagnostic is appropriate:

```powershell
python main.py --scenario compound_hormuz_red_sea --days 240 --simulations 0 --calibration --calibration-levels 0.9 1.0 1.1
```

Run deterministically while editing assumptions:

```bash
python main.py --scenario hormuz_30d_severe --days 240 --simulations 0
```

The default 200 draws are for iteration. Use `--simulations 5000` only after the scenario and assumptions are stable.

## Outputs

Each run writes to `outputs/<scenario>/`:

- `commodity_daily.csv`
- `scenario_summary.csv`
- `monte_carlo_summary.csv`
- `scenario_target_check.csv`
- `ecological_externalities_daily.csv`
- `ecological_externalities_summary.csv`
- `ecological_monte_carlo_summary.csv`
- `model_run_metadata.json`
- `executive_brief.pdf`
- `charts/transmission_timeline.png`
- `charts/impact_by_commodity.png`
- `charts/demand_balance.png`
- `charts/market_balance_decomposition.png`
- `charts/crude_market_segmentation.png`
- `charts/ecological_externalities.png` when the ecological branch is active
- `charts/sensor_fusion.png` when sensor fusion is active

With `--compare-scenarios`, the model also writes `outputs/scenario_comparison.csv`.
With `--calibration`, the selected scenario directory also receives:

- `calibration_sensitivity.csv`
- `calibration_summary.csv`

The Monte Carlo and target-check files include exact simulated Brent band-coverage shares. Price metrics remain commodity-specific; no cross-commodity aggregate price is reported.

## Input governance

- `commodities.csv`: market values, supply/price elasticity, dynamic demand, commercial inventory, strategic reserves, substitution, and lag parameters
- `chokepoints.csv`: rerouting, ramp, freight, and insurance parameters
- `exposure_matrix.csv`: commodity route shares, serial route groups, and confidence
- `scenarios.csv`: event timing, duration, severity, and recovery
- `scenario_catalog.csv`: scenario probability, risk premium, demand policy, and validation bands
- `market_balancing.csv`: pipeline bypass, emergency-release, and external-supply timing and capacity
- `crude_market_structure.csv`: sour-market concentration, grade compatibility, segmented-channel insulation, nominal reassignment, upstream/grid/terminal availability, and basis assumptions
- `ecological_externalities.csv`: conditional incident severity, channel-specific lags, value at risk, and confidence
- `chokepoint_dependencies.csv`: lagged stress transmission between nodes
- `sensor_signals.csv`: synthetic sensor-fusion demonstration
- `validation_events.csv`: observed calibration anchors
- `source_register.csv`: public sources and assumption status

## Calibration anchors

- EIA reports substantial demand reduction from high fuel prices, constrained availability, and government measures during the 2026 Hormuz disruption. The August outlook estimates global consumption falling by roughly 1.2 million barrels/day in 2026 and documents continuing inventory and recovery effects.
- EIA route-flow work anchors Hormuz oil and LNG exposure and Red Sea diversion behavior.
- EIA crude-quality guidance anchors the fact that density and sulfur content affect refinery processing and the economic substitutability of crude grades.
- EIA estimates about 2.6 million barrels/day of available Saudi and UAE pipeline capacity could bypass Hormuz; this anchors the crude bypass ceiling.
- IEA emergency-response documentation anchors the explicit stock-release mechanism. Release timing and accessible daily flow remain scenario assumptions.
- The World Bank reports that fertilizer disruption can reduce application and emerge later in harvest outcomes.
- USGS identifies the United States and Qatar as leading helium producers/exporters; exact route exposure and commercial inventories remain assumptions pending better shipment data.
- NOAA incident and restoration material anchors the separation of environmental injury and multi-year recovery from short-run commodity pricing; all ecological values and severities remain analyst assumptions.
- USGS earthquake information and Reuters infrastructure reporting anchor the distinction between intact upstream barrels and unavailable grid, terminal, refining, or petrochemical enabling layers. The three availability shares remain scenario assumptions.

Full URLs and usage are recorded in `data/input/source_register.csv`.

## Validation

```bash
python -m unittest discover -s tests -v
```

The 26 tests cover bounded loss, recovery, serial-route grouping, dynamic demand, structural-flow offsets, strategic-stock depletion, price-contribution reconciliation, dependency propagation, sensor selection-bias correction, confidence maturity and AIS staleness, crude-channel misclassification, sour-basis conservation, heavy-sour enabling availability and legacy defaults, delayed ecological transmission and ecological Monte Carlo quantiles, seasonal fertilizer lag, helium reserve treatment, inventory exhaustion, impact reconciliation, commodity Monte Carlo quantiles and target coverage, scenario comparison, aggregate-price governance, and calibration baseline preservation.

The GitHub Actions workflow repeats the suite on Python 3.11, 3.12, 3.13, and 3.14 and runs a deterministic 30-day smoke scenario. Generated files are written outside the checked-out repository during CI.

## Repository and data policy

The public repository includes the source code, tests, documentation, and the curated CSV configuration required to reproduce the model. Those inputs are public-source anchors, synthetic signals, or explicitly labeled analyst assumptions.

The repository excludes generated run outputs, raw or licensed source material, third-party practitioner packets and derived diagnostics, credentials, private correspondence, operational sensor feeds, local environments, caches, and temporary rendering files. Recreate outputs with the commands above rather than committing them.

See `CONTRIBUTING.md` before proposing changes, `RELEASE_CHECKLIST.md` before tagging a release, `docs/github_readiness_audit.md` for the publication controls, and `CITATION.cff` when citing the software. The project is released under the MIT License.

## Interpretation cautions

- Outputs are global gross exposure and should not be read as additive GDP loss.
- Scenario probabilities are analyst priors, not statistically estimated event frequencies.
- Scenarios can overlap conceptually. Probability-weighted scenario rows must not be added unless the paths have first been redefined as mutually exclusive branches.
- Brent targets are validation comparators, not imposed outcomes.
- Sensor rows are synthetic examples and must not be mistaken for live SAR/AIS observations.
- Dependency weights are analyst assumptions and may mix congestion, security, insurance, and rerouting mechanisms.
- Serial grouping reduces double-counting but does not replace shipment-level origin-destination routing.
- Demand response remains an aggregate reduced-form state rather than a sector-by-country system.
- Sour-complex prices are model proxies, not observed Oman, Dubai, or Dated Brent forecasts; the basis parameters require public grade-flow calibration.
- Segmented-channel shifts are analytic assumptions and do not identify particular buyers, sanctions programs, or vessels.
- Ecological externalities activate only in the named conditional branch, carry low confidence, and are excluded from commodity totals.
- Sensor identity, staleness, recall, and validation-status fields are synthetic in the bundled demonstration.
- Bypass capacity, emergency-release accessibility, and external supply response are source-anchored where possible but retain analyst timing assumptions.
- Fertilizer is aggregated; urea, ammonia, DAP, sulfur, and potash need separate calendars and trade networks.
- Helium availability depends on purity, containers, allocation, and industrial qualification—not only aggregate volume.

## Recommended next build

Add mutually exclusive scenario-tree probabilities, Bayesian sensor updating,
public grade-level cargo and refinery configuration data, country-level demand
and inventory states, bilateral trade flows, and sector input-output tables.
Those additions would turn the current global transmission engine into a
regional incidence model capable of estimating who absorbs the shock and how
physical evidence changes scenario probabilities.
