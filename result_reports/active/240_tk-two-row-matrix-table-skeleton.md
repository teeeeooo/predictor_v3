# 240 Tk Two-Row Matrix Table Skeleton

## Goal

Implement a minimal but functional Tk two-row matrix table surface as the third slice of the batch two-row matrix foundation, on top of existing BatchMatrixSpec and per-cell role controller compatibility.

## Scope

- New surface: `ui_tk/batch_matrix_table.py`
- Reuse existing `BatchTableViewport` for scroll containment.
- Reuse existing `TkTableController` for Excel-like interaction (no controller fork).
- Per-cell role resolution via `cell_role(position)`.
- Fixed columns: Case, Row Type; measurement points and result metrics from `BatchMatrixSpec`.
- One logical case renders two physical rows.
- Case and result values appear only on the first physical row; second physical row uses real blank read-only cells.
- Editable input cells use Entry; read-only/static cells use Label.
- `add_case` / `remove_case` operate on logical cases with a minimum-one-case guard.
- `snapshot` / `restore_snapshot` are logical-case based.
- Tests: `tests/test_ui_tk_batch_matrix_table.py` (headless contract + controller integration where Tk is available).

## Non-goals

- No connection to existing Hong Kong CSPF batch dialog/section/spec/handler.
- No calculation adapter.
- No copy-all / CSV export / xlsx export / export data contract.
- No BaseSection or large framework.
- No change to existing row-per-case batch behavior.

## Created Skeleton / Surface

- `ui_tk/batch_matrix_table.py`
  - `BatchMatrixTable(ttk.Frame)` implements the TkTableSurface contract.
  - Uses `BatchMatrixSpec` for semantic mapping (cell kind, input/result keys, display text).
  - Wraps content in `BatchTableViewport` for vertical scroll.
  - `_rebuild_table` creates a real widget grid: header row + physical rows per logical case.
  - `cell_role(position)` maps `MatrixCellKind` → `CellRole` (EDITABLE, DISABLED, RESULT, READONLY).
  - `set_positions_batch` mutates only editable input cells, updates StringVars, and notifies.
  - `set_result` / `clear_results` update result metric labels per logical case.

## MVC / SoC Boundary

- **Model / Spec**: `batch_matrix_models.py` owns logical-case structure, cell descriptors, and display text.
- **View / Surface**: `batch_matrix_table.py` owns Tk widget grid, viewport containment, and variable lifecycle.
- **Controller**: `table/controller.py` `TkTableController` owns selection, copy/paste TSV, clear, undo, and navigation.
- No controller fork; the existing `cell_role(position)` hook is sufficient.

## No-merge / Blank Read-only Behavior

- No merged cells, no fake-merged cells, no rowspan/overlay/widget spanning.
- Every visible grid position has a real widget with a real address.
- Second physical row Case cell is a real blank Label (blank_read_only).
- Second physical row result cells are real blank Labels.
- Not-applicable cells are disabled Labels skipped by edit/paste/clear paths.

## Controller Integration

- `TkTableController(table)` attaches to `BatchMatrixTable` and works without modification.
- Paste and clear are filtered by `cell_role(position)`; only EDITABLE cells mutate.
- Copy preserves physical rectangular TSV shape, including blank second-row Case/result cells.
- Undo is grouped per user action.

## Tests

- `tests/test_ui_tk_batch_matrix_table.py`
  - Construction, row/column count, case/row_type/result display, not-applicable non-editable, cell_role mapping.
  - Controller paste, clear, copy with real surface.
  - add_case / remove_case with minimum-one guard.
  - snapshot/restore logical-case behavior.
- Tk unavailable in this Codespaces environment → tests skip gracefully (`pytest.importorskip` + `TclError` guard).
- Existing tests remain passing:
  - `test_ui_tk_batch_matrix_models.py`: 9 passed
  - `test_ui_tk_table_controller_per_cell_roles.py`: 4 passed
  - `test_ui_tk_batch_table_controller.py`: 13 passed
  - `test_ui_tk_hong_kong_cspf_batch_spec.py`: 5 passed

## Existing Behavior Regression Check

- No changes to `ui_tk/batch_case_table.py`, `ui_tk/batch_table_viewport.py`, calculator core, region config, profile registry, golden fixtures, or existing expected values.
- `python3 -B tools/check_code_structure.py` passes (only pre-existing `bin_detail_panel.py` 400 LOC warning).
- `git diff --check` clean.

## Known Risks

- Tk skeleton tests are skipped in headless environments; Windows/manual GUI smoke is still needed for visual layout verification.
- `set_result` updates result StringVars but does not trigger recalculation; that belongs to the future adapter slice.
- `add_case` scrolls to bottom unconditionally; future dialog integration may need scroll-to-new-case only when already at bottom.

## Next Suggested Action

- **Hong Kong CSPF matrix migration**: connect `BatchMatrixTable` to the existing Hong Kong CSPF batch handler/dialog behind a feature flag or explicit migration path.
- Add focused Windows GUI smoke for two-row matrix paste/clear/undo parity before treating the surface as stable.

## Project Memory Delta

- Two-row matrix Tk surface is now real and testable; future table-heavy work should prefer this foundation over ad-hoc Entry grids.
- `BatchMatrixSpec` + `cell_role(position)` + `TkTableController` pattern is confirmed as the standard integration path for matrix tables.
