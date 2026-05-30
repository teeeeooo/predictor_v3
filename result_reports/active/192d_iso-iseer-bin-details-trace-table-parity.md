# 192-d ISO/ISEER Bin Details Trace Table Parity

## Goal

Port the PyQt reference `bin_details` trace table behavior to the Tkinter `ISO / ISEER 2-point` section.

This is reference parity implementation, not a new input-point detail design.

## PyQt Reference Target

- `TraceTableModel` columns:
  - `Bin No`
  - `Temp [°C]`
  - `Hours`
  - `Load [W]`
  - `Capacity [W]`
  - `Power [W]`
  - `EER`
  - `CSTL [Wh]`
  - `CSEC [Wh]`
- `TwoPointTableModel.recalculate_row()` stores `iso_res.get("bin_details")` and `iseer_res.get("bin_details")`.
- `TraceDetailPanel` lets the user inspect ISO vs ISEER trace data from those retained `bin_details`.

## Changed Files

- Added `ui_tk/sections/bin_trace_table.py`.
- Updated `ui_tk/sections/iso_iseer_2point_section.py`.
- Updated `ui_tk/tabs/iso16358_tab.py`.
- Updated `tests/test_ui_tk_iso_table_autocalc.py`.
- Updated `docs/WORK_PLAN.md`.

## Implementation

### BinTraceTable

Added a read-only Tk `ttk.Treeview` trace surface that maps `bin_details` keys to the PyQt trace table columns:

- `bin_no`
- `tj`
- `nj`
- `lc`
- `capacity`
- `power`
- `eer`
- `cstl_bin`
- `csec_bin`

Formatting follows the PyQt reference: float values render with two decimals, missing values render safely as empty strings, and raw dict / traceback / `None` text is not exposed.

### ISO/ISEER retention

`IsoIseer2PointSection` now retains only trace data:

- `ISO 16358-1` -> ISO `bin_details`
- `India ISEER` -> ISEER `bin_details`

It does not retain raw calculator result snapshots and does not reintroduce `ResultSnapshot`, `DetailResultTable`, or an input-point detail table.

Invalid input or calculation errors clear retained trace data and update the visible trace surface with a safe status.

### Trace UI

Added an ISO/ISEER-only `Bin trace` toggle and readonly selector:

- Default collapsed.
- Default selector: `ISO 16358-1`.
- Selector can switch to `India ISEER`.
- Expand/collapse calls a narrow callback; `Iso16358Tab` owns the existing one-shot fit path.
- No root/toplevel `<Configure>` observer, continuous geometry observer, `window_geometry.py`, or `ScrollableFrame` change.

## Tests

Focused tests cover:

- Default collapsed trace pane.
- Expand/collapse with `bin_details` rows.
- PyQt trace table column parity.
- ISO/ISEER selector row refresh.
- Invalid input clearing stale trace rows.
- Profile switch lifecycle while trace is expanded.
- Existing full app subprocess smoke remains in the focused suite.

## Verification

- `python3 -B -m py_compile ui_tk/sections/bin_trace_table.py ui_tk/sections/iso_iseer_2point_section.py ui_tk/tabs/iso16358_tab.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py`: OK.
- Quick smoke: `python3 -B -m pytest tests/test_ui_tk_iso_table_autocalc.py::test_iso_iseer_bin_trace_expands_with_bin_details tests/test_ui_tk_calculator_foundation.py::test_calculator_tk_app_builds_widget_tree -q -rxXs`: 2 passed.
- Process check before final focused verification: no lingering pytest process; only the check command and concurrent structure check matched.
- `python3 -B tools/check_code_structure.py`: OK.
- Final focused: `python3 -B -m pytest tests/test_ui_tk_profile_resolver.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py -q -rxXs`: 55 passed.
- `git diff --check`: clean.
- Process check after verification: no lingering pytest process; only the check command itself matched.

## Manual Check Result

User manual smoke completed with no issues found:

- App default profile remains `ISO / ISEER 2-point`.
- ISO/ISEER 2-point comparison table remains normal.
- Bin trace starts collapsed.
- Expanding Bin trace shows the PyQt-reference bin-level table.
- `ISO 16358-1` / `India ISEER` trace selection works.
- Invalid input does not leave stale success trace rows.
- Hong Kong / SASO switching keeps existing behavior normal.
- Repeated expand/collapse has no window size, scroll, or resize hang issue.

## Excluded Scope

- No graph implementation.
- No SASO trace implementation.
- No internal formula trace implementation.
- No input-point detail table, `ResultSnapshot`, or `DetailResultTable`.
- No core/config/profile registry/golden/fixture changes.
- No PyQt source changes.
- No `ResultPanel`, `window_geometry.py`, `ScrollableFrame`, or `profile_resolver` changes.

## Next Action

Choose the next follow-up slice from:

- SASO bin trace parity
- table CSV export foundation
- bin graph parity
- multi/batch design

## Commit / Push

- Source/test implementation commit: `f935571 192-d: add ISO ISEER bin trace parity`
- Docs/report commit: `623cde4 192-d: document ISO ISEER bin trace parity`
- Manual smoke closeout commit: `45da308 192-d: close out bin trace manual smoke`
- Push: completed for implementation/docs and manual smoke closeout.
