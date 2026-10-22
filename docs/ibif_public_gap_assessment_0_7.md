# Public-data gap assessment 0.7

2026-10-22 evidence supplement to freeze 0.6. No frozen rule, eligibility row,
model code or runtime input changed. **All 38 windows remain BLOCKED_NOT_RUN.**
The [12-row gap matrix](calibration_inventory/public_gap_matrix_0_7.csv) distinguishes
resolved source/definition questions from partial physical inputs and gaps not
recovered in this bounded search. Not recovered does not mean impossible or
unavailable from every public, commercial or governmental source.

## Inventory: what public data can resolve

The already recovered 27 regional stock selections remain useful observations.
New custody evidence authenticates the [JODI questionnaire](https://www.jodidata.org/_resources/files/pages/jodi-oil-questionnaire/extended-jodi-questionnaire.pdf)
to July 30, 2014. Page2 defines crude as including lease condensate and excluding
NGL; closing stocks include government as well as industry holdings. Therefore
JODI closing stocks cannot be relabeled commercial or added to separate SPR
holdings without an ownership reconciliation. Its detailed product definitions
also distinguish plant condensate from condensate commingled with crude; an EI
crude-and-condensate crosswalk is not automatically exact. The questionnaire has
inconsistent stock-change sign wording between short and long definitions;
this assessment uses stock levels only and does not infer changes from that form.

Public regional gross levels, definitions and selected government release notices
are recoverable. They do not establish a complete historical global usable-stock
panel. Operating floors, accessibility, grade/location constraints and disjoint
ownership remain missing. The DOE capability evidence recovered in 0.6 is a dated
engineering case, not an origin-specific release authorization or delivered flow.
A regional stock diagnostic can be specified using public data; replacing the
global buffer requires either additional evidence or a separately approved model
scope change. Do not silently apply a universal haircut or treat missing stocks
as zero. No inventory parameter is promoted here.

## Route allocation: public anchors, incomplete cargo accounting

The [SCA circular](https://www.suezcanal.gov.eg/English/Navigation/NavigationCirculars/Pages/PC_12-11-2019.aspx)
was recovered from a December 14, 2019 capture. It describes VLCCs unloading part
of their cargo into SUMED before transiting the canal. This establishes a combined
logistics pattern, not a quantitative cargo split. The circular's stated validity
ends June 30, 2020; it is not evidence of an active 2021 or 2024 tariff or capability.
Public vessel counts or deadweight cannot recover crude quantities by route.

A [March 26, 2021 IEA commentary](https://www.iea.org/commentaries/suez-canal-closure-highlights-asias-growing-dependence-on-eastward-oil-flows)
provides canal-only directional crude estimates of about 1.1 million b/d eastbound
and 0.4 westbound. This demonstrates that public canal-specific anchors exist,
but the article misses the March 25 cutoff for the fixed March 27 origin. The exact
averaging period is not established here; no global share is computed. The origin
is not moved to admit this evidence. The IEA's 2.5 million b/d SUMED capacity also
differs from the earlier EIA 2.8 figure; neither is adopted as free spare capacity.

The [2019 EIA article](https://www.eia.gov/todayinenergy/detail.php?id=40152)
contains older direction/product charts, including separate pipeline evidence.
A current chart SVG was retrieved, but no exact numeric canal/SUMED allocation
was extracted. Older chart points cannot resolve later cargo matching, operational
availability or grade constraints. Combined 2022 reference-year ratios stay as
candidates only. Do not subtract unlike periods or infer spare bypass as nameplate
minus an unrelated flow estimate. Serial Bab/Suez overlap still needs cargo-level
accounting or a separately declared bounding model.

## Historical scenario inputs: two custody gaps closed

Four new archive payloads were downloaded and matched to their CDX SHA-1 digests;
SHA-256 values and capture URLs are in the
[archive witness ledger](calibration_inventory/public_archive_witnesses_0_7.csv).

- **Panama:** A-48 dated October 30 was captured October 31, 2023 at 20:48:34 UTC.
  The archived PDF matches the previously recovered file. It clears the two-day
  source cutoff for November 2. Its page 1 prose gives 24 booking slots starting
  November 7, while the page 1 final heading and page 2 table retain 25 through
  November 7 and start 24 on November 8. Both rendered pages were checked. Keep the
  conflict unresolved; no cutoff-qualified correction chain was recovered.
  Other announced totals are transcribed in the facts ledger, not converted to
  crude flow. Even a corrected slot schedule would not determine severity.
- **Red Sea:** EIA's February 1, 2024 report was captured that day at 13:55:56 UTC,
  qualifying for February 3. It reports December crude transit 18% below the
  January-November average. This is a lagged route-flow observation, not global
  supply destruction, a daily capacity measure or a future duration forecast.
  Diversions, cargo mix and timing prevent automatic assignment of severity 0.18.
- **Suez:** the exact MSC notice URL returned no CDX record through March 25, 2021;
  current direct retrieval returned 403. This is a bounded negative search, not
  proof no contemporaneous notice exists. Existing date-labeled evidence remains
  distinct from authenticated historical bytes.

The [six fact rows](calibration_inventory/scenario_facts_0_7.csv) preserve the two
conflicting Panama values, three other announced totals and the Red Sea statistic.
No future actual reopening, later advisory or realized duration enters a scenario.
Complete notice coverage and remaining-duration distributions are not recovered.

## Practical disposition

1. Public-data work can proceed on regional gross-stock diagnostics and route-flow
   observations, with vintage, ownership and commodity checks. These are useful
   descriptive validation targets, not a substitute global usable inventory.
2. Panama custody is resolved; its November 7 conflict and crude mapping remain
   open. Red Sea custody/magnitude is partially resolved; future response remains
   unknown. These source-level advances do not change replay eligibility.
3. Pause attempts to manufacture a single calibrated global point path from
   aggregates. The next defensible research design is an explicitly bounded,
   conditional sensitivity study, or acquisition of the missing operational data.
   Such a change needs a new protocol before execution and cannot inherit a claim
   of historical forecasting accuracy. No fitting or model run is introduced here.

Freeze 0.6 remains byte-for-byte intact. This evidence supplement records progress
and limits without weakening its gates. PR #6 stays draft and unmerged.
