"""0.9 trajectory execution. Default CLI verifies inputs without running cases."""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import platform
import shutil
import subprocess
import sys

from diagnostics import depletion_inputs as inputs
from diagnostics.sensitivity import Case, ROOT, simulate, summarize, text_hash

RECEIPT_SHA256 = 'dabdf5217a16641e4a942800065e1421d6f0c388543cd2ff1f553aa7b96a5c1c'
RECEIPT = Path('docs/calibration_inventory/depletion_materialization_receipt_0_9.json')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_materialized(folder: Path) -> tuple[dict, tuple[inputs.MaterializedCase, ...]]:
    config, designs = inputs.load_design()
    if text_hash(ROOT / RECEIPT) != RECEIPT_SHA256:
        raise ValueError('Materialization receipt changed')
    receipt = json.loads((ROOT / RECEIPT).read_text(encoding='utf-8'))
    if digest(folder/'materialization_manifest.json') != receipt['materialization_manifest_sha256']:
        raise ValueError('Input provenance mismatch')
    manifest = json.loads((folder/'materialization_manifest.json').read_text(encoding='utf-8'))
    if (manifest['status'] != 'INPUTS_MATERIALIZED_STUDY_NOT_EXECUTED' or
            manifest['study_executed'] is not False or
            manifest['design_manifest_sha256'] != inputs.MANIFEST_SHA256 or
            manifest['source_sha256'] != text_hash(Path(inputs.__file__)) or
            manifest['case_count'] != config['case_count'] or
            digest(folder/'materialized_inputs.json') != manifest['inputs_sha256']):
        raise ValueError('Materialized inputs failed provenance checks')
    saved = json.loads((folder/'materialized_inputs.json').read_text(encoding='utf-8'))
    if len(saved) != len(designs):
        raise ValueError('Incomplete materialized table')
    cases = tuple(inputs.materialize(d, config) for d in designs)
    if saved != [asdict(c) for c in cases]:
        raise ValueError('Saved inputs differ from frozen materialization')
    return config, cases


def legacy_case(case: inputs.MaterializedCase) -> Case:
    if not isinstance(case, inputs.MaterializedCase):
        raise ValueError('Materialized inputs required')
    raw = asdict(case.design)
    values = {k: raw[k] for k in Case.__dataclass_fields__ if k in raw}
    values.update(block='A', commercial_production_days=case.commercial_production_days,
                  strategic_production_days=case.strategic_production_days)
    return Case(**values)


def equation_config(config: dict) -> dict:
    # These proxy constants are frozen in the preserved 0.8 specification.
    return dict(config, reroute_time_constant_days=10,
                optional_price_proxy=dict(base=82, elasticity=.18, premium_cap=1.5))


def simulate_case(case: inputs.MaterializedCase, config: dict) -> list[dict]:
    """Use the unchanged 0.8 equations; only identities and output labels are new."""
    return simulate(legacy_case(case), equation_config(config))


def summarize_case(case: inputs.MaterializedCase, rows: list[dict], horizon: int, config: dict) -> dict:
    result = summarize(legacy_case(case), rows, horizon, config['reference_production_million_bpd'])
    result['block'] = case.design.block
    result.update(inputs.boundary_metrics(case, horizon, config))
    part = rows[:horizon]
    tolerance = config['absolute_classification_tolerance']
    release = math.fsum(r['strategic_release'] for r in part)
    unmet = math.fsum(r['physical_shortage'] for r in part)
    expected_release = min(case.strategic_production_days, result['unconstrained_release_production_days'])
    expected_unmet = max(0, result['commercial_required_production_days']-case.commercial_production_days)
    if abs(release-expected_release) > tolerance or abs(unmet-expected_unmet) > tolerance:
        raise ArithmeticError('Cumulative threshold identity failed')
    result.update(actual_release_production_days=release, cumulative_unmet_production_days=unmet)
    for label, cutoff in [('raw', 0.0), ('tolerance', tolerance)]:
        shortage_days = [r['day'] for r in part if r['physical_shortage'] > cutoff]
        result[f'first_shortage_day_{label}'] = next(iter(shortage_days), None)
        result[f'shortage_days_{label}'] = len(shortage_days)
        result[f'cumulative_shortage_positive_{label}'] = unmet > cutoff
        for stock in ('commercial', 'strategic'):
            initial = getattr(case, stock+'_production_days')
            depletion = [r['day'] for r in part if r[stock+'_stock'] <= cutoff]
            # Empty initial stocks are never labeled positive-stock depletion.
            result[f'positive_{stock}_depleted_{label}'] = initial > 0 and bool(depletion)
            result[f'first_positive_{stock}_depletion_day_{label}'] = next(iter(depletion), None) if initial > 0 else None
    return result


def audit_rows(case: inputs.MaterializedCase, rows: list[dict], config: dict) -> None:
    """Check saved daily equations and balances without calling simulate."""
    if [r['day'] for r in rows] != list(range(config['days'])):
        raise ValueError('Daily coverage or ordering mismatch')
    d = case.design
    commercial, strategic = case.commercial_production_days, case.strategic_production_days
    for r in rows:
        if not all(isinstance(v, (int, float, bool)) and math.isfinite(v) for v in r.values()):
            raise ValueError('Nonfinite daily values')
        t = r['day']
        decay = 1 if t < d.duration_days else (0 if d.recovery_to_5pct_days == 0 else 20**(-(t-d.duration_days)/d.recovery_to_5pct_days))
        severity = d.severity*decay
        gross = d.allocation*config['route_reference_million_bpd'][d.route_reference]/config['reference_production_million_bpd']*severity
        request = 0 if t < d.release_delay_days else d.release_fraction_per_day*(1-math.exp(-(t-d.release_delay_days)/d.release_ramp_days))
        release = min(gross, request, strategic)
        market = gross-release
        draw = min(market, commercial)
        expected = dict(severity=severity, reroute_fraction=0, gross_gap=gross,
                        strategic_release=release, market_gap=market, commercial_draw=draw,
                        physical_shortage=market-draw, commercial_stock=commercial-draw,
                        strategic_stock=strategic-release, price_proxy=82*(1+min(1.5,market/.18)),
                        cap_binding=market/.18>=1.5)
        if set(r) != set(expected)|{'day'}:
            raise ValueError('Unexpected daily schema')
        for name, value in expected.items():
            if abs(r[name]-value) > config['absolute_classification_tolerance']:
                raise ValueError(f'Daily equation mismatch: {name}')
        if min(r['commercial_stock'],r['strategic_stock'],r['physical_shortage']) < 0:
            raise ValueError('Negative daily state')
        commercial, strategic = r['commercial_stock'], r['strategic_stock']


def source_hashes() -> dict:
    return {name:text_hash(Path(__file__).with_name(name)) for name in
            ('depletion_runner.py','depletion_report.py','depletion_inputs.py','sensitivity.py')}


def run_study(folder: Path, output: Path, execute: bool = False) -> None:
    config, cases = load_materialized(folder)
    output.mkdir(parents=True, exist_ok=False)
    record = dict(status='INCOMPLETE', study_executed=False, case_count=len(cases),
                  design_manifest_sha256=inputs.MANIFEST_SHA256, receipt_sha256=RECEIPT_SHA256,
                  source_hashes=source_hashes(), python_version=sys.version, platform=platform.platform(),
                  executable_sha256=digest(Path(sys.executable)),
                  git_head_at_invocation=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),
                  worktree_dirty=bool(subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain'],text=True).strip()))
    manifest = output/'run_manifest.json'
    def save():
        manifest.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    save()
    for name in ('materialization_manifest.json','materialized_inputs.json'):
        shutil.copyfile(folder/name,output/name)
    record['input_hashes'] = {name:digest(output/name) for name in ('materialization_manifest.json','materialized_inputs.json')}
    if not execute:
        record['status']='INPUTS_VERIFIED_STUDY_NOT_EXECUTED'
        save()
        return
    summaries=[]
    duplicates={}
    with (output/'daily.csv').open('w',encoding='utf-8',newline='') as f:
        writer=None
        for case in cases:
            rows=simulate_case(case,config)
            audit_rows(case,rows,config)
            key=tuple(v for k,v in asdict(legacy_case(case)).items() if k not in ('case_id','block'))
            row_hash=hashlib.sha256(json.dumps(rows,sort_keys=True,allow_nan=False).encode()).hexdigest()
            if key in duplicates and duplicates[key]!=row_hash:
                raise ArithmeticError('Duplicate parameter results disagree')
            duplicates[key]=row_hash
            if writer is None:
                writer=csv.DictWriter(f,fieldnames=['case_id',*rows[0]],lineterminator='\n')
                writer.writeheader()
            writer.writerows(dict(case_id=case.design.case_id,**r) for r in rows)
            summaries.extend(summarize_case(case,rows,h,config) for h in config['summary_horizons'])
    (output/'summaries.json').write_text(json.dumps(summaries,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    record.update(status='HYPOTHETICAL_0_9_EXECUTED_NOT_CALIBRATED', study_executed=True,
                  daily_rows=len(cases)*config['days'],summary_rows=len(summaries),unique_parameter_cases=len(duplicates),
                  outputs_sha256={name:digest(output/name) for name in ('daily.csv','summaries.json')})
    save()


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    run_study(args.inputs,args.output,args.execute)
    print('Study executed' if args.execute else 'Inputs verified; study not executed')


if __name__=='__main__':
    main()
