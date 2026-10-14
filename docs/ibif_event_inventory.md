# IBIF event/control inventory and forecast-date availability

Draft 0.2, reviewed October 13, 2026 (America/Chicago; retrievals October 14 UTC).
This is a **retrospective feasibility inventory**, not a fitted backtest or a
record of forecasts actually issued. PR #6 remains draft and unmerged.

## Result

The inventory contains **9 proposed origins, 18 horizon records, 126 input-family
checks and 17 source records**. Three disruption origins cover Suez, Panama and
the Red Sea. Six calendar-selected control candidates are retained, including
failed controls. **Zero records qualify for replay**: no complete, dated input
bundle or daily no-change-baseline vintage has been authenticated.

Seven horizon records are excluded as quiet controls; five await a complete
control screen; six disruption records are blocked on inputs. These categories
are not missing observations encoded as zero. No target means, model errors,
fitted weights, sample-size claims or calibration results were computed.

## Scope and selection

This first, purposive inventory covers three named cases encountered during
feasibility research: the 2021 Suez blockage, 2023 Panama drought restrictions,
and the 2023-24 Red Sea disruption. It is not an exhaustive notice universe,
preregistered sample or unbiased selection of all disruptions. Notice discovery
used carrier/authority publications and EIA reporting; no price-error filter was
used. Broader event discovery and a fixed notice-universe rule remain required
before fitting. The existing 2026 anchors remain excluded for the reasons in
[data feasibility](ibif_data_feasibility.md); they have not been silently replaced.

Control candidates are January 1 and July 1 of each event-origin year (2021,
2023, 2024), at 00:00 UTC. All six are retained regardless of contamination.
This is a transparent design choice made now, not historical preregistration.
Screening is incomplete and spans the target horizon as well as the origin;
an origin can be eligible for one horizon and unsuitable for another.

| Origin UTC | Candidate | Contemporaneous documentation identified | Decision |
|---|---|---|---|
| 2021-01-01 | Calendar control | December 2020 STEO, released December 8 | 30-day screen pending; 90-day window contains Suez blockage |
| 2021-03-27 | Suez blockage | MSC March 25 advisory; March STEO released March 9; EIA 2019 route context | Notice supports closure; remaining duration, crude loss and daily baseline unresolved |
| 2021-07-01 | Calendar control | June STEO, released June 8 | Both horizons need a complete quiet-period screen |
| 2023-01-01 | Calendar control | December 2022 STEO, released December 6 | Panama onset within target may contaminate; exact restriction timing unresolved |
| 2023-07-01 | Calendar control | June STEO, released June 6 | Exclude as quiet: retrospective EIA account places Panama restrictions from January 2023 |
| 2023-11-02 | Panama restriction phase | ACP October 30 advisory and EIA October 31 article; October STEO released October 11 | Announced plans available; realized throughput and Brent mapping unresolved |
| 2024-01-01 | Calendar control | December STEO, released December 12; EIA December 4 route context | Exclude as quiet: overlapping Panama/Red Sea disruption |
| 2024-02-03 | Red Sea, late-crisis | EIA February 1 assessment; January STEO released January 9 | Dated flow context available; not an onset forecast or mapped supply-loss input |
| 2024-07-01 | Calendar control | June STEO and June rerouting article, both June 11 | Exclude as quiet: documented continuing rerouting |

The 2023-24 Panama and Red Sea cases are provisionally grouped together because
their crises overlap and rerouting connects them. They are **not three proven
independent event clusters**. The January 2021 90-day control shares the Suez
cluster. Grouping is retrospective evaluation metadata, never an input feature.
Even excluded controls remain visible. No train/validation/test split is assigned.

## What the source dates establish

The [EIA archive](https://www.eia.gov/outlooks/steo/outlook.php) identifies the
release dates of all nine selected monthly outlooks; each PDF was retrieved and
its opening market discussion inspected. These were the latest monthly releases
listed before the respective origins. They establish dated market context, not
the latest daily Brent print, a complete historical parameter bundle, or the
original bytes seen by a forecaster. Monthly estimates, annual projections and
realized daily observations must remain distinct.

The [MSC notice](https://www.msc.com/en/newsroom/customer-advisories/2021/march/suez-canal-blockage)
is dated March 25 and records the vessel still obstructing transit at 18:00 CET.
That is a status observation time, not a verified publication timestamp. The web
reader exposed the advisory; direct download returned HTTP 403, so no original
HTML hash is claimed. The [2019 EIA context](https://www.eia.gov/todayinenergy/detail.php?id=40152)
predates the Suez origin but combines canal/pipeline and petroleum categories:
it cannot simply become a 2021 global crude exposure weight.

The [ACP A-48-2023 notice](https://pancanal.com/wp-content/uploads/2023/01/ADV48-2023-Reduction-in-Transits-Due-to-the-Ongoing-Deficit-in-Precipitation-in-the-Canal-Watershed.pdf),
page 1, is dated October 30, despite `2023/01` in its URL. Its scheduled booking
limits are announced plans, not realized vessel counts. The
[October EIA article](https://www.eia.gov/todayinEnergy/detail.php?id=60842)
provides energy-shipping context dominated by LPG. Neither source supplies a
Brent-specific global supply-loss fraction. Its retrospective January restriction
account flags controls; it is not admitted as an input at January or July origins.

The [February Red Sea assessment](https://www.eia.gov/todayinenergy/detail.php?id=61363)
provides dated route and flow information, with reporting lag. Its price example
is not demonstrably the most recent daily price available at February 3.
[December route context](https://www.eia.gov/todayinenergy/detail.php?id=61025)
predates the January control. The
[June rerouting article](https://www.eia.gov/todayinenergy/detail.php?id=62263)
supports rejecting July as quiet but is forbidden at the February origin.
Later reports may support contamination labels only; they cannot supply earlier
forecast features. None of these sources establishes the absence of other shocks.

## Cutoff and missing-data rules

Publication times are date-only. For the three event origins, the proposed cutoff
is no earlier than 00:00 UTC two calendar days after the latest selected notice
date. This conservative design allows a full local publication day to elapse;
it is not proof of an exact posting time or unchanged page history. The Suez
origin is March 27, Panama November 2, and Red Sea February 3. No same-day
publication-time precision has been invented. Monthly reports are comfortably
before all cutoffs; current retrieval time never substitutes for release time.

Target dates follow the current draft specification: origin date +1 through
origin date +H inclusive. Both H=30 and H=90 are recorded. Outcomes, expected
observation counts, exact UTC event/publication timestamps, replay model commit
and input-manifest hash remain blank where unverified. Source date granularity
and publication-date evidence live in the linked source register. Blank means
unresolved or not applicable, never zero. These are metadata tables, not runtime
input CSVs; none should be loaded into the model.

The availability matrix distinguishes dated documents from usable numeric model
inputs. Missing families include daily baseline vintages; mapped route exposure;
inventory denominators; severity/duration/recovery assumptions; dependency and
lag parameters; policy/balancing schedules; elasticities/substitution; crude-grade
and logistics parameters; and scenario priors. Synthetic sensors stay excluded.
Business exposure and impact-scale parameters remain outside this price pilot.
The 2026 repository parameters are not historical observations.

## Reviewable files and next gate

- [Origins](calibration_inventory/origins.csv): one row per proposed cutoff.
- [Event/control ledger](calibration_inventory/event_control_ledger.csv): 18
  records using the existing 33-column schema, with explicit nonacceptance reasons.
- [Input availability](calibration_inventory/input_availability.csv): 14 families
  at each of 9 origins, with source IDs, dates, locators and recovery actions.
- [Sources](calibration_inventory/sources.csv): URLs, dates, current retrieval
  hashes where available, and historical-vintage limits.
- [Cutoff exclusions](calibration_inventory/cutoff_exclusions.csv): concrete
  future-information rejection examples.

First recover daily-price release vintages and contemporaneous crude exposure /
inventory denominators for Suez and Red Sea. Then define and review a fixed
assumption policy for parameters that were never observed. Expand and complete
the notice/control screen, resolve the observation calendar, count independent
eligible clusters, and freeze splits and acceptance criteria before fitting.
Panama should remain a mapping feasibility case unless a defensible Brent channel
is established. A reconstructed historical scenario must be labeled as such.
