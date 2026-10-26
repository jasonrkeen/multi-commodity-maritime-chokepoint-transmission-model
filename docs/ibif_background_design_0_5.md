# Background-period comparator design 0.5

Decision date: October 22, 2026. This replaces no earlier screening result.
Protocol 0.4 and its 32 exclusions remain valid for its strict incident-free
definition. This amendment is informed by those inspected incidents and is not
blinded, preregistered, causal, or prospective validation.

## Estimand and fixed universe

Assess unconditional calendar-origin price forecasting in ordinary market
conditions, where ordinary includes maintenance, geopolitical incidents and
crises. These are **background calendar comparators**, not untreated or quiet
controls. Use every January/April/July/October 1 at 00:00 UTC in 2021-2024: 16
origins, each with 30- and 90-day targets. Retain all 32 candidate windows. Do not
replace an origin, change its date or remove it because of an incident, price
movement, poor model fit or unavailable input. Missing inputs cause an explicit
NOT_RUN row, not a favorable replacement date. Keep the three purposive event
origins in a separate descriptive stratum, not a representative treatment sample.

Targets, observation calendar and losses follow the calibration specification.
Both model and no-change forecast must use policy 0.4's same lagged ALFRED price.
Price baseline alone supports no-change forecasts; a model run additionally needs
all accepted physical/scenario inputs. Report baseline-only and paired-eligible
counts separately. Compute paired errors only on identical windows, disclose every
missing pair and never describe the paired subset as the complete calendar sample.
No target values or errors are computed by this design document.

## Information and incident handling

Maintain two separate ledgers:

1. **Forecast information:** only sources satisfying the two-day cutoff, with
   vintage and source hash. At-origin restriction/detention status can be known,
   unknown or absent in a documented bounded source set. Missing coverage is
   unknown, not zero severity. Future incident labels cannot enter features.
2. **Retrospective diagnostics:** the existing incident/maintenance witnesses,
   plus any later recovered events, clearly label-only. These do not filter the
   calendar universe, choose scenario inputs, tune parameters, or justify causal
   effects. A single positive witness is not a complete window's incident count.

Routine planned maintenance and verified disruptions are retained. Before any
market-model replay, freeze a scenario-construction rule using available notices
for severity, response and duration distributions. No realized closure duration,
future announcement or final incident classification may supply forecast inputs.
Do not assume no disruption when notices are missing. A no-disruption model
scenario may later be reported as an explicit counterfactual, not an as-issued
forecast. Sensor fusion stays off absent verified causal historical observations.

## Eligibility and dependence

Calendar membership is fixed; execution eligibility is separate and requires
price-policy pass, accepted physical normalization, documented historical
scenario assumptions, complete outcome calendar and a frozen model/version.
Retain each failed gate. The prior strict-control exclusion never itself blocks
background membership; it also does not resolve any execution gate.

Treat each origin's two horizons as paired dependent results, not two independent
events. Cross-origin shared crises and overlapping information/target windows
must be grouped before resampling or splitting. Report calendar-year blocks and
crisis overlap identifiers; four years are only four possible annual blocks and
are not an adequate precision argument. The 2023-2024 compound crisis crosses
years, so annual blocks alone do not guarantee independence. No default daily-row
bootstrap or significance claim is permitted. Keep the purposive event stratum
separate and flag overlap with calendar windows to prevent double counting.

## Before fitting

Freeze the outcome vintage/calendar, historical scenario builder, accepted input
mappings, model commit, paired-eligibility manifest, chronological split/purge
rules and practically meaningful improvement threshold. Do not choose them from
the pilot errors. No held-out sample is assigned here: these historical years
have already been explored. A later prospective phase needs a separately dated
protocol and genuinely future origins. BCS weights, confidence and escalation
remain experimental/UNASSESSED; public price comparisons do not validate business
losses. Keep PR #6 draft and unmerged.
