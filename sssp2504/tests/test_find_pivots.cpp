#include "sssp2504/find_pivots.hpp"

#include <cassert>
#include <limits>
#include <vector>

using namespace sssp2504;

static void test_basic_pivot_pick() {
  Graph g(6);
  g.add_edge(0, 1, 1);
  g.add_edge(1, 2, 1);
  g.add_edge(2, 3, 1);
  g.add_edge(0, 4, 5);
  g.add_edge(4, 5, 1);

  std::vector<double> d_hat(6, std::numeric_limits<double>::infinity());
  std::vector<int> pred(6, -1);
  d_hat[0] = 0.0;

  auto out = find_pivots(g, d_hat, pred, /*B=*/10.0, /*S=*/{0}, /*k=*/2);

  assert(!out.visited_w.empty());
  assert(out.visited_w.size() >= 3);
  assert(!out.pivots.empty());
  assert(out.pivots[0] == 0);
  assert(out.rounds >= 1);
  assert(out.relax_attempts >= out.relax_successes);
}

static void test_early_return_when_w_too_large() {
  Graph g(8);
  for (int v = 1; v < 8; ++v) g.add_edge(0, v, 1.0);

  std::vector<double> d_hat(8, std::numeric_limits<double>::infinity());
  std::vector<int> pred(8, -1);
  d_hat[0] = 0.0;

  auto out = find_pivots(g, d_hat, pred, /*B=*/10.0, /*S=*/{0}, /*k=*/2);

  // |W| becomes 8 > k|S| = 2, so we must return P=S.
  assert(out.pivots.size() == 1);
  assert(out.pivots[0] == 0);
}

static void test_tie_breaker_prefers_smaller_predecessor() {
  Graph g(4);
  g.add_edge(0, 2, 1.0);
  g.add_edge(1, 2, 1.0);
  g.add_edge(2, 3, 1.0);

  std::vector<double> d_hat(4, std::numeric_limits<double>::infinity());
  std::vector<int> pred(4, -1);
  d_hat[0] = 0.0;
  d_hat[1] = 0.0;

  auto rr = bounded_relax_round(g, d_hat, pred, /*B=*/10.0, /*frontier=*/{1, 0});
  (void)rr;

  // Same distance via 0 and 1, tie-break keeps smaller predecessor id (0).
  assert(pred[2] == 0);
}

int main() {
  test_basic_pivot_pick();
  test_early_return_when_w_too_large();
  test_tie_breaker_prefers_smaller_predecessor();
  return 0;
}
