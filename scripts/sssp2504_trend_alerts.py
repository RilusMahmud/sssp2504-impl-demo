#!/usr/bin/env python3
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
history_path = ROOT / "reports" / "sssp2504-scale-matrix-history.jsonl"
out_json = ROOT / "reports" / "sssp2504-drift-alerts.json"
out_md = ROOT / "reports" / "sssp2504-drift-alerts.md"
out_pr = ROOT / "reports" / "sssp2504-governance-pr-comment.md"

rows = []
for line in history_path.read_text().splitlines() if history_path.exists() else []:
    if line.strip():
        r = json.loads(line)
        r.setdefault("sorting_us_p95_global", r.get("sorting_us_p95", 0))
        r.setdefault("phases_p95_global", r.get("phases_p95", 0))
        r.setdefault("relax_attempts_p95_global", r.get("relax_attempts_p95", 0))
        r.setdefault("bucket", "unknown")
        rows.append(r)


def pct(a, b):
    return 0.0 if a == 0 else ((b - a) / a) * 100.0


def window_stats(n):
    w = rows[-n:] if rows else []
    if not w:
        return {"count": 0}
    first, last = w[0], w[-1]
    return {
        "count": len(w),
        "sorting_us_p95_drift_pct": pct(first["sorting_us_p95_global"], last["sorting_us_p95_global"]),
        "phases_p95_drift_pct": pct(first["phases_p95_global"], last["phases_p95_global"]),
        "relax_p95_drift_pct": pct(first["relax_attempts_p95_global"], last["relax_attempts_p95_global"]),
        "all_exact": all(x.get("all_exact") for x in w),
    }


def classify(w):
    if w.get("count", 0) < 2:
        return "INSUFFICIENT"
    if not w.get("all_exact", True):
        return "ERROR"
    worst = max(w.get("sorting_us_p95_drift_pct", 0), w.get("relax_p95_drift_pct", 0), w.get("phases_p95_drift_pct", 0))
    if worst > 15:
        return "ERROR"
    if worst > 5:
        return "WARN"
    return "OK"


def seasonal_hint(rows):
    if len(rows) < 3:
        return "Insufficient history for seasonality hint."
    cur = rows[-1]
    bucket = cur.get("bucket", "unknown")
    peers = [r for r in rows[:-1] if r.get("bucket") == bucket]
    if len(peers) < 2:
        return f"Limited same-bucket history ({bucket}); treat drift cautiously."
    baseline = statistics.median([r["sorting_us_p95_global"] for r in peers])
    curv = cur["sorting_us_p95_global"]
    d = pct(baseline, curv)
    if d > 10:
        return f"Current bucket ({bucket}) is above its seasonal baseline by {d:+.2f}% (possible runner-load or contention spike)."
    if d < -10:
        return f"Current bucket ({bucket}) is below seasonal baseline by {d:+.2f}% (faster-than-usual run conditions)."
    return f"Current bucket ({bucket}) is near seasonal baseline ({d:+.2f}%)."

w7 = window_stats(7)
w30 = window_stats(30)
status7 = classify(w7)
status30 = classify(w30)
hint = seasonal_hint(rows)

result = {"window7": w7, "window30": w30, "status7": status7, "status30": status30, "seasonality_hint": hint}
out_json.write_text(json.dumps(result, indent=2) + "\n")

md = [
    "# sssp2504 Drift Alerts",
    "",
    f"- status7: **{status7}**",
    f"- status30: **{status30}**",
    f"- seasonality_hint: {hint}",
    "",
    "| window | points | p95 sort drift % | p95 phases drift % | p95 relax drift % | exact |",
    "|---|---:|---:|---:|---:|:---:|",
    f"| 7 | {w7.get('count',0)} | {w7.get('sorting_us_p95_drift_pct',0):+.2f}% | {w7.get('phases_p95_drift_pct',0):+.2f}% | {w7.get('relax_p95_drift_pct',0):+.2f}% | {'✅' if w7.get('all_exact',False) else '❌'} |",
    f"| 30 | {w30.get('count',0)} | {w30.get('sorting_us_p95_drift_pct',0):+.2f}% | {w30.get('phases_p95_drift_pct',0):+.2f}% | {w30.get('relax_p95_drift_pct',0):+.2f}% | {'✅' if w30.get('all_exact',False) else '❌'} |",
]
out_md.write_text("\n".join(md) + "\n")

pr = [
    "### sssp2504 Governance Summary",
    "",
    f"- Drift status (7): **{status7}**",
    f"- Drift status (30): **{status30}**",
    f"- 7-window p95 sorting drift: `{w7.get('sorting_us_p95_drift_pct',0):+.2f}%`",
    f"- 7-window p95 relax drift: `{w7.get('relax_p95_drift_pct',0):+.2f}%`",
    f"- Exactness (7-window): `{'PASS' if w7.get('all_exact',False) else 'FAIL'}`",
    f"- Seasonality hint: {hint}",
    "",
    "See artifacts:",
    "- reports/sssp2504-ci-threshold-check.md",
    "- reports/sssp2504-drift-alerts.md",
    "- reports/sssp2504-policy-pr-block.md",
    "- reports/governance-rollup.md",
]
out_pr.write_text("\n".join(pr) + "\n")

print(out_md)
print(out_pr)
