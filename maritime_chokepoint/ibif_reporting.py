"""Deterministic JSON/CSV/Markdown output for the replacement IBIF adapter."""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path

from .ibif_adapter import DIMENSIONS


def _escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def write_ibif_outputs(run_dir: Path, assessment: dict) -> tuple[Path, ...]:
    # Serialize everything before writing; reject nonstandard NaN JSON.
    payload = json.dumps(assessment, indent=2, allow_nan=False) + "\n"
    rows = []
    lines = ["# IBIF replacement assessment", "", assessment["provenance"], "",
             "**Experimental and uncalibrated. Escalation remains UNASSESSED.**", "",
             assessment["interpretation"], "",
             f"Scenario: {_escape(assessment['scenario'])}; horizon: {assessment['horizon_days']} days.",
             "", "Probability is separate from consequence and evidence quality. The sensor proxy is not overall analytic confidence.",
             "", "| Commodity | Probability | BCS /100 | Risk pressure /100 | Modeled exposure USD | Sensor proxy /100 |",
             "|---|---:|---:|---:|---:|---:|"]
    for item in assessment["commodities"]:
        row = {"schema_version": assessment["schema_version"], "scenario": assessment["scenario"],
               "horizon_days": assessment["horizon_days"],
               "calibration_status": assessment["calibration_status"]}
        row.update({k: v for k, v in item.items() if k not in ("scores", "raw_peaks", "sensitivity_bcs", "collection_gaps")})
        row.update({f"score_{k}": item["scores"][k] for k in DIMENSIONS})
        row.update({f"sensitivity_bcs_{k}": v for k, v in item["sensitivity_bcs"].items()})
        row["collection_gaps"] = "; ".join(item["collection_gaps"])
        rows.append(row)
        proxy = item["sensor_evidence_proxy"]
        proxy_text = "unavailable" if proxy is None else f"{proxy:.2f}"
        lines.append(f"| {_escape(item['commodity'])} | {item['scenario_probability']:.1%} | {item['business_consequence_score']:.2f} | {item['risk_pressure']:.2f} | {item['gross_modeled_exposure_usd']:,.2f} | {proxy_text} |")
    lines += ["", "## Assumptions and collection gaps", "",
              "Dimensions use independent horizon peaks; those peaks may occur on different days. Impact is scaled to horizon commodity market value, with a cap at 100; this is an arbitrary consequence scale, not a loss fraction. No portfolio BCS is computed.", "",
              f"Weights: {json.dumps(assessment['weights'], sort_keys=True)}.",
              f"Impact scale multiplier: {assessment['impact_market_multiple']}.",
              f"Sensor source status: {_escape(', '.join(assessment['sensor_source_statuses']) or 'unknown')}.", ""]
    for item in assessment["commodities"]:
        lines += [f"### {_escape(item['commodity'])}", "",
                  f"Sensitivity BCS (not calibrated alternatives): {json.dumps(item['sensitivity_bcs'], sort_keys=True)}.", ""]
        lines += [f"- {_escape(gap)}" for gap in item["collection_gaps"]]
        lines += [""]
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    paths = tuple(Path(run_dir) / f"ibif_assessment.{ext}" for ext in ("json", "csv", "md"))
    Path(run_dir).mkdir(parents=True, exist_ok=True)
    for path, text in zip(paths, (payload, buffer.getvalue(), "\n".join(lines))):
        path.write_text(text, encoding="utf-8")
    return paths
