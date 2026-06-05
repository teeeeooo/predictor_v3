# 218 — Common Tk Table Foundation Preflight

## Goal

Decide how `predictor_v3` should converge the calculator main tables and Hong
Kong CSPF batch table onto a common Tk table foundation before another
interaction patch is added.

This is report-only preflight. No UI code, tests, core logic, data, or
`docs/designs` files were changed.

## Checked Scope

- `result_reports/active/216_calculator-tk-batch-table-windows-smoke-follow-up.md`
- `result_reports/active/217_table-ux-target-and-example-evidence-update.md`
- `docs/WORK_PLAN.md`
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
- `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md`
- `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`
- `AGENT_TASK_ROUTER.md` UI/table route
- `ui_tk/metric_input_table.py`
- `ui_tk/excel_like_table_controller.py`
- `ui_tk/table_grid.py`
- `ui_tk/table_grid_model.py`
- `ui_tk/batch_table.py`
- `ui_tk/batch_table_controller.py`
- `ui_tk/batch_case_table.py`
- `ui_tk/batch_models.py`
- `ui_tk/batch_controller.py`
- `ui_tk/sections/hong_kong_cspf_batch_section.py`
- `ui_tk/sections/hong_kong_cspf_batch_spec.py`
- `ui_tk/tabs/iso16358_tab.py`
- `ui_tk/calculator_app.py`
- Relevant table/controller tests by heading search only
- SPOT via GitHub Connector: `README.md`, `ui/initial_values_table.py`,
  `ui/main_screen.py`

## Current Problem

216 fixed several batch table smoke gaps, but it did so inside a separate
batch controller path. The remaining risk is structural:

- main calculator tables use `MetricInputTable` + `ExcelLikeTableController`;
- batch uses `BatchCaseTable` + `BatchTableController`;
- older `TableGrid` / `TableGridModel` exists as another partial table path;
- table interaction helpers are duplicated across main and batch;
- Windows smoke is still needed to prove core interaction behaviors such as
  copy, paste, undo, replace-on-type, read-only result copy, and layout sizing.

## Desired Table UX Behavior

The completion target is the toolkit-neutral contract in
`03_SPREADSHEET_TABLE_UX_CONTRACT.md`, not a toolkit-specific implementation.

Required behavior:

- rectangular cell selection;
- TSV copy and paste;
- single-column multi-row paste from Excel;
- Delete / Backspace clear of editable selected cells;
- grouped undo for paste, clear, and edit operations;
- repeated Ctrl+Z follows the table undo stack, not the active cell or current
  column;
- Tab / Shift+Tab / Enter / Shift+Enter navigation;
- arrow-key navigation in selection mode;
- click-type replace-on-type;
- read-only result cells are selectable/copyable;
- read-only/result cells cannot be mutated by typing, paste, delete, or undo
  targets;
- row identity is row header metadata by default, not a calculation input
  column;
- table/dialog/main layout sizing does not enlarge the parent window or leave
  excessive blank space;
- calculator auto-calc batch keeps blank, partial, or invalid rows
  result-blank while valid rows continue to calculate independently.

## Current Main Table Analysis

### Strengths

- `MetricInputTable` already exposes rows, columns, editable cell frames,
  static cells, field order, and text values.
- `ExcelLikeTableController` owns rectangular selection, TSV copy/paste,
  grouped clear/undo, navigation, and replace-on-type for main calculator
  editable matrices.
- Multiple sections already reuse this pair: Hong Kong CSPF/HSPF,
  ISO/ISEER 2-point, and SASO T3.
- Focused tests exist for the main controller helpers and behavior.

### Gaps

- The controller is tied to editable metric matrices; result/read-only cells
  are not first-class selectable/copyable table cells in the same contract.
- The surface contract is implicit in `MetricInputTable` attributes rather
  than a reusable table surface interface.
- It does not directly support row-per-case batch with result columns.
- Numeric paste is intentionally atomic for the current auto-calc matrix
  surface, which is not the same policy as calculator batch's partial-row
  result-blank behavior.
- `TableGrid` / `TableGridModel` is a separate partial foundation but is not
  the active main calculator surface.

### Decision

Do not migrate main first. Main is stable enough to remain as the compatibility
target while the common foundation is extracted around shared interaction
semantics. Main migration should happen after the batch surface proves the
foundation can support result/read-only roles and row headers.

## Current Batch Table Analysis

### Strengths

- `BatchProfileSpec` / `BatchColumnSpec` already separates input/result/status
  column roles from Hong Kong-specific calculation.
- `BatchCalculationController` and `HongKongCspfBatchHandler` keep calculation
  outside the table interaction surface.
- Batch auto-calc is separate from the table controller.
- 216 removed the visible Case input column and added row headers.

### Gaps

- `BatchTableController` duplicates interaction logic from
  `ExcelLikeTableController` instead of sharing an interaction core.
- Undo snapshots use whole-row text restore through `set_text_rows()`, which
  rebuilds the table and can disturb focus, selection, bindings, and edit
  sessions.
- The controller has less explicit programmatic mutation guarding than the
  desired behavior needs.
- Result cells are labels/frames rather than a proven selectable/copyable
  cell role across Windows smoke.
- Paste helpers were fixed, but helper behavior and real Tk-bound controller
  behavior remain separate risk surfaces.
- Layout sizing was minimally capped in `Iso16358Tab`, not solved by a common
  table/dialog sizing policy.

### Decision

Treat current `BatchTableController` as an interim implementation to be
absorbed. Continue patching it only for blocking hotfixes; the next normal
implementation should introduce common table interaction foundation and move
batch onto it.

## SPOT Example/Evidence

SPOT was checked through the GitHub Connector only. It is not source of truth,
not a dependency, not a vendor target, and not a copy target.

Useful behavior evidence:

- README describes an initial-values table workflow with Excel paste, undo,
  Enter, and Tab style editing.
- `ui/initial_values_table.py` shows a concrete Tkinter table interaction
  layer with Tk-free pure helpers for clipboard parsing, paste target
  resolution, navigation resolution, key classification, and replace-on-type.
- The Tk-bound controller registers existing cells instead of building all
  widgets itself.
- It uses edit-session snapshots, a programmatic mutation guard, grouped undo
  snapshots, and focus re-anchoring after paste/undo/delete.
- `ui/main_screen.py` shows the table behavior inside a real main UI surface,
  not only a standalone demo.

Do not copy:

- SPOT's project-specific naming, Excel/COM workflow, global state, visual
  tokens, message text, or file structure.
- SPOT's exact implementation. Use it only as evidence for behavior and as a
  design hint for separating pure helpers from Tk-bound registration.

## Common Tk Table Foundation Proposal

### Module Candidates

- `ui_tk/table_interaction_core.py`
  - Tk-free pure helpers and state policies.
- `ui_tk/tk_table_surface.py`
  - Surface protocols and cell metadata dataclasses.
- `ui_tk/tk_table_controller.py`
  - Tk-bound controller that registers a surface and owns user interaction.
- Keep existing `ui_tk/metric_input_table.py` and `ui_tk/batch_case_table.py`
  as surface adapters until migrated.

Names can change in implementation, but the boundary should not.

### Tk-Free Core Responsibilities

- clipboard parse / encode;
- rectangular selection bounds;
- paste target resolution, including single-column multi-row paste;
- editable/read-only/disabled role filtering;
- navigation resolution for Tab, Enter, shifted variants, and arrows;
- key classification and replace-on-type eligibility;
- edit snapshot and undo stack policy;
- mutation grouping for paste, clear, edit, and restore;
- result/read-only mutation prevention rules.

### Tk-Bound Controller Responsibilities

- cell registration through surface metadata;
- selection painting;
- focus and edit-session lifecycle;
- copy / paste / delete / undo / replace / navigation bindings;
- programmatic mutation guard;
- in-place snapshot restore when possible;
- controller-level callbacks for value changes and recalculation scheduling;
- no calculator/profile/region logic.

### Surface Adapter Responsibilities

- Main matrix adapter:
  - exposes current `MetricInputTable` rows, columns, editable/static roles,
    values, and mutation hooks.
- Batch row-per-case adapter:
  - exposes input/result roles, row headers, dynamic row add/remove, and result
    update hooks.
- Result/read-only role support:
  - selectable/copyable;
  - excluded from edit/paste/delete mutation paths.
- Layout:
  - table exposes requested rows/columns/density hints;
  - app/dialog owner decides geometry and scroll behavior.

### Calculation Boundary

The foundation must not know Hong Kong, CSPF, HSPF, profile IDs, dispatcher
objects, or calculator formulas. Batch auto-calc remains a callback boundary:

1. table input mutation emits a grouped changed event;
2. batch section schedules recalculation;
3. handler maps row input to existing calculator core path;
4. table surface receives result-column text updates through result hooks.

## Migration Options

| Option | Decision | Reason |
| --- | --- | --- |
| A. Batch first on common foundation, main later | Recommended | Solves the failing surface first while avoiding regression in stable main tables. |
| B. Main first, batch later | Not recommended | High regression risk in currently working calculator flows before fixing the failing batch surface. |
| C. Skeleton plus simultaneous main/batch partial conversion | Backup only | Good for architecture, but larger blast radius and harder Windows smoke attribution. |
| D. Keep patching `BatchTableController` | Reject | Repeats the same independent-controller pattern that caused the gap. |
| E. Defer foundation and patch only five smoke bugs | Reject | Faster locally but leaves the next table-shaped UI exposed to the same failure mode. |

Recommended direction: Option A with a small foundation-first implementation
slice. Build the shared core/controller boundary, migrate batch first, and
defer main migration until the foundation is proven by focused tests and
Windows smoke.

## 219 First Implementation Slice

Suggested task name:

`219 — common Tk table foundation first slice`

### Candidate Files

New:

- `ui_tk/table_interaction_core.py`
- `ui_tk/tk_table_surface.py`
- `ui_tk/tk_table_controller.py`
- `tests/test_ui_tk_table_interaction_core.py`
- `tests/test_ui_tk_tk_table_controller.py`
- `result_reports/active/219_common-tk-table-foundation-first-slice.md`

Modify:

- `ui_tk/batch_case_table.py`
- `ui_tk/batch_table_controller.py` or replace/deprecate it
- `ui_tk/batch_table.py` if its protocol is absorbed by the new surface
- `ui_tk/sections/hong_kong_cspf_batch_section.py`
- `tests/test_ui_tk_batch_table_controller.py`
- `tests/test_ui_tk_hong_kong_cspf_batch_spec.py`
- `docs/WORK_PLAN.md` only if next actions change

Do not modify in 219:

- calculator core;
- region configs;
- fixture/golden expected;
- HSPF/EN/AHRI/KS batch;
- detail/bin schema;
- graph/export;
- SPOT/vendor files;
- main `MetricInputTable` behavior except compatibility read-only adapters if
  needed for tests.

### Include In First Slice

- Tk-free clipboard parse/encode and paste target resolution;
- selection bounds and editable/read-only role filtering;
- navigation helper for Tab/Enter/arrows;
- undo stack policy for grouped paste/clear/edit/restore;
- programmatic mutation guard;
- a Tk-bound controller that can register a row-per-case batch surface;
- result/read-only cells selectable/copyable but not mutable;
- batch auto-calc callback remains outside the controller;
- batch table uses row headers, not Case input column;
- controller-level parity tests for the 216 smoke gaps.

### Exclude From First Slice

- main calculator table migration;
- PySide/WPF adapters;
- import/export/graph/detail features;
- full visual redesign;
- HSPF/EN/AHRI/KS batch profiles.

### Focused Test Candidates

- parse/encode TSV;
- single-column multi-row paste targets;
- paste expands dynamic rows only through surface adapter policy;
- paste skips read-only result cells;
- copy includes selectable result cells;
- Delete/Backspace clear editable cells only;
- grouped undo for paste and clear independent of active cell;
- edit-session snapshot restore after click-type replace;
- Tab/Enter/arrow navigation helpers;
- programmatic mutation does not create extra undo groups;
- valid Hong Kong CSPF batch row still equals single-case core path.

### Manual Windows Smoke Candidates

- Excel TSV paste: one column/many rows and multi-column/many rows;
- Ctrl+Z repeated after typing, paste, clear, and after moving focus;
- arrow, Tab, Enter, shifted variants;
- click-type replace;
- result cell selection/copy and mutation prevention;
- Add/Remove Row keeps row headers and selection sane;
- dialog and main window sizing.

## Verification Plan For 219

Automatic tests should prove core interaction behavior through pure helper and
controller/surface fakes before Windows smoke. GUI smoke remains final platform
confirmation, not the first place core paste/undo/navigation bugs are found.

Do not rely on fragile OS keyboard event tests for every behavior; use fake
surface/controller-level tests for core semantics and a compact Windows smoke
check for actual Tk focus/selection behavior.

## Excluded Scope

- No code changes in this report.
- No tests were added or modified.
- No SPOT code copied/imported/vendored.
- No result report lifecycle/archive maintenance.

## Next Action

Common Tk table foundation first slice.

## Validation

- `git diff --check` — passed.
- `python3 -B tools/check_code_structure.py` — passed with the existing soft
  warning that `ui_tk/sections/bin_detail_panel.py` exceeds the 400 LOC soft
  limit.
- `git status --short` — reviewed before commit.

Not run:

- `pytest` — preflight/report-only task; no code or tests changed.
- GUI smoke — no UI code changed.
