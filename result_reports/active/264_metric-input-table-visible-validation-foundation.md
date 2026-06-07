# 264 MetricInputTable Visible Invalid-Field Validation Foundation

## Goal

Add visible invalid-cell marking foundation to `MetricInputTable` before paste
policy alignment. Invalid values can now be displayed to the user at the cell
level, preparing for future raw-text paste + visible validation + execution
blocking policy.

## Scope

- `ui_tk/metric_input_table.py`: invalid field state API + visual marking
- `ui_tk/layout_constants.py`: `TABLE_INVALID_BG` token
- `tests/test_ui_tk_metric_input_table_validation.py`: focused tests

## 263 Windows Closeout

Previous adapter slice (263) Windows check:

- `tests/test_ui_tk_metric_input_table_adapter.py`: **23 passed, 1 skipped**
- Skip reason: Python 3.14.5 Tcl/Tk runtime `init.tcl` environment issue, not
  adapter assertion failure.
- Main table manual behavior: **OK**
- Paste policy divergence remains: main (`ExcelLikeTableController` atomic
  reject) vs batch/common (`TkTableController` role-filter raw text).

## Implemented Invalid Field State API

### Storage and Query

| Method | Description |
|---|---|
| `set_invalid_fields(errors: Mapping[str, str])` | Mark fields invalid with messages. Unknown keys raise `KeyError`. |
| `clear_invalid_fields(fields: Iterable[str] \| None = None)` | Clear specific or all invalid fields. Unknown keys raise `KeyError`. |
| `invalid_fields() -> dict[str, str]` | Return copy of current invalid state. |
| `is_field_invalid(field_key: str) -> bool` | Query whether a field is invalid. |
| `invalid_message(field_key: str) -> str \| None` | Get invalid message for a field. |

### Visual Marking

| Method | Description |
|---|---|
| `_apply_field_visual_state(field_key: str)` | Set entry background to `TABLE_INVALID_BG` or `TABLE_EDITABLE_BG`. |
| `_apply_all_visual_states()` | Apply visual state to all editable entries. |

`set_invalid_fields()` and `clear_invalid_fields()` automatically call
`_apply_all_visual_states()` so visual state is always consistent with stored
state.

### `default_cell_background()` Update

`default_cell_background(position)` now returns `TABLE_INVALID_BG` for editable
cells whose field key is in the invalid state. This ensures future
`TkTableController` (which uses `default_cell_background()` as its base color)
will correctly display invalid cells.

Current `ExcelLikeTableController` does **not** call
`default_cell_background()` — it paints directly on `editable_entries` — so this
change has no effect on existing behavior.

### Layout Constant

- `TABLE_INVALID_BG = "#fee2e2"` added to `layout_constants.py`
- Light red, clearly distinct from white editable (`#ffffff`) and static gray
  (`#f1f3f5`) backgrounds.

## Behavior Preservation

- `ExcelLikeTableController` file: **unchanged**
- `validate_paste_matrix()`: **unchanged**
- `test_invalid_paste_is_rejected_without_partial_apply`: **preserved**
- Calculator section files: **unchanged**
- `MetricInputTable.get_numeric_values()`: **unchanged**
- `set_values_batch()` / `set_positions_batch()`: **do not auto-clear invalid state**
- Existing `MetricInputTable` public API: **unchanged**

## Tests

### New validation foundation tests

| Test Class | Tests | Result |
|---|---|---|
| `TestInvalidFieldStateStorage` | set/clear/query invalid state, unknown key errors | SKIPPED (headless) |
| `TestInvalidVisualMarking` | entry background changes, default_cell_background | SKIPPED (headless) |
| `TestInvalidStateDoesNotChangeExistingBehavior` | no auto-clear on set_values/set_positions, get_numeric_values still raises | SKIPPED (headless) |
| `TestInvalidStateWithReadOnlyCells` | read-only cells unaffected | SKIPPED (headless) |

All 18 tests skipped due to headless Tk unavailability. Windows GUI smoke remains
final verification.

### Regression tests

| Suite | Result |
|---|---|
| `test_ui_tk_excel_like_table_controller.py` | 3 passed, 27 skipped (identical) |
| `test_ui_tk_metric_input_table_adapter.py` | 24 skipped (identical) |
| `test_ui_tk_table_controller.py` | 7 passed (identical) |
| `test_ui_tk_table_interaction_core.py` | 11 passed (identical) |

Total: 21 passed, 51 skipped. Identical to before.

## Known Risk

- `metric_input_table.py` now exceeds 400 LOC (431). Next responsibility addition
  must trigger helper extraction, not file growth. This is acknowledged.

## Excluded Scope

- Paste policy alignment (next slice)
- Invalid paste rejection removal (next slice)
- Controller switch to `TkTableController` (future slice)
- Calculator section integration (caller responsibility)
- Field-schema validation engine (future slice)
- Batch matrix changes

## Next Suggested Action

**Main paste policy alignment** — remove atomic paste rejection from
`ExcelLikeTableController`, allow invalid values through to cells, use the new
invalid-field marking API to display errors, and block execution via
`get_numeric_values()` / status path.

## Project Memory Delta

- `MetricInputTable` now has explicit invalid-field state storage + visual
  marking foundation.
- Invalid state does **not** auto-clear on value changes; callers must explicitly
  clear via `clear_invalid_fields()`.
- `default_cell_background()` is now the canonical source for base cell
  background including invalid state, preparing for `TkTableController` paint
  integration.
- `ExcelLikeTableController` continues to paint directly on entries; invalid
  background integration will need explicit coordination during controller switch.
