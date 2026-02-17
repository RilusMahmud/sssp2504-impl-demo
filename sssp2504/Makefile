CXX ?= g++
CXXFLAGS ?= -std=c++20 -O2 -Wall -Wextra -Iinclude

LIB_SRCS = src/graph.cpp src/dijkstra.cpp src/find_pivots.cpp src/bmssp.cpp src/sorting_barrier.cpp
CLI_SRCS = src/main.cpp
BENCH_SRCS = bench/benchmark.cpp
TEST_SRCS = tests/test_basic.cpp
TEST_PIVOT_SRCS = tests/test_find_pivots.cpp
TEST_BMSSP_SRCS = tests/test_bmssp.cpp
TEST_RANDOM_SRCS = tests/test_correctness_random.cpp
TEST_SORTING_BARRIER_SRCS = tests/test_sorting_barrier.cpp
TEST_SORTING_BARRIER_REGRESSION_SRCS = tests/test_sorting_barrier_regression.cpp

all: sssp2504_cli sssp2504_bench sssp2504_tests sssp2504_tests_find_pivots sssp2504_tests_bmssp sssp2504_tests_random sssp2504_tests_sorting_barrier sssp2504_tests_sorting_barrier_regression

sssp2504_cli: $(LIB_SRCS) $(CLI_SRCS)
	$(CXX) $(CXXFLAGS) $^ -o $@

sssp2504_bench: $(LIB_SRCS) $(BENCH_SRCS)
	$(CXX) $(CXXFLAGS) $^ -o $@

sssp2504_tests: $(LIB_SRCS) $(TEST_SRCS)
	$(CXX) $(CXXFLAGS) $^ -o $@

sssp2504_tests_find_pivots: $(LIB_SRCS) $(TEST_PIVOT_SRCS)
	$(CXX) $(CXXFLAGS) $^ -o $@

sssp2504_tests_bmssp: $(LIB_SRCS) $(TEST_BMSSP_SRCS)
	$(CXX) $(CXXFLAGS) $^ -o $@

sssp2504_tests_random: $(LIB_SRCS) $(TEST_RANDOM_SRCS)
	$(CXX) $(CXXFLAGS) $^ -o $@

sssp2504_tests_sorting_barrier: $(LIB_SRCS) $(TEST_SORTING_BARRIER_SRCS)
	$(CXX) $(CXXFLAGS) $^ -o $@

sssp2504_tests_sorting_barrier_regression: $(LIB_SRCS) $(TEST_SORTING_BARRIER_REGRESSION_SRCS)
	$(CXX) $(CXXFLAGS) $^ -o $@

test: sssp2504_tests sssp2504_tests_find_pivots sssp2504_tests_bmssp sssp2504_tests_random sssp2504_tests_sorting_barrier sssp2504_tests_sorting_barrier_regression
	./sssp2504_tests
	./sssp2504_tests_find_pivots
	./sssp2504_tests_bmssp
	./sssp2504_tests_random
	./sssp2504_tests_sorting_barrier
	./sssp2504_tests_sorting_barrier_regression

clean:
	rm -f sssp2504_cli sssp2504_bench sssp2504_tests sssp2504_tests_find_pivots sssp2504_tests_bmssp sssp2504_tests_random sssp2504_tests_sorting_barrier sssp2504_tests_sorting_barrier_regression
