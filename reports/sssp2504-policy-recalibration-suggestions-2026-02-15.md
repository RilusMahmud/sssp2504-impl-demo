# Policy Recalibration Suggestions (Phase 8)

Date: 2026-02-15

## Inputs
- Scale summary: `reports/sssp2504-scale-matrix-summary.json`
- Current policy profiles: `reports/sssp2504-ci-threshold-policy.profiles.json`

Observed aggregates:
- `sorting_us_p95 = 19214`
- `sorting_us_max = 19214`
- `phases_p95 = 10`
- `phases_max = 10`
- `relax_attempts_p95 = 685896`
- `relax_attempts_max = 685896`
- `all_exact = true`

## Suggested policy strategy

Use margin bands over observed values:
- **Local profile**: +10% headroom
- **CI profile**: +20% headroom (runner variability)

### Suggested thresholds

Local (suggested):
- `sorting_us_p95_max <= 21136`
- `sorting_us_max <= 21136`
- `phases_p95_max <= 11`
- `phases_max <= 12`
- `relax_attempts_p95_max <= 754486`
- `relax_attempts_max <= 754486`

CI (suggested):
- `sorting_us_p95_max <= 23057`
- `sorting_us_max <= 23057`
- `phases_p95_max <= 11`
- `phases_max <= 12`
- `relax_attempts_p95_max <= 823076`
- `relax_attempts_max <= 823076`

## Recommendation

Current policy already passes. Keep current thresholds for now, and only apply tighter values after collecting at least 5 historical snapshots to avoid overfitting a single run window.
