# 247 Copy-All And CSV Export Parity For BatchMatrixTable

## Goal

Add copy-all and CSV export parity to the Hong Kong CSPF BatchMatrixTable path
while keeping export/copy formatting responsibility out of the table surface owner.

## Scope

- `BatchMatrixTable`: add thin `table_export_data()` and `copy_all()` methods.
- `HongKongCspfBatchSection`: add "Copy All" and "Export CSV" buttons.
- Reuse existing `ui_tk.table_clipboard` and `ui_tk.table_csv_export` helpers.
- Focused tests for export shape.

## Reference Parity Evidence

- Existing result tables (`iso_saso_t3_result_table.py`, `iso_iseer_2point_result_table.py`,
  `bin_trace_table.py`) expose `table_export_data()` returning `(headers, rows)` and
  use `copy_table_to_clipboard()` from `ui_tk.table_clipboard`.
- `bin_detail_panel.py` uses `export_table_to_csv()` from `ui_tk.table_csv_export`.
- Reused: `table_clipboard.encode_table_tsv`, `copy_table_to_clipboard`,
  `table_csv_export.export_table_to_csv`, `table_csv_export.write_csv`.

## Copy/Export Owner Boundary

| Responsibility | Owner |
|---|---|
| Physical grid text extraction | `BatchMatrixTable.table_export_data()` (thin, 3 lines) |
| TSV encoding / clipboard I/O | `ui_tk.table_clipboard` (reused) |
| CSV encoding / file dialog | `ui_tk.table_csv_export` (reused) |
| UI button wiring | `HongKongCspfBatchSection` |
| Domain result schema | `HongKongCspfBatchHandler` (unchanged) |

`BatchMatrixTable` does not own formatting, quoting, file I/O, or dialog logic.

## Output Shape Decision

- Headers: column labels from `BatchMatrixSpec` ("Case", "Row Type", measurement
  points, result metrics).
- Rows: physical row count, each cell is `text_at_position((row, column))`.
- Case numbers appear on first physical row only; second physical row Case is blank.
- Result values appear on first physical row only; second physical row results are blank.
- Disabled/not-applicable cells render as empty string.
- This matches the visible two-row matrix grid exactly.

## Fixed/Implemented Behavior

### BatchMatrixTable
- `table_export_data()`: returns `(headers, rows)` tuple; headers from spec labels,
  rows from physical grid text.
- `copy_all()`: delegates to `copy_table_to_clipboard(self, headers, rows)`.

### HongKongCspfBatchSection
- "Copy All" button: calls `self.table.copy_all()`.
- "Export CSV" button: calls `export_table_to_csv(self._frame, filename, headers, rows)`.
- Existing "Add Case" / "Remove Case" buttons unchanged.

## Tests

### BatchMatrixTable Tk tests (skipped in headless Codespaces)
- `test_table_export_data_returns_headers_and_physical_rows`
- `test_table_export_data_includes_result_first_row_only`
- `test_copy_all_puts_physical_grid_on_clipboard`

### Existing regression
- `test_ui_tk_table_interaction_core.py`: 11 passed
- `test_ui_tk_batch_table_controller.py`: 13 passed
- `test_ui_tk_hong_kong_cspf_matrix_migration.py`: 14 passed
- `test_ui_tk_batch_matrix_models.py`: 9 passed
- `test_ui_tk_table_controller_per_cell_roles.py`: 4 passed
- `test_ui_tk_batch_matrix_table.py`: 1 skipped (Tk unavailable)
- `test_ui_tk_hong_kong_cspf_batch_spec.py`: 5 passed

## Manual Smoke Checklist (Windows)

- [ ] Hong Kong CSPF batch matrix dialog opens.
- [ ] Copy All produces two-row physical table shape.
- [ ] Case/result first row only, second row blank.
- [ ] Pasted clipboard into Excel keeps expected rows/columns.
- [ ] Export CSV opens in Excel with expected rows/columns.
- [ ] Calculated CSPF/CSEC values appear in export.
- [ ] MxN paste, undo, no flicker behavior from 246 remains stable.
- [ ] Close/reopen state persistence remains stable.

## Known Risks

- `batch_matrix_table.py` is now 422 LOC (soft limit 400). Further responsibility
  additions should trigger extraction to a helper or adapter.
- File dialog for CSV export requires real Tk; headless tests skip clipboard/CSV
  verification.
- Ragged TSV edge in `parse_clipboard_matrix` is unchanged; if copy/export helpers
  are extended to handle ragged shapes, that should be a separate slice.

## Excluded Scope

- No xlsx export.
- No Excel COM / DRM export.
- No EN/AHRI/KS profile expansion.
- No calculator core or handler changes.
- No existing row-per-case fallback deletion.

## Next Suggested Action

- Windows manual smoke for copy-all / CSV export / MxN paste / undo checklist.

## Project Memory Delta

- `table_clipboard` and `table_csv_export` are the confirmed common owners for
  table copy/export in both flat row-per-case and two-row matrix surfaces.
- `table_export_data()` is the thin surface contract for export shape; formatting
  and I/O live in dedicated helpers.
- `batch_matrix_table.py` LOC warning means future additions to this file should
  prefer helper extraction.
