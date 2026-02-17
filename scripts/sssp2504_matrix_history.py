#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
summary_path = ROOT / "reports" / "sssp2504-scale-matrix-summary.json"
history_path = ROOT / "reports" / "sssp2504-scale-matrix-history.jsonl"
trend_md = ROOT / "reports" / "sssp2504-scale-matrix-trend.md"

now = datetime.now(timezone.utc)
summary = json.loads(summary_path.read_text())
agg = summary["aggregates"]
record = {
    "ts": now.isoformat(),
    "hour_utc": now.hour,
    "dow_utc": now.weekday(),
    "bucket": f"d{now.weekday()}-h{now.hour:02d}",
    "case_count": agg.get("case_count"),
    "sorting_us_p95_global": agg.get("sorting_us_p95_global", agg.get("sorting_us_p95", 0)),
    "sorting_us_max_p95": agg.get("sorting_us_max_p95", agg.get("sorting_us_max", 0)),
    "phases_p95_global": agg.get("phases_p95_global", agg.get("phases_p95", 0)),
    "phases_max_p95": agg.get("phases_max_p95", agg.get("phases_max", 0)),
    "relax_attempts_p95_global": agg.get("relax_attempts_p95_global", agg.get("relax_attempts_p95", 0)),
    "relax_attempts_max_p95": agg.get("relax_attempts_max_p95", agg.get("relax_attempts_max", 0)),
    "all_exact": agg.get("all_exact"),
}

with history_path.open("a") as f:
    f.write(json.dumps(record) + "\n")

rows = []
for line in history_path.read_text().splitlines():
    if not line.strip():
        continue
    r = json.loads(line)
    r.setdefault("sorting_us_p95_global", r.get("sorting_us_p95", 0))
    r.setdefault("phases_p95_global", r.get("phases_p95", 0))
    r.setdefault("relax_attempts_p95_global", r.get("relax_attempts_p95", 0))
    r.setdefault("bucket", "unknown")
    rows.append(r)

rows = rows[-20:]

md = [
    "# sssp2504 Scale Matrix Trend",
    "",
    "| ts | bucket | p95(us) | p95 phases | p95 relax | exact |",
    "|---|---|---:|---:|---:|:---:|",
]
for r in rows:
    md.append(
        f"| {r['ts']} | {r.get('bucket','?')} | {r['sorting_us_p95_global']} | {r['phases_p95_global']} | {r['relax_attempts_p95_global']} | {'✅' if r.get('all_exact') else '❌'} |"
    )

trend_md.write_text("\n".join(md) + "\n")
print(trend_md)
