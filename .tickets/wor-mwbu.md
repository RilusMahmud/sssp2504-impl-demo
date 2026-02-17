---
id: wor-mwbu
status: closed
deps: []
links: []
created: 2026-02-15T06:59:10Z
type: task
priority: 1
assignee: RilusMahmud
parent: wor-sfn4
tags: [sssp, optimization, algorithm]
---
# Reduce phase explosion in sorting-barrier frontier scheduling


## Notes

**2026-02-15T06:59:50Z**

Implemented frontier scheduling optimization in sorting_barrier.cpp: next phase now includes only step.U vertices whose distances improved this phase (and <B), instead of all finite vertices.
