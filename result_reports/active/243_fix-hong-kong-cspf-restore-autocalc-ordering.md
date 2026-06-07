# 243 Fix Hong Kong CSPF Matrix Restore/Autocalc Ordering

## Goal

Ensure `HongKongCspfBatchSection.__init__()` connects `values_changed_callback` before calling `initial_snapshot.restore_snapshot()` so that any notification from restore triggers the autocalc schedule.

## Scope

- Verify and confirm the callback-restore ordering in `ui_tk/sections/hong_kong_cspf_batch_section.py`.
- Add focused guard test if headlessly feasible.
- Run existing foundation regression tests.

## Fixed Ordering

After reading `HongKongCspfBatchSection.__init__()` (lines 75–121), the current ordering is already correct:

1. `BatchMatrixTable` creation
2. `TkTableController` attachment
3. `HongKongCspfMatrixController` creation
4. `DebouncedAutoCalc` creation
5. `table.set_values_changed_callback(self._auto_calc.schedule)` — callback connected
6. `table.restore_snapshot(initial_snapshot)` — if present; restore triggers `_notify_changed()` → callback is already connected
7. Action row / buttons / status label construction
8. `self._auto_calc.flush_now()` — forces immediate calculation

No code change was required; the ordering was already correct when the file was read.

## Tests

- No new headless guard test added for this ordering.
- Rationale: `restore_snapshot()` triggers `_rebuild_table()` which creates Tk widgets, and `_notify_changed()` triggers the `DebouncedAutoCalc.schedule()` callback. Testing this ordering headlessly would require a heavy test double for both the Tk widget grid and the debounce scheduler. The prompt explicitly discourages "무리한 test double" creation.
- Existing tests provide sufficient coverage for the functional contracts:
  - `test_ui_tk_hong_kong_cspf_matrix_migration.py`: 14 passed
  - `test_ui_tk_batch_matrix_models.py`: 9 passed
  - `test_ui_tk_table_controller_per_cell_roles.py`: 4 passed
  - `test_ui_tk_batch_matrix_table.py`: 1 skipped (Tk unavailable)
  - `test_ui_tk_batch_table_controller.py`: 13 passed
  - `test_ui_tk_hong_kong_cspf_batch_spec.py`: 5 passed

## Validation

- `python -m pytest tests/test_ui_tk_hong_kong_cspf_matrix_migration.py`: 14 passed
- `python -m pytest tests/test_ui_tk_batch_matrix_models.py`: 9 passed
- `python -m pytest tests/test_ui_tk_table_controller_per_cell_roles.py`: 4 passed
- `python -m pytest tests/test_ui_tk_batch_matrix_table.py`: 1 skipped (Tk unavailable in headless Codespaces)
- `python -m pytest tests/test_ui_tk_batch_table_controller.py`: 13 passed
- `python -m pytest tests/test_ui_tk_hong_kong_cspf_batch_spec.py`: 5 passed
- `python3 -m py_compile ui_tk/sections/hong_kong_cspf_batch_section.py`: OK
- `python3 -B tools/check_code_structure.py`: OK (only pre-existing `bin_detail_panel.py` 400 LOC warning)
- `git diff --check`: clean
- `git status --short`: clean (no tracked file changes)

## Known Risks

- Windows manual GUI smoke is still required to verify the actual dialog open/close/restore behavior in a real Tk environment.
- The DebouncedAutoCalc `schedule()` + `flush_now()` interaction has not been tested under real Tk event-loop timing.

## Excluded Scope

- No changes to `ui_tk/batch_matrix_table.py`, `ui_tk/table/controller.py`, `ui_tk/table/interaction_core.py`, calculator core, region config, profile registry, or golden fixtures.
- No copy-all / CSV export / xlsx export / EN/AHRI/KS profile expansion.

## Next Suggested Action

- Windows manual smoke for Hong Kong CSPF batch matrix dialog (open, two-row layout, paste, calculate, add/remove case, close/reopen state persistence).

## Project Memory Delta

- `HongKongCspfBatchSection` init ordering already satisfies the callback-before-restore pattern. Future dialog-level lifecycle reviews should check this same ordering for other batch surfaces.
