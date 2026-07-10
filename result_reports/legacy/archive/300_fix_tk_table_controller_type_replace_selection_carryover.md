# 300 Fix TkTableController Type-Replace Selection Carryover

## Goal

Resolve the issue where a subsequent typed character does not append to the first character because of macOS/Tk selection carryover behavior in `TkTableController`.

## Scope

- Modify `_type_replace` in `ui_tk/table/controller.py` to clear the selection on the focused widget after first-character replacement.
- Add regression tests in `tests/test_ui_tk_metric_input_table_controller_parity.py` to verify multi-key type-replace appending behavior.
- Ensure all existing controller and UI tests pass.

## Reproduction / Root Cause

- **Reproduction**: Click a cell, type `10` -> only `0` remains. Type `100` -> only `00` remains.
- **Root Cause**:
  - Cell click select runs `_show_selection_caret()`, which selects the entire Entry text (creating a widget selection range).
  - During first-key entry, `_type_replace()` replaces the value programmatically using `set_positions_batch()` and moves the insertion cursor to the end (`icursor("end")`), but it does not clear the selection.
  - On macOS/Tk, the selection persists globally, causing the subsequent native keypresses (e.g. `0`) to replace the first character rather than appending to it.

## Implementation

- Modified `ui_tk/table/controller.py` (`_type_replace` method):
  - After `set_positions_batch()` succeeds, added `widget.select_clear()` to explicitly release the text selection.
  - This ensures subsequent native keystrokes append to the cursor position instead of replacing the selected text.

## Tests

- Added `test_type_replace_clears_selection_for_multi_key_append` in `tests/test_ui_tk_metric_input_table_controller_parity.py`:
  - Selects cell `(0, 0)` and asserts selection is present.
  - Sends a fake event representing keypress `9` (different from default `1` to trigger mutation).
  - Asserts that value becomes `9`, `selection_present()` becomes `False`, and `icursor` position is at index 1.
  - Simulates subsequent `0` and `0` inputs at the insert cursor, commits, and asserts the final cell value is `900`.

## Validation

Focused regression tests passed successfully under macOS Aqua/Tk:
- `tests/test_ui_tk_metric_input_table_controller_parity.py`: 16 passed
- `tests/test_ui_tk_hong_kong_hspf_controller_switch.py`: 6 passed
- `tests/test_ui_tk_hong_kong_cspf_controller_switch.py`: 5 passed
- `py_compile` succeeded on `ui_tk/table/controller.py`.
- `check_code_structure.py` found no new violations.
- `git diff --check` passed cleanly.

## Manual GUI Smoke Required

The following manual verification must be run by the user:
- Run `python3 app_calculator_tk.py`
- Select the `Hong Kong HSPF` or `Hong Kong CSPF` profile.
- Click a cell, type `1`, `10`, or `100` and confirm the full text remains without the first characters getting overwritten.
- Verify undo (Ctrl+Z), paste, and clear functionality still work normally.

## Excluded Scope

- No changes to `HongKongHspfSection`, `HongKongCspfSection`, or other profile sections.
- No changes to `interaction_core.py` or `ResultPanel`.
- No controller switch expansion performed.

## Active Report Count

- 8 active reports present (below 10, lifecycle cleanup not needed).

## Next

- Post-type-replace selection fix GUI smoke.

## Commit / Push

- Implementation & test commit: `9358c8e`
- Active report commit & push: Pending final execution.
