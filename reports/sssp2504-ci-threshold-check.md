# sssp2504 CI Threshold Check

- status: **PASS**
- policy: `reports/sssp2504-ci-threshold-policy.profiles.json`
- profile: `local`
- summary: `reports/sssp2504-scale-matrix-summary.json`

| metric | value | limit | pass |
|---|---:|---:|:---:|
| all_exact | True | True | ✅ |
| sorting_us_p95_global | 19379 | 22000 | ✅ |
| sorting_us_max_p95 | 19379 | 24000 | ✅ |
| phases_p95_global | 10 | 10 | ✅ |
| phases_max_p95 | 10 | 12 | ✅ |
| relax_attempts_p95_global | 685896 | 720000 | ✅ |
| relax_attempts_max_p95 | 685896 | 760000 | ✅ |
