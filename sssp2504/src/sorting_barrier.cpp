#include "sssp2504/sorting_barrier.hpp"

#include <algorithm>
#include <limits>

namespace sssp2504 {

SortingBarrierResult directed_sssp_sorting_barrier(
    const Graph& g,
    int source,
    int level,
    int k,
    int t,
    double B,
    int max_phases) {
  SortingBarrierResult out;
  out.dist.assign(g.n, std::numeric_limits<double>::infinity());
  out.pred.assign(g.n, -1);

  if (source < 0 || source >= g.n) return out;

  out.dist[source] = 0.0;
  std::vector<int> active = {source};
  std::vector<char> seen(g.n, false);
  seen[source] = true;
  out.visited_total = 1;

  const int limit = (max_phases > 0) ? max_phases : std::max(1, g.n);
  for (int ph = 0; ph < limit && !active.empty(); ++ph) {
    const auto dist_before = out.dist;

    BMSSPMetrics metrics;
    auto step = bmssp(g, out.dist, out.pred, level, B, active, k, t, &metrics);
    ++out.phases;

    out.recursive_calls += metrics.recursive_calls;
    out.find_pivots_calls += metrics.find_pivots_calls;
    out.find_pivots_rounds += metrics.find_pivots_rounds;
    out.relax_attempts += metrics.relax_attempts;
    out.relax_successes += metrics.relax_successes;
    out.boundary_advancement_events += metrics.boundary_advancement_events;
    out.partial_returns += metrics.partial_returns;
    out.max_u_size = std::max(out.max_u_size, metrics.max_u_size);

    std::vector<int> next_active;
    next_active.reserve(step.U.size());

    bool any_change = false;
    for (int v : step.U) {
      if (v < 0 || v >= g.n) continue;
      if (out.dist[v] + 1e-12 < dist_before[v] && out.dist[v] < B) {
        next_active.push_back(v);
        any_change = true;
      }
      if (!seen[v] && out.dist[v] < std::numeric_limits<double>::infinity()) {
        seen[v] = true;
        ++out.visited_total;
      }
    }

    active.swap(next_active);

    if (!step.successful) B = std::min(B, step.B_prime);
    if (!any_change && step.successful) break;
  }

  // Correctness-closure pass: finish remaining improvements with full-bound relax waves.
  std::vector<int> frontier;
  frontier.reserve(g.n);
  for (int v = 0; v < g.n; ++v) {
    if (out.dist[v] < std::numeric_limits<double>::infinity()) frontier.push_back(v);
  }
  while (!frontier.empty()) {
    auto rr = bounded_relax_round(
        g,
        out.dist,
        out.pred,
        std::numeric_limits<double>::infinity(),
        frontier);
    out.relax_attempts += rr.relax_attempts;
    out.relax_successes += rr.relax_successes;
    frontier.swap(rr.next_frontier);
  }

  return out;
}

}  // namespace sssp2504
