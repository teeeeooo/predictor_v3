# 194-e PyQt-Style Detail Panel IA Recovery

## Goal

Recover the PyQt reference detail-panel IA in Tkinter result surfaces while preserving the table copy and bin/detail CSV foundations.

## Scope

- Replaced main-screen `Trace` controls with `상세 보기 ↓ / 상세 닫기 ↑` detail toggles.
- Added a reusable Tkinter bin detail panel with source selector, summary strip, graph selector, Canvas graph, bin/detail table, and detail action row.
- Moved bin/detail table copy and CSV export into the detail panel.
- Kept result comparison TSV copy via Ctrl/Cmd+C and table methods; no visible result copy button remains.
- Kept result comparison CSV export absent.
- Applied the detail panel to ISO/ISEER, SASO T3, and Hong Kong CSPF.

## Implementation

- `BinDetailPanel` owns source selection, summary display, graph selection, `BinTraceTable` reuse, `상세 복사`, and `상세 CSV 내보내기`.
- `BinDetailGraph` draws a lightweight Tk Canvas line graph from existing `bin_details`; no new graph dependency was added.
- ISO/ISEER detail sources are `ISO 16358-1` and `India ISEER`.
- SASO detail sources are `Required only (3-point)` and `With 35 Min (4-point)`, with safe status for disabled or invalid optional data.
- Hong Kong CSPF uses a single-source detail panel.
- Existing section-local result rendering and calculation flow remain unchanged.

## Verification

- Quick smoke for ISO/ISEER detail panel open/close plus full app build: 2 passed.
- Process check: no lingering pytest process.
- `python3 -B tools/check_code_structure.py`: OK after moving graph colors away from raw hex literals.
- Changed Python `py_compile`: OK.
- Final focused verification: 74 passed.
- Process check after final focused: no lingering pytest process.
- `git diff --check`: clean.

## Manual Check Needed

- ISO/ISEER, SASO, and Hong Kong CSPF show only `상세 보기 ↓` on the main result surface.
- Opening detail shows source selector where applicable, summary, graph selector, graph, detail table, `상세 복사`, and `상세 CSV 내보내기`.
- Closing detail hides the panel and restores `상세 보기 ↓`.
- Detail copy writes header-included TSV.
- Detail CSV export still writes the selected/current bin detail table.
- Result comparison CSV export is absent.
- Main-screen user-visible `Trace` wording is absent.
- Multi-monitor geometry clipping remains a separate issue.

## Excluded Scope

- No dual-monitor geometry fix.
- No graph export or HTML export.
- No `ResultPanel` internal changes.
- No Hong Kong HSPF detail/trace schema implementation.
- No `MetricInputTable` or `ExcelLikeTableController` changes.
- No `table_clipboard` or `table_csv_export` changes.
- No core/profile/config/golden/fixture/PyQt changes.
- No BaseSection/shared result framework.
- No lifecycle summary/archive, project log, or memory seed updates.

## Next Suggested Action

- Manual smoke for 194-e detail panel IA.
- Then choose one focused follow-up:
  - Multi-monitor geometry audit/hotfix.
  - Graph polish/export after graph parity.
  - ResultPanel summary copy/export alignment if still needed.
  - MetricInputTable full-table copy enhancement.
  - Hong Kong HSPF heating trace schema/implementation.

## Changed Files

- `ui_tk/sections/bin_detail_panel.py`
- `ui_tk/sections/bin_trace_table.py`
- `ui_tk/sections/iso_iseer_2point_section.py`
- `ui_tk/sections/iso_saso_t3_section.py`
- `ui_tk/sections/hong_kong_cspf_section.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/194e_pyqt-style-detail-panel-ia-recovery.md`

## Project Memory Delta

- none
