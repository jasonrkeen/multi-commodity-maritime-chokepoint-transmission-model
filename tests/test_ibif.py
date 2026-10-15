from __future__ import annotations

import copy
import json
from pathlib import Path
import random
import tempfile
import unittest

import numpy as np
import pandas as pd

from maritime_chokepoint.ibif_adapter import build_ibif_assessment, ScoringConfig
from maritime_chokepoint.ibif_reporting import write_ibif_outputs
from maritime_chokepoint.io import load_inputs
from maritime_chokepoint.model import run_scenario


class IBIFTests(unittest.TestCase):
    def setUp(self):
        self.parameters = pd.DataFrame([dict(commodity="Example", annual_market_value_usd=36500.,
                                             commercial_inventory_days=8., strategic_reserve_days=2.)])
        self.daily = pd.DataFrame([dict(
            scenario="test", commodity="Example", day=day, scenario_probability=.25,
            active_route_weight_pct=.4, supply_loss_pct=.2, dependency_induced_severity=.1,
            balanced_supply_loss_pct=.1, net_market_gap_pct=.1, physical_shortage_pct=.2,
            inventory_remaining_days=5., direct_disruption_severity=.5, lag_state_pct=.3,
            total_impact_usd=20., sensor_confidence=.8, track_continuity_confidence=.6,
        ) for day in range(2)])

    def assess(self, **kwargs):
        return build_ibif_assessment(self.daily, self.parameters, sensor_fusion_active=True, sensor_evidence_available=True, **kwargs)

    def test_enabled_but_absent_sensor_observations_withhold_proxy(self):
        for available in (None, False):
            result = build_ibif_assessment(self.daily, self.parameters,
                sensor_fusion_active=True, sensor_evidence_available=available)
            self.assertIsNone(result["commodities"][0]["sensor_evidence_proxy"])
            self.assertFalse(result["sensor_evidence_available"])

    def test_weight_sum_tolerance_is_absolute(self):
        with self.assertRaises(ValueError):
            ScoringConfig(weights=(.2, .2, .2, .15, .2500000005))

    def test_inventory_sum_overflow_is_rejected(self):
        self.parameters[["commercial_inventory_days", "strategic_reserve_days"]] = 1e308
        with self.assertRaises(ValueError):
            self.assess()

    def test_hand_calculated_scores_and_probability_units(self):
        r = self.assess()["commodities"][0]
        # E=30, D=10, V=(10+20+50)/3, T=(50+10+30)/3, I=40/200*100.
        self.assertAlmostEqual(r["business_consequence_score"], 22.833333333333332)
        self.assertAlmostEqual(r["risk_pressure"], 5.708333333333333)
        self.assertAlmostEqual(r["sensor_evidence_proxy"], 60)
        self.assertEqual(r["gross_modeled_exposure_usd"], 40)
        self.assertIsNone(r["analytic_confidence"])
        self.assertEqual(r["escalation_status"], "UNASSESSED")

    def test_inputs_and_random_states_are_unchanged(self):
        before = self.daily.copy(deep=True)
        parameters = self.parameters.copy(deep=True)
        rng = np.random.get_state()
        py_rng = random.getstate()
        self.assess()
        pd.testing.assert_frame_equal(before, self.daily)
        pd.testing.assert_frame_equal(parameters, self.parameters)
        after = np.random.get_state()
        self.assertEqual(rng[0], after[0])
        np.testing.assert_array_equal(rng[1], after[1])
        self.assertEqual(rng[2:], after[2:])
        self.assertEqual(py_rng, random.getstate())

    def test_inactive_sensors_are_missing_not_zero_confidence(self):
        daily = self.daily.drop(columns=["sensor_confidence", "track_continuity_confidence"])
        result = build_ibif_assessment(daily, self.parameters, sensor_fusion_active=False)
        self.assertIsNone(result["commodities"][0]["sensor_evidence_proxy"])
        self.assertTrue(any("inactive" in s for s in result["commodities"][0]["collection_gaps"]))

    def test_rejects_missing_empty_nonfinite_and_wrong_types(self):
        for change in (lambda d: d.iloc[:0], lambda d: d.drop(columns="lag_state_pct"),
                       lambda d: d.assign(total_impact_usd=np.nan),
                       lambda d: d.assign(total_impact_usd=np.inf),
                       lambda d: d.assign(total_impact_usd=-1.),
                       lambda d: d.assign(total_impact_usd="20")):
            with self.subTest(change=change), self.assertRaises(ValueError):
                build_ibif_assessment(change(self.daily), self.parameters, sensor_fusion_active=True)

    def test_rejects_invalid_probabilities(self):
        for values in ([25., 25.], [-.1, -.1], [.2, .3]):
            self.daily["scenario_probability"] = values
            with self.assertRaises(ValueError): self.assess()

    def test_rejects_incomplete_or_duplicated_panel(self):
        for daily in (self.daily.assign(day=[0, 0]), self.daily.assign(day=[0, 2]),
                      self.daily.assign(day=[0, .5]), self.daily.assign(scenario=["a", "b"]),
                      self.daily.assign(commodity=["Example", "other"])):
            with self.subTest(daily=daily), self.assertRaises(ValueError):
                build_ibif_assessment(daily, self.parameters, sensor_fusion_active=True)

    def test_zero_initial_inventory_omits_depletion(self):
        self.parameters[["commercial_inventory_days", "strategic_reserve_days"]] = 0.
        r = self.assess()["commodities"][0]
        self.assertIsNone(r["inventory_depletion_fraction"])
        self.assertEqual(r["scores"]["vulnerability"], 15)

    def test_zero_exposure_and_probability_endpoints(self):
        for c in self.daily.select_dtypes("number").columns:
            if c != "day": self.daily[c] = 0.
        self.daily["inventory_remaining_days"] = 10.
        self.assertEqual(self.assess()["commodities"][0]["business_consequence_score"], 0)
        self.daily["total_impact_usd"] = 20.
        for p in (0., 1.):
            self.daily["scenario_probability"] = p
            r = self.assess()["commodities"][0]
            self.assertEqual(r["risk_pressure"], p * r["business_consequence_score"])

    def test_saturation_and_sensitivity_are_explicit(self):
        self.daily["total_impact_usd"] = 1000.
        r = self.assess()["commodities"][0]
        self.assertTrue(r["impact_score_saturated"])
        self.assertEqual(r["scores"]["impact"], 100)
        self.assertEqual(r["impact_normalization_ratio"], 10)
        self.assertTrue(all(0 <= x <= 100 for x in r["sensitivity_bcs"].values()))

    def test_configuration_and_sensor_bounds(self):
        for kwargs in ({"weights": (1.,)}, {"weights": (-1., 1., 1., 0., 0.)},
                       {"impact_market_multiple": 0}, {"impact_market_multiple": np.nan}):
            with self.assertRaises(ValueError): ScoringConfig(**kwargs)
        self.daily["sensor_confidence"] = 80.
        with self.assertRaises(ValueError): self.assess()

    def test_three_reports_are_deterministic_and_reconcile(self):
        assessment = self.assess(source_statuses=("synthetic_demo",))
        before = copy.deepcopy(assessment)
        with tempfile.TemporaryDirectory() as d:
            paths = write_ibif_outputs(Path(d), assessment)
            first = [p.read_bytes() for p in paths]
            write_ibif_outputs(Path(d), assessment)
            self.assertEqual(first, [p.read_bytes() for p in paths])
            self.assertEqual(len(list(Path(d).iterdir())), 3)
            self.assertEqual(json.loads(paths[0].read_text()), assessment)
            csv = pd.read_csv(paths[1])
            self.assertAlmostEqual(csv.iloc[0]["business_consequence_score"], assessment["commodities"][0]["business_consequence_score"])
            self.assertIn("Synthetic sensor", paths[2].read_text())
        self.assertEqual(assessment, before)

    def test_real_model_outputs_and_synthetic_label(self):
        inputs = load_inputs(Path(__file__).resolve().parents[1] / "data/input")
        daily = run_scenario(inputs, "sensor_fused_hormuz", 10)
        before = daily.copy(deep=True)
        result = build_ibif_assessment(daily, inputs.commodities, sensor_fusion_active=True,
                                       source_statuses=("synthetic_demo",))
        self.assertEqual(len(result["commodities"]), 4)
        self.assertEqual(result["calibration_status"], "EXPERIMENTAL_UNCALIBRATED")
        pd.testing.assert_frame_equal(daily, before)


if __name__ == "__main__":
    unittest.main()
