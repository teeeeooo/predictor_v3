# Tkinter Excel-Like Table Contract Recovery

## Background

The project UI rules treat table-shaped surfaces as spreadsheet-like by default. The current Tkinter app preserves that behavior for editable input grids, but result, trace, and summary surfaces evolved through separate read-only implementations.

This note restores the project-level table contract before adding more table, trace, graph, or export surfaces.

## Original Intent

Users should be able to treat every table-like surface as something that can be copied into Excel or another spreadsheet without manual cleanup. Editable input tables additionally support spreadsheet editing behavior.

The intent is not limited to input tables. Read-only result and trace tables must also be Excel-friendly for selection, copy, and export workflows.

## Current Mismatch

- `MetricInputTable` plus `ExcelLikeTableController` provides cell selection, drag selection, TSV copy/paste, delete/backspace clear, undo, and Tab/Enter navigation for editable inputs.
- ISO/ISEER, SASO, and Hong Kong CSPF result/trace tables are read-only display/export surfaces. They have `Treeview` rendering, Ctrl/Cmd+C bindings, and CSV export hooks, but the copy contract is not yet standardized across all table surfaces.
- `ResultPanel` renders Hong Kong CSPF/HSPF summary cards with labels, not a grid-like table surface. It has retained copy text, but no table-shaped export/copy hook.
- PyQt read-only table references were ported toward result/trace parity, but Tkinter selection/copy UX alignment for read-only tables was not made an explicit gate.
- The higher-level rule “all table-like surfaces provide Excel-friendly copy/export” was not explicit enough in the current Tkinter implementation slices.

This is a contract recovery issue, not a reason to blame prior slices. The fix is to make the cross-surface rule explicit and recover it incrementally.

## Table Surface Categories

- **Editable input table**: `MetricInputTable` with `ExcelLikeTableController`.
- **Read-only result comparison table**: ISO/ISEER and SASO comparison tables.
- **Read-only bin trace table**: `BinTraceTable` used for ISO/ISEER, SASO, and Hong Kong CSPF cooling traces.
- **ResultPanel summary surface**: Hong Kong CSPF/HSPF metric summary cards.
- **Future graph/table surfaces**: graph-adjacent data tables, diagnostics, or exported detail tables.

## Excel-Like Contract For All Tables

- Every table-like surface must provide Excel paste-friendly TSV copy.
- Copy output must include headers.
- Ctrl/Cmd+C must trigger the current table's copy action.
- Ctrl/Cmd+A should target the current table's whole data surface where feasible.
- A visible copy button should place header-included whole-table TSV on the clipboard.
- CSV export and TSV copy should share the same export data hook so headers, row order, and status handling stay aligned.
- Missing, invalid, or status-only states must copy/export safe user-facing strings, not raw dictionaries, `None`, tracebacks, or uncontrolled long floats.
- Treeview/Label implementation limits are acceptable if copy/export behavior preserves the spreadsheet workflow.
- Full Excel-style mouse drag range selection including headers is not required in the next slice.
- New table surfaces must not be added unless they define how they satisfy this contract.

## Input Table Behavior To Preserve

Editable input tables must not regress:

- Cell click and drag selection.
- TSV copy/paste.
- Numeric paste validation.
- Delete/backspace clear.
- Ctrl/Cmd+Z undo.
- Tab/Shift+Tab and Enter/Shift+Enter navigation.
- F2/double-click edit entry lifecycle.
- Existing selection-mode vs edit-mode behavior.

## Read-Only Result / Trace Requirements

Read-only result and trace tables must provide:

- Header-included whole-table TSV copy.
- Ctrl/Cmd+C support.
- A copy button or equivalent visible command.
- Shared `table_export_data()` or equivalent hook for CSV and TSV.
- Safe status-row copy/export when no rows are available.

Range editing, paste, delete, and undo are no-ops for read-only tables.

## ResultPanel Direction

Short term:

- Add `summary_export_data()` or an equivalent copy/export hook.
- Provide header/value/status TSV and CSV-compatible data for Hong Kong summary results.

Medium term:

- Consider replacing or supplementing label-card summaries with a table-like summary surface when repeated result values need spreadsheet workflows.

Not in this task:

- No `ResultPanel` implementation change.
- No migration away from the current summary card visual path.

## What Not To Implement Now

- No source changes in this audit/design slice.
- No full Excel-style header drag/range selection recovery.
- No graph, graph export, HTML export, or HSPF heating trace implementation.
- No BaseSection, presenter/controller, or shared result framework.

## Implementation Recovery Plan

1. `194-d table copy UX recovery foundation`
   - Add a TSV copy helper based on existing export data hooks.
   - Add header-included whole-table TSV copy to read-only result/trace tables.
   - Add copy buttons and Ctrl/Cmd+C behavior where missing.
   - Preserve existing CSV export.
   - Exclude ResultPanel, input table changes, graph, and HSPF trace.
2. `194-e ResultPanel summary export/copy alignment`
   - Add Hong Kong summary TSV/CSV-compatible hook.
   - Keep label-card rendering unless a separate design chooses replacement.
   - Exclude HSPF trace and graph.
3. `194-f MetricInputTable full-table copy enhancement`
   - Preserve existing edit/paste/drag selection behavior.
   - Add header-included whole-input-table copy where appropriate.
   - Exclude read-only table refactors.
4. Later slices
   - Hong Kong HSPF heating trace schema/design.
   - Bin graph parity and optional SPOT-style HTML export.
   - Multi/batch design.

## Acceptance Criteria

- Every table-like surface has an owner for TSV copy and CSV/export data.
- Read-only result/trace copy output includes headers and rows in visible order.
- CSV and TSV copy use the same data hook.
- Ctrl/Cmd+C works for the focused/current table surface.
- Copy button behavior is deterministic and header-included.
- Input table spreadsheet editing behavior remains unchanged.
- ResultPanel has an explicit short-term alignment path.
