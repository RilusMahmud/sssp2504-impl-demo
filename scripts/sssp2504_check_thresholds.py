#!/usr/bin/env python3
import json
import sys
from pathlib import Path

if len(sys.argv) not in (2, 3, 4):
    print("Usage: sssp2504_check_thresholds.py <policy.json> [profile] [summary.md]", file=sys.stderr)
    sys.exit(2)

policy_path = Path(sys.argv[1])
profile = sys.argv[2] if len(sys.argv) >= 3 else None
summary_out = Path(sys.argv[3]) if len(sys.argv) == 4 else None

policy = json.loads(policy_path.read_text())
summary_path = Path(policy["matrixSummary"])
summary = json.loads(summary_path.read_text())
agg = summary["aggregates"]

if "profiles" in policy:
    profile = profile or "ci"
    if profile not in policy["profiles"]:
        raise SystemExit(f"Unknown profile '{profile}'. Available: {', '.join(policy['profiles'].keys())}")
    req = policy["profiles"][profile]
else:
    req = policy["requirements"]

errors = []
checks = []

def check(metric, limit_key):
    if limit_key not in req:
        return
    val = agg.get(metric, 10**18)
    lim = req[limit_key]
    ok = val <= lim
    checks.append((metric, val, lim, ok))
    if not ok:
        errors.append(f"{metric}={val} > {lim}")

exact_ok = bool(agg.get("all_exact")) == bool(req.get("all_exact", True))
if not exact_ok:
    errors.append(f"all_exact={agg.get('all_exact')} expected {req.get('all_exact')}")

check("sorting_us_p95_global", "sorting_us_p95_global_max")
check("sorting_us_max_p95", "sorting_us_max_p95_max")
check("phases_p95_global", "phases_p95_global_max")
check("phases_max_p95", "phases_max_p95_max")
check("relax_attempts_p95_global", "relax_attempts_p95_global_max")
check("relax_attempts_max_p95", "relax_attempts_max_p95_max")

status = "PASS" if not errors else "FAIL"

if summary_out:
    lines = [
        "# sssp2504 CI Threshold Check",
        "",
        f"- status: **{status}**",
        f"- policy: `{policy_path}`",
        f"- profile: `{profile or 'default'}`",
        f"- summary: `{summary_path}`",
        "",
        "| metric | value | limit | pass |",
        "|---|---:|---:|:---:|",
        f"| all_exact | {agg.get('all_exact')} | {req.get('all_exact', True)} | {'✅' if exact_ok else '❌'} |",
    ]
    for m,v,l,ok in checks:
        lines.append(f"| {m} | {v} | {l} | {'✅' if ok else '❌'} |")
    if errors:
        lines += ["", "## Fail reasons"] + [f"- {e}" for e in errors]
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.write_text("\n".join(lines) + "\n")

if errors:
    print("Threshold policy failed:")
    if profile:
        print(f" profile={profile}")
    for e in errors:
        print(" -", e)
    sys.exit(1)

print("Threshold policy passed." + (f" profile={profile}" if profile else ""))
