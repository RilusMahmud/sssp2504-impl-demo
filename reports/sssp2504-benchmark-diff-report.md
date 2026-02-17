# sssp2504 Benchmark Diff Report

- Baseline: `reports/sssp2504-benchmark-baseline.json`
- Candidate: `reports/sssp2504-benchmark-candidate.json`

- Baseline exactness: `True`
- Candidate exactness: `True`

| Metric | Baseline | Candidate | Delta | Delta % | Band |
|---|---:|---:|---:|---:|:---:|
| timing_us.sorting_barrier | 2157 | 2829 | +672 | +31.15% | 🛑 |
| run.phases | 8 | 8 | +0 | +0.00% | ✅ |
| metrics.relax_attempts | 101386 | 101386 | +0 | +0.00% | ✅ |
| metrics.relax_successes | 12250 | 12250 | +0 | +0.00% | ✅ |
| validation.mismatch_count | 0 | 0 | +0 | +0.00% | ✅ |

**Verdict:** Correctness parity maintained. Drift band: ERROR (performance/work regression >15% on at least one key lower-is-better metric).
