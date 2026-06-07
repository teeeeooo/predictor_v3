# 266 Correct 265 Paste-Policy Focused Tests

## Goal

Fix two 265 focused tests that had incorrect expectations for actual
Windows/Tk validation semantics before Windows validation closeout.

## Scope

- `tests/test_ui_tk_excel_like_table_controller.py`: correct
  `test_valid_paste_clears_previous_invalid_state` and
  `test_invalid_field_background_shown_in_paint`

## Corrected Tests

### `test_valid_paste_clears_previous_invalid_state`

**Problem:** `table.get_numeric_values()` was called outside `try/except`,
causing an unhandled `ValueError` that would abort the test on actual Tk.

**Fix:** Moved the first `get_numeric_values()` call inside `try/except` so the
invalid state is properly triggered and verified before the valid paste.

### `test_invalid_field_background_shown_in_paint`

**Problem:** After paste and validation, `controller.select((0, 1))` made the
invalid cell the **active** cell. In the paint hierarchy, active cells use
`TABLE_ACTIVE_BG`, which overrides the invalid base background. The test
expected `TABLE_INVALID_BG` for an active cell, which is incorrect.

**Fix:** Call `controller._clear_selection()` before checking backgrounds.
This removes active/selected overlays so the base background (invalid or
editable) is visible without hierarchy interference.

## Production Code Change

**None.** This is a test-only correction.

## Validation

| Suite | Result |
|---|---|
| `test_ui_tk_excel_like_table_controller.py` | 3 passed, 30 skipped |
| `test_ui_tk_metric_input_table_validation.py` | 18 skipped |
| `test_ui_tk_metric_input_table_adapter.py` | 24 skipped |
| `test_ui_tk_table_controller.py` | 7 passed |
| `test_ui_tk_table_interaction_core.py` | 11 passed |

Total: 21 passed, 75 skipped. Identical pure-helper pass rate.

## Windows/Tk Follow-up Checklist

- [ ] `tests/test_ui_tk_excel_like_table_controller.py -rs -vv` passes on Windows
- [ ] Mixed paste `10\tbad` applies raw text; undo restores original
- [ ] Invalid non-selected cell shows `TABLE_INVALID_BG` after validation
- [ ] Invalid active/selected cell shows `TABLE_ACTIVE_BG`/`TABLE_SELECTED_BG` (overlay correct)
- [ ] Valid correction clears invalid marking; calculation resumes

## Excluded Scope

- No paste policy rollback
- No production code changes
- No controller switch
- No batch/common changes

## Next

Windows validation closeout for 265, then controller switch preflight or
ui_tk folder cleanup.
