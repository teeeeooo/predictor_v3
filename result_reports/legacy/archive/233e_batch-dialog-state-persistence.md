# 233E - Batch Dialog State Persistence on Close/Reopen

## Goal

Preserve the Hong Kong CSPF batch dialog's in-session row/input state when the user closes and reopens the dialog.

The user-facing rule is: closing a dialog hides/destroys the display surface; it is not an implicit reset or clear action.

## Current State Lifecycle Audit

The batch dialog is opened from `HongKongCspfSection._open_batch_dialog()` and owned as `_batch_dialog` while the `Toplevel` exists.

Before this change:

1. `HongKongCspfBatchDialog` built a new `HongKongCspfBatchSection` and `BatchCaseTable` every time it opened.
2. `close()` disposed the section, destroyed the toplevel, and called `_clear_batch_dialog()`.
3. `_clear_batch_dialog()` only cleared the dialog reference.
4. Reopen therefore rebuilt the table from default rows and discarded user-entered rows/values.

`BatchCaseTable` already exposes `snapshot()` and `restore_snapshot()`. That snapshot is sufficient for the current first slice because it stores the table text rows, including input and result columns. Restore notifies the table change callback and the batch section performs normal auto-calculation, so restored result state is safe to keep or refresh.

Region/profile lifetime is left to the existing `HongKongCspfSection` lifecycle. The snapshot is only in-memory and section-local; app restart persistence is intentionally out of scope.

## MVC / SoC Boundary

- `HongKongCspfBatchDialog` remains the `Toplevel` shell owner and only captures a table snapshot during close.
- `HongKongCspfSection` is the session-local state owner for the batch snapshot.
- `BatchCaseTable` remains the table surface/model owner that provides snapshot/restore.
- Calculation, export, table viewport, and batch layout concerns were not mixed with dialog persistence.

No disk persistence, app-wide state framework, or withdraw/hide workaround was introduced.

## Implementation

Changed `ui_tk/sections/hong_kong_cspf_batch_section.py`:

- `HongKongCspfBatchSection` accepts an optional `initial_snapshot` and restores it into the table before the initial recalculation flush.
- `HongKongCspfBatchDialog.close()` captures `section.table.snapshot()` before dispose/destroy.
- `HongKongCspfBatchDialog` passes the snapshot to the close callback.

Changed `ui_tk/sections/hong_kong_cspf_section.py`:

- Added `_batch_snapshot` as section-local in-memory state.
- Dialog open passes the saved snapshot, if present.
- Dialog close stores the latest snapshot and clears only the live dialog reference.

Changed `tests/test_ui_tk_iso_table_autocalc.py`:

- Extended the existing batch dialog open-path test to enter multiple rows/values, close the dialog, reopen it, and verify row count and input values are retained.
- Existing assertions for dialog-not-tab behavior, no Status column, no Run/Clear buttons, row headers, Add Row, and sizing helper call remain covered.

## Snapshot Persistence Scope

Preserved within the current section session:

- row count;
- input text values;
- result/status text values present in the table snapshot;
- restored table shape after close/reopen.

Not preserved:

- app restart state;
- state after the parent section itself is destroyed and rebuilt;
- future export/layout metadata beyond current table text rows.

## Validation

Executed:

- `python -m pytest -q tests/test_ui_tk_iso_table_autocalc.py` - 8 passed, 46 skipped.
- `python -m pytest -q tests/test_ui_tk_hong_kong_cspf_batch_spec.py tests/test_ui_tk_batch_table_controller.py` - 18 passed.
- `python -m pytest -q tests/test_ui_tk_calculator_foundation.py` - 13 passed, 11 skipped.
- `python3 -B tools/check_code_structure.py` - passed with one pre-existing soft warning: `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `git diff --check` - passed.
- `git status --short` - expected modified/new files only.

GUI smoke was not run in this environment. Windows manual smoke remains required.

## Windows Manual Smoke Needed

Check on Windows:

- Enter several batch rows/values, close, reopen, and confirm row count and input values are retained.
- Confirm calculated result cells are safely retained or recalculated after reopen.
- Confirm close/reopen does not reset to five blank/default rows unless the section was rebuilt.
- Confirm paste/add/remove behavior still works after reopen.
- Confirm 233D first-show sizing improvement remains.
- Confirm manual resize remains possible.
- Confirm Hong Kong main profile lower blank fix remains stable.
- Confirm no refit loop returns.

## Excluded Scope

Not changed:

- batch table viewport/scroll containment;
- Add Row below-dialog visibility;
- copy/export/xlsx behavior;
- two-row matrix batch layout;
- calculation core or region config;
- UI/UX or architecture policy docs;
- report lifecycle/archive.

## Next Action

233F - batch table viewport/scroll containment.
