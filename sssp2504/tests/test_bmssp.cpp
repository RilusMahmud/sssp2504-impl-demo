#include "sssp2504/bmssp.hpp"

#include <cassert>
#include <limits>
#include <vector>

using namespace sssp2504;

int main() {
  Graph g(7);
  g.add_edge(0, 1, 1);
  g.add_edge(1, 2, 1);
  g.add_edge(2, 3, 1);
  g.add_edge(0, 4, 2);
  g.add_edge(4, 5, 1);
  g.add_edge(5, 6, 1);

  {
    std::vector<double> d_hat(7, std::numeric_limits<double>::infinity());
    std::vector<int> pred(7, -1);
    d_hat[0] = 0.0;

    auto out = bmssp(g, d_hat, pred, /*level=*/2, /*B=*/10.0, /*S=*/{0}, /*k=*/2, /*t=*/1);

    assert(!out.U.empty());
    assert(out.B_prime <= 10.0);

    // With this tiny graph and budget, the prototype should fully succeed.
    assert(out.successful);
    assert(out.B_prime == 10.0);
  }

  {
    std::vector<double> d_hat(7, std::numeric_limits<double>::infinity());
    std::vector<int> pred(7, -1);
    d_hat[0] = 0.0;

    // Tiny threshold (k=1, level=1, t=1 => 2) should force partial behavior.
    auto out = bmssp(g, d_hat, pred, /*level=*/1, /*B=*/10.0, /*S=*/{0}, /*k=*/1, /*t=*/1);
    assert(!out.successful);
    assert(out.B_prime < 10.0);
  }

  {
    // Progression check on a longer chain: deeper levels should move farther.
    Graph chain(12);
    for (int i = 0; i + 1 < 12; ++i) chain.add_edge(i, i + 1, 1.0);

    std::vector<double> d_hat(12, std::numeric_limits<double>::infinity());
    std::vector<int> pred(12, -1);
    d_hat[0] = 0.0;

    auto out = bmssp(chain, d_hat, pred, /*level=*/4, /*B=*/100.0, /*S=*/{0}, /*k=*/2, /*t=*/2);
    assert(out.successful);
    // At minimum the bounded waves should populate within k hops.
    assert(d_hat[2] < std::numeric_limits<double>::infinity());
  }

  return 0;
}
