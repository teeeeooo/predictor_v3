# 263 MetricInputTable TkTableSurface Adapter Compatibility

## Goal

Add `TkTableSurface`-compatible position-based adapter methods to
`MetricInputTable` without changing existing behavior. This is the first
step toward future `TkTableController` migration.

## Scope

- `ui_tk/metric_input_table.py`: add adapter methods
- `tests/test_ui_tk_metric_input_table_adapter.py`: focused adapter tests

## Implemented Adapter Methods

### Position↔Address Helpers

- `_address_at_position(position: tuple[int, int]) -> tuple[str, str]`
  - Converts `(row_idx, col_idx)` to `(row_key, col_key)`
  - Validates bounds, raises `IndexError` on out-of-range
- `_field_key_at_position(position: tuple[int, int]) -> str | None`
  - Returns field key for editable cells, `None` otherwise

### TkTableSurface Contract Methods

| Method | Implementation |
|---|---|
| `row_count()` | `len(self.rows)` |
| `column_count()` | `len(self.columns)` |
| `cell_roles()` | Broad fallback tuple (EDITABLE/READONLY per cell) |
| `cell_role(position)` | EDITABLE if in `editable_cells`, else READONLY |
| `text_at_position(position)` | Delegates to `text_at_address()` |
| `set_positions_batch(values)` | Maps positions→addresses, delegates to `set_address_values_batch()` |
| `snapshot()` | Returns copy of `self._values` |
| `restore_snapshot(snapshot)` | Delegates to `set_values_batch()` |
| `cell_frame(position)` | Returns `cell_frames[address]` |
| `cell_widget(position)` | Returns entry for editable, frame for read-only |
| `focus_widget(position)` | Same as `cell_widget()` |
| `default_cell_background(position)` | `TABLE_EDITABLE_BG` or `TABLE_STATIC_BG` |
| `ensure_row_count(count)` | No-op (fixed-row surface) |

### Design Decisions

- **No clipboard/winfo wrappers**: `MetricInputTable` inherits Tk widget
  methods (`clipboard_clear`, `clipboard_append`, `clipboard_get`,
  `winfo_containing`) directly. No recursive shadowing.
- **No behavior change**: all adapter methods wrap existing address-based
  data without modifying construction, value storage, callbacks, or parsing.
- **Fixed rows**: `ensure_row_count()` is a no-op because main calculator
  tables never dynamically add rows.

## Behavior Preservation

- `ExcelLikeTableController` file: **unchanged**
- `validate_paste_matrix()`: **unchanged**
- `test_invalid_paste_is_rejected_without_partial_apply`: **preserved**
- Calculator section files: **unchanged**
- `MetricInputTable.get_numeric_values()`: **unchanged**
- Existing `MetricInputTable` public API: **unchanged**

## Tests

### New adapter tests

| Test Class | Tests | Result |
|---|---|---|
| `TestAdapterDimensions` | row_count, column_count | SKIPPED (headless) |
| `TestAdapterCellRole` | editable/readonly role, cell_roles tuple | SKIPPED (headless) |
| `TestAdapterTextAccess` | text_at_position vs text_at_address | SKIPPED (headless) |
| `TestAdapterSetPositions` | set_positions_batch updates, no-change, readonly ignore | SKIPPED (headless) |
| `TestAdapterSnapshot` | snapshot, restore_snapshot | SKIPPED (headless) |
| `TestAdapterWidgets` | cell_frame, cell_widget, focus_widget | SKIPPED (headless) |
| `TestAdapterBackground` | default_cell_background editable/readonly | SKIPPED (headless) |
| `TestAdapterEnsureRowCount` | ensure_row_count no-op | SKIPPED (headless) |
| `TestAdapterOutOfRange` | IndexError on out-of-range | SKIPPED (headless) |
| `TestAdapterClipboardNotShadowed` | inherited methods present | SKIPPED (headless) |

All 24 tests skipped due to headless Tk unavailability. Windows GUI smoke
remains final verification for widget-return tests.

### Regression tests

| Suite | Result |
|---|---|
| `tests/test_ui_tk_excel_like_table_controller.py` | 3 passed, 27 skipped (identical to before) |

No regression in existing behavior.

## Excluded Scope

- Paste policy alignment (next slice)
- Invalid paste rejection removal (next slice)
- Visible cell validation / invalid marking (next slice)
- Controller switch to `TkTableController` (future slice)
- Result/detail Treeview migration (not applicable)
- Batch matrix changes
- Calculator core changes

## Risks

- Adapter methods add public API surface that must be maintained.
- `ensure_row_count()` no-op may need revisiting if a future controller
  expects dynamic row expansion; main tables are fixed-row by design.
- `TkTableController` paints ALL cells (headers/static included), while
  `ExcelLikeTableController` paints only editable cells. This visible
  difference will surface during controller switch, not in this adapter slice.

## Next Suggested Action

**Paste policy alignment / visible validation slice** (Candidate A from 262).

## Project Memory Delta

- `MetricInputTable` now exposes `TkTableSurface`-compatible position-based
  adapter methods without behavior change.
- Safe migration order confirmed: adapter → paste policy → controller switch.
- `ensure_row_count()` on fixed-row surfaces is a no-op, not a failure.
