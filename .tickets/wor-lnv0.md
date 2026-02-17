---
id: wor-lnv0
status: closed
deps: [wor-evpt]
links: []
created: 2026-02-15T06:52:40Z
type: task
priority: 1
assignee: RilusMahmud
parent: wor-anbc
tags: [sssp, correctness, algorithm]
---
# Fix frontier/phase propagation to recover full shortest paths


## Notes

**2026-02-15T06:57:14Z**

Implemented fixes: BMSSP partial boundary update now uses max discovered distance under B; sorting-barrier now includes post-phase full-bound relax waves for correctness closure.
