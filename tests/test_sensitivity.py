"""Engineering fixtures only: these tests do not execute the 689-case study."""
import copy
from dataclasses import asdict, replace
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from diagnostics.sensitivity import (Case, ROOT, load_design, simulate, summarize,
                                     text_hash, verify_manifest, main)


class SensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config, cls.cases = load_design()

    def fixture(self, **changes):
        return replace(self.cases[0], allocation=1, severity=1, duration_days=2,
                       recovery_to_5pct_days=0, reroute_fraction=0,
                       **changes)

    def test_frozen_inventory_and_unique_cases(self):
        self.assertEqual(len(self.cases), 689)
        self.assertEqual(len({c.case_id for c in self.cases}), 689)
        self.assertEqual({b: sum(c.block == b for c in self.cases) for b in 'ABCN'},
                         dict(A=324, B=108, C=256, N=1))

    def test_hand_calculated_fixture_and_depletion(self):
        config = copy.deepcopy(self.config)
        config.update(days=3, reference_production_million_bpd=2)
        config['route_reference_million_bpd']['suez_sumed'] = 1
        case = self.fixture(commercial_production_days=.3)
        rows = simulate(case, config)
        # q=.5: day 0 draws .3 and leaves .2; day 1 leaves .5; day 2 ends shock.
        for row, gross, draw, shortage in zip(rows, [.5,.5,0], [.3,0,0], [.2,.5,0]):
            for name, expected in [('gross_gap',gross),('commercial_draw',draw),('physical_shortage',shortage)]:
                self.assertAlmostEqual(row[name], expected, delta=1e-10)
        summary = summarize(case, rows, 3, 2)
        self.assertAlmostEqual(summary['cumulative_shortage_million_barrels'], 1.4, delta=1e-10)
        self.assertEqual(summary['first_commercial_depletion_day'], 0)
        self.assertFalse(summary['commercial_initially_empty'])
        self.assertTrue(summary['strategic_initially_empty'])

    def test_release_timing_ramp_and_stock_limit(self):
        case = self.fixture(strategic_production_days=.001, release_fraction_per_day=.05,
                            release_delay_days=1, release_ramp_days=1)
        case = replace(case, duration_days=30)
        rows = simulate(case, dict(self.config, days=4))
        self.assertEqual([r['strategic_release'] for r in rows[:2]], [0, 0])
        self.assertAlmostEqual(rows[2]['strategic_release'], .001, delta=1e-10)
        self.assertEqual(rows[3]['strategic_release'], 0)
        self.assertEqual(summarize(case, rows, 4, 81.157)['first_strategic_depletion_day'], 2)
        uncapped = simulate(replace(case, strategic_production_days=10, release_fraction_per_day=.01), dict(self.config, days=4))
        self.assertAlmostEqual(uncapped[2]['strategic_release'], .01*(1-math.exp(-1)), delta=1e-10)

    def test_recovery_and_reroute_boundaries(self):
        case = replace(self.fixture(), recovery_to_5pct_days=14, reroute_fraction=.75)
        rows = simulate(case, dict(self.config, days=17))
        self.assertEqual(rows[1]['severity'], 1)
        self.assertEqual(rows[2]['severity'], 1)
        self.assertAlmostEqual(rows[16]['severity'], .05, delta=1e-10)
        self.assertEqual(rows[0]['reroute_fraction'], 0)
        self.assertAlmostEqual(rows[10]['reroute_fraction'], .75*(1-math.exp(-1)), delta=1e-10)
        abrupt = simulate(self.fixture(), dict(self.config, days=3))
        self.assertEqual(abrupt[2]['severity'], 0)

    def test_conservation_and_stock_budgets(self):
        case = replace(self.fixture(commercial_production_days=.1, strategic_production_days=.05,
                                    release_fraction_per_day=.01), duration_days=90)
        rows = simulate(case, self.config)
        for row in rows:
            self.assertGreaterEqual(min(row['commercial_stock'], row['strategic_stock'], row['physical_shortage']), 0)
            self.assertAlmostEqual(row['gross_gap'], row['strategic_release']+row['commercial_draw']+row['physical_shortage'], delta=1e-10)
        self.assertLessEqual(math.fsum(r['commercial_draw'] for r in rows), .1+1e-10)
        self.assertLessEqual(math.fsum(r['strategic_release'] for r in rows), .05+1e-10)

    def test_zero_exposure_and_zero_reserve(self):
        rows = simulate(replace(self.fixture(), allocation=0), self.config)
        self.assertTrue(all(r['gross_gap']==0 and r['price_proxy']==82 for r in rows))
        rows = simulate(self.fixture(release_fraction_per_day=.05), self.config)
        self.assertTrue(all(r['strategic_release']==0 for r in rows))

    def test_commercial_stock_does_not_change_price(self):
        empty = simulate(self.fixture(), self.config)
        stocked = simulate(self.fixture(commercial_production_days=35), self.config)
        self.assertEqual([r['price_proxy'] for r in empty], [r['price_proxy'] for r in stocked])
        self.assertGreater(empty[0]['physical_shortage'], stocked[0]['physical_shortage'])
        summary = summarize(self.fixture(commercial_production_days=35), stocked, 30, 81.157)
        self.assertIsNone(summary['first_commercial_depletion_day'])

    def test_duplicate_parameters_and_determinism(self):
        seen = {}
        pair = None
        for case in self.cases:
            key = tuple(v for k,v in asdict(case).items() if k not in ('case_id','block'))
            if key in seen:
                pair = seen[key], case
                break
            seen[key] = case
        self.assertIsNotNone(pair)
        a,b = pair
        self.assertEqual(simulate(a,self.config), simulate(b,self.config))
        self.assertEqual(simulate(a,self.config), simulate(a,self.config))

    def test_invalid_parameters_rejected(self):
        for field in ('allocation','severity','reroute_fraction','release_fraction_per_day',
                      'commercial_production_days','strategic_production_days'):
            for value in (-1, float('nan'), float('inf'), True):
                with self.subTest(field=field,value=value), self.assertRaises(ValueError):
                    simulate(replace(self.fixture(), **{field:value}), self.config)
        for field in ('duration_days','recovery_to_5pct_days','release_delay_days','release_ramp_days'):
            for value in (-1, 1.5, True):
                with self.subTest(field=field,value=value), self.assertRaises(ValueError):
                    simulate(replace(self.fixture(), **{field:value}), self.config)
        for change in ({'release_ramp_days':0},{'allocation':1.1},{'route_reference':'panama'}, {'historical_origin':'2023-11-02'}):
            with self.assertRaises(ValueError):
                simulate(replace(self.fixture(), **change), self.config)
        for change in ({'days':0},{'days':1.2},{'reference_production_million_bpd':float('nan')}):
            with self.assertRaises(ValueError):
                simulate(self.fixture(), dict(self.config, **change))

    def test_summary_horizon_and_cap(self):
        config = copy.deepcopy(self.config)
        config['reference_production_million_bpd']=4
        config['route_reference_million_bpd']['suez_sumed']=4
        rows = simulate(self.fixture(), config)
        self.assertEqual(rows[0]['price_proxy'],205)
        self.assertEqual(summarize(self.fixture(),rows,30,4)['cap_binding_days'],2)
        for horizon in (0,181,1.5):
            with self.assertRaises(ValueError): summarize(self.fixture(),rows,horizon,4)

    def test_manifest_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            inventory=root/'docs/calibration_inventory'
            inventory.mkdir(parents=True)
            source=root/'fixture.txt'
            source.write_text('original\n',encoding='utf-8')
            manifest=inventory/'manifest.json'
            manifest.write_text(json.dumps({'files':{'fixture.txt':text_hash(source)}}),encoding='utf-8')
            pin=text_hash(manifest)
            verify_manifest(root,'manifest.json',pin)
            source.write_text('changed\n',encoding='utf-8')
            with self.assertRaises(ValueError): verify_manifest(root,'manifest.json',pin)
            manifest.write_text('{}',encoding='utf-8')
            with self.assertRaises(ValueError): verify_manifest(root,'manifest.json',pin)

    def test_cli_default_does_not_execute_or_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'verification'
            command=[sys.executable,'-m','diagnostics.sensitivity','--output',str(output)]
            subprocess.run(command,cwd=ROOT,check=True,capture_output=True)
            self.assertEqual([p.name for p in output.iterdir()],['run_manifest.json'])
            record=json.loads((output/'run_manifest.json').read_text(encoding='utf-8'))
            self.assertEqual(record['status'],'INPUTS_VERIFIED_STUDY_NOT_EXECUTED')
            self.assertEqual(len(record['cases_sha256']),689)
            before=hashlib.sha256((output/'run_manifest.json').read_bytes()).hexdigest()
            self.assertNotEqual(subprocess.run(command,cwd=ROOT,capture_output=True).returncode,0)
            self.assertEqual(before,hashlib.sha256((output/'run_manifest.json').read_bytes()).hexdigest())

    def test_execution_writer_fixture_and_failed_run_status(self):
        # Three fixture days only, not a run of the frozen study.
        config=dict(self.config,days=3,summary_horizons=[3])
        with tempfile.TemporaryDirectory() as tmp:
            for fail in (False,True):
                output=Path(tmp)/str(fail)
                with patch('sys.argv',['sensitivity','--execute','--output',str(output)]), \
                     patch('diagnostics.sensitivity.load_design',return_value=(config,[self.fixture()])):
                    if fail:
                        with patch('diagnostics.sensitivity.simulate',side_effect=ArithmeticError('fixture failure')):
                            with self.assertRaises(ArithmeticError): main()
                    else:
                        main()
                record=json.loads((output/'run_manifest.json').read_text(encoding='utf-8'))
                if fail:
                    self.assertEqual(record['status'],'INCOMPLETE')
                    self.assertNotIn('outputs_sha256',record)
                else:
                    self.assertEqual(record['status'],'HYPOTHETICAL_DIAGNOSTIC_EXECUTED_NOT_CALIBRATED')
                    for name,digest in record['outputs_sha256'].items():
                        self.assertEqual(hashlib.sha256((output/name).read_bytes()).hexdigest(),digest)
                    self.assertEqual(len((output/'daily.csv').read_text(encoding='utf-8').splitlines()),4)
                    summaries=json.loads((output/'summaries.json').read_text(encoding='utf-8'))
                    self.assertEqual(len(summaries),1)


if __name__ == '__main__':
    unittest.main()
