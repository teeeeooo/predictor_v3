# 219 — Common Tk Table Foundation First Slice

## Goal

Implement the first common Tk table foundation slice and move the Hong Kong
CSPF batch table onto it without migrating the existing calculator main matrix
tables yet.

The foundation is not batch-specific. It is the first shared Tk interaction
path intended to support:

- current calculator main matrix tables;
- current Hong Kong CSPF row-per-case batch table;
- future HSPF / EN14825 / AHRI / KS batch tables;
- future Tkinter table-shaped UI;
- later PySide / Web / WPF adapter planning through the toolkit-neutral
  interaction contract.

## File Placement Judgment

Placed new foundation modules under `ui_tk/table/`.

Reason:

- `ui_tk/` root already contains app composition, batch, existing table
  controllers, table grid experiments, result panel helpers, clipboard/export
  helpers, and geometry helpers.
- Adding more root-level `table_*` files would increase responsibility drift.
- `ui_tk/table/` makes the new boundary explicit: common Tk table interaction
  foundation, not Hong Kong/CSPF/batch-specific logic.

No table-external `ui_tk` cleanup was done in this slice.

## New Foundation Structure

New files:

- `ui_tk/table/__init__.py`
- `ui_tk/table/roles.py`
- `ui_tk/table/interaction_core.py`
- `ui_tk/table/surface.py`
- `ui_tk/table/controller.py`

### Tk-free Interaction Core

`ui_tk/table/interaction_core.py` owns pure helpers:

- TSV parse/encode;
- rectangular selection bounds;
- positions in bounds;
- copyable position filtering;
- paste target resolution;
- single-column multi-row paste;
- editable/read-only/result role filtering;
- Delete/Backspace clear target filtering;
- Tab / Shift+Tab / Enter / Shift+Enter navigation;
- arrow-key navigation;
- replace-on-type key classification;
- grouped `UndoStack`.

It imports no Tkinter, calculator, profile, region, Hong Kong, or CSPF code.

### Surface / Role Abstraction

`ui_tk/table/roles.py` defines:

- `CellRole.EDITABLE`
- `CellRole.RESULT`
- `CellRole.READONLY`
- `CellRole.HEADER`
- `CellRole.ROW_HEADER`
- `CellRole.DISABLED`

with small role policy helpers:

- `is_mutable()`
- `is_selectable()`
- `is_copyable()`

`ui_tk/table/surface.py` defines `TkTableSurface`, a small protocol for
surface adapters. The surface owns cells, values, snapshots, restore behavior,
clipboard access, and Tk widgets. The controller owns interaction.

### Tk-bound Controller

`ui_tk/table/controller.py` adds `TkTableController`.

Responsibilities:

- register/bind a table surface;
- rectangular selection;
- selection painting;
- focus/edit session lifecycle;
- Ctrl/Cmd+C TSV copy;
- Ctrl/Cmd+V TSV paste;
- Delete/Backspace clear;
- Ctrl/Cmd+Z grouped undo;
- Tab/Enter/arrow navigation;
- click-type replace;
- programmatic mutation guard;
- result/read-only cells selectable/copyable but not mutable.

The controller does not build cells and does not know calculator/profile logic.

## Batch Bridge / Migration

Modified:

- `ui_tk/batch_table.py`
- `ui_tk/batch_table_controller.py`
- `ui_tk/batch_case_table.py`

Changes:

- `batch_table.py` is now a compatibility export layer over `ui_tk.table`.
- `BatchTableController` is now a deprecated compatibility name wrapping
  `TkTableController`.
- `BatchCaseTable` implements the new surface API:
  - `cell_roles()`
  - `snapshot()`
  - `restore_snapshot()`
- `BatchCaseTable.restore_snapshot()` restores in place when row count matches,
  reducing unnecessary table rebuilds during undo.
- Row headers remain metadata/visual identity, not input columns.
- Result columns remain read-only/selectable/copyable and are skipped by
  paste/delete/type mutation paths.
- Batch auto-calc remains outside the foundation: input mutation notifies the
  existing section boundary, which schedules recalculation.

Unchanged calculation boundary:

- `BatchProfileSpec` / `BatchColumnSpec`
- `BatchCalculationController`
- `HongKongCspfBatchHandler`
- existing single-case CSPF core path

## Main Table Migration

Not migrated in this slice.

Reason:

- Current main calculator sections already use `MetricInputTable` +
  `ExcelLikeTableController` and have focused behavior tests.
- Migrating main and batch in the same slice would make Windows smoke failures
  harder to attribute.
- This slice builds the common boundary through the failing batch surface first.

Future main migration should adapt `MetricInputTable` to `TkTableSurface` or
extract a matrix adapter over the same controller.

## 216 NG Coverage

| 216 issue | Coverage in 219 |
| --- | --- |
| grouped undo was cell/position-like | Common `UndoStack`; controller tests cover grouped paste/clear and repeated Ctrl+Z without focus movement. |
| Case input column | Remains removed; row header behavior kept through batch spec tests. |
| single-column multi-row paste | Core and controller tests cover one Excel column pasted down multiple rows. |
| arrow navigation missing | Core and controller tests cover arrow navigation. |
| main lower blank space | Not directly changed; layout owner remains `Iso16358Tab` / app geometry. Windows smoke must confirm after batch foundation. |

## 214A / 03 Parity Evidence

| Item | Evidence |
| --- | --- |
| multi-cell rectangular selection | `TkTableController.selected_positions()` and controller fake-surface selection tests. |
| copy as TSV | `test_controller_copies_selectable_result_cells`. |
| paste from TSV | core parse/target tests and controller paste tests. |
| single-column multi-row paste | `test_paste_targets_support_single_column_multi_row_and_skip_result_cells`. |
| Delete/Backspace clear | `test_controller_clear_and_undo_are_grouped_and_active_cell_independent`. |
| grouped undo | controller paste/clear/replace tests. |
| Tab/Enter navigation | core navigation helper tests. |
| arrow-key navigation | core and controller navigation tests. |
| click/type replace-on-type | `test_controller_click_type_replace_then_repeated_undo_without_focus_move`. |
| read-only result cell copy | `test_controller_copies_selectable_result_cells`. |
| read-only result mutation prevention | paste/clear/type tests skip result cells. |
| row identity as row header | existing Hong Kong CSPF batch spec tests and unchanged `BatchCaseTable` row headers. |
| layout sizing acceptance | Not changed in this slice; Windows smoke required. |

## Tests Added / Updated

Added:

- `tests/test_ui_tk_table_interaction_core.py`
- `tests/test_ui_tk_table_controller.py`

Updated:

- `tests/test_ui_tk_batch_table_controller.py`

Behavior now covered:

- Tk-free core import does not load Tkinter;
- TSV parse/encode;
- single-column multi-row paste;
- MxN paste target filtering;
- paste skips result cells;
- copy includes result cells;
- clear only mutates editable cells;
- grouped undo for paste/clear;
- repeated Ctrl+Z without focus movement;
- click-type replace snapshot restore;
- navigation helpers and controller path;
- compatibility batch controller path.

## File Lifecycle / Cleanup Plan

New foundation files:

- `ui_tk/table/*`

Existing table files kept:

- `ui_tk/metric_input_table.py`
- `ui_tk/excel_like_table_controller.py`
- `ui_tk/table_grid.py`
- `ui_tk/table_grid_model.py`
- `ui_tk/table_clipboard.py`
- `ui_tk/table_csv_export.py`

Adapter / compatibility files:

- `ui_tk/batch_case_table.py` — first consumer surface adapter.
- `ui_tk/batch_table.py` — compatibility export layer.
- `ui_tk/batch_table_controller.py` — deprecated compatibility name.

Deprecated candidates after smoke and migration:

- `ui_tk/batch_table_controller.py`, once imports can use
  `ui_tk.table.controller.TkTableController` directly.
- batch-specific helper exports in `ui_tk/batch_table.py`, once all tests and
  consumers use `ui_tk.table.interaction_core`.
- `ui_tk/table_grid.py` / `ui_tk/table_grid_model.py`, if future audit shows
  they are unused or redundant with `ui_tk/table/`.

Table-external cleanup candidates:

- `ui_tk/sections/bin_detail_panel.py` is already over the structure checker
  soft LOC limit.
- result/detail/bin panels are growing and should stay separate from table
  foundation work.
- `ui_tk` root still has several table-related modules; cleanup should wait
  until Windows smoke and main migration clarify the final owner graph.

Cleanup trigger:

- common-foundation batch table passes Windows smoke;
- main table migration plan is accepted;
- import graph confirms old batch-specific controller/helpers are unused;
- root `ui_tk` table file sprawl blocks the next UI change.

No delete/rename/move cleanup was done here to keep the foundation slice small.

## Validation

- `python -m pytest -q tests/test_ui_tk_table_interaction_core.py` — passed.
- `python -m pytest -q tests/test_ui_tk_table_controller.py` — passed.
- `python -m pytest -q tests/test_ui_tk_batch_table_controller.py` — passed.
- `python -m pytest -q tests/test_ui_tk_hong_kong_cspf_batch_spec.py` — passed.
- `python -m pytest -q tests/test_ui_tk_batch_models.py` — passed.
- `python -m pytest -q tests/test_ui_tk_iso_table_autocalc.py` — passed with
  Tk-dependent skips in the headless environment.
- `python -m pytest -q tests/test_ui_tk_calculator_foundation.py` — passed with
  Tk-dependent skips in the headless environment.
- `python -m pytest -q tests/test_ui_tk_iso16358_helpers.py tests/test_ui_tk_profile_resolver.py` — passed.
- `python3 -B tools/check_code_structure.py` — passed with existing soft
  warning that `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `git diff --check` — passed.
- `git status --short` — reviewed before commit.

Not run:

- `python app_calculator_tk.py` — GUI smoke requires a display; `DISPLAY` is
  not set in the Codex environment.

## Windows Manual Smoke Needed

- Open Hong Kong CSPF batch dialog.
- Paste one Excel column into multiple rows.
- Paste MxN TSV across input and result columns; result columns must not mutate.
- Select/copy result cells.
- Delete/Backspace editable selection only.
- Ctrl+Z after paste and clear without moving focus.
- Repeated Ctrl+Z after click-type replace and paste.
- Arrow, Tab, Enter, shifted variants.
- Add/Remove Row keeps row headers and selection behavior sane.
- Confirm batch dialog sizing and main lower blank space.

## Excluded Scope

- No calculator core changes.
- No region config changes.
- No fixture/golden changes.
- No main matrix table migration.
- No HSPF / EN14825 / AHRI / KS batch profiles.
- No detail/bin schema, graph/export, or internal formula trace.
- No SPOT code copied/imported/vendored.
- No docs/designs changes.

## Next Action

Windows GUI smoke closeout for the common-foundation Hong Kong CSPF batch table.
