# Historical scenario construction and eligibility: freeze 0.6

Frozen 2026-10-22, before any pilot outcome/error computation. This is an
amendment informed by inspected historical evidence, not preregistration or
prospective validation. Scope: public Brent outcomes for the existing 16 quarterly
2021-2024 origins and three purposive event origins; 30/90-day horizons, 38 rows.
The two strata stay separate. The 32 calendar windows remain included regardless
of incidents. Previous quiet-control exclusions are diagnostic labels only.

## Deterministic evidence-to-scenario rules

1. **Information cutoff.** Use origin D at 00:00 UTC. Publication policy 0.4
   applies: date <= D-2; price age <=14 calendar days. For recovered archive
   content, use the later of evidenced publication date and earliest verified
   capture date for those exact bytes. Preserve both dates; never infer publication
   from observation period. Select the latest eligible version in the declared
   inspected source set, not whichever gives favorable model output. Conflicting
   eligible versions require a documented correction chain; otherwise block.
2. **Coverage and status.** Before construction, require a hashed search manifest
   covering the relevant authority/operator notices for Suez/SUMED, Bab el-Mandeb,
   Hormuz and Panama through cutoff, including unresolved older restrictions.
   Record search bounds, unavailable archives, corrections and scope. A missing
   notice, no search hit or absence of a known incident cannot establish normal
   capacity. Extract explicit OPEN / RESTRICTED / CLOSED / UNKNOWN status for
   each affected route and commodity. UNKNOWN blocks construction. Incident
   witnesses in the retrospective control screen never enter the forecast bundle.
3. **Magnitude.** A quantitative restricted flow must share units, period,
   commodity and route scope with its normal-flow denominator. Severity is
   1 - available_flow/normal_flow, constrained by documented measurements to [0,1];
   contradictions block rather than clip. A verified complete closure can set
   route severity=1 only for the exact physical route concerned. Canal closure
   cannot imply Suez-plus-pipeline closure. Transit-count or vessel-size reductions,
   security warnings and named attacks do not translate directly into crude flow
   loss. No discretionary mild/moderate/severe lookup or fitted severity is allowed.
4. **Timing.** Convert only evidenced as-of schedules into full UTC daily intervals.
   Model day0 is D+1. In-progress events carry their original elapsed time for
   response ramps; do not restart at day0. A planned future reopening must be
   labeled an as-of plan, never replaced by the eventual actual reopening.
   Unknown remaining duration or recovery curve blocks a point replay. Do not
   use realized duration, later reports, or the repository's 30/60-day templates.
   Subdaily changes not representable by the daily engine require a separately
   validated aggregation rule; no rounding is silently permitted.
5. **Future shocks and uncertainty.** This version allows only a fully evidenced
   announced-schedule conditional path, not an unconditional probabilistic forecast.
   No unannounced future incident is inserted. Persistence beyond a documented
   schedule, duration distributions and scenario priors are not supplied here;
   they require a new version with pre-cutoff empirical support. Monte Carlo and
   sensor fusion stay off. A probability of one, if a future runner requires it,
   means conditional evaluation weight only, not certainty about occurrence.
6. **Physical response.** Require compatible route shares, disjoint usable stocks,
   operating floors, delivery limits, release authorization/start/ramp/duration,
   rerouting/substitution, structural offsets and demand responses. Every active
   parameter must have an eligible source or separately frozen, explicitly labeled
   analyst assumption supported without outcomes. None are approved by this freeze.
   Missing is never zero. No automatic use of current input CSV defaults. Serial
   routes cannot be added and nameplate bypass capacity is not free spare flow.
7. **Freshness.** As conservative analyst design gates, annual reference-flow
   periods must end no earlier than 24 calendar months before origin; stock levels
   no earlier than 35 calendar days; current operational status must have an
   explicit reconfirmation within seven calendar days. These limits do not prove
   representativeness, source completeness or validity. A source's shorter stated
   validity supersedes them. Expiry or absence blocks, with no exception chosen
   after errors. Older structural engineering facts require a documented continued-
   applicability decision, not extrapolation of an old operational rate.
8. **Version and output.** Pin model source at
   `7659db2f2f760b056ea8384cad295920dc38830f`, baseline price vintage, all input
   hashes and the compiler version. No compiler is implemented/validated here;
   this is a construction specification. Review every parameter and exclude
   leakage from preprocessing. A validated replay adapter must demonstrate UTC
   alignment, elapsed-state carryover and equivalent unchanged model execution
   before any historical run. Business-dollar and IBIF confidence claims remain
   out of scope; BCS stays experimental and escalation UNASSESSED.

## Eligibility algorithm and immutable decision

Each of these gates must explicitly PASS: price, exposure mapping, usable inventory,
notice coverage, severity, duration/recovery, other response parameters, validated
replay implementation, and outcome-calendar/vintage completeness. Unknown and
not-reviewed fail closed. Source-date PASS alone cannot set a physical gate PASS.
Keep every failed gate, not only the first. Missing/failed origins remain in the
universe; no substitutes and no selection by realized price direction.

`calibration_inventory/replay_eligibility_0_6.csv` freezes 38 BLOCKED_NOT_RUN rows,
including the three event origins and every background window. Nine original
price selections (18 rows) retain PASS_PRICE_POLICY_ONLY; the ten added quarterly
origins have not had prices audited. Eight background windows plus the February
2024 event's two windows clear the exposure publication date, but none clears
exposure acceptance. The DOE archive date clears six background windows plus
that event's two windows; all eight fail inventory freshness and global coverage.

The freeze manifest hashes these rules, source-witness decisions, membership,
recovery decisions and machine-readable policy using UTF-8 LF canonical text.
Do not edit frozen files in place after publication: any new evidence or changed
rule creates 0.7 with a reason, prior hash, changed eligibility and exposure-to-
outcomes disclosure. No rows may be promoted just by changing BLOCKED to PASS.

## Limits and remaining prerequisites

This freeze closes the **rules and eligibility decision**, not the physical-data
gaps. Zero market replays and zero fits are authorized by its current evidence.
Outcomes, holiday completeness, splits, overlap groups, sample adequacy and
numerical performance thresholds remain outside this freeze and unresolved.
Before evaluation, freeze those separately; use the same observation calendar
and lagged starting price for model and no-change. Keep crisis-crossing origins
clustered and report missing pairs. Four calendar years do not establish adequate
independent sample size. Never call these reconstructed conditional paths issued
forecasts, causal estimates, or validation of business-impact scores.
