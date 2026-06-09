# 302 Implement IsoIseer2PointSection Controller Switch

## Goal

Migrate `IsoIseer2PointSection` from the legacy `ExcelLikeTableController` to the common `TkTableController` + `interaction_core.py` foundation, verifying stable table interaction, paste, and undo behaviors.

## Scope

- Replace `ExcelLikeTableController` import and instantiation with `TkTableController` in `ui_tk/sections/iso_iseer_2point_section.py`.
- Add focused regression tests verifying controller class, paste behaviors, baseline calculations, invalid values, and undo behaviors.
- Ensure all tests pass under Xvfb/Tk.

## Target Structure

- **Section class**: `IsoIseer2PointSection`
- **Input Matrix**: `self.input_table` (an instance of `MetricInputTable` which conforms to the `TkTableSurface` interface)
- **Controller**: `self.input_controller` (now instantiated as `TkTableController(self.input_table)`)
- **Output Surface**: `self.result_table` (an instance of `IsoIseer2PointResultTable` which is a custom Treeview comparison table)
- **Flicker/Undo Fixes**: Treeview updates do not destroy labels, meaning result updating does not require stable update logic but inherits correct type-replace selection clearing and undo stacks.

## Implementation

- Modified `ui_tk/sections/iso_iseer_2point_section.py`:
  - Replaced `from ui_tk.excel_like_table_controller import ExcelLikeTableController` with `from ui_tk.table.controller import TkTableController`.
  - Changed `self.input_controller = ExcelLikeTableController(self.input_table)` to `self.input_controller = TkTableController(self.input_table)`.

## Tests

- Created `tests/test_ui_tk_iso_iseer_2point_controller_switch.py` with 6 focused tests:
  - `test_input_controller_is_tk_table_controller`: Asserts correct controller instantiation.
  - `test_paste_updates_input_editable_cell`: Simulates valid paste on an editable cell.
  - `test_paste_does_not_reject_invalid_text`: Simulates raw text paste without validation block at the controller paste layer.
  - `test_recalculate_now_after_valid_values`: Verifies baseline calculation runs correctly and populates Treeview rows.
  - `test_recalculate_blocks_on_invalid_value`: Verifies calculation shows error status when invalid numeric cell text is parsed.
  - `test_undo_restores_original_value`: Simulates invalid edit in edit-mode, commits, and triggers `ctrl._undo_last()` to verify rollback success.

## Validation

All focused regression tests passed successfully under macOS Aqua/Tk context:
- `tests/test_ui_tk_iso_iseer_2point_controller_switch.py`: 6 passed
- `tests/test_ui_tk_hong_kong_hspf_controller_switch.py`: 6 passed
- `tests/test_ui_tk_hong_kong_cspf_controller_switch.py`: 5 passed
- `tests/test_ui_tk_metric_input_table_controller_parity.py`: 16 passed
- `py_compile` succeeded on `ui_tk/sections/iso_iseer_2point_section.py`.
- `check_code_structure.py` found no new violations.
- `git diff --check` passed cleanly.

## Manual GUI Smoke Required

The following manual verification must be run by the user:
- Run `python3 app_calculator_tk.py`
- Select the `ISO / ISEER 2-point` profile.
- Click a cell, type `1`, `10`, or `100` and confirm the full text remains without the first characters getting overwritten.
- Verify undo (Ctrl+Z), paste, and clear functionality still work normally.
- Confirm recalculation updates the custom result Treeview table correctly.
- Confirm detail panel toggle works, and switching profiles works cleanly.

## Excluded Scope

- No changes to `HongKongHspfSection`, `HongKongCspfSection`, or `IsoSasoT3Section`.
- No changes to `IsoIseer2PointResultTable`.
- No controller switch for `IsoSasoT3Section` performed.

## Active Report Count

- 10 active reports present (below 10, lifecycle cleanup not needed).

## Next

- Post-2-point controller switch GUI smoke.

## Commit / Push

- Implementation & test commit: `c5c39a4`
- Active report commit & push: Committed and pushed to remote main branch.
