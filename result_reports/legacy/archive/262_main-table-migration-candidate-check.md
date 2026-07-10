# 262 Main Table Migration Candidate Check with Paste/Validation Policy Audit

## Goal

Audit whether `MetricInputTable + ExcelLikeTableController` can safely converge
on the common Tk table foundation (`TkTableSurface + TkTableController`),
and determine the correct paste/validation policy for calculator main tables.

## Scope

- Audit current main table path ownership and structure.
- Compare `MetricInputTable` with `TkTableSurface` contract.
- Evaluate adapter feasibility without behavior change.
- Audit paste policy against common UX contract and user intent.
- Assess visible validation and execution blocking path.
- Classify result/detail Treeview surfaces.
- Classify legacy/root table files.
- Recommend one safe implementation slice.

## Current Main Table Path

### `MetricInputTable` (296 LOC)

**Owns:**
- Rows/columns metadata (`self.rows`, `self.columns`)
- Editable/static cell mapping (`self.editable_cells: Mapping[CellAddress, str]`)
- Field key mapping (`self._values: dict[str, str]`, `self._variables`, `self._entries`)
- Value storage and batch update (`set_values_batch`, `set_values`, `set_value`)
- Numeric parsing (`get_numeric_values()` → `parse_numeric_cell()`)
- Widget/frame registry (`self.cell_frames`, `self.editable_cell_frames`, `self.static_cell_frames`)
- Table construction (`_build_table`, `_add_header_cell`, `_add_row_header`, `_add_editable_cell`, `_add_static_cell`)
- Layout (`_configure_column_weights`, responsive grid)

**Key characteristic:** Uses `(row_key, column_key)` string-address tuples, not `(row, col)` integer positions.

### `ExcelLikeTableController` (396 LOC)

**Owns:**
- Selection state machine (`anchor`, `active`, `selection_bounds`, `selected_positions`)
- Copy/paste (`_copy`, `_paste` with atomic `validate_paste_matrix()`)
- Clear/delete (`_clear`)
- Undo (`_undo_last`, `_undo: list[dict[str, str]]`)
- Navigation (`_navigate`, `_arrow`, `_focus_next`)
- Replace-on-type (`_type_replace`)
- Edit mode lifecycle (`_enter_edit_mode`, `_commit_edit`, `_cancel_edit`)
- Key bindings (Ctrl+C/V/Z, Delete, Tab, Enter, arrows, F2, Esc)
- Selection painting (`_paint_selection`)
- Active controller singleton (`_active_controller`)

**Key coupling to `MetricInputTable`:**
- `table.editable_entries[field_key]`
- `table.editable_cell_frames[field_key]`
- `table.field_key_for_address(address)`
- `table.text_at_address(address)`
- `table.set_address_values_batch(values)`
- `table.get_text_values()`
- `table.rows`, `table.columns`
- `table.table_frame`, `table.header_cells`, `table.row_header_cells`, `table.static_cell_frames`

The controller maintains its own position↔address mapping (`self._by_position`).

## Common Table Foundation Comparison

### `TkTableSurface` Protocol (38 LOC)

| Method | Contract | `MetricInputTable` Status |
|---|---|---|
| `row_count()` | Returns int | **Missing** (has `len(self.rows)`) |
| `column_count()` | Returns int | **Missing** (has `len(self.columns)`) |
| `cell_roles()` | Returns tuple[CellRole, ...] | **Missing** |
| `cell_role(position)` | Returns CellRole | **Missing** |
| `text_at_position(position)` | Returns str | **Different** (`text_at_address(address)`) |
| `set_positions_batch(values)` | Returns bool | **Different** (`set_address_values_batch(values)`) |
| `snapshot()` | Returns object | **Missing** (can derive from `get_text_values()`) |
| `restore_snapshot(snapshot)` | Returns None | **Missing** (can use `set_values_batch`) |
| `cell_frame(position)` | Returns widget | **Missing** (has `cell_frames[address]`) |
| `cell_widget(position)` | Returns widget | **Missing** (has `editable_entries[field_key]`) |
| `focus_widget(position)` | Returns widget | **Missing** |
| `default_cell_background(position)` | Returns str | **Missing** |
| `clipboard_clear/append/get()` | Clipboard I/O | **Missing** (uses `tkinter.Misc` methods implicitly) |
| `winfo_containing(x, y)` | Widget lookup | **Missing** (uses `tkinter.Misc.winfo_containing`) |
| `ensure_row_count(count)` | Dynamic row resize | **Missing** (fixed row count) |

### `TkTableController` vs `ExcelLikeTableController`

| Behavior | `TkTableController` | `ExcelLikeTableController` |
|---|---|---|
| Position addressing | `(row, col)` integers | `(row, col)` integers with internal address mapping |
| Selection painting | Paints all cells via `cell_frame` + `cell_widget` | Paints only editable cells via `editable_entries` |
| Paste validation | **None** — role-filter only, values pass through | **Atomic numeric validation** — whole paste rejected if any cell invalid |
| Undo stack | `UndoStack` dataclass with limit | Simple `list[dict[str, str]]` |
| Navigation | Grid-based (wraps around edges) | Editable-cell-only sequence |
| Key binding scope | All cells (including headers/static) | Editable cells + table_frame only |
| Focus handling | `focus_widget(position).focus_set()` | `entry.focus_set()` with internal focus tracking |
| Active controller | No singleton | `_active_controller` singleton for cross-table deselection |

### `BatchMatrixTable` Reference

`BatchMatrixTable` (422 LOC) implements `TkTableSurface` with:
- `cell_role(position)` using `BatchMatrixSpec.resolve_cell(position).kind`
- `text_at_position(position)` using logical case index mapping
- `set_positions_batch(values)` with batch depth and change tracking
- `snapshot()` / `restore_snapshot(snapshot)` using case dict copies
- `ensure_row_count(count)` for dynamic row expansion

This proves the contract works for complex real tables.

## MetricInputTable Surface Adapter Feasibility

**Verdict: FEASIBLE with adapter methods.**

`MetricInputTable` already owns all required data; it just lacks the position-based interface methods expected by `TkTableSurface`.

**Proposed adapter methods (no behavior change):**

```python
def row_count(self) -> int:
    return len(self.rows)

def column_count(self) -> int:
    return len(self.columns)

def cell_role(self, position: tuple[int, int]) -> CellRole:
    address = self._address_at_position(position)
    if address in self.editable_cells:
        return CellRole.EDITABLE
    return CellRole.READONLY

def text_at_position(self, position: tuple[int, int]) -> str:
    return self.text_at_address(self._address_at_position(position))

def set_positions_batch(self, values: Mapping[tuple[int, int], str]) -> bool:
    return self.set_address_values_batch({
        self._address_at_position(pos): val for pos, val in values.items()
    })

def snapshot(self) -> dict[str, str]:
    return dict(self._values)

def restore_snapshot(self, snapshot: dict[str, str]) -> None:
    self.set_values_batch(snapshot)

def cell_frame(self, position: tuple[int, int]) -> tk.Frame:
    return self.cell_frames[self._address_at_position(position)]

def cell_widget(self, position: tuple[int, int]) -> tk.Widget:
    address = self._address_at_position(position)
    field_key = self.editable_cells.get(address)
    if field_key is not None:
        return self.editable_entries[field_key]
    return self.cell_frames[address]

def focus_widget(self, position: tuple[int, int]) -> tk.Widget:
    return self.cell_widget(position)

def default_cell_background(self, position: tuple[int, int]) -> str:
    role = self.cell_role(position)
    if role is CellRole.EDITABLE:
        return TABLE_EDITABLE_BG
    return TABLE_STATIC_BG

def clipboard_clear(self) -> None:
    self.clipboard_clear()

def clipboard_append(self, text: str) -> None:
    self.clipboard_append(text)

def clipboard_get(self) -> str:
    return self.clipboard_get()

def winfo_containing(self, root_x: int, root_y: int):
    return self.winfo_containing(root_x, root_y)
```

**Note:** `ensure_row_count(count)` would raise `NotImplementedError` or be a no-op since main tables have fixed rows. This is acceptable for a read-only adapter.

**Risk assessment:**
- No existing behavior changes
- No key bindings, painting, or interaction changes
- Existing `ExcelLikeTableController` continues to work unchanged
- Future `TkTableController` can be attached to the same surface

## Paste Policy and Validation Standard Audit

### Current `ExcelLikeTableController._paste()` Flow

1. Parse clipboard → `ClipboardMatrix`
2. `validate_paste_matrix(matrix)` — validates **ALL** cells with `parse_numeric_cell`
3. If any cell is invalid → **whole paste silently rejected** (returns `"break"`)
4. If all valid → compute targets → apply

### `TkTableController._paste()` Flow

1. Parse clipboard → `ClipboardMatrix`
2. `editable_paste_targets_by_role()` — filters by `CellRole.EDITABLE` only
3. **No value validation** — all values pass through
4. Apply targets via `set_positions_batch()`

### Common UX Contract §4 (Paste)

> "Pasted values go through the same per-column validator as inline edits.
> **Invalid pasted cells are marked but do not abort the paste**;
> other valid cells still land."

### `TKINTER_TABLE_ADAPTER.md` §4

> "For this numeric auto-calculation surface, a paste is validated as one
> action before applying any values. If any pasted numeric cell is invalid,
> no cell is changed and no recalculation is scheduled. Inline invalid edits
> remain visible through the existing result-status path. This atomic paste
> policy is a **paste-specific deviation** from the common baseline..."

### User Intent Analysis

The user's stated intent:
- Invalid values pasted must be **visible** to the user
- Invalid state must be shown at table/cell/result/status layer
- Calculation must **not silently execute** with invalid values
- But **paste itself should not be silently cancelled**

This aligns with the **common UX contract**, not the current deviation.

### Conclusion

**Current atomic paste rejection is a legacy misinterpretation.**

- The common contract explicitly says invalid cells should be marked, not abort paste.
- The adapter doc acknowledges this is a "deviation" for the current binding.
- The user's intent matches the common contract: allow paste, mark invalid, block execution.
- `test_invalid_paste_is_rejected_without_partial_apply` is a regression guard for the deviation, not a source-of-truth for target UX.

### Recommended Paste Policy

1. **Paste layer**: No atomic value validation. Role-filter only (editable cells).
2. **Validation layer**: Per-cell validation after paste. Mark invalid cells with `color.bg.cell.invalid`.
3. **Execution layer**: `get_numeric_values()` (or equivalent) raises on invalid values, blocking calculation. Status shows which fields are invalid.

This is the same three-layer separation: paste → validate → execute.

## Validation Visibility and Execution Blocking Audit

### Current Path

- `MetricInputTable.get_numeric_values()` calls `parse_numeric_cell(value)` for each cell
- `parse_numeric_cell` raises `ValueError` on empty, non-numeric, or non-finite input
- Calculator sections catch this in `recalculate_now()` and show error in status label
- **However:** No per-cell visual invalid marking exists in `MetricInputTable` or `ExcelLikeTableController`
- The invalid state is only visible through the **status label after failed calculation**, not at the cell level

### Gap

If we remove atomic paste rejection (allow invalid paste), we need:
- Per-cell invalid background/border marking
- Clear invalid marking on valid edits
- Status aggregation showing which fields are invalid

### Current Partial Coverage

- Empty cell → `parse_numeric_cell` raises → status shows error
- This is sufficient for blocking execution, but insufficient for visible cell-level feedback
- Common contract §5 requires `color.bg.cell.invalid` token usage

## Result/Detail Treeview Classification

| Surface | Widget | Editable? | Controller Migration? |
|---|---|---|---|
| `IsoIseer2PointResultTable` | Treeview | Read-only | **No** — read-only copy only |
| `IsoSasoT3ResultTable` | Treeview | Read-only | **No** — read-only copy only |
| `BinTraceTable` | Treeview | Read-only | **No** — read-only copy/export only |

**Verdict:** Result/detail Treeview tables are **NOT** editable spreadsheet controller migration targets. They remain separate read-only surfaces with their own copy/export contract via `table_clipboard` and `table_csv_export`.

## Legacy/Root Table File Cleanup Classification

| File | LOC | Role | Classification |
|---|---|---|---|
| `ui_tk/metric_input_table.py` | 296 | Active main table surface | **Active standard** (with adapter additions) |
| `ui_tk/excel_like_table_controller.py` | 396 | Active main table controller | **Active path** (target for future replacement) |
| `ui_tk/table_grid.py` | 129 | Generic Entry-grid experiment | **Deprecated candidate** — unused by main or batch |
| `ui_tk/table_grid_model.py` | 159 | `TableGridModel`, `parse_numeric_cell` | **Partial utility** — `parse_numeric_cell` is imported by active code; model is deprecated with `TableGrid` |
| `ui_tk/batch_table_controller.py` | ~200 | Old batch controller | **Compatibility wrapper** — still used by `BatchCaseTable` |
| `ui_tk/batch_table.py` | ~150 | Old batch table | **Compatibility wrapper** — still used by older batch sections |
| `ui_tk/batch_case_table.py` | ~180 | Row-per-case batch table | **Fallback path** — still used |
| `ui_tk/batch_matrix_table.py` | 422 | Two-row matrix batch table | **Active standard** — implements `TkTableSurface` |
| `ui_tk/table_clipboard.py` | ~60 | Copy/export helper | **Active utility** — shared by all table surfaces |
| `ui_tk/table_csv_export.py` | ~60 | CSV export helper | **Active utility** — shared by all table surfaces |

**Cleanup timing:**
- `table_grid.py` + `table_grid_model.py` (model only) can be cleaned up after `parse_numeric_cell` is extracted
- `batch_table.py` + `batch_table_controller.py` can be retired when `BatchCaseTable` is fully replaced by `BatchMatrixTable`
- No immediate deletions — this is a classification audit only

## Candidate Options

### Candidate A: Paste Policy Alignment First

- Remove atomic paste validation from `ExcelLikeTableController._paste()`
- Allow invalid values through to cells
- Add per-cell invalid marking to `MetricInputTable`
- Update `test_invalid_paste_is_rejected_without_partial_apply` to new behavior

**Pros:** Directly addresses user's primary concern.
**Cons:** Requires adding visible validation surface before changing behavior; higher regression risk; mixes behavior change with surface enhancement.

### Candidate B: MetricInputTable TkTableSurface Adapter Compatibility First

- Add `TkTableSurface` adapter methods to `MetricInputTable` (no behavior change)
- Keep `ExcelLikeTableController` untouched
- Enables future `TkTableController` attachment

**Pros:** Zero behavior change; low risk; enables all future migration; pure interface addition.
**Cons:** Does not immediately address paste policy.

### Candidate C: Direct Controller Switch to TkTableController

- Add adapter methods + switch from `ExcelLikeTableController` to `TkTableController`

**Pros:** Full convergence in one slice.
**Cons:** Changes selection painting, navigation, undo, paste, and key bindings simultaneously; very high regression risk; not safe as a single slice.

### Candidate D: TkTableController Contract Change

- Modify `TkTableController` to match `ExcelLikeTableController` behavior

**Pros:** None — the common contract already defines target behavior.
**Cons:** Deviates common foundation from its purpose; rejected.

### Candidate E: Result/Detail Treeview Migration

- Migrate read-only Treeview tables to editable controller

**Pros:** None — these are read-only by design.
**Cons:** Wrong target; rejected.

## Recommended Next Slice

**Candidate B: MetricInputTable TkTableSurface Adapter Compatibility First**

**Rationale:**
1. Zero behavior change — lowest risk.
2. `MetricInputTable` already owns all data; only position-based interface methods are missing.
3. Enables future `TkTableController` attachment without breaking existing `ExcelLikeTableController`.
4. Paste policy alignment (Candidate A) becomes easier and safer once the surface is on the common contract.
5. Direct controller switch (Candidate C) is too risky without this adapter bridge.

**Implementation scope:**
- Add adapter methods to `MetricInputTable` (listed in feasibility section)
- Add focused tests proving adapter methods work and preserve existing behavior
- No changes to `ExcelLikeTableController`, `TkTableController`, or calculator sections

**Follow-up slice:**
- Candidate A (paste policy alignment) after adapter is stable
- Then Candidate C (controller switch) as the final convergence step

**Files to modify in next slice:**
- `ui_tk/metric_input_table.py` (add adapter methods)
- `tests/test_ui_tk_metric_input_table_adapter.py` (new focused tests)

**Files to NOT modify:**
- `ui_tk/excel_like_table_controller.py`
- `ui_tk/table/controller.py`
- Calculator sections
- Result/detail tables

## Excluded Scope

- No code changes in this audit slice.
- No test changes.
- No controller switch.
- No paste policy change yet.
- No result/detail Treeview migration.
- No legacy file cleanup yet.
- No EN/AHRI/KS profile expansion.

## Risks

- Adapter methods add surface API surface that must be maintained during any future `MetricInputTable` refactoring.
- `ensure_row_count()` being a no-op or raising may cause issues if `TkTableController` is attached later (it calls `ensure_row_count` on paste overflow).
- Two controllers (`ExcelLikeTableController` and future `TkTableController`) cannot coexist on the same surface; migration requires a clean switch.
- `TkTableController` paints ALL cells (including static/headers), while `ExcelLikeTableController` paints only editable cells. This is a visible behavior difference.

## Project Memory Delta

- `MetricInputTable` can become `TkTableSurface`-compatible through adapter methods without behavior change.
- Current atomic paste rejection in `ExcelLikeTableController` is a deviation from the common UX contract; target policy is role-filter + per-cell marking + execution blocking.
- `test_invalid_paste_is_rejected_without_partial_apply` guards the deviation, not the target UX.
- Result/detail Treeview tables are read-only surfaces and not editable controller migration targets.
- `table_grid.py` is a deprecated experiment; `parse_numeric_cell` from `table_grid_model.py` is the only active dependency.
- Safe migration order: adapter (B) → paste policy (A) → controller switch (C).
