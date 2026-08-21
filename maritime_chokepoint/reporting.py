from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

from . import __version__


COLORS = {
    "Crude oil": "#173B57",
    "LNG": "#00A6A6",
    "Fertilizer": "#D99A2B",
    "Helium": "#8B5CF6",
}


def _money(value: float) -> str:
    if abs(value) >= 1e12:
        return f"${value/1e12:,.2f}T"
    if abs(value) >= 1e9:
        return f"${value/1e9:,.2f}B"
    return f"${value/1e6:,.1f}M"


def _target_check(
    summary: pd.DataFrame, catalog: pd.Series, mc: pd.DataFrame
) -> pd.DataFrame:
    crude = summary.loc[summary["commodity"] == "Crude oil"].iloc[0]
    modeled = float(crude["peak_implied_price_usd"])
    low = float(catalog["brent_target_low_usd"])
    high = float(catalog["brent_target_high_usd"])
    if modeled < low:
        status = "below_target_band"
        gap = modeled - low
    elif modeled > high:
        status = "above_target_band"
        gap = modeled - high
    else:
        status = "within_target_band"
        gap = 0.0
    coverage = None
    if not mc.empty:
        crude_mc = mc.loc[mc["commodity"] == "Crude oil"]
        if not crude_mc.empty:
            coverage = crude_mc.iloc[0]
    return pd.DataFrame(
        [
            {
                "scenario": catalog["scenario"],
                "scenario_probability": catalog["scenario_probability"],
                "modeled_peak_brent_usd": modeled,
                "analyst_target_low_usd": low,
                "analyst_target_high_usd": high,
                "target_check_status": status,
                "distance_to_band_usd": gap,
                "monte_carlo_simulations": (
                    int(coverage["simulations"]) if coverage is not None else 0
                ),
                "mc_below_band_share": (
                    float(coverage["target_band_below_share"])
                    if coverage is not None
                    else np.nan
                ),
                "mc_within_band_share": (
                    float(coverage["target_band_within_share"])
                    if coverage is not None
                    else np.nan
                ),
                "mc_above_band_share": (
                    float(coverage["target_band_above_share"])
                    if coverage is not None
                    else np.nan
                ),
                "governance_note": (
                    "Target band is a validation comparator and does not drive pricing."
                ),
            }
        ]
    )


def _plot_timeline(daily: pd.DataFrame, path: Path) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    for commodity, group in daily.groupby("commodity", sort=False):
        color = COLORS.get(commodity)
        axes[0].plot(
            group["day"], group["price_shock_pct"] * 100, label=commodity, color=color
        )
        axes[1].plot(group["day"], group["supply_loss_pct"] * 100, color=color)
        axes[1].plot(
            group["day"],
            group["demand_reduction_pct"] * 100,
            color=color,
            linestyle="--",
            alpha=0.85,
        )
        axes[2].plot(
            group["day"], group["lagged_impact_usd"] / 1e6, color=color
        )
    axes[0].set_ylabel("Price shock (%)")
    axes[1].set_ylabel("Supply / demand (%)")
    axes[2].set_ylabel("Lagged impact ($M/day)")
    axes[2].set_xlabel("Day")
    axes[0].legend(ncol=4, frameon=False)
    axes[1].text(
        0.99,
        0.90,
        "solid: supply loss | dashed: demand reduction",
        transform=axes[1].transAxes,
        ha="right",
        fontsize=8,
        color="#555555",
    )
    for ax in axes:
        ax.grid(alpha=0.2)
    fig.suptitle(
        "Immediate repricing, dynamic demand, and lagged transmission",
        fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _plot_impact(summary: pd.DataFrame, path: Path) -> None:
    plot = summary.loc[summary["commodity"] != "TOTAL"].copy()
    x = np.arange(len(plot))
    fig, ax = plt.subplots(figsize=(10, 5.8))
    ax.bar(
        x,
        plot["immediate_impact_usd"] / 1e9,
        label="Immediate",
        color="#2878B5",
    )
    ax.bar(
        x,
        plot["lagged_impact_usd"] / 1e9,
        bottom=plot["immediate_impact_usd"] / 1e9,
        label="Lagged",
        color="#F5A742",
    )
    ax.set_xticks(x, plot["commodity"])
    ax.set_ylabel("Cumulative gross exposure ($B)")
    ax.set_title("Impact composition by commodity", fontweight="bold")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.2)
    totals = plot["total_impact_usd"] / 1e9
    offset = max(float(totals.max()) * 0.015, 0.5)
    for xpos, value in zip(x, totals):
        ax.text(
            xpos,
            value + offset,
            f"${value:,.1f}B",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )
    ax.set_ylim(0, float(totals.max()) * 1.12)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _plot_demand_balance(daily: pd.DataFrame, path: Path) -> None:
    crude = daily.loc[daily["commodity"] == "Crude oil"].copy()
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(
        crude["day"],
        crude["supply_loss_pct"] * 100,
        label="Physical supply loss",
        color="#C94C4C",
        linewidth=2,
    )
    ax.plot(
        crude["day"],
        crude["demand_reduction_pct"] * 100,
        label="Dynamic demand reduction",
        color="#2C8C6B",
        linewidth=2,
    )
    ax.plot(
        crude["day"],
        crude["net_market_gap_pct"] * 100,
        label="Residual market gap",
        color="#173B57",
        linewidth=2,
    )
    ax.set_xlabel("Day")
    ax.set_ylabel("Share of baseline market (%)")
    ax.set_title("Crude oil balance: supply shock versus demand response", fontweight="bold")
    ax.grid(alpha=0.2)
    price_ax = ax.twinx()
    price_ax.plot(
        crude["day"],
        crude["implied_price_usd"],
        label="Dynamic-demand price",
        color="#6D4C9F",
        linewidth=1.5,
        alpha=0.85,
    )
    price_ax.plot(
        crude["day"],
        crude["static_demand_implied_price_usd"],
        label="Static-demand counterfactual",
        color="#777777",
        linewidth=1.5,
        linestyle=":",
    )
    price_ax.set_ylabel("Modeled crude price ($/b)")
    lines, labels = ax.get_legend_handles_labels()
    price_lines, price_labels = price_ax.get_legend_handles_labels()
    ax.legend(lines + price_lines, labels + price_labels, frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _plot_sensor_fusion(daily: pd.DataFrame, path: Path) -> bool:
    sensor = daily.loc[
        (daily["commodity"] == "Crude oil")
        & daily["ais_declared_transit_index"].notna()
    ].copy()
    if sensor.empty:
        return False
    fig, axes = plt.subplots(2, 1, figsize=(10, 6.5), sharex=True)
    axes[0].plot(
        sensor["day"],
        sensor["ais_declared_transit_index"],
        label="AIS-declared transit",
        color="#2878B5",
    )
    axes[0].plot(
        sensor["day"],
        sensor["sar_detected_transit_index"],
        label="SAR-detected transit",
        color="#D06B2C",
    )
    axes[0].fill_between(
        sensor["day"],
        sensor["ais_declared_transit_index"],
        sensor["sar_detected_transit_index"],
        where=(
            sensor["sar_detected_transit_index"]
            >= sensor["ais_declared_transit_index"]
        ),
        color="#8B5CF6",
        alpha=0.18,
        label="Undeclared-activity discrepancy",
    )
    axes[0].plot(
        sensor["day"],
        sensor["weighted_undeclared_activity_index"],
        color="#6D4C9F",
        linestyle="--",
        linewidth=1.5,
        label="Confidence-weighted undeclared activity",
    )
    axes[1].plot(
        sensor["day"],
        sensor["market_risk_premium_pct"] * 100,
        color="#8B5CF6",
        label="Total risk premium",
    )
    axes[1].plot(
        sensor["day"],
        sensor["dependency_induced_severity"] * 100,
        color="#D99A2B",
        label="Dependency-induced severity",
    )
    axes[1].plot(
        sensor["day"],
        sensor["sensor_confidence"] * 100,
        color="#2C8C6B",
        linestyle="--",
        label="Detection confidence",
    )
    axes[0].set_ylabel("Transit index")
    axes[1].set_ylabel("Percent")
    axes[1].set_xlabel("Day")
    axes[0].legend(frameon=False, ncol=2)
    axes[1].legend(frameon=False, ncol=3)
    for ax in axes:
        ax.grid(alpha=0.2)
    fig.suptitle("Illustrative AIS-SAR fusion and opacity signal", fontweight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return True


def _plot_market_balance(daily: pd.DataFrame, path: Path) -> None:
    crude = daily.loc[daily["commodity"] == "Crude oil"].copy()
    fig, axes = plt.subplots(2, 1, figsize=(10.5, 7.5), sharex=True)

    axes[0].plot(
        crude["day"],
        crude["supply_loss_pct"] * 100,
        color="#173B57",
        linewidth=2,
        label="Gross route loss",
    )
    axes[0].stackplot(
        crude["day"],
        crude["bypass_supply_offset_pct"] * 100,
        crude["strategic_release_offset_pct"] * 100,
        crude["external_supply_response_pct"] * 100,
        labels=["Pipeline bypass", "Emergency stocks", "External supply"],
        colors=["#2878B5", "#D99A2B", "#2C8C6B"],
        alpha=0.55,
    )
    axes[0].plot(
        crude["day"],
        crude["balanced_supply_loss_pct"] * 100,
        color="#C94C4C",
        linewidth=2,
        label="Loss after structural offsets",
    )
    axes[0].set_ylabel("Baseline market share (%)")
    axes[0].set_title("Structural supply offsets", fontweight="bold")
    axes[0].legend(frameon=False, ncol=3, fontsize=8)

    axes[1].stackplot(
        crude["day"],
        crude["physical_gap_price_contribution_pct"] * 100,
        crude["base_risk_price_contribution_pct"] * 100,
        crude["opacity_price_contribution_pct"] * 100,
        labels=["Residual physical gap", "Scenario risk premium", "Opacity premium"],
        colors=["#C94C4C", "#8B5CF6", "#D99A2B"],
        alpha=0.65,
    )
    axes[1].set_ylabel("Contribution to price shock (%)")
    axes[1].set_xlabel("Day")
    axes[1].set_title("Brent shock decomposition", fontweight="bold")
    price_ax = axes[1].twinx()
    price_ax.plot(
        crude["day"],
        crude["implied_price_usd"],
        color="#173B57",
        linewidth=1.8,
        label="Modeled Brent proxy",
    )
    price_ax.plot(
        crude["day"],
        crude["no_structural_offsets_implied_price_usd"],
        color="#555555",
        linestyle=":",
        linewidth=1.5,
        label="Without structural offsets",
    )
    price_ax.set_ylabel("Modeled crude price ($/b)")
    lines, labels = axes[1].get_legend_handles_labels()
    price_lines, price_labels = price_ax.get_legend_handles_labels()
    axes[1].legend(
        lines + price_lines,
        labels + price_labels,
        frameon=False,
        ncol=3,
        fontsize=8,
        loc="upper right",
    )
    for ax in axes:
        ax.grid(alpha=0.2)
    fig.suptitle(
        "Crude market balancing and price attribution",
        fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _plot_crude_segmentation(daily: pd.DataFrame, path: Path) -> None:
    crude = daily.loc[daily["commodity"] == "Crude oil"].copy()
    fig, axes = plt.subplots(2, 1, figsize=(10.5, 7.2), sharex=True)
    axes[0].plot(
        crude["day"],
        crude["implied_price_usd"],
        label="Global Brent proxy",
        color="#173B57",
        linewidth=2,
    )
    axes[0].plot(
        crude["day"],
        crude["regional_sour_price_usd"],
        label="Regional sour-complex proxy",
        color="#C94C4C",
        linewidth=2,
    )
    axes[0].fill_between(
        crude["day"],
        crude["implied_price_usd"],
        crude["regional_sour_price_usd"],
        color="#D99A2B",
        alpha=0.20,
        label="Modeled grade/logistics basis",
    )
    axes[0].set_ylabel("Modeled crude price ($/b)")
    axes[0].set_title("Crude benchmark segmentation", fontweight="bold")
    axes[0].legend(frameon=False, ncol=3)

    axes[1].plot(
        crude["day"],
        crude["demand_reduction_pct"] * 100,
        label="True consumption response",
        color="#2C8C6B",
        linewidth=2,
    )
    axes[1].plot(
        crude["day"],
        crude["apparent_benchmark_demand_reduction_pct"] * 100,
        label="Apparent benchmark withdrawal",
        color="#8B5CF6",
        linewidth=2,
        linestyle="--",
    )
    axes[1].fill_between(
        crude["day"],
        crude["demand_reduction_pct"] * 100,
        crude["apparent_benchmark_demand_reduction_pct"] * 100,
        color="#8B5CF6",
        alpha=0.14,
        label="Segmented-channel shift",
    )
    axes[1].set_ylabel("Share of baseline demand (%)")
    axes[1].set_xlabel("Day")
    axes[1].set_title("Consumption response versus market-channel shift", fontweight="bold")
    axes[1].legend(frameon=False, ncol=3)
    for ax in axes:
        ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _plot_ecological_externalities(daily: pd.DataFrame, path: Path) -> bool:
    if daily.empty:
        return False
    fig, axes = plt.subplots(2, 1, figsize=(10.5, 7.2), sharex=True)
    for channel, group in daily.groupby("channel", sort=False):
        axes[0].plot(
            group["day"], group["impact_state_pct"] * 100, label=channel
        )
        axes[1].plot(
            group["day"], group["lagged_impact_usd"] / 1e6, label=channel
        )
    axes[0].set_ylabel("Impact state (%)")
    axes[0].set_title("Conditional ecological transmission states", fontweight="bold")
    axes[1].set_ylabel("Gross exposure ($M/day)")
    axes[1].set_xlabel("Day")
    axes[1].set_title("Confidence-weighted economic exposure", fontweight="bold")
    axes[0].legend(frameon=False, ncol=2)
    for ax in axes:
        ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return True


def _pdf_report(
    path: Path,
    scenario: str,
    days: int,
    simulations: int,
    daily: pd.DataFrame,
    summary: pd.DataFrame,
    mc: pd.DataFrame,
    target_check: pd.DataFrame,
    timeline_path: Path,
    impact_path: Path,
    demand_path: Path,
    balance_path: Path,
    sensor_path: Path,
    has_sensor_chart: bool,
    segmentation_path: Path,
    ecological_path: Path,
    ecological_summary: pd.DataFrame,
    ecological_mc: pd.DataFrame,
    has_ecological_chart: bool,
) -> None:
    with PdfPages(path) as pdf:
        fig = plt.figure(figsize=(8.5, 11))
        fig.patch.set_facecolor("white")
        fig.text(0.08, 0.94, "MARITIME CHOKEPOINT TRANSMISSION", fontsize=10, color="#51758A")
        fig.text(0.08, 0.90, "Executive Brief", fontsize=26, fontweight="bold", color="#173B57")
        fig.text(0.08, 0.865, scenario.replace("_", " ").title(), fontsize=14, color="#333333")
        total = summary.loc[summary["commodity"] == "TOTAL"].iloc[0]
        fig.text(0.08, 0.81, _money(total["total_impact_usd"]), fontsize=28, fontweight="bold", color="#D06B2C")
        fig.text(0.08, 0.785, f"modeled gross exposure over {days} days", fontsize=10, color="#555555")
        fig.text(0.08, 0.74, "CHANNEL AND PROBABILITY VIEW", fontsize=10, fontweight="bold", color="#51758A")
        fig.text(0.08, 0.705, f"Immediate  {_money(total['immediate_impact_usd'])}", fontsize=12)
        fig.text(0.37, 0.705, f"Lagged  {_money(total['lagged_impact_usd'])}", fontsize=12)
        fig.text(
            0.65,
            0.705,
            f"Weighted  {_money(total['probability_weighted_impact_usd'])}",
            fontsize=12,
        )
        if not mc.empty:
            row = mc.loc[mc["commodity"] == "TOTAL"].iloc[0]
            fig.text(0.08, 0.655, "MONTE CARLO RANGE", fontsize=10, fontweight="bold", color="#51758A")
            fig.text(
                0.08,
                0.62,
                f"P05 {_money(row['p05_total_impact_usd'])}   |   "
                f"P50 {_money(row['p50_total_impact_usd'])}   |   "
                f"P95 {_money(row['p95_total_impact_usd'])}",
                fontsize=12,
            )
        image = plt.imread(impact_path)
        ax = fig.add_axes([0.08, 0.21, 0.84, 0.35])
        ax.imshow(image)
        ax.axis("off")
        fig.text(
            0.08,
            0.145,
            "Interpretation: gross exposure combines market repricing, logistics cost, and delayed downstream\n"
            "transmission. The probability-weighted figure uses the editable scenario prior. Neither is net GDP loss.",
            fontsize=9,
            color="#555555",
        )
        fig.text(0.08, 0.07, f"Model v{__version__} | {simulations:,} Monte Carlo draws", fontsize=8, color="#777777")
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        fig = plt.figure(figsize=(8.5, 11))
        fig.text(0.08, 0.94, "CRUDE MARKET SEGMENTATION", fontsize=18, fontweight="bold", color="#173B57")
        image = plt.imread(segmentation_path)
        ax = fig.add_axes([0.05, 0.34, 0.90, 0.53])
        ax.imshow(image)
        ax.axis("off")
        crude = summary.loc[summary["commodity"] == "Crude oil"].iloc[0]
        fig.text(
            0.08,
            0.275,
            f"Peak Brent proxy ${crude['peak_implied_price_usd']:,.0f}/b | "
            f"peak sour proxy ${crude['peak_regional_sour_price_usd']:,.0f}/b | "
            f"maximum basis ${crude['peak_regional_sour_spread_usd']:,.0f}/b",
            fontsize=10,
        )
        fig.text(
            0.08,
            0.235,
            "Minimum upstream-grid-terminal availability "
            f"{crude['minimum_heavy_sour_enabling_availability_pct']:.0%} | "
            "effective reassigned heavy-sour share "
            f"{crude['peak_effective_reassigned_heavy_sour_share_pct']:.2%}",
            fontsize=9.2,
        )
        fig.text(
            0.08,
            0.145,
            "The regional basis isolates grade compatibility and route friction. Reassigned heavy-sour barrels\n"
            "are usable only when upstream, grid, and terminal layers function; they are not new global supply. "
            "Segmented discounted channels\n"
            "reduce the price shock experienced by participating buyers without being labeled demand destruction.",
            fontsize=9.2,
            color="#555555",
            linespacing=1.5,
        )
        fig.text(
            0.08,
            0.045,
            "Governance: parameters are illustrative analyst assumptions. The Brent and sour paths are separate\n"
            "proxies, not observed benchmark forecasts, and require public grade-flow calibration before operational use.",
            fontsize=9,
            color="#555555",
            linespacing=1.4,
        )
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        if has_ecological_chart:
            fig = plt.figure(figsize=(8.5, 11))
            fig.text(0.08, 0.94, "CONDITIONAL ECOLOGICAL EXTERNALITIES", fontsize=18, fontweight="bold", color="#173B57")
            image = plt.imread(ecological_path)
            ax = fig.add_axes([0.05, 0.34, 0.90, 0.53])
            ax.imshow(image)
            ax.axis("off")
            total = ecological_summary["lagged_impact_usd"].sum()
            fig.text(
                0.08,
                0.275,
                f"Separate confidence-weighted exposure over the horizon: {_money(total)}",
                fontsize=11,
                fontweight="bold",
            )
            if not ecological_mc.empty:
                mc_total = ecological_mc.loc[
                    ecological_mc["channel"] == "TOTAL"
                ].iloc[0]
                fig.text(
                    0.08,
                    0.245,
                    f"Monte Carlo P05 {_money(mc_total['p05_lagged_impact_usd'])} | "
                    f"P50 {_money(mc_total['p50_lagged_impact_usd'])} | "
                    f"P95 {_money(mc_total['p95_lagged_impact_usd'])}",
                    fontsize=9.5,
                )
            fig.text(
                0.08,
                0.18,
                "This branch activates only when ecological incident severity is explicitly assumed. It is not inferred\n"
                "from vessel disruption alone and is excluded from the core commodity total. The channels represent\n"
                "desalination continuity, fisheries/coastal livelihoods, and long-duration remediation spending.",
                fontsize=9.2,
                color="#555555",
                linespacing=1.5,
            )
            fig.text(
                0.08,
                0.085,
                "Governance: annual values, incident severities, timing, and confidence are low-confidence analyst\n"
                "assumptions intended for sensitivity analysis, not estimates of an observed environmental event.",
                fontsize=9,
                color="#555555",
                linespacing=1.4,
            )
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

        fig = plt.figure(figsize=(8.5, 11))
        fig.text(0.08, 0.94, "TRANSMISSION TIMELINE", fontsize=18, fontweight="bold", color="#173B57")
        image = plt.imread(timeline_path)
        ax = fig.add_axes([0.05, 0.35, 0.90, 0.52])
        ax.imshow(image)
        ax.axis("off")
        fig.text(0.08, 0.28, "WHAT CHANGED IN V0.5", fontsize=10, fontweight="bold", color="#51758A")
        fig.text(
            0.08,
            0.14,
            "- Brent and the regional sour complex now have separate price paths.\n"
            "- Benchmark withdrawal is separated from true consumption reduction.\n"
            "- Reassigned sour barrels reduce a regional gap but never add global supply.\n"
            "- Sensor opacity is weighted by recall, identity, AIS staleness, and backtest status.\n"
            "- Conditional ecological costs run on separate, longer clocks outside commodity totals.",
            fontsize=9.5,
            linespacing=1.6,
        )
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        fig = plt.figure(figsize=(8.5, 11))
        fig.text(
            0.08,
            0.94,
            "STRUCTURAL MARKET BALANCING",
            fontsize=18,
            fontweight="bold",
            color="#173B57",
        )
        balance_image = plt.imread(balance_path)
        ax = fig.add_axes([0.05, 0.31, 0.90, 0.55])
        ax.imshow(balance_image)
        ax.axis("off")
        crude = summary.loc[summary["commodity"] == "Crude oil"].iloc[0]
        fig.text(
            0.08,
            0.245,
            "BALANCE ATTRIBUTION",
            fontsize=10,
            fontweight="bold",
            color="#51758A",
        )
        fig.text(
            0.08,
            0.195,
            f"Peak gross route loss {crude['peak_supply_loss_pct']:.1%} | "
            f"peak structural offset {crude['peak_structural_supply_offset_pct']:.1%} | "
            f"peak residual gap {crude['peak_net_market_gap_pct']:.1%}",
            fontsize=10,
        )
        fig.text(
            0.08,
            0.155,
            rf"Peak modeled Brent ${crude['peak_implied_price_usd']:,.0f}/b | "
            rf"without structural offsets ${crude['peak_no_structural_offsets_price_usd']:,.0f}/b | "
            rf"maximum daily structural moderation ${crude['peak_structural_moderation_usd']:,.0f}/b",
            fontsize=9.5,
        )
        fig.text(
            0.08,
            0.075,
            "Governance: bypass and emergency-release values are source-anchored where possible; timing,\n"
            "accessibility, and non-regional supply response remain editable analyst assumptions. Price\n"
            "contributions are proportionally scaled only when a commodity price-shock cap binds.",
            fontsize=9,
            color="#555555",
            linespacing=1.4,
        )
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        fig = plt.figure(figsize=(8.5, 11))
        fig.text(0.08, 0.94, "DEMAND AND SIGNAL DIAGNOSTICS", fontsize=18, fontweight="bold", color="#173B57")
        demand_image = plt.imread(demand_path)
        ax = fig.add_axes([0.06, 0.49, 0.88, 0.36])
        ax.imshow(demand_image)
        ax.axis("off")
        check = target_check.iloc[0]
        fig.text(0.08, 0.43, "BRENT VALIDATION COMPARATOR", fontsize=10, fontweight="bold", color="#51758A")
        fig.text(
            0.08,
            0.39,
            rf"Modeled peak \${check['modeled_peak_brent_usd']:,.0f}/b | "
            rf"Analyst band \${check['analyst_target_low_usd']:,.0f}-\${check['analyst_target_high_usd']:,.0f}/b | "
            f"{str(check['target_check_status']).replace('_', ' ')}",
            fontsize=10,
        )
        if int(check["monte_carlo_simulations"]) > 0:
            fig.text(
                0.08,
                0.365,
                f"Monte Carlo band coverage: below {check['mc_below_band_share']:.0%} | "
                f"within {check['mc_within_band_share']:.0%} | "
                f"above {check['mc_above_band_share']:.0%}",
                fontsize=9.5,
                color="#555555",
            )
        crude = summary.loc[summary["commodity"] == "Crude oil"].iloc[0]
        fig.text(
            0.08,
            0.335,
            rf"Static-demand counterfactual peak \${crude['peak_static_demand_price_usd']:,.0f}/b; "
            f"dynamic demand moderates the daily path by as much as "
            rf"\${crude['peak_demand_moderation_usd']:,.0f}/b.",
            fontsize=9.5,
            color="#555555",
        )
        if has_sensor_chart:
            sensor_image = plt.imread(sensor_path)
            ax = fig.add_axes([0.08, 0.045, 0.84, 0.255])
            ax.imshow(sensor_image)
            ax.axis("off")
        else:
            fig.text(
                0.08,
                0.25,
                "Sensor fusion is inactive in this scenario. Run sensor_fused_hormuz to demonstrate how\n"
                "SAR-corrected passage, AIS selection bias, ballast movement, thermal anomalies, and radar\n"
                "wake confidence update the physical path and opacity premium together.",
                fontsize=10,
                color="#555555",
                linespacing=1.5,
            )
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)


def write_outputs(
    run_dir: Path,
    scenario: str,
    days: int,
    simulations: int,
    seed: int,
    daily: pd.DataFrame,
    summary: pd.DataFrame,
    mc: pd.DataFrame,
    catalog: pd.Series,
    ecological_daily: pd.DataFrame,
    ecological_summary: pd.DataFrame,
    ecological_mc: pd.DataFrame,
) -> None:
    charts = run_dir / "charts"
    charts.mkdir(parents=True, exist_ok=True)
    daily.to_csv(run_dir / "commodity_daily.csv", index=False)
    summary.to_csv(run_dir / "scenario_summary.csv", index=False)
    mc.to_csv(run_dir / "monte_carlo_summary.csv", index=False)
    target_check = _target_check(summary, catalog, mc)
    target_check.to_csv(run_dir / "scenario_target_check.csv", index=False)
    ecological_daily.to_csv(
        run_dir / "ecological_externalities_daily.csv", index=False
    )
    ecological_summary.to_csv(
        run_dir / "ecological_externalities_summary.csv", index=False
    )
    ecological_mc.to_csv(
        run_dir / "ecological_monte_carlo_summary.csv", index=False
    )

    timeline = charts / "transmission_timeline.png"
    impact = charts / "impact_by_commodity.png"
    demand = charts / "demand_balance.png"
    balance = charts / "market_balance_decomposition.png"
    sensor = charts / "sensor_fusion.png"
    segmentation = charts / "crude_market_segmentation.png"
    ecological = charts / "ecological_externalities.png"
    _plot_timeline(daily, timeline)
    _plot_impact(summary, impact)
    _plot_demand_balance(daily, demand)
    _plot_market_balance(daily, balance)
    has_sensor_chart = _plot_sensor_fusion(daily, sensor)
    _plot_crude_segmentation(daily, segmentation)
    has_ecological_chart = _plot_ecological_externalities(
        ecological_daily, ecological
    )
    _pdf_report(
        run_dir / "executive_brief.pdf",
        scenario,
        days,
        simulations,
        daily,
        summary,
        mc,
        target_check,
        timeline,
        impact,
        demand,
        balance,
        sensor,
        has_sensor_chart,
        segmentation,
        ecological,
        ecological_summary,
        ecological_mc,
        has_ecological_chart,
    )

    metadata = {
        "model_version": __version__,
        "scenario": scenario,
        "scenario_probability": float(catalog["scenario_probability"]),
        "horizon_days": days,
        "monte_carlo_simulations": simulations,
        "seed": seed,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "sensor_fusion_active": bool(catalog["use_sensor_fusion"]),
        "interpretation": "Gross modeled exposure; not net GDP loss.",
    }
    (run_dir / "model_run_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
