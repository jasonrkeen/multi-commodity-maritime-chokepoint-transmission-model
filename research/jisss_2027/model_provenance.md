# Model Provenance

## Reference Run

Reference run date: 2026-08-19

Reference run commit: unresolved

The outputs used as the frozen reference for Experiment A are dated
August 19, 2026.

The repository does not contain a Git commit from August 19 that can be
demonstrated to correspond exactly to the source-code and input state used
for that reference run.

The nearest earlier identifiable commit is:

- commit: e73f25ae30995b7c1beb309296965d2fc5cf881d
- date: 2026-08-12
- message: Improve dependency compatibility policy (#4)

The next identifiable repository commit is:

- commit: 6c1cc646fa9486817fe5d8c9f1f6fdd9eadfa451
- date: 2026-08-21
- message: Add heavy-sour infrastructure availability (#5)

The August 21 commit includes changes to model input and source-registration
files containing records dated August 19. This provides evidence that relevant
model and input work occurred on the reference-run date, but it does not prove
that the August 21 Git tree is identical to the August 19 reference-run state.

Accordingly, the study distinguishes between the reference-run date and the
publication-validation base commit.

## Publication Validation Base

Publication validation base commit:
6c1cc646fa9486817fe5d8c9f1f6fdd9eadfa451

Publication validation base commit date:
2026-08-21

The August 21 commit is used as the nearest documented repository state for
publication validation and reproducibility review.

It is not represented as the exact August 19 reference-run commit.

## Validation Principle

The frozen reference outputs and assumptions are evaluated before any
retrospective calibration changes are made using observed 2026 outcomes.

Where exact source-code provenance cannot be demonstrated, the limitation is
disclosed rather than reconstructed retrospectively.

## Experiment Classes

### Experiment A - Frozen-Specification Event Validation

No model-parameter modification.

### Experiment B - Retrospective Calibration

Parameter changes are permitted only after Experiment A is locked.

### Experiment C - Prospective Strategic-Warning Specification

Future-facing refinement may be informed by Experiments A and B.

## Terminology

The exercise should not be described as an out-of-sample prediction of the
2026 crisis.

Preferred terms include:

- frozen-specification validation;
- directional agreement;
- structural agreement;
- mechanism evidence;
- prospective observation;
- contemporaneous observation;
- retrospective observation; and
- retrospective calibration.

## Provenance Limitation

The exact Git commit corresponding to the August 19 reference run is unresolved.

This limitation does not invalidate the frozen-output validation design, but it
does limit claims about exact source-tree reproducibility for the reference run.

The final manuscript should therefore distinguish between:

1. the August 19 reference-run/model freeze; and
2. the August 21 publication-validation base commit.
