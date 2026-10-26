# Physical recovery decisions 0.6

Decision date: 2026-10-22. This amends the custody and availability findings in
0.5; it does not rewrite its original records. Raw sources are retained locally,
not committed. Archive links and digests are in
[archive witnesses](calibration_inventory/archive_witnesses_0_6.csv).

## Resolved archival gaps

- EI 2023 PDF: recovered the July 12, 2023 18:30:21 UTC capture of the same
  `single_3.pdf` URL. The archive SHA-1 digest matches the downloaded payload.
  Printed p17 confirms world 2022 crude-and-condensate production 81.157 million
  barrels/day. Use July 12 as the conservative **available-by** date for these
  exact bytes, not June 26 as proof that this precise edition existed at release.
- EIA route SVG: recovered December 4, 2023 22:16:21 UTC capture, digest verified.
  Its 2022 crude/condensate rows confirm Suez/SUMED 3.6 and Bab el-Mandeb 3.3
  million barrels/day. Current and archived SVG bytes need not match: use the
  archived payload and verified cells, not an assertion of whole-file identity.
- DOE CY2022 PDF: recovered January 18, 2024 23:19:52 UTC capture. Both its archive
  digest and SHA-256 match the previously downloaded report. Its physical stock
  and drawdown figures are authenticated to that capture. Original release day
  remains unknown. The first policy-eligible origin is January 20, 2024; this
  excludes January 1 and earlier origins. Do not backdate to the cover month,
  directory name, PDF creation metadata, or an undated current landing page.

An archive capture is evidence of availability by capture time, not proof of the
first public release or an analyst's actual possession. The uniform two-calendar-
day lag applies to the capture date when it is the content witness. No failed
archive lookup proves that a document did not exist earlier.

## Physical mapping decisions

The two 2022 ratios remain reference-year candidates (4.44% / 4.07%). Custody is
now recovered; global-production versus demand interpretation, cross-publisher
condensate boundaries, serial overlap, canal/pipeline allocation and origin-date
representativeness remain unapproved. No earlier origin may inherit the 2023
publication. The same-period criterion is mandatory; no 1H2023/2022 hybrid.

DOE's 372.1 million barrels are a US physical stock, not its 402.4 million book
inventory. Neither is a globally deployable buffer. Its end-2022 stock is stale
at every origin that clears the newly established archive cutoff. Operational
rates of 4.0/3.6/2.1 million barrels/day describe successive 30-day intervals in
the report's year-end capability case, not an authorized 2024 release schedule.

Additional public-source review did not recover a complete vintage-specific,
disjoint global crude stock panel with operating floors, accessibility and
release constraints. [JODI's current FAQ](https://www.jodidata.org/oil/support/faqs.aspx)
explains that missing country submissions are not filled. The
[IEF December 2024 transparency report](https://www.ief.org/reports/global-oil-inventories-data-report)
discusses underreporting, particularly outside the OECD. These are methodological
context only, not features available at earlier origins. The
[IEA Oil Supply Security methodology](https://iea.blob.core.windows.net/assets/26ec1827-813a-484f-8af9-c6286c477ee5/oil_security.pdf)
uses adjustments and net-import cover for reserve accounting; its general 10%
deduction is not evidence that 90% of each global crude stock is deliverable.
Do not import that convention as an empirical accessibility coefficient.

Disposition: **global physical mappings remain unresolved and excluded**, not
zero-filled, extrapolated from the US, or repaired by fitting prices. Current
35/10-day assumptions are not promoted to historical inputs. This is a bounded
recovery result, not proof that suitable proprietary or governmental data do not
exist. A reduced-market sensitivity study would require a separate amendment
and could not retain the global historical-validation claim.

The executable eligibility decision is now frozen in
[replay rules 0.6](ibif_replay_rules_0_6.md): all 38 windows are blocked. The rule
freeze is a versioned exclusion decision; it is not a completed input bundle or
permission to fit outcomes.
