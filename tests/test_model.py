from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from maritime_chokepoint.analysis import (
    build_scenario_comparison,
    run_calibration_sensitivity,
    summarize_calibration,
)
from maritime_chokepoint.io import load_inputs
from maritime_chokepoint.model import (
    disruption_envelope,
    run_ecological_externalities,
    run_scenario,
    summarize_ecological_externalities,
    summarize_scenario,
)
from maritime_chokepoint.signals import build_sensor_panel
from maritime_chokepoint.simulation import (
    run_ecological_monte_carlo,
    run_monte_carlo,
)


ROOT = Path(__file__).resolve().parents[1]


class ChokepointModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inputs = load_inputs(ROOT / "data" / "input")

    def test_disruption_recovers(self) -> None:
        event = self.inputs.scenarios.iloc[0]
        self.assertEqual(disruption_envelope(-1, event), 0.0)
        self.assertGreater(disruption_envelope(0, event), 0.0)
        self.assertGreater(
            disruption_envelope(31, event), disruption_envelope(80, event)
        )

    def test_losses_and_price_shocks_are_bounded(self) -> None:
        daily = run_scenario(self.inputs, "multi_node_stress", 120)
        self.assertTrue(daily["supply_loss_pct"].between(0, 1).all())
        self.assertTrue(daily["demand_reduction_pct"].between(0, 1).all())
        self.assertTrue((daily["price_shock_pct"] >= 0).all())
        caps = self.inputs.commodities.set_index("commodity")["price_shock_cap_pct"]
        for commodity, group in daily.groupby("commodity"):
            self.assertLessEqual(
                group["price_shock_pct"].max(), caps[commodity] + 1e-12
            )

    def test_immediate_precedes_lagged(self) -> None:
        daily = run_scenario(self.inputs, "hormuz_30d_severe", 90)
        day_zero = daily[daily["day"] == 0]
        self.assertGreater(day_zero["immediate_impact_usd"].sum(), 0)
        self.assertEqual(day_zero["lagged_impact_usd"].sum(), 0)

    def test_dynamic_demand_reduces_residual_gap(self) -> None:
        daily = run_scenario(self.inputs, "hormuz_30d_severe", 90)
        crude = daily[daily["commodity"] == "Crude oil"].set_index("day")
        initial = float(
            self.inputs.scenario_catalog.loc[
                self.inputs.scenario_catalog["scenario"] == "hormuz_30d_severe",
                "initial_demand_reduction_share",
            ].iloc[0]
        )
        self.assertEqual(crude.loc[0, "demand_reduction_pct"], initial)
        self.assertGreater(crude.loc[20, "demand_reduction_pct"], initial)
        self.assertLess(
            crude.loc[20, "net_market_gap_pct"],
            crude.loc[20, "supply_loss_pct"],
        )
        self.assertLess(
            crude.loc[20, "implied_price_usd"],
            crude.loc[20, "static_demand_implied_price_usd"],
        )

    def test_segmented_channels_are_not_mislabeled_as_demand_destruction(self) -> None:
        daily = run_scenario(self.inputs, "sensor_fused_hormuz", 90)
        crude = daily[daily["commodity"] == "Crude oil"]
        active = crude[crude["segmented_channel_shift_pct"] > 0]
        self.assertFalse(active.empty)
        self.assertTrue(
            (
                active["apparent_benchmark_demand_reduction_pct"]
                > active["demand_reduction_pct"]
            ).all()
        )
        self.assertTrue(
            (
                active["experienced_price_shock_pct"]
                <= active["price_shock_pct"] + 1e-12
            ).all()
        )

    def test_sour_basis_is_separate_from_global_supply_balance(self) -> None:
        baseline = run_scenario(self.inputs, "compound_hormuz_red_sea", 90)
        structure = self.inputs.crude_market_structure.copy()
        mask = structure["scenario"] == "compound_hormuz_red_sea"
        structure.loc[mask, "reassigned_heavy_sour_share"] = 0.0
        no_reassignment = run_scenario(
            self.inputs.with_frames(crude_market_structure=structure),
            "compound_hormuz_red_sea",
            90,
        )
        baseline_crude = baseline[baseline["commodity"] == "Crude oil"]
        no_reassignment_crude = no_reassignment[
            no_reassignment["commodity"] == "Crude oil"
        ]
        self.assertTrue(
            baseline_crude["net_market_gap_pct"].reset_index(drop=True).equals(
                no_reassignment_crude["net_market_gap_pct"].reset_index(drop=True)
            )
        )
        self.assertLess(
            baseline_crude["regional_sour_spread_usd"].sum(),
            no_reassignment_crude["regional_sour_spread_usd"].sum(),
        )
        self.assertTrue(
            (
                baseline_crude["regional_sour_price_usd"]
                >= baseline_crude["implied_price_usd"]
            ).all()
        )

    def test_heavy_sour_offset_requires_upstream_grid_and_terminal(self) -> None:
        baseline = run_scenario(self.inputs, "sensor_fused_hormuz", 30)
        structure = self.inputs.crude_market_structure.copy()
        mask = structure["scenario"] == "sensor_fused_hormuz"
        structure.loc[mask, "upstream_availability_share"] = 0.90
        structure.loc[mask, "grid_availability_share"] = 0.50
        structure.loc[mask, "terminal_availability_share"] = 0.80
        constrained = run_scenario(
            self.inputs.with_frames(crude_market_structure=structure),
            "sensor_fused_hormuz",
            30,
        )
        baseline_crude = baseline[baseline["commodity"] == "Crude oil"]
        constrained_crude = constrained[constrained["commodity"] == "Crude oil"]
        expected_availability = 0.90 * 0.50 * 0.80
        self.assertTrue(
            constrained_crude["heavy_sour_enabling_availability_pct"]
            .sub(expected_availability)
            .abs()
            .lt(1e-12)
            .all()
        )
        self.assertTrue(
            constrained_crude["effective_reassigned_heavy_sour_share_pct"]
            .sub(0.025 * expected_availability)
            .abs()
            .lt(1e-12)
            .all()
        )
        self.assertTrue(
            baseline_crude["net_market_gap_pct"].reset_index(drop=True).equals(
                constrained_crude["net_market_gap_pct"].reset_index(drop=True)
            )
        )
        self.assertGreaterEqual(
            constrained_crude["regional_sour_spread_usd"].sum(),
            baseline_crude["regional_sour_spread_usd"].sum(),
        )

    def test_v05_crude_structure_defaults_to_neutral_availability(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_dir = Path(directory) / "input"
            shutil.copytree(ROOT / "data" / "input", input_dir)
            path = input_dir / "crude_market_structure.csv"
            structure = pd.read_csv(path).drop(
                columns=[
                    "upstream_availability_share",
                    "grid_availability_share",
                    "terminal_availability_share",
                ]
            )
            structure.to_csv(path, index=False)
            legacy_inputs = load_inputs(input_dir)
            for column in [
                "upstream_availability_share",
                "grid_availability_share",
                "terminal_availability_share",
            ]:
                self.assertTrue(
                    (legacy_inputs.crude_market_structure[column] == 1.0).all()
                )

    def test_structural_offsets_reduce_the_unbalanced_path(self) -> None:
        daily = run_scenario(self.inputs, "sensor_fused_hormuz", 120)
        crude = daily[daily["commodity"] == "Crude oil"]
        self.assertGreater(crude["structural_supply_offset_pct"].max(), 0.0)
        self.assertTrue(
            (
                crude["balanced_supply_loss_pct"]
                <= crude["supply_loss_pct"] + 1e-12
            ).all()
        )
        self.assertTrue(
            (
                crude["no_structural_offsets_implied_price_usd"]
                >= crude["implied_price_usd"] - 1e-12
            ).all()
        )
        self.assertGreater(crude["structural_moderation_price_usd"].max(), 0.0)

    def test_price_contributions_reconcile_to_price_shock(self) -> None:
        daily = run_scenario(self.inputs, "sensor_fused_hormuz", 120)
        components = (
            daily["physical_gap_price_contribution_pct"]
            + daily["base_risk_price_contribution_pct"]
            + daily["opacity_price_contribution_pct"]
        )
        self.assertTrue((components - daily["price_shock_pct"]).abs().lt(1e-12).all())

    def test_strategic_release_depletes_reserve_once(self) -> None:
        daily = run_scenario(self.inputs, "sensor_fused_hormuz", 120)
        crude = daily[daily["commodity"] == "Crude oil"].reset_index(drop=True)
        initial = float(
            self.inputs.commodities.loc[
                self.inputs.commodities["commodity"] == "Crude oil",
                "strategic_reserve_days",
            ].iloc[0]
        )
        released = float(crude["strategic_release_offset_pct"].sum())
        remaining = float(crude["strategic_reserve_remaining_days"].iloc[-1])
        self.assertAlmostEqual(initial - remaining, released, places=9)
        self.assertTrue(
            crude["strategic_reserve_remaining_days"].diff().fillna(0).le(1e-12).all()
        )

    def test_dependency_matrix_propagates_hormuz_stress(self) -> None:
        daily = run_scenario(self.inputs, "hormuz_30d_severe", 60)
        crude = daily[daily["commodity"] == "Crude oil"]
        self.assertEqual(
            crude.loc[crude["day"] < 5, "dependency_induced_severity"].max(),
            0.0,
        )
        self.assertGreater(crude["dependency_induced_severity"].max(), 0.0)

    def test_red_sea_serial_nodes_are_not_added(self) -> None:
        daily = run_scenario(self.inputs, "red_sea_60d_diversion", 2)
        crude_day_zero = daily.loc[
            (daily["commodity"] == "Crude oil") & (daily["day"] == 0)
        ].iloc[0]
        expected_group_max = max(0.085 * 0.70, 0.065 * 0.60)
        self.assertAlmostEqual(
            crude_day_zero["supply_loss_pct"], expected_group_max, places=9
        )

    def test_sensor_fusion_corrects_ais_selection_bias(self) -> None:
        panel = build_sensor_panel(self.inputs, "sensor_fused_hormuz", 90)
        day_14 = panel.loc[panel["day"] == 14].iloc[0]
        ais_only_disruption = 1.0 - day_14["ais_declared_transit_index"]
        self.assertLess(day_14["physical_disruption_signal"], ais_only_disruption)
        self.assertAlmostEqual(day_14["dark_activity_index"], 0.27, places=6)
        self.assertGreater(day_14["opacity_risk_premium_pct"], 0.0)

    def test_sensor_confidence_decays_without_abrupt_reversion(self) -> None:
        panel = build_sensor_panel(self.inputs, "sensor_fused_hormuz", 120)
        day_60 = panel.loc[panel["day"] == 60].iloc[0]
        day_61 = panel.loc[panel["day"] == 61].iloc[0]
        day_105 = panel.loc[panel["day"] == 105].iloc[0]
        self.assertLess(day_61["fusion_confidence"], day_60["fusion_confidence"])
        self.assertGreater(day_61["fusion_confidence"], 0.0)
        self.assertEqual(day_105["fusion_confidence"], 0.0)
        self.assertGreater(day_61["observed_transit_index"], day_60["observed_transit_index"])

    def test_sensor_weighting_uses_identity_staleness_and_backtest_status(self) -> None:
        sensors = self.inputs.sensors.copy()
        fresh = sensors.copy()
        fresh["median_ais_staleness_hours"] = 0.0
        fresh["validation_status"] = "backtested"
        stale = sensors.copy()
        stale["median_ais_staleness_hours"] = 96.0
        stale["validation_status"] = "unvalidated"
        fresh_panel = build_sensor_panel(
            self.inputs.with_frames(sensors=fresh), "sensor_fused_hormuz", 61
        )
        stale_panel = build_sensor_panel(
            self.inputs.with_frames(sensors=stale), "sensor_fused_hormuz", 61
        )
        self.assertGreater(
            fresh_panel["weighted_undeclared_activity_index"].max(),
            stale_panel["weighted_undeclared_activity_index"].max(),
        )
        self.assertTrue(
            (
                stale_panel["weighted_undeclared_activity_index"]
                <= stale_panel["dark_activity_index"] + 1e-12
            ).all()
        )

    def test_fertilizer_seasonal_effect_starts_after_delay(self) -> None:
        daily = run_scenario(self.inputs, "hormuz_30d_severe", 190)
        fertilizer = daily[daily["commodity"] == "Fertilizer"].set_index("day")
        self.assertEqual(
            fertilizer.loc[:149, "seasonal_lag_component_pct"].max(), 0.0
        )
        self.assertGreater(
            fertilizer.loc[150:, "seasonal_lag_component_pct"].max(), 0.0
        )

    def test_helium_has_no_strategic_reserve(self) -> None:
        daily = run_scenario(self.inputs, "hormuz_30d_severe", 90)
        helium = daily[daily["commodity"] == "Helium"]
        self.assertTrue((helium["strategic_reserve_remaining_days"] == 0).all())
        self.assertGreater(helium["commercial_inventory_remaining_days"].max(), 0)
        self.assertTrue((helium["strategic_release_offset_pct"] == 0).all())

    def test_inventory_can_exhaust_under_long_severe_shock(self) -> None:
        scenarios = self.inputs.scenarios.copy()
        mask = scenarios["scenario"] == "hormuz_30d_severe"
        scenarios.loc[mask, "duration_days"] = 365
        scenarios.loc[mask, "severity"] = 1.0
        stressed = self.inputs.with_frames(scenarios=scenarios)
        daily = run_scenario(stressed, "hormuz_30d_severe", 365)
        helium = daily[daily["commodity"] == "Helium"]
        self.assertEqual(helium["inventory_remaining_days"].min(), 0.0)
        self.assertGreater(helium["physical_shortage_pct"].max(), 0.0)

    def test_summary_total_matches_components(self) -> None:
        daily = run_scenario(self.inputs, "compound_hormuz_red_sea", 180)
        summary = summarize_scenario(daily)
        total = summary[summary["commodity"] == "TOTAL"].iloc[0]
        self.assertAlmostEqual(
            total["total_impact_usd"],
            total["immediate_impact_usd"] + total["lagged_impact_usd"],
            places=2,
        )
        self.assertTrue(pd.isna(total["peak_implied_price_usd"]))
        self.assertTrue(pd.isna(total["peak_price_shock_pct"]))
        self.assertAlmostEqual(
            total["probability_weighted_impact_usd"],
            total["total_impact_usd"] * total["scenario_probability"],
            places=2,
        )

    def test_ecological_branch_is_delayed_and_separate(self) -> None:
        scenario = "compound_hormuz_red_sea_ecological"
        ecological = run_ecological_externalities(self.inputs, scenario, 240)
        fisheries = ecological[
            ecological["channel"] == "Fisheries and coastal livelihoods"
        ]
        self.assertEqual(
            fisheries.loc[fisheries["day"] < 90, "lagged_impact_usd"].max(),
            0.0,
        )
        self.assertGreater(
            fisheries.loc[fisheries["day"] >= 90, "lagged_impact_usd"].max(),
            0.0,
        )
        ecological_summary = summarize_ecological_externalities(ecological)
        self.assertGreater(ecological_summary["lagged_impact_usd"].sum(), 0.0)
        core = summarize_scenario(run_scenario(self.inputs, scenario, 240))
        compound = summarize_scenario(
            run_scenario(self.inputs, "compound_hormuz_red_sea", 240)
        )
        self.assertAlmostEqual(
            float(
                core.loc[
                    core["commodity"] == "TOTAL", "total_impact_usd"
                ].iloc[0]
            ),
            float(
                compound.loc[
                    compound["commodity"] == "TOTAL", "total_impact_usd"
                ].iloc[0]
            ),
            places=2,
        )

    def test_ecological_monte_carlo_quantiles_are_ordered(self) -> None:
        mc = run_ecological_monte_carlo(
            self.inputs,
            "compound_hormuz_red_sea_ecological",
            120,
            simulations=8,
            seed=11,
        )
        self.assertFalse(mc.empty)
        self.assertTrue(
            (mc["p05_lagged_impact_usd"] <= mc["p50_lagged_impact_usd"]).all()
        )
        self.assertTrue(
            (mc["p50_lagged_impact_usd"] <= mc["p95_lagged_impact_usd"]).all()
        )
        self.assertIn("TOTAL", set(mc["channel"]))

    def test_monte_carlo_quantiles_ordered(self) -> None:
        mc = run_monte_carlo(
            self.inputs,
            "sensor_fused_hormuz",
            60,
            simulations=12,
            seed=7,
        )
        self.assertTrue(
            (mc["p05_total_impact_usd"] <= mc["p50_total_impact_usd"]).all()
        )
        self.assertTrue(
            (mc["p50_total_impact_usd"] <= mc["p95_total_impact_usd"]).all()
        )
        crude = mc.loc[mc["commodity"] == "Crude oil"].iloc[0]
        self.assertAlmostEqual(
            crude["target_band_below_share"]
            + crude["target_band_within_share"]
            + crude["target_band_above_share"],
            1.0,
        )
        total = mc.loc[mc["commodity"] == "TOTAL"].iloc[0]
        self.assertTrue(pd.isna(total["p50_peak_implied_price_usd"]))

    def test_scenario_comparison_reconciles_weighted_exposure(self) -> None:
        comparison = build_scenario_comparison(self.inputs, 30)
        self.assertEqual(len(comparison), len(self.inputs.scenario_catalog))
        self.assertTrue(
            (
                comparison["probability_weighted_impact_usd"]
                - comparison["gross_exposure_usd"]
                * comparison["scenario_probability"]
            ).abs().lt(0.01).all()
        )
        ecological = comparison.loc[
            comparison["scenario"] == "compound_hormuz_red_sea_ecological"
        ].iloc[0]
        self.assertGreater(ecological["separate_ecological_externality_usd"], 0.0)
        non_ecological = comparison.loc[
            comparison["scenario"] != "compound_hormuz_red_sea_ecological"
        ]
        self.assertTrue(
            (non_ecological["separate_ecological_externality_usd"] == 0.0).all()
        )

    def test_calibration_is_diagnostic_and_preserves_baseline(self) -> None:
        grid = run_calibration_sensitivity(
            self.inputs,
            "sensor_fused_hormuz",
            30,
            levels=(1.0,),
        )
        self.assertEqual(len(grid), 1)
        self.assertTrue(bool(grid.iloc[0]["is_baseline"]))
        baseline = summarize_scenario(
            run_scenario(self.inputs, "sensor_fused_hormuz", 30)
        )
        crude = baseline.loc[baseline["commodity"] == "Crude oil"].iloc[0]
        self.assertAlmostEqual(
            grid.iloc[0]["peak_brent_usd"], crude["peak_implied_price_usd"]
        )
        calibration = summarize_calibration(grid).iloc[0]
        self.assertEqual(
            calibration["governance_decision"],
            "investigate_no_automatic_recalibration",
        )

    def test_calibration_structural_factor_is_active(self) -> None:
        grid = run_calibration_sensitivity(
            self.inputs,
            "sensor_fused_hormuz",
            30,
            levels=(0.75, 1.25),
        )
        self.assertIn("structural_supply_offset_multiplier", grid.columns)
        grouped = grid.groupby("structural_supply_offset_multiplier")[
            "peak_structural_supply_offset_pct"
        ].mean()
        self.assertGreater(grouped.loc[1.25], grouped.loc[0.75])


if __name__ == "__main__":
    unittest.main()
