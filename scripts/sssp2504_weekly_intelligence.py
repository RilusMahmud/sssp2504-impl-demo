#!/usr/bin/env python3
import json
import statistics
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
history_path = ROOT / "reports" / "sssp2504-scale-matrix-history.jsonl"
rollup_path = ROOT / "reports" / "governance-rollup.json"
out_json = ROOT / "reports" / "governance-weekly-intelligence.json"
out_md = ROOT / "reports" / "governance-weekly-intelligence.md"

rows = []
if history_path.exists():
    for line in history_path.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            r.setdefault("sorting_us_p95_global", r.get("sorting_us_p95", 0))
            r.setdefault("phases_p95_global", r.get("phases_p95", 0))
            r.setdefault("relax_attempts_p95_global", r.get("relax_attempts_p95", 0))
            try:
                r["_dt"] = datetime.fromisoformat(r["ts"].replace("Z", "+00:00"))
            except Exception:
                r["_dt"] = datetime.now(timezone.utc)
            rows.append(r)

now = datetime.now(timezone.utc)
last7 = [r for r in rows if now - r["_dt"] <= timedelta(days=7)]
prev7 = [r for r in rows if timedelta(days=7) < (now - r["_dt"]) <= timedelta(days=14)]

def agg(window):
    if not window:
        return None
    return {
        "count": len(window),
        "sorting_p95_med": statistics.median([r["sorting_us_p95_global"] for r in window]),
        "phases_p95_med": statistics.median([r["phases_p95_global"] for r in window]),
        "relax_p95_med": statistics.median([r["relax_attempts_p95_global"] for r in window]),
        "exact_all": all(r.get("all_exact", False) for r in window),
        "sorting_std": statistics.pstdev([r["sorting_us_p95_global"] for r in window]) if len(window) > 1 else 0.0,
    }

A = agg(last7)
B = agg(prev7)

def pct(a,b):
    return 0.0 if a == 0 else ((b-a)/a)*100.0

deltas = None
if A and B:
    deltas = {
        "sorting_p95_med_pct": pct(B["sorting_p95_med"], A["sorting_p95_med"]),
        "phases_p95_med_pct": pct(B["phases_p95_med"], A["phases_p95_med"]),
        "relax_p95_med_pct": pct(B["relax_p95_med"], A["relax_p95_med"]),
        "exact_changed": (A["exact_all"] != B["exact_all"]),
    }

# Confidence score: based on data sufficiency + low variance
if A:
    suff = min(1.0, A["count"] / 7.0)
    var_penalty = min(1.0, A["sorting_std"] / max(1.0, A["sorting_p95_med"]))
    confidence = max(0.0, min(1.0, suff * (1.0 - var_penalty)))
else:
    confidence = 0.0

# Action ranking (simple heuristic)
actions = []
if deltas:
    if deltas["sorting_p95_med_pct"] > 5:
        actions.append((80, "Investigate runtime drift (sorting p95 up >5% WoW); inspect runner load/profile."))
    if deltas["relax_p95_med_pct"] > 5:
        actions.append((70, "Investigate relax-attempt growth; inspect frontier expansion behavior and graph-shape sensitivity."))
    if deltas["phases_p95_med_pct"] > 5:
        actions.append((60, "Investigate phase-count drift; inspect threshold policy and pivot/partial-return behavior."))
    if deltas["exact_changed"]:
        actions.append((100, "Exactness status changed week-over-week; run immediate regression triage."))
if not actions:
    actions.append((40, "No major regressions detected; keep monitoring and accumulate more weekly samples."))
actions.sort(reverse=True)
actions = [a[1] for a in actions[:3]]

risk = 0
if rollup_path.exists():
    roll = json.loads(rollup_path.read_text())
    repos = roll.get("repos", [])
    risk = max([r.get("risk_score", 0) for r in repos] or [0])

out = {
    "generatedAt": now.isoformat(),
    "window": {"last7_count": len(last7), "prev7_count": len(prev7)},
    "last7": A,
    "prev7": B,
    "deltas": deltas,
    "confidence": round(confidence, 3),
    "top_actions": actions,
    "max_repo_risk": risk,
}
out_json.write_text(json.dumps(out, indent=2) + "\n")

lines = [
    "# Weekly Governance Intelligence",
    "",
    f"Generated: {out['generatedAt']}",
    f"Confidence: **{out['confidence']:.2f}**",
    f"Max repo risk score: **{risk}**",
    "",
    "## Week-over-week deltas",
]
if deltas:
    lines += [
        f"- sorting p95 median: {deltas['sorting_p95_med_pct']:+.2f}%",
        f"- phases p95 median: {deltas['phases_p95_med_pct']:+.2f}%",
        f"- relax p95 median: {deltas['relax_p95_med_pct']:+.2f}%",
        f"- exactness changed: {deltas['exact_changed']}",
    ]
else:
    lines += ["- Insufficient history for WoW delta."]

lines += ["", "## Top 3 actions"]
for i, a in enumerate(actions, 1):
    lines.append(f"{i}. {a}")

out_md.write_text("\n".join(lines) + "\n")
print(out_md)
print(out_json)
