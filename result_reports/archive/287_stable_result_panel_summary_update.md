# 287 Stable ResultPanel Summary Update

## Goal

Reduce ResultPanel flicker in Hong Kong CSPF after the controller switch
pilot by implementing stable in-place summary updates instead of full
widget destroy/recreate on every `set_summaries()` call.

## Scope

- `ui_tk/result_panel.py`: stable update implementation.
- `tests/test_ui_tk_result_panel_stable_update.py`: 9 new focused tests.
- `tests/test_ui_tk_controller_type_replace_flicker_diagnostic.py`: update
  ResultPanel rebuild diagnostic to reflect new behavior.

## Excluded Scope

- No controller switch expansion.
- No rollback.
- No `TkTableController` or `ExcelLikeTableController` changes.
- No section file changes.
- No invalid text undo fix (deferred to later follow-up).

## Windows Smoke Context

After 286 (removing redundant `focus_set()` from `TkTableController._type_replace`):

- Tests: diagnostic 8 passed / 1 skipped, parity 14 passed / 1 skipped, pilot 5 passed.
- Flicker still persisted.
- Numeric undo OK.
- Invalid text undo not working (deferred).

Conclusion: `focus_set()` was not sufficient root cause. The direct visual
mechanism is `ResultPanel.set_summaries()` full rebuild.

## Root Cause Reassessment

`ResultPanel.set_summaries()` previously called `_clear_summary_tables()`
which `destroy()`s all child widgets before creating new ones. This happens
even when the summary shape (title + field labels) is unchanged — e.g.,
when only numeric values change during auto-calculation after each keystroke.

## Stable Update Implementation

### Shape Detection

A "shape" is defined as `(title, tuple(field_label, ...))`. If two
summaries have the same title and same field labels in the same order,
they have the same shape.

### Update Path (same shape)

1. `_can_update_in_place()` compares stored shapes against new shapes.
2. If all summaries match: `_update_summary_values()` is called.
3. Value label `text` is updated via `label.configure(text=new_value)`.
4. Status label `text` is updated via `label.configure(text=new_status)`.
5. Copy text is still regenerated via `_set_copy_text()`.
6. **No widget destroy/create occurs.**

### Rebuild Path (shape changed)

If any summary title, field label, or field count changes, the old behavior
is preserved: `_clear_summary_tables()` + full `_render_summary_table()`.

### Data Structures Added

| Attribute | Type | Purpose |
|-----------|------|---------|
| `summary_value_labels` | `dict[str, tuple[tk.Label, ...]]` | References to value text labels for in-place update |
| `_summary_shapes` | `dict[str, tuple[str, tuple[str, ...]]]` | Stored shapes per summary title |

## Tests

`tests/test_ui_tk_result_panel_stable_update.py` (9 tests):

| Class | Tests | What they verify |
|-------|-------|-----------------|
| `TestStableUpdate` | 3 | Same shape keeps widget identity, updates value text, updates status text |
| `TestRebuildOnShapeChange` | 4 | Field label change, title change, field count change, status-only→fields trigger rebuild |
| `TestClear` | 1 | Clear resets state, next set_summaries rebuilds cleanly |
| `TestCopyText` | 1 | Copy text is updated even during stable in-place update |

Diagnostic test updated:
- `test_result_panel_rebuilds_children` → split into `test_same_shape_does_not_rebuild` and `test_shape_change_rebuilds`

## Validation

| Suite | Tests | Result |
|-------|-------|--------|
| Stable update | 9 | 9 passed, 0 skipped, 0 failures |
| Diagnostic | 10 | 10 passed, 0 skipped, 0 failures |
| Parity | 15 | 15 passed, 0 skipped, 0 failures |
| Pilot | 5 | 5 passed, 0 skipped, 0 failures |
| **Total** | **39** | **39 passed, 0 skipped, 0 failures** |

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
7. Type digits one by one into the input table
8. Confirm ResultPanel no longer flickers
9. Confirm single-key replace-on-type, paste, invalid, undo, clear, detail,
   profile-switch behavior intact

## Next

- **Post-stable-update Windows smoke** for HongKongCspfSection flicker.
- If Windows smoke passes: proceed with controller switch expansion to
  remaining sections.
- If flicker persists: investigate secondary candidates (e.g., `_paint_selection`
  full-grid configure vs editable-only configure).
- **Invalid text undo** remains a separate follow-up slice.

## Risks

- Stable update assumes field label order is stable. If a section reorders
  fields between calculations, the shape will change and a full rebuild will
  occur — correct behavior.
- `clear()` correctly resets all state so the next `set_summaries()` rebuilds.
- The `_show_text_mode()` path (used by `append()` and `set_text()`) still
  clears all summary tables before showing text — correct behavior.
