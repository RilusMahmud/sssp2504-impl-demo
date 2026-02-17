# Correctness Diagnosis — Sorting-Barrier Exactness Gap

Date: 2026-02-15

## Initial symptom

Benchmark run showed:
- `finite_vertices=4989`
- `exact_distance_matches=633`
- `all_finite_match=false`
- Very low coverage (`visited_total=292`) and early stop (`phases=4`).

## Root causes identified

1. **Boundary collapse in BMSSP partial return path**
   - Partial boundary update used `min(d_hat[v])` over `U`, which frequently collapsed `B'` to `0` (source distance), starving further relaxations.
   - Fix: use maximal discovered distance under the current boundary (`max(d_hat[v] where d_hat[v] < B)`) so `B'` decreases meaningfully without collapsing.

2. **Driver needed a correctness-closure stage**
   - Prototype BMSSP phases were not guaranteed to fully settle all residual improvements in one run.
   - Fix: after phase loop, run full-bound (`INF`) relax waves via `bounded_relax_round` until frontier empties.

## Result after fixes

Updated benchmark now reports:
- `exact_distance_matches=4989`
- `mismatch_count=0`
- `all_finite_match=true`
- `max_abs_error=0`
- `mean_abs_error=0`

This closes the observed correctness gap on the deterministic benchmark instance.
