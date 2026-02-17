#pragma once

#include "sssp2504/find_pivots.hpp"

namespace sssp2504 {

struct BMSSPMetrics {
  int recursive_calls{};
  int find_pivots_calls{};
  int find_pivots_rounds{};
  int relax_attempts{};
  int relax_successes{};
  int boundary_advancement_events{};
  int partial_returns{};
  int max_u_size{};
};

struct BMSSPResult {
  double B_prime;
  std::vector<int> U;
  bool successful;
};

BMSSPResult bmssp(
    const Graph& g,
    std::vector<double>& d_hat,
    std::vector<int>& pred,
    int level,
    double B,
    const std::vector<int>& S,
    int k,
    int t,
    BMSSPMetrics* metrics = nullptr);

}  // namespace sssp2504
