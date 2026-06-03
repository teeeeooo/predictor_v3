# 194-c Excel-Like Table Contract Recovery

## Goal

Audit the current Tkinter table UX against the project Excel-like table intent and document a recovery contract before further table/trace/graph work.

## Scope

- Reviewed existing Excel-like UI/UX docs and current Tkinter table-related implementations by targeted class/function references.
- Added `docs/designs/2026-05-30-tkinter-excel-like-table-contract-recovery.md`.
- Updated WORK_PLAN with the next recovery slice.
- No source or test files were modified.

## Current Responsibility Check

- Editable inputs: `MetricInputTable` plus `ExcelLikeTableController` owns spreadsheet editing behavior including selection, TSV copy/paste, delete/clear, undo, and navigation.
- Read-only result/trace tables: Treeview-based surfaces own display, Ctrl/Cmd+C binding, copy text, and CSV export hooks, but not a shared header-included TSV copy contract.
- `ResultPanel`: label-card summary surface with retained copy text, not a grid-like table/export data contract.
- CSV export foundation: currently writes table-shaped surface headers/rows where a surface exposes export data.

## Mismatch

- The Excel-like contract was effectively applied first to editable input/paste behavior.
- Result/trace tables were implemented as read-only display/export surfaces, so selection/copy UX was not recovered to the same baseline.
- `ResultPanel` remained a summary-card path and diverges from grid/table copy semantics.
- PyQt read-only table references were ported for display parity, but Tkinter read-only copy/selection parity was not an explicit acceptance gate.
- The cross-surface rule “all table-like surfaces provide Excel-friendly copy/export” was not explicit enough for new table surfaces.

## Confirmed Contract

- All table-like surfaces must provide Excel paste-friendly TSV copy.
- Copy output must include headers.
- Ctrl/Cmd+C must trigger current table copy.
- Ctrl/Cmd+A should select/target the whole table where feasible.
- Copy buttons should write header-included whole-table TSV to the clipboard.
- CSV export and TSV copy should share the same export data hook.
- Existing input table drag/copy/paste/edit/navigation/undo behavior must not regress.
- Full Excel-style mouse drag range selection including headers is deferred.
- ResultPanel needs a short-term summary export/copy hook or equivalent alignment path.
- New table surfaces must not be added without satisfying this contract.

## Recovery Order

1. `194-d table copy UX recovery foundation`
   - Use export hooks for header-included TSV copy helper.
   - Add read-only result/trace copy button and Ctrl/Cmd+C alignment.
   - Preserve CSV export.
   - Exclude ResultPanel and input table changes.
2. `194-e ResultPanel summary export/copy alignment`
   - Add Hong Kong summary TSV/CSV-compatible data hook.
   - Keep current label-card rendering unless a later design changes it.
   - Exclude HSPF trace and graph.
3. `194-f MetricInputTable full-table copy enhancement`
   - Preserve existing edit/paste/drag behavior.
   - Add header-included whole input table copy.
   - Exclude read-only result/trace refactors.
4. Later
   - Hong Kong HSPF heating trace schema/implementation.
   - Bin graph parity with possible SPOT-style HTML export.
   - Multi/batch design.

## Excluded Scope

- No implementation changes.
- No source/test changes.
- No table copy implementation.
- No CSV export changes.
- No ResultPanel, MetricInputTable, or ExcelLikeTableController changes.
- No HSPF trace, graph, graph export, HTML export, BaseSection, or shared framework.
- No project log, memory seed, summary, archive, or lifecycle maintenance.

## Verification

- `python3 -B tools/check_code_structure.py`: OK.
- `git diff --check`: OK.
- `git status --short`: checked before commit.
- `git diff --name-only`: checked before commit.
- `git diff --stat`: checked before commit.

## Changed Files

- `docs/designs/2026-05-30-tkinter-excel-like-table-contract-recovery.md`
- `result_reports/active/194c_excel-like-table-contract-recovery.md`
- `docs/WORK_PLAN.md`

## Project Memory Delta

- none
