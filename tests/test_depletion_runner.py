"""Small engineering runs only; never execute the frozen 3,997-case study."""
from contextlib import contextmanager
from dataclasses import replace,asdict
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from diagnostics import depletion_inputs as inp
from diagnostics import depletion_runner as run
from diagnostics import depletion_report as report
from diagnostics.sensitivity import text_hash


class DepletionRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config,design=inp.load_design()
        cls.fixed=design[0]
        cls.scaled=next(c for c in design if c.block=='T')
        cls.null=design[-1]

    def fixture_cases(self):
        designs=(replace(self.fixed,case_id='fixtureF1',commercial_production_days=.1),
                 replace(self.fixed,case_id='fixtureF2',commercial_production_days=.2),
                 replace(self.scaled,case_id='fixtureT1',commercial_threshold_multiplier=1),
                 replace(self.scaled,case_id='fixtureT2',commercial_threshold_multiplier=1,strategic_threshold_multiplier=1),
                 self.null)
        return tuple(inp.materialize(d,self.config) for d in designs)

    @contextmanager
    def fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'inputs';folder.mkdir()
            cases=self.fixture_cases()
            config=dict(self.config,case_count=5,block_counts={'F':2,'T':2,'N':1})
            (folder/'materialized_inputs.json').write_text(json.dumps([asdict(c) for c in cases]),encoding='utf-8')
            (folder/'materialization_manifest.json').write_text('{"fixture":true}',encoding='utf-8')
            with patch.object(run,'load_materialized',return_value=(config,cases)):
                yield root,folder,config,cases

    def test_input_loader_rejects_hash_and_receipt_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'inputs'
            config,design=inp.load_design()
            inp.write_inputs(folder,config,design)
            path=root/run.RECEIPT;path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'materialization_manifest_sha256':run.digest(folder/'materialization_manifest.json')}),encoding='utf-8')
            with patch.object(run,'ROOT',root),patch.object(run,'RECEIPT_SHA256',text_hash(path)):
                loaded=run.load_materialized(folder)
                self.assertEqual(len(loaded[1]),3997)
                (folder/'materialized_inputs.json').write_text('[]',encoding='utf-8')
                with self.assertRaises(ValueError):run.load_materialized(folder)
                path.write_text('{}',encoding='utf-8')
                with self.assertRaises(ValueError):run.load_materialized(folder)

    def test_equation_and_cumulative_audit_on_fixture(self):
        for case in self.fixture_cases():
            rows=run.simulate_case(case,self.config)
            run.audit_rows(case,rows,self.config)
            for h in (30,90,180):
                s=run.summarize_case(case,rows,h,self.config)
                self.assertAlmostEqual(s['cumulative_unmet_production_days'],max(0,s['commercial_required_production_days']-case.commercial_production_days),delta=1e-10)
                self.assertEqual(s['block'],case.design.block)
        rows[0]['market_gap']+=.1
        with self.assertRaises(ValueError):run.audit_rows(case,rows,self.config)

    def test_empty_stock_is_not_positive_stock_depletion(self):
        case=inp.materialize(self.null,self.config)
        s=run.summarize_case(case,run.simulate_case(case,self.config),180,self.config)
        self.assertTrue(s['commercial_initially_empty'])
        self.assertFalse(s['positive_commercial_depleted_raw'])
        self.assertIsNone(s['first_positive_commercial_depletion_day_raw'])
        self.assertIsNone(s['first_shortage_day_raw'])
        self.assertEqual(s['shortage_days_raw'],0)

    def test_equal_boundary_tolerance_and_depletion_flags(self):
        case=inp.materialize(replace(self.scaled,commercial_threshold_multiplier=1,strategic_threshold_multiplier=1),self.config)
        s=run.summarize_case(case,run.simulate_case(case,self.config),180,self.config)
        self.assertTrue(s['positive_commercial_depleted_tolerance'])
        self.assertFalse(s['cumulative_shortage_positive_tolerance'])
        self.assertFalse(s['shortage_expected_tolerance'])

    def test_cumulative_small_shortage_differs_from_daily_count(self):
        case=inp.materialize(replace(self.scaled,commercial_threshold_multiplier=1),self.config)
        # Deliberately small numerical boundary fixture; raw values are retained.
        case=replace(case,commercial_production_days=case.commercial_production_days-1e-12)
        s=run.summarize_case(case,run.simulate_case(case,self.config),180,self.config)
        self.assertTrue(s['shortage_expected_raw'])
        self.assertFalse(s['shortage_expected_tolerance'])
        self.assertGreaterEqual(s['shortage_days_raw'],s['shortage_days_tolerance'])

    def test_default_no_execution_and_no_overwrite(self):
        with self.fixture() as (root,folder,config,cases):
            with patch.object(run,'simulate_case',side_effect=AssertionError('must not execute')):
                run.run_study(folder,root/'verify')
            record=json.loads((root/'verify/run_manifest.json').read_text(encoding='utf-8'))
            self.assertFalse(record['study_executed'])
            self.assertEqual(record['status'],'INPUTS_VERIFIED_STUDY_NOT_EXECUTED')
            self.assertFalse((root/'verify/daily.csv').exists())
            with self.assertRaises(FileExistsError):run.run_study(folder,root/'verify')

    def test_failed_run_cannot_be_reported(self):
        with self.fixture() as (root,folder,config,cases):
            with patch.object(run,'simulate_case',side_effect=ArithmeticError('fixture')):
                with self.assertRaises(ArithmeticError):run.run_study(folder,root/'run',True)
            record=json.loads((root/'run/run_manifest.json').read_text(encoding='utf-8'))
            self.assertEqual(record['status'],'INCOMPLETE')
            with self.assertRaises(ValueError):report.report(root/'run',root/'report')
            self.assertFalse((root/'report').exists())

    def test_fixture_execution_report_hashes_and_labels(self):
        with self.fixture() as (root,folder,config,cases):
            run.run_study(folder,root/'run',True)
            report.report(root/'run',root/'report')
            record=json.loads((root/'report/report_manifest.json').read_text(encoding='utf-8'))
            self.assertEqual(record['matched_pairs'],2)
            self.assertEqual(record['pair_horizons'],6)
            for name,digest in record['outputs_sha256'].items():self.assertEqual(run.digest(root/'report'/name),digest)
            pairs=[json.loads(x) for x in (root/'report/matched_pairs.jsonl').read_text(encoding='utf-8').splitlines()]
            self.assertEqual({p['contrast_kind'] for p in pairs},{'single_physical_factor','normalized_multi_input_contrast'})
            for pair in pairs:
                self.assertIn('release_delay_days',pair['held_fixed_design_fields'])
            boundaries=json.loads((root/'report/boundaries.json').read_text(encoding='utf-8'))
            self.assertEqual(len(boundaries),15)
            self.assertEqual(len({r['initial_commercial_production_days'] for r in boundaries if r['case_id']=='fixtureT1'}),1)
            ranges=json.loads((root/'report/ranges.json').read_text(encoding='utf-8'))
            null=next(r for r in ranges if r['block']=='N' and r['horizon_days']==180)
            self.assertEqual(null['metrics']['first_shortage_day_raw']['null_count'],1)
            with self.assertRaises(FileExistsError):report.report(root/'run',root/'report')

    def test_saved_output_tampering_is_rejected(self):
        with self.fixture() as (root,folder,config,cases):
            run.run_study(folder,root/'run',True)
            (root/'run/daily.csv').write_text('bad',encoding='utf-8')
            with self.assertRaises(ValueError):report.verify_run(root/'run')

    def test_rehashed_bad_summary_still_fails_recomputation(self):
        with self.fixture() as (root,folder,config,cases):
            run.run_study(folder,root/'run',True)
            path=root/'run/summaries.json'
            values=json.loads(path.read_text(encoding='utf-8'));values[0]['shortage_days_raw']+=1
            path.write_text(json.dumps(values),encoding='utf-8')
            manifest=root/'run/run_manifest.json';record=json.loads(manifest.read_text(encoding='utf-8'))
            record['outputs_sha256']['summaries.json']=run.digest(path)
            manifest.write_text(json.dumps(record),encoding='utf-8')
            with self.assertRaises(ValueError):report.verify_run(root/'run')

    def test_duplicate_cases_are_retained_and_agree(self):
        with self.fixture() as (root,folder,config,cases):
            duplicate=replace(cases[0],design=replace(cases[0].design,case_id='fixtureF2'))
            altered=(cases[0],duplicate,*cases[2:])
            with patch.object(run,'load_materialized',return_value=(config,altered)):
                run.run_study(folder,root/'run',True)
                record=json.loads((root/'run/run_manifest.json').read_text(encoding='utf-8'))
                self.assertEqual(record['case_count'],5)
                self.assertEqual(record['unique_parameter_cases'],4)
                report.verify_run(root/'run')

    def test_reporting_failure_retains_incomplete_status(self):
        with self.fixture() as (root,folder,config,cases):
            run.run_study(folder,root/'run',True)
            with patch.object(report,'extrema',side_effect=ValueError('fixture report failure')):
                with self.assertRaises(ValueError):report.report(root/'run',root/'report')
            record=json.loads((root/'report/report_manifest.json').read_text(encoding='utf-8'))
            self.assertEqual(record['status'],'INCOMPLETE')


if __name__=='__main__':unittest.main()
