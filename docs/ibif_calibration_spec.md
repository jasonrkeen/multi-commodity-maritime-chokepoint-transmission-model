# Draft IBIF public market calibration specification

Status: **DRAFT 0.2 — not preregistered, not fitted, not operational**.
The public-market-first scope was selected on October 13, 2026. The October 22
cutoff amendment and fixed control screen are linked below. Unresolved gates
prevent treating this draft as a frozen evaluation protocol. These documentation
decisions do not change runtime model inputs.

## Purpose and claim boundary

First assess the crude-oil market path against public Brent observations.
Success would support only a specified market-model evaluation. It would not
validate organization-specific losses, the five IBIF dimensions, BCS weights,
scenario probabilities, sensor reliability or escalation thresholds. Keep the
existing weights fixed as experimental descriptors; do not fit BCS to the
model's own dollar output. Flow observations are a secondary feasibility track.

## Proposed primary outcome

| Item | Definition |
|---|---|
| Commodity and benchmark | Crude oil; EIA Europe Brent Spot Price FOB, nominal USD/barrel, daily series `RBRTE` |
| Primary horizon | 30 calendar days; 90 days is a separately reported secondary horizon |
| Unit of evaluation | One independently documented disruption cluster and forecast origin; controls are separate documented quiet-period origins |
| Forecast origin | A UTC timestamp at which all forecast inputs must already be published and accessible; observation dates alone do not establish availability |
| Target window | Dates from the first full UTC day after the origin through day H inclusive |
| Primary target | Arithmetic mean of published daily Brent prices on the valid observation dates in that window |
| Model mapping | Model `day=0` maps to the first target calendar day; align `implied_price_usd` for Crude oil to the same observation dates before averaging |
| Primary loss | Absolute difference between predicted and observed horizon means, in USD/barrel |
| Secondary diagnostics | Signed bias, daily path MAE on the same dates, peak-price error and 90-day results; do not select a winner by whichever metric looks best |
| Baseline | Constant latest numeric Brent observation in the ALFRED vintage dated origin minus two calendar days; same baseline for model and comparator; policy 0.4 applies |

Let D be the valid observed dates, P(d) the observed price and F(d) the model
price. The primary observation is `mean(P(d), d in D)` and the primary error is
`abs(mean(F(d), d in D) - mean(P(d), d in D))`. Daily MAE is a distinct secondary
measure; it does not replace the primary after results are seen. Report per-origin
losses, average origins within each disruption cluster, then weight clusters
equally. Report disrupted and control strata separately, without data-driven
reweighting. Multiple dates from one crisis are not independent events.

Use the source's observation calendar. Preserve holiday, absent, withheld and
unavailable markers; do not interpolate target prices or fill weekends with
zeros. Report valid observation counts and distinguish routine nonpublication
from unexplained gaps. Require every scheduled source observation for the window
or an explicit documented exclusion; the source calendar and completeness rule
must be resolved before evaluation. Do not discard declining-price episodes or
clip negative changes. This is predictive association, not causal attribution of
all price changes to the chokepoint.

## Forecast inputs and replay rules

Each origin needs a separate frozen input bundle and model commit. Historic
route weights, baseline price, inventories, event severity/duration assumptions,
policy responses and other parameters must be justified from material available
then. The current 2026 assumptions cannot silently stand in for earlier vintages.
Rebase the price input only by a declared, reviewed replay rule; no runtime replay
implementation is introduced here.

Choose an event origin and scenario-construction rule from contemporaneous
restriction notices, not a later price peak or a hand-picked fitted path. Do not
use realized closure duration or future sensor rows as forecast inputs. Keep
sensor fusion off in the initial pilot unless actual, time-stamped observations
and a causal processing policy are verified. Filtering rows is insufficient if
interpolation, normalization or feature construction still uses future data.

When publication vintages cannot be recovered, label the exercise retrospective
reconstruction and exclude it from claims of genuine forecast performance. A
current revised price history can provide an outcome snapshot; it cannot prove
which inputs were available at a historical forecast origin. Retain both the
outcome snapshot date and the input publication dates.

## Event ledger and eligibility

Use the [header-only event ledger](templates/ibif_event_ledger.csv), with one row
per cluster/origin/horizon/metric. It deliberately contains no invented events.

Required evidence includes a stable cluster ID; chokepoint; primary event notice
and locator; event start/end and publication timestamp; issue timestamp;
commodity/benchmark/unit; target dates; source series and snapshot hash; input
manifest and model commit; data vintage; forecast/estimate/observed/synthetic
classification; valid and expected observation counts; exclusions; and review
status. Retain an inclusion register even for excluded events.

Build a candidate universe from a fixed set of official notices before examining
model errors. Include quiet periods under a fixed calendar rule and record
overlapping crises as shared clusters. Do not select controls because prices
were stable. The 2021-2024 quarterly control universe and rule are fixed in protocol 0.4;
all 32 control windows are excluded. The disruption universe remains exploratory.
Target data volume is not evidence of enough independent replayable events.

## Development and evaluation

Keep the current model and no-change forecast as baseline candidates. Limit any
later fitting to a small prespecified set of interpretable market parameters;
do not optimize to the analyst Brent comparator bands. Parameter selection,
normalization and missing-data choices belong inside development folds.

After the eligible event inventory is fixed, record chronological train,
validation and final-test boundaries in a signed-off split manifest. Keep related
origins/commodities in one cluster and purge training target windows overlapping
later forecast origins. Respect publication delays. Determine adequate cluster
counts using desired error precision and decision relevance; no minimum count
has yet been justified. Historical data inspected during this feasibility work
are not a blind prospective holdout. A prospective phase begins only after the
final protocol and model are frozen.

Compare primary errors with the no-change baseline on identical windows. Report
paired cluster-level differences and uncertainty where the independent-cluster
count permits defensible inference. Do not bootstrap daily rows as independent
events. Define the practically meaningful improvement, uncertainty tolerance,
subgroup checks and minimum sample adequacy before opening the final test.
These numerical acceptance criteria remain unresolved; passing a significance
test alone is insufficient. Failure or inconclusive evidence must remain visible.

## Secondary flow track

Explore matched daily chokepoint transit/volume estimates separately. A vessel
count or AIS-derived tonnage estimate is not the model's global commodity supply
loss fraction. Verify commodity coverage, units, geography, baseline denominator,
revision policy and independence from model-input data before a comparison.
Do not combine price and flow errors into one fitted score. The source inventory
in [data feasibility](ibif_data_feasibility.md) is discovery evidence, not an
approved flow dataset.

## Freeze checklist and next work

| Gate | Current state | Required artifact |
|---|---|---|
| Scope | Public market outcomes selected | This draft |
| Primary target | Brent 30-day mean proposed | Approved calendar, alignment and completeness policy |
| Outcomes | Public price snapshot accessible | Audited extraction and source-use terms |
| Events and as-of inputs | [Candidate inventory populated](ibif_event_inventory.md); zero accepted replay rows | 32 controls excluded under fixed rule; cutoff adopted; numeric global mappings and other inputs still missing |
| Model replay | Not implemented or validated | Versioned as-of replay rules and regression evidence |
| Splits and acceptance | Unresolved | Immutable split manifest, precision rationale and numerical criteria |
| Fitting | Not started | Only after the preceding gates close |

Freeze by recording the approved specification hash, dated decision log, event
inventory and split-manifest hashes, model/input hashes and access controls for
test outcomes. Amendments require a new version explaining whether the prior
test set has been exposed. Keep analytic confidence null, escalation UNASSESSED,
and PR #6 draft until separately authorized otherwise.

The temporal evaluation rule follows [Forecasting: Principles and Practice,
section 5.10](https://otexts.com/fpp3/toolbox.html#time-series-cross-validation).
The primary target and gates here are project proposals, not that source's
endorsement of this model.

The [publication and mapping policy 0.4](ibif_publication_mapping_policy.md)
explicitly replaces the draft 0.1 freshest-price baseline with a lagged ALFRED
channel. Nine recovered price selections and 27 descriptive stock selections
are audited against that rule. It does not authenticate original EIA intraday
releases or authorize regional stocks as global buffers. The
[fixed control protocol](ibif_control_protocol_0_4.md) and
[32-window results](ibif_control_results_0_4.md) replace the informal quiet-period
selection procedure. These amendments were made during historical feasibility
work, before fitting, and are not prospective preregistration. Zero complete
replay bundles are accepted; numeric mappings, scenario policy, outcome calendar,
splits and performance acceptance criteria remain gates.

October 22 background-design amendment: [calendar comparators](ibif_background_design_0_5.md) retain all 32 quarterly windows as NOT_RUN;
[physical recovery](ibif_physical_inputs_0_5.md) adds two reference-year exposure candidates and partial US inventory evidence.
These do not approve global buffers, historical replay, or calibration.
