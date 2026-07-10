# 289 Narrow ResultPanel Focus Helper Exception Handling

## Goal

Narrow broad exception handling in ResultPanel focus preservation helpers to Tkinter boundary errors only.

## Scope

- `ui_tk/result_panel.py`: change `except Exception` to `except tk.TclError` in `_is_descendant_of_panel()` and `_restore_focus_if_alive()`.

## Excluded Scope

- No behavior change to focus preservation logic.
- No stable update path change.
- No controller switch expansion.
- No undo policy change.

## Cleanup Summary

### Before

```python
except Exception:
    pass
```

### After

```python
except tk.TclError:
    pass
```

Applied in:
- `_is_descendant_of_panel()`: widget parent-chain traversal may raise `tk.TclError` when a widget is destroyed during iteration.
- `_restore_focus_if_alive()`: `winfo_exists()` or `focus_set()` may raise `tk.TclError` if the widget is no longer valid.

## Validation

| Suite | Tests | Result |
|-------|-------|--------|
| Stable update | 13 | 13 passed, 0 skipped, 0 failures |
| Diagnostic | 10 | 10 passed, 0 skipped, 0 failures |
| **Total** | **23** | **23 passed, 0 skipped, 0 failures** |

| Check | Command | Result |
|-------|---------|--------|
| Compile result_panel | `py_compile ui_tk/result_panel.py` | OK |
| Structure guard | `python3 -B tools/check_code_structure.py` | No new violations |
| Git diff check | `git diff --check` | Clean |

## Manual Windows Smoke Still Required

Same as 288:

1. `python -m pytest tests/test_ui_tk_result_panel_stable_update.py -rs -vv`
2. `python -m pytest tests/test_ui_tk_controller_type_replace_flicker_diagnostic.py -rs -vv`
3. Run `calculator_tk`
4. Select Hong Kong CSPF profile
5. Confirm flicker-free numeric input
6. Enter invalid text; confirm error summary
7. Press Ctrl+Z; confirm original value restored
8. Confirm paste / clear / numeric undo / detail / profile-switch intact

## Next

- **Post-focus-preservation Windows smoke for invalid text undo.**
- Controller switch expansion remains blocked until Windows smoke passes.
- If invalid text undo persists, next slice is `TkTableController edit-session undo policy fix`.
