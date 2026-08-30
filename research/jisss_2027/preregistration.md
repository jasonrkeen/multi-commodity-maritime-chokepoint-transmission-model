# JISSS 2027 Validation Preregistration

## Study

From Open Sources to Strategic Warning:
A Quantitative Framework for Modeling Maritime Chokepoint
Disruption and National Security Risk

## Frozen model

Repository:
jasonrkeen/multi-commodity-maritime-chokepoint-transmission-model

Publication-validation base commit:
6c1cc646fa9486817fe5d8c9f1f6fdd9eadfa451

Reference model run:
19 August 2026

Public Scenario Lab publication:
29 August 2026

## Governance rule

Observed outcome data collected for this validation study will not
be used to alter the frozen reference model before baseline
validation metrics are calculated.

Any subsequent parameter modifications will be classified as
retrospective calibration and reported separately.

## Frozen reference outputs

Gross modeled exposure: $884.92 billion
Immediate exposure: $158.27 billion
Lagged exposure: $726.64 billion
Monte Carlo P50: $903.90 billion
Monte Carlo P95: $1.283 trillion
Peak Brent proxy: $127.18/bbl

## Primary validation questions

1. Did the model correctly identify the direction and relative severity of disruption?
2. Did observed energy and maritime conditions fall within modeled scenario ranges?
3. Did modeled substitution mechanisms correspond with observed rerouting behavior?
4. Did modeled price-pressure ranges reasonably encompass observed market behavior?
5. Did the model correctly identify lagged transmission as a major consequence channel?
6. Did compound maritime stress create consequences not captured by an oil-only or single-chokepoint assessment?

## Validation metrics

- Mean Absolute Error where directly comparable
- Root Mean Squared Error where directly comparable
- Directional accuracy
- Simulation interval coverage
- Scenario-band classification accuracy
- Rank-order accuracy across commodity channels

## Evidence classifications

A - independently observable and directly comparable
B - independently observable but indirectly comparable
C - retrospective contextual evidence
D - practitioner-derived evidence excluded from quantitative validation

## Calibration rule

Baseline validation will be completed before any retrospective calibration.

Original and recalibrated results will both be retained.
