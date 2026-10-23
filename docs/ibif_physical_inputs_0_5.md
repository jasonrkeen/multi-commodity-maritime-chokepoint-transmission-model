# Physical-input recovery 0.5

Status: reference-year candidates and partial inventory evidence; no runtime
parameters changed, no replay accepted, no outcome fitting performed.

## Exposure

The [EIA December 4, 2023 chart](https://www.eia.gov/todayinenergy/detail.php?id=61025)
reports 2022 crude-and-condensate flows of 3.6 million barrels/day through
Suez/SUMED and 3.3 through Bab el-Mandeb. The [EI 2023 Review](https://energyinst.org/__data/assets/pdf_file/0004/1055542/EI_Stat_Review_PDF_single_3.pdf),
printed p17 (PDF p19), reports world 2022 crude-and-condensate production of
81.157 million barrels/day. Its separate commodity table excludes NGLs;
methodology p56 includes lease/gas condensates requiring refining.
[EI's dated release account](https://knowledge.energyinst.org/new-energy-world/article?id=138000)
identifies June 26, 2023 publication. Direct EI download returned 403; values
are web-readable, without locally authenticated PDF bytes or a historical capture.

Matched-period ratios are 3.6/81.157 = **4.44%** and 3.3/81.157 = **4.07%**.
These are reference-year production shares, not seaborne-trade shares or
current demand shares. CSV arithmetic retains precision for reproduction,
not measurement precision. Cross-publisher condensate definitions remain a
harmonization limitation. The jointly available date is December 4, 2023;
policy 0.4 first permits a December 6 origin. Thus only the four 2024 quarterly
origins (eight windows) pass this publication-date gate; all still fail full
execution eligibility. Earlier origins cannot inherit these data retroactively.

Do not mix 1H2023 route flows with this annual 2022 denominator. Do not add the
two route shares: serial traffic overlaps. The current route-group maximum is
an approximation, not cargo-level deduplication. Suez/SUMED is a combined corridor,
not canal-only exposure or evidence of spare bypass capacity. Before adoption,
freeze the market definition and stale-input rule, obtain period-matched earlier
vintages, resolve canal/pipeline allocation and authenticate source custody.

## Inventory and release constraints

The [DOE CY2022 report](https://www.energy.gov/sites/default/files/2023-12/SPR%202022%20Annual%20Report%20to%20Congress.pdf)
Table4 (pp14-15) distinguishes 372.1 million physical barrels from 402.4 million
book barrels including receivables. Figure4 (p18) gives operational drawdown
rates of 4.0, 3.6 and 2.1 million barrels/day across successive 30-day intervals,
conditional on market acceptance. These are dated US capabilities, not global
usable stocks or current release promises. The October 2023 cover and December
URL directory do not establish public availability. All DOE facts remain
excluded from historical cutoff-qualified inputs pending a dated release witness.

Compatible accounting requires separate disjoint commercial and strategic stocks,
commodity coverage, operational floors, accessible fractions, delivery constraints,
release authorization and release timing. Normalize usable barrels by the same
market flow used for exposure; normalize release rates separately. Book receivables
are not physically available stocks. Do not add US stocks to an OECD total that
already includes them. Do not replace missing global data with zero or extrapolate
US inventory days globally. No numerical global inventory mapping is approved.

The model applies strategic release before price formation but commercial draws
after contemporaneous price formation. Brent-only loss cannot identify the latter
buffer; physical shortage/stock outcomes and a model-structure review are needed.
The legacy 35/10-day assumptions remain unvalidated. Annual market value also
requires separate evidence; price calibration does not validate business dollars.

## Evidence and next gates

`calibration_inventory/physical_facts_0_5.csv` contains eight curated source facts;
`exposure_candidates_0_5.csv` contains two derived candidates. Existing regional
stock decisions remain preserved. Download hashes identify current retrieved bytes,
not historical custody. Raw reports remain outside Git and the source-only package.

1. Recover cutoff-qualified earlier global production/route vintages and resolve
   the commodity/corridor definitions before accepting exposure parameters.
2. Recover disjoint usable commercial/strategic stock coverage and delivery limits;
   otherwise predeclare a partial-region sensitivity design, not a global estimate.
3. Freeze historical notice coverage, scenario construction and outcome vintage;
   complete eligibility and dependence ledgers before any paired replay or fitting.

Background membership is defined separately in `ibif_background_design_0_5.md`.
All 32 calendar windows are retained and NOT_RUN. Historical strict exclusions
remain diagnostic evidence. No quiet-control, causal or prospective claim follows.
