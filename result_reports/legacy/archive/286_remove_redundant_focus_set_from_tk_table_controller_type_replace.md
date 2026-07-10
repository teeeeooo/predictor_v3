# 286 Remove Redundant focus_set from TkTableController Type-Replace

## Goal

Remove the redundant `focus_set()` call in `TkTableController._type_replace()`
to mitigate the ResultPanel flicker observed in Hong Kong CSPF after the
controller switch pilot (284).

## Scope

- `ui_tk/table/controller.py`: remove one `focus_set()` call from
  `TkTableController._type_replace()`.
- `tests/test_ui_tk_controller_type_replace_flicker_diagnostic.py`: add
  regression test that `_type_replace` no longer calls `focus_set`.

## Excluded Scope

- No ResultPanel stable-update refactor.
- No controller switch expansion.
- No rollback.
- No changes to other controller methods (`_click`, `_navigate`, `_arrow`).

## 285 Diagnostic Link

285 identified the redundant `focus_set()` in `TkTableController._type_replace`
as the only behavioral difference that could explain why CSPF (TkTableController)
flickers while HSPF (ExcelLikeTableController) does not:

- Callback/render counts are identical between the two sections.
- ResultPanel full rebuild occurs in both.
- ExcelLikeTableController `_type_replace` does not call `focus_set()`.

## Fix Summary

In `ui_tk/table/controller.py`, `TkTableController._type_replace()`:

**Before:**
```python
if self.table.set_positions_batch({position: event.char}):
    self._mode = "edit"
    self._replace_pending = False
    self.table.focus_widget(position).focus_set()   # <-- removed
    widget = self.table.focus_widget(position)
    widget.icursor("end")
```

**After:**
```python
if self.table.set_positions_batch({position: event.char}):
    self._mode = "edit"
    self._replace_pending = False
    widget = self.table.focus_widget(position)
    widget.icursor("end")
```

The entry widget already has focus when the `<KeyPress>` binding fires.
Calling `focus_set()` again is unnecessary and on Windows appears to trigger
an extra focus/visual event that amplifies the ResultPanel rebuild flicker.

## Regression Tests

| Suite | Tests | Result |
|-------|-------|--------|
| Diagnostic (with new regression) | 9 | 9 passed, 0 skipped, 0 failures |
| Controller parity | 15 | 15 passed, 0 skipped, 0 failures |
| HongKongCspf pilot | 5 | 5 passed, 0 skipped, 0 failures |
| **Total** | **29** | **29 passed, 0 skipped, 0 failures** |

New regression test: `TestTypeReplaceDoesNotCallFocusSet`
- Monkeypatches the target entry widget's `focus_set` to count calls.
- Calls `_type_replace` with a fake key event.
- Asserts `focus_set` was called 0 times.
- Asserts value changed to typed char and controller entered edit mode
  (behavioral parity intact).

## Validation

| Check | Command | Result |
|-------|---------|--------|
| Diagnostic tests | `xvfb-run -a pytest tests/test_ui_tk_controller_type_replace_flicker_diagnostic.py -rs -vv` | 9 passed, 0 skipped, 0 failures |
| Parity tests | `xvfb-run -a pytest tests/test_ui_tk_metric_input_table_controller_parity.py -rs -vv` | 15 passed, 0 skipped, 0 failures |
| Pilot tests | `xvfb-run -a pytest tests/test_ui_tk_hong_kong_cspf_controller_switch.py -rs -vv` | 5 passed, 0 skipped, 0 failures |
| Compile controller | `py_compile ui_tk/table/controller.py` | OK |
| Structure guard | `python3 -B tools/check_code_structure.py` | No new violations |
| Git diff check | `git diff --check` | Clean |

## Manual Windows Smoke Required

Before marking this fix complete, the following must be verified on Windows:

1. `python -m pytest tests/test_ui_tk_controller_type_replace_flicker_diagnostic.py -rs -vv`
2. `python -m pytest tests/test_ui_tk_metric_input_table_controller_parity.py -rs -vv`
3. `python -m pytest tests/test_ui_tk_hong_kong_cspf_controller_switch.py -rs -vv`
4. Run `calculator_tk`
5. Select Hong Kong CSPF profile
6. Type digits one by one into the input table
7. Confirm ResultPanel no longer flickers
8. Confirm single-key replace-on-type still works
9. Confirm paste/invalid/undo/clear/detail/profile-switch behavior intact

## Next

- **Post-fix Windows smoke** for HongKongCspfSection flicker.
- If Windows smoke passes: proceed with controller switch expansion to
  remaining sections (`HongKongHspfSection`, `IsoIseer2pointSection`, `SasoT3Section`).
- If flicker persists: investigate `TkTableController._paint_selection` full-grid
  configure as secondary candidate.

## Risks

- Removing `focus_set()` might affect an edge case where the cell frame
  (not the entry) has focus and receives the `<KeyPress>` event. This is
  mitigated by existing focus handling in `_click` and `_navigate`.
- ResultPanel full rebuild remains a visual inefficiency; a stable-update
  redesign may be needed later for overall smoothness regardless of this fix.
