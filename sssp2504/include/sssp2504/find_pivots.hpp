#pragma once

#include "sssp2504/graph.hpp"
#include <vector>

namespace sssp2504 {

struct BoundedRelaxResult {
  std::vector<int> next_frontier;
  int relax_attempts{};
  int relax_successes{};
};

struct PivotResult {
  std::vector<int> pivots;
  std::vector<int> visited_w;
  int rounds{};
  int relax_attempts{};
  int relax_successes{};
};

BoundedRelaxResult bounded_relax_round(
    const Graph& g,
    std::vector<double>& d_hat,
    std::vector<int>& pred,
    double B,
    const std::vector<int>& frontier);

PivotResult find_pivots(
    const Graph& g,
    std::vector<double>& d_hat,
    std::vector<int>& pred,
    double B,
    const std::vector<int>& S,
    int k);

}  // namespace sssp2504
