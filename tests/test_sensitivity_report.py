import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from diagnostics.sensitivity_report import extrema, matched_pairs, audit_run, close


class SensitivityReportTests(unittest.TestCase):
    def test_extrema_preserve_ties_nulls_and_zero(self):
        result=extrema([dict(case_id='a',v=None),dict(case_id='b',v=0),
                        dict(case_id='c',v=2),dict(case_id='d',v=2)],'v')
        self.assertEqual(result,dict(min=0,max=2,min_ids=['b'],max_ids=['c','d'],null_count=1))
        self.assertEqual(extrema([dict(case_id='a',v=None)],'v')['min'],None)

    def test_pairs_hold_every_other_factor_and_block_fixed(self):
        cases=[dict(case_id=str(i),block=b,x=x,y=y,status='design',historical_origin='NONE')
               for i,(b,x,y) in enumerate([('A',0,1),('A',1,1),('A',2,1),('A',2,2),('B',0,1)])]
        pairs=matched_pairs(cases)
        self.assertEqual(len(pairs),4)  # three x level pairs plus one y pair
        lookup={c['case_id']:c for c in cases}
        for pair in pairs:
            left,right=lookup[pair['low_case']],lookup[pair['high_case']]
            self.assertEqual(left['block'],right['block'])
            self.assertLess(left[pair['factor']],right[pair['factor']])
            self.assertEqual(sum(left[k]!=right[k] for k in ('x','y')),1)

    def test_route_order_is_explicit_and_not_numeric_coercion(self):
        pairs=matched_pairs([dict(case_id='a',block='A',route='suez',x=1),
                             dict(case_id='b',block='A',route='bab',x=1)])
        self.assertEqual((pairs[0]['low'],pairs[0]['high']),('bab','suez'))
        self.assertEqual(pairs[0]['low_case'],'b')

    def test_numerical_audit_fails_closed(self):
        close(1,1+1e-12)
        for other in (1.001,float('nan'),float('inf')):
            with self.assertRaises(ValueError): close(1,other)

    def test_incomplete_run_is_rejected_before_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'run_manifest.json').write_text(json.dumps({'status':'INCOMPLETE'}),encoding='utf-8')
            with patch('diagnostics.sensitivity_report.load_design',return_value=({},[])):
                with self.assertRaisesRegex(ValueError,'not complete'): audit_run(root)


if __name__=='__main__':
    unittest.main()
