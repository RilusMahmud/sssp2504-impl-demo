#include "sssp2504/graph.hpp"

#include <stdexcept>

namespace sssp2504 {

void Graph::add_edge(int u, int v, double w) {
  if (u < 0 || u >= n || v < 0 || v >= n) {
    throw std::out_of_range("vertex id out of range");
  }
  if (w < 0.0) {
    throw std::invalid_argument("negative weights are not supported");
  }
  adj[u].push_back({v, w});
}

}  // namespace sssp2504
