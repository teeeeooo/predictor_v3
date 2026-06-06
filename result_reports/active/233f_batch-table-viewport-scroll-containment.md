# 233F - Batch Table Viewport / Scroll Containment

## Goal

Keep the Hong Kong CSPF batch table contained inside the batch dialog when rows are added, without growing the dialog for every new row and without changing batch calculation, export, or table schema behavior.

## Current Viewport / Overflow Audit

The current batch dialog content is built by `HongKongCspfBatchSection`, and the table surface is `BatchCaseTable`.

Before this change:

- `BatchCaseTable` was a `ttk.Frame` containing one direct `table_frame` grid.
- Header, row headers, input cells, and result cells were all rebuilt directly into that single grid.
- `Add Row` called `model.add_row()`, `_rebuild_table()`, and `_notify_changed()`.
- There was no vertical viewport or scrollbar between the table and dialog.
- When row count exceeded the dialog's visible area, the table content could extend below the dialog instead of being contained.

This is a table surface containment issue, not a dialog first-show sizing issue. The dialog shell should not grow on every added row.

A fixed-header/body split would be a larger table-structure change because the current controller registers cells in one common grid. This slice implements safe table-wide vertical containment first and leaves fixed header/body split as a possible follow-up if smoke requires it.

## MVC / SoC Boundary

- Dialog shell: keeps first-show sizing, parent-centered placement, and `Toplevel` lifecycle from 233D.
- Batch table surface: owns row-growth viewport/scroll containment.
- Table model/controller: continues to own row values, selection, paste, add/remove, and snapshot/restore behavior.
- Calculation/export/state persistence: not mixed into viewport logic.

No new app-wide scrolling framework or two-row batch layout was introduced.

## Implementation

Changed `ui_tk/batch_case_table.py`:

- Wrapped `table_frame` inside a `Canvas`-based vertical viewport provided by
  `ui_tk/batch_table_viewport.py`.
- Limited the requested viewport height to the initial/default visible row count, while allowing manual dialog resize to allocate more canvas space.
- Kept the existing `table_frame` and cell registration behavior so `BatchTableController` continues to work through existing `cell_frame()` / `cell_widget()` APIs.
- `add_row()` now rebuilds the table and scrolls to the bottom so the newly added row is reachable.

Added `ui_tk/batch_table_viewport.py`:

- Owns the canvas, vertical scrollbar, content window, scrollregion sync, and
  auto-show/hide scrollbar behavior.
- Keeps viewport-specific Tk code out of `BatchCaseTable`, which stays below
  the structure checker soft LOC limit.

Fixed header/body split was not implemented in this slice. The whole table, including header, scrolls together when overflow exists.

## Preserved 233D / 233E Behavior

- 233D hidden-first, content-measured batch dialog first-show sizing is unchanged.
- 233E close/reopen state persistence is unchanged.
- Batch paste/add/remove/calculation behavior remains on the existing model/controller path.
- No copy/export/two-row matrix behavior was added.

## Tests

Updated `tests/test_ui_tk_iso_table_autocalc.py`:

- verifies batch dialog still opens as dialog, not a metric tab;
- verifies hidden-first sizing helper path still runs;
- verifies no Status column, no Run Batch, no Clear Results;
- verifies the batch table exposes `vertical_scroll_containment` viewport roles;
- verifies Add Row makes the internal scrollbar path active;
- verifies close/reopen still preserves added rows and input values.

Existing batch table controller and Hong Kong CSPF batch spec tests were rerun.

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

- Add Row repeatedly and confirm rows remain reachable inside the dialog viewport.
- Confirm vertical scrollbar or internal viewport is usable.
- Confirm batch dialog first-show sizing improvement remains.
- Confirm manual resize remains possible.
- Confirm close/reopen preserves added rows and input values.
- Confirm paste/add/remove behavior remains intact.
- Confirm batch calculation behavior remains intact.
- Confirm Hong Kong main profile lower blank fix remains stable.
- Confirm no refit loop returns.

## Excluded Scope

Not changed:

- fixed-header/body split;
- two-row matrix batch layout;
- batch copy/export/xlsx;
- batch calculation logic;
- batch model schema;
- main profile flicker;
- UI/UX policy or architecture docs;
- report lifecycle/archive.

## Next Action

Windows smoke - main and batch window sizing.
