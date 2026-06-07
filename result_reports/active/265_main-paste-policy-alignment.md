# 265 Main Paste Policy Alignment with Visible Numeric Validation

## Goal

Align main `MetricInputTable + ExcelLikeTableController` paste policy with the
common table UX contract: allow raw text paste, mark invalid fields visibly,
block calculation execution.

## Scope

- `ui_tk/metric_input_table.py`: update `get_numeric_values()` to validate all
  fields and manage visible invalid state
- `ui_tk/excel_like_table_controller.py`: remove atomic paste pre-validation,
  add invalid background awareness to selection painting
- Test updates for new paste behavior

## Previous State

- `ExcelLikeTableController._paste()` called `validate_paste_matrix()` before
  applying any values. If any pasted cell was non-numeric, the entire paste was
  silently rejected.
- `MetricInputTable.get_numeric_values()` raised `ValueError` on the first
  invalid field without marking which field was wrong.
- No per-cell visual invalid state existed before 264.

## 263 Windows Closeout

- `tests/test_ui_tk_metric_input_table_adapter.py`: **23 passed, 1 skipped**
- Skip reason: Python 3.14.5 Tcl/Tk `init.tcl` environment issue.
- No adapter assertion failure observed.
- Main table manual behavior: **OK**.

## Implemented Paste Policy Change

### `ExcelLikeTableController._paste()`

Removed `validate_paste_matrix(matrix)` pre-check. Paste now:
1. Parses clipboard TSV
2. Resolves paste targets
3. Applies raw text to editable cells
4. Records one undo group
5. Notifies callback once

Invalid values are no longer rejected at the paste layer.

### `ExcelLikeTableController._paint_selection()`

Added `_base_background_for_field()` which checks `table.is_field_invalid()`.
If a field is invalid, the base color is `TABLE_INVALID_BG` instead of
`TABLE_EDITABLE_BG`. Selection/active overlays still take precedence.

This preserves the existing selection visual hierarchy:
- Active cell: `TABLE_ACTIVE_BG`
- Selected cell: `TABLE_SELECTED_BG`
- Invalid cell (not selected): `TABLE_INVALID_BG`
- Valid cell (not selected): `TABLE_EDITABLE_BG`

## Implemented Numeric Validation / Invalid Marking Flow

### `MetricInputTable.get_numeric_values()`

Updated behavior:
1. Calls `clear_invalid_fields()` to reset previous invalid state
2. Iterates all editable fields
3. Tries `parse_numeric_cell()` on each value
4. Collects all invalid fields with message `"숫자 입력 필요"`
5. If any invalid: calls `set_invalid_fields(invalid)`, raises `ValueError`
6. If all valid: returns numeric dict (clear already done in step 1)

### Caller Integration

Calculator sections (`iso_iseer_2point_section.py`,
`hong_kong_cspf_section.py`, `iso_saso_t3_section.py`,
`hong_kong_hspf_section.py`) already catch `ValueError` from
`get_numeric_values()` in `recalculate_now()`.

No section code changes were required. The existing generic status message
(`"입력 오류: 숫자 입력을 확인하세요."`) is now paired with red cell backgrounds
that show exactly which fields are invalid.

### Invalid Clear on Correction

When the user edits an invalid cell to a valid value, the next auto-calc
(triggered by `DebouncedAutoCalc`) calls `get_numeric_values()`, which:
1. Clears all invalid state
2. Re-validates all fields
3. Only re-marks still-invalid fields

This means fixing one cell automatically clears its invalid marking.

## Status / Execution Blocking

Invalid state now blocks execution at two levels:
1. **Visual**: red cell backgrounds show which fields need attention
2. **Functional**: `get_numeric_values()` raises before calculator core is called

The section's `ValueError` catch displays a status message. Red cells + status
message together prevent silent errors.

## Tests

### Updated tests

| Test | Description | Result |
|---|---|---|
| `test_invalid_paste_is_rejected_without_partial_apply` | Now expects paste applies raw text, undo restores, callback fires once | SKIPPED (headless) |
| `test_invalid_paste_marks_invalid_fields_on_validation` | Paste applies; `get_numeric_values()` marks invalid | SKIPPED (headless) |
| `test_valid_paste_clears_previous_invalid_state` | Valid paste updates value; next validation succeeds and clears | SKIPPED (headless) |
| `test_invalid_field_background_shown_in_paint` | Invalid cell shows `TABLE_INVALID_BG` after validation | SKIPPED (headless) |

### New validation tests

| Test | Description | Result |
|---|---|---|
| `test_get_numeric_values_marks_invalid_fields` | Multiple invalid fields all marked | SKIPPED (headless) |
| `test_get_numeric_values_clears_previous_invalid_for_valid` | Valid value clears previous invalid state | SKIPPED (headless) |
| `test_get_numeric_values_clears_all_then_remarks_on_revalidation` | Clear all, then remark only still-invalid | SKIPPED (headless) |

### Regression tests

| Suite | Result |
|---|---|
| `test_ui_tk_excel_like_table_controller.py` | 3 passed, 30 skipped (pure helpers unchanged) |
| `test_ui_tk_metric_input_table_validation.py` | 18 skipped |
| `test_ui_tk_metric_input_table_adapter.py` | 24 skipped |
| `test_ui_tk_table_controller.py` | 7 passed |
| `test_ui_tk_table_interaction_core.py` | 11 passed |

Total: 21 passed, 75 skipped. Identical pure-helper pass rate.

## Excluded Scope

- Controller switch to `TkTableController` (future slice)
- Batch/common table behavior changes
- ML field-schema validation engine
- Categorical/text/required/range validation
- Calculator core changes
- Section status message improvements (could be enhanced in follow-up)
- `validate_paste_matrix()` function cleanup (function kept for test compatibility)

## Risks

- `metric_input_table.py` (445 LOC) and `excel_like_table_controller.py` (401 LOC)
  now exceed the 400 LOC soft limit. Next addition must trigger helper extraction.
- `get_numeric_values()` now has side effects (widget background changes). This
  is appropriate since it's called from the Tk event loop, but tests that mock
  the table without Tk widgets would need stubs for `clear_invalid_fields()`
  and `set_invalid_fields()`.
- Selection painting now queries `is_field_invalid()` on every paint. For large
  tables this is O(n) per paint where n = editable cells. Main calculator tables
  are small (typically 4-14 editable cells), so this is acceptable.

## Next Suggested Action

**Main table controller switch preflight** — evaluate whether
`ExcelLikeTableController` can now be replaced by `TkTableController` given that
`MetricInputTable` implements `TkTableSurface` and handles invalid visual state.

Alternative: **ui_tk folder cleanup** — extract helpers from the now-soft-limit
exceeded files before further growth.

## Project Memory Delta

- Calculator main table paste policy now aligns with common UX contract:
  raw-text paste, per-cell visible invalid marking, execution blocking.
- `get_numeric_values()` is the owner for numeric validation + visible marking +
  execution blocking for main calculator tables.
- `ExcelLikeTableController._paint_selection()` queries `is_field_invalid()`
  for base background, enabling invalid cell display without controller switch.
- Paste layer must not reject values for validation reasons; validation belongs
  in the field-evaluation layer after paste.
