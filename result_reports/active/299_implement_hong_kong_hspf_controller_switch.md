# 299 Implement HongKongHspfSection Controller Switch

## Goal

Migrate `HongKongHspfSection` from the legacy `ExcelLikeTableController` to the common `TkTableController` + `interaction_core.py` foundation, ensuring stable table interactions, same-shape updates, and focus preservation.

## Scope

- Replace `ExcelLikeTableController` import and instantiation with `TkTableController` in `ui_tk/sections/hong_kong_hspf_section.py`.
- Add focused regression tests verifying controller switch, paste behaviors, baseline recalculations, invalid values, and edit-session undo behavior.
- Ensure all tests pass under Xvfb/Tk.

## Target Structure

- **Section class**: `HongKongHspfSection`
- **Input Matrix**: `self.input_table` (an instance of `MetricInputTable` which conforms to the `TkTableSurface` interface)
- **Controller**: `self.input_controller` (now instantiated as `TkTableController(self.input_table)`)
- **Flicker/Undo Fixes**: Inherits stable `ResultPanel` updates and external focus preservation directly via the existing `ResultPanel` integration.

## Implementation

- Modified `ui_tk/sections/hong_kong_hspf_section.py`:
  - Replaced `from ui_tk.excel_like_table_controller import ExcelLikeTableController` with `from ui_tk.table.controller import TkTableController`.
  - Changed `self.input_controller = ExcelLikeTableController(self.input_table)` to `self.input_controller = TkTableController(self.input_table)`.

## Tests

- Created `tests/test_ui_tk_hong_kong_hspf_controller_switch.py` with 6 focused tests:
  - `test_input_controller_is_tk_table_controller`: Asserts correct controller instantiation.
  - `test_paste_updates_input_editable_cell`: Simulates valid paste on an editable cell.
  - `test_paste_does_not_reject_invalid_text`: Simulates raw text paste without validation block at the controller paste layer.
  - `test_recalculate_now_after_valid_values`: Verifies baseline calculation runs correctly.
  - `test_recalculate_blocks_on_invalid_value`: Verifies calculation shows error status when invalid numeric cell text is parsed.
  - `test_undo_restores_original_value`: Simulates invalid edit in edit-mode, commits, and triggers `ctrl._undo_last()` to verify rollback success.

## Validation

All focused regression tests passed successfully under macOS Aqua/Tk context:
- `tests/test_ui_tk_hong_kong_hspf_controller_switch.py`: 6 passed
- `tests/test_ui_tk_hong_kong_cspf_controller_switch.py`: 5 passed
- `tests/test_ui_tk_metric_input_table_controller_parity.py`: 15 passed
- `tests/test_ui_tk_result_panel_stable_update.py`: 13 passed
- `py_compile` succeeded on `ui_tk/sections/hong_kong_hspf_section.py`.
- `check_code_structure.py` found no new violations.
- `git diff --check` passed cleanly.

## Manual GUI Smoke Required

The following manual verification must be run by the user:
- Run `python3 app_calculator_tk.py`
- Select the `Hong Kong HSPF` profile.
- Confirm numeric updates trigger calculations without flicker.
- Test valid copy-paste operations.
- Input invalid text (e.g. `abc`), confirm calculation block (error summary displayed), and verify Ctrl+Z restores the original value.
- Confirm detail panel toggle works, and switching profiles works cleanly.

## Excluded Scope

- No changes to `HongKongCspfSection`, `IsoIseer2PointSection`, or `IsoSasoT3Section`.
- No calculator core logic modifications.
- No changes to `TkTableController` itself or layout.

## Active Report Count

- 7 active reports present (below 10, lifecycle cleanup not needed).

## Next

- Post-HSPF controller switch GUI smoke.

## Commit / Push

- Implementation & test commit: `de94bce`
- Active report commit & push: Pending final execution.
