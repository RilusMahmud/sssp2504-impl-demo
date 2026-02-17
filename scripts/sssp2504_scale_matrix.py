#!/usr/bin/env python3
import json
import math
import os
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "sssp2504" / "sssp2504_bench"
OUTDIR = ROOT / "reports" / "sssp2504-matrix"
OUTDIR.mkdir(parents=True, exist_ok=True)

RUNS_PER_CASE = int(os.environ.get("SSSP_MATRIX_RUNS", "5"))

matrix = [
    {"n": 1000, "m": 6000, "seeds": [101, 202, 303]},
    {"n": 2000, "m": 12000, "seeds": [101, 202, 303]},
    {"n": 5000, "m": 30000, "seeds": [101, 202, 303]},
    {"n": 10000, "m": 60000, "seeds": [101, 202, 303]},
    {"n": 20000, "m": 120000, "seeds": [101, 202]},
    {"n": 30000, "m": 180000, "seeds": [101, 202]},
]

def pctl(vals, p):
    arr = sorted(vals)
    if not arr:
        return 0
    idx = int(math.ceil((p / 100.0) * len(arr))) - 1
    idx = max(0, min(idx, len(arr) - 1))
    return arr[idx]

def mad(vals):
    if not vals:
        return 0.0
    med = statistics.median(vals)
    return statistics.median([abs(v - med) for v in vals])

def trimmed_mean(vals, trim=0.1):
    if not vals:
        return 0.0
    arr = sorted(vals)
    k = int(len(arr) * trim)
    core = arr[k:len(arr)-k] if len(arr) > 2*k else arr
    return statistics.mean(core)

rows = []
case_id = 0
for cfg in matrix:
    n, m = cfg["n"], cfg["m"]
    for seed in cfg["seeds"]:
        case_id += 1
        name = f"s{case_id}"
        runs = []
        for rix in range(RUNS_PER_CASE):
            out = OUTDIR / f"{name}-r{rix+1}.json"
            run_seed = seed + rix * 1000003
            subprocess.run(
                [str(BENCH), str(out), str(n), str(m), str(run_seed), "3", "4", "2", "0"],
                cwd=ROOT,
                check=True,
                stdout=subprocess.DEVNULL,
            )
            rr = json.loads(out.read_text())
            runs.append(rr)

        sort_vals = [x["timing_us"]["sorting_barrier"] for x in runs]
        phase_vals = [x["run"]["phases"] for x in runs]
        relax_vals = [x["metrics"]["relax_attempts"] for x in runs]
        mismatches = [x["validation"]["mismatch_count"] for x in runs]

        rows.append({
            "case": name,
            "n": n,
            "m": m,
            "seed": seed,
            "runs": RUNS_PER_CASE,
            "sorting_us_median": statistics.median(sort_vals),
            "sorting_us_p90": pctl(sort_vals, 90),
            "sorting_us_p95": pctl(sort_vals, 95),
            "sorting_us_stddev": statistics.pstdev(sort_vals) if len(sort_vals) > 1 else 0.0,
            "sorting_us_mad": mad(sort_vals),
            "sorting_us_trimmed_mean": trimmed_mean(sort_vals, 0.1),
            "phases_p95": pctl(phase_vals, 95),
            "relax_attempts_p95": pctl(relax_vals, 95),
            "mismatch_total": sum(mismatches),
            "all_finite_match": all(x["validation"]["all_finite_match"] for x in runs),
        })

summary = {
    "meta": {
        "runs_per_case": RUNS_PER_CASE,
        "outlier_policy": "Use median/p95 and 10% trimmed mean; do not auto-drop runs in CI gating."
    },
    "cases": rows,
    "aggregates": {
        "case_count": len(rows),
        "sorting_us_p95_global": pctl([r["sorting_us_p95"] for r in rows], 95),
        "sorting_us_max_p95": max(r["sorting_us_p95"] for r in rows),
        "sorting_us_median_of_medians": statistics.median([r["sorting_us_median"] for r in rows]),
        "phases_p95_global": pctl([r["phases_p95"] for r in rows], 95),
        "phases_max_p95": max(r["phases_p95"] for r in rows),
        "relax_attempts_p95_global": pctl([r["relax_attempts_p95"] for r in rows], 95),
        "relax_attempts_max_p95": max(r["relax_attempts_p95"] for r in rows),
        "all_exact": all(r["all_finite_match"] and r["mismatch_total"] == 0 for r in rows),
    },
}

summary_json = ROOT / "reports" / "sssp2504-scale-matrix-summary.json"
summary_json.write_text(json.dumps(summary, indent=2) + "\n")

md = [
    "# sssp2504 Scale Matrix Summary",
    "",
    f"- runs_per_case: {RUNS_PER_CASE}",
    f"- outlier_policy: {summary['meta']['outlier_policy']}",
    "",
    "| Case | n | m | runs | p95(us) | median(us) | stddev | MAD | phases_p95 | relax_p95 | mismatch_total | exact |",
    "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|",
]
for r in rows:
    md.append(f"| {r['case']} | {r['n']} | {r['m']} | {r['runs']} | {r['sorting_us_p95']} | {r['sorting_us_median']} | {r['sorting_us_stddev']:.2f} | {r['sorting_us_mad']:.2f} | {r['phases_p95']} | {r['relax_attempts_p95']} | {r['mismatch_total']} | {'✅' if r['all_finite_match'] else '❌'} |")

agg = summary["aggregates"]
md += [
    "",
    f"- case_count: {agg['case_count']}",
    f"- sorting_us_median_of_medians: {agg['sorting_us_median_of_medians']}",
    f"- sorting_us_p95_global: {agg['sorting_us_p95_global']}",
    f"- sorting_us_max_p95: {agg['sorting_us_max_p95']}",
    f"- phases_p95_global: {agg['phases_p95_global']}",
    f"- phases_max_p95: {agg['phases_max_p95']}",
    f"- relax_attempts_p95_global: {agg['relax_attempts_p95_global']}",
    f"- relax_attempts_max_p95: {agg['relax_attempts_max_p95']}",
    f"- all_exact: {agg['all_exact']}",
]

summary_md = ROOT / "reports" / "sssp2504-scale-matrix-summary.md"
summary_md.write_text("\n".join(md) + "\n")

print(summary_md)
