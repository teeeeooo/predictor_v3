# 195 Summary - Tkinter Detail Panel, Copy, and Graph Arc

## Scope

This lifecycle summary covers the active Tkinter ISO profile/detail/copy/graph arc after `191_summary-tkinter-iso-profile-expansion-arc.md`.

Covered active reports:

- `190b_saso-t3-tkinter-implementation.md`
- `191b_work-plan-compaction.md`
- `192a_tkinter-next-slice-selection-audit.md`
- `192b_detail-trace-graph-result-surface-design.md`
- `192c_revert-wrong-detail-foundation.md`
- `192d_iso-iseer-bin-details-trace-table-parity.md`
- `193a_saso-trace-and-hk-trace-availability.md`
- `193b_result-surface-export-boundary.md`
- `193c_table-csv-export-foundation.md`
- `193d_csv-export-closeout-next-slice.md`
- `194a_hong-kong-section-naming-cleanup.md`
- `194b_hong-kong-cspf-bin-trace.md`
- `194c_excel-like-table-contract-recovery.md`
- `194d_table-copy-ux-recovery-foundation.md`
- `194e_pyqt-style-detail-panel-ia-recovery.md`

## Completed Work

- Implemented `SASO T3` as a dedicated Tkinter ISO section using the existing `saso_t3_cspf` profile path.
- Added SASO required-only 3-point and optional-min 4-point comparison rows.
- Reverted the wrong input-point detail foundation and returned to the PyQt reference `bin_details` target.
- Added ISO/ISEER `bin_details` detail table parity.
- Added SASO T3 `bin_details` detail table support.
- Audited Hong Kong CSPF/HSPF trace availability and confirmed CSPF can reuse cooling `bin_details`; HSPF needs a heating-specific schema.
- Renamed Hong Kong section owners to `hong_kong_cspf_section.py` and `hong_kong_hspf_section.py`.
- Added Hong Kong CSPF `bin_details` detail table support.
- Added table CSV export helper and table export hooks.
- Corrected scope so result comparison tables use TSV copy only, while detail/bin tables keep TSV copy plus CSV export.
- Added header-included TSV copy foundation for read-only result/detail tables.
- Recovered the PyQt-style detail panel IA in Tkinter:
  - Main result surface exposes `상세 보기 ↓ / 상세 닫기 ↑`.
  - Detail panel owns source selector, summary strip, graph selector, Canvas graph, bin/detail table, `상세 복사`, and `상세 CSV 내보내기`.
  - Main-screen user-visible `Trace` controls were removed.
- Added graph axis label hotfix:
  - x-axis is outdoor temperature bin `tj`, displayed as `Outdoor Temp [°C]`.
  - if `tj` is unavailable, x-axis falls back to `Bin index`.
  - y-axis is the selected series from the graph selector.
  - `Bin Hours [h]` remains a y-series backed by `nj`.

## Important Decisions

- PyQt calculator reference IA is the source of truth for detail/result parity work.
- User-visible `Trace` terminology should not drive the Tkinter main result IA; use the detail panel pattern instead.
- Result comparison tables are read-only result surfaces with header-included TSV copy, not CSV export targets.
- Detail/bin tables are read-only table surfaces with header-included TSV copy and CSV export.
- The shared `table_export_data()` hook is the bridge for TSV copy and CSV export data.
- `ResultPanel` remains unchanged for Hong Kong summary rendering until a separate summary copy/export alignment slice.
- Hong Kong HSPF detail/trace remains excluded until a heating trace schema is designed.
- Graph export and HTML export remain deferred until graph parity is stable.

## Known Remaining Issues

- Dual-monitor geometry clipping needs a separate audit/hotfix; this summary does not close that issue.
- Hong Kong HSPF heating trace schema and implementation remain open.
- Graph polish/export, including possible SPOT-style HTML export, remains deferred.
- `MetricInputTable` header-included whole-table copy enhancement remains deferred; existing edit/paste/drag/navigation/undo behavior must be preserved.

## Verification Summary

- Focused source/test checks were used throughout the arc instead of full pytest.
- Latest graph axis label hotfix verification:
  - no lingering pytest process before/after focused tests.
  - `python3 -B tools/check_code_structure.py`: OK.
  - changed Python `py_compile`: OK.
  - quick smoke for graph axis/detail panel plus full app build: 2 passed.
  - final focused verification: 74 passed.
  - `git diff --check`: clean.

## Project Memory Seed Sync Judgment

Update `result_reports/memory/project_memory_seed.md` with summary-level durable decisions:

- PyQt-style detail panel IA is the parity target for Tkinter ISO result detail surfaces.
- Result comparison tables use TSV copy; detail/bin tables use TSV copy plus CSV export.
- Detail graph x-axis is outdoor temperature `tj`; selected graph series is the y-axis.
- Dual-monitor geometry clipping remains an unresolved audit/hotfix item.
