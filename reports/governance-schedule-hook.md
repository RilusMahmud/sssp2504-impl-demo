# Governance Schedule Hook

Use this command for scheduled weekly generation (e.g., Sunday 09:00 local):

```bash
cd /home/claw/.openclaw/workspace && SSSP_MATRIX_RUNS=3 THRESHOLD_PROFILE=ci-standard bash scripts/ci_sssp2504.sh
```

Suggested cron entry:

```cron
0 9 * * 0 cd /home/claw/.openclaw/workspace && SSSP_MATRIX_RUNS=3 THRESHOLD_PROFILE=ci-standard bash scripts/ci_sssp2504.sh >> /tmp/sssp2504-weekly.log 2>&1
```

This produces:
- `reports/governance-weekly-intelligence.md`
- `reports/governance-rollup.md`
- `reports/sssp2504-ci-threshold-check.md`
- `reports/sssp2504-governance-pr-comment.md`
