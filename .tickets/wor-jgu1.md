---
id: wor-jgu1
status: closed
deps: []
links: []
created: 2026-02-14T16:18:57Z
type: epic
priority: 1
assignee: RilusMahmud
tags: [sssp, research, prototype]
---
# Implement directed-SSSP sorting-barrier prototype (arXiv:2504.17033)

Build a theorem-faithful prototype and validation harness for the deterministic O(m log^{2/3} n) directed SSSP algorithm.


## Notes

**2026-02-14T16:28:24Z**

User confirmed C++ implementation and theorem-faithful correctness-first approach.

**2026-02-15T06:49:14Z**

Prototype is now end-to-end: graph + deterministic relax/tie handling, FindPivots, BMSSP recursion with boundary progression semantics, sorting-barrier driver, correctness tests, and JSON benchmark reporting under reports/.
