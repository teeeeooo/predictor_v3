# 242 Hong Kong CSPF Matrix Migration

## Goal

Migrate the Hong Kong CSPF batch dialog from the row-per-case `BatchCaseTable` surface to the two-row `BatchMatrixTable` surface while preserving the existing calculation handler and row-per-case code as fallback.

## Scope

- Connect `BatchMatrixTable` + `HONG_KONG_CSPF_MATRIX_SPEC` + `TkTableController` to the Hong Kong CSPF batch workflow.
- Reuse existing `HongKongCspfBatchHandler.calculate_row()` without modification.
- Preserve existing row-per-case code (`BatchCaseTable`, `BatchCalculationController`, `HONG_KONG_CSPF_BATCH_SPEC`) as fallback.
- Add focused migration tests.

## Non-Goals

- Copy-all / CSV export / xlsx export parity.
- EN/AHRI/KS profile expansion.
- Calculator core changes.
- Region config / profile registry / golden fixture changes.
- Existing row-per-case batch implementation deletion.
- BaseSection or large framework introduction.

## Migration Path

### Adapter: `HongKongCspfMatrixController`

- New class in `ui_tk/sections/hong_kong_cspf_batch_section.py`.
- Iterates `BatchMatrixTable.cases` (logical case dicts).
- Calls existing `HongKongCspfBatchHandler.calculate_row(case)` per logical case.
- Applies results via `BatchMatrixTable.set_result(logical_index, result.values)`.
- Returns `_MatrixCalculationSummary` with valid/blank/error counts.
- No Hong Kong-specific logic in `BatchMatrixTable` or `TkTableController`.

### Input Key Contract

- `HONG_KONG_CSPF_MATRIX_SPEC.input_keys` matches `HONG_KONG_CSPF_BATCH_SPEC.input_keys` exactly: `(declared_capacity, full_capacity, full_power, half_capacity, half_power)`.
- Matrix case dict is directly compatible with `HongKongCspfBatchHandler.calculate_row()` — no key mapping required.

### Result Mapping

- Handler returns `{CSPF: "...", CSEC: "..."}` per logical case.
- `BatchMatrixTable.set_result(logical_index, values)` stores results in the case dict.
- CSPF/CSEC display on first physical row (capacity row) via `MatrixCellKind.RESULT`.
- Second physical row (power row) result cells remain blank read-only via `MatrixCellKind.BLANK_READ_ONLY`.

## Dialog Integration

### Section: `HongKongCspfBatchSection`

- Replaced `BatchCaseTable` with `BatchMatrixTable`.
- Replaced `BatchCalculationController` with `HongKongCspfMatrixController`.
- Attached `TkTableController` as `interaction_controller` for Excel-like paste/copy/clear/undo.
- Buttons changed from "Add Row"/"Remove Row" to "Add Case"/"Remove Case".
- `add_case()` / `remove_case()` operate on logical case pairs (two physical rows each).
- Minimum one case preserved by `BatchMatrixTable.remove_case()`.
- `DebouncedAutoCalc` pattern preserved (150ms delay).

### Dialog: `HongKongCspfBatchDialog`

- Wraps the updated section in a `Toplevel`.
- `snapshot()` returns `list[dict[str, str]]` (converted from matrix tuple) for parent section compatibility.
- `restore_snapshot()` accepts both tuple and list formats.
- Close/reopen state persistence pattern preserved via parent section's `_batch_snapshot`.
- Window geometry, min size, centering behavior unchanged.

## MVC / SoC Boundary

| Responsibility | Owner |
|---|---|
| Matrix spec / cell mapping | `batch_matrix_models.py` |
| Matrix table Tk surface | `batch_matrix_table.py` |
| Excel-like interaction | `table/controller.py` (unchanged) |
| Profile-specific calculation | `hong_kong_cspf_batch_spec.py` (unchanged) |
| Matrix ↔ handler bridge | `hong_kong_cspf_batch_section.py` (`HongKongCspfMatrixController`) |
| Dialog / Toplevel ownership | `hong_kong_cspf_batch_section.py` (`HongKongCspfBatchDialog`) |
| Viewport / scroll | `batch_table_viewport.py` (reused, unchanged) |

## Tests

### New: `tests/test_ui_tk_hong_kong_cspf_matrix_migration.py` (14 tests)

- Adapter input/result key contract matches existing batch spec.
- Controller calculates each logical case independently.
- Controller result matches direct handler call (CSPF = 4.939).
- Blank cases produce blank results.
- Invalid input produces error state.
- Mixed valid/blank/error cases handled correctly.
- Result display text on first physical row only.
- Second-row Case/result cells are blank read-only.
- Add Case produces two physical rows.
- Remove Case preserves minimum one case.
- Editable cells are input cells only.
- Restore snapshot accepts list format.
- Existing handler contract preserved.

### Existing (all pass, no changes)

- `test_ui_tk_batch_matrix_models.py`: 9 passed
- `test_ui_tk_table_controller_per_cell_roles.py`: 4 passed
- `test_ui_tk_batch_matrix_table.py`: 1 skipped (Tk unavailable)
- `test_ui_tk_batch_table_controller.py`: 13 passed
- `test_ui_tk_hong_kong_cspf_batch_spec.py`: 5 passed

## Existing Behavior Regression Check

- `HongKongCspfBatchHandler.calculate_row()` unchanged — existing spec tests pass.
- `HONG_KONG_CSPF_BATCH_SPEC` unchanged — fallback code preserved.
- `BatchCaseTable` unchanged — importable for fallback recovery.
- `BatchCalculationController` unchanged — importable for fallback recovery.
- `HongKongCspfSection` (single-case) unchanged — dialog open/close pattern preserved.

## Manual Smoke Checklist (Windows)

- [ ] Hong Kong CSPF batch dialog opens from section button
- [ ] Two-row matrix layout displays (Capacity/Power per case)
- [ ] Case number shows on first row only, second row blank
- [ ] Result CSPF/CSEC shows on first row only, second row blank
- [ ] Add Case adds a two-row pair
- [ ] Remove Case removes a logical pair; minimum one case preserved
- [ ] Excel paste into capacity/power rows updates editable cells only
- [ ] Calculate produces correct CSPF/CSEC results
- [ ] Wheel scroll works over entry/label/header/cell frames
- [ ] Close/reopen preserves case data (snapshot persistence)
- [ ] Status bar shows valid/blank/error counts
- [ ] Copy selection produces rectangular TSV with blank second-row Case/result cells

## Excluded Scope

- Copy-all / CSV / xlsx export implementation.
- EN/AHRI/KS profile matrix migration.
- BaseSection or common batch framework.
- Existing row-per-case code deletion.
- Calculator core or golden fixture changes.

## Known Risks

- Tk GUI tests are skipped in headless Codespaces; Windows manual smoke is required.
- Snapshot format changed from flat row list to logical case tuple; parent section compatibility is maintained through list conversion in `dialog.snapshot()` and dual-format acceptance in `restore_snapshot()`.
- Old cached snapshots from the row-per-case format are key-compatible but structurally different (flat rows vs. matrix cases); close/reopen within the same session works correctly, but cross-version snapshot restoration is not guaranteed.

## Next Suggested Action

- Batch table copy-all + CSV export parity for the matrix surface.

## Project Memory Delta

- Hong Kong CSPF batch migration to two-row matrix surface is complete; row-per-case code preserved as fallback.
- `HongKongCspfMatrixController` is the adapter pattern for profile-specific matrix calculation bridging.
