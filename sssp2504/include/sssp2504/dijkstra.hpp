#pragma once

#include "sssp2504/graph.hpp"
#include <vector>

namespace sssp2504 {

struct SSSPResult {
  std::vector<double> dist;
  std::vector<int> pred;
};

SSSPResult dijkstra(const Graph& g, int s);

}  // namespace sssp2504
