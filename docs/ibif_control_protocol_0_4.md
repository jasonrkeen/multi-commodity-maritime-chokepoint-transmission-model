# Fixed control-screening protocol 0.4

Decision date: October 22, 2026 (America/Chicago). Fix this file and candidate
universe in Git before searching the additional windows. This is a historical,
exploratory protocol, not prospective preregistration: the six earlier control
origins and their incidents are already known. Do not inspect price outcomes or
model errors to select, exclude, rank or replace candidates.

## Universe and interval

Take every quarter-start UTC midnight (January, April, July, October 1) in
2021 through 2024 inclusive: 16 origins, each with 30- and 90-calendar-day targets,
32 windows. This extends the earlier six-origin pool by ten origins, including
all four quarters of 2022. Retain earlier decisions as historical records.
The target begins origin date + 1 day and ends origin date + H days, inclusive.
The screening interval is origin date - 30 days through origin date + H days,
inclusive. Dates on the boundaries count. Adjacent/overlapping windows must not
be treated as independent events in later evaluation.

## Fixed incident rule

Exclude for a documented merchant-vessel attack, detention, navigation incident
requiring salvage/tow assistance, or physical transit restriction in Suez,
Bab el-Mandeb/Red Sea, Panama, or Hormuz/Gulf of Oman approaches. Include a dated
official security notice describing a current qualifying incident inside the
interval. Cargo need not be crude. A tug-assisted malfunction qualifies even
when traffic continues. Routine escort/tow operations without an incident do not.
Do not infer material crude losses, a closure, or a continuous incident duration
from this broad rule. A witness inside one horizon does not automatically exclude
the other. An ongoing restriction needs explicit interval or dated in-window
confirmation; do not carry it forward indefinitely.

## Evidence and stopping rules

Use primary SCA, ACP, EIA, IMO, carrier, and national-government maritime/security
publications. Search each additional origin using its year/quarter and the four
geographies; retain queries, retrieved sources, source locators and retrieval
failures. Prior verified witnesses may be reused only if their supported dates
overlap the new window. Later publications can support retrospective labels only;
they cannot enter the historical forecast input bundle.

Stop screening a window at a verified positive witness: EXCLUDED_INCIDENT.
If no positive witness is found, require an accessible, date-complete record for
each geography/source family before assigning SCREEN_NEGATIVE_BOUNDED_SOURCES.
Search-engine silence, a broken archive, or an unenumerated notice collection
means UNRESOLVED_COVERAGE, never incident-free. Bounded screen-negative status is
not proof of no incidents and is not replay eligibility. Record coverage limits
and keep excluded and unresolved candidates in the register. Do not replace them
with hand-picked quiet dates or relax this rule to obtain accepted controls.

## Change control

Record the fixing commit and SHA-256 in the results. Corrections to evidence may
change decisions with an audit trail. Changes to dates, geography, incident
definition or coverage threshold require a new protocol version, with disclosure
that existing evidence was inspected. Price calendar, replay eligibility,
development/test splits and statistical acceptance remain separate gates.
