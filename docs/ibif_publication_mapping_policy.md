# Publication cutoffs and model mappings: policy 0.4

Adopted for pilot preparation on October 22, 2026. This is an explicit amendment
to draft 0.1, not a claim of historical preregistration or calibrated parameters.
The original 0.3 recovery tables remain unchanged. Runtime inputs remain unchanged.

## Publication policy: resolved by specifying the information channel

Use ALFRED `DCOILBRENTEU` as the sole baseline-price input channel. For an issue
timestamp at UTC midnight on date D, request the vintage dated D minus two
calendar days. Select the latest numeric observation in that vintage, with
observation date no later than the vintage date. Record URL, vintage header,
observation date, value, retrieval time and SHA-256. No interpolation, holiday
deletion, forward-dated observations or fallback to the current revised series.
Missing export, header mismatch or no numeric observation means BLOCKED_PRICE.
Record price age in calendar days; more than 14 days means BLOCKED_STALE_PRICE.
Fourteen days is a conservative analyst-selected pilot guardrail, not an estimated
publication delay or an outcome-tuned optimum. Do not silently drop blocked rows.

This replaces the ambiguous freshest-price-across-all-channels baseline with
**last available in the prescribed lagged ALFRED vintage**. Both the model and
no-change comparator must use the same selected baseline. Previous-day vintages
remain timing diagnostics only; do not choose the more accurate-looking price.
The nine original selections are in
[publication decisions](calibration_inventory/publication_decisions_0_4.csv).
All nine clear this policy's date, header and age checks; this does not approve
the other inputs or the full replay. Expanded controls are excluded before price
retrieval; no new price series are required to justify their exclusions.

[ALFRED documentation](https://fred.stlouisfed.org/docs/api/fred/alfred.html)
supports vintage selection and revision tracking. A date-specific export does
not supply an authenticated intraday EIA publication log. We make no assertion
that these are the freshest EIA prices or that the analyst actually issued a
forecast then. This remains an archival, channel-constrained reconstruction.

For all other date-only reports, require publication date <= D minus two days.
This is a deliberately uniform lag: even the end of that date at UTC-12 precedes
the UTC origin. It does not authenticate a backdated or subsequently edited page.
Require the dated archival file and its source provenance; mutable present-day
pages alone cannot prove historical feature content. Preserve estimate/forecast
labels. Do not substitute an observation period for publication date. Exact
timestamps, if later recovered, do not override this version's lag; a faster
policy requires a versioned amendment applied to every origin.

Choose the most recent eligible report in the inspected archive, not the most
recent report whose observations predate the origin. Hence June 30, 2021 and
November 1, 2023 WPSR reports are excluded at July 1 and November 2 origins.
Recovered June 23, 2021 and October 25, 2023 Table 1 reports replace those two
selections for descriptive regional-stock evidence only. Their current-week
commercial/SPR values are respectively 459.1/623.9 and 421.1/351.3 million barrels.
The resulting 27 selections are in
[stock decisions](calibration_inventory/stock_decisions_0_4.csv).
The current [WPSR schedule](https://www.eia.gov/petroleum/supply/weekly/schedule.php)
is not used to invent historical publication timestamps. All nine STEO releases
already clear the lag. Their completed-quarter stocks remain potentially revised
estimates, not final observations or known deployable reserves.

These decisions resolve the pilot cutoff **rule**, not missing historical
authentication. Outcome vintages/calendar completeness are a separate gate and
are not changed here. Later control-screening evidence is always label-only.

## Exposure mapping: use compatible physical units and scope

The inspected `maritime_chokepoint/model.py` multiplies `route_share_global` by
disruption severity, applies rerouting/substitution, takes a maximum within a
route group, then a bounded union across groups. A compatible proposed mapping is
`route_share_global = Q_route / Q_global`, where both are unique commodity flows
in barrels/day for the same reference period and commodity definition, documented
before the cutoff. Transit counts, capacity, seaborne shares and global shares
are different quantities. Publication eligibility alone does not validate them.

| Recovered evidence | Defensible use | Decision for the present crude model |
|---|---|---|
| 2017 seaborne petroleum share published in 2019 | Dated contextual anchor | Reject direct conversion to global crude share: denominator, product scope and age differ |
| SUMED 2.8 million b/d nameplate capacity | Physical capacity ceiling | Reject as realized throughput, incremental spare bypass or an independent additive route |
| 1H2023 Suez/SUMED crude+condensate 4.9 million b/d | Combined corridor flow at later eligible origins | Conditional only: need compatible global denominator and crude/condensate scope; canal-only event also needs canal/pipeline split |
| 1H2023 Bab el-Mandeb crude+condensate 4.5 million b/d | Strait flow at later eligible origins | Conditional only: same denominator/scope issue; do not add serial cargo again |
| Panama all-vessel restrictions / LPG-heavy evidence | Event and capacity labels | Reject as crude global route share; commodity-specific flow is missing |

Sources: the dated [2019 EIA article](https://www.eia.gov/todayinenergy/detail.php?id=40152)
and [December 2023 EIA flow table](https://www.eia.gov/todayinenergy/images/2023.12.04/chart2.svg),
with origin-specific provenance in the preserved recovery tables. The 2023 flows
are eligible only for January, February and July 2024 among the nine original
origins. Do not backdate them. A later vintage cannot replace an earlier one just
because the reference period is earlier.

For an explicitly redefined crude-plus-condensate scenario, a matched positive
global crude-plus-condensate denominator would make `4.9/Q_global` and
`4.5/Q_global` dimensionally valid reference-period shares. It would not establish
current flows at each origin or a crude-only calibration. We have not recovered
and approved that matched denominator here. For a canal-only event the affected
share lies between zero and the combined corridor share absent a split; that
trivial bound is insufficient for a point forecast. The model's group maximum
avoids adding serial routes, but does not recover actual cargo overlap. Keep
Suez/SUMED and Bab el-Mandeb in one route group; never sum 4.9 and 4.5 as unique
global supply. Nameplate capacity may already serve baseline cargo and cannot
also be counted as fully free rerouting capacity.

## Inventory mapping: effective global-demand days, not regional days

The model reduces commercial inventory by a daily deficit fraction and strategic
inventory by its release fraction. Their dimensional interpretation is days of
the same global commodity market used by supply loss. A conditional mapping is
`commercial_inventory_days = sum(accessible_fraction * max(stock - operating_floor, 0)) / Q_global`.
Stocks are barrels; Q_global is barrels/day; disjoint geographic/ownership pools
must not overlap. Accessibility, minimum operating stocks, grade, location and
delivery timing require evidence. For strategic stocks use disjoint deliverable
barrels divided by the same Q_global, **and** an independently justified release
rate, start, ramp and duration. A stock total is not permission or capacity to
release it immediately. Do not fit these choices to observed Brent errors.

| Stock series | Accepted interpretation | Rejected substitution |
|---|---|---|
| U.S. commercial crude excluding SPR | Published regional estimate | Global accessible buffer; U.S. days-of-supply treated as global days |
| U.S. SPR crude | Regional strategic holdings | Automatic announced release or globally deliverable inventory |
| OECD commercial crude and other liquids | Broader regional stock estimate | Crude-only global inventory; addition to U.S. commercial stocks already inside OECD |

No numerical global inventory mapping is approved. Adding non-OECD stocks would
still require matching definitions and accessibility; missing stocks are not
zero. Even `U.S. stocks / global demand` is only a gross contribution from that
region, not total effective buffer. It is not a lower bound on deliverable global
stocks without evidence of accessibility. Current crude settings of 35 commercial
and 10 strategic days remain scenario assumptions, irrespective of their legacy
`calibrated_assumption` CSV label; this audit does not empirically validate them.

Commercial draw occurs **after** the contemporaneous price calculation and feeds
physical shortage/lagged effects. Strategic release occurs **before** price and
reduces the net gap. Brent-only fitting therefore cannot identify the commercial
buffer from this implementation's price path. It also cannot validate gross
business-impact dollars, inventory stress dimensions or initial combined buffers.
Retain dollar-scale assumptions separately; rebasing price does not by itself
justify annual market-value/downstream exposure values.

## Decision and next gate

The cutoff policy is now explicit and applied to the nine recovered origins.
The mapping rules are justified against the actual equations, with incompatible
proxies rejected. **Zero complete replay bundles are accepted.** Missing compatible
flow denominators, deliverable stock parameters, historical scenario assumptions,
outcome calendar, splits and acceptance criteria still prevent fitting. If those
cannot be sourced, a clearly labeled scenario sensitivity exercise is possible,
but it must not be promoted to historical forecast validation.
