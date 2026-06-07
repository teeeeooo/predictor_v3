# 241 Fix Tk Two-Row Matrix Skeleton Guards Before Migration

## Goal

Fix small issues discovered in the 240 skeleton before proceeding to Hong Kong CSPF matrix migration.

## Scope

- Remove header grid overlap in `BatchMatrixTable._build_headers()`.
- Correct snapshot/restore test logic in `tests/test_ui_tk_batch_matrix_table.py`.
- Remove duplicate Next Action entry in `docs/WORK_PLAN.md`.

## Fixed Items

### Header grid overlap (ui_tk/batch_matrix_table.py)
- `_build_headers()` previously placed a corner cell at `row=0, column=0`, then placed the "Case" column header at the same `row=0, column=0`, causing two widgets to occupy the same grid cell.
- Matrix tables have no separate row-header column (Case is already column 0), so the corner cell is unnecessary.
- Removed the corner cell block; column headers now start cleanly at column 0.

### Snapshot/restore test logic (tests/test_ui_tk_batch_matrix_table.py)
- `test_snapshot_restore_is_logical_case_based` previously changed a value, then took a snapshot, then restored that same snapshot, expecting the original pre-change value to appear.
- Logic corrected: take snapshot before mutation, mutate, then restore and assert the pre-mutation value is back.

### WORK_PLAN duplicate cleanup (docs/WORK_PLAN.md)
- Removed duplicated "Batch table copy-all + CSV export parity" item under Next Actions.
- Re-numbered subsequent items to keep sequence intact.

## Validation

- `python -m pytest tests/test_ui_tk_batch_matrix_models.py`: 9 passed
- `python -m pytest tests/test_ui_tk_table_controller_per_cell_roles.py`: 4 passed
- `python -m pytest tests/test_ui_tk_batch_matrix_table.py`: 1 skipped (Tk unavailable in headless Codespaces environment)
- `python3 -m py_compile ui_tk/batch_matrix_table.py tests/test_ui_tk_batch_matrix_table.py`: OK
- `python3 -B tools/check_code_structure.py`: OK (only pre-existing `bin_detail_panel.py` warning)
- `git diff --check`: clean

## Known Risks

- Tk tests are skipped in headless environments; Windows GUI smoke is still required for visual layout verification after the header fix.

## Excluded Scope

- No Hong Kong CSPF matrix migration.
- No new feature expansion (copy-all, CSV export, calculation adapter, etc.).
- No change to existing row-per-case batch, controller, viewport, or core.

## Next Suggested Action

- Proceed with Hong Kong CSPF matrix migration slice.

## Project Memory Delta

- Header grid overlap in matrix tables: when the first data column itself serves as the row identifier (Case), do not add a separate corner cell. This is a difference from flat row-per-case tables where a row-header column exists.
