#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

make -C sssp2504 clean
make -C sssp2504 test
make -C sssp2504 sssp2504_bench

REPORT_PATH="reports/sssp2504-benchmark-report.json"
./sssp2504/sssp2504_bench "$REPORT_PATH" >/tmp/sssp2504_ci_bench.log

# Optional scale-matrix policy gate (enabled by default in CI)
if [[ "${RUN_SCALE_MATRIX:-1}" == "1" ]]; then
  python3 scripts/sssp2504_scale_matrix.py >/tmp/sssp2504_scale_matrix.log
  POLICY_FILE="${THRESHOLD_POLICY_FILE:-reports/sssp2504-ci-threshold-policy.profiles.json}"
  DETECTED_PROFILE="$(python3 scripts/sssp2504_detect_profile.py)"
  POLICY_PROFILE="${THRESHOLD_PROFILE:-$DETECTED_PROFILE}"
  CI_SUMMARY="${CI_THRESHOLD_SUMMARY:-reports/sssp2504-ci-threshold-check.md}"
  python3 scripts/sssp2504_check_thresholds.py "$POLICY_FILE" "$POLICY_PROFILE" "$CI_SUMMARY"
  python3 scripts/sssp2504_matrix_history.py >/tmp/sssp2504_matrix_history.log
  python3 scripts/sssp2504_policy_suggest.py >/tmp/sssp2504_policy_suggest.log
  python3 scripts/sssp2504_trend_alerts.py >/tmp/sssp2504_trend_alerts.log
  python3 scripts/sssp2504_governance_collect.py >/tmp/sssp2504_governance_collect.log
  python3 scripts/sssp2504_weekly_intelligence.py >/tmp/sssp2504_weekly_intel.log

  # Optional PR governance comment publishing (dry-run by default).
  if [[ -n "${GITHUB_TOKEN:-}" && -n "${GITHUB_REPOSITORY:-}" ]]; then
    if [[ -z "${PR_NUMBER:-}" && -n "${GITHUB_EVENT_PATH:-}" && -f "${GITHUB_EVENT_PATH}" ]]; then
      PR_NUMBER="$(python3 - <<'PY'
import json, os
p=os.environ.get('GITHUB_EVENT_PATH')
try:
    d=json.load(open(p))
    pr=d.get('pull_request',{}) if isinstance(d,dict) else {}
    print(pr.get('number',''))
except Exception:
    print('')
PY
)"
      export PR_NUMBER
    fi

    if [[ -n "${PR_NUMBER:-}" ]]; then
      python3 scripts/sssp2504_publish_pr_comment.py >/tmp/sssp2504_pr_comment.log || true
    fi
  fi
fi

python3 - <<'PY'
import json,sys
p='reports/sssp2504-benchmark-report.json'
with open(p) as f:
    r=json.load(f)

v=r.get('validation',{})
required=[
  ('all_finite_match', True),
  ('mismatch_count', 0),
]
for k,exp in required:
    if v.get(k)!=exp:
        raise SystemExit(f'CI gate failed: validation.{k}={v.get(k)!r}, expected {exp!r}')

if r.get('run',{}).get('phases',0) < 1:
    raise SystemExit('CI gate failed: run.phases must be >= 1')

if r.get('metrics',{}).get('relax_attempts',0) < r.get('metrics',{}).get('relax_successes',0):
    raise SystemExit('CI gate failed: relax_attempts < relax_successes')

print('CI gates passed for sssp2504 benchmark report.')
PY

echo "sssp2504 CI checks passed"
