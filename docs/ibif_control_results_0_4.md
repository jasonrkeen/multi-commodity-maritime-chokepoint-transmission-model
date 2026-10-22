# Expanded control screening: results 0.4

Reviewed October 22, 2026. The [protocol](ibif_control_protocol_0_4.md) was committed
as `b0a39c7d23e016a069fb1967f9a0c899db269541` before the additional source search.
Its file SHA-256 is
`3a3b1734ebe11df5d9b524aa54c3c98610f3f2a1b7751664c42a5de9273a877b`.
This is a fixed historical exploratory screen, not a blinded or prospective study.
Prior incidents were already known. No price outcomes or model errors were used.

## Result

The calendar universe is now 16 origins / 32 horizon windows, up from six / 12.
The [complete register](calibration_inventory/control_screen_0_4.csv) retains every
quarter start of 2021-2024 and both horizons. **All 32 windows have a verified
positive exclusion witness; zero controls are accepted.** The earlier twelve
decisions remain unchanged in `control_screen.csv`; the new register rechecks
their identical intervals against the fixed rule. Three disruption origins
remain separate in the original event ledger. The combined candidate universe
therefore has 19 distinct origins and 38 horizon records, not 38 independent events.

| Added origin | Witness inside both screening intervals | Source locator |
|---|---|---|
| April 1, 2021 | March 25 ongoing Suez blockage, inside washout | Preserved MSC advisory, `msc_suez` |
| October 1, 2021 | September 9 completed lane maintenance | ACP A-39-2021, p.2 |
| January 1, 2022 | January 3 completed lane maintenance | ACP A-03-2022, p.2 |
| April 1, 2022 | April 4 completed lane maintenance | ACP A-17-2022, p.2 |
| July 1, 2022 | July 7 completed lane maintenance | ACP A-27-2022, p.2 |
| October 1, 2022 | September 20 completed lane maintenance | ACP A-33-2022, p.2 |
| April 1, 2023 | March 5 MSC ISTANBUL tug-assisted refloating | SCA dated statement |
| October 1, 2023 | September 7 completed lane maintenance | ACP A-45-2023, p.2 |
| April 1, 2024 | March 4 current Galaxy Leader detention notice | IMO dated statement |
| October 1, 2024 | September 16 completed lane maintenance | ACP A-38-2024, p.2 |

All source URLs and publication dates are in the register and `sources.csv`.
Publication dates of retrospective accounts may be later than the origin or
target. They are labels only, never historical features. Completed maintenance
rows, not merely announced or tentative future work, support the seven ACP
decisions. Estimated capacity in those tables is not realized crude throughput.
Do not infer all-vessel closure or material oil losses. SCA explicitly reports
that MSC ISTANBUL did not negatively affect Canal traffic; it still meets the
fixed assisted-transit criterion. The IMO witness describes continuing detention;
we do not infer the initial seizure date from that March statement.

## What the expansion shows

The fixed rule includes physical transit restrictions without an exception for
scheduled maintenance. Seven of the ten added origins fail for that reason.
These are legitimate applications of the broad rule but reveal its poor
suitability for identifying ordinary background market periods. This finding
must not be hidden by calling all exclusions geopolitical or material crude
disruptions. It does not show that quiet oil markets never occur.

The sources were discovered by official-domain queries and the ACP advisory
index, then read at the stated locators. A positive witness stops screening;
other geographies need not be enumerated after exclusion. No window was passed
on search silence. [Search notes](calibration_inventory/control_search_log_0_4.csv)
record discovery paths and rejected leads. This is not an exhaustive incident
census. ACP and SCA direct downloads returned 403 while their full text was
readable through the web reader; those new sources have no invented local-file
hash. The IMO March statement and two replacement EIA Table 1 PDFs were downloaded
and hashed. The source register now has 72 records; the original 59 remain.

## Next methodological decision

Do not keep moving calendar dates until a quiet sample appears. Retain this
failed strict-control design. A separate future protocol can define **background
market origins with measured disruption covariates**, allowing ordinary planned
maintenance without claiming incident absence. It would change the estimand and
must disclose this screen's prior evidence exposure. A narrower material-crude
rule requires commodity-specific flows and a justified numerical threshold first;
vessel counts and maintenance hours alone cannot supply it. Neither alternative
is adopted or fitted in this revision. Existing cases remain unaccepted for
replay under the [cutoff and mapping policy](ibif_publication_mapping_policy.md).

## Verification

All 44 unit tests passed (68.843 seconds). The deterministic 30-day,
zero-simulation contributor smoke run passed with seed 20260810 after installing
the repository's declared dependencies in an isolated local environment; the
first smoke attempt stopped on a missing plotting dependency before model work.
The evidence audit checked 32 interval decisions, nine vintage selections,
27 stock selections, source references/hashes, preserved original rows, protocol
identity, and relative links. No runtime or model-input changes were introduced.
The full 240-day/200-simulation equivalence protocol was not rerun; its earlier
evidence remains attributed to commit `729b193`, not to this documentation update.
