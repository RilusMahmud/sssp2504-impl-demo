#pragma once

#include <cstdint>
#include <vector>

namespace sssp2504 {

struct Edge {
  int to;
  double w;
};

struct Graph {
  int n{};
  std::vector<std::vector<Edge>> adj;

  explicit Graph(int n = 0) : n(n), adj(n) {}
  void add_edge(int u, int v, double w);
};

}  // namespace sssp2504
