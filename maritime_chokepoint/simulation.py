from __future__ import annotations

import numpy as np
import pandas as pd

from .io import ModelInputs
from .model import (
    run_ecological_externalities,
    run_scenario,
    summarize_ecological_externalities,
    summarize_scenario,
)


def _perturb_inputs(inputs: ModelInputs, rng: np.random.Generator) -> ModelInputs:
    commodities = inputs.commodities.copy()
    scenarios = inputs.scenarios.copy()
    exposures = inputs.exposures.copy()
    dependencies = inputs.dependencies.copy()
    sensors = inputs.sensors.copy()
    balancing = inputs.market_balancing.copy()
    crude_structure = inputs.crude_market_structure.copy()
    ecological = inputs.ecological_externalities.copy()

    elasticity_noise = rng.lognormal(mean=0.0, sigma=0.20, size=len(commodities))
    demand_noise = rng.lognormal(mean=0.0, sigma=0.22, size=len(commodities))
    commercial_inventory_noise = rng.lognormal(
        mean=0.0, sigma=0.25, size=len(commodities)
    )
    strategic_inventory_noise = rng.lognormal(
        mean=0.0, sigma=0.20, size=len(commodities)
    )
    market_noise = rng.lognormal(mean=0.0, sigma=0.12, size=len(commodities))
    cap_noise = rng.lognormal(mean=0.0, sigma=0.15, size=len(commodities))
    seasonal_noise = rng.lognormal(mean=0.0, sigma=0.25, size=len(commodities))
    commodities["short_run_adjustment_elasticity"] *= elasticity_noise
    commodities["demand_price_elasticity"] *= demand_noise
    commodities["commercial_inventory_days"] *= commercial_inventory_noise
    commodities["strategic_reserve_days"] *= strategic_inventory_noise
    commodities["market_tightness"] *= market_noise
    commodities["price_shock_cap_pct"] *= cap_noise
    commodities["seasonal_transmission_multiplier"] *= seasonal_noise

    exposure_noise = rng.lognormal(mean=0.0, sigma=0.12, size=len(exposures))
    reroute_noise = rng.normal(loc=1.0, scale=0.12, size=len(exposures))
    exposures["route_share_global"] = np.clip(
        exposures["route_share_global"] * exposure_noise, 0.0, 0.95
    )
    exposures["reroute_modifier"] = np.clip(
        exposures["reroute_modifier"] * reroute_noise, 0.25, 1.75
    )

    severity_noise = rng.normal(loc=1.0, scale=0.10, size=len(scenarios))
    duration_noise = rng.lognormal(mean=0.0, sigma=0.18, size=len(scenarios))
    scenarios["severity"] = np.clip(scenarios["severity"] * severity_noise, 0, 1)
    scenarios["duration_days"] = np.maximum(
        1, np.rint(scenarios["duration_days"] * duration_noise)
    ).astype(int)

    dependency_noise = rng.lognormal(mean=0.0, sigma=0.18, size=len(dependencies))
    dependencies["transmission_weight"] = np.clip(
        dependencies["transmission_weight"] * dependency_noise, 0, 1
    )
    bypass_noise = rng.lognormal(mean=0.0, sigma=0.15, size=len(balancing))
    release_noise = rng.lognormal(mean=0.0, sigma=0.25, size=len(balancing))
    response_noise = rng.lognormal(mean=0.0, sigma=0.25, size=len(balancing))
    balancing["bypass_capacity_share"] = np.clip(
        balancing["bypass_capacity_share"] * bypass_noise, 0, 1
    )
    balancing["strategic_release_share"] = np.clip(
        balancing["strategic_release_share"] * release_noise, 0, 1
    )
    balancing["external_supply_response_share"] = np.clip(
        balancing["external_supply_response_share"] * response_noise, 0, 1
    )
    if not sensors.empty:
        ais_noise = rng.normal(0.0, 0.035, size=len(sensors))
        sar_noise = rng.normal(0.0, 0.030, size=len(sensors))
        confidence_noise = rng.normal(0.0, 0.06, size=len(sensors))
        sensors["ais_declared_transit_index"] = np.clip(
            sensors["ais_declared_transit_index"] + ais_noise, 0, 1
        )
        sensors["sar_detected_transit_index"] = np.clip(
            sensors["sar_detected_transit_index"] + sar_noise, 0, 1
        )
        sensors["source_confidence"] = np.clip(
            sensors["source_confidence"] + confidence_noise, 0, 1
        )
        recall_noise = rng.normal(0.0, 0.05, size=len(sensors))
        sensors["detection_recall_assumption"] = np.clip(
            sensors["detection_recall_assumption"] + recall_noise, 0, 1
        )
    grade_noise = rng.lognormal(mean=0.0, sigma=0.15, size=len(crude_structure))
    channel_noise = rng.lognormal(mean=0.0, sigma=0.18, size=len(crude_structure))
    crude_structure["sour_dependent_market_share"] = np.clip(
        crude_structure["sour_dependent_market_share"] * grade_noise, 0.05, 1
    )
    crude_structure["segmented_channel_share"] = np.clip(
        crude_structure["segmented_channel_share"] * channel_noise, 0, 1
    )
    if not ecological.empty:
        severity_noise = rng.lognormal(mean=0.0, sigma=0.25, size=len(ecological))
        value_noise = rng.lognormal(mean=0.0, sigma=0.35, size=len(ecological))
        ecological["severity"] = np.clip(
            ecological["severity"] * severity_noise, 0, 1
        )
        ecological["annual_value_at_risk_usd"] *= value_noise
    return inputs.with_frames(
        commodities=commodities,
        exposures=exposures,
        scenarios=scenarios,
        market_balancing=balancing,
        dependencies=dependencies,
        sensors=sensors,
        crude_market_structure=crude_structure,
        ecological_externalities=ecological,
    )


def run_monte_carlo(
    inputs: ModelInputs,
    scenario_name: str,
    days: int,
    *,
    simulations: int,
    seed: int,
) -> pd.DataFrame:
    if simulations == 0:
        return pd.DataFrame()
    rng = np.random.default_rng(seed)
    records: list[pd.DataFrame] = []
    for draw in range(simulations):
        perturbed = _perturb_inputs(inputs, rng)
        daily = run_scenario(perturbed, scenario_name, days)
        summary = summarize_scenario(daily)
        summary["draw"] = draw
        records.append(
            summary[
                [
                    "draw",
                    "commodity",
                    "immediate_impact_usd",
                    "lagged_impact_usd",
                    "total_impact_usd",
                    "peak_price_shock_pct",
                    "peak_demand_reduction_pct",
                    "peak_implied_price_usd",
                    "peak_structural_supply_offset_pct",
                    "peak_no_structural_offsets_price_usd",
                    "peak_structural_moderation_usd",
                    "peak_regional_sour_spread_usd",
                    "peak_regional_sour_price_usd",
                ]
            ]
        )
    draws = pd.concat(records, ignore_index=True)

    catalog = inputs.scenario_catalog.loc[
        inputs.scenario_catalog["scenario"] == scenario_name
    ].iloc[0]
    target_low = float(catalog["brent_target_low_usd"])
    target_high = float(catalog["brent_target_high_usd"])

    output_rows = []
    for commodity, group in draws.groupby("commodity", sort=False):
        row: dict[str, float | str | int] = {
            "commodity": commodity,
            "simulations": simulations,
        }
        for source, label in [
            ("immediate_impact_usd", "immediate_impact_usd"),
            ("lagged_impact_usd", "lagged_impact_usd"),
            ("total_impact_usd", "total_impact_usd"),
            ("peak_price_shock_pct", "peak_price_shock_pct"),
            ("peak_demand_reduction_pct", "peak_demand_reduction_pct"),
            ("peak_implied_price_usd", "peak_implied_price_usd"),
            (
                "peak_structural_supply_offset_pct",
                "peak_structural_supply_offset_pct",
            ),
            (
                "peak_no_structural_offsets_price_usd",
                "peak_no_structural_offsets_price_usd",
            ),
            ("peak_structural_moderation_usd", "peak_structural_moderation_usd"),
            ("peak_regional_sour_spread_usd", "peak_regional_sour_spread_usd"),
            ("peak_regional_sour_price_usd", "peak_regional_sour_price_usd"),
        ]:
            unavailable = (
                commodity == "TOTAL"
                and source
                in {
                    "peak_price_shock_pct",
                    "peak_implied_price_usd",
                    "peak_no_structural_offsets_price_usd",
                    "peak_structural_moderation_usd",
                }
            ) or (
                commodity != "Crude oil"
                and source
                in {
                    "peak_regional_sour_spread_usd",
                    "peak_regional_sour_price_usd",
                }
            )
            if unavailable:
                row[f"p05_{label}"] = np.nan
                row[f"p50_{label}"] = np.nan
                row[f"p95_{label}"] = np.nan
            else:
                values = group[source].to_numpy()
                row[f"p05_{label}"] = float(np.quantile(values, 0.05))
                row[f"p50_{label}"] = float(np.quantile(values, 0.50))
                row[f"p95_{label}"] = float(np.quantile(values, 0.95))
        if commodity == "Crude oil":
            prices = group["peak_implied_price_usd"]
            row["target_band_below_share"] = float((prices < target_low).mean())
            row["target_band_within_share"] = float(
                prices.between(target_low, target_high, inclusive="both").mean()
            )
            row["target_band_above_share"] = float((prices > target_high).mean())
        else:
            row["target_band_below_share"] = np.nan
            row["target_band_within_share"] = np.nan
            row["target_band_above_share"] = np.nan
        output_rows.append(row)
    return pd.DataFrame(output_rows)


def run_ecological_monte_carlo(
    inputs: ModelInputs,
    scenario_name: str,
    days: int,
    *,
    simulations: int,
    seed: int,
) -> pd.DataFrame:
    if simulations == 0 or inputs.ecological_externalities.loc[
        inputs.ecological_externalities["scenario"] == scenario_name
    ].empty:
        return pd.DataFrame()
    rng = np.random.default_rng(seed + 10_000)
    records: list[dict[str, float | int | str]] = []
    for draw in range(simulations):
        perturbed = _perturb_inputs(inputs, rng)
        daily = run_ecological_externalities(perturbed, scenario_name, days)
        summary = summarize_ecological_externalities(daily)
        for _, row in summary.iterrows():
            records.append(
                {
                    "draw": draw,
                    "channel": str(row["channel"]),
                    "lagged_impact_usd": float(row["lagged_impact_usd"]),
                }
            )
        records.append(
            {
                "draw": draw,
                "channel": "TOTAL",
                "lagged_impact_usd": float(summary["lagged_impact_usd"].sum()),
            }
        )
    draws = pd.DataFrame(records)
    output = []
    for channel, group in draws.groupby("channel", sort=False):
        values = group["lagged_impact_usd"].to_numpy()
        output.append(
            {
                "channel": channel,
                "simulations": simulations,
                "p05_lagged_impact_usd": float(np.quantile(values, 0.05)),
                "p50_lagged_impact_usd": float(np.quantile(values, 0.50)),
                "p95_lagged_impact_usd": float(np.quantile(values, 0.95)),
            }
        )
    return pd.DataFrame(output)
