cmake_minimum_required(VERSION 3.16)
project(sssp2504 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(sssp2504
    src/graph.cpp
    src/dijkstra.cpp
    src/find_pivots.cpp
    src/bmssp.cpp
    src/sorting_barrier.cpp
)

target_include_directories(sssp2504 PUBLIC include)

add_executable(sssp2504_cli src/main.cpp)
target_link_libraries(sssp2504_cli PRIVATE sssp2504)

add_executable(sssp2504_tests tests/test_basic.cpp)
target_link_libraries(sssp2504_tests PRIVATE sssp2504)

add_executable(sssp2504_tests_find_pivots tests/test_find_pivots.cpp)
target_link_libraries(sssp2504_tests_find_pivots PRIVATE sssp2504)

add_executable(sssp2504_tests_bmssp tests/test_bmssp.cpp)
target_link_libraries(sssp2504_tests_bmssp PRIVATE sssp2504)

add_executable(sssp2504_bench bench/benchmark.cpp)
target_link_libraries(sssp2504_bench PRIVATE sssp2504)

add_executable(sssp2504_tests_random tests/test_correctness_random.cpp)
target_link_libraries(sssp2504_tests_random PRIVATE sssp2504)

add_executable(sssp2504_tests_sorting_barrier tests/test_sorting_barrier.cpp)
target_link_libraries(sssp2504_tests_sorting_barrier PRIVATE sssp2504)
