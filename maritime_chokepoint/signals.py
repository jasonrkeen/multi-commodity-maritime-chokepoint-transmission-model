from __future__ import annotations

import numpy as np
import pandas as pd

from .io import ModelInputs


SIGNAL_COLUMNS = [
    "ais_declared_transit_index",
    "sar_detected_transit_index",
    "ballast_repositioning_z",
    "thermal_anomaly_z",
    "radar_wake_persistence_z",
    "source_confidence",
    "identity_resolution_share",
    "median_ais_staleness_hours",
    "detection_recall_assumption",
]

VALIDATION_WEIGHTS = {
    "unvalidated": 0.60,
    "partial_backtest": 0.80,
    "backtested": 1.00,
}


def build_sensor_panel(
    inputs: ModelInputs, scenario_name: str, days: int
) -> pd.DataFrame:
    """Interpolate sparse sensor observations and derive fusion diagnostics.

    The bundled rows are synthetic demonstrations. SAR is weighted more heavily than
    AIS for physical passage, while the SAR-minus-AIS discrepancy is retained as an
    opacity signal rather than being misclassified as missing physical flow.
    """

    selected = inputs.sensors.loc[
        inputs.sensors["scenario"] == scenario_name
    ].copy()
    if selected.empty:
        return pd.DataFrame()

    panels: list[pd.DataFrame] = []
    for chokepoint, group in selected.groupby("chokepoint", sort=False):
        group = group.sort_values("day").set_index("day")
        first_day = max(int(group.index.min()), 0)
        last_observed_day = min(int(group.index.max()), days - 1)
        observed_index = pd.Index(
            range(first_day, last_observed_day + 1), name="day"
        )
        interpolated = group[SIGNAL_COLUMNS].reindex(observed_index).interpolate(
            method="linear", limit_direction="both"
        )
        status = group["validation_status"].reindex(observed_index).ffill().bfill()
        extension_end = min(last_observed_day + 45, days - 1)
        if extension_end > last_observed_day:
            last = interpolated.loc[last_observed_day]
            extension_rows = []
            for day in range(last_observed_day + 1, extension_end + 1):
                progress = (day - last_observed_day) / (
                    extension_end - last_observed_day
                )
                extension_rows.append(
                    {
                        "day": day,
                        "ais_declared_transit_index": (
                            last["ais_declared_transit_index"]
                            + progress
                            * (1.0 - last["ais_declared_transit_index"])
                        ),
                        "sar_detected_transit_index": (
                            last["sar_detected_transit_index"]
                            + progress
                            * (1.0 - last["sar_detected_transit_index"])
                        ),
                        "ballast_repositioning_z": (
                            last["ballast_repositioning_z"] * (1.0 - progress)
                        ),
                        "thermal_anomaly_z": (
                            last["thermal_anomaly_z"] * (1.0 - progress)
                        ),
                        "radar_wake_persistence_z": (
                            last["radar_wake_persistence_z"] * (1.0 - progress)
                        ),
                        "source_confidence": (
                            last["source_confidence"] * (1.0 - progress)
                        ),
                        "identity_resolution_share": (
                            last["identity_resolution_share"] * (1.0 - progress)
                        ),
                        "median_ais_staleness_hours": (
                            last["median_ais_staleness_hours"] + 24.0 * progress
                        ),
                        "detection_recall_assumption": (
                            last["detection_recall_assumption"] * (1.0 - progress)
                        ),
                    }
                )
            extension = pd.DataFrame(extension_rows).set_index("day")
            interpolated = pd.concat([interpolated, extension])
            extension_status = pd.Series(
                "unvalidated", index=extension.index, name="validation_status"
            )
            status = pd.concat([status, extension_status])
        interpolated["scenario"] = scenario_name
        interpolated["chokepoint"] = chokepoint
        interpolated["source_type"] = "synthetic_demo_interpolated_or_decayed"

        ais = interpolated["ais_declared_transit_index"].clip(0, 1)
        sar = interpolated["sar_detected_transit_index"].clip(0, 1)
        observed_transit = (0.35 * ais + 0.65 * sar).clip(0, 1)
        physical_disruption = (1.0 - observed_transit).clip(0, 1)
        dark_activity = (sar - ais).clip(lower=0, upper=1)
        ballast_pressure = (
            interpolated["ballast_repositioning_z"].clip(lower=0) / 3.0
        ).clip(0, 1)
        thermal_pressure = (
            interpolated["thermal_anomaly_z"].clip(lower=0) / 3.0
        ).clip(0, 1)
        wake_multiplier = (
            0.85 + 0.08 * interpolated["radar_wake_persistence_z"]
        ).clip(0.75, 1.10)
        validation_weight = status.map(VALIDATION_WEIGHTS).fillna(0.60)
        detection_confidence = (
            interpolated["source_confidence"]
            * wake_multiplier
            * validation_weight
            * interpolated["detection_recall_assumption"].clip(0, 1)
        ).clip(0, 1)
        track_continuity = (
            interpolated["identity_resolution_share"].clip(0, 1)
            * np.exp(
                -np.log(2.0)
                * interpolated["median_ais_staleness_hours"].clip(lower=0)
                / 48.0
            )
        ).clip(0, 1)
        weighted_undeclared_activity = (
            dark_activity
            * detection_confidence
            * (0.50 + 0.50 * track_continuity)
        ).clip(0, 1)
        forward_risk = (
            0.50 * physical_disruption
            + 0.30 * ballast_pressure
            + 0.20 * thermal_pressure
        ).clip(0, 1)

        interpolated["observed_transit_index"] = observed_transit
        interpolated["physical_disruption_signal"] = physical_disruption
        interpolated["dark_activity_index"] = dark_activity
        interpolated["forward_risk_signal"] = forward_risk
        interpolated["fusion_severity"] = (
            0.80 * physical_disruption + 0.20 * forward_risk
        ).clip(0, 1)
        interpolated["validation_status"] = status
        interpolated["validation_weight"] = validation_weight
        interpolated["track_continuity_confidence"] = track_continuity
        interpolated["weighted_undeclared_activity_index"] = (
            weighted_undeclared_activity
        )
        interpolated["fusion_confidence"] = detection_confidence
        interpolated["opacity_risk_premium_pct"] = (
            weighted_undeclared_activity * (0.12 + 0.04 * ballast_pressure)
        ).clip(0, 0.20)
        panels.append(interpolated.reset_index())

    return pd.concat(panels, ignore_index=True)
