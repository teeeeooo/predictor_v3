# 193-c Table CSV Export Foundation

## Goal

Add CSV export foundation for Tkinter table-shaped ISO/ISEER and SASO result/trace surfaces, following the 193-b boundary note.

## Scope

- Corrected 193-b commit/push pending wording.
- Added a small `ui_tk.table_csv_export` helper.
- Added thin export data hooks to table-shaped result/trace surfaces.
- Added CSV export buttons to ISO/ISEER and SASO sections.
- Added focused helper, table hook, and section button tests.
- Updated WORK_PLAN with the 193-c checkpoint.

## Export Targets

- ISO / ISEER result comparison table.
- SASO T3 result comparison table.
- ISO / ISEER bin trace table.
- SASO T3 bin trace table.

## Implementation

- `write_csv()` uses the Python standard `csv` module and defaults to `utf-8-sig` for Excel-friendly output.
- `export_table_to_csv()` owns the Tk save dialog wrapper and treats cancel as a no-op `False`.
- Table surfaces expose `table_export_data()` returning safe headers and rows.
- Missing/status-only table states export a safe status row instead of raw dicts, tracebacks, or `None`.
- Sections only wire buttons and pass current surface data to the helper.

## Excluded Scope

- No Hong Kong `ResultPanel` export.
- No graph, graph export, HTML export, or internal formula trace.
- No Hong Kong trace implementation.
- No BaseSection, presenter/controller layer, or shared result framework.
- No core/profile/config/golden/fixture/PyQt changes.
- No `project_log.md`, memory seed, summary, archive, or lifecycle maintenance.

## Verification

- Process check before verification: no lingering pytest process; only the check command and concurrent Python checks matched.
- `python3 -B tools/check_code_structure.py`: OK.
- `python3 -B -m py_compile ui_tk/table_csv_export.py ui_tk/sections/bin_trace_table.py ui_tk/sections/iso_iseer_2point_result_table.py ui_tk/sections/iso_saso_t3_result_table.py ui_tk/sections/iso_iseer_2point_section.py ui_tk/sections/iso_saso_t3_section.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py`: OK.
- Quick smoke: `python3 -B -m pytest tests/test_ui_tk_iso_table_autocalc.py::test_table_csv_export_writes_headers_and_rows tests/test_ui_tk_calculator_foundation.py::test_calculator_tk_app_builds_widget_tree -q -rxXs`: 2 passed.
- Initial final focused run failed because `ttk.Button.invoke()` returns Tcl integer `1`/`0`, not Python `True`/`False`; tests were corrected.
- Final focused rerun: `python3 -B -m pytest tests/test_ui_tk_profile_resolver.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py -q -rxXs`: 64 passed.
- Process check after final focused: no lingering pytest process; only the check command and concurrent structure guard matched.
- `git diff --check`: clean.

## Manual Check Needed

- Confirm the four CSV export buttons open save dialogs and write expected CSV files:
  - ISO/ISEER result.
  - ISO/ISEER trace.
  - SASO result.
  - SASO trace.
- Confirm dialog cancel is silent.

## Known Risks

- CSV export is intentionally limited to current table-shaped result/trace surfaces.
- Hong Kong `ResultPanel` remains out of scope.
- Graph export still waits for graph parity and may later use SPOT-style HTML export.

## Next Suggested Action

- Manual smoke for 193-c CSV export.
- Then choose one follow-up:
  - Bin graph parity with SPOT-style HTML export later.
  - Hong Kong CSPF trace implementation.
  - Hong Kong HSPF heating trace schema design.
  - Multi/batch design.

## Changed Files

- `ui_tk/table_csv_export.py`
- `ui_tk/sections/bin_trace_table.py`
- `ui_tk/sections/iso_iseer_2point_result_table.py`
- `ui_tk/sections/iso_saso_t3_result_table.py`
- `ui_tk/sections/iso_iseer_2point_section.py`
- `ui_tk/sections/iso_saso_t3_section.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `result_reports/active/193b_result-surface-export-boundary.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/193c_table-csv-export-foundation.md`

## Scope Compliance

- No forbidden files were modified.
- No Hong Kong export, graph export, or shared section framework was introduced.

## Commit / Push

- Source/test implementation commit: `ec86048 193-c: add table CSV export foundation`
- Docs/report commit: pending at report creation.
- Push: pending at report creation.

## Project Memory Delta

- none
