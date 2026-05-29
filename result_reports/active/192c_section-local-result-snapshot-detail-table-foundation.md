# 192-c Section-Local Result Snapshot Detail Table Foundation

## Goal

Implement the 192-b recommendation as a foundation, not a one-off MVP: retain section-local result snapshots in Tkinter ISO/ISEER and SASO sections, then use those snapshots for the first read-only detail surface.

## Scope

- Implemented in:
  - `ui_tk/sections/result_snapshot.py`
  - `ui_tk/sections/detail_result_table.py`
  - `ui_tk/sections/iso_iseer_2point_section.py`
  - `ui_tk/sections/iso_saso_t3_section.py`
  - `ui_tk/tabs/iso16358_tab.py`
  - `tests/test_ui_tk_iso_table_autocalc.py`
- Updated:
  - `docs/WORK_PLAN.md`
- Excluded:
  - Core calculator/config/profile registry/golden/fixture changes.
  - Hong Kong `ResultPanel` path changes.
  - PyQt source changes.
  - Graph, bin-details trace table, internal formula trace, multi/batch, EN/AHRI.
  - Shared/generic result framework extraction.

## Implementation

### Section-local result snapshot

Added `ResultSnapshot` with `label`, `points`, `summary`, `bin_details`, and `status`.

The snapshot keeps the raw section-local data that was previously discarded after formatting comparison rows. CSPF `bin_details` is preserved for later reference trace/graph slices, but this task does not render it.

ISO/ISEER now retains two snapshots: `ISO 16358-1` and `India ISEER`.

SASO T3 now retains `Required only (3-point)`, `With 35 Min (4-point)` when optional 35 Min is enabled and valid, and a safe status snapshot for invalid optional 35 Min while preserving required-only detail.

Invalid required input clears snapshots so stale success detail cannot remain visible as current output.

### Detail table foundation

Added `DetailResultTable`, a section-local read-only Treeview surface with columns:

- `Profile/Scenario`
- `Point`
- `Capacity [W]`
- `Power [W]`
- `EER`
- `CSPF/ISEER`
- `CSTL [kWh]`
- `CSEC [kWh]`
- `Status`

Rows are combined rather than selected. ISO/ISEER shows ISO and India rows in one table. SASO shows required-only and optional 4-point rows in one table when available.

Summary values repeat per row for simple reading and TSV copy. Missing values render as `-`; raw dicts, traceback text, and `None` are not exposed.

### Collapse/expand and geometry

Each section has a default-collapsed `상세 결과` toggle. The detail table frame is not gridded while collapsed, so startup geometry is unchanged.

Expand/collapse calls only a narrow section callback. `Iso16358Tab` owns the one-shot fit through the existing `_fit_toplevel_to_current_content` path. No root/toplevel `<Configure>` observer, continuous geometry observer, hardcoded pixel policy, `window_geometry.py`, or `ScrollableFrame` change was added.

## Tests

Added focused tests for:

- ISO/ISEER default collapsed state and detail expand/collapse.
- ISO/ISEER combined detail rows for `ISO 16358-1` and `India ISEER`.
- Snapshot `bin_details` preservation without rendering trace/graph.
- ISO/ISEER invalid input clearing stale detail rows.
- SASO default collapsed state.
- SASO required-only detail rows.
- SASO optional valid 35 Min detail rows.
- SASO optional invalid 35 Min keeping required detail and showing safe 4-point status.
- SASO required invalid input clearing all detail rows.
- Profile switch lifecycle with detail expanded.

## Verification

- Process check before final focused verification: no lingering pytest process; only the check command itself matched.
- `python3 -B -m py_compile ui_tk/sections/result_snapshot.py ui_tk/sections/detail_result_table.py ui_tk/sections/iso_iseer_2point_section.py ui_tk/sections/iso_saso_t3_section.py ui_tk/tabs/iso16358_tab.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py`: OK.
- Quick smoke: `python3 -B -m pytest tests/test_ui_tk_iso_table_autocalc.py::test_iso_iseer_detail_table_expands_with_snapshot_rows tests/test_ui_tk_calculator_foundation.py::test_calculator_tk_app_builds_widget_tree -q -rxXs`: 2 passed.
- `python3 -B tools/check_code_structure.py`: OK.
- Final focused: `python3 -B -m pytest tests/test_ui_tk_profile_resolver.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py -q -rxXs`: 57 passed.
- `git diff --check`: clean.

During verification, a focused pytest run hung after new tests used `root.update()`. The hang process was killed and the tests were corrected to use `update_idletasks()` for idle geometry callbacks. The corrected focused sequence and final focused suite passed.

## Manual Check Needed

- Real Tk shell smoke for ISO/ISEER and SASO detail expand/collapse.
- Profile switch smoke while detail is expanded.
- Visual check that the expanded detail table remains readable on the target display and scrolls when screen-capped.

## Known Risks

- Detail table uses combined rows only; no row selector was added by design.
- `bin_details` is retained but not displayed. A future design slice should decide whether the next surface is bin-details reference trace or graph.
- Internal formula trace remains blocked on a future core/data contract.

## Next Action

Run 192-c manual smoke, then select the next Design First Gate slice from:

- bin-details reference trace design
- graph design
- multi/batch design

## Commit / Push

- Source/test implementation commit: `679b027 192-c: add section result detail snapshots`
- Docs/report commit: pending at report creation.
- Push: pending at report creation.
