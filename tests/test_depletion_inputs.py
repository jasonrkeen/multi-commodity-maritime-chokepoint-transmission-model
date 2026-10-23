"""0.9 input tests; no execution of the 3,997-case trajectory study."""
from dataclasses import asdict, replace
import hashlib
import json
import math
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from diagnostics import depletion_inputs as module
from diagnostics.depletion_inputs import (load_design, thresholds, materialize,
                                         boundary_metrics, contrast_kind, write_inputs)
from diagnostics.sensitivity import Case, simulate


class DepletionInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config, cls.cases = load_design()
        cls.fixed = cls.cases[0]
        cls.scaled = next(c for c in cls.cases if c.block == 'T')
        cls.old_config = json.loads((module.ROOT/'docs/calibration_inventory/sensitivity_design_0_8.json').read_text(encoding='utf-8'))

    def trajectory(self, inputs):
        # Only engineering fixtures use the preserved 0.8 equation implementation.
        raw=asdict(inputs.design)
        fields={k:raw[k] for k in Case.__dataclass_fields__ if k in raw}
        fields.update(block='A',commercial_production_days=inputs.commercial_production_days,
                      strategic_production_days=inputs.strategic_production_days)
        return simulate(Case(**fields), self.old_config)

    def test_full_design_coverage_nulls_and_units(self):
        self.assertEqual(len(self.cases),3997)
        self.assertEqual(len({c.case_id for c in self.cases}),3997)
        self.assertEqual({b:sum(c.block==b for c in self.cases) for b in 'FTN'},dict(F=2916,T=1080,N=1))
        self.assertIsNone(self.scaled.commercial_production_days)
        self.assertIsNone(self.scaled.strategic_production_days)
        self.assertEqual(self.fixed.commercial_production_days,0)
        self.assertAlmostEqual(.005*self.config['reference_production_million_bpd'],.405785)
        with self.assertRaises(ValueError): boundary_metrics(self.scaled,30,self.config)

    def test_geometric_gross_threshold(self):
        value=thresholds(self.fixed,180,self.config)
        ratio=math.exp(-math.log(20)/30)
        expected=(3.6/81.157)*(90+(1-ratio**90)/(1-ratio))
        self.assertAlmostEqual(value.gross_production_days,expected,delta=1e-10)

    def test_every_design_row_materializes_without_missing_stocks(self):
        for case in self.cases:
            value=materialize(case,self.config)
            self.assertTrue(math.isfinite(value.commercial_production_days))
            self.assertTrue(math.isfinite(value.strategic_production_days))
            self.assertGreaterEqual(min(value.commercial_production_days,value.strategic_production_days),0)
            if case.block != 'T':
                self.assertEqual(value.commercial_production_days,case.commercial_production_days)
                self.assertEqual(value.strategic_production_days,case.strategic_production_days)

    def test_hand_calculated_release_and_delay_boundary(self):
        case=replace(self.fixed,release_fraction_per_day=.01,release_delay_days=1,release_ramp_days=1)
        self.assertEqual(thresholds(case,2,self.config).unconstrained_release_production_days,0)
        self.assertAlmostEqual(thresholds(case,3,self.config).unconstrained_release_production_days,.01*(1-math.exp(-1)),delta=1e-10)
        self.assertAlmostEqual(thresholds(case,3,self.config).gross_production_days,3*3.6/81.157,delta=1e-10)

    def test_materialization_is_deterministic_and_design_immutable(self):
        before=asdict(self.scaled)
        first=materialize(self.scaled,self.config)
        self.assertEqual(first,materialize(self.scaled,self.config))
        self.assertEqual(asdict(self.scaled),before)
        bound=thresholds(self.scaled,180,self.config)
        self.assertAlmostEqual(first.strategic_production_days,self.scaled.strategic_threshold_multiplier*bound.unconstrained_release_production_days)
        self.assertAlmostEqual(first.commercial_production_days,self.scaled.commercial_threshold_multiplier*bound.commercial_required(first.strategic_production_days))

    def test_shorter_horizons_retain_starting_stocks(self):
        case=materialize(replace(self.scaled,commercial_threshold_multiplier=1),self.config)
        start=(case.commercial_production_days,case.strategic_production_days)
        small=boundary_metrics(case,30,self.config)
        full=boundary_metrics(case,180,self.config)
        self.assertEqual((case.commercial_production_days,case.strategic_production_days),start)
        self.assertAlmostEqual(small['commercial_required_production_days'],thresholds(case.design,30,self.config).commercial_required(start[1]))
        self.assertTrue(full['commercial_within_tolerance'])
        self.assertGreater(small['commercial_margin_production_days'],0)
        with self.assertRaises(ValueError): materialize(self.scaled,dict(self.config,threshold_materialization_horizon=30))

    def test_threshold_identity_against_fixture_trajectories(self):
        for alpha in (.99,1,1.01):
            for beta in (.99,1,1.01):
                case=materialize(replace(self.scaled,strategic_threshold_multiplier=alpha,
                                         commercial_threshold_multiplier=beta),self.config)
                rows=self.trajectory(case)
                for horizon in (30,90,180):
                    bounds=thresholds(case.design,horizon,self.config)
                    release=math.fsum(r['strategic_release'] for r in rows[:horizon])
                    shortage=math.fsum(r['physical_shortage'] for r in rows[:horizon])
                    self.assertAlmostEqual(release,min(case.strategic_production_days,bounds.unconstrained_release_production_days),delta=1e-10)
                    required=bounds.commercial_required(case.strategic_production_days)
                    self.assertAlmostEqual(shortage,max(0,required-case.commercial_production_days),delta=1e-10)
                    self.assertLessEqual(math.fsum(r['commercial_draw'] for r in rows[:horizon]),case.commercial_production_days+1e-10)

    def test_equality_depletion_without_shortage_and_unused_stock(self):
        inputs=materialize(replace(self.scaled,commercial_threshold_multiplier=1,strategic_threshold_multiplier=1),self.config)
        rows=self.trajectory(inputs)
        self.assertLessEqual(abs(rows[-1]['commercial_stock']),1e-10)
        self.assertLessEqual(math.fsum(r['physical_shortage'] for r in rows),1e-10)
        self.assertTrue(boundary_metrics(inputs,180,self.config)['commercial_within_tolerance'])
        above=materialize(replace(self.scaled,strategic_threshold_multiplier=1.5),self.config)
        self.assertGreater(self.trajectory(above)[-1]['strategic_stock'],0)

    def test_positive_stock_exhaustion_precedes_later_shortage(self):
        inputs=materialize(replace(self.fixed,commercial_production_days=.1),self.config)
        rows=self.trajectory(inputs)
        exhaustion=next(r['day'] for r in rows if r['commercial_stock']==0)
        self.assertTrue(any(r['day']>exhaustion and r['physical_shortage']>0 for r in rows))

    def test_raw_and_tolerance_flags_do_not_snap(self):
        inputs=materialize(replace(self.scaled,commercial_threshold_multiplier=1),self.config)
        near=replace(inputs,commercial_production_days=inputs.commercial_production_days-1e-12)
        flags=boundary_metrics(near,180,self.config)
        self.assertTrue(flags['shortage_expected_raw'])
        self.assertFalse(flags['shortage_expected_tolerance'])
        self.assertLess(flags['commercial_margin_production_days'],0)

    def test_null_case_and_duplicate_numerical_inputs(self):
        null=materialize(self.cases[-1],self.config)
        self.assertEqual(thresholds(null.design,180,self.config).gross_production_days,0)
        self.assertEqual(boundary_metrics(null,180,self.config)['commercial_required_production_days'],0)
        duplicate=replace(self.scaled,case_id='duplicate')
        self.assertEqual(thresholds(duplicate,180,self.config),thresholds(self.scaled,180,self.config))
        self.assertEqual(materialize(duplicate,self.config).strategic_production_days,materialize(self.scaled,self.config).strategic_production_days)

    def test_invalid_fields_collapsed_thresholds_and_horizons(self):
        for change in ({'commercial_production_days':0},{'strategic_threshold_multiplier':float('nan')},
                       {'commercial_threshold_multiplier':-1},{'release_delay_days':1.5},
                       {'release_ramp_days':0},{'release_fraction_per_day':float('inf')}):
            with self.assertRaises(ValueError): materialize(replace(self.scaled,**change),self.config)
        for change in ({'release_fraction_per_day':0},{'allocation':0}):
            with self.assertRaises(ValueError): materialize(replace(self.scaled,**change),self.config)
        for horizon in (0,181,1.5,True):
            with self.assertRaises(ValueError): thresholds(self.fixed,horizon,self.config)
        with self.assertRaises(ValueError): thresholds(replace(self.fixed,reroute_fraction=.5),30,self.config)

    def test_contrast_labels(self):
        self.assertEqual(contrast_kind(self.fixed,replace(self.fixed,release_delay_days=7)),'single_physical_factor')
        self.assertEqual(contrast_kind(self.scaled,replace(self.scaled,commercial_threshold_multiplier=1)),'single_physical_factor')
        self.assertEqual(contrast_kind(self.scaled,replace(self.scaled,strategic_threshold_multiplier=1)),'normalized_multi_input_contrast')
        self.assertEqual(contrast_kind(self.scaled,replace(self.scaled,release_delay_days=7)),'normalized_multi_input_contrast')
        for other in (self.fixed,replace(self.scaled,release_delay_days=7,release_ramp_days=7),self.scaled):
            with self.assertRaises(ValueError): contrast_kind(self.scaled,other)

    def test_manifest_and_prior_file_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            manifest=json.loads((module.ROOT/module.MANIFEST).read_text(encoding='utf-8'))
            for relative in [str(module.MANIFEST),*manifest['files'],*manifest['preserved_prior_files']]:
                dest=root/relative;dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(module.ROOT/relative,dest)
            self.assertEqual(len(load_design(root)[1]),3997)
            prior=root/'docs/calibration_inventory/replay_eligibility_0_6.csv'
            prior.write_text('changed',encoding='utf-8')
            with self.assertRaises(ValueError): load_design(root)
            shutil.copyfile(module.ROOT/'docs/calibration_inventory/replay_eligibility_0_6.csv',prior)
            (root/module.MANIFEST).write_text('{}',encoding='utf-8')
            with self.assertRaises(ValueError): load_design(root)

    def test_writer_provenance_no_overwrite_and_failure_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'good'
            fixture_config=dict(self.config,case_count=1,block_counts={'T':1})
            with self.assertRaises(ValueError): write_inputs(output,self.config,(self.scaled,))
            self.assertFalse(output.exists())
            write_inputs(output,fixture_config,(self.scaled,))
            record=json.loads((output/'materialization_manifest.json').read_text(encoding='utf-8'))
            self.assertEqual(record['status'],'INPUTS_MATERIALIZED_STUDY_NOT_EXECUTED')
            self.assertFalse(record['study_executed'])
            self.assertEqual(record['inputs_sha256'],hashlib.sha256((output/'materialized_inputs.json').read_bytes()).hexdigest())
            with self.assertRaises(FileExistsError): write_inputs(output,fixture_config,(self.scaled,))
            failed=Path(tmp)/'failed'
            with patch.object(module,'materialize',side_effect=ValueError('fixture')):
                with self.assertRaises(ValueError): write_inputs(failed,fixture_config,(self.scaled,))
            self.assertEqual(json.loads((failed/'materialization_manifest.json').read_text(encoding='utf-8'))['status'],'INCOMPLETE')


if __name__=='__main__':
    unittest.main()
