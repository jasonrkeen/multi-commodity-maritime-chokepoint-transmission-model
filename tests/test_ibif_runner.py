import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'tools/validate_ibif_equivalence.py'
spec = importlib.util.spec_from_file_location('equivalence_runner', SCRIPT)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class RunnerTests(unittest.TestCase):
    def test_checks_remain_active_under_optimized_python(self):
        code = f"import runpy; m=runpy.run_path({str(SCRIPT)!r}); m['require'](False, 'expected failure')"
        process = subprocess.run([sys.executable, '-O', '-c', code], capture_output=True, text=True)
        self.assertNotEqual(process.returncode, 0)
        self.assertIn('expected failure', process.stderr)

    def test_empty_baseline_cannot_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, 'missing or empty'):
                runner.compare_outputs(Path(folder), Path(folder), False, Path(folder)/'render')

    def test_output_changes_and_missing_files_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            a, b = Path(folder)/'a', Path(folder)/'b'
            a.mkdir(); b.mkdir()
            files = {'commodity_daily.csv':'x\n1\n', 'scenario_summary.csv':'x\n1\n',
                     'monte_carlo_summary.csv':'x\n1\n', 'executive_brief.pdf':'same fixture',
                     'model_run_metadata.json':json.dumps({'generated_at_utc':'a','scenario':'x'})}
            for name, data in files.items():
                (a/name).write_text(data); (b/name).write_text(data)
            (b/'model_run_metadata.json').write_text(json.dumps({'generated_at_utc':'b','scenario':'x'}))
            result=runner.compare_outputs(a,b,False,Path(folder)/'render')
            self.assertEqual(len(result['exceptions']),1)
            (b/'commodity_daily.csv').write_text('x\n2\n')
            with self.assertRaisesRegex(ValueError,'Unexpected output difference'):
                runner.compare_outputs(a,b,False,Path(folder)/'render')
            (b/'commodity_daily.csv').unlink()
            with self.assertRaisesRegex(ValueError,'inventory'):
                runner.compare_outputs(a,b,False,Path(folder)/'render')
