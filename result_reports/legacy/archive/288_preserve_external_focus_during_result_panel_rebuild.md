# 288 Preserve External Focus During ResultPanel Shape-Change Rebuild

## Goal

Preserve external widget focus during ResultPanel shape-change rebuild to mitigate the remaining invalid text undo UX issue after 287 stable update.

## Scope

- `ui_tk/result_panel.py`: add external focus capture/restore helpers to shape-change rebuild path.
- `tests/test_ui_tk_result_panel_stable_update.py`: 4 new focused tests for focus preservation.

## Excluded Scope

- No TkTableController undo policy change.
- No controller switch expansion.
- No rollback.
- No ResultPanel layout redesign.
- No clear/append/set_text behavior change beyond existing.

## Windows Smoke Context

After 287:
- ResultPanel flicker resolved.
- Numeric input / paste / clear / detail / profile switch OK.
- Remaining issue: invalid text undo does not behave as expected.
- Root cause hypothesis: shape-change rebuild destroys ResultPanel children, disturbing Windows Tk focus/event routing.

## Focus-Risk Path

- `set_summaries()` -> `_can_update_in_place()` False -> `_clear_summary_tables()` -> child.destroy()
- Invalid input causes status-only summary (fields=()) -> shape change -> full rebuild.
- `_clear_summary_tables()` destroys all `_summary_holder` children; this may shift Tk focus away from the input table entry.

## Focus Preservation Implementation

Added helpers:

- `_capture_external_focus()`: returns current focus widget if it is outside this ResultPanel.
- `_is_descendant_of_panel(widget)`: walks parent chain to detect panel membership.
- `_restore_focus_if_alive(widget)`: calls `focus_set()` only if widget still exists.

Applied only in `set_summaries()` shape-change `else` path:

```python
else:
    external_focus = self._capture_external_focus()
    self._clear_summary_tables()
    for row, summary in enumerate(summaries):
        self._render_summary_table(row, summary)
    if external_focus is not None:
        self._restore_focus_if_alive(external_focus)
```

Same-shape stable update path is untouched.

Direct `focus_set()` was chosen over `after_idle` because the rebuild is fully synchronous and immediate restore is simpler and more predictable.

## Tests

`tests/test_ui_tk_result_panel_stable_update.py` (4 new tests):

| Class | Test | What it verifies |
|-------|------|-----------------|
| TestFocusPreservation | test_external_focus_preserved_on_shape_change | External Entry focus stays after shape-change rebuild |
| TestFocusPreservation | test_same_shape_does_not_change_focus | Same-shape update does not move focus |
| TestFocusPreservation | test_internal_focus_not_restored_on_shape_change | Internal widget destroyed; focus not forced back |
| TestFocusPreservation | test_destroyed_external_focus_ignored | Destroyed external widget does not raise |

Headless note: tests use `deiconify()` + `focus_force()` + `update()`. If `focus_get()` is still None, the test skips with reason "Focus not available in this environment".

## Validation

| Suite | Tests | Result |
|-------|-------|--------|
| Stable update | 13 | 13 passed, 0 skipped, 0 failures |
| Diagnostic | 10 | 10 passed, 0 skipped, 0 failures |
| Parity | 15 | 15 passed, 0 skipped, 0 failures |
| Pilot | 5 | 5 passed, 0 skipped, 0 failures |
| **Total** | **43** | **43 passed, 0 skipped, 0 failures** |

| Check | Command | Result |
|-------|---------|--------|
| Compile result_panel | `py_compile ui_tk/result_panel.py` | OK |
| Structure guard | `python3 -B tools/check_code_structure.py` | No new violations |
| Git diff check | `git diff --check` | Clean |

## Manual Windows Smoke Required

Before marking this fix complete:

1. `python -m pytest tests/test_ui_tk_result_panel_stable_update.py -rs -vv`
2. `python -m pytest tests/test_ui_tk_controller_type_replace_flicker_diagnostic.py -rs -vv`
3. `python -m pytest tests/test_ui_tk_metric_input_table_controller_parity.py -rs -vv`
4. `python -m pytest tests/test_ui_tk_hong_kong_cspf_controller_switch.py -rs -vv`
5. Run `calculator_tk`
6. Select Hong Kong CSPF profile
7. Type digits one by one; confirm ResultPanel no longer flickers
8. Enter invalid text; confirm error summary appears
9. Press Ctrl+Z; confirm original value is restored
10. Confirm undo keeps the same cell editable
11. Confirm paste / clear / numeric undo / detail / profile-switch behavior intact

## Next

- **Post-focus-preservation Windows smoke for invalid text undo.**
- Controller switch expansion remains blocked until Windows smoke passes.
- If invalid text undo persists after this fix, next slice is `TkTableController edit-session undo policy fix`.
