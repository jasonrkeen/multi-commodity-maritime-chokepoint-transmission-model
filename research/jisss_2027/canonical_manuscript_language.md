# JISSS 2027 Canonical Manuscript Language

## Study Title

From Open Sources to Strategic Warning:
A Quantitative Framework for Modeling Maritime Chokepoint Disruption and
National Security Risk

---

## Abstract - Validation and Findings Language

This study evaluates whether an open-source probabilistic framework can improve
strategic warning by quantifying the conditional economic and national-security
consequences of maritime chokepoint disruption. The framework integrates
physical maritime disruption, commodity-market transmission, substitution
constraints, downstream effects, and uncertainty through scenario analysis and
Monte Carlo simulation.

The reference model was frozen on August 19, 2026. The exact Git commit
corresponding to that reference run cannot be demonstrated from the repository
history; the August 21, 2026 commit
6c1cc646fa9486817fe5d8c9f1f6fdd9eadfa451 is therefore treated only as the
publication-validation base rather than as the exact reference-run source tree.

Experiment A evaluates the frozen specification without retrospective parameter
changes. Following temporal review, the evidence register contained 13 clean
prospective observations, four mixed-window observations, and 12 retrospective
observations. The final validation scorecard classified eight dimensions as
SUPPORT, two as PARTIAL, three as NOT COMPARABLE, and none as CONTRADICT.
Validation-domain coverage was classified as three COVERED, seven PARTIAL, and
one GAP.

No global validation percentage is reported. Exploratory weighted support and
coverage indices developed during the research process were retired because the
weights and category-to-score mappings were not established before the
prospective evidence was evaluated and because heterogeneous validation types
cannot be defensibly collapsed into a single accuracy statistic.

The findings indicate that quantitative OSINT can strengthen strategic warning
by estimating conditional consequence distributions and by exposing
cross-domain transmission mechanisms. The framework should not be interpreted
as predicting whether a geopolitical crisis will occur or as converting gross
strategic exposure into realized economic loss.

---

## Introduction - Validation Design

The empirical contribution of this study is not a claim that the framework
predicted the 2026 crisis. The model was developed during the crisis and is
therefore evaluated through frozen-specification validation rather than
described as an out-of-sample forecast.

A reference model run was frozen on August 19, 2026. Evidence observed after
that date was subsequently collected and classified according to its
measurement window. Observations measured entirely after August 19 were
eligible for prospective validation. Measurements spanning the freeze were
classified as mixed and retained only where appropriate as contextual evidence.

This distinction matters because publication date alone does not establish
prospective validity. A report published after the model freeze may still
describe conditions measured before or across the freeze. The validation
framework therefore evaluates the temporal status of the underlying
measurement rather than simply the date on which an article or statistical
release appeared.

Following temporal audit, Experiment A contained 13 clean prospective
observations, four mixed-window observations, and 12 retrospective observations.

The final assessment does not collapse these heterogeneous observations into a
single validation percentage. Instead, evidence is classified according to
whether it supports a directional claim, threshold, transmission mechanism,
contextual interpretation, or directly comparable numerical quantity.

Across the final scorecard, eight dimensions were classified as SUPPORT, two as
PARTIAL, three as NOT COMPARABLE, and none as CONTRADICT. Across the 11
predefined validation domains, three are classified as COVERED, seven as
PARTIAL, and one as a GAP.

These classifications describe the availability, relevance, and comparability
of evidence. They are not equivalent to a forecast-accuracy percentage or a
probability that the model is correct.

---

## Methods - Model Freeze and Provenance

### Model Freeze and Repository Provenance

The reference model run used for Experiment A is dated August 19, 2026.

The exact Git commit corresponding to that run is unresolved. The repository
contains an identifiable earlier commit dated August 12, 2026 and a subsequent
commit dated August 21, 2026. The August 21 commit incorporates changes to model
inputs and source-registration files containing records dated August 19, but
this does not establish that the August 21 repository tree is identical to the
source and input state used for the August 19 reference run.

The study therefore distinguishes between two provenance concepts.

The reference-run date is August 19, 2026.

The publication-validation base commit is:

6c1cc646fa9486817fe5d8c9f1f6fdd9eadfa451

dated August 21, 2026.

The publication-validation base is used as the nearest documented repository
state for reproducibility review. It is not represented as the exact August 19
reference-run commit.

This limitation is disclosed rather than reconstructed retrospectively.

---

## Methods - Temporal Validation Rule

### Temporal Classification

Temporal eligibility is determined by the measurement window of an observation,
not solely by publication date.

The validation windows are:

- PRE_FREEZE: January 1-August 18, 2026;
- FREEZE_DAY: August 19, 2026;
- POST_FREEZE: August 20-December 31, 2026; and
- MIXED: any measurement interval crossing August 19.

PRE_FREEZE observations are retrospective context.

FREEZE_DAY observations are contemporaneous and require source-time review.

POST_FREEZE observations may qualify for prospective Experiment A validation.

MIXED observations are retained where analytically useful but are excluded from
clean prospective numerical comparison.

This rule was applied even when exclusion reduced the apparent strength of the
validation results.

For example, a 10-day Hormuz average covering August 16-25 was reclassified as
MIXED because its measurement interval crossed the freeze. A separate
late-August disruption statistic measured conditions from conflict onset
through August 28 and was also classified as mixed because its comparison
period incorporated pre-freeze conditions.

---

## Methods - Validation Evidence Types

### Validation Use

The study separates evidence according to the statistical claim it can
reasonably support.

Five principal validation uses are recognized:

1. direct point error;
2. directional evidence;
3. threshold evidence;
4. mechanism evidence; and
5. contextual evidence.

Direct numerical error measures such as absolute error, percentage error, MAE,
or RMSE are reserved for observations that represent the same statistic as the
frozen model output.

A daily Brent settlement, for example, is not treated as direct point-error
evidence against a modeled scenario-peak price. Likewise, observed Dubai or
Oman cash premiums are not treated as numerical error observations against the
model's constructed maximum regional sour-crude price proxy.

LNG cargo cancellations can support persistence or disruption mechanisms but
do not constitute a direct numerical validation of modeled LNG-flow magnitude.

Observed freight, refined-product, LNG, or sour-crude stresses can provide
evidence of lagged transmission mechanisms but cannot directly validate the
model's dollar-denominated lagged strategic-exposure estimate.

---

## Methods - Categorical Assessment

### Experiment A Assessment

Experiment A evaluates the frozen specification without modifying model
parameters.

Each validation claim is classified as:

SUPPORT - qualifying evidence is consistent with the relevant frozen model
expectation.

PARTIAL - evidence supports a component, direction, threshold, or mechanism but
does not permit complete validation.

CONTRADICT - qualifying evidence is materially inconsistent with the frozen
expectation.

NOT COMPARABLE - the available observed statistic and modeled quantity cannot
be defensibly evaluated on a like-for-like basis.

The final scorecard contains:

- SUPPORT: 8;
- PARTIAL: 2;
- NOT COMPARABLE: 3; and
- CONTRADICT: 0.

No numerical values are assigned to these categories in the final analysis.

---

## Methods - Domain Coverage

### Validation-Domain Coverage

The study evaluates evidence across 11 predefined domains:

1. Hormuz physical throughput;
2. Bab el-Mandeb / Red Sea throughput;
3. crude-price response;
4. regional sour-crude basis response;
5. LNG disruption;
6. refined-product disruption;
7. alternative pipeline utilization;
8. inventory drawdowns;
9. production shut-ins;
10. freight and war-risk cost; and
11. immediate versus lagged transmission.

Coverage is reported categorically:

- COVERED: 3 domains;
- PARTIAL: 7 domains; and
- GAP: 1 domain.

Ten of eleven domains therefore contain at least some evidence relevant to
Experiment A, but most remain only partially testable.

No numerical domain-coverage index is reported.

---

## Methods - Retirement of Aggregate Scores

### Methodological Correction

During development of the validation workflow, exploratory mappings assigned
numerical values and weights to categorical evidence assessments. Those
internal calculations produced aggregate support values of 91.5% and later
90.5% after temporal correction.

A separate exploratory numerical domain-coverage calculation produced 72.7%.

These figures are not validation results and are not used in the final study.

They were retired because the weighting schemes and numerical mappings were not
established before prospective evidence was evaluated. In addition,
directional, threshold, mechanism, contextual, and direct numerical evidence
represent different statistical claims and cannot be defensibly collapsed into
a single accuracy percentage.

The earlier calculations remain visible in Git history for methodological
transparency.

---

## Results - Experiment A

### Frozen-Specification Validation

After temporal review, the validation evidence register contained:

- 13 clean prospective observations;
- four mixed-window observations; and
- 12 retrospective observations.

Automated governance checks identified no remaining temporal, dependency,
scorecard, or coverage errors and produced no warnings.

Across the final Experiment A scorecard:

- eight dimensions were classified as SUPPORT;
- two were classified as PARTIAL;
- three were classified as NOT COMPARABLE; and
- none were classified as CONTRADICT.

The results show substantial structural and directional consistency across
several transmission mechanisms, but they do not establish a conventional
forecast-accuracy rate.

The absence of a CONTRADICT classification should also not be interpreted as
proof that the framework is correct. The validation period remains limited,
some domains are only partially observable, and several modeled quantities do
not have direct real-world statistical counterparts.

---

## Results - Domain Findings

### Hormuz Physical Throughput

The Hormuz physical-throughput domain is classified as COVERED.

Multiple clean post-freeze visible-vessel observations documented continuing
impairment after the August 19 freeze. These observations support persistence
and directional disruption claims.

Exact magnitude testing remains limited by AIS visibility, vessel-universe
definitions, reporting cutoffs, and potential revisions to commercial vessel
datasets.

### Bab el-Mandeb / Red Sea Throughput

The Bab el-Mandeb / Red Sea domain is classified as COVERED.

Post-freeze observations documented continuing corridor activity while Hormuz
remained impaired.

This evidence supports comparative corridor functionality but does not by
itself prove causal rerouting from Hormuz.

### Crude-Price Response

The crude-price domain is PARTIAL.

Post-freeze Brent settlements support directional price elevation under
continued disruption. Daily settlement prices, however, are not equivalent to
the frozen modeled scenario-peak statistic and therefore are not used for
direct point-error testing.

### Regional Sour-Crude Basis

The regional sour-crude basis domain is COVERED.

Post-freeze Dubai and Oman cash premiums provide independently observable
market evidence of localized sour-crude stress.

The observed premium construction is not identical to the frozen regional
sour-price peak construction, so the evidence supports direction and magnitude
class rather than conventional point-error validation.

### LNG

The LNG domain is PARTIAL.

Post-freeze QatarEnergy cargo cancellations provide evidence that LNG
disruption persisted after the model freeze.

Cargo cancellations are evidence of disruption and persistence but do not
provide a directly comparable LNG export-flow magnitude.

### Refined Products

The refined-products domain is PARTIAL.

Post-freeze Mediterranean ULSD observations support downstream refined-product
stress.

A single benchmark does not establish the magnitude or breadth of the complete
refined-product transmission channel.

### Alternative Pipelines

The alternative-pipeline domain is PARTIAL.

Post-freeze reporting indicated use of the Habshan-Fujairah bypass at
approximately 1.8 million barrels per day.

This supports the modeled bypass mechanism but does not establish broader Gulf
pipeline utilization. Independent evidence for the Saudi East-West/Yanbu route
remains a priority.

### Inventories

The inventory domain is PARTIAL.

EIA data for the week ending August 21 showed declining strategic and total
crude inventories. Because the weekly measurement interval crossed the August
19 freeze, those observations are classified as mixed rather than clean
prospective evidence.

A fully post-freeze weekly observation is required for stronger Experiment A
testing.

### Production Shut-Ins

Production shut-ins remain the single GAP domain.

Post-freeze reporting corroborates continuing Gulf production constraints, but
no qualifying observed production-loss magnitude measured wholly after August
19 had been identified at the time of the assessment.

Available quantitative figures measured July conditions, crossed the freeze,
or represented forecasts.

The evidence gap is retained rather than filled using temporally inappropriate
data.

### Freight and War-Risk Cost

The freight and war-risk domain is PARTIAL.

Post-freeze LR2 freight reached a reported record, supporting the freight-cost
transmission mechanism.

The broader domain remains partial because a separate independently observed
war-risk insurance measure has not yet been incorporated.

### Immediate Versus Lagged Transmission

The immediate-versus-lagged domain is PARTIAL.

Post-freeze freight, sour-crude, refined-product, and LNG evidence demonstrates
that economic effects persisted through multiple downstream channels after the
initial disruption.

These mechanisms support the structural importance of lagged transmission but
cannot directly validate the modeled $726.64 billion lagged strategic-exposure
amount.

---

## Discussion - Interpretation of Validation

Experiment A provides evidence that several important mechanisms embedded in
the frozen framework remained consistent with subsequently observed conditions.

This finding should be interpreted narrowly.

The validation does not demonstrate that the framework predicted the 2026
geopolitical crisis. The model was developed during that crisis.

It also does not demonstrate that the frozen gross-exposure estimate equals
realized GDP loss, corporate loss, market-capitalization loss, or another
directly observable economic outcome.

Instead, the strongest evidence concerns the structure of transmission:
physical maritime impairment, elevated freight costs, localized sour-crude
stress, downstream refined-product effects, LNG disruption, bypass
infrastructure utilization, and persistence across multiple economic channels.

The results therefore support the framework primarily as a strategic-warning
and consequence-estimation architecture rather than as a conventional
point-forecasting model.

---

## Discussion - Why No Headline Accuracy Percentage

A single validation percentage would imply statistical equivalence among
evidence types that are fundamentally different.

Directional agreement in vessel activity is not equivalent to direct numerical
agreement with a modeled commodity price.

A record freight observation is not equivalent to direct validation of a
dollar-denominated exposure estimate.

Evidence of LNG cargo cancellation validates a disruption mechanism but is not
equivalent to an observed LNG-flow percentage.

For this reason, the final analysis intentionally sacrifices a convenient
headline percentage in favor of transparent claim-level classifications.

The result is less numerically dramatic but more methodologically defensible.

---

## Discussion - Evidence Gaps

An important feature of the validation process is the preservation of negative
findings and incomplete evidence.

Production shut-ins remain a complete evidence gap.

Inventory evidence remains partially constrained by a measurement window that
crosses the freeze.

LNG evidence demonstrates persistence but not directly comparable export-flow
magnitude.

Alternative-pipeline evidence demonstrates one bypass route rather than the
entire regional substitution system.

War-risk insurance remains less directly observed than freight rates.

These limitations identify priorities for continued evidence collection and
reduce the risk that validation becomes an exercise in selecting only
supportive observations.

---

## Limitations - Provenance

The exact Git commit corresponding to the August 19, 2026 reference run cannot
be demonstrated from the current repository history.

The August 21 commit is the nearest documented repository state used for
publication-validation review, but it is not represented as the exact
reference-run source tree.

This limits claims of exact source-tree reproducibility for the August 19 run.

The frozen outputs and documented assumptions nevertheless remain fixed for
Experiment A, and the provenance limitation is disclosed rather than
retrospectively reconstructed.

---

## Limitations - Interpretation of Exposure

The framework estimates conditional strategic exposure under modeled disruption
conditions.

Gross exposure is not equivalent to GDP loss, realized corporate loss,
market-capitalization loss, fiscal loss, or expected investment return.

The Monte Carlo median is the median of the modeled conditional distribution;
it should not be described as the most likely real-world loss.

Similarly, the historical probability-weighted output based on an 18% scenario
prior is not treated as a current probability estimate and is not used as a
headline validation result.

---

## Conclusion

This study evaluates whether quantitative OSINT can improve strategic warning
by organizing open-source observations into a reproducible framework for
estimating the conditional consequences of maritime chokepoint disruption.

The findings support a qualified conclusion.

Following an August 19, 2026 model freeze, subsequently observed evidence
documented continuing maritime impairment and transmission across freight,
regional sour-crude pricing, refined products, LNG, and alternative
infrastructure.

Across the final frozen-specification validation scorecard, eight dimensions
were classified as SUPPORT, two as PARTIAL, three as NOT COMPARABLE, and none
as CONTRADICT.

Across the 11 validation domains, three are COVERED, seven PARTIAL, and one
remains a GAP.

These categories do not constitute a forecast-accuracy percentage.

They instead describe where subsequently observed evidence supports frozen
model expectations, where only part of a mechanism can be assessed, and where
direct numerical comparison is not defensible.

The broader implication is that quantitative OSINT is most useful for strategic
warning when it does not pretend to eliminate uncertainty. Its value lies in
making assumptions explicit, distinguishing evidence types, enforcing temporal
discipline, estimating conditional consequence distributions, identifying
cross-domain transmission mechanisms, and preserving unresolved uncertainty.

For intelligence practitioners, policymakers, and enterprise risk professionals,
such a framework can narrow the gap between recognizing a geopolitical
disruption and understanding the range of consequences that may follow.
