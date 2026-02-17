#include "sssp2504/dijkstra.hpp"

#include <iostream>

using namespace sssp2504;

int main() {
  Graph g(5);
  g.add_edge(0, 1, 2);
  g.add_edge(0, 2, 5);
  g.add_edge(1, 2, 1);
  g.add_edge(1, 3, 2);
  g.add_edge(2, 4, 3);
  g.add_edge(3, 4, 1);

  auto r = dijkstra(g, 0);
  std::cout << "dist(4)=" << r.dist[4] << "\n";
  return 0;
}
