# JISSS 2027 Methodology Corrections

## Purpose

This document records methodological corrections made during validation of the
2026 maritime chokepoint model for the planned JISSS study.

The corrections are preserved prospectively in Git history. Earlier commits
are not rewritten or removed.

## 1. Retirement of aggregate Experiment A support scores

Early validation development used exploratory numerical mappings for categorical
assessments such as SUPPORT and PARTIAL and applied analyst-selected weights to
produce an aggregate structural/directional support percentage.

Those calculations produced exploratory values including 91.5% and, after a
temporal correction, 90.5%.

These percentages are retired from the final validation methodology.

### Reason

The category-to-score mappings and weighting scheme were not preregistered.
The scorecard also combines heterogeneous validation types, including:

- directional evidence;
- threshold evidence;
- mechanism evidence;
- contextual evidence; and
- direct numerical comparison.

Collapsing these evidence types into a single percentage creates a degree of
precision not supported by the validation design.

### Final treatment

Experiment A is reported categorically:

- SUPPORT: 8
- PARTIAL: 2
- NOT_COMPARABLE: 3
- CONTRADICT: 0

No global model-support or forecast-accuracy percentage is reported.

## 2. Retirement of numerical validation-domain coverage index

An exploratory domain-coverage matrix previously mapped categorical coverage
states to numerical values and produced a 72.7% coverage index.

That index is retired.

### Reason

The 11 validation domains contain different targets, evidence types, and
degrees of observability. No domain weighting or numerical mapping was
preregistered.

### Final treatment

Coverage is reported categorically:

- COVERED: 3
- PARTIAL: 7
- GAP: 1

Ten of eleven domains contain at least some evidence relevant to Experiment A,
but most remain partially testable.

## 3. Temporal-classification correction

Experiment A uses the measurement period of an observation, not merely the
publication date, to determine temporal eligibility.

The model/reference freeze is August 19, 2026.

- PRE_FREEZE: January 1-August 18, 2026
- FREEZE_DAY: August 19, 2026
- POST_FREEZE: August 20-December 31, 2026
- MIXED: measurement windows crossing August 19

Two initially prospective Hormuz observations were subsequently reclassified:

1. A 10-day Hormuz average covering August 16-25 crossed the freeze and was
   reclassified as MIXED.
2. A late-August reduction statistic measured conditions from conflict onset
   through August 28 and therefore incorporated pre-freeze information. It was
   also reclassified as MIXED.

Mixed observations remain available as context but cannot enter clean
prospective quantitative validation.

## 4. Numerical-error restriction

MAE, RMSE, percentage error, and similar numerical error measures are reserved
for like-for-like comparisons in which the observed and modeled quantities
represent the same statistic.

Examples of non-comparable quantities include:

- daily Brent settlement versus modeled scenario peak;
- observed Dubai/Oman cash premium versus modeled regional sour-price peak;
- LNG cargo cancellation count versus modeled LNG flow magnitude; and
- observed downstream mechanisms versus modeled dollar-denominated lagged
  strategic exposure.

These observations may still provide directional, threshold, or mechanism
evidence.

## 5. Production shut-in evidence gap

The production shut-in domain remains a documented evidence gap.

Available quantitative observations identified during the review either:

- measure July conditions;
- cross the August 19 freeze;
- or represent forecasts rather than clean post-freeze observed outcomes.

The gap is preserved rather than filled with temporally or statistically
inappropriate evidence.

## 6. Validation philosophy

The final validation design prioritizes:

- transparent evidence classification;
- prospective temporal discipline;
- direct comparability where possible;
- explicit non-comparability where necessary;
- visible evidence gaps;
- reproducible automated governance; and
- preservation of methodological corrections in version control.

The objective is not to maximize an apparent validation score. The objective is
to produce a defensible record of what the frozen model did and did not receive
support for from subsequently observed evidence.
