# Policy Recalibration Suggestions (Phase 9)

Date: 2026-02-15

## Basis
- Matrix summary: `reports/sssp2504-scale-matrix-summary.json`
- Current policy profiles: `reports/sssp2504-ci-threshold-policy.profiles.json`
- Trend: `reports/sssp2504-scale-matrix-trend.md`

Observed (global p95/max-p95):
- `sorting_us_p95_global = 24404`
- `sorting_us_max_p95 = 24404`
- `phases_p95_global = 10`
- `phases_max_p95 = 10`
- `relax_attempts_p95_global = 720155`
- `relax_attempts_max_p95 = 720155`
- `all_exact = true`

## Recommendation
Current CI profile is already near observed envelope and passes.

Suggested adjustments (optional, conservative):
- Keep `ci` as-is for now to avoid churn.
- Tighten `local` profile slightly after at least 3 consecutive stable snapshots:
  - `sorting_us_p95_global_max`: 22000 -> 21000
  - `sorting_us_max_p95_max`: 24000 -> 23000
  - `relax_attempts_p95_global_max`: 720000 -> 710000 (only if trend remains flat)

## Governance rule
Do not auto-apply threshold changes. Require manual review + one approval cycle when:
- exactness remains true on all cases,
- last 3 trend snapshots are stable (no upward p95 drift >5%),
- candidate policy still has >=8% headroom over latest observed values.
