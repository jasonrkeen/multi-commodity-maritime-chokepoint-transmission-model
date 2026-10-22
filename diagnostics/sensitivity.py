"""Frozen 0.8 physical diagnostic. Standard library only; no model imports."""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass, fields
import hashlib
import json
import math
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = Path('docs/calibration_inventory')
# Independent pins prevent a modified manifest from silently blessing changed inputs.
DESIGN_MANIFEST_SHA256 = 'a554b0e83c0a621fb087745e93603d32cef408f18c26cd3d43fd8a9bf4305fae'
REPLAY_MANIFEST_SHA256 = '9b6513c9ead3ddad69285595e98aa646118d803816bbd2c9c0ef116a6668e695'


def text_hash(path: Path) -> str:
    return hashlib.sha256(path.read_text(encoding='utf-8').replace('\r\n', '\n').encode('utf-8')).hexdigest()


@dataclass(frozen=True)
class Case:
    case_id: str
    block: str
    route_reference: str
    allocation: float
    severity: float
    duration_days: int
    recovery_to_5pct_days: int
    reroute_fraction: float
    commercial_production_days: float
    strategic_production_days: float
    release_fraction_per_day: float
    release_delay_days: int
    release_ramp_days: int
    status: str = 'DESIGN_ONLY_NOT_RUN'
    historical_origin: str = 'NONE'

    def validate(self) -> None:
        for name in ('allocation', 'severity', 'reroute_fraction', 'release_fraction_per_day',
                     'commercial_production_days', 'strategic_production_days'):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or value < 0:
                raise ValueError(f'Invalid {name}')
        for name in ('allocation', 'severity', 'reroute_fraction', 'release_fraction_per_day'):
            if getattr(self, name) > 1:
                raise ValueError(f'Invalid {name}')
        for name in ('duration_days', 'recovery_to_5pct_days', 'release_delay_days', 'release_ramp_days'):
            value = getattr(self, name)
            if type(value) is not int or value < (1 if name == 'release_ramp_days' else 0):
                raise ValueError(f'Invalid {name}')
        if self.route_reference not in ('suez_sumed', 'bab'):
            raise ValueError('Unknown route')
        if not self.case_id or self.block not in ('A', 'B', 'C', 'N'):
            raise ValueError('Invalid case identity')
        if self.status != 'DESIGN_ONLY_NOT_RUN' or self.historical_origin != 'NONE':
            raise ValueError('Not a hypothetical design case')


def verify_manifest(root: Path, name: str, pin: str) -> dict[str, str]:
    path = root / INVENTORY / name
    if text_hash(path) != pin:
        raise ValueError(f'Changed manifest: {name}')
    entries = json.loads(path.read_text(encoding='utf-8'))['files']
    for relative, expected in entries.items():
        source = (root / relative).resolve()
        if not source.is_relative_to(root.resolve()) or text_hash(source) != expected:
            raise ValueError(f'Frozen file mismatch: {relative}')
    return entries


def load_design(root: Path = ROOT) -> tuple[dict, list[Case]]:
    verify_manifest(root, 'sensitivity_manifest_0_8.json', DESIGN_MANIFEST_SHA256)
    verify_manifest(root, 'freeze_manifest_0_6.json', REPLAY_MANIFEST_SHA256)
    config = json.loads((root / INVENTORY / 'sensitivity_design_0_8.json').read_text(encoding='utf-8'))
    integer_fields = {'duration_days', 'recovery_to_5pct_days', 'release_delay_days', 'release_ramp_days'}
    strings = {'case_id', 'block', 'route_reference', 'status', 'historical_origin'}
    cases = []
    with (root / INVENTORY / config['case_file']).open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        if set(reader.fieldnames or []) != {f.name for f in fields(Case)}:
            raise ValueError('Unexpected case schema')
        for row in reader:
            case = Case(**{k: v if k in strings else int(v) if k in integer_fields else float(v) for k, v in row.items()})
            case.validate()
            cases.append(case)
    if len(cases) != config['case_count'] or len({c.case_id for c in cases}) != len(cases):
        raise ValueError('Case count or identity mismatch')
    if {b: sum(c.block == b for c in cases) for b in config['block_counts']} != config['block_counts']:
        raise ValueError('Block count mismatch')
    return config, cases


def simulate(case: Case, config: dict) -> list[dict]:
    """Daily end-of-day stocks; depletion day uses this zero-based day index."""
    case.validate()
    days = config['days']
    if type(days) is not int or days <= 0:
        raise ValueError('Invalid horizon')
    q_total = config['reference_production_million_bpd']
    route = config['route_reference_million_bpd'][case.route_reference]
    tau = config['reroute_time_constant_days']
    price = config['optional_price_proxy']
    for value in (q_total, route, tau, price['base'], price['elasticity'], price['premium_cap']):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError('Invalid reference configuration')
    if route > q_total:
        raise ValueError('Route exceeds reference production')
    q = case.allocation * route / q_total
    commercial, strategic = case.commercial_production_days, case.strategic_production_days
    rows = []
    for day in range(days):
        elapsed = day - case.duration_days
        severity = case.severity if elapsed < 0 else (0.0 if case.recovery_to_5pct_days == 0 else case.severity * math.exp(-math.log(20) * elapsed / case.recovery_to_5pct_days))
        reroute = case.reroute_fraction * -math.expm1(-day / tau)
        gross = q * severity * (1 - reroute)
        requested = 0.0 if day < case.release_delay_days else case.release_fraction_per_day * -math.expm1(-(day - case.release_delay_days) / case.release_ramp_days)
        release = min(gross, requested, strategic)
        strategic -= release
        market = gross - release
        draw = min(market, commercial)
        commercial -= draw
        shortage = market - draw
        premium = market / price['elasticity']
        row = dict(day=day, severity=severity, reroute_fraction=reroute, gross_gap=gross,
                   strategic_release=release, market_gap=market, commercial_draw=draw,
                   physical_shortage=shortage, commercial_stock=commercial, strategic_stock=strategic,
                   price_proxy=price['base'] * (1 + min(price['premium_cap'], premium)),
                   cap_binding=premium >= price['premium_cap'])
        if not all(math.isfinite(v) for v in row.values()) or min(commercial, strategic, shortage) < 0:
            raise ArithmeticError('Nonfinite or negative state')
        if not math.isclose(gross, release + draw + shortage, rel_tol=0, abs_tol=1e-10):
            raise ArithmeticError('Mass balance failed')
        rows.append(row)
    for key, initial in [('commercial_draw', case.commercial_production_days), ('strategic_release', case.strategic_production_days)]:
        if math.fsum(r[key] for r in rows) > initial + 1e-10:
            raise ArithmeticError('Stock budget exceeded')
    return rows


def summarize(case: Case, rows: list[dict], horizon: int, production: float) -> dict:
    if type(horizon) is not int or not 0 < horizon <= len(rows):
        raise ValueError('Invalid summary horizon')
    if isinstance(production, bool) or not math.isfinite(production) or production <= 0:
        raise ValueError('Invalid summary production')
    part = rows[:horizon]
    result = dict(case_id=case.case_id, block=case.block, horizon_days=horizon)
    for name in ('market_gap', 'physical_shortage', 'price_proxy'):
        result[f'mean_{name}'] = math.fsum(r[name] for r in part) / horizon
        result[f'peak_{name}'] = max(r[name] for r in part)
    result['cumulative_shortage_million_barrels'] = production * math.fsum(r['physical_shortage'] for r in part)
    for name, draw in [('commercial', 'commercial_draw'), ('strategic', 'strategic_release')]:
        result[f'cumulative_{draw}_production_days'] = math.fsum(r[draw] for r in part)
        result[f'min_{name}_stock_production_days'] = min(r[f'{name}_stock'] for r in part)
        result[f'end_{name}_stock_production_days'] = part[-1][f'{name}_stock']
        result[f'first_{name}_depletion_day'] = next((r['day'] for r in part if r[f'{name}_stock'] == 0), None)
        result[f'{name}_initially_empty'] = getattr(case, f'{name}_production_days') == 0
    result['cap_binding_days'] = sum(r['cap_binding'] for r in part)
    return result


def provenance(config: dict, cases: list[Case]) -> dict:
    return dict(status='INPUTS_VERIFIED_NOT_STUDY_RESULTS', historical_replay=False,
                production_model_run=False, case_count=len(cases),
                design_manifest_sha256=DESIGN_MANIFEST_SHA256, replay_manifest_sha256=REPLAY_MANIFEST_SHA256,
                harness_sha256=text_hash(Path(__file__)), python_version=sys.version,
                platform=platform.platform(), executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
                cases_sha256={c.case_id: hashlib.sha256(json.dumps(asdict(c), sort_keys=True).encode('utf-8')).hexdigest() for c in cases})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New directory; existing directories are never overwritten')
    parser.add_argument('--execute', action='store_true', help='Explicitly execute hypothetical cases; default only verifies frozen inputs')
    args = parser.parse_args()
    config, cases = load_design()
    record = provenance(config, cases)
    args.output.mkdir(parents=True, exist_ok=False)
    record['status'] = 'INCOMPLETE' if args.execute else 'INPUTS_VERIFIED_STUDY_NOT_EXECUTED'
    manifest = args.output / 'run_manifest.json'
    manifest.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    if args.execute:
        summaries = []
        with (args.output / 'daily.csv').open('w', encoding='utf-8', newline='') as stream:
            writer = None
            for case in cases:
                rows = simulate(case, config)
                output_rows = [dict(case_id=case.case_id, **r) for r in rows]
                if writer is None:
                    writer = csv.DictWriter(stream, fieldnames=list(output_rows[0]), lineterminator='\n')
                    writer.writeheader()
                writer.writerows(output_rows)
                summaries.extend(summarize(case, rows, h, config['reference_production_million_bpd']) for h in config['summary_horizons'])
        (args.output / 'summaries.json').write_text(json.dumps(summaries, indent=2, allow_nan=False) + '\n', encoding='utf-8')
        record['status'] = 'HYPOTHETICAL_DIAGNOSTIC_EXECUTED_NOT_CALIBRATED'
        record['outputs_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (args.output / 'daily.csv', args.output / 'summaries.json')}
        manifest.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(record['status'])


if __name__ == '__main__':
    main()
