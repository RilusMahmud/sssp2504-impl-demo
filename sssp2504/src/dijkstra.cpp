#include "sssp2504/dijkstra.hpp"

#include <functional>
#include <limits>
#include <queue>

namespace sssp2504 {

SSSPResult dijkstra(const Graph& g, int s) {
  const double INF = std::numeric_limits<double>::infinity();
  SSSPResult out;
  out.dist.assign(g.n, INF);
  out.pred.assign(g.n, -1);

  using QN = std::pair<double, int>;
  std::priority_queue<QN, std::vector<QN>, std::greater<>> pq;

  out.dist[s] = 0.0;
  pq.push({0.0, s});

  while (!pq.empty()) {
    auto [d, u] = pq.top();
    pq.pop();
    if (d != out.dist[u]) continue;

    for (const auto& e : g.adj[u]) {
      const double nd = d + e.w;
      if (nd < out.dist[e.to]) {
        out.dist[e.to] = nd;
        out.pred[e.to] = u;
        pq.push({nd, e.to});
      }
    }
  }

  return out;
}

}  // namespace sssp2504
