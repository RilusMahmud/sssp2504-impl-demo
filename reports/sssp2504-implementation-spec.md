# Implementation Spec: Directed SSSP Sorting-Barrier Prototype

Paper: *Breaking the Sorting Barrier for Directed Single-Source Shortest Paths* (arXiv:2504.17033v2)

## 1) Goal

Implement a theorem-faithful prototype for directed SSSP with nonnegative real weights under comparison-addition assumptions, centered on:

- `FindPivots(B, S)`
- `BMSSP(l, B, S)`
- top-level recursion/driver

Prototype priorities:
1. Correctness and invariant visibility
2. Determinism and reproducibility
3. Instrumented complexity counters
4. Performance second

## 2) Graph model and representation

- Directed graph `G=(V,E)` with `n=|V|`, `m=|E|`.
- Edge weights: nonnegative `double` (configurable to fixed-point wrapper later).
- Outgoing adjacency list (CSR-like vectors in prototype).
- Optional constant-degree transformed graph mode (phase 2) for theorem alignment.

## 3) Core state

Per vertex `v`:
- `d_hat[v]` (upper bound estimate)
- `pred[v]` (predecessor for current best path)
- `complete[v]` flag (debug/verification only; derived in proofs, asserted via checks)

Global:
- source `s`
- current boundary interval context `[b, B)` for staged progress

Tie-breaking (deterministic):
- Compare tuples `(distance, hop_count, endpoint_id, predecessor_chain_lex_hash)`.
- Phase 1 simplification: `(distance, endpoint_id)` while preserving deterministic behavior.

## 4) Subroutine contracts

### 4.1 FindPivots(B, S)

Input assumptions:
- For every incomplete `v` with `d(v) < B`, shortest `s->v` path visits some complete `u in S`.

Output:
- Set `W` and pivot set `P ⊆ S`.
- `|W| = O(k|S|)` (or bounded by discovered region)
- `|P| <= |W|/k`
- For each relevant `x`, either:
  - `x in W` and complete at end of bounded relaxations, or
  - shortest path to `x` visits a complete pivot `y in P`.

Operational plan:
1. Initialize `W0=S`, `W=S`.
2. Perform `k` rounds of bounded relaxations from frontier wave `Wi-1`.
3. Add improved vertices under `<B` into `Wi`, union into `W`.
4. If `|W| > k|S|`, early-return `P=S`.
5. Build tight-edge forest on `W`, choose roots in `S` with subtree size `>=k` as pivots.

### 4.2 BMSSP(l, B, S)

Input assumptions:
- `|S| <= 2^(l*t)`.
- same completeness gateway condition as above.

Output:
- boundary `B' <= B`
- set `U` complete at termination
- either:
  - successful: `B'=B`, or
  - partial: `B'<B` and `|U| = Θ(k*2^(l*t))`.

Operational plan:
- Use `FindPivots` to shrink recursive frontier.
- Recurse on level `l-1` with controlled-sized pulled subsets.
- Stop when bound reaches `B` or partial-work threshold reached.

## 5) Parameters

- `k = floor(log(n)^(1/3))`
- `t = floor(log(n)^(2/3))`
- recursion levels `L = ceil(log(n)/t)`

Prototype allows overrides for experiments.

## 6) Validation strategy

Reference solvers:
- Deterministic Dijkstra (binary heap) for exact cross-check on nonnegative graphs.

Test sets:
- Random sparse digraphs
- Layered DAG-like graphs
- Long-chain + hub stress graphs
- Equal-weight and tie-heavy graphs

Checks:
- Final distances equal reference (within epsilon if double)
- `d_hat` monotone non-increasing per vertex
- Predecessor acyclic consistency assertions
- BMSSP outcome shape (successful/partial constraints)

## 7) Instrumentation

Counters:
- Relaxation attempts/successes
- FindPivots rounds
- Recursive calls by level
- Pulled subset sizes
- Boundary advancement events

Outputs:
- JSON report per run under `reports/`.

## 8) Implementation phases

Phase A: spec + skeleton + reference baseline
Phase B: FindPivots + bounded relax
Phase C: BMSSP recursion
Phase D: verify + benchmark + tuning

## 9) Open clarifications

1. Numeric exactness target: strict theorem tie-ordering vs practical floating-point deterministic mode.
2. Whether to include explicit constant-degree transform in first milestone.
3. Prototype language default switched to C++ here (toolchain available); Rust can be used once cargo is available.
