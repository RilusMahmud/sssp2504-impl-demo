#include "sssp2504/dijkstra.hpp"

#include <cassert>
#include <cmath>

using namespace sssp2504;

int main() {
  Graph g(4);
  g.add_edge(0, 1, 1);
  g.add_edge(1, 2, 2);
  g.add_edge(0, 2, 10);
  g.add_edge(2, 3, 3);

  auto r = dijkstra(g, 0);
  assert(std::fabs(r.dist[2] - 3.0) < 1e-9);
  assert(std::fabs(r.dist[3] - 6.0) < 1e-9);
  return 0;
}
