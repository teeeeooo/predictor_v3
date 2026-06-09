# 281 Controller Switch Parity Test Foundation

## Goal

Create focused tests that verify `MetricInputTable + TkTableController` behavior
parity before any production controller switch.

## Scope

- New test file: `tests/test_ui_tk_metric_input_table_controller_parity.py`
- 15 focused tests covering:
  - Controller attach and select/active/selected positions
  - Copy/paste behavior (clipboard roundtrip, raw text acceptance, editable-only)
  - Clear and undo (clear editable, undo restores)
  - Invalid visual state (background through surface)
  - Replace-on-type (single char, edit mode, undo)

## Excluded Scope

- No production code changes.
- No controller switch implementation.
- No section file changes.
- No map regeneration.

## Parity Contract (Task 1)

Tested behaviors that must not regress during switch:

1. Controller can attach to `MetricInputTable` without runtime error.
2. `select()` sets anchor/active correctly; `extend=True` preserves anchor.
3. `selected_positions()` returns correct cells for single and range selection.
4. `_copy()` puts selected cell values on the clipboard.
5. `_paste()` applies raw text to editable cells (does not reject invalid text
   at paste layer — per 265 policy).
6. Paste role-filtering ignores readonly cells.
7. `_clear()` clears only editable cells.
8. `_undo_last()` restores previous values after paste or clear.
9. `default_cell_background()` returns invalid color when
   `set_invalid_fields()` is called.
10. `_type_replace()` writes one typed character and enters edit mode;
    undo restores previous value.

## Tests Added (Tasks 2-5)

| Class | Tests | What they verify |
|-------|-------|-----------------|
| `TestAttachAndSelect` | 5 | Controller attach, select, extend, selected positions |
| `TestCopyPaste` | 4 | Copy to clipboard, paste raw text, no validation rejection, editable-only |
| `TestClearAndUndo` | 3 | Clear editable, undo after clear, undo after paste |
| `TestInvalidVisualState` | 2 | Invalid background via surface, clear restores editable background |
| `TestReplaceOnType` | 1 | Type char, edit mode, undo restores |

All tests use direct controller method calls (not event simulation) for
stability. Fake event object used only for `_type_replace`.

## Result (Task 6)

- **15 tests collected, 15 skipped, 0 failures**
- Skip reason: headless environment (`Tk not available: no display name and no
  $DISPLAY environment variable`)
- This matches the existing adapter/validation test skip pattern.
- Tests are structurally correct and will execute in a GUI environment.
- No production code changes needed.

## Validation (Task 7)

| Check | Command | Result |
|-------|---------|--------|
| Parity tests | `pytest tests/test_ui_tk_metric_input_table_controller_parity.py -rs -vv` | 15 skipped, 0 failures |
| Compile check | `py_compile tests/...controller_parity.py` | OK |
| Structure guard | `python3 -B tools/check_code_structure.py` | No new violations |
| Git diff check | `git diff --check` | Clean |

## Modified Files

- `tests/test_ui_tk_metric_input_table_controller_parity.py`

## Next

- **Controller switch pilot implementation** — but first run the same focused
  parity test command in a Windows/iMac GUI environment to confirm they pass
  before switching production controllers.
- If GUI parity tests pass: proceed with pilot section controller switch.
- If any parity test fails: stop and analyze the specific gap before switch.

## Risks

- Headless skip means real widget interaction is not verified in CI.
- Windows/iMac focused parity test run is required before switch.
- Replace-on-type test uses a fake event; real key event behavior may differ
  slightly (e.g., modifier state).

## Project Memory Delta

- Parity test foundation for controller switch is in place.
- 15 focused tests cover attach, select, copy, paste, clear, undo, invalid
  visual state, replace-on-type.
- No production code changes were needed.
- Next gate: GUI environment parity test confirmation.
