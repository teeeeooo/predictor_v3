# 194-b Hong Kong CSPF Bin Trace

## Goal

Add Hong Kong CSPF `bin_details` trace support using the existing Tkinter `BinTraceTable` and CSV export foundation.

## Scope

- Added section-local Hong Kong CSPF trace retention.
- Added collapsed Hong Kong CSPF `Bin trace` UI.
- Added Hong Kong CSPF trace CSV export button.
- Wired CSPF trace expand/collapse to the tab-owned one-shot fit callback.
- Added focused lifecycle, stale-state, trace row, and export button tests.

## Implementation

- `HongKongCspfSection` now retains only CSPF `bin_details` after successful `calculate_cspf()`.
- Invalid input or calculation errors clear retained trace rows and set a safe trace status.
- The existing `ResultPanel` summary path remains unchanged.
- The existing `BinTraceTable` is reused because Hong Kong CSPF uses cooling/CSPF-style bin keys.
- Trace CSV export uses the existing `table_csv_export` helper and default filename `hong_kong_cspf_bin_trace.csv`.

## HSPF Exclusion

Hong Kong HSPF remains excluded. Its raw bin data is heating-specific and needs a separate heating trace schema decision before implementation.

## Verification

- Process check before verification: no lingering pytest process; only the check command and concurrent Python checks matched.
- `python3 -B tools/check_code_structure.py`: OK.
- `python3 -B -m py_compile ui_tk/sections/hong_kong_cspf_section.py ui_tk/tabs/iso16358_tab.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py`: OK.
- Quick smoke: `python3 -B -m pytest tests/test_ui_tk_iso_table_autocalc.py::test_hong_kong_cspf_bin_trace_expands_with_bin_details tests/test_ui_tk_calculator_foundation.py::test_calculator_tk_app_builds_widget_tree -q -rxXs`: 2 passed.
- Final focused: `python3 -B -m pytest tests/test_ui_tk_profile_resolver.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py -q -rxXs`: 68 passed.
- Process check after final focused: no lingering pytest process; only the check command and `rg` matched.
- `git diff --check`: clean.

## Manual Check Needed

- Hong Kong CSPF trace starts collapsed.
- Expanding/collapsing trace does not resize/scroll hang.
- Trace rows render for default CSPF calculation.
- Invalid CSPF input clears stale trace rows.
- Trace CSV export writes `hong_kong_cspf_bin_trace.csv`.
- File dialog cancel is silent.
- Switching ISO/ISEER / Hong Kong / SASO with CSPF trace expanded is safe.

## Excluded Scope

- No Hong Kong HSPF trace or heating schema implementation.
- No graph, graph export, HTML export, or internal formula trace.
- No Hong Kong ResultPanel export or ResultPanel refactor.
- No core/profile/config/golden/fixture/PyQt changes.
- No BaseSection/shared result framework.
- No lifecycle summary/archive, project log, or memory seed updates.

## Next Suggested Action

- Manual smoke for Hong Kong CSPF trace.
- Then choose one follow-up:
  - Bin graph parity with SPOT-style HTML export later.
  - Hong Kong HSPF heating trace schema design.
  - Multi/batch design.

## Changed Files

- `ui_tk/sections/hong_kong_cspf_section.py`
- `ui_tk/tabs/iso16358_tab.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/194b_hong-kong-cspf-bin-trace.md`

## Project Memory Delta

- none
