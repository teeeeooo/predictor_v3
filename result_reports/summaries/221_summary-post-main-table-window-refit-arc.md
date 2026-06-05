# 221 Summary — Post-main Table Foundation and Window Refit Arc

## Covered Reports

Archived by this summary:

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

Active context intentionally not archived by this summary:

- `221c_dynamic-content-refit-loop-stabilization.md`

## Arc Result

The post-main branch returned from the C# WPF spike to the Tkinter calculator
path, implemented the first Hong Kong CSPF batch surface, discovered that the
initial batch table did not meet the Excel-like table contract, and created a
common Tk table foundation first slice. Selected-range fill paste is resolved.

The window geometry work reached a clear boundary: local Hong Kong nested
notebook refit scheduling caused a Windows resize loop in 221B, and 221C
stabilized the app by disabling direct metric tab-change refit. The remaining
Hong Kong CSPF lower blank space is an owner-boundary problem, not a local
one-off fix.

## Major Decisions

- C# WPF is not merged into `main`. It remains a technology-choice experiment,
  and the calculator flow returns to `calculator_tk`.
- Table-shaped UI must satisfy the toolkit-neutral Excel-like contract in
  `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`.
- Toolkit adapters explain implementation approach only; they are not the
  table UX source of truth.
- SPOT is concrete desired-UX evidence only, not a source of truth, dependency,
  vendor target, or copy target.
- New Tkinter table-shaped UI should use the common Tk table foundation before
  adding independent controllers.
- `docs/designs/README.md` is the design record index. Individual design
  records are evidence/library records rather than active rule owners.
- Dynamic/nested content refit is a toolkit-neutral owner-boundary issue. A
  common dynamic content refit owner is needed before reintroducing nested
  tab-change refit.

## Completed Work

- Merged the UI/UX SSOT adoption branch into `main`.
- Added the lightweight architecture triage rule before the WPF spike.
- Closed the C# WPF spike without merging C# code.
- Planned and implemented the first Hong Kong CSPF row-per-case batch mode.
- Moved batch entry from a metric tab into a CSPF-page dialog.
- Removed the visible Case input column and moved row identity to row headers.
- Removed the visible Status result column from calculator batch output.
- Changed batch calculation to auto-calc style with blank/partial/invalid rows
  leaving result cells blank.
- Created `ui_tk/table/` common Tk table foundation first slice:
  Tk-free interaction helpers, cell roles, surface protocol, and Tk controller.
- Migrated the Hong Kong CSPF batch table path to the common foundation bridge.
- Added selected-range fill paste behavior:
  `1 x N` clipboard into `M x N` selection repeats the row, and `1 x 1`
  clipboard fills the selected editable range.
- Preserved result/read-only cell mutation protection and grouped undo for the
  common table foundation path.
- Corrected Hong Kong HSPF load-line source to measured `7 Full` capacity and
  removed rated heating capacity as a required UI input for Hong Kong HSPF.
- Added table parity gate rules and controller/helper-level validation
  expectations.
- Split long agent workflow details into owner docs and tightened smoke
  follow-up read/validation flow.
- Added nested notebook / dynamic sub-tab refit policy to
  `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`.
- Stabilized the 221B Windows refit loop in 221C by disabling direct metric
  tab-change refit and holding the scheduler pending guard through the active
  fit.

## Known Remaining Issues

- Hong Kong CSPF lower blank space is not fully resolved.
- Direct metric notebook tab-change refit remains disabled until a common
  dynamic content refit owner is designed.
- Common Tk table foundation is batch-first; calculator main table migration is
  not done.
- HSPF / EN14825 / AHRI / KS batch modes are not implemented.
- Common detail/bin result schema is still pending.
- Windows GUI smoke is still required after the dynamic refit owner decision.

## Current Active Report Kept

`221c_dynamic-content-refit-loop-stabilization.md` stays active because it is
the direct evidence for the next decision: common dynamic content refit owner
preflight. It records the refit loop cause, the stabilization rollback/disable,
and why local tab-level scheduling is not enough.

## Next Action

Common dynamic content refit owner preflight.
