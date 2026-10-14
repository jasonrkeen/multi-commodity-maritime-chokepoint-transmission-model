# IBIF public market data feasibility

Assessed October 13, 2026, America/Chicago. Retrieval timestamps are recorded in
UTC and may fall on October 14. Scope: the public repository's three validation
anchors, the proposed Brent outcome source, and one potential flow-data family.
This is not a comprehensive historical event search or a calibration run.

**Proceed with dataset design; do not fit yet.** A public Brent history is
accessible. The candidate inventory now has 9 origins and 18 horizon records,
but no complete input bundle has been accepted, so there are zero accepted
calibration ledger rows. This means zero qualified replay
cases, not zero public price observations. The original input CSVs remain intact.

## Proposed outcome source

The [EIA daily Europe Brent Spot Price FOB series](https://www.eia.gov/dnav/pet/hist/RBRTED.htm)
is in nominal USD/barrel. A saved HTML snapshot was parsed independently of the
model. It contains 9,102 numeric observations from May 20, 1987 through October 6,
2026, in 10,235 weekday cells; 1,133 cells are blank. Blank cells include
nonpublication dates and trailing unreported cells, not necessarily data errors.
There were no duplicate parsed dates. The page reports release on October 7,
2026. This is an extraction profile, not a count of independent disruption cases.

The current snapshot corroborates a rounded April 2026 mean of USD 117:
20 numeric daily entries average USD 117.2875. It does not authenticate a
particular historical input vintage or the repository's undated USD 72 baseline.
Do not replace the original baseline with a guessed month.

The source provides outcome-series access, but the following are unresolved:

- Historical availability timestamps and revisions for inputs at each origin.
- A complete observation calendar distinguishing holidays and genuine gaps.
- A versioned extraction policy and verification of the intended source-use and
  redistribution terms before distributing underlying data.
- Eligible event/control origins, input bundles and sufficient independent clusters.
- Benchmark alignment: Brent spot is not an organization invoice, a sour-crude
  spread, global economic exposure or the IBIF composite score.

The HTML snapshot SHA-256 is
`9a2f723bd2a77087b60ca8f87f93e3952657d9ba5ea88a30bef776bec9c5731d`.
Snapshot and extraction evidence are retained outside this source-only PR.

## Existing anchor audit

| Repository anchor | Source finding | Eligibility for this pilot |
|---|---|---|
| `HORMUZ_2026_BRENT`: 72 to 117, April 2026 | The current EIA daily series supports 117 as a rounded monthly mean; the 72 baseline lacks a period. The cited rolling STEO page now displays another release, so it cannot itself prove the August vintage. The August PDF was retrieved, but the exact 72-to-117 pairing was not authenticated there. | Partial corroboration only; not an aligned 30-day event-origin forecast target. Exclude until baseline, dates and vintage are explicit. |
| `HORMUZ_2026_DEMAND`: -1.2 million b/d annual average, 2026 | [August STEO](https://www.eia.gov/outlooks/steo/archives/aug26.pdf), PDF page 19 (zero-based page 18), annual change in world liquids consumption chart, contains -1.2 for 2026 in a forecast presentation. It is not a completed-year observation. | Exclude from realized-outcome labels; retain only as a dated forecast/context item. Also outside the Brent target. |
| `HORMUZ_2026_FERTILIZER`: +35%, first five months of 2026 year over year | [June Food and Nutrition Security Update](https://thedocs.worldbank.org/en/doc/40ebbf38f5a6b68bfc11e5273e1405d4-0090012022/related/Food-and-Nutrition-Security-Update-edition-123-June-2026.pdf), pages 1-2, supports the aggregate statement. Its market outlook is as of June 22; the exact June 30 publication day in the register was not independently established. | Published summary corroborated, not underlying index reconstruction or causal attribution. Outside the commodity and time-window definition of this pilot. |

The [EIA archive index](https://www.eia.gov/outlooks/steo/outlook.php) identifies
August 11, 2026 as the August release. Use its dated PDF rather than the rolling
global-oil URL when referring to that vintage. Likewise, the
[World Bank landing page](https://www.worldbank.org/en/brief/2023/06/09/food-security-update)
now carries a September update; the recovered June PDF is the relevant document.
These source checks do not make the three heterogeneous anchors a training set.

The existing `run_calibration_sensitivity` routine varies four market assumptions
and compares outputs with a catalog Brent band. It does not fit the IBIF adapter
to these three rows. No anchor was silently corrected or promoted to observed
ground truth by this documentation change.

## Source and input inventory

| Item | Verified availability or role | Remaining requirement |
|---|---|---|
| EIA daily Brent history | Numeric history retrieved and profiled | Calendar, outcome freeze, input vintages, terms and event alignment |
| EIA dated STEO archive | August PDF retrieved; forecast context distinguishable | Separate observed estimates from forecasts; no future-vintage inputs |
| World Bank June report | Dated report and relevant fertilizer passage recovered | Not a Brent outcome; disaggregated underlying series needed for any later fertilizer pilot |
| IMF PortWatch | [Primary methodology](https://www.imf.org/-/media/files/publications/wp/2025/english/wpiea2025093-print-pdf.pdf) describes AIS-derived estimates and revisions | Candidate only: no daily chokepoint dataset retrieved/profiled here; verify availability, terms, vintages, commodity mapping and denominator |
| Repository sensor rows | Explicitly synthetic demonstrations | Exclude from empirical sensor-performance training; obtain real paired observations if later needed |
| Repository scenario/commodity parameters | Conditional paths and analyst assumptions | Recover contemporaneous per-origin versions; no automatic reuse as historical inputs |
| Event and control ledger | [Populated feasibility inventory](ibif_event_inventory.md): 9 origins, 18 horizon records, 126 input checks | Zero accepted replays; complete notice screening and historical input recovery before splitting |
| Organization-level losses | Not part of the selected public-market pilot | Separate data agreement and specification for any business-impact claim |

PortWatch's modeled maritime measures would be complementary diagnostics, not
independent proof of a global commodity-loss fraction. Reusing the same AIS data
as both a predictor and its validation target requires explicit dependence checks.

## Decision and immediate handoff

1. Adopt the [draft Brent target definition](ibif_calibration_spec.md) after
   resolving the calendar/alignment policy. Keep the pilot separate from BCS fitting.
2. Expand the populated candidate inventory into a defined notice universe and
   complete the control screen. Preserve all exclusions, including missing vintages.
3. Audit historical input availability and implement an as-of replay policy in a
   separate reviewed change. Do not use realized future duration or interpolated
   future sensor values.
4. Count eligible independent clusters, then determine split dates and precision
   requirements. Do not infer sample adequacy from 9,102 daily prices.
5. Freeze the specification, ledger and evaluation decisions before fitting.

The [event inventory and input availability matrix](ibif_event_inventory.md) now
record candidate dates, dated sources, exclusions and unresolved input families.
A calibrated model, fitted BCS weights and operational thresholds are not supported by the evidence assembled so far.
