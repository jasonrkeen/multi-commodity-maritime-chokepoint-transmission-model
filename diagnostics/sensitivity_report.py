"""Audit and describe a completed frozen sensitivity run without changing it."""
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import asdict
import hashlib
from itertools import combinations
import csv
import json
import math
from pathlib import Path

from diagnostics.sensitivity import (load_design, text_hash, DESIGN_MANIFEST_SHA256,
                                     REPLAY_MANIFEST_SHA256)

TOLERANCE = 1e-10


def close(left: float, right: float) -> None:
    if not math.isfinite(left) or not math.isfinite(right) or abs(left-right) > TOLERANCE:
        raise ValueError(f'Numerical audit failed: {left} != {right}')


def extrema(rows: list[dict], metric: str, id_field: str = 'case_id') -> dict:
    """Keep every exact tie and distinguish missing from zero."""
    valid = [r for r in rows if r[metric] is not None]
    if not valid:
        return dict(min=None, max=None, min_ids=[], max_ids=[], null_count=len(rows))
    low, high = min(r[metric] for r in valid), max(r[metric] for r in valid)
    return dict(min=low, max=high,
                min_ids=[r[id_field] for r in valid if r[metric] == low],
                max_ids=[r[id_field] for r in valid if r[metric] == high],
                null_count=len(rows)-len(valid))


def matched_pairs(cases: list[dict]) -> list[dict]:
    """All distinct levels within block, equal on every other model input."""
    factors = [k for k in cases[0] if k not in ('case_id','block','status','historical_origin')]
    pairs = []
    for factor in factors:
        groups = defaultdict(list)
        for case in cases:
            key = (case['block'], *(case[k] for k in factors if k != factor))
            groups[key].append(case)
        for group in groups.values():
            for left, right in combinations(sorted(group, key=lambda r: r[factor]), 2):
                if left[factor] != right[factor]:
                    pairs.append(dict(pair_id=f'{factor}:{left["case_id"]}:{right["case_id"]}',
                                      block=left['block'], factor=factor, low=left[factor], high=right[factor],
                                      low_case=left['case_id'], high_case=right['case_id']))
    return pairs


def audit_run(run: Path) -> tuple[dict, list[dict], list[dict], dict]:
    config, objects = load_design()
    cases = [asdict(c) for c in objects]
    case_map = {c['case_id']: c for c in cases}
    manifest = json.loads((run/'run_manifest.json').read_text(encoding='utf-8'))
    if manifest['status'] != 'HYPOTHETICAL_DIAGNOSTIC_EXECUTED_NOT_CALIBRATED':
        raise ValueError('Run is not complete')
    if (manifest['design_manifest_sha256'] != DESIGN_MANIFEST_SHA256 or
            manifest['replay_manifest_sha256'] != REPLAY_MANIFEST_SHA256 or
            manifest['case_count'] != len(cases) or
            set(manifest['cases_sha256']) != set(case_map)):
        raise ValueError('Run provenance does not match frozen design')
    if manifest['harness_sha256'] != text_hash(Path(__file__).with_name('sensitivity.py')):
        raise ValueError('Harness differs from execution source')
    for name in ('daily.csv', 'summaries.json'):
        if hashlib.sha256((run/name).read_bytes()).hexdigest() != manifest['outputs_sha256'][name]:
            raise ValueError(f'Output hash mismatch: {name}')
    for case in cases:
        digest = hashlib.sha256(json.dumps(case, sort_keys=True).encode('utf-8')).hexdigest()
        if manifest['cases_sha256'][case['case_id']] != digest:
            raise ValueError('Case hash mismatch')
    daily = defaultdict(list)
    with (run/'daily.csv').open(encoding='utf-8',newline='') as f:
        for raw in csv.DictReader(f):
            if raw['case_id'] not in case_map:
                raise ValueError('Unknown case')
            row = {k: (v=='True' if k=='cap_binding' else int(v) if k=='day' else float(v))
                   for k,v in raw.items() if k!='case_id'}
            if raw['cap_binding'] not in ('True','False') or not all(math.isfinite(v) for v in row.values()):
                raise ValueError('Invalid daily value')
            daily[raw['case_id']].append(row)
    if set(daily) != set(case_map):
        raise ValueError('Missing cases')
    duplicates = {}
    duplicate_count = 0
    for cid, rows in daily.items():
        case=case_map[cid]
        if [r['day'] for r in rows] != list(range(config['days'])):
            raise ValueError('Day coverage or order mismatch')
        commercial,strategic=case['commercial_production_days'],case['strategic_production_days']
        for row in rows:
            if min(row['commercial_stock'],row['strategic_stock'],row['physical_shortage'],row['strategic_release'],row['commercial_draw'])<0:
                raise ValueError('Negative balance')
            close(row['gross_gap'],row['strategic_release']+row['commercial_draw']+row['physical_shortage'])
            close(row['market_gap'],row['gross_gap']-row['strategic_release'])
            close(row['commercial_stock']+row['commercial_draw'],commercial)
            close(row['strategic_stock']+row['strategic_release'],strategic)
            commercial,strategic=row['commercial_stock'],row['strategic_stock']
        key=tuple(v for k,v in case.items() if k not in ('case_id','block'))
        if key in duplicates:
            if rows != daily[duplicates[key]]:
                raise ValueError('Duplicate parameter results disagree')
            duplicate_count+=1
        else:
            duplicates[key]=cid
    summaries=json.loads((run/'summaries.json').read_text(encoding='utf-8'))
    expected={(cid,h) for cid in case_map for h in config['summary_horizons']}
    if len(summaries)!=len(expected) or {(r['case_id'],r['horizon_days']) for r in summaries}!=expected:
        raise ValueError('Summary coverage mismatch')
    # Recompute every summary directly from serialized daily data, without the harness summarizer.
    for row in summaries:
        case=case_map[row['case_id']]
        part=daily[row['case_id']][:row['horizon_days']]
        if row['block']!=case['block']: raise ValueError('Block mismatch')
        for name in ('market_gap','physical_shortage','price_proxy'):
            close(row['mean_'+name],sum(r[name] for r in part)/len(part))
            close(row['peak_'+name],max(r[name] for r in part))
        close(row['cumulative_shortage_million_barrels'],sum(r['physical_shortage'] for r in part)*config['reference_production_million_bpd'])
        for name,draw in [('commercial','commercial_draw'),('strategic','strategic_release')]:
            close(row[f'cumulative_{draw}_production_days'],sum(r[draw] for r in part))
            close(row[f'end_{name}_stock_production_days'],part[-1][name+'_stock'])
            close(row[f'min_{name}_stock_production_days'],min(r[name+'_stock'] for r in part))
            if row[f'first_{name}_depletion_day']!=next((r['day'] for r in part if r[name+'_stock']==0),None):
                raise ValueError('Depletion mismatch')
            if row[f'{name}_initially_empty']!=(case[name+'_production_days']==0): raise ValueError('Initial stock flag mismatch')
        if row['cap_binding_days']!=sum(r['cap_binding'] for r in part): raise ValueError('Cap count mismatch')
    audit=dict(status='PASS',cases=len(cases),daily_rows=sum(map(len,daily.values())),
               summaries=len(summaries),unique_parameter_cases=len(duplicates),duplicate_case_rows=duplicate_count,
               frozen_manifests='UNCHANGED',all_summary_metrics_recomputed=True,
               all_daily_balances_checked=True,full_study_executed=True,historical_replay=False)
    return config,cases,summaries,audit


def build_report(run: Path, output: Path) -> dict:
    config,cases,summaries,audit=audit_run(run)
    metrics=[k for k in summaries[0] if k not in ('case_id','block','horizon_days') and not k.endswith('initially_empty')]
    ranges=[]
    for block in ['ALL',*config['block_counts']]:
        for horizon in config['summary_horizons']:
            rows=[r for r in summaries if r['horizon_days']==horizon and (block=='ALL' or r['block']==block)]
            ranges.append(dict(block=block,horizon_days=horizon,case_count=len(rows),
                               metrics={m:extrema(rows,m) for m in metrics}))
    pairs=matched_pairs(cases)
    indexed={(r['case_id'],r['horizon_days']):r for r in summaries}
    contrasts=[]
    for pair in pairs:
        for horizon in config['summary_horizons']:
            low,high=(indexed[(pair[k],horizon)] for k in ('low_case','high_case'))
            contrasts.append(dict(**pair,horizon_days=horizon,
                                  deltas={m:None if low[m] is None or high[m] is None else high[m]-low[m] for m in metrics}))
    grouped=defaultdict(list)
    for row in contrasts:
        grouped[(row['block'],row['factor'],row['low'],row['high'],row['horizon_days'])].append(dict(pair_id=row['pair_id'],**row['deltas']))
    contrast_ranges=[dict(block=k[0],factor=k[1],low=k[2],high=k[3],horizon_days=k[4],pair_count=len(rows),
                          metrics={m:extrema(rows,m,'pair_id') for m in metrics}) for k,rows in grouped.items()]
    audit.update(matched_pairs=len(pairs),matched_pair_horizons=len(contrasts))
    output.mkdir(parents=True,exist_ok=False)
    files={'cases.json':cases,'ranges.json':ranges,'matched_pairs.json':contrasts,
           'matched_ranges.json':contrast_ranges,'audit.json':audit}
    for name,value in files.items():
        (output/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    provenance=dict(run_manifest_sha256=hashlib.sha256((run/'run_manifest.json').read_bytes()).hexdigest(),
                    report_source_sha256=text_hash(Path(__file__)),
                    outputs_sha256={name:hashlib.sha256((output/name).read_bytes()).hexdigest() for name in files},
                    matching_rule='Within block; all unordered distinct levels; all other modeled inputs identical; delta high minus low; categorical route ordered lexically.',
                    tie_rule='All exact floating-point ties; rounding only for display.',
                    null_rule='Depletion deltas null when either case never depletes; exclude nulls from extrema and count them.',
                    interpretation='Sampled hypothetical extrema, not confidence bounds or calibration. No weighting or across-case expected value.')
    (output/'report_manifest.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    return audit


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(build_report(args.run,args.output),indent=2))
