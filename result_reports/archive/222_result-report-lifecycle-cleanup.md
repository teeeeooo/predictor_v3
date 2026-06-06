# 222 — Result Report Lifecycle Cleanup

## Goal

Reduce the oversized active report set after the table/window-refit arc by
summarizing completed reports, archiving reports sufficiently covered by the
summary, and keeping only current blocker / next-decision evidence active.

## Inventory Result

Initial active report count: 22.

Classification:

- archive possible: `202` through `221b`; these are completed and now covered
  by `result_reports/summaries/221_summary-post-main-table-window-refit-arc.md`;
- active keep: `221c_dynamic-content-refit-loop-stabilization.md`; this is the
  direct evidence for the next decision, common dynamic content refit owner
  preflight;
- no ambiguous hold reports after this pass.

After archive moves and this report, active report count is expected to be 2:

- `221c_dynamic-content-refit-loop-stabilization.md`
- `222_result-report-lifecycle-cleanup.md`

## Summary File

Created:

- `result_reports/summaries/221_summary-post-main-table-window-refit-arc.md`

The summary covers:

- post-main merge and WPF spike closeout context;
- calculator_tk batch mode design and Hong Kong CSPF first slice;
- Hong Kong HSPF load-line source correction;
- batch UI parity corrections;
- design record/rule-source cleanup that supported table UX gates;
- toolkit-neutral table parity gate update;
- harness workflow owner cleanup;
- SPOT example/evidence boundary;
- common Tk table foundation preflight and first slice;
- selected-range fill paste resolution;
- nested notebook/window refit policy update;
- 221B local nested refit scheduling attempt;
- 221C stabilization context and the remaining blocker.

## Archived Reports

Moved to `result_reports/archive/`:

- `202_main-merge-execution.md`
- `203_lightweight-architecture-triage-rule.md`
- `204_wpf-spike-closeout-and-ui-contract-lessons.md`
- `205_calculator-tk-batch-mode-design-plan.md`
- `206_calculator-tk-hong-kong-cspf-batch.md`
- `207_hong-kong-hspf-load-line-source-correction.md`
- `208_calculator-tk-batch-ui-parity-correction.md`
- `209_design-records-lifecycle-rule-source-audit.md`
- `210_minimal-design-inventory-and-table-rule-source-cleanup.md`
- `211_design-record-index-consolidation.md`
- `212_batch-case-table-keep-replace-preflight.md`
- `213_calculator-tk-batch-table-ux-correction.md`
- `214a_table-parity-gate-update.md`
- `215_harness-workflow-owner-cleanup.md`
- `216_calculator-tk-batch-table-windows-smoke-follow-up.md`
- `217_table-ux-target-and-example-evidence-update.md`
- `218_common-tk-table-foundation-preflight.md`
- `219_common-tk-table-foundation-first-slice.md`
- `220_selected-range-fill-paste-and-main-sizing-follow-up.md`
- `221a_window-geometry-policy-nested-refit.md`
- `221b_hong-kong-nested-notebook-refit-scheduling.md`

## Active Reports Kept

- `221c_dynamic-content-refit-loop-stabilization.md` — kept because it records
  the Windows resize-loop cause, the stabilization disable/rollback, and the
  local-vs-common refit owner boundary judgment needed for the next task.

## Memory Seed Update

Updated `result_reports/memory/project_memory_seed.md` with compact durable
entries:

- common Tk table foundation is the preferred path for table-shaped Tk UI;
- SPOT is desired-UX evidence, not source of truth or dependency;
- selected-range fill paste is part of the table UX contract;
- dynamic/nested content refit is an open owner-boundary question; Hong Kong
  lower blank space remains unresolved after loop stabilization.

## WORK_PLAN / Project Log

Updated `docs/WORK_PLAN.md` source summaries to include
`221_summary-post-main-table-window-refit-arc.md`.

Updated `project_log.md` with a short lifecycle cleanup entry and kept 221C as
the active next-decision evidence.

## Validation

- `git diff --check` — passed.
- `python3 -B tools/check_code_structure.py` — passed with the existing soft
  warning that `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `git status --short` — reviewed before commit.

Not run:

- pytest — lifecycle/documentation-only work.
- GUI smoke — no UI code changes.

## Next Action

Common dynamic content refit owner preflight.
