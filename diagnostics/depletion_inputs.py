"""Frozen 0.9 input loading and algebraic thresholds; no trajectory runner."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, fields
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import sys

from diagnostics.sensitivity import ROOT, text_hash

MANIFEST = Path('docs/calibration_inventory/depletion_manifest_0_9.json')
MANIFEST_SHA256 = '9f73628eb85789764749fe051b11605a247d49bc1a8d95856f2a9af332868fb8'


def finite_nonnegative(value: float, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or value < 0:
        raise ValueError(f'Invalid {name}')


@dataclass(frozen=True)
class DepletionCase:
    case_id: str
    block: str
    stock_basis: str
    commercial_production_days: float | None
    strategic_production_days: float | None
    strategic_threshold_multiplier: float | None
    commercial_threshold_multiplier: float | None
    release_fraction_per_day: float
    release_delay_days: int
    release_ramp_days: int
    route_reference: str
    allocation: float
    severity: float
    duration_days: int
    recovery_to_5pct_days: int
    reroute_fraction: float
    status: str
    historical_origin: str

    def validate(self) -> None:
        if not self.case_id or self.block not in ('F', 'T', 'N'):
            raise ValueError('Invalid case identity')
        if self.route_reference != 'suez_sumed' or self.status != 'DESIGN_ONLY_NOT_RUN' or self.historical_origin != 'NONE':
            raise ValueError('Not a 0.9 hypothetical design case')
        for name in ('allocation', 'severity', 'release_fraction_per_day', 'reroute_fraction'):
            value = getattr(self, name)
            finite_nonnegative(value, name)
            if value > 1:
                raise ValueError(f'Invalid {name}')
        for name in ('release_delay_days', 'release_ramp_days', 'duration_days', 'recovery_to_5pct_days'):
            value = getattr(self, name)
            if type(value) is not int or value < (1 if name == 'release_ramp_days' else 0):
                raise ValueError(f'Invalid {name}')
        if self.block == 'T':
            if self.stock_basis != 'threshold_multipliers_180d' or self.commercial_production_days is not None or self.strategic_production_days is not None:
                raise ValueError('T design stock fields must remain null')
            finite_nonnegative(self.strategic_threshold_multiplier, 'alpha')
            finite_nonnegative(self.commercial_threshold_multiplier, 'beta')
        else:
            if self.stock_basis != 'fixed_production_days' or self.strategic_threshold_multiplier is not None or self.commercial_threshold_multiplier is not None:
                raise ValueError('Fixed stocks cannot contain multipliers')
            finite_nonnegative(self.commercial_production_days, 'commercial stock')
            finite_nonnegative(self.strategic_production_days, 'strategic stock')


@dataclass(frozen=True)
class Thresholds:
    horizon_days: int
    gross_production_days: float
    unconstrained_release_production_days: float

    def commercial_required(self, strategic_stock: float) -> float:
        finite_nonnegative(strategic_stock, 'strategic stock')
        return self.gross_production_days - min(strategic_stock, self.unconstrained_release_production_days)


@dataclass(frozen=True)
class MaterializedCase:
    design: DepletionCase
    commercial_production_days: float
    strategic_production_days: float
    materialization_horizon_days: int

    def __post_init__(self) -> None:
        self.design.validate()
        finite_nonnegative(self.commercial_production_days, 'materialized commercial stock')
        finite_nonnegative(self.strategic_production_days, 'materialized strategic stock')
        if self.materialization_horizon_days != 180:
            raise ValueError('Starting stocks must use the frozen 180-day horizon')


def load_design(root: Path = ROOT) -> tuple[dict, tuple[DepletionCase, ...]]:
    if text_hash(root / MANIFEST) != MANIFEST_SHA256:
        raise ValueError('0.9 manifest changed')
    manifest = json.loads((root / MANIFEST).read_text(encoding='utf-8'))
    for relative, digest in (manifest['files'] | manifest['preserved_prior_files']).items():
        path = (root / relative).resolve()
        if not path.is_relative_to(root.resolve()) or text_hash(path) != digest:
            raise ValueError(f'Frozen file changed: {relative}')
    folder = root / MANIFEST.parent
    config = json.loads((folder / 'depletion_design_0_9.json').read_text(encoding='utf-8'))
    strings = {'case_id', 'block', 'stock_basis', 'route_reference', 'status', 'historical_origin'}
    integers = {'release_delay_days', 'release_ramp_days', 'duration_days', 'recovery_to_5pct_days'}
    nullable = {'commercial_production_days', 'strategic_production_days', 'strategic_threshold_multiplier', 'commercial_threshold_multiplier'}
    cases = []
    with (folder / config['cases_file']).open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != [field.name for field in fields(DepletionCase)]:
            raise ValueError('Unexpected case schema')
        for row in reader:
            parsed = {k: v if k in strings else None if k in nullable and v == '' else int(v) if k in integers else float(v) for k, v in row.items()}
            case = DepletionCase(**parsed)
            case.validate()
            cases.append(case)
    if len(cases) != config['case_count'] or len({c.case_id for c in cases}) != len(cases):
        raise ValueError('Case coverage or duplicate ID mismatch')
    if {b: sum(c.block == b for c in cases) for b in config['block_counts']} != config['block_counts']:
        raise ValueError('Block count mismatch')
    return config, tuple(cases)


def thresholds(case: DepletionCase, horizon: int, config: dict) -> Thresholds:
    """Sum exogenous gross gap and requested capacity, without stock-state simulation."""
    case.validate()
    if type(horizon) is not int or not 0 < horizon <= config['days']:
        raise ValueError('Invalid threshold horizon')
    production = config['reference_production_million_bpd']
    route = config['route_reference_million_bpd'][case.route_reference]
    for name, value in [('production', production), ('route', route)]:
        finite_nonnegative(value, name)
        if value == 0:
            raise ValueError(f'Zero {name}')
    if route > production:
        raise ValueError('Route exceeds production')
    gross, capacity = [], []
    for day in range(horizon):
        elapsed = day - case.duration_days
        severity = case.severity if elapsed < 0 else (0.0 if case.recovery_to_5pct_days == 0 else case.severity * math.exp(-math.log(20) * elapsed / case.recovery_to_5pct_days))
        # 0.9 freezes rerouting at zero, so no unfrozen time constant is introduced.
        if case.reroute_fraction != 0:
            raise ValueError('0.9 fixes rerouting at zero')
        gap = case.allocation * route / production * severity
        request = 0.0 if day < case.release_delay_days else case.release_fraction_per_day * -math.expm1(-(day-case.release_delay_days) / case.release_ramp_days)
        gross.append(gap)
        capacity.append(min(gap, request))
    result = Thresholds(horizon, math.fsum(gross), math.fsum(capacity))
    if not 0 <= result.unconstrained_release_production_days <= result.gross_production_days:
        raise ArithmeticError('Invalid cumulative threshold')
    return result


def materialize(case: DepletionCase, config: dict) -> MaterializedCase:
    case.validate()
    if config['threshold_materialization_horizon'] != 180:
        raise ValueError('Materialization horizon changed')
    if case.block == 'T':
        bounds = thresholds(case, 180, config)
        strategic = case.strategic_threshold_multiplier * bounds.unconstrained_release_production_days
        requirement = bounds.commercial_required(strategic)
        if bounds.unconstrained_release_production_days <= 0 or requirement <= 0:
            raise ValueError('Collapsed T threshold')
        commercial = case.commercial_threshold_multiplier * requirement
    else:
        commercial, strategic = case.commercial_production_days, case.strategic_production_days
    return MaterializedCase(case, commercial, strategic, 180)


def boundary_metrics(case: MaterializedCase, horizon: int, config: dict) -> dict:
    """Static boundary diagnostics keep the original materialized starting stocks."""
    if not isinstance(case, MaterializedCase):
        raise ValueError('Materialized inputs required')
    bounds = thresholds(case.design, horizon, config)
    required = bounds.commercial_required(case.strategic_production_days)
    margin = case.commercial_production_days - required
    tolerance = config['absolute_classification_tolerance']
    finite_nonnegative(tolerance, 'tolerance')
    return dict(horizon_days=horizon, gross_production_days=bounds.gross_production_days,
                unconstrained_release_production_days=bounds.unconstrained_release_production_days,
                commercial_required_production_days=required, commercial_margin_production_days=margin,
                strategic_margin_production_days=case.strategic_production_days-bounds.unconstrained_release_production_days,
                commercial_exact_equality=margin == 0,
                commercial_within_tolerance=abs(margin) <= tolerance,
                shortage_expected_raw=margin < 0, shortage_expected_tolerance=margin < -tolerance)


def contrast_kind(left: DepletionCase, right: DepletionCase) -> str:
    left.validate()
    right.validate()
    if left.block != right.block or left.block == 'N':
        raise ValueError('No cross-block or null matching')
    ignored = {'case_id', 'status', 'historical_origin'}
    changed = [f.name for f in fields(DepletionCase) if f.name not in ignored and getattr(left, f.name) != getattr(right, f.name)]
    allowed = {'commercial_production_days', 'strategic_production_days', 'release_fraction_per_day', 'release_delay_days', 'release_ramp_days'} if left.block == 'F' else {'strategic_threshold_multiplier', 'commercial_threshold_multiplier', 'release_fraction_per_day', 'release_delay_days', 'release_ramp_days'}
    if len(changed) != 1 or changed[0] not in allowed:
        raise ValueError('Not a permitted one-design-factor comparison')
    if left.block == 'F' or changed[0] == 'commercial_threshold_multiplier':
        return 'single_physical_factor'
    return 'normalized_multi_input_contrast'


def write_inputs(output: Path, config: dict, cases: tuple[DepletionCase, ...]) -> None:
    if len(cases) != config['case_count'] or len({c.case_id for c in cases}) != len(cases):
        raise ValueError('Incomplete or duplicate materialization input set')
    if {b: sum(c.block == b for c in cases) for b in config['block_counts']} != config['block_counts']:
        raise ValueError('Materialization block coverage mismatch')
    output.mkdir(parents=True, exist_ok=False)
    record = dict(status='INCOMPLETE', study_executed=False, source_sha256=text_hash(Path(__file__)),
                  design_manifest_sha256=MANIFEST_SHA256, python_version=sys.version,
                  platform=platform.platform(), executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest())
    manifest = output / 'materialization_manifest.json'
    manifest.write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
    rows = [asdict(materialize(case, config)) for case in cases]
    path = output / 'materialized_inputs.json'
    path.write_text(json.dumps(rows, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    record.update(status='INPUTS_MATERIALIZED_STUDY_NOT_EXECUTED', case_count=len(rows),
                  inputs_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    manifest.write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--materialize-output', type=Path, help='Optional new directory for inputs only; never executes trajectories')
    args = parser.parse_args()
    config, cases = load_design()
    if args.materialize_output is not None:
        write_inputs(args.materialize_output, config, cases)
        print('INPUTS_MATERIALIZED_STUDY_NOT_EXECUTED')
    else:
        print(f'INPUTS_VERIFIED_STUDY_NOT_EXECUTED: {len(cases)} cases')


if __name__ == '__main__':
    main()
