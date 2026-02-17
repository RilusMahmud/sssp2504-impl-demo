#!/usr/bin/env python3
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
policy_path = ROOT / "reports" / "sssp2504-ci-threshold-policy.profiles.json"
summary_path = ROOT / "reports" / "sssp2504-scale-matrix-summary.json"
out_report = ROOT / "reports" / "sssp2504-policy-suggestion.md"
out_pr = ROOT / "reports" / "sssp2504-policy-pr-block.md"

policy = json.loads(policy_path.read_text())
summary = json.loads(summary_path.read_text())
agg = summary["aggregates"]

latest = {
    "sorting_us_p95_global_max": agg.get("sorting_us_p95_global", 0),
    "sorting_us_max_p95_max": agg.get("sorting_us_max_p95", 0),
    "phases_p95_global_max": agg.get("phases_p95_global", 0),
    "phases_max_p95_max": agg.get("phases_max_p95", 0),
    "relax_attempts_p95_global_max": agg.get("relax_attempts_p95_global", 0),
    "relax_attempts_max_p95_max": agg.get("relax_attempts_max_p95", 0),
}

# Suggest 12% headroom over latest observed for perf metrics.
def suggested(v):
    return int(math.ceil(v * 1.12))

profiles = policy.get("profiles", {})

lines = ["# sssp2504 Policy Suggestion", "", "Suggested updates (manual review only):", ""]
pr = ["### Suggested threshold updates", "", "```json"]

proposal = {}
for name, prof in profiles.items():
    if name == "local":
        factor = 1.08
    elif name in ("ci-fast",):
        factor = 1.12
    else:
        factor = 1.20

    p = dict(prof)
    for k, obs in latest.items():
        if k in p:
            newv = int(math.ceil(obs * factor))
            if newv != p[k]:
                p[k] = newv
    proposal[name] = p

    lines.append(f"## {name}")
    for k in latest:
        cur = prof.get(k)
        new = p.get(k)
        obs = latest[k]
        if cur is None:
            continue
        delta = new - cur
        lines.append(f"- {k}: current={cur}, observed={obs}, suggested={new} ({delta:+})")
    lines.append("")

pr.append(json.dumps({"profiles": proposal}, indent=2))
pr.append("```")

out_report.write_text("\n".join(lines) + "\n")
out_pr.write_text("\n".join(pr) + "\n")
print(out_report)
print(out_pr)
