#!/usr/bin/env python3
import json
import sys
from pathlib import Path

if len(sys.argv) < 3:
    print("Usage: sssp2504_bench_diff.py <baseline.json> <candidate.json> [out.md]", file=sys.stderr)
    sys.exit(2)

base_p = Path(sys.argv[1])
cand_p = Path(sys.argv[2])
out_p = Path(sys.argv[3]) if len(sys.argv) > 3 else None

base = json.loads(base_p.read_text())
cand = json.loads(cand_p.read_text())

def g(d, *ks, default=None):
    for k in ks:
        if not isinstance(d, dict):
            return default
        d = d.get(k)
    return d if d is not None else default

def band(pref, pct):
    if pref != "lower":
        return "ok"
    if pct > 15:
        return "error"
    if pct > 5:
        return "warn"
    return "ok"

rows = [
    ("timing_us.sorting_barrier", g(base, "timing_us", "sorting_barrier", default=0), g(cand, "timing_us", "sorting_barrier", default=0), "lower"),
    ("run.phases", g(base, "run", "phases", default=0), g(cand, "run", "phases", default=0), "lower"),
    ("metrics.relax_attempts", g(base, "metrics", "relax_attempts", default=0), g(cand, "metrics", "relax_attempts", default=0), "lower"),
    ("metrics.relax_successes", g(base, "metrics", "relax_successes", default=0), g(cand, "metrics", "relax_successes", default=0), "neutral"),
    ("validation.mismatch_count", g(base, "validation", "mismatch_count", default=0), g(cand, "validation", "mismatch_count", default=0), "lower"),
]

base_ok = bool(g(base, "validation", "all_finite_match", default=False))
cand_ok = bool(g(cand, "validation", "all_finite_match", default=False))

lines = []
lines.append("# sssp2504 Benchmark Diff Report")
lines.append("")
lines.append(f"- Baseline: `{base_p}`")
lines.append(f"- Candidate: `{cand_p}`")
lines.append("")
lines.append(f"- Baseline exactness: `{base_ok}`")
lines.append(f"- Candidate exactness: `{cand_ok}`")
lines.append("")
lines.append("| Metric | Baseline | Candidate | Delta | Delta % | Band |")
lines.append("|---|---:|---:|---:|---:|:---:|")

has_warn = False
has_error = False
for name, b, c, pref in rows:
    delta = c - b
    pct = (delta / b * 100.0) if b else 0.0
    bnd = band(pref, pct)
    if bnd == "warn":
        has_warn = True
    if bnd == "error":
        has_error = True
    badge = "✅" if bnd == "ok" else ("⚠️" if bnd == "warn" else "🛑")
    lines.append(f"| {name} | {b} | {c} | {delta:+} | {pct:+.2f}% | {badge} |")

lines.append("")
if cand_ok and not base_ok:
    verdict = "Candidate improves correctness."
elif (not cand_ok) and base_ok:
    verdict = "Candidate regresses correctness (reject)."
else:
    verdict = "Correctness parity maintained."

if has_error:
    verdict += " Drift band: ERROR (performance/work regression >15% on at least one key lower-is-better metric)."
elif has_warn:
    verdict += " Drift band: WARN (regression >5% on at least one key lower-is-better metric)."
else:
    verdict += " Drift band: OK."

lines.append(f"**Verdict:** {verdict}")

text = "\n".join(lines) + "\n"
print(text)
if out_p:
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(text)
