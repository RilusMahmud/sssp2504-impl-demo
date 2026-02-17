#include "sssp2504/dijkstra.hpp"
#include "sssp2504/sorting_barrier.hpp"

#include <cassert>
#include <cmath>
#include <limits>

using namespace sssp2504;

int main() {
  Graph g(8);
  g.add_edge(0, 1, 1);
  g.add_edge(1, 2, 1);
  g.add_edge(2, 3, 1);
  g.add_edge(3, 4, 1);
  g.add_edge(0, 5, 10);
  g.add_edge(5, 6, 1);
  g.add_edge(6, 7, 1);
  g.add_edge(1, 6, 2);

  auto ref = dijkstra(g, 0);
  auto got = directed_sssp_sorting_barrier(g, 0, /*level=*/3, /*k=*/2, /*t=*/2, /*B=*/1e9);

  for (int v = 0; v < g.n; ++v) {
    if (ref.dist[v] == std::numeric_limits<double>::infinity()) {
      assert(got.dist[v] == std::numeric_limits<double>::infinity());
    } else {
      assert(std::fabs(ref.dist[v] - got.dist[v]) <= 1e-9);
    }
  }

  assert(got.phases >= 1);
  assert(got.recursive_calls >= got.phases);
  assert(got.find_pivots_calls >= 1);
  assert(got.find_pivots_rounds >= got.find_pivots_calls);
  assert(got.relax_attempts >= got.relax_successes);
  assert(got.max_u_size >= 1);
  return 0;
}
