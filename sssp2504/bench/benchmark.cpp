#include "sssp2504/dijkstra.hpp"
#include "sssp2504/sorting_barrier.hpp"

#include <chrono>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <random>
#include <sstream>
#include <vector>

using namespace sssp2504;

static Graph make_random_graph(int n, int m, uint64_t seed) {
  Graph g(n);
  std::mt19937_64 rng(seed);
  std::uniform_int_distribution<int> pick_v(0, n - 1);
  std::uniform_real_distribution<double> pick_w(1.0, 20.0);

  for (int i = 0; i < m; ++i) {
    int u = pick_v(rng), v = pick_v(rng);
    if (u == v) v = (v + 1) % n;
    g.add_edge(u, v, pick_w(rng));
  }
  return g;
}

static std::string build_json(
    int n,
    int m,
    int source,
    int level,
    int k,
    int t,
    uint64_t seed,
    long long dijkstra_us,
    long long sorting_barrier_us,
    int finite_total,
    int finite_match,
    int mismatch_count,
    double max_abs_error,
    double mean_abs_error,
    const SortingBarrierResult& out) {
  std::ostringstream os;
  os << "{\n";
  os << "  \"algorithm\": \"directed_sssp_sorting_barrier\",\n";
  os << "  \"n\": " << n << ",\n";
  os << "  \"m\": " << m << ",\n";
  os << "  \"source\": " << source << ",\n";
  os << "  \"seed\": " << seed << ",\n";
  os << "  \"params\": {\"level\": " << level << ", \"k\": " << k << ", \"t\": " << t << "},\n";
  os << "  \"timing_us\": {\"dijkstra\": " << dijkstra_us
     << ", \"sorting_barrier\": " << sorting_barrier_us << "},\n";
  os << "  \"timing_ms\": {\"dijkstra\": " << (dijkstra_us / 1000.0)
     << ", \"sorting_barrier\": " << (sorting_barrier_us / 1000.0) << "},\n";
  os << "  \"validation\": {\"finite_vertices\": " << finite_total
     << ", \"exact_distance_matches\": " << finite_match
     << ", \"mismatch_count\": " << mismatch_count
     << ", \"max_abs_error\": " << max_abs_error
     << ", \"mean_abs_error\": " << mean_abs_error
     << ", \"all_finite_match\": " << (finite_match == finite_total ? "true" : "false") << "},\n";
  os << "  \"run\": {\"phases\": " << out.phases
     << ", \"visited_total\": " << out.visited_total << "},\n";
  os << "  \"metrics\": {\n";
  os << "    \"recursive_calls\": " << out.recursive_calls << ",\n";
  os << "    \"find_pivots_calls\": " << out.find_pivots_calls << ",\n";
  os << "    \"find_pivots_rounds\": " << out.find_pivots_rounds << ",\n";
  os << "    \"relax_attempts\": " << out.relax_attempts << ",\n";
  os << "    \"relax_successes\": " << out.relax_successes << ",\n";
  os << "    \"boundary_advancement_events\": " << out.boundary_advancement_events << ",\n";
  os << "    \"partial_returns\": " << out.partial_returns << ",\n";
  os << "    \"max_u_size\": " << out.max_u_size << "\n";
  os << "  }\n";
  os << "}\n";
  return os.str();
}

int main(int argc, char** argv) {
  int n = 5000;
  int m = 30000;
  int source = 0;
  int level = 3;
  int k = 4;
  int t = 2;
  double B = 1e12;
  uint64_t seed = 2504;

  std::filesystem::path out_path = "../reports/sssp2504-benchmark-report.json";
  if (argc > 1) out_path = argv[1];
  if (argc > 2) n = std::atoi(argv[2]);
  if (argc > 3) m = std::atoi(argv[3]);
  if (argc > 4) seed = static_cast<uint64_t>(std::strtoull(argv[4], nullptr, 10));
  if (argc > 5) level = std::atoi(argv[5]);
  if (argc > 6) k = std::atoi(argv[6]);
  if (argc > 7) t = std::atoi(argv[7]);
  if (argc > 8) source = std::atoi(argv[8]);

  auto g = make_random_graph(n, m, seed);

  auto t0 = std::chrono::steady_clock::now();
  auto ref = dijkstra(g, source);
  auto t1 = std::chrono::steady_clock::now();

  auto t2 = std::chrono::steady_clock::now();
  auto out = directed_sssp_sorting_barrier(g, source, level, k, t, B, -1);
  auto t3 = std::chrono::steady_clock::now();

  auto dijkstra_us = std::chrono::duration_cast<std::chrono::microseconds>(t1 - t0).count();
  auto sorting_barrier_us = std::chrono::duration_cast<std::chrono::microseconds>(t3 - t2).count();

  int finite_match = 0;
  int finite_total = 0;
  int mismatch_count = 0;
  double max_abs_error = 0.0;
  double sum_abs_error = 0.0;
  for (int i = 0; i < n; ++i) {
    if (ref.dist[i] < std::numeric_limits<double>::infinity()) {
      ++finite_total;
      const double err = std::abs(ref.dist[i] - out.dist[i]);
      if (err <= 1e-9) {
        ++finite_match;
      } else {
        ++mismatch_count;
      }
      max_abs_error = std::max(max_abs_error, err);
      sum_abs_error += err;
    }
  }

  const double mean_abs_error = (finite_total > 0) ? (sum_abs_error / finite_total) : 0.0;

  const auto json = build_json(
      n,
      m,
      source,
      level,
      k,
      t,
      seed,
      dijkstra_us,
      sorting_barrier_us,
      finite_total,
      finite_match,
      mismatch_count,
      max_abs_error,
      mean_abs_error,
      out);

  std::filesystem::create_directories(out_path.parent_path());
  std::ofstream ofs(out_path);
  ofs << json;
  ofs.close();

  std::cout << json;
  std::cout << "report_path=\"" << out_path.string() << "\"\n";

  return 0;
}
