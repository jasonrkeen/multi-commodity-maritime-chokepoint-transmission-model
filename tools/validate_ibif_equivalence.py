"""Run six source-pinned comparisons; write evidence outside both checkouts."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys

BASE = "6c1cc646fa9486817fe5d8c9f1f6fdd9eadfa451"
SCENARIOS = ("sensor_fused_hormuz", "compound_hormuz_red_sea")
ADDITIONS = {"ibif_assessment.json", "ibif_assessment.csv", "ibif_assessment.md"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(folder):
    return {p.relative_to(folder).as_posix(): digest(p)
            for p in folder.rglob("*") if p.is_file()}


def git(folder, *args):
    return subprocess.check_output(["git", "-C", str(folder), *args], text=True).strip()


def snapshot(folder):
    names = subprocess.check_output(["git", "-C", str(folder), "ls-files", "-z",
                                    "--cached", "--others", "--exclude-standard"]).decode().split("\0")
    return {name: digest(folder / name) for name in sorted(set(names)) if name}


def compare_pdf(a, b, dest):
    from pypdf import PdfReader
    from PIL import Image, ImageChops
    pattern = rb"/CreationDate\s*\(D:[^)]*\)"
    require(re.sub(pattern, b"/CreationDate (IGNORED)", a.read_bytes()) ==
            re.sub(pattern, b"/CreationDate (IGNORED)", b.read_bytes()),
            "PDF differs beyond CreationDate")
    readers = [PdfReader(p) for p in (a, b)]
    require([p.extract_text() for p in readers[0].pages] ==
            [p.extract_text() for p in readers[1].pages], "PDF text differs")
    dest.mkdir(parents=True)
    for label, pdf in (("a", a), ("b", b)):
        subprocess.run([shutil.which("pdftoppm"), "-r", "100", "-png", str(pdf), str(dest / label)],
                       check=True, capture_output=True)
    left, right = sorted(dest.glob("a-*.png")), sorted(dest.glob("b-*.png"))
    require(len(left) == len(right) > 0, "PDF page counts differ")
    for x, y in zip(left, right):
        with Image.open(x) as one, Image.open(y) as two:
            require(one.size == two.size and ImageChops.difference(
                one.convert("RGB"), two.convert("RGB")).getbbox() is None, "PDF pixels differ")
    return {"allowed_difference": "CreationDate only", "identical_rendered_pages": len(left)}


def compare_outputs(baseline, candidate, enabled, render_dir):
    before, after = inventory(baseline), inventory(candidate)
    require(bool(before), "Baseline output is missing or empty")
    required = {"commodity_daily.csv", "scenario_summary.csv", "monte_carlo_summary.csv",
                "model_run_metadata.json", "executive_brief.pdf"}
    require(required <= set(before), "Required baseline outputs missing")
    require(set(after) == set(before) | (ADDITIONS if enabled else set()), "Output inventory differs")
    result = {"byte_identical": [], "exceptions": {}, "hashes": after}
    for name in before:
        a, b = baseline / name, candidate / name
        if before[name] == after[name]:
            result["byte_identical"].append(name)
        elif name == "model_run_metadata.json":
            x, y = json.loads(a.read_text()), json.loads(b.read_text())
            require("generated_at_utc" in x and "generated_at_utc" in y, "Missing timestamp")
            del x["generated_at_utc"], y["generated_at_utc"]
            require(x == y, "Run metadata differs beyond timestamp")
            result["exceptions"][name] = "generated_at_utc only"
        elif name == "executive_brief.pdf":
            result["exceptions"][name] = compare_pdf(a, b, render_dir)
        else:
            raise ValueError("Unexpected output difference: " + name)
    if enabled:
        assessment = json.loads((candidate / "ibif_assessment.json").read_text())
        metadata = json.loads((candidate / "model_run_metadata.json").read_text())
        require(assessment["scenario"] == metadata["scenario"] and
                assessment["horizon_days"] == metadata["horizon_days"], "IBIF run identity differs")
        require(assessment["calibration_status"] == "EXPERIMENTAL_UNCALIBRATED", "Missing limits")
        import pandas as pd
        import numpy as np
        daily = pd.read_csv(candidate / "commodity_daily.csv")
        report = pd.read_csv(candidate / "ibif_assessment.csv")
        records = assessment["commodities"]
        require(len(records) == len(report) == daily.commodity.nunique(), "Commodity counts differ")
        require({r["commodity"] for r in records} == set(report.commodity) == set(daily.commodity), "Commodity coverage differs")
        for row in records:
            require(row["analytic_confidence"] is None and row["escalation_status"] == "UNASSESSED", "Unsupported confidence/escalation")
            require(np.isclose(row["gross_modeled_exposure_usd"], daily.loc[
                daily.commodity == row["commodity"], "total_impact_usd"].sum(), rtol=1e-14, atol=0), "Exposure does not reconcile")
            require(np.isclose(row["business_consequence_score"], report.loc[
                report.commodity == row["commodity"], "business_consequence_score"].iloc[0], rtol=1e-14, atol=0), "CSV score differs")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--days", type=int, default=240)
    parser.add_argument("--simulations", type=int, default=200)
    parser.add_argument("--seed", type=int, default=20260812)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    base, candidate, out = (p.resolve() for p in (args.baseline, args.candidate, args.output_dir))
    require(args.days > 0 and args.simulations >= 0 and 1 <= args.workers <= 6, "Invalid run settings")
    require(base != candidate, "Use separate baseline and candidate checkouts")
    require(not out.exists() and not any(out.is_relative_to(p) or p.is_relative_to(out)
                                        for p in (base, candidate)), "Use a new output directory outside both source trees")
    require(git(base, "rev-parse", "HEAD") == BASE and not git(base, "status", "--porcelain"), "Baseline must be the clean pinned commit")
    require(shutil.which("pdftoppm") is not None, "Install Poppler pdftoppm")
    import pypdf
    import numpy, pandas, matplotlib, PIL
    pins = {"baseline": snapshot(base), "candidate": snapshot(candidate)}
    out.mkdir(parents=True)
    result = {"status": "RUNNING", "base_commit": BASE, "candidate_head": git(candidate, "rev-parse", "HEAD"),
              "candidate_dirty": bool(git(candidate, "status", "--porcelain")),
              "settings": vars(args) | {"baseline": str(base), "candidate": str(candidate), "output_dir": str(out)},
              "environment": {"python": sys.version, "platform": platform.platform(), "numpy": numpy.__version__,
                              "pandas": pandas.__version__, "matplotlib": matplotlib.__version__,
                              "pypdf": pypdf.__version__, "Pillow": PIL.__version__},
              "source_hashes": pins, "runs": [], "comparisons": []}
    result_path = out / "equivalence_results.json"
    def save():
        result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    save()
    try:
        def run(task):
            scenario, mode = task
            repo = base if mode == "untouched" else candidate
            destination = out / mode / scenario
            cmd = [sys.executable, str(repo / "main.py"), "--scenario", scenario,
                   "--days", str(args.days), "--simulations", str(args.simulations),
                   "--seed", str(args.seed), "--output-dir", str(destination)]
            if mode == "enabled": cmd.append("--ibif")
            env = os.environ.copy()
            env["MPLBACKEND"] = "Agg"
            env["MPLCONFIGDIR"] = str(out / ("mpl_" + scenario + mode))
            # Do not let a caller's import override replace the snapshotted model.
            env.pop("PYTHONPATH", None)
            with (out / (scenario + "_" + mode + ".log")).open("w") as log:
                process = subprocess.run(cmd, cwd=repo, env=env, stdout=log, stderr=subprocess.STDOUT)
            return {"scenario": scenario, "mode": mode, "command": cmd, "exit_code": process.returncode}
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            result["runs"] = list(pool.map(run, [(s, m) for s in SCENARIOS for m in ("untouched", "disabled", "enabled")]))
        require(all(r["exit_code"] == 0 for r in result["runs"]), "A model run failed; inspect logs")
        for scenario in SCENARIOS:
            for mode in ("disabled", "enabled"):
                comparison = compare_outputs(out / "untouched" / scenario / scenario,
                    out / mode / scenario / scenario, mode == "enabled", out / "renders" / scenario / mode)
                result["comparisons"].append({"scenario": scenario, "mode": mode, **comparison})
        require(snapshot(base) == pins["baseline"] and snapshot(candidate) == pins["candidate"], "Source changed during execution")
        result["status"] = "PASS"
    except Exception as error:
        result.update(status="FAIL", error=str(error))
        raise
    finally:
        save()
    print(f"PASS: {args.days} days, {args.simulations} simulations, seed {args.seed}. Evidence: {result_path}")


if __name__ == "__main__":
    main()
