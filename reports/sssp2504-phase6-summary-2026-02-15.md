# Phase 6 Summary — Scale Validation + CI Threshold Policy

Date: 2026-02-15
Epic: `wor-ly5d`

## Completed

1. **Scale matrix runner**
- Added configurable benchmark CLI args in `sssp2504/bench/benchmark.cpp`
  - `out_path n m seed level k t source`
- Added matrix runner script: `scripts/sssp2504_scale_matrix.py`
- Generated:
  - `reports/sssp2504-scale-matrix-summary.json`
  - `reports/sssp2504-scale-matrix-summary.md`

Current matrix snapshot:
- s1 (1000, 6000, seed 101): sorting_us 516, phases 6, relax_attempts 30841, exact ✅
- s2 (2000, 12000, seed 202): sorting_us 907, phases 7, relax_attempts 44345, exact ✅
- s3 (5000, 30000, seed 2504): sorting_us 2161, phases 8, relax_attempts 101386, exact ✅

2. **CI threshold policy**
- Added policy file: `reports/sssp2504-ci-threshold-policy.json`
- Added checker: `scripts/sssp2504_check_thresholds.py`
- Initial thresholds:
  - `all_exact = true`
  - `sorting_us_max <= 4000`
  - `phases_max <= 12`
  - `relax_attempts_max <= 130000`

3. **CI integration**
- Updated gate script: `scripts/ci_sssp2504.sh`
  - Runs tests + benchmark
  - Runs scale matrix + threshold checker (default on)
- Existing workflow `.github/workflows/sssp2504-ci.yml` now enforces this via the gate script.

## Outcome
- Phase 6 objectives achieved.
- Scale validation and policy-based drift gates are now active.
