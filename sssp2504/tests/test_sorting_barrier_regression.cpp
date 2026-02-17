#include "sssp2504/dijkstra.hpp"
#include "sssp2504/sorting_barrier.hpp"

#include <cassert>
#include <cmath>
#include <cstdint>
#include <limits>
#include <random>
#include <vector>

using namespace sssp2504;

static Graph make_er_graph(int n, int m, uint64_t seed) {
  Graph g(n);
  std::mt19937_64 rng(seed);
  std::uniform_int_distribution<int> pick_v(0, n - 1);
  std::uniform_real_distribution<double> pick_w(0.5, 15.0);
  for (int i = 0; i < m; ++i) {
    int u = pick_v(rng), v = pick_v(rng);
    if (u == v) v = (v + 1) % n;
    g.add_edge(u, v, pick_w(rng));
  }
  return g;
}

static Graph make_layered_dag(int layers, int width, uint64_t seed) {
  const int n = layers * width;
  Graph g(n);
  std::mt19937_64 rng(seed);
  std::uniform_real_distribution<double> pick_w(0.2, 3.0);

  for (int l = 0; l + 1 < layers; ++l) {
    for (int i = 0; i < width; ++i) {
      const int u = l * width + i;
      for (int j = 0; j < width; ++j) {
        if ((i + j + l) % 3 == 0) {
          const int v = (l + 1) * width + j;
          g.add_edge(u, v, pick_w(rng));
        }
      }
    }
  }
  return g;
}

static Graph make_chain_hub(int n, uint64_t seed) {
  Graph g(n);
  std::mt19937_64 rng(seed);
  std::uniform_real_distribution<double> pick_w(0.1, 5.0);

  for (int i = 0; i + 1 < n; ++i) {
    g.add_edge(i, i + 1, pick_w(rng));
  }

  const int hub = n / 2;
  for (int i = 0; i < n; ++i) {
    if (i == hub) continue;
    if (i % 4 == 0) g.add_edge(hub, i, pick_w(rng) + 1.0);
    if (i % 5 == 0) g.add_edge(i, hub, pick_w(rng) + 1.0);
  }

  return g;
}

static void assert_exact(const Graph& g, int source) {
  constexpr double INF = std::numeric_limits<double>::infinity();
  auto ref = dijkstra(g, source);
  auto got = directed_sssp_sorting_barrier(g, source, /*level=*/3, /*k=*/4, /*t=*/2, /*B=*/1e12);

  for (int v = 0; v < g.n; ++v) {
    if (ref.dist[v] == INF) {
      assert(got.dist[v] == INF);
    } else {
      assert(std::fabs(ref.dist[v] - got.dist[v]) <= 1e-9);
    }
  }
  assert(got.phases >= 1);
}

int main() {
  const std::vector<uint64_t> seeds = {11, 29, 47};

  // Medium ER graphs.
  for (uint64_t s : seeds) {
    auto g = make_er_graph(/*n=*/128, /*m=*/900, s);
    assert_exact(g, 0);
  }

  // Large-ish ER graphs.
  for (uint64_t s : seeds) {
    auto g = make_er_graph(/*n=*/512, /*m=*/5000, 1000 + s);
    assert_exact(g, 0);
  }

  // Layered DAGs.
  for (uint64_t s : seeds) {
    auto g = make_layered_dag(/*layers=*/16, /*width=*/24, 2000 + s); // n=384
    assert_exact(g, 0);
  }

  // Chain+hub stress.
  for (uint64_t s : seeds) {
    auto g = make_chain_hub(/*n=*/600, 3000 + s);
    assert_exact(g, 0);
  }

  return 0;
}
