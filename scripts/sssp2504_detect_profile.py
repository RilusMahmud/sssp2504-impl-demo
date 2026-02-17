#!/usr/bin/env python3
import os

# Heuristic environment classifier:
# - Explicit override via THRESHOLD_PROFILE always wins.
# - In CI:
#     * >=8 vCPU => ci-fast
#     * else      => ci-standard
# - Outside CI: local

override = os.environ.get("THRESHOLD_PROFILE")
if override:
    print(override)
    raise SystemExit(0)

is_ci = os.environ.get("CI", "").lower() in ("1", "true", "yes")
cpus = os.cpu_count() or 1

if is_ci:
    print("ci-fast" if cpus >= 8 else "ci-standard")
else:
    print("local")
