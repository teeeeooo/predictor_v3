# 645 Active Report - Lifecycle Cleanup / KOREA Calculator Sub-Arc

## Goal

Clean up active report lifecycle after the KOREA calculator sub-arc by
summarizing completed reports and archiving completed active reports.

## Scope

- Created `result_reports/summaries/644_summary-korea-calculator-subarc-closeout.md`.
- Moved completed KOREA reports `636-643` to `result_reports/archive/`.
- Moved completed prior lifecycle cleanup report `623` to
  `result_reports/archive/`.
- Updated `result_reports/memory/project_memory_seed.md` with the new summary
  registration and one compact durable KOREA decision entry.
- Created this compact lifecycle cleanup report.

## Changed Files

- `result_reports/summaries/644_summary-korea-calculator-subarc-closeout.md`
- `result_reports/archive/623_active-report-lifecycle-cleanup-arc11-arc12.md`
- `result_reports/archive/636_korea-notebook-subarc-readiness.md`
- `result_reports/archive/637_korea-top-level-tab-skeleton.md`
- `result_reports/archive/638_korea-cspf-single-midpoint-guide.md`
- `result_reports/archive/639_korea-hspf-single-midpoint-guide.md`
- `result_reports/archive/640_korea-batch-dialogs.md`
- `result_reports/archive/641_korea-detail-view.md`
- `result_reports/archive/642_korea-subarc-closeout.md`
- `result_reports/archive/643_korea-guide-table-helper-cleanup.md`
- `result_reports/memory/project_memory_seed.md`
- `result_reports/active/645_active-report-lifecycle-cleanup-korea-subarc.md`

## Verification

- `git diff --check`: OK.
- Active report count check: OK, now below lifecycle threshold.
- Memory seed registration check: OK.
- Commit/push publication match: final local/remote match is reported in the
  terminal response.

## Known Risks

- Memory seed compaction was not performed in this cleanup. The seed already
  exceeds the dedicated maintenance threshold, so compaction should remain a
  separate memory maintenance task.
- Active reports unrelated to the KOREA sub-arc remain active.

## Commit / Push

- Commit: performed after report finalization; final hash is reported in the
  terminal response.
- Push: performed after commit; final remote match is reported in the terminal
  response.
