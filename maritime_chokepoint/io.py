from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

import pandas as pd


HEAVY_SOUR_AVAILABILITY_COLUMNS = (
    "upstream_availability_share",
    "grid_availability_share",
    "terminal_availability_share",
)


@dataclass(frozen=True)
class ModelInputs:
    commodities: pd.DataFrame
    chokepoints: pd.DataFrame
    exposures: pd.DataFrame
    scenarios: pd.DataFrame
    scenario_catalog: pd.DataFrame
    market_balancing: pd.DataFrame
    crude_market_structure: pd.DataFrame
    ecological_externalities: pd.DataFrame
    dependencies: pd.DataFrame
    sensors: pd.DataFrame
    validation_events: pd.DataFrame
    sources: pd.DataFrame

    def with_frames(
        self,
        *,
        commodities: pd.DataFrame | None = None,
        chokepoints: pd.DataFrame | None = None,
        exposures: pd.DataFrame | None = None,
        scenarios: pd.DataFrame | None = None,
        scenario_catalog: pd.DataFrame | None = None,
        market_balancing: pd.DataFrame | None = None,
        crude_market_structure: pd.DataFrame | None = None,
        ecological_externalities: pd.DataFrame | None = None,
        dependencies: pd.DataFrame | None = None,
        sensors: pd.DataFrame | None = None,
        validation_events: pd.DataFrame | None = None,
    ) -> "ModelInputs":
        return replace(
            self,
            commodities=self.commodities if commodities is None else commodities,
            chokepoints=self.chokepoints if chokepoints is None else chokepoints,
            exposures=self.exposures if exposures is None else exposures,
            scenarios=self.scenarios if scenarios is None else scenarios,
            scenario_catalog=(
                self.scenario_catalog if scenario_catalog is None else scenario_catalog
            ),
            market_balancing=(
                self.market_balancing
                if market_balancing is None
                else market_balancing
            ),
            crude_market_structure=(
                self.crude_market_structure
                if crude_market_structure is None
                else crude_market_structure
            ),
            ecological_externalities=(
                self.ecological_externalities
                if ecological_externalities is None
                else ecological_externalities
            ),
            dependencies=self.dependencies if dependencies is None else dependencies,
            sensors=self.sensors if sensors is None else sensors,
            validation_events=(
                self.validation_events
                if validation_events is None
                else validation_events
            ),
        )


def _read(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required input not found: {path}")
    return pd.read_csv(path)


def _read_crude_market_structure(path: Path) -> pd.DataFrame:
    frame = _read(path)
    for column in HEAVY_SOUR_AVAILABILITY_COLUMNS:
        if column not in frame.columns:
            frame[column] = 1.0
    return frame


def load_inputs(input_dir: Path) -> ModelInputs:
    inputs = ModelInputs(
        commodities=_read(input_dir / "commodities.csv"),
        chokepoints=_read(input_dir / "chokepoints.csv"),
        exposures=_read(input_dir / "exposure_matrix.csv"),
        scenarios=_read(input_dir / "scenarios.csv"),
        scenario_catalog=_read(input_dir / "scenario_catalog.csv"),
        market_balancing=_read(input_dir / "market_balancing.csv"),
        crude_market_structure=_read_crude_market_structure(
            input_dir / "crude_market_structure.csv"
        ),
        ecological_externalities=_read(
            input_dir / "ecological_externalities.csv"
        ),
        dependencies=_read(input_dir / "chokepoint_dependencies.csv"),
        sensors=_read(input_dir / "sensor_signals.csv"),
        validation_events=_read(input_dir / "validation_events.csv"),
        sources=_read(input_dir / "source_register.csv"),
    )
    validate_inputs(inputs)
    return inputs


def validate_inputs(inputs: ModelInputs) -> None:
    required = {
        "commodities": {
            "commodity",
            "annual_market_value_usd",
            "annual_downstream_value_at_risk_usd",
            "short_run_adjustment_elasticity",
            "demand_price_elasticity",
            "demand_adjustment_days",
            "demand_recovery_half_life_days",
            "max_demand_reduction_share",
            "market_tightness",
            "price_shock_cap_pct",
            "exposed_spend_share",
            "commercial_inventory_days",
            "strategic_reserve_days",
            "lag_onset_days",
            "lag_adjustment_days",
            "recovery_half_life_days",
            "downstream_input_cost_share",
            "availability_multiplier",
            "seasonal_lag_days",
            "seasonal_transmission_multiplier",
            "substitution_rate_per_day",
            "max_substitution_share",
        },
        "chokepoints": {
            "chokepoint",
            "base_reroute_share",
            "reroute_ramp_days",
            "reroute_cost_uplift_pct",
            "insurance_uplift_pct",
        },
        "exposures": {
            "commodity",
            "chokepoint",
            "route_group",
            "route_share_global",
            "reroute_modifier",
        },
        "scenarios": {
            "scenario",
            "chokepoint",
            "start_day",
            "duration_days",
            "severity",
            "recovery_days",
        },
        "scenario_catalog": {
            "scenario",
            "scenario_probability",
            "use_sensor_fusion",
            "base_market_risk_premium_pct",
            "initial_demand_reduction_share",
            "policy_demand_reduction_share",
        },
        "market_balancing": {
            "scenario",
            "commodity",
            "bypass_capacity_share",
            "bypass_ramp_days",
            "strategic_release_share",
            "strategic_release_start_day",
            "strategic_release_ramp_days",
            "strategic_release_duration_days",
            "strategic_release_decay_half_life_days",
            "external_supply_response_share",
            "external_supply_response_start_day",
            "external_supply_response_ramp_days",
            "external_supply_response_decay_half_life_days",
        },
        "crude_market_structure": {
            "scenario",
            "sour_dependent_market_share",
            "alternative_grade_compatibility_share",
            "segmented_channel_share",
            "panic_premium_insulation_share",
            "reassigned_heavy_sour_share",
            "upstream_availability_share",
            "grid_availability_share",
            "terminal_availability_share",
            "sour_spread_sensitivity_usd",
            "sour_spread_cap_usd",
            "logistics_friction_premium_usd",
        },
        "ecological_externalities": {
            "scenario",
            "channel",
            "start_day",
            "duration_days",
            "severity",
            "lag_onset_days",
            "adjustment_days",
            "recovery_half_life_days",
            "annual_value_at_risk_usd",
            "confidence",
        },
        "dependencies": {
            "source_chokepoint",
            "target_chokepoint",
            "transmission_weight",
            "lag_days",
        },
        "sensors": {
            "scenario",
            "chokepoint",
            "day",
            "ais_declared_transit_index",
            "sar_detected_transit_index",
            "ballast_repositioning_z",
            "thermal_anomaly_z",
            "radar_wake_persistence_z",
            "source_confidence",
            "identity_resolution_share",
            "median_ais_staleness_hours",
            "detection_recall_assumption",
            "validation_status",
            "source_type",
        },
    }
    for name, columns in required.items():
        frame = getattr(inputs, name)
        missing = columns - set(frame.columns)
        if missing:
            raise ValueError(f"{name}.csv missing columns: {sorted(missing)}")

    if inputs.commodities["commodity"].duplicated().any():
        raise ValueError("Commodity names must be unique")
    if inputs.chokepoints["chokepoint"].duplicated().any():
        raise ValueError("Chokepoint names must be unique")
    if inputs.scenario_catalog["scenario"].duplicated().any():
        raise ValueError("Scenario catalog names must be unique")
    if inputs.exposures.duplicated(["commodity", "chokepoint"]).any():
        raise ValueError("Exposure commodity/chokepoint pairs must be unique")
    if inputs.market_balancing.duplicated(["scenario", "commodity"]).any():
        raise ValueError("Market-balancing scenario/commodity pairs must be unique")
    if inputs.crude_market_structure["scenario"].duplicated().any():
        raise ValueError("Crude-market structure scenario names must be unique")
    if inputs.ecological_externalities.duplicated(["scenario", "channel"]).any():
        raise ValueError("Ecological scenario/channel pairs must be unique")

    commodity_names = set(inputs.commodities["commodity"])
    chokepoint_names = set(inputs.chokepoints["chokepoint"])
    catalog_names = set(inputs.scenario_catalog["scenario"])
    if not set(inputs.exposures["commodity"]).issubset(commodity_names):
        raise ValueError("Exposure matrix contains an unknown commodity")
    if not set(inputs.exposures["chokepoint"]).issubset(chokepoint_names):
        raise ValueError("Exposure matrix contains an unknown chokepoint")
    if not set(inputs.scenarios["chokepoint"]).issubset(chokepoint_names):
        raise ValueError("Scenarios contain an unknown chokepoint")
    if not set(inputs.scenarios["scenario"]).issubset(catalog_names):
        raise ValueError("Scenario events are missing from scenario_catalog.csv")
    if not set(inputs.market_balancing["scenario"]).issubset(catalog_names):
        raise ValueError("Market-balancing rows contain an unknown scenario")
    if not set(inputs.market_balancing["commodity"]).issubset(commodity_names):
        raise ValueError("Market-balancing rows contain an unknown commodity")
    if set(inputs.crude_market_structure["scenario"]) != catalog_names:
        raise ValueError(
            "crude_market_structure.csv must contain exactly one row per scenario"
        )
    if not set(inputs.ecological_externalities["scenario"]).issubset(catalog_names):
        raise ValueError("Ecological rows contain an unknown scenario")
    expected_balancing = {
        (scenario, commodity)
        for scenario in catalog_names
        for commodity in commodity_names
    }
    actual_balancing = set(
        inputs.market_balancing[["scenario", "commodity"]].itertuples(
            index=False, name=None
        )
    )
    missing_balancing = expected_balancing - actual_balancing
    if missing_balancing:
        raise ValueError(
            "Market-balancing rows missing scenario/commodity pairs: "
            f"{sorted(missing_balancing)}"
        )
    dependency_nodes = set(inputs.dependencies["source_chokepoint"]) | set(
        inputs.dependencies["target_chokepoint"]
    )
    if not dependency_nodes.issubset(chokepoint_names):
        raise ValueError("Dependency matrix contains an unknown chokepoint")
    if not set(inputs.sensors["scenario"]).issubset(catalog_names):
        raise ValueError("Sensor signals contain an unknown scenario")
    if not set(inputs.sensors["chokepoint"]).issubset(chokepoint_names):
        raise ValueError("Sensor signals contain an unknown chokepoint")

    bounded = [
        (inputs.exposures, "route_share_global"),
        (inputs.chokepoints, "base_reroute_share"),
        (inputs.scenarios, "severity"),
        (inputs.scenario_catalog, "scenario_probability"),
        (inputs.scenario_catalog, "use_sensor_fusion"),
        (inputs.scenario_catalog, "initial_demand_reduction_share"),
        (inputs.market_balancing, "bypass_capacity_share"),
        (inputs.market_balancing, "strategic_release_share"),
        (inputs.market_balancing, "external_supply_response_share"),
        (inputs.dependencies, "transmission_weight"),
        (inputs.commodities, "max_substitution_share"),
        (inputs.commodities, "max_demand_reduction_share"),
        (inputs.sensors, "ais_declared_transit_index"),
        (inputs.sensors, "sar_detected_transit_index"),
        (inputs.sensors, "source_confidence"),
        (inputs.sensors, "identity_resolution_share"),
        (inputs.sensors, "detection_recall_assumption"),
        (inputs.crude_market_structure, "sour_dependent_market_share"),
        (inputs.crude_market_structure, "alternative_grade_compatibility_share"),
        (inputs.crude_market_structure, "segmented_channel_share"),
        (inputs.crude_market_structure, "panic_premium_insulation_share"),
        (inputs.crude_market_structure, "reassigned_heavy_sour_share"),
        (inputs.crude_market_structure, "upstream_availability_share"),
        (inputs.crude_market_structure, "grid_availability_share"),
        (inputs.crude_market_structure, "terminal_availability_share"),
        (inputs.ecological_externalities, "severity"),
        (inputs.ecological_externalities, "confidence"),
    ]
    for frame, column in bounded:
        if not frame[column].between(0, 1).all():
            raise ValueError(f"{column} must be between 0 and 1")

    nonnegative_balancing = [
        "bypass_ramp_days",
        "strategic_release_start_day",
        "strategic_release_ramp_days",
        "strategic_release_duration_days",
        "strategic_release_decay_half_life_days",
        "external_supply_response_start_day",
        "external_supply_response_ramp_days",
        "external_supply_response_decay_half_life_days",
    ]
    for column in nonnegative_balancing:
        if (inputs.market_balancing[column] < 0).any():
            raise ValueError(f"{column} cannot be negative")

    if (inputs.sensors["median_ais_staleness_hours"] < 0).any():
        raise ValueError("median_ais_staleness_hours cannot be negative")
    valid_statuses = {"unvalidated", "partial_backtest", "backtested"}
    if not set(inputs.sensors["validation_status"]).issubset(valid_statuses):
        raise ValueError(
            "validation_status must be unvalidated, partial_backtest, or backtested"
        )
    nonnegative_externality = [
        "start_day",
        "duration_days",
        "lag_onset_days",
        "adjustment_days",
        "recovery_half_life_days",
        "annual_value_at_risk_usd",
    ]
    for column in nonnegative_externality:
        if (inputs.ecological_externalities[column] < 0).any():
            raise ValueError(f"{column} cannot be negative")
