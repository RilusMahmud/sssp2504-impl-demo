#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
config_path = ROOT / "reports" / "governance-repos.json"
out_json = ROOT / "reports" / "governance-rollup.json"
out_md = ROOT / "reports" / "governance-rollup.md"
out_weekly = ROOT / "reports" / "governance-weekly-summary.md"

if config_path.exists():
    cfg = json.loads(config_path.read_text())
    repos = cfg.get("repos", [])
else:
    repos = [{"name": "sssp2504", "path": str(ROOT)}]

items = []
for r in repos:
    name = r.get("name") or Path(r["path"]).name
    base = Path(r["path"])

    thr_file = base / "reports" / "sssp2504-ci-threshold-check.md"
    drift_file = base / "reports" / "sssp2504-drift-alerts.json"
    bench_file = base / "reports" / "sssp2504-benchmark-report.json"

    threshold_status = "UNKNOWN"
    if thr_file.exists():
        txt = thr_file.read_text()
        if "status: **PASS**" in txt:
            threshold_status = "PASS"
        elif "status: **FAIL**" in txt:
            threshold_status = "FAIL"

    drift7 = "UNKNOWN"
    drift30 = "UNKNOWN"
    if drift_file.exists():
        d = json.loads(drift_file.read_text())
        drift7 = d.get("status7", "UNKNOWN")
        drift30 = d.get("status30", "UNKNOWN")

    exact = None
    sort_us = None
    if bench_file.exists():
        b = json.loads(bench_file.read_text())
        exact = b.get("validation", {}).get("all_finite_match")
        sort_us = b.get("timing_us", {}).get("sorting_barrier")

    risk = 0
    if threshold_status == "FAIL": risk += 50
    if drift7 == "ERROR" or drift30 == "ERROR": risk += 30
    elif drift7 == "WARN" or drift30 == "WARN": risk += 15
    if exact is False: risk += 40

    items.append({
        "repo": name,
        "path": str(base),
        "threshold_status": threshold_status,
        "drift7": drift7,
        "drift30": drift30,
        "exact": exact,
        "sorting_us": sort_us,
        "risk_score": risk,
    })

items.sort(key=lambda x: x["risk_score"], reverse=True)

rollup = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "repoCount": len(items),
    "repos": items,
}
out_json.write_text(json.dumps(rollup, indent=2) + "\n")

md = [
    "# Governance Rollup",
    "",
    f"Generated: {rollup['generatedAt']}",
    "",
    "| Repo | Threshold | Drift7 | Drift30 | Exact | sorting_us | Risk |",
    "|---|:---:|:---:|:---:|:---:|---:|---:|",
]
for i in items:
    ex = "✅" if i["exact"] is True else ("❌" if i["exact"] is False else "?")
    md.append(f"| {i['repo']} | {i['threshold_status']} | {i['drift7']} | {i['drift30']} | {ex} | {i['sorting_us'] or '-'} | {i['risk_score']} |")

md += ["", "## Attention order"]
for i in items:
    md.append(f"- {i['repo']}: risk={i['risk_score']} ({i['threshold_status']}, drift7={i['drift7']}, drift30={i['drift30']})")

out_md.write_text("\n".join(md) + "\n")

weekly = [
    "# Weekly Governance Summary",
    "",
    "## Snapshot",
    f"- repos monitored: {len(items)}",
    f"- highest risk repo: {items[0]['repo'] if items else 'n/a'}",
    "",
    "## Regressions",
    "- (fill from rollup deltas)",
    "",
    "## Improvements",
    "- (fill from rollup deltas)",
    "",
    "## Actions",
    "- (top 3 risk-reduction tasks)",
]
out_weekly.write_text("\n".join(weekly) + "\n")

print(out_md)
print(out_json)
print(out_weekly)
