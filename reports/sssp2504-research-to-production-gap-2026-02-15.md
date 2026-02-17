# sssp2504 Research-to-Production Gap & Rollout Risk

Date: 2026-02-15
Task: `wor-b3pi`

## 1) Current strengths
- Deterministic prototype for directed SSSP in place.
- Exactness validated on current deterministic corpus and benchmark seeds.
- Strong instrumentation and benchmark reporting available.

## 2) Key gaps to production

1. **Coverage scope**
   - Current validation corpus is substantial but finite; production needs broader adversarial and real-world graph distributions.

2. **Performance SLO definition**
   - Prototype is fast for tested sizes, but no formal latency/throughput SLOs exist yet.

3. **Resource behavior under scale**
   - Need memory/CPU characterization at larger n,m and concurrent workload scenarios.

4. **Operational interface**
   - No stable public API/CLI contract yet for external integration and versioning.

5. **Observability + failure policy**
   - Metrics exist, but no production alert thresholds, degradation behavior, or fallback policy documented.

## 3) Risk matrix

- **Correctness regression risk:** Medium
  - Mitigation: enforce CI gates (`all_finite_match=true`, `mismatch_count=0`) + expanded corpus.

- **Performance drift risk:** Medium
  - Mitigation: benchmark diff checks per PR with threshold alerts.

- **Input-distribution risk:** Medium/High
  - Mitigation: add synthetic adversarial generators + sampled real datasets.

- **Operability risk:** Medium
  - Mitigation: define API contract, error model, and logging schema.

## 4) Rollout plan

### Stage A: Internal hardening
- Expand regression corpus and benchmark matrix.
- Add PR gates + baseline/candidate diff checks.

### Stage B: Controlled canary
- Run shadow mode against representative workloads.
- Compare output parity and cost/time deltas with reference solver.

### Stage C: Gradual adoption
- Route small percentage of jobs to new path.
- Monitor correctness/performance thresholds and rollback triggers.

### Stage D: General availability
- Promote once stability and SLO targets are met across agreed horizon.

## 5) Exit criteria for production-ready signoff
- Zero correctness regressions across approved corpus window.
- Stable benchmark deltas within agreed tolerance bands.
- Documented API + observability + rollback runbook.
- Canary success over target traffic period.
