#pragma once

#include "sssp2504/bmssp.hpp"
#include <vector>

namespace sssp2504 {

struct SortingBarrierResult {
  std::vector<double> dist;
  std::vector<int> pred;
  int phases{};
  int visited_total{};

  // Instrumentation counters aggregated from BMSSP/FindPivots.
  int recursive_calls{};
  int find_pivots_calls{};
  int find_pivots_rounds{};
  int relax_attempts{};
  int relax_successes{};
  int boundary_advancement_events{};
  int partial_returns{};
  int max_u_size{};
};

SortingBarrierResult directed_sssp_sorting_barrier(
    const Graph& g,
    int source,
    int level,
    int k,
    int t,
    double B = 1e18,
    int max_phases = -1);

}  // namespace sssp2504
