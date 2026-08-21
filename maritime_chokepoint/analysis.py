from __future__ import annotations

import math
from itertools import product
from typing import Iterable

import pandas as pd

from .io import ModelInputs
from .model import (
    run_ecological_externalities,
    run_scenario,
    summarize_ecological_externalities,
    summarize_scenario,
)


def target_band_status(value: float, low: float, high: float) -> tuple[str, float]:
    """Return the comparator status and signed distance to the nearest band edge."""
    if value < low:
        return "below_target_band", value - low
    if value > high:
        return "above_target_band", value - high
    return "within_target_band", 0.0


def build_scenario_comparison(inputs: ModelInputs, days: int) -> pd.DataFrame:
    """Build a deterministic, side-by-side view of every catalog scenario."""
    rows: list[dict[str, float | str]] = []
    for _, catalog in inputs.scenario_catalog.iterrows():
        scenario = str(catalog["scenario"])
        summary = summarize_scenario(run_scenario(inputs, scenario, days))
        ecological_summary = summarize_ecological_externalities(
            run_ecological_externalities(inputs, scenario, days)
        )
        total = summary.loc[summary["commodity"] == "TOTAL"].iloc[0]
        crude = summary.loc[summary["commodity"] == "Crude oil"].iloc[0]
        low = float(catalog["brent_target_low_usd"])
        high = float(catalog["brent_target_high_usd"])
        peak = float(crude["peak_implied_price_usd"])
        status, distance = target_band_status(peak, low, high)
        total_impact = float(total["total_impact_usd"])
        ecological_impact = (
            float(ecological_summary["lagged_impact_usd"].sum())
            if not ecological_summary.empty
            else 0.0
        )
        rows.append(
            {
                "scenario": scenario,
                "scenario_probability": float(catalog["scenario_probability"]),
                "gross_exposure_usd": total_impact,
                "immediate_impact_usd": float(total["immediate_impact_usd"]),
                "lagged_impact_usd": float(total["lagged_impact_usd"]),
                "lagged_impact_share": (
                    float(total["lagged_impact_usd"]) / total_impact
                    if total_impact
                    else 0.0
                ),
                "probability_weighted_impact_usd": float(
                    total["probability_weighted_impact_usd"]
                ),
                "peak_brent_usd": peak,
                "peak_regional_sour_price_usd": float(
                    crude["peak_regional_sour_price_usd"]
                ),
                "peak_regional_sour_spread_usd": float(
                    crude["peak_regional_sour_spread_usd"]
                ),
                "minimum_heavy_sour_enabling_availability_pct": float(
                    crude["minimum_heavy_sour_enabling_availability_pct"]
                ),
                "peak_effective_reassigned_heavy_sour_share_pct": float(
                    crude["peak_effective_reassigned_heavy_sour_share_pct"]
                ),
                "static_demand_peak_brent_usd": float(
                    crude["peak_static_demand_price_usd"]
                ),
                "maximum_demand_moderation_usd": float(
                    crude["peak_demand_moderation_usd"]
                ),
                "peak_crude_supply_loss_pct": float(
                    crude["peak_supply_loss_pct"]
                ),
                "peak_structural_supply_offset_pct": float(
                    crude["peak_structural_supply_offset_pct"]
                ),
                "peak_balanced_crude_supply_loss_pct": float(
                    crude["peak_balanced_supply_loss_pct"]
                ),
                "peak_crude_demand_reduction_pct": float(
                    crude["peak_demand_reduction_pct"]
                ),
                "peak_apparent_benchmark_demand_reduction_pct": float(
                    crude["peak_apparent_benchmark_demand_reduction_pct"]
                ),
                "peak_segmented_channel_shift_pct": float(
                    crude["peak_segmented_channel_shift_pct"]
                ),
                "separate_ecological_externality_usd": ecological_impact,
                "separate_probability_weighted_ecological_usd": (
                    ecological_impact * float(catalog["scenario_probability"])
                ),
                "no_structural_offsets_peak_brent_usd": float(
                    crude["peak_no_structural_offsets_price_usd"]
                ),
                "maximum_structural_moderation_usd": float(
                    crude["peak_structural_moderation_usd"]
                ),
                "analyst_target_low_usd": low,
                "analyst_target_high_usd": high,
                "target_check_status": status,
                "distance_to_band_usd": distance,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["gross_exposure_usd", "scenario"], ascending=[False, True]
    ).reset_index(drop=True)


def run_calibration_sensitivity(
    inputs: ModelInputs,
    scenario_name: str,
    days: int,
    *,
    levels: Iterable[float] = (0.75, 1.0, 1.25),
) -> pd.DataFrame:
    """Run a transparent grid without mutating or auto-selecting the baseline."""
    grid_levels = tuple(float(level) for level in levels)
    if not grid_levels or any(level <= 0 for level in grid_levels):
        raise ValueError("Calibration levels must contain positive values")

    catalog_rows = inputs.scenario_catalog.loc[
        inputs.scenario_catalog["scenario"] == scenario_name
    ]
    if catalog_rows.empty:
        raise ValueError(f"Scenario catalog entry not found: {scenario_name}")
    base_catalog = catalog_rows.iloc[0]
    low = float(base_catalog["brent_target_low_usd"])
    high = float(base_catalog["brent_target_high_usd"])
    rows: list[dict[str, float | str | bool | int]] = []

    for draw_id, multipliers in enumerate(product(grid_levels, repeat=4)):
        demand_elasticity, demand_days, structural_supply, risk_premium = multipliers
        commodities = inputs.commodities.copy().astype(
            {
                "demand_adjustment_days": float,
            }
        )
        crude_mask = commodities["commodity"] == "Crude oil"
        commodities.loc[crude_mask, "demand_price_elasticity"] *= demand_elasticity
        commodities.loc[crude_mask, "demand_adjustment_days"] *= demand_days

        balancing = inputs.market_balancing.copy()
        balance_mask = (
            (balancing["scenario"] == scenario_name)
            & (balancing["commodity"] == "Crude oil")
        )
        for column in [
            "bypass_capacity_share",
            "strategic_release_share",
            "external_supply_response_share",
        ]:
            balancing.loc[balance_mask, column] *= structural_supply

        catalog = inputs.scenario_catalog.copy()
        scenario_mask = catalog["scenario"] == scenario_name
        catalog.loc[scenario_mask, "base_market_risk_premium_pct"] *= risk_premium
        perturbed = inputs.with_frames(
            commodities=commodities,
            scenario_catalog=catalog,
            market_balancing=balancing,
        )
        summary = summarize_scenario(run_scenario(perturbed, scenario_name, days))
        crude = summary.loc[summary["commodity"] == "Crude oil"].iloc[0]
        total = summary.loc[summary["commodity"] == "TOTAL"].iloc[0]
        peak = float(crude["peak_implied_price_usd"])
        status, distance = target_band_status(peak, low, high)
        assumption_distance = sum(abs(math.log(value)) for value in multipliers)
        rows.append(
            {
                "grid_run": draw_id,
                "scenario": scenario_name,
                "demand_price_elasticity_multiplier": demand_elasticity,
                "demand_adjustment_days_multiplier": demand_days,
                "structural_supply_offset_multiplier": structural_supply,
                "market_risk_premium_multiplier": risk_premium,
                "is_baseline": all(abs(value - 1.0) < 1e-12 for value in multipliers),
                "assumption_distance_score": assumption_distance,
                "peak_brent_usd": peak,
                "static_demand_peak_brent_usd": float(
                    crude["peak_static_demand_price_usd"]
                ),
                "maximum_demand_moderation_usd": float(
                    crude["peak_demand_moderation_usd"]
                ),
                "maximum_structural_moderation_usd": float(
                    crude["peak_structural_moderation_usd"]
                ),
                "peak_structural_supply_offset_pct": float(
                    crude["peak_structural_supply_offset_pct"]
                ),
                "gross_exposure_usd": float(total["total_impact_usd"]),
                "immediate_impact_usd": float(total["immediate_impact_usd"]),
                "lagged_impact_usd": float(total["lagged_impact_usd"]),
                "peak_physical_shortage_pct": float(
                    crude["peak_physical_shortage_pct"]
                ),
                "analyst_target_low_usd": low,
                "analyst_target_high_usd": high,
                "target_check_status": status,
                "distance_to_band_usd": distance,
                "absolute_distance_to_band_usd": abs(distance),
            }
        )

    output = pd.DataFrame(rows)
    order = output.sort_values(
        ["absolute_distance_to_band_usd", "assumption_distance_score", "grid_run"]
    ).index
    output.loc[order, "diagnostic_rank"] = range(1, len(output) + 1)
    return output.sort_values("grid_run").reset_index(drop=True)


def summarize_calibration(grid: pd.DataFrame) -> pd.DataFrame:
    """Summarize sensitivity evidence while keeping the baseline decision explicit."""
    if grid.empty:
        raise ValueError("Calibration grid cannot be empty")
    baseline_rows = grid.loc[grid["is_baseline"]]
    baseline = baseline_rows.iloc[0] if not baseline_rows.empty else None
    nearest = grid.sort_values(
        ["absolute_distance_to_band_usd", "assumption_distance_score", "grid_run"]
    ).iloc[0]
    return pd.DataFrame(
        [
            {
                "scenario": grid["scenario"].iloc[0],
                "grid_runs": len(grid),
                "in_band_runs": int(
                    (grid["target_check_status"] == "within_target_band").sum()
                ),
                "in_band_share": float(
                    (grid["target_check_status"] == "within_target_band").mean()
                ),
                "minimum_peak_brent_usd": float(grid["peak_brent_usd"].min()),
                "maximum_peak_brent_usd": float(grid["peak_brent_usd"].max()),
                "baseline_peak_brent_usd": (
                    float(baseline["peak_brent_usd"])
                    if baseline is not None
                    else float("nan")
                ),
                "baseline_target_status": (
                    str(baseline["target_check_status"])
                    if baseline is not None
                    else "baseline_not_in_grid"
                ),
                "nearest_peak_brent_usd": float(nearest["peak_brent_usd"]),
                "nearest_demand_price_elasticity_multiplier": float(
                    nearest["demand_price_elasticity_multiplier"]
                ),
                "nearest_demand_adjustment_days_multiplier": float(
                    nearest["demand_adjustment_days_multiplier"]
                ),
                "nearest_structural_supply_offset_multiplier": float(
                    nearest["structural_supply_offset_multiplier"]
                ),
                "nearest_market_risk_premium_multiplier": float(
                    nearest["market_risk_premium_multiplier"]
                ),
                "governance_decision": "investigate_no_automatic_recalibration",
                "governance_note": (
                    "The analyst band is an external comparator; sensitivity results "
                    "do not overwrite baseline assumptions."
                ),
            }
        ]
    )
