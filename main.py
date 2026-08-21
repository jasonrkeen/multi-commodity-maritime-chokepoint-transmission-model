from __future__ import annotations

import argparse
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib"))

from maritime_chokepoint.io import load_inputs  # noqa: E402
from maritime_chokepoint.analysis import (  # noqa: E402
    build_scenario_comparison,
    run_calibration_sensitivity,
    summarize_calibration,
)
from maritime_chokepoint.model import (  # noqa: E402
    run_ecological_externalities,
    run_scenario,
    summarize_ecological_externalities,
    summarize_scenario,
)
from maritime_chokepoint.reporting import write_outputs  # noqa: E402
from maritime_chokepoint.simulation import (  # noqa: E402
    run_ecological_monte_carlo,
    run_monte_carlo,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Multi-commodity maritime chokepoint transmission model"
    )
    parser.add_argument(
        "--scenario", default="compound_hormuz_red_sea", help="Scenario name"
    )
    parser.add_argument("--days", type=int, default=240, help="Simulation horizon")
    parser.add_argument(
        "--simulations", type=int, default=200, help="Monte Carlo draws; 0 disables"
    )
    parser.add_argument("--seed", type=int, default=20260810, help="Random seed")
    parser.add_argument(
        "--input-dir", type=Path, default=ROOT / "data" / "input"
    )
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs")
    parser.add_argument("--list-scenarios", action="store_true")
    parser.add_argument(
        "--compare-scenarios",
        action="store_true",
        help="Write a deterministic side-by-side scenario comparison",
    )
    parser.add_argument(
        "--calibration",
        action="store_true",
        help="Run the non-driving sensitivity and calibration diagnostic",
    )
    parser.add_argument(
        "--calibration-levels",
        nargs="+",
        type=float,
        default=[0.75, 1.0, 1.25],
        help="Positive multipliers used by the four-factor calibration grid",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    inputs = load_inputs(args.input_dir)

    if args.list_scenarios:
        for name in sorted(inputs.scenario_catalog["scenario"].unique()):
            print(name)
        return

    if args.days <= 0:
        raise SystemExit("--days must be positive")
    if args.simulations < 0:
        raise SystemExit("--simulations cannot be negative")
    if not args.calibration_levels or any(
        level <= 0 for level in args.calibration_levels
    ):
        raise SystemExit("--calibration-levels must contain positive values")
    if args.scenario not in set(inputs.scenario_catalog["scenario"]):
        valid = ", ".join(sorted(inputs.scenario_catalog["scenario"].unique()))
        raise SystemExit(f"Unknown scenario '{args.scenario}'. Valid: {valid}")

    daily = run_scenario(inputs, args.scenario, args.days)
    summary = summarize_scenario(daily)
    ecological_daily = run_ecological_externalities(
        inputs, args.scenario, args.days
    )
    ecological_summary = summarize_ecological_externalities(ecological_daily)
    ecological_mc = run_ecological_monte_carlo(
        inputs,
        args.scenario,
        args.days,
        simulations=args.simulations,
        seed=args.seed,
    )
    mc = run_monte_carlo(
        inputs,
        args.scenario,
        args.days,
        simulations=args.simulations,
        seed=args.seed,
    )
    run_dir = args.output_dir / args.scenario
    catalog = inputs.scenario_catalog.loc[
        inputs.scenario_catalog["scenario"] == args.scenario
    ].iloc[0]
    write_outputs(
        run_dir,
        args.scenario,
        args.days,
        args.simulations,
        args.seed,
        daily,
        summary,
        mc,
        catalog,
        ecological_daily,
        ecological_summary,
        ecological_mc,
    )

    comparison_path = None
    if args.compare_scenarios:
        comparison = build_scenario_comparison(inputs, args.days)
        comparison_path = args.output_dir / "scenario_comparison.csv"
        comparison_path.parent.mkdir(parents=True, exist_ok=True)
        comparison.to_csv(comparison_path, index=False)

    calibration_paths = None
    if args.calibration:
        grid = run_calibration_sensitivity(
            inputs,
            args.scenario,
            args.days,
            levels=args.calibration_levels,
        )
        calibration_summary = summarize_calibration(grid)
        grid_path = run_dir / "calibration_sensitivity.csv"
        calibration_summary_path = run_dir / "calibration_summary.csv"
        grid.to_csv(grid_path, index=False)
        calibration_summary.to_csv(calibration_summary_path, index=False)
        calibration_paths = (grid_path, calibration_summary_path)

    total = summary.loc[summary["commodity"] == "TOTAL"].iloc[0]
    print("=" * 72)
    print("Multi-Commodity Maritime Chokepoint Transmission Model")
    print("=" * 72)
    print(f"Scenario: {args.scenario}")
    print(f"Horizon:  {args.days} days")
    print(f"Gross modeled exposure: ${total['total_impact_usd']/1e9:,.2f} billion")
    print(f"  Immediate:             ${total['immediate_impact_usd']/1e9:,.2f} billion")
    print(f"  Lagged:                ${total['lagged_impact_usd']/1e9:,.2f} billion")
    print(
        "  Probability weighted: "
        f"${total['probability_weighted_impact_usd']/1e9:,.2f} billion "
        f"(prior {total['scenario_probability']:.0%})"
    )
    crude = summary.loc[summary["commodity"] == "Crude oil"].iloc[0]
    print(
        f"Peak modeled Brent proxy: ${crude['peak_implied_price_usd']:,.2f}/b "
        f"(analyst band ${catalog['brent_target_low_usd']:,.0f}-"
        f"${catalog['brent_target_high_usd']:,.0f})"
    )
    print(
        "Static-demand counterfactual peak: "
        f"${crude['peak_static_demand_price_usd']:,.2f}/b; "
        f"maximum demand moderation ${crude['peak_demand_moderation_usd']:,.2f}/b"
    )
    print(
        "No-structural-offset counterfactual peak: "
        f"${crude['peak_no_structural_offsets_price_usd']:,.2f}/b; "
        "maximum structural moderation "
        f"${crude['peak_structural_moderation_usd']:,.2f}/b"
    )
    print(
        "Regional sour-complex proxy peak: "
        f"${crude['peak_regional_sour_price_usd']:,.2f}/b "
        f"(maximum basis ${crude['peak_regional_sour_spread_usd']:,.2f}/b)"
    )
    print(
        "Heavy-sour enabling availability/effective reassignment: "
        f"{crude['minimum_heavy_sour_enabling_availability_pct']:.1%} / "
        f"{crude['peak_effective_reassigned_heavy_sour_share_pct']:.2%}"
    )
    print(
        "Peak true/apparent crude demand reduction: "
        f"{crude['peak_demand_reduction_pct']:.2%} / "
        f"{crude['peak_apparent_benchmark_demand_reduction_pct']:.2%}"
    )
    if not ecological_summary.empty:
        ecological_total = ecological_summary["lagged_impact_usd"].sum()
        print(
            "Conditional ecological externality exposure: "
            f"${ecological_total/1e9:,.2f} billion "
            "(reported separately from commodity total)"
        )
        if not ecological_mc.empty:
            ecological_mc_total = ecological_mc.loc[
                ecological_mc["channel"] == "TOTAL"
            ].iloc[0]
            print(
                "Ecological Monte Carlo P05/P50/P95: "
                f"${ecological_mc_total['p05_lagged_impact_usd']/1e9:,.2f}B / "
                f"${ecological_mc_total['p50_lagged_impact_usd']/1e9:,.2f}B / "
                f"${ecological_mc_total['p95_lagged_impact_usd']/1e9:,.2f}B"
            )
    if not mc.empty:
        mc_total = mc.loc[mc["commodity"] == "TOTAL"].iloc[0]
        print(
            "Monte Carlo total P05/P50/P95: "
            f"${mc_total['p05_total_impact_usd']/1e9:,.2f}B / "
            f"${mc_total['p50_total_impact_usd']/1e9:,.2f}B / "
            f"${mc_total['p95_total_impact_usd']/1e9:,.2f}B"
        )
        crude_mc = mc.loc[mc["commodity"] == "Crude oil"].iloc[0]
        print(
            "Brent target-band coverage (below/within/above): "
            f"{crude_mc['target_band_below_share']:.1%} / "
            f"{crude_mc['target_band_within_share']:.1%} / "
            f"{crude_mc['target_band_above_share']:.1%}"
        )
    if comparison_path is not None:
        print(f"Scenario comparison: {comparison_path.resolve()}")
    if calibration_paths is not None:
        print(f"Calibration grid: {calibration_paths[0].resolve()}")
        print(f"Calibration summary: {calibration_paths[1].resolve()}")
    print(f"Outputs: {run_dir.resolve()}")


if __name__ == "__main__":
    main()
