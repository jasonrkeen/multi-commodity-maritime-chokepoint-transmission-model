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
COVERAGE_PATH = OUTPUTS / "coverage_gap_matrix.csv"
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

VALID_USES = {
    "direct_point_error",
    "directional",
    "threshold",
    "mechanism",
    "contextual",
}

VALID_COVERAGE = {
    "COVERED",
    "PARTIAL",
    "GAP",
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
        eligible = is_true(
            row["eligible_for_quantitative_validation"]
        )

        if start > end:
            errors.append(
                f"{oid}: date_start is after date_end"
            )

        if temporal not in VALID_TEMPORAL:
            errors.append(
                f"{oid}: invalid temporal_classification "
                f"'{temporal}'"
            )

        if temporal == "prospective" and start < POST_FREEZE_START:
            errors.append(
                f"{oid}: marked prospective but begins {start}, "
                f"before clean post-freeze window "
                f"{POST_FREEZE_START}"
            )

        if start <= FREEZE_DATE < end and eligible:
            errors.append(
                f"{oid}: spans freeze but remains "
                f"quantitatively eligible"
            )

        if temporal == "mixed" and eligible:
            errors.append(
                f"{oid}: mixed-window observation cannot be "
                f"quantitatively eligible"
            )

        if temporal in {
            "retrospective",
            "contemporaneous",
        } and eligible:
            warnings.append(
                f"{oid}: {temporal} observation is "
                f"quantitatively eligible; review whether "
                f"this is intentional"
            )

    return errors, warnings


def validate_metrics(metrics, observations):
    errors = []
    warnings = []

    obs_by_id = {
        r["observation_id"]: r
        for r in observations
    }

    for row in metrics:
        metric_id = row["metric_id"]

        refs = [
            row.get(
                "source_observation_1", ""
            ).strip(),
            row.get(
                "source_observation_2", ""
            ).strip(),
        ]

        refs = [r for r in refs if r]

        for ref in refs:
            if ref not in obs_by_id:
                errors.append(
                    f"{metric_id}: references unknown "
                    f"observation {ref}"
                )

        if is_true(
            row["eligible_for_model_comparison"]
        ):
            for ref in refs:
                obs = obs_by_id.get(ref)

                if not obs:
                    continue

                if not is_true(
                    obs[
                        "eligible_for_quantitative_validation"
                    ]
                ):
                    errors.append(
                        f"{metric_id}: eligible metric "
                        f"depends on ineligible observation "
                        f"{ref}"
                    )

                if (
                    obs[
                        "temporal_classification"
                    ].strip()
                    != "prospective"
                ):
                    errors.append(
                        f"{metric_id}: eligible metric "
                        f"depends on non-prospective "
                        f"observation {ref}"
                    )

    return errors, warnings


def validate_scorecard(rows):
    errors = []
    warnings = []

    counts = {
        "SUPPORT": 0,
        "PARTIAL": 0,
        "CONTRADICT": 0,
        "NOT_COMPARABLE": 0,
    }

    for row in rows:
        sid = row["scorecard_id"].strip()
        assessment = row["assessment"].strip()
        validation_use = row.get(
            "validation_use", ""
        ).strip()

        if assessment not in VALID_ASSESSMENTS:
            errors.append(
                f"{sid}: invalid assessment "
                f"'{assessment}'"
            )
            continue

        counts[assessment] += 1

        if validation_use not in VALID_USES:
            errors.append(
                f"{sid}: invalid validation_use "
                f"'{validation_use}'"
            )

    return errors, warnings, counts


def validate_coverage(rows):
    errors = []

    counts = {
        "COVERED": 0,
        "PARTIAL": 0,
        "GAP": 0,
    }

    ids = set()

    for row in rows:
        domain_id = row["domain_id"].strip()
        status = row["current_status"].strip()

        if domain_id in ids:
            errors.append(
                f"Duplicate coverage domain: {domain_id}"
            )
        ids.add(domain_id)

        if status not in VALID_COVERAGE:
            errors.append(
                f"{domain_id}: invalid coverage status "
                f"'{status}'"
            )
            continue

        counts[status] += 1

    if len(rows) != 11:
        errors.append(
            f"Expected 11 validation domains; "
            f"found {len(rows)}"
        )

    return errors, counts


def main():
    observations = load_csv(OBS_PATH)
    metrics = load_csv(METRIC_PATH)
    scorecard = load_csv(SCORECARD_PATH)
    coverage = load_csv(COVERAGE_PATH)

    errors = []
    warnings = []

    e, w = validate_observations(observations)
    errors.extend(e)
    warnings.extend(w)

    e, w = validate_metrics(
        metrics,
        observations,
    )
    errors.extend(e)
    warnings.extend(w)

    e, w, score_counts = validate_scorecard(
        scorecard
    )
    errors.extend(e)
    warnings.extend(w)

    e, coverage_counts = validate_coverage(
        coverage
    )
    errors.extend(e)

    temporal_counts = {}

    for row in observations:
        key = row[
            "temporal_classification"
        ].strip()
        temporal_counts[key] = (
            temporal_counts.get(key, 0) + 1
        )

    eligible_count = sum(
        is_true(
            r[
                "eligible_for_quantitative_validation"
            ]
        )
        for r in observations
    )

    report = []

    report.append(
        "# Experiment A - Automated Validation"
    )
    report.append("")
    report.append(
        f"Freeze date: {FREEZE_DATE.isoformat()}"
    )
    report.append(
        f"Clean prospective window begins: "
        f"{POST_FREEZE_START.isoformat()}"
    )

    report.append("")
    report.append("## Observation counts")
    report.append("")

    for key in sorted(temporal_counts):
        report.append(
            f"- {key}: {temporal_counts[key]}"
        )

    report.append(
        "- quantitatively eligible observations: "
        f"{eligible_count}"
    )

    report.append("")
    report.append("## Scorecard")
    report.append("")

    for key, value in score_counts.items():
        report.append(f"- {key}: {value}")

    report.append(
        "- no aggregate numerical support "
        "percentage is reported"
    )

    report.append("")
    report.append(
        "## Validation-domain coverage"
    )
    report.append("")

    for key, value in coverage_counts.items():
        report.append(f"- {key}: {value}")

    report.append(
        "- no numerical domain-coverage index "
        "is reported"
    )

    report.append("")
    report.append("## Governance checks")
    report.append("")

    if errors:
        report.append(
            f"- FAIL: {len(errors)} error(s)"
        )
    else:
        report.append(
            "- PASS: no temporal, dependency, "
            "scorecard, or coverage errors"
        )

    if warnings:
        report.append(
            f"- warnings: {len(warnings)}"
        )
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
