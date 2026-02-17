#include "sssp2504/bmssp.hpp"

#include <algorithm>
#include <cmath>

namespace sssp2504 {
namespace {

int bounded_work_threshold(int k, int level, int t) {
  const int exp = std::max(0, level) * std::max(1, t);
  const int capped_exp = std::min(exp, 20);  // avoid overflow in prototype.
  return std::max(1, k) * (1 << capped_exp);
}

void merge_unique(std::vector<int>& dst, const std::vector<int>& src) {
  std::vector<char> seen;
  int max_id = -1;
  for (int v : dst) max_id = std::max(max_id, v);
  for (int v : src) max_id = std::max(max_id, v);
  if (max_id >= 0) seen.assign(max_id + 1, false);

  std::vector<int> merged;
  merged.reserve(dst.size() + src.size());
  for (int v : dst) {
    if (v >= 0 && v < (int)seen.size() && !seen[v]) {
      seen[v] = true;
      merged.push_back(v);
    }
  }
  for (int v : src) {
    if (v >= 0 && v < (int)seen.size() && !seen[v]) {
      seen[v] = true;
      merged.push_back(v);
    }
  }
  dst.swap(merged);
}

std::vector<int> newly_added(const std::vector<int>& before, const std::vector<int>& after) {
  int max_id = -1;
  for (int v : before) max_id = std::max(max_id, v);
  for (int v : after) max_id = std::max(max_id, v);
  std::vector<char> in_before(std::max(0, max_id + 1), false);
  for (int v : before) {
    if (v >= 0 && v < (int)in_before.size()) in_before[v] = true;
  }

  std::vector<int> out;
  for (int v : after) {
    if (v >= 0 && v < (int)in_before.size() && !in_before[v]) out.push_back(v);
  }
  return out;
}

void record_find_pivots_metrics(const PivotResult& piv, BMSSPMetrics* metrics) {
  if (!metrics) return;
  ++metrics->find_pivots_calls;
  metrics->find_pivots_rounds += piv.rounds;
  metrics->relax_attempts += piv.relax_attempts;
  metrics->relax_successes += piv.relax_successes;
}

void record_u_size(int u_size, BMSSPMetrics* metrics) {
  if (!metrics) return;
  metrics->max_u_size = std::max(metrics->max_u_size, u_size);
}

}  // namespace

BMSSPResult bmssp(
    const Graph& g,
    std::vector<double>& d_hat,
    std::vector<int>& pred,
    int level,
    double B,
    const std::vector<int>& S,
    int k,
    int t,
    BMSSPMetrics* metrics) {
  if (metrics) ++metrics->recursive_calls;

  if (S.empty()) return {.B_prime = B, .U = {}, .successful = true};

  auto piv = find_pivots(g, d_hat, pred, B, S, k);
  record_find_pivots_metrics(piv, metrics);

  BMSSPResult out{.B_prime = B, .U = piv.visited_w, .successful = true};
  record_u_size((int)out.U.size(), metrics);

  // Base case: no deeper contraction possible.
  if (level <= 0 || piv.pivots.empty()) {
    return out;
  }

  const int threshold = bounded_work_threshold(k, level, t);
  if ((int)out.U.size() >= threshold) {
    // Partial-progress contract: return a smaller boundary and bounded-sized U.
    double new_boundary = 0.0;
    for (int v : out.U) {
      if (v >= 0 && v < (int)d_hat.size() && d_hat[v] < B) {
        new_boundary = std::max(new_boundary, d_hat[v]);
      }
    }
    out.B_prime = new_boundary;
    out.successful = false;
    if (metrics) ++metrics->partial_returns;
    return out;
  }

  auto rec = bmssp(g, d_hat, pred, level - 1, B, piv.pivots, k, t, metrics);
  auto before_merge = out.U;
  merge_unique(out.U, rec.U);
  record_u_size((int)out.U.size(), metrics);

  // Boundary progression: continue bounded growth from newly discovered vertices.
  auto seed = newly_added(before_merge, out.U);
  for (int i = 0; i < level && !seed.empty(); ++i) {
    auto wave = find_pivots(g, d_hat, pred, B, seed, k);
    record_find_pivots_metrics(wave, metrics);
    auto snapshot = out.U;
    merge_unique(out.U, wave.visited_w);
    record_u_size((int)out.U.size(), metrics);

    if ((int)out.U.size() >= threshold) {
      double new_boundary = 0.0;
      for (int v : out.U) {
        if (v >= 0 && v < (int)d_hat.size() && d_hat[v] < B) {
          new_boundary = std::max(new_boundary, d_hat[v]);
        }
      }
      out.B_prime = new_boundary;
      out.successful = false;
      if (metrics) ++metrics->partial_returns;
      return out;
    }

    seed = newly_added(snapshot, out.U);
    if (!seed.empty() && metrics) ++metrics->boundary_advancement_events;
  }

  out.B_prime = rec.B_prime;
  out.successful = rec.successful;
  return out;
}

}  // namespace sssp2504
