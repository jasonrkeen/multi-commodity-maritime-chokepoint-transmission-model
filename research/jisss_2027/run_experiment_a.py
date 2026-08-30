from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"

OBS_PATH = DATA / "observed_2026.csv"
METRIC_PATH = OUTPUTS / "validation_metrics.csv"
SCORECARD_PATH = OUTPUTS / "experiment_a_scorecard.csv"
REPORT_PATH = OUTPUTS / "experiment_a_automated_validation.md"

FREEZE_DATE = date(2026, 8, 19)
POST_FREEZE_START = date(2026, 8, 20)

VALID_TEMPORAL = {
    "retrospective",
    "contemporaneous",
    "prospective",
    "mixed",
}

VALID_ASSESSMENTS = {
    "SUPPORT",
    "PARTIAL",
    "CONTRADICT",
    "NOT_COMPARABLE",
}


def parse_date(value: str) -> date:
    return date.fromisoformat(value.strip())


def is_true(value: str) -> bool:
    return value.strip().upper() == "TRUE"


def load_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def validate_observations(rows):
    errors = []
    warnings = []

    ids = set()

    for row in rows:
        oid = row["observation_id"].strip()

        if oid in ids:
            errors.append(f"Duplicate observation_id: {oid}")
        ids.add(oid)

        start = parse_date(row["date_start"])
        end = parse_date(row["date_end"])
        temporal = row["temporal_classification"].strip()
        eligible = is_true(row["eligible_for_quantitative_validation"])

        if start > end:
            errors.append(f"{oid}: date_start is after date_end")

        if temporal not in VALID_TEMPORAL:
            errors.append(
                f"{oid}: invalid temporal_classification '{temporal}'"
            )

        # Clean prospective evidence must begin entirely after freeze.
        if temporal == "prospective" and start < POST_FREEZE_START:
            errors.append(
                f"{oid}: marked prospective but begins {start}, "
                f"before clean post-freeze window {POST_FREEZE_START}"
            )

        # Anything spanning freeze cannot enter clean quantitative holdout.
        if start <= FREEZE_DATE < end and eligible:
            errors.append(
                f"{oid}: spans freeze but remains quantitatively eligible"
            )

        if temporal == "mixed" and eligible:
            errors.append(
                f"{oid}: mixed-window observation cannot be quantitatively eligible"
            )

        if temporal in {"retrospective", "contemporaneous"} and eligible:
            warnings.append(
                f"{oid}: {temporal} observation is quantitatively eligible; "
                "review whether this is intentional"
            )

    return errors, warnings


def validate_metrics(metrics, observations):
    errors = []
    warnings = []

    obs_by_id = {r["observation_id"]: r for r in observations}

    for row in metrics:
        metric_id = row["metric_id"]

        refs = [
            row.get("source_observation_1", "").strip(),
            row.get("source_observation_2", "").strip(),
        ]

        refs = [r for r in refs if r]

        for ref in refs:
            if ref not in obs_by_id:
                errors.append(
                    f"{metric_id}: references unknown observation {ref}"
                )

        if is_true(row["eligible_for_model_comparison"]):
            for ref in refs:
                obs = obs_by_id.get(ref)
                if not obs:
                    continue

                if not is_true(
                    obs["eligible_for_quantitative_validation"]
                ):
                    errors.append(
                        f"{metric_id}: eligible metric depends on "
                        f"ineligible observation {ref}"
                    )

                if (
                    obs["temporal_classification"].strip()
                    != "prospective"
                ):
                    errors.append(
                        f"{metric_id}: eligible metric depends on "
                        f"non-prospective observation {ref}"
                    )

    return errors, warnings


def validate_scorecard(rows):
    errors = []
    warnings = []

    numerator = 0.0
    denominator = 0.0

    counts = {
        "SUPPORT": 0,
        "PARTIAL": 0,
        "CONTRADICT": 0,
        "NOT_COMPARABLE": 0,
    }

    for row in rows:
        sid = row["scorecard_id"]
        assessment = row["assessment"].strip()

        if assessment not in VALID_ASSESSMENTS:
            errors.append(
                f"{sid}: invalid assessment '{assessment}'"
            )
            continue

        counts[assessment] += 1

        score_raw = row["score"].strip()
        weight = float(row["weight"] or 0)

        if assessment == "NOT_COMPARABLE":
            if weight != 0:
                errors.append(
                    f"{sid}: NOT_COMPARABLE row has nonzero weight"
                )
            continue

        if not score_raw:
            errors.append(
                f"{sid}: scoreable assessment has no score"
            )
            continue

        score = float(score_raw)

        if not 0 <= score <= 1:
            errors.append(
                f"{sid}: score outside [0,1]"
            )

        if weight <= 0:
            errors.append(
                f"{sid}: scoreable assessment has nonpositive weight"
            )
            continue

        numerator += score * weight
        denominator += weight

    aggregate = (
        numerator / denominator if denominator else None
    )

    return errors, warnings, counts, aggregate


def main():
    observations = load_csv(OBS_PATH)
    metrics = load_csv(METRIC_PATH)
    scorecard = load_csv(SCORECARD_PATH)

    errors = []
    warnings = []

    e, w = validate_observations(observations)
    errors.extend(e)
    warnings.extend(w)

    e, w = validate_metrics(metrics, observations)
    errors.extend(e)
    warnings.extend(w)

    e, w, counts, aggregate = validate_scorecard(scorecard)
    errors.extend(e)
    warnings.extend(w)

    temporal_counts = {}
    for row in observations:
        key = row["temporal_classification"].strip()
        temporal_counts[key] = temporal_counts.get(key, 0) + 1

    eligible_count = sum(
        is_true(r["eligible_for_quantitative_validation"])
        for r in observations
    )

    report = []

    report.append("# Experiment A - Automated Validation")
    report.append("")
    report.append(f"Freeze date: {FREEZE_DATE.isoformat()}")
    report.append(
        f"Clean prospective window begins: "
        f"{POST_FREEZE_START.isoformat()}"
    )
    report.append("")

    report.append("## Observation counts")
    report.append("")

    for key in sorted(temporal_counts):
        report.append(f"- {key}: {temporal_counts[key]}")

    report.append(
        f"- quantitatively eligible observations: {eligible_count}"
    )

    report.append("")
    report.append("## Scorecard")
    report.append("")

    for key, value in counts.items():
        report.append(f"- {key}: {value}")

    if aggregate is not None:
        report.append(
            f"- weighted structural/directional support: "
            f"{aggregate:.1%}"
        )

    report.append("")
    report.append("## Governance checks")
    report.append("")

    if errors:
        report.append(f"- FAIL: {len(errors)} error(s)")
    else:
        report.append("- PASS: no temporal or dependency errors")

    if warnings:
        report.append(f"- warnings: {len(warnings)}")
    else:
        report.append("- warnings: 0")

    if errors:
        report.append("")
        report.append("### Errors")
        report.append("")
        for item in errors:
            report.append(f"- {item}")

    if warnings:
        report.append("")
        report.append("### Warnings")
        report.append("")
        for item in warnings:
            report.append(f"- {item}")

    REPORT_PATH.write_text(
        "\n".join(report) + "\n",
        encoding="utf-8",
    )

    print("\n".join(report))

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
