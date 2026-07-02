# 655 Active Report Lifecycle Cleanup - Pre-Arc 13.5

## Goal

Reduce active report noise after calculator maintenance and micro-polish
closeout, while preserving the Arc 13.5 planning report as the next active
work pointer.

## Scope

- Created `result_reports/summaries/654_summary-calculator-maintenance-micro-polish-closeout.md`.
- Archived completed active reports `634`, `645`, `646`, `647`, `648`, `649`,
  `652`, and `653`.
- Kept `635_planning-doc-sync-arc13-5-feature-catalog-editor.md` active.
- Updated the memory seed source coverage and KOREA calculator entry for the
  midpoint guide recommended-capacity correction.

## Changed Files

- `result_reports/summaries/654_summary-calculator-maintenance-micro-polish-closeout.md`
- `result_reports/archive/634_fix-table-font-en14825-header-width.md`
- `result_reports/archive/645_active-report-lifecycle-cleanup-korea-subarc.md`
- `result_reports/archive/646_korea-midpoint-guide-recommended-capacity-fix.md`
- `result_reports/archive/647_memory-seed-maintenance.md`
- `result_reports/archive/648_project-log-lifecycle-cleanup.md`
- `result_reports/archive/649_memory-seed-second-pass-audit.md`
- `result_reports/archive/652_delete-stale-iso-hspf-xlsm-audit.md`
- `result_reports/archive/653_calculator-micro-polish.md`
- `result_reports/memory/project_memory_seed.md`
- `result_reports/active/655_active-report-lifecycle-cleanup-pre-arc13-5.md`

## Verification

- `git diff --check`: OK.
- Active report count: OK; active folder now only keeps the Arc 13.5 planning
  pointer and this cleanup report.
- Memory seed sync: summary coverage and KOREA entry updated.
- Runtime tests not run; this is docs/report lifecycle maintenance only.

## Known Risks

- `635` intentionally remains active as the Arc 13.5 planning pointer.
- Detailed historical recall still requires reading archived source reports or
  the new summary.

## Commit / Push

- Commit and push are performed after final validation.
