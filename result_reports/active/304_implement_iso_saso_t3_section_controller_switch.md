# 304 Implement IsoSasoT3Section Controller Switch

## Goal

Migrate `IsoSasoT3Section` from the legacy `ExcelLikeTableController` to the common `TkTableController` + `interaction_core.py` foundation, verifying stable table interaction, paste, and undo behaviors.

## Scope

- Replace `ExcelLikeTableController` import and instantiation with `TkTableController` in `ui_tk/sections/iso_saso_t3_section.py`.
- Add focused regression tests verifying controller class, paste behaviors, baseline calculations, invalid values, optional 35 Min error rows, and undo behaviors.
- Ensure all tests pass under Xvfb/Tk.

## Target Structure

- **Section class**: `IsoSasoT3Section`
- **Input Matrix**: `self.input_table` (an instance of `MetricInputTable` which conforms to the `TkTableSurface` interface)
- **Controller**: `self.input_controller` (now instantiated as `TkTableController(self.input_table)`)
- **Output Surface**: `self.result_table` (an instance of `IsoSasoT3ResultTable` which is a custom Treeview comparison table)
- **Flicker/Undo Fixes**: Custom Treeview updates do not destroy labels, and inherit correct type-replace selection clearing and undo stacks.

## Implementation

- Modified `ui_tk/sections/iso_saso_t3_section.py`:
  - Replaced `from ui_tk.excel_like_table_controller import ExcelLikeTableController` with `from ui_tk.table.controller import TkTableController`.
  - Changed `self.input_controller = ExcelLikeTableController(self.input_table)` to `self.input_controller = TkTableController(self.input_table)`.

## Tests

- Created `tests/test_ui_tk_iso_saso_t3_controller_switch.py` with 7 focused tests:
  - `test_input_controller_is_tk_table_controller`: Asserts correct controller instantiation.
  - `test_paste_updates_input_editable_cell`: Simulates valid paste on an editable cell.
  - `test_paste_does_not_reject_invalid_text`: Simulates raw text paste without validation block at the controller paste layer.
  - `test_recalculate_now_after_valid_values`: Verifies baseline calculation runs correctly and populates Treeview rows.
  - `test_recalculate_blocks_on_invalid_required_value`: Verifies required calculation blocks and shows error when a required cell gets invalid text.
  - `test_recalculate_blocks_on_invalid_optional_value`: Verifies optional calculation produces an error row for optional while leaving the required row calculated when optional 35 Min receives invalid text.
  - `test_undo_restores_original_value`: Simulates invalid edit in edit-mode, commits, and triggers `ctrl._undo_last()` to verify rollback success.

## Validation

All focused regression tests passed successfully under macOS Aqua/Tk context:
- `tests/test_ui_tk_iso_saso_t3_controller_switch.py`: 7 passed
- `tests/test_ui_tk_iso_iseer_2point_controller_switch.py`: 6 passed
- `tests/test_ui_tk_hong_kong_hspf_controller_switch.py`: 6 passed
- `tests/test_ui_tk_hong_kong_cspf_controller_switch.py`: 5 passed
- `tests/test_ui_tk_metric_input_table_controller_parity.py`: 16 passed
- `py_compile` succeeded on `ui_tk/sections/iso_saso_t3_section.py`.
- `check_code_structure.py` found no new violations.
- `git diff --check` passed cleanly.

## Manual GUI Smoke Required

The following manual verification must be run by the user:
- Run `python3 app_calculator_tk.py`
- Select the `ISO / SASO T3` profile.
- Click a cell, type `1`, `10`, or `100` and confirm the full text remains without the first characters getting overwritten.
- Verify undo (Ctrl+Z), paste, and clear functionality still work normally.
- Confirm recalculation updates the custom result Treeview table correctly.
- Confirm optional 35 Min toggle behavior (3-point vs 4-point calculation) and detail panel.

## Excluded Scope

- No changes to `HongKongHspfSection`, `HongKongCspfSection`, or `IsoIseer2PointSection`.
- No changes to `IsoSasoT3ResultTable` or optional 35 Min toggle/state behavior.

## Active Report Count

- 12 active reports present (>10, lifecycle cleanup is pending).

## Lifecycle Maintenance Note

- **Pending**: Deferred to a follow-up lifecycle cleanup step after manual GUI smoke closeout is completed.

## Next

- Post-SASO T3 controller switch GUI smoke.

## Commit / Push

- Implementation & test commit: `8781a35`
- Active report commit & push: Committed and pushed to remote main branch.
