# Historical input recovery and control screening

Draft 0.3. Reviewed October 13, 2026, America/Chicago (October 14 UTC).
This extends the [event inventory](ibif_event_inventory.md). It does not change
runtime inputs, fit outcomes, or establish model calibration. PR #6 stays draft.

## Recovery result

- **18 date-specific Brent vintages**: two for each of nine proposed origins.
- **27 inventory values**: nine U.S. commercial crude stocks, nine U.S. strategic
  reserve stocks, and nine OECD commercial crude-and-other-liquids stock values.
- **24 origin-linked exposure/capacity records**, including the December 2023
  table's crude-and-condensate flow values for the three later origins. These
  repeat shared evidence across origins; they are not 24 independent estimates.
- **12 control-window decisions**: all excluded under the explicit, conservative
  incident-free screen below. No incident-free controls were accepted.

The combined source register now has 59 records. Recovery is materially stronger
than the initial current-price snapshot, but **zero complete replay bundles are
accepted**. Exact latest-release cutoffs and model-compatible exposure/inventory
mappings remain unresolved. Other scenario parameters also lack frozen historical
policies. Recovered source facts must not be confused with usable model settings.

## Daily Brent vintages

[ALFRED](https://fred.stlouisfed.org/docs/api/fred/alfred.html) retains historical
versions of FRED observations. The public export returned `DCOILBRENTEU` with a
column label containing the requested vintage date. For every origin, exports
were retrieved for origin date minus two days and minus one day; all labels,
observation dates and numeric values were checked and files hashed. This is
recovery from an official archival mirror, not recovery of original EIA release
files or an intraday publication log.

| Proposed origin | Conservative vintage | Last observation in that vintage | USD/barrel | Previous-day vintage differs? |
|---|---|---|---:|---|
| 2021-01-01 | 2020-12-30 | 2020-12-28 | 50.88 | No |
| 2021-03-27 | 2021-03-25 | 2021-03-22 | 63.89 | No |
| 2021-07-01 | 2021-06-29 | 2021-06-21 | 74.49 | Yes: June 28, 74.78 |
| 2023-01-01 | 2022-12-30 | 2022-12-27 | 82.45 | No |
| 2023-07-01 | 2023-06-29 | 2023-06-26 | 73.86 | No |
| 2023-11-02 | 2023-10-31 | 2023-10-23 | 91.88 | Yes: October 30, 90.73 |
| 2024-01-01 | 2023-12-30 | 2023-12-25 | 80.23 | No |
| 2024-02-03 | 2024-02-01 | 2024-01-29 | 83.99 | No |
| 2024-07-01 | 2024-06-29 | 2024-06-24 | 86.75 | No |

Every row is a candidate information set, **not an approved baseline**. The two-day
rule conservatively avoids treating a whole U.S. calendar day's vintage as
available at an earlier UTC midnight. It sacrifices freshness. The previous-day
files expose the boundary sensitivity; their intraday release times were not
authenticated. Identical adjacent vintages do not prove there was no faster EIA
publication channel. The draft specification still calls for the last demonstrably
available price; adopting a fixed ALFRED channel/lag would require an explicit
protocol amendment before replay, rather than silently relabeling these values.

The export's observation calendar is preserved, including dates that may be
holidays. No interpolation, holiday deletion or replacement with today's series
was performed. Observation date, vintage date and retrieval time are distinct.
Per-file URLs and hashes are in
[recovered price vintages](calibration_inventory/recovered_price_vintages.csv).

## Inventories and exposure

The [EIA weekly archive](https://www.eia.gov/petroleum/supply/weekly/archive/)
links dated report pages and their Table 1 PDFs. The latest pre-origin report
was recovered for each date; Table 1's current-week commercial crude and SPR
columns were extracted. Release dates are December 30, 2020; March 24 and June 30,
2021; December 29, 2022; June 28, November 1 and December 28, 2023; January 31 and
June 26, 2024. June 30, 2021 and November 1, 2023 fall on the previous calendar
day: the inventory table flags their intraday cutoff uncertainty instead of
assuming an exact release hour. All other selected reports clear the conservative
two-day date rule.

For example, the March 24 report gives 502.7 million barrels of commercial crude
and 637.8 million barrels in the SPR for the week ending March 19. The January 31,
2024 report gives 421.9 and 357.4 million barrels respectively for January 26.
These are **U.S. stock estimates**, not global reserves available to every user.
SPR stocks are not an announced release schedule or fully deployable capacity.

Table 3a of each previously recovered STEO supplies an OECD commercial-stock
value for the latest completed quarter before its release. The March 2021 vintage
reports 3,033 million barrels for 2020 Q4; January 2024 reports 2,843 million for
2023 Q4. Past periods can still be estimated or revised. These include other
liquids and are not global crude-only stocks. The source's estimate/forecast
distinction has not been erased by calling a quarter completed. No stock-to-days
conversion was approved: a matching geography, commodity denominator and accessible
buffer definition are required. Each of the 27 values has a period, page/column
locator, source hash and mapping status in the
[inventory table](calibration_inventory/recovered_inventory_inputs.csv).

For exposure, the 2019 EIA publication supplies an older seaborne-petroleum share
and SUMED nameplate capacity. Those are dated anchors, not current route weights.
The [December 2023 table](https://www.eia.gov/todayinenergy/images/2023.12.04/chart2.svg)
provides first-half-2023 crude-and-condensate flows of 4.9 million barrels/day
through Suez/SUMED and 4.5 through Bab el-Mandeb. This source was available for the
January, February and July 2024 origins only. It cannot be backdated to Suez 2021
or Panama November 2023. The serial corridor must not be added twice. Canal versus
pipeline, crude versus condensate, period and global denominator mismatches remain
unresolved. No exact values were inferred by digitizing the older bar chart.

The [exposure table](calibration_inventory/recovered_exposure_inputs.csv) records
these constraints. Panama still lacks a recovered crude-specific global route
share; capacity and LNG/LPG traffic cannot substitute for it.

## Completed screen of the existing controls

`incident-free-draft-0.3` makes the earlier informal term “quiet” explicit:
exclude a window if a primary authority/carrier source documents a merchant
attack, detention, navigation incident requiring salvage/tow assistance, or
physical transit restriction in Suez, Bab el-Mandeb/Red Sea, Panama, or the
Hormuz/Gulf of Oman approaches. Screen from 30 days before the origin through
the target end; a contemporaneous official security notice within this interval
also fails the washout. Cargo need not be crude. This broad design choice is
made after inspecting these candidate incidents and before fitting, **not a
preregistered material-flow rule**. This exploratory screen cannot support claims
that the control-selection procedure was independent of incident discovery.

The bounded source families are SCA, ACP, EIA, carrier notices, IMO, and national
government maritime/security statements. Search stops for exclusion once an
adequate positive witness is verified. Therefore completion means every existing
candidate has an exclusion decision, not that all notices or incidents have been
enumerated. Search failures do not establish a quiet period. Dates were never
selected using stable prices or model errors.

| Control origin (both horizons) | Exclusion witness | Claim boundary |
|---|---|---|
| January 2021 | [Korean foreign ministry](https://www.mofa.go.kr/eng/brd/m_5676/view.do?company_cd=&company_nm=&itm_seq_1=0&itm_seq_2=0&multi_itm_seq=0&page=1&seq=321513&srchFr=&srchTo=&srchTp=&srchWord=&titleNm=): February 2 discussion of nearly month-long Hankuk Chemi detention | Supports January overlap; exact seizure day is not asserted from this release. Suez also overlaps the 90-day target. |
| July 2021 | [UK government](https://www.gov.uk/government/news/uk-condemns-deliberate-attack-on-oil-tanker-by-iran): July 29 attack on Mercer Street off Oman | Attack in the approach region, not a demonstrated Hormuz closure |
| January 2023 | [SCA](https://www.suezcanal.gov.eg/English/MediaCenter/News/Pages/SCA_9-1-2023.aspx): January 9 GLORY machinery failure and assisted transit | Authority explicitly says navigation was uninterrupted; not evidence of material crude loss |
| July 2023 | [EIA October account](https://www.eia.gov/todayinEnergy/detail.php?id=60842): daily vessel limit from July 30 | Within both target windows; published later, usable only as a screening label |
| January 2024 | [EIA February account](https://www.eia.gov/todayinenergy/detail.php?id=61363): Red Sea attacks, December flow reductions and January avoidance | Retrospective contamination evidence, not an input available January 1 |
| July 2024 | [IMO June 14 statement](https://www.imo.org/en/mediacentre/pressbriefings/pages/merchant-vessel-tutor.aspx): current TUTOR attack aftermath | Security notice inside the 30-day washout; no July flow path or exact attack day inferred |

All 12 windows fail this incident-free definition. A narrower **material crude-flow
control** definition could yield different decisions, especially for GLORY, and
would require a separately frozen materiality rule and new screening. The present
result must not be described as twelve proven oil-supply disruptions. Later
publication evidence remains `RETROSPECTIVE_LABEL_ONLY`; it never enters an earlier
feature bundle. [Control screen](calibration_inventory/control_screen.csv) retains
each window, witness, screening interval and interpretation limit.

## Remaining gate

The first public pilot still lacks accepted quiet controls and enough eligible
independent disruption cases. Next define the price publication channel/cutoff,
map regional stocks and flows to explicitly justified model assumptions, and
expand the calendar control pool under the chosen rule. Freeze those choices,
the outcome calendar, replay policy, splits and acceptance criteria before fitting.
Do not relax exclusions merely to produce a successful backtest. No BCS, confidence
or business-impact calibration is supported by this recovery.

Direct retrieval failures are retained in local manifests: an initial ALFRED
request form timed out, while bounded historical exports succeeded; ONI and Navy
files returned 403; the Korean ministry page had a TLS failure locally but its full
dated text was accessible through the web reader. Failed files are not claimed as
downloaded. Original downloaded reports and price histories remain outside this
source-only PR; it contains curated evidence records and provenance metadata.
