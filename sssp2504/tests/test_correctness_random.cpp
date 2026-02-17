#include "sssp2504/dijkstra.hpp"
#include "sssp2504/find_pivots.hpp"

#include <cassert>
#include <cmath>
#include <limits>
#include <random>
#include <vector>

using namespace sssp2504;

static Graph random_graph(int n, int m, uint64_t seed) {
  Graph g(n);
  std::mt19937_64 rng(seed);
  std::uniform_int_distribution<int> pick(0, n - 1);
  std::uniform_real_distribution<double> w(0.5, 8.0);

  for (int i = 0; i < m; ++i) {
    int u = pick(rng), v = pick(rng);
    if (u == v) v = (v + 1) % n;
    g.add_edge(u, v, w(rng));
  }
  return g;
}

int main() {
  constexpr double INF = std::numeric_limits<double>::infinity();

  for (uint64_t seed = 1; seed <= 20; ++seed) {
    Graph g = random_graph(/*n=*/32, /*m=*/180, seed);

    auto ref = dijkstra(g, 0);

    std::vector<double> d_hat(g.n, INF);
    std::vector<int> pred(g.n, -1);
    d_hat[0] = 0.0;

    std::vector<int> frontier = {0};
    int guard = 0;
    while (!frontier.empty() && guard++ < 5000) {
      auto rr = bounded_relax_round(g, d_hat, pred, INF, frontier);
      frontier.swap(rr.next_frontier);
    }

    for (int v = 0; v < g.n; ++v) {
      if (ref.dist[v] == INF) {
        assert(d_hat[v] == INF);
      } else {
        assert(std::fabs(d_hat[v] - ref.dist[v]) <= 1e-8);
      }
    }
  }

  return 0;
}
