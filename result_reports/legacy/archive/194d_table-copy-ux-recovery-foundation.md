# 194-d Table Copy UX Recovery Foundation

## Goal

Recover the Excel paste-friendly copy baseline for read-only Tkinter result and trace table surfaces.

## Scope

- Added a small TSV clipboard helper for table-shaped data.
- Reused existing `table_export_data()` hooks for header-included TSV copy.
- Added copy APIs and keyboard handling to read-only result and bin trace table classes.
- Added visible copy buttons for ISO/ISEER result and trace, SASO result and trace, and Hong Kong CSPF trace.
- Preserved trace CSV export and removed result comparison CSV buttons from the current sections.

## Implementation

- `ui_tk/table_clipboard.py` encodes header-included TSV and writes it to the Tk clipboard.
- `IsoIseer2PointResultTable`, `IsoSasoT3ResultTable`, and `BinTraceTable` now expose `copy_table()` backed by `table_export_data()`.
- Ctrl/Cmd+C copies the whole current read-only table as TSV.
- Ctrl/Cmd+A safely targets all Treeview rows where available; no Excel-style range highlighting was added.
- Section files only wire buttons to table methods; TSV formatting remains outside sections.
- Result comparison tables now provide TSV copy only. Trace tables continue to provide both TSV copy and CSV export.

## Tests

- Added pure helper tests for header-included TSV and header-only empty rows.
- Added table/section tests for ISO/ISEER result copy, ISO/ISEER trace copy, SASO result copy, SASO trace copy, and Hong Kong CSPF trace copy.
- Added keyboard/no-crash coverage for read-only table copy/select-all behavior.
- Preserved existing trace, CSV export, and app smoke coverage.

## Verification

- Process check before verification: no lingering pytest process.
- `python3 -B tools/check_code_structure.py`: OK.
- Changed Python `py_compile`: OK.
- Quick smoke for table copy helper plus full app build: 2 passed.
- Final focused verification initially exposed an incorrect status-copy test expectation; the test was corrected to the actual header-included TSV contract.
- Final focused verification rerun: 74 passed.
- Process check after final focused: no lingering pytest process.
- `git diff --check`: clean.

## Manual Check Needed

- ISO/ISEER and SASO result copy buttons copy header-included TSV.
- ISO/ISEER, SASO, and Hong Kong CSPF trace copy buttons copy header-included TSV.
- Ctrl/Cmd+C on focused read-only result/trace tables copies whole-table TSV.
- Ctrl/Cmd+A on focused read-only result/trace tables is safe.
- Trace CSV export still works.
- Result comparison CSV buttons are absent.

## Excluded Scope

- No `ResultPanel` summary export/copy alignment.
- No `MetricInputTable` full-table copy enhancement.
- No Hong Kong HSPF trace or heating schema implementation.
- No graph, graph export, HTML export, or internal formula trace.
- No CSV writer behavior change.
- No core/profile/config/golden/fixture/PyQt changes.
- No BaseSection/shared result framework.
- No lifecycle summary/archive, project log, or memory seed updates.

## Next Suggested Action

- Manual smoke for 194-d table copy UX.
- Then `194-e ResultPanel summary export/copy alignment`.
- Later: `194-f MetricInputTable full-table copy enhancement`, Hong Kong HSPF heating trace schema, and bin graph parity.

## Changed Files

- `ui_tk/table_clipboard.py`
- `ui_tk/sections/bin_trace_table.py`
- `ui_tk/sections/iso_iseer_2point_result_table.py`
- `ui_tk/sections/iso_saso_t3_result_table.py`
- `ui_tk/sections/iso_iseer_2point_section.py`
- `ui_tk/sections/iso_saso_t3_section.py`
- `ui_tk/sections/hong_kong_cspf_section.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/194d_table-copy-ux-recovery-foundation.md`

## Project Memory Delta

- none
