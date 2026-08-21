from __future__ import annotations

import math

import numpy as np
import pandas as pd

from .io import ModelInputs
from .signals import build_sensor_panel


def disruption_envelope(day: int, event: pd.Series) -> float:
    start = int(event["start_day"])
    duration = int(event["duration_days"])
    severity = float(event["severity"])
    recovery = max(float(event["recovery_days"]), 0.0)
    if day < start:
        return 0.0
    if day < start + duration:
        return severity
    if recovery == 0:
        return 0.0
    elapsed = day - (start + duration)
    return severity * math.exp(-math.log(20.0) * elapsed / recovery)


def _bounded_union(left: float, right: float) -> float:
    return 1.0 - (1.0 - float(np.clip(left, 0, 1))) * (
        1.0 - float(np.clip(right, 0, 1))
    )


def _reroute_share(day_since_start: int, base: float, ramp_days: float) -> float:
    if day_since_start < 0:
        return 0.0
    if ramp_days <= 0:
        return base
    ramp = 1.0 - math.exp(-day_since_start / ramp_days)
    return float(np.clip(base * ramp, 0.0, 1.0))


def _adaptive_lag(
    previous: float, target: float, adjustment_days: float, recovery_half_life: float
) -> float:
    if target >= previous:
        alpha = 1.0 - math.exp(-1.0 / max(adjustment_days, 1.0))
    else:
        alpha = 1.0 - math.exp(-math.log(2.0) / max(recovery_half_life, 1.0))
    return previous + alpha * (target - previous)


def _ramped_response(
    day_since_start: int,
    start_day: float,
    maximum_share: float,
    ramp_days: float,
    duration_days: float = 0.0,
    decay_half_life_days: float = 1.0,
) -> float:
    """Return a bounded response flow with optional duration and decay."""
    if maximum_share <= 0 or day_since_start < start_day:
        return 0.0
    elapsed = day_since_start - start_day
    ramp = 1.0 - math.exp(-elapsed / max(ramp_days, 1.0))
    active = maximum_share * ramp
    if duration_days <= 0 or elapsed < duration_days:
        return float(np.clip(active, 0.0, maximum_share))
    peak = maximum_share * (
        1.0 - math.exp(-duration_days / max(ramp_days, 1.0))
    )
    decay_elapsed = elapsed - duration_days
    decay = math.exp(
        -math.log(2.0) * decay_elapsed / max(decay_half_life_days, 1.0)
    )
    return float(np.clip(peak * decay, 0.0, maximum_share))


def _capped_contributions(
    physical: float,
    base_risk: float,
    opacity: float,
    cap: float,
) -> tuple[float, float, float, float]:
    """Scale additive price components proportionally when the cap binds."""
    raw_total = max(physical, 0.0) + max(base_risk, 0.0) + max(opacity, 0.0)
    if raw_total <= 0:
        return 0.0, 0.0, 0.0, 0.0
    scale = min(1.0, max(cap, 0.0) / raw_total)
    physical_component = max(physical, 0.0) * scale
    base_component = max(base_risk, 0.0) * scale
    opacity_component = max(opacity, 0.0) * scale
    return (
        physical_component,
        base_component,
        opacity_component,
        physical_component + base_component + opacity_component,
    )


def _severity_panels(
    inputs: ModelInputs,
    events: pd.DataFrame,
    scenario_name: str,
    days: int,
    use_sensor_fusion: bool,
) -> tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame
]:
    chokepoints = list(inputs.chokepoints["chokepoint"])
    direct = pd.DataFrame(0.0, index=range(days), columns=chokepoints)
    for _, event in events.iterrows():
        cp_name = str(event["chokepoint"])
        for day in range(days):
            direct.loc[day, cp_name] = _bounded_union(
                direct.loc[day, cp_name], disruption_envelope(day, event)
            )

    sensor_panel = build_sensor_panel(inputs, scenario_name, days)
    opacity = pd.DataFrame(0.0, index=range(days), columns=chokepoints)
    sensor_diagnostics = pd.DataFrame()
    observed = direct.copy()
    if use_sensor_fusion and not sensor_panel.empty:
        for _, signal in sensor_panel.iterrows():
            day = int(signal["day"])
            cp_name = str(signal["chokepoint"])
            confidence = float(signal["fusion_confidence"])
            sensor_severity = float(signal["fusion_severity"])
            observed.loc[day, cp_name] = (
                (1.0 - confidence) * direct.loc[day, cp_name]
                + confidence * sensor_severity
            )
            opacity.loc[day, cp_name] = float(signal["opacity_risk_premium_pct"])
        sensor_diagnostics = sensor_panel.set_index(["day", "chokepoint"])

    total = observed.copy()
    for day in range(days):
        for _, dependency in inputs.dependencies.iterrows():
            lag = int(dependency["lag_days"])
            source_day = day - lag
            if source_day < 0:
                continue
            source = str(dependency["source_chokepoint"])
            target = str(dependency["target_chokepoint"])
            transmitted = (
                float(total.loc[source_day, source])
                * float(dependency["transmission_weight"])
            )
            total.loc[day, target] = _bounded_union(
                total.loc[day, target], transmitted
            )
    dependency_induced = (total - observed).clip(lower=0, upper=1)
    return direct, total, dependency_induced, opacity, sensor_diagnostics


def run_scenario(
    inputs: ModelInputs, scenario_name: str, days: int
) -> pd.DataFrame:
    events = inputs.scenarios.loc[
        inputs.scenarios["scenario"] == scenario_name
    ].copy()
    if events.empty:
        raise ValueError(f"Scenario not found: {scenario_name}")
    catalog_rows = inputs.scenario_catalog.loc[
        inputs.scenario_catalog["scenario"] == scenario_name
    ]
    if catalog_rows.empty:
        raise ValueError(f"Scenario catalog entry not found: {scenario_name}")
    catalog = catalog_rows.iloc[0]

    direct_severity, total_severity, dependency_severity, opacity, sensors = (
        _severity_panels(
            inputs,
            events,
            scenario_name,
            days,
            bool(catalog["use_sensor_fusion"]),
        )
    )
    chokepoints = inputs.chokepoints.set_index("chokepoint")
    exposures = inputs.exposures.set_index(["commodity", "chokepoint"])
    balancing = inputs.market_balancing.loc[
        inputs.market_balancing["scenario"] == scenario_name
    ].set_index("commodity")
    crude_structure = inputs.crude_market_structure.loc[
        inputs.crude_market_structure["scenario"] == scenario_name
    ].iloc[0]
    rows: list[dict[str, float | int | str]] = []

    for _, commodity in inputs.commodities.iterrows():
        name = str(commodity["commodity"])
        balance = balancing.loc[name]
        commercial_inventory = float(commodity["commercial_inventory_days"])
        strategic_inventory = float(commodity["strategic_reserve_days"])
        initial_commercial = commercial_inventory
        lag_state = 0.0
        demand_state = float(catalog["initial_demand_reduction_share"])
        delayed_targets = [0.0] * max(int(commodity["lag_onset_days"]), 0)
        seasonal_targets = [0.0] * max(int(commodity["seasonal_lag_days"]), 0)

        for day in range(days):
            group_losses: dict[str, float] = {}
            group_logistics: dict[str, float] = {}
            group_insurance: dict[str, float] = {}
            group_active_route: dict[str, float] = {}
            max_disruption = 0.0
            max_direct = 0.0
            max_dependency = 0.0
            max_opacity = 0.0

            for cp_name in total_severity.columns:
                key = (name, cp_name)
                if key not in exposures.index:
                    continue
                envelope = float(total_severity.loc[day, cp_name])
                if envelope <= 0:
                    continue
                exposure = exposures.loc[key]
                cp = chokepoints.loc[cp_name]
                route_group = str(exposure["route_group"])
                route_share = float(exposure["route_share_global"])
                raw_route_loss = route_share * envelope
                base_reroute = float(cp["base_reroute_share"]) * float(
                    exposure["reroute_modifier"]
                )
                day_since_first_event = max(
                    day - int(events["start_day"].min()), 0
                )
                reroute = _reroute_share(
                    day_since_first_event,
                    float(np.clip(base_reroute, 0.0, 1.0)),
                    float(cp["reroute_ramp_days"]),
                )
                substitution = min(
                    float(commodity["max_substitution_share"]),
                    float(commodity["substitution_rate_per_day"])
                    * day_since_first_event,
                )
                loss = raw_route_loss * (1.0 - reroute) * (1.0 - substitution)
                group_losses[route_group] = max(
                    group_losses.get(route_group, 0.0),
                    float(np.clip(loss, 0.0, 1.0)),
                )
                group_logistics[route_group] = max(
                    group_logistics.get(route_group, 0.0),
                    raw_route_loss
                    * reroute
                    * float(cp["reroute_cost_uplift_pct"]),
                )
                group_insurance[route_group] = max(
                    group_insurance.get(route_group, 0.0),
                    raw_route_loss * float(cp["insurance_uplift_pct"]),
                )
                group_active_route[route_group] = max(
                    group_active_route.get(route_group, 0.0), raw_route_loss
                )
                max_disruption = max(max_disruption, envelope)
                max_direct = max(max_direct, float(direct_severity.loc[day, cp_name]))
                max_dependency = max(
                    max_dependency, float(dependency_severity.loc[day, cp_name])
                )
                max_opacity = max(max_opacity, float(opacity.loc[day, cp_name]))

            supply_loss = 0.0
            for group_loss in group_losses.values():
                supply_loss = _bounded_union(supply_loss, group_loss)

            day_since_first_event = max(
                day - int(events["start_day"].min()), 0
            )
            bypass_available = _ramped_response(
                day_since_first_event,
                0.0,
                float(balance["bypass_capacity_share"]),
                float(balance["bypass_ramp_days"]),
            )
            bypass_offset = min(supply_loss, bypass_available)
            remaining_after_bypass = max(supply_loss - bypass_offset, 0.0)

            release_available = _ramped_response(
                day_since_first_event,
                float(balance["strategic_release_start_day"]),
                float(balance["strategic_release_share"]),
                float(balance["strategic_release_ramp_days"]),
                float(balance["strategic_release_duration_days"]),
                float(balance["strategic_release_decay_half_life_days"]),
            )
            strategic_release_offset = min(
                remaining_after_bypass,
                release_available,
                strategic_inventory,
            )
            strategic_inventory -= strategic_release_offset
            remaining_after_release = max(
                remaining_after_bypass - strategic_release_offset, 0.0
            )

            external_available = _ramped_response(
                day_since_first_event,
                float(balance["external_supply_response_start_day"]),
                float(balance["external_supply_response_share"]),
                float(balance["external_supply_response_ramp_days"]),
                0.0,
                float(balance["external_supply_response_decay_half_life_days"]),
            )
            external_supply_offset = min(
                remaining_after_release, external_available
            )
            structural_supply_offset = (
                bypass_offset
                + strategic_release_offset
                + external_supply_offset
            )
            balanced_supply_loss = max(
                supply_loss - structural_supply_offset, 0.0
            )

            demand_applied = demand_state
            net_market_gap = max(balanced_supply_loss - demand_applied, 0.0)
            elasticity = max(
                float(commodity["short_run_adjustment_elasticity"]), 0.01
            )
            base_risk_premium = (
                float(catalog["base_market_risk_premium_pct"]) * max_disruption
            )
            total_risk_premium = base_risk_premium + max_opacity
            market_tightness = float(commodity["market_tightness"])
            price_cap = float(commodity["price_shock_cap_pct"])
            static_demand_price_shock = min(
                price_cap,
                balanced_supply_loss
                / elasticity
                * market_tightness
                + total_risk_premium,
            )
            physical_price_component_raw = (
                net_market_gap / elasticity * market_tightness
            )
            (
                physical_gap_price_contribution,
                base_risk_price_contribution,
                opacity_price_contribution,
                price_shock,
            ) = _capped_contributions(
                physical_price_component_raw,
                base_risk_premium,
                max_opacity,
                price_cap,
            )
            no_structural_gap = max(supply_loss - demand_applied, 0.0)
            no_structural_offsets_price_shock = min(
                price_cap,
                no_structural_gap / elasticity * market_tightness
                + total_risk_premium,
            )
            no_balancing_price_shock = min(
                price_cap,
                supply_loss / elasticity * market_tightness
                + total_risk_premium,
            )
            implied_price = float(commodity["baseline_price_usd"]) * (
                1.0 + price_shock
            )
            static_demand_implied_price = float(commodity["baseline_price_usd"]) * (
                1.0 + static_demand_price_shock
            )
            no_structural_offsets_implied_price = float(
                commodity["baseline_price_usd"]
            ) * (1.0 + no_structural_offsets_price_shock)
            no_balancing_implied_price = float(
                commodity["baseline_price_usd"]
            ) * (1.0 + no_balancing_price_shock)

            grade_mismatch_gap = 0.0
            regional_sour_spread = 0.0
            regional_sour_price = np.nan
            segmented_channel_shift = 0.0
            experienced_price_shock = price_shock
            base_reassigned_heavy_sour_share = 0.0
            heavy_sour_enabling_availability = 1.0
            effective_reassigned_heavy_sour_share = 0.0
            if name == "Crude oil":
                segmented_channel_shift = (
                    float(crude_structure["segmented_channel_share"])
                    * max_disruption
                )
                experienced_price_shock = price_shock * (
                    1.0
                    - float(crude_structure["segmented_channel_share"])
                    * float(
                        crude_structure["panic_premium_insulation_share"]
                    )
                )
                base_reassigned_heavy_sour_share = float(
                    crude_structure["reassigned_heavy_sour_share"]
                )
                heavy_sour_enabling_availability = (
                    float(crude_structure["upstream_availability_share"])
                    * float(crude_structure["grid_availability_share"])
                    * float(crude_structure["terminal_availability_share"])
                )
                effective_reassigned_heavy_sour_share = (
                    base_reassigned_heavy_sour_share
                    * heavy_sour_enabling_availability
                )
                grade_mismatch_gap = max(
                    balanced_supply_loss
                    / max(
                        float(crude_structure["sour_dependent_market_share"]),
                        0.01,
                    )
                    * (
                        1.0
                        - float(
                            crude_structure[
                                "alternative_grade_compatibility_share"
                            ]
                        )
                    )
                    - effective_reassigned_heavy_sour_share,
                    0.0,
                )
                regional_sour_spread = min(
                    float(crude_structure["sour_spread_cap_usd"]),
                    grade_mismatch_gap
                    * float(crude_structure["sour_spread_sensitivity_usd"])
                    + max_disruption
                    * float(
                        crude_structure["logistics_friction_premium_usd"]
                    ),
                )
                regional_sour_price = implied_price + regional_sour_spread
            target_demand_reduction = min(
                float(commodity["max_demand_reduction_share"]),
                experienced_price_shock
                * float(commodity["demand_price_elasticity"])
                + float(catalog["policy_demand_reduction_share"])
                * max_disruption,
            )
            demand_state = _adaptive_lag(
                demand_state,
                target_demand_reduction,
                float(commodity["demand_adjustment_days"]),
                float(commodity["demand_recovery_half_life_days"]),
            )

            daily_market_value = float(commodity["annual_market_value_usd"]) / 365.0
            repricing = (
                daily_market_value
                * price_shock
                * float(commodity["exposed_spend_share"])
            )
            logistics = daily_market_value * (
                sum(group_logistics.values()) + sum(group_insurance.values())
            )
            immediate = repricing + logistics

            physical_deficit = net_market_gap
            commercial_draw = min(commercial_inventory, physical_deficit)
            commercial_inventory -= commercial_draw
            physical_shortage = max(physical_deficit - commercial_draw, 0.0)
            if physical_deficit < 1e-8 and commercial_inventory < initial_commercial:
                rebuild_days = max(float(commodity["inventory_rebuild_days"]), 1.0)
                commercial_inventory = min(
                    initial_commercial,
                    commercial_inventory + initial_commercial / rebuild_days,
                )

            regular_lag_target = (
                price_shock * float(commodity["downstream_input_cost_share"])
                + physical_shortage * float(commodity["availability_multiplier"])
            )
            delayed_targets.append(regular_lag_target)
            delayed_regular = delayed_targets.pop(0)
            seasonal_targets.append(balanced_supply_loss)
            seasonal_supply_loss = seasonal_targets.pop(0)
            seasonal_component = seasonal_supply_loss * float(
                commodity["seasonal_transmission_multiplier"]
            )
            lag_target = delayed_regular + seasonal_component
            lag_state = _adaptive_lag(
                lag_state,
                lag_target,
                float(commodity["lag_adjustment_days"]),
                float(commodity["recovery_half_life_days"]),
            )
            lagged = (
                float(commodity["annual_downstream_value_at_risk_usd"])
                / 365.0
                * lag_state
            )
            total_impact = immediate + lagged

            signal_key_candidates = [
                (day, cp_name)
                for cp_name in total_severity.columns
                if (day, cp_name) in sensors.index
            ]
            if signal_key_candidates:
                signal_rows = sensors.loc[signal_key_candidates]
                ais_index = float(signal_rows["ais_declared_transit_index"].min())
                sar_index = float(signal_rows["sar_detected_transit_index"].min())
                dark_activity = float(signal_rows["dark_activity_index"].max())
                weighted_dark_activity = float(
                    signal_rows["weighted_undeclared_activity_index"].max()
                )
                sensor_confidence = float(signal_rows["fusion_confidence"].max())
                track_continuity = float(
                    signal_rows["track_continuity_confidence"].max()
                )
            else:
                ais_index = np.nan
                sar_index = np.nan
                dark_activity = 0.0
                weighted_dark_activity = 0.0
                sensor_confidence = 0.0
                track_continuity = 0.0

            rows.append(
                {
                    "scenario": scenario_name,
                    "scenario_probability": float(catalog["scenario_probability"]),
                    "day": day,
                    "commodity": name,
                    "direct_disruption_severity": max_direct,
                    "dependency_induced_severity": max_dependency,
                    "supply_loss_pct": supply_loss,
                    "bypass_supply_offset_pct": bypass_offset,
                    "strategic_release_offset_pct": strategic_release_offset,
                    "external_supply_response_pct": external_supply_offset,
                    "structural_supply_offset_pct": structural_supply_offset,
                    "balanced_supply_loss_pct": balanced_supply_loss,
                    "demand_reduction_pct": demand_applied,
                    "segmented_channel_shift_pct": segmented_channel_shift,
                    "apparent_benchmark_demand_reduction_pct": min(
                        demand_applied + segmented_channel_shift, 1.0
                    ),
                    "experienced_price_shock_pct": experienced_price_shock,
                    "target_demand_reduction_pct": target_demand_reduction,
                    "net_market_gap_pct": net_market_gap,
                    "price_shock_pct": price_shock,
                    "physical_gap_price_contribution_pct": (
                        physical_gap_price_contribution
                    ),
                    "base_risk_price_contribution_pct": (
                        base_risk_price_contribution
                    ),
                    "opacity_price_contribution_pct": opacity_price_contribution,
                    "implied_price_usd": implied_price,
                    "grade_mismatch_gap_pct": grade_mismatch_gap,
                    "regional_sour_spread_usd": regional_sour_spread,
                    "regional_sour_price_usd": regional_sour_price,
                    "base_reassigned_heavy_sour_share_pct": (
                        base_reassigned_heavy_sour_share
                    ),
                    "heavy_sour_enabling_availability_pct": (
                        heavy_sour_enabling_availability
                    ),
                    "effective_reassigned_heavy_sour_share_pct": (
                        effective_reassigned_heavy_sour_share
                    ),
                    "static_demand_price_shock_pct": static_demand_price_shock,
                    "static_demand_implied_price_usd": static_demand_implied_price,
                    "demand_moderation_price_usd": (
                        static_demand_implied_price - implied_price
                    ),
                    "no_structural_offsets_price_shock_pct": (
                        no_structural_offsets_price_shock
                    ),
                    "no_structural_offsets_implied_price_usd": (
                        no_structural_offsets_implied_price
                    ),
                    "structural_moderation_price_usd": (
                        no_structural_offsets_implied_price - implied_price
                    ),
                    "no_balancing_price_shock_pct": no_balancing_price_shock,
                    "no_balancing_implied_price_usd": no_balancing_implied_price,
                    "total_balancing_moderation_price_usd": (
                        no_balancing_implied_price - implied_price
                    ),
                    "market_risk_premium_pct": total_risk_premium,
                    "active_route_weight_pct": sum(group_active_route.values()),
                    "commercial_inventory_remaining_days": commercial_inventory,
                    "strategic_reserve_remaining_days": strategic_inventory,
                    "inventory_remaining_days": (
                        commercial_inventory + strategic_inventory
                    ),
                    "physical_shortage_pct": physical_shortage,
                    "seasonal_lag_component_pct": seasonal_component,
                    "ais_declared_transit_index": ais_index,
                    "sar_detected_transit_index": sar_index,
                    "dark_activity_index": dark_activity,
                    "weighted_undeclared_activity_index": weighted_dark_activity,
                    "sensor_confidence": sensor_confidence,
                    "track_continuity_confidence": track_continuity,
                    "immediate_repricing_usd": repricing,
                    "immediate_logistics_usd": logistics,
                    "immediate_impact_usd": immediate,
                    "lag_state_pct": lag_state,
                    "lagged_impact_usd": lagged,
                    "total_impact_usd": total_impact,
                    "probability_weighted_impact_usd": (
                        total_impact * float(catalog["scenario_probability"])
                    ),
                }
            )

    return pd.DataFrame(rows)


def run_ecological_externalities(
    inputs: ModelInputs, scenario_name: str, days: int
) -> pd.DataFrame:
    """Run conditional, non-commodity ecological economic-impact paths.

    These rows are kept outside commodity exposure totals because ecological
    incident severity is a separate scenario assumption, not a necessary
    consequence of reduced vessel passage.
    """
    selected = inputs.ecological_externalities.loc[
        inputs.ecological_externalities["scenario"] == scenario_name
    ].copy()
    if selected.empty:
        return pd.DataFrame(
            columns=[
                "scenario",
                "scenario_probability",
                "day",
                "channel",
                "hazard_severity",
                "impact_state_pct",
                "confidence",
                "lagged_impact_usd",
                "probability_weighted_impact_usd",
            ]
        )
    probability = float(
        inputs.scenario_catalog.loc[
            inputs.scenario_catalog["scenario"] == scenario_name,
            "scenario_probability",
        ].iloc[0]
    )
    rows: list[dict[str, float | int | str]] = []
    for _, channel in selected.iterrows():
        lag_queue = [0.0] * int(channel["lag_onset_days"])
        impact_state = 0.0
        for day in range(days):
            start = int(channel["start_day"])
            duration = int(channel["duration_days"])
            if day < start:
                hazard = 0.0
            elif day < start + duration:
                hazard = float(channel["severity"])
            else:
                elapsed = day - (start + duration)
                hazard = float(channel["severity"]) * math.exp(
                    -math.log(2.0)
                    * elapsed
                    / max(float(channel["recovery_half_life_days"]), 1.0)
                )
            lag_queue.append(hazard)
            delayed_hazard = lag_queue.pop(0)
            impact_state = _adaptive_lag(
                impact_state,
                delayed_hazard,
                float(channel["adjustment_days"]),
                float(channel["recovery_half_life_days"]),
            )
            lagged_impact = (
                float(channel["annual_value_at_risk_usd"])
                / 365.0
                * impact_state
                * float(channel["confidence"])
            )
            rows.append(
                {
                    "scenario": scenario_name,
                    "scenario_probability": probability,
                    "day": day,
                    "channel": str(channel["channel"]),
                    "hazard_severity": hazard,
                    "impact_state_pct": impact_state,
                    "confidence": float(channel["confidence"]),
                    "lagged_impact_usd": lagged_impact,
                    "probability_weighted_impact_usd": (
                        lagged_impact * probability
                    ),
                }
            )
    return pd.DataFrame(rows)


def summarize_ecological_externalities(daily: pd.DataFrame) -> pd.DataFrame:
    if daily.empty:
        return pd.DataFrame(
            columns=[
                "channel",
                "scenario_probability",
                "lagged_impact_usd",
                "probability_weighted_impact_usd",
                "peak_hazard_severity",
                "peak_impact_state_pct",
                "confidence",
            ]
        )
    return (
        daily.groupby("channel", sort=False)
        .agg(
            scenario_probability=("scenario_probability", "first"),
            lagged_impact_usd=("lagged_impact_usd", "sum"),
            probability_weighted_impact_usd=(
                "probability_weighted_impact_usd",
                "sum",
            ),
            peak_hazard_severity=("hazard_severity", "max"),
            peak_impact_state_pct=("impact_state_pct", "max"),
            confidence=("confidence", "first"),
        )
        .reset_index()
    )


def summarize_scenario(daily: pd.DataFrame) -> pd.DataFrame:
    grouped = daily.groupby("commodity", sort=False)
    summary = grouped.agg(
        scenario_probability=("scenario_probability", "first"),
        immediate_impact_usd=("immediate_impact_usd", "sum"),
        lagged_impact_usd=("lagged_impact_usd", "sum"),
        total_impact_usd=("total_impact_usd", "sum"),
        probability_weighted_impact_usd=(
            "probability_weighted_impact_usd",
            "sum",
        ),
        peak_supply_loss_pct=("supply_loss_pct", "max"),
        peak_structural_supply_offset_pct=("structural_supply_offset_pct", "max"),
        peak_balanced_supply_loss_pct=("balanced_supply_loss_pct", "max"),
        cumulative_bypass_offset_days=("bypass_supply_offset_pct", "sum"),
        cumulative_strategic_release_days=("strategic_release_offset_pct", "sum"),
        cumulative_external_supply_response_days=(
            "external_supply_response_pct",
            "sum",
        ),
        peak_demand_reduction_pct=("demand_reduction_pct", "max"),
        peak_apparent_benchmark_demand_reduction_pct=(
            "apparent_benchmark_demand_reduction_pct",
            "max",
        ),
        peak_segmented_channel_shift_pct=("segmented_channel_shift_pct", "max"),
        peak_net_market_gap_pct=("net_market_gap_pct", "max"),
        peak_price_shock_pct=("price_shock_pct", "max"),
        peak_implied_price_usd=("implied_price_usd", "max"),
        peak_regional_sour_spread_usd=("regional_sour_spread_usd", "max"),
        peak_regional_sour_price_usd=("regional_sour_price_usd", "max"),
        minimum_heavy_sour_enabling_availability_pct=(
            "heavy_sour_enabling_availability_pct",
            "min",
        ),
        peak_effective_reassigned_heavy_sour_share_pct=(
            "effective_reassigned_heavy_sour_share_pct",
            "max",
        ),
        peak_static_demand_price_usd=(
            "static_demand_implied_price_usd",
            "max",
        ),
        peak_demand_moderation_usd=("demand_moderation_price_usd", "max"),
        peak_no_structural_offsets_price_usd=(
            "no_structural_offsets_implied_price_usd",
            "max",
        ),
        peak_structural_moderation_usd=("structural_moderation_price_usd", "max"),
        peak_no_balancing_price_usd=("no_balancing_implied_price_usd", "max"),
        peak_total_balancing_moderation_usd=(
            "total_balancing_moderation_price_usd",
            "max",
        ),
        peak_physical_gap_price_contribution_pct=(
            "physical_gap_price_contribution_pct",
            "max",
        ),
        peak_base_risk_price_contribution_pct=(
            "base_risk_price_contribution_pct",
            "max",
        ),
        peak_opacity_price_contribution_pct=(
            "opacity_price_contribution_pct",
            "max",
        ),
        peak_physical_shortage_pct=("physical_shortage_pct", "max"),
        peak_dependency_severity=("dependency_induced_severity", "max"),
        peak_dark_activity_index=("dark_activity_index", "max"),
        peak_weighted_undeclared_activity_index=(
            "weighted_undeclared_activity_index",
            "max",
        ),
        minimum_inventory_days=("inventory_remaining_days", "min"),
        minimum_strategic_reserve_days=(
            "strategic_reserve_remaining_days",
            "min",
        ),
    ).reset_index()
    total = {
        "commodity": "TOTAL",
        "scenario_probability": summary["scenario_probability"].iloc[0],
        "immediate_impact_usd": summary["immediate_impact_usd"].sum(),
        "lagged_impact_usd": summary["lagged_impact_usd"].sum(),
        "total_impact_usd": summary["total_impact_usd"].sum(),
        "probability_weighted_impact_usd": summary[
            "probability_weighted_impact_usd"
        ].sum(),
        "peak_supply_loss_pct": summary["peak_supply_loss_pct"].max(),
        "peak_structural_supply_offset_pct": summary[
            "peak_structural_supply_offset_pct"
        ].max(),
        "peak_balanced_supply_loss_pct": summary[
            "peak_balanced_supply_loss_pct"
        ].max(),
        "cumulative_bypass_offset_days": summary[
            "cumulative_bypass_offset_days"
        ].sum(),
        "cumulative_strategic_release_days": summary[
            "cumulative_strategic_release_days"
        ].sum(),
        "cumulative_external_supply_response_days": summary[
            "cumulative_external_supply_response_days"
        ].sum(),
        "peak_demand_reduction_pct": summary["peak_demand_reduction_pct"].max(),
        "peak_apparent_benchmark_demand_reduction_pct": summary[
            "peak_apparent_benchmark_demand_reduction_pct"
        ].max(),
        "peak_segmented_channel_shift_pct": summary[
            "peak_segmented_channel_shift_pct"
        ].max(),
        "peak_net_market_gap_pct": summary["peak_net_market_gap_pct"].max(),
        # Commodity prices have different units and cannot be aggregated.
        "peak_price_shock_pct": np.nan,
        "peak_implied_price_usd": np.nan,
        "peak_regional_sour_spread_usd": np.nan,
        "peak_regional_sour_price_usd": np.nan,
        "peak_static_demand_price_usd": np.nan,
        "peak_demand_moderation_usd": np.nan,
        "peak_no_structural_offsets_price_usd": np.nan,
        "peak_structural_moderation_usd": np.nan,
        "peak_no_balancing_price_usd": np.nan,
        "peak_total_balancing_moderation_usd": np.nan,
        "peak_physical_gap_price_contribution_pct": np.nan,
        "peak_base_risk_price_contribution_pct": np.nan,
        "peak_opacity_price_contribution_pct": np.nan,
        "peak_physical_shortage_pct": summary[
            "peak_physical_shortage_pct"
        ].max(),
        "peak_dependency_severity": summary["peak_dependency_severity"].max(),
        "peak_dark_activity_index": summary["peak_dark_activity_index"].max(),
        "peak_weighted_undeclared_activity_index": summary[
            "peak_weighted_undeclared_activity_index"
        ].max(),
        "minimum_inventory_days": summary["minimum_inventory_days"].min(),
        "minimum_strategic_reserve_days": summary[
            "minimum_strategic_reserve_days"
        ].min(),
    }
    return pd.concat([summary, pd.DataFrame([total])], ignore_index=True)
