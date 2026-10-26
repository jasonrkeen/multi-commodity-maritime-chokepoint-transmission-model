"""Audited 0.9 ranges, stock boundaries and explicitly labeled matched contrasts."""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from dataclasses import asdict
from itertools import combinations
import json
import math
from pathlib import Path

from diagnostics import depletion_runner as runner
from diagnostics.depletion_inputs import contrast_kind
from diagnostics.sensitivity_report import extrema


def iter_pairs(cases):
    for block in ('F','T'):
        members=[c for c in cases if c.design.block==block]
        factors=['release_fraction_per_day','release_delay_days','release_ramp_days']
        factors+=['commercial_production_days','strategic_production_days'] if block=='F' else ['strategic_threshold_multiplier','commercial_threshold_multiplier']
        for factor in factors:
            groups=defaultdict(list)
            for case in members:
                design=asdict(case.design)
                key=tuple(v for k,v in design.items() if k not in ('case_id',factor))
                groups[key].append(case)
            for group in groups.values():
                for left,right in combinations(sorted(group,key=lambda c:getattr(c.design,factor)),2):
                    if getattr(left.design,factor)==getattr(right.design,factor):
                        continue
                    yield left,right,factor,contrast_kind(left.design,right.design)


def verify_run(run: Path):
    config,cases=runner.load_materialized(run)
    record=json.loads((run/'run_manifest.json').read_text(encoding='utf-8'))
    if record['status']!='HYPOTHETICAL_0_9_EXECUTED_NOT_CALIBRATED' or record['study_executed'] is not True:
        raise ValueError('No completed 0.9 study')
    if (record['source_hashes']!=runner.source_hashes() or
            record['design_manifest_sha256']!=runner.inputs.MANIFEST_SHA256 or
            record['receipt_sha256']!=runner.RECEIPT_SHA256 or record['case_count']!=len(cases)):
        raise ValueError('Run source or input lineage mismatch')
    for name in ('daily.csv','summaries.json'):
        if runner.digest(run/name)!=record['outputs_sha256'][name]:
            raise ValueError('Output hash mismatch')
    for name in ('materialized_inputs.json','materialization_manifest.json'):
        if runner.digest(run/name)!=record['input_hashes'][name]:
            raise ValueError('Input snapshot hash mismatch')
    summaries=json.loads((run/'summaries.json').read_text(encoding='utf-8'))
    indexed={(r['case_id'],r['horizon_days']):r for r in summaries}
    expected={(c.design.case_id,h) for c in cases for h in config['summary_horizons']}
    if len(summaries)!=len(expected) or set(indexed)!=expected:
        raise ValueError('Summary coverage mismatch')
    # Consume one case at a time; do not hold the full daily grid in memory.
    with (run/'daily.csv').open(encoding='utf-8',newline='') as f:
        reader=iter(csv.DictReader(f))
        for case in cases:
            rows=[]
            for day in range(config['days']):
                raw=next(reader,None)
                if raw is None or raw.pop('case_id')!=case.design.case_id:
                    raise ValueError('Daily case coverage/order mismatch')
                if raw['cap_binding'] not in ('True','False'):
                    raise ValueError('Invalid boolean encoding')
                row={k:int(v) if k=='day' else v=='True' if k=='cap_binding' else float(v) for k,v in raw.items()}
                rows.append(row)
            runner.audit_rows(case,rows,config)
            for h in config['summary_horizons']:
                computed=runner.summarize_case(case,rows,h,config)
                saved=indexed[(case.design.case_id,h)]
                if computed.keys()!=saved.keys():
                    raise ValueError('Summary schema mismatch')
                for key,value in computed.items():
                    other=saved[key]
                    if isinstance(value,float):
                        if type(other) not in (float,int) or not math.isfinite(other) or abs(value-other)>1e-10:
                            raise ValueError(f'Summary mismatch: {key}')
                    elif type(value)!=type(other) or value!=other:
                        raise ValueError(f'Summary flag/identity mismatch: {key}')
        if next(reader,None) is not None:
            raise ValueError('Unexpected extra daily records')
    if record['daily_rows']!=len(cases)*config['days'] or record['summary_rows']!=len(summaries):
        raise ValueError('Manifest row counts disagree')
    return config,cases,summaries


def report(run: Path, output: Path) -> None:
    config,cases,summaries=verify_run(run)
    output.mkdir(parents=True,exist_ok=False)
    record=dict(status='INCOMPLETE',source_hashes=runner.source_hashes(),run_manifest_sha256=runner.digest(run/'run_manifest.json'))
    manifest=output/'report_manifest.json'
    manifest.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    metadata={'case_id','block','horizon_days'}
    metrics=[k for k,v in summaries[0].items() if k not in metadata and not isinstance(v,bool)]
    flags=[k for k,v in summaries[0].items() if isinstance(v,bool)]
    ranges=[]
    for block in ['ALL',*config['block_counts']]:
        for horizon in config['summary_horizons']:
            rows=[r for r in summaries if r['horizon_days']==horizon and (block=='ALL' or r['block']==block)]
            ranges.append(dict(block=block,horizon_days=horizon,case_count=len(rows),
                               metrics={m:extrema(rows,m) for m in metrics},
                               flags={m:dict(true=sum(r[m] for r in rows),false=sum(not r[m] for r in rows)) for m in flags}))
    lookup={(r['case_id'],r['horizon_days']):r for r in summaries}
    aggregate={}
    pairs=0
    with (output/'matched_pairs.jsonl').open('w',encoding='utf-8') as f:
        for left,right,factor,kind in iter_pairs(cases):
            pairs+=1
            low,high=getattr(left.design,factor),getattr(right.design,factor)
            identity=f'{factor}:{left.design.case_id}:{right.design.case_id}'
            held={k:v for k,v in asdict(left.design).items() if k not in ('case_id',factor)}
            for horizon in config['summary_horizons']:
                a,b=lookup[(left.design.case_id,horizon)],lookup[(right.design.case_id,horizon)]
                deltas={m:None if a[m] is None or b[m] is None else b[m]-a[m] for m in metrics}
                row=dict(pair_id=identity,block=left.design.block,factor=factor,contrast_kind=kind,low=low,high=high,
                         low_case=left.design.case_id,high_case=right.design.case_id,held_fixed_design_fields=held,
                         horizon_days=horizon,deltas=deltas,flag_transitions={m:[a[m],b[m]] for m in flags})
                f.write(json.dumps(row,allow_nan=False)+'\n')
                key=(left.design.block,factor,kind,low,high,horizon)
                bucket=aggregate.setdefault(key,dict(pair_count=0,metrics={}))
                bucket['pair_count']+=1
                for m,value in deltas.items():
                    cell=bucket['metrics'].setdefault(m,dict(min=None,max=None,min_pair=None,max_pair=None,min_ties=0,max_ties=0,null_count=0))
                    if value is None:
                        cell['null_count']+=1
                        continue
                    for bound,better in [('min',lambda x,y:x<y),('max',lambda x,y:x>y)]:
                        if cell[bound] is None or better(value,cell[bound]):
                            cell[bound]=value;cell[bound+'_pair']=identity;cell[bound+'_ties']=1
                        elif value==cell[bound]:
                            cell[bound+'_ties']+=1
    matched_ranges=[dict(block=k[0],factor=k[1],contrast_kind=k[2],low=k[3],high=k[4],horizon_days=k[5],**v) for k,v in aggregate.items()]
    # Every fixed-grid point is retained; C_H(S) is the conditional joint boundary.
    boundaries=[dict(case_id=c.design.case_id,block=c.design.block,release_fraction_per_day=c.design.release_fraction_per_day,
                     release_delay_days=c.design.release_delay_days,release_ramp_days=c.design.release_ramp_days,
                     initial_commercial_production_days=c.commercial_production_days,
                     initial_strategic_production_days=c.strategic_production_days,
                     **runner.inputs.boundary_metrics(c,h,config)) for c in cases for h in config['summary_horizons']]
    outputs={'ranges.json':ranges,'matched_ranges.json':matched_ranges,'boundaries.json':boundaries,
             'cases.json':[asdict(c) for c in cases]}
    for name,value in outputs.items():
        (output/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    lines=['# Hypothetical 0.9 depletion study report','',
           'Uncalibrated sampled results: no confidence intervals, historical replay or business-impact validation. Duplicate parameter cases are not independent observations.',
           '', '| Block | Horizon | Cases | Cumulative shortage range (million barrels) | Representative min / max cases | Positive commercial depletion (tolerance) |',
           '|---|---:|---:|---:|---|---:|']
    for row in ranges:
        metric=row['metrics']['cumulative_shortage_million_barrels']
        lines.append(f'| {row["block"]} | {row["horizon_days"]} | {row["case_count"]} | {metric["min"]:.6f} to {metric["max"]:.6f} | {metric["min_ids"][0]} / {metric["max_ids"][0]} | {row["flags"]["positive_commercial_depleted_tolerance"]["true"]} |')
    lines+=['', f'{pairs} within-block matched pairs; each is evaluated at every summary horizon.',
            '', 'All exact case endpoint ties and flag counts are in ranges.json; complete original and materialized inputs are in cases.json. boundaries.json retains every timing/stock grid point and C_H(S), without empirical interpolation.',
            '', 'matched_ranges.json gives delta ranges, representative endpoint pairs and tie counts. matched_pairs.jsonl retains every pair, all held-fixed design fields, endpoint IDs and flag transitions, so all tied pair endpoints remain recoverable.',
            '', 'F comparisons and T beta comparisons are single-physical-factor. T alpha and timing comparisons are normalized multi-input contrasts, not isolated physical timing effects. Deltas are higher minus lower. Null event-day deltas are excluded from extrema and counted separately.',
            '', 'Initially empty stock is distinct from positive-stock depletion; equality depletion can occur without shortage. Raw and 1e-10 tolerance flags are separate. A cumulative shortage can exceed tolerance even if each daily shortage is below tolerance; the cumulative flag and daily-day count intentionally measure different quantities.',
            '', 'The report checks saved daily equations and balances independently of the trajectory loop, then recomputes summary values and flags using the summary implementation. This is engineering consistency checking, not an independent economic validation. No weights or expected values are assigned across cases.', '']
    (output/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    record.update(status='HYPOTHETICAL_REPORT_COMPLETE_NOT_CALIBRATED',matched_pairs=pairs,
                  pair_horizons=pairs*len(config['summary_horizons']),
                  tie_policy='All exact case endpoint ties in ranges; matched endpoint representative/count in matched_ranges; every pair retained in JSONL.',
                  null_policy='Null day deltas remain null; excluded from extrema, counted separately.',
                  interpretation='Sampled ranges only. No calibration, confidence intervals, historical replay or case weighting.',
                  outputs_sha256={name:runner.digest(output/name) for name in [*outputs,'matched_pairs.jsonl','REPORT.md']})
    manifest.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    report(args.run,args.output)
