#include "sssp2504/find_pivots.hpp"

#include <algorithm>
#include <cmath>

namespace sssp2504 {

BoundedRelaxResult bounded_relax_round(
    const Graph& g,
    std::vector<double>& d_hat,
    std::vector<int>& pred,
    double B,
    const std::vector<int>& frontier) {
  BoundedRelaxResult out;
  std::vector<char> seen(g.n, false);

  for (int u : frontier) {
    for (const auto& e : g.adj[u]) {
      ++out.relax_attempts;
      const double nd = d_hat[u] + e.w;
      const bool better = (nd < d_hat[e.to]);
      const bool tie_better = (std::fabs(nd - d_hat[e.to]) <= 1e-12) &&
                              (pred[e.to] == -1 || u < pred[e.to]);
      if (!(better || tie_better)) continue;

      ++out.relax_successes;
      d_hat[e.to] = nd;
      pred[e.to] = u;

      if (nd < B && !seen[e.to]) {
        seen[e.to] = true;
        out.next_frontier.push_back(e.to);
      }
    }
  }

  return out;
}

PivotResult find_pivots(
    const Graph& g,
    std::vector<double>& d_hat,
    std::vector<int>& pred,
    double B,
    const std::vector<int>& S,
    int k) {
  PivotResult out;
  out.visited_w = S;
  std::vector<int> prev = S;

  std::vector<char> in_w(g.n, false);
  for (int s : S) in_w[s] = true;

  for (int step = 1; step <= std::max(0, k); ++step) {
    auto rr = bounded_relax_round(g, d_hat, pred, B, prev);
    out.relax_attempts += rr.relax_attempts;
    out.relax_successes += rr.relax_successes;
    ++out.rounds;

    for (int v : rr.next_frontier) {
      if (!in_w[v]) {
        in_w[v] = true;
        out.visited_w.push_back(v);
      }
    }

    prev.swap(rr.next_frontier);

    if ((int)out.visited_w.size() > std::max(1, k) * (int)S.size()) {
      out.pivots = S;
      return out;
    }
    if (prev.empty()) break;
  }

  const double EPS = 1e-12;
  std::vector<int> in_w_index(g.n, -1);
  for (int i = 0; i < (int)out.visited_w.size(); ++i) in_w_index[out.visited_w[i]] = i;

  std::vector<std::vector<int>> children(g.n);
  for (int v : out.visited_w) {
    const int p = (v >= 0 && v < (int)pred.size()) ? pred[v] : -1;
    if (p < 0 || in_w_index[p] == -1) continue;

    bool tight = false;
    for (const auto& e : g.adj[p]) {
      if (e.to == v && std::fabs((d_hat[p] + e.w) - d_hat[v]) <= EPS) {
        tight = true;
        break;
      }
    }
    if (tight) children[p].push_back(v);
  }

  std::vector<int> subtree(g.n, 0);
  std::vector<int> order = out.visited_w;
  std::sort(order.begin(), order.end(), [&](int a, int b) { return d_hat[a] > d_hat[b]; });

  for (int v : order) {
    int sum = 1;
    for (int c : children[v]) sum += subtree[c];
    subtree[v] = sum;
  }

  for (int s : S) {
    if (subtree[s] >= std::max(1, k)) out.pivots.push_back(s);
  }

  return out;
}

}  // namespace sssp2504
