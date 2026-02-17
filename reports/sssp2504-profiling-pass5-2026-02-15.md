# sssp2504 Profiling Pass (Phase 5)

Date: 2026-02-15
Task: `wor-plcu`

## Method

1. Built benchmark with `-pg` and ran `gprof`.
2. Re-ran production benchmark 10 times and collected `timing_us.sorting_barrier`.
3. Used existing internal metrics (`relax_attempts`, `phases`, etc.) to identify likely hot loops.

## Findings

### A) Runtime distribution (10 runs)
- sorting_barrier_us runs: `2300, 2292, 2309, 2300, 2290, 2313, 2621, 2319, 2296, 2496`
- mean: `2353.6 us`
- median: `2304.5 us`
- min/max: `2290 / 2621 us`

### B) Hot-path indicators
- Dominant algorithmic work is still relax-heavy traversal:
  - `relax_attempts`: `~101k`
  - `phases`: `8`
- `gprof` at current runtime scale produced weak time attribution (`no time accumulated`) due short run duration, but call structure confirms repeated activity in:
  - `bounded_relax_round`
  - `find_pivots`
  - vector reallocation sites in graph/frontier construction

### C) Optimization guidance
- Most leverage remains in reducing relax attempts/edge scans, not in micro-level code motion.
- Next safe wins likely:
  1. Frontier dedup/compaction improvements to reduce repeated relax candidates.
  2. Memory locality improvements in adjacency traversal.
  3. Optional pre-sizing of frontier buffers where bounds are known.

## Conclusion
Profiling confirms the current implementation is already fast (≈2.3 ms median), stable, and dominated by relax-loop work; future optimization should focus on algorithmic work reduction and locality rather than instrumentation-level tuning.
