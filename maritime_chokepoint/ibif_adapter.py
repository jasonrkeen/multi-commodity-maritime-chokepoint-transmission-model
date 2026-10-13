"""Experimental reporting-only replacement; not the unrecovered IBIF v0.2."""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
import pandas as pd

VERSION = "replacement-0.1.0"
BASE_COMMIT = "6c1cc646fa9486817fe5d8c9f1f6fdd9eadfa451"
DIMENSIONS = ("exposure", "dependency", "vulnerability", "transmission", "impact")
REQUIRED = (
    "scenario_probability", "active_route_weight_pct", "supply_loss_pct",
    "dependency_induced_severity", "balanced_supply_loss_pct",
    "net_market_gap_pct", "physical_shortage_pct", "inventory_remaining_days",
    "direct_disruption_severity", "lag_state_pct", "total_impact_usd",
)


@dataclass(frozen=True)
class ScoringConfig:
    """Explicit analyst choices; sensitivity is not empirical calibration."""

    weights: tuple[float, ...] = (0.20, 0.20, 0.20, 0.15, 0.25)
    impact_market_multiple: float = 1.0

    def __post_init__(self) -> None:
        if (len(self.weights) != 5
                or not all(math.isfinite(w) and w >= 0 for w in self.weights)
                or not math.isclose(sum(self.weights), 1.0, abs_tol=1e-12)):
            raise ValueError("Five finite nonnegative weights must sum to one")
        if not math.isfinite(self.impact_market_multiple) or self.impact_market_multiple <= 0:
            raise ValueError("impact_market_multiple must be finite and positive")


def _numeric(frame: pd.DataFrame, columns: tuple[str, ...]) -> None:
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")
    for column in columns:
        if (not pd.api.types.is_numeric_dtype(frame[column])
                or pd.api.types.is_bool_dtype(frame[column])):
            raise ValueError(f"{column} must have a numeric dtype")
        values = frame[column].to_numpy(dtype=float)
        if not np.isfinite(values).all() or (values < 0).any():
            raise ValueError(f"{column} must be finite and nonnegative")


def _score(value: float) -> float:
    return 100.0 * min(1.0, max(0.0, value))


def build_ibif_assessment(
    daily: pd.DataFrame,
    commodities: pd.DataFrame,
    *,
    sensor_fusion_active: bool,
    source_statuses: tuple[str, ...] = (),
    config: ScoringConfig | None = None,
) -> dict:
    """Read complete deterministic daily output; never run or modify the model.

    Scores describe each commodity over the supplied horizon. Independent peak
    components need not occur on the same day. There is no portfolio BCS, alert
    threshold, organizational-loss estimate, or overall analytic-confidence score.
    """
    config = config or ScoringConfig()
    if daily.empty or daily.columns.duplicated().any():
        raise ValueError("Daily output must be nonempty with unique columns")
    if not {"scenario", "commodity", "day"}.issubset(daily.columns):
        raise ValueError("scenario, commodity and day are required")
    if daily[["scenario", "commodity"]].isna().any().any():
        raise ValueError("Scenario and commodity identifiers cannot be missing")
    if daily["scenario"].nunique() != 1 or daily.duplicated(["commodity", "day"]).any():
        raise ValueError("Expected one scenario and unique commodity/day rows")
    _numeric(daily, REQUIRED + ("day",))
    probabilities = daily["scenario_probability"].unique()
    if len(probabilities) != 1 or not 0 <= float(probabilities[0]) <= 1:
        raise ValueError("Scenario probability must be one constant fraction in [0, 1]")
    probability = float(probabilities[0])
    if ("commodity" not in commodities or commodities.columns.duplicated().any()
            or commodities["commodity"].isna().any()
            or commodities["commodity"].duplicated().any()):
        raise ValueError("Commodity parameters require unique nonmissing identifiers")
    _numeric(commodities, ("annual_market_value_usd", "commercial_inventory_days",
                           "strategic_reserve_days"))
    if set(daily["commodity"]) != set(commodities["commodity"]):
        raise ValueError("Daily output must cover exactly the parameter commodities")
    days = sorted(daily["day"].unique())
    if days != list(range(len(days))):
        raise ValueError("Expected complete integer days starting at zero")
    sensor_columns = ("sensor_confidence", "track_continuity_confidence")
    if sensor_fusion_active:
        _numeric(daily, sensor_columns)
        if (daily[list(sensor_columns)] > 1).any().any():
            raise ValueError("Sensor confidence inputs must be fractions in [0, 1]")
    parameters = commodities.set_index("commodity")
    records = []
    for name, group in daily.groupby("commodity", sort=True):
        if sorted(group["day"].tolist()) != days:
            raise ValueError("Each commodity requires the same complete horizon")
        group = group.sort_values("day")
        params = parameters.loc[name]
        initial_inventory = float(params["commercial_inventory_days"] + params["strategic_reserve_days"])
        market_scale = float(params["annual_market_value_usd"]) * len(days) / 365.0
        if market_scale <= 0 or not math.isfinite(market_scale):
            raise ValueError("Horizon market-value scale must be finite and positive")
        peak = lambda column: float(group[column].max())
        total = float(group["total_impact_usd"].sum())
        if not math.isfinite(total):
            raise ValueError("Total modeled exposure must be finite")
        depletion = (max(0.0, 1.0 - float(group["inventory_remaining_days"].min()) / initial_inventory)
                     if initial_inventory > 0 else None)
        vulnerability_parts = [_score(peak("net_market_gap_pct")), _score(peak("physical_shortage_pct"))]
        if depletion is not None:
            vulnerability_parts.append(_score(depletion))
        raw_impact_ratio = total / market_scale / config.impact_market_multiple
        if not math.isfinite(raw_impact_ratio):
            raise ValueError("Impact normalization overflow")
        scores = {
            "exposure": (_score(peak("active_route_weight_pct")) + _score(peak("supply_loss_pct"))) / 2,
            "dependency": (_score(peak("dependency_induced_severity")) + _score(peak("balanced_supply_loss_pct"))) / 2,
            "vulnerability": sum(vulnerability_parts) / len(vulnerability_parts),
            "transmission": sum(_score(peak(c)) for c in ("direct_disruption_severity", "dependency_induced_severity", "lag_state_pct")) / 3,
            "impact": _score(raw_impact_ratio),
        }
        bcs = sum(w * scores[d] for w, d in zip(config.weights, DIMENSIONS))
        equal_weight = sum(scores.values()) / 5
        impact_heavy = sum(w * scores[d] for w, d in zip((.15, .15, .15, .15, .40), DIMENSIONS))
        gaps = ["No organizational exposure mapping or observed-outcome calibration",
                "No validated operational escalation thresholds"]
        if depletion is None:
            gaps.append("Initial inventory is zero: depletion component omitted; other vulnerability components equally weighted")
        if not sensor_fusion_active:
            gaps.append("Sensor fusion inactive: sensor evidence proxy is unavailable")
        if not source_statuses:
            gaps.append("Sensor source status not supplied")
        elif any("synthetic" in str(s).lower() for s in source_statuses):
            gaps.append("Synthetic sensor demonstration; not operational evidence")
        records.append({
            "commodity": str(name), "scenario_probability": probability,
            "gross_modeled_exposure_usd": total,
            "probability_weighted_exposure_usd": total * probability,
            "horizon_market_value_scale_usd": market_scale,
            "impact_normalization_ratio": raw_impact_ratio,
            "impact_score_saturated": raw_impact_ratio >= 1,
            "initial_inventory_days": initial_inventory,
            "inventory_depletion_fraction": depletion,
            "raw_peaks": {c: peak(c) for c in REQUIRED if c not in ("scenario_probability", "inventory_remaining_days", "total_impact_usd")},
            "scores": scores, "business_consequence_score": bcs,
            "risk_pressure": probability * bcs,
            "sensor_evidence_proxy": (float(group[list(sensor_columns)].min(axis=1).mean()) * 100
                                      if sensor_fusion_active else None),
            "analytic_confidence": None, "escalation_status": "UNASSESSED",
            "sensitivity_bcs": {"equal_weights": equal_weight, "impact_heavy": impact_heavy,
                                "half_impact_scale": bcs + config.weights[4] * (_score(raw_impact_ratio * 2) - scores["impact"]),
                                "double_impact_scale": bcs + config.weights[4] * (_score(raw_impact_ratio / 2) - scores["impact"])},
            "collection_gaps": gaps,
        })
    return {
        "schema_version": VERSION, "provenance": "Explicit replacement; original IBIF v0.2 package unrecovered",
        "target_base_commit": BASE_COMMIT, "scenario": str(daily["scenario"].iloc[0]),
        "horizon_days": len(days), "scenario_probability": probability,
        "calibration_status": "EXPERIMENTAL_UNCALIBRATED",
        "interpretation": "Gross modeled exposure; not realized loss or net GDP loss. Per-commodity scores are heuristic horizon descriptors, not forecasts or escalation decisions.",
        "sensor_fusion_active": bool(sensor_fusion_active),
        "sensor_source_statuses": sorted(set(str(s) for s in source_statuses)),
        "weights": dict(zip(DIMENSIONS, config.weights)),
        "impact_market_multiple": config.impact_market_multiple,
        "commodities": records,
    }
