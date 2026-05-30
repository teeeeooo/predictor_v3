# Work Plan

## Purpose

- Maintain the current focus, next actions, active constraints, and deferred/hold items.
- Keep detailed work history in `project_log.md`, `result_reports/summaries/`, and `result_reports/archive/`.
- Keep long-term goals and Phase 1~5 direction in `PROJECT_CHARTER.md`.
- Keep refactor candidates and structural triggers in `docs/REFACTOR_PLAN.md`.

## Work Plan Update Rule

- WORK_PLAN is a current execution board, not a task log.
- After a summary/archive lifecycle closes an arc, replace covered detailed checkpoints with summary references.
- Do not append full report content, long terminal output, or repeated next-action history here.
- Add only compact checkpoints that change current focus, next execution order, active constraints, or hold status.
- Active reports should not record the docs/report commit hash that includes the same report, and should not leave `pending at report creation` commit/push wording; commit/push results belong in the final chat report.

## Current Focus

- Tkinter calculator ISO profile expansion arc is complete.
- Completed in the current arc:
  - `ISO / ISEER 2-point` default profile with section-local comparison table.
  - `Hong Kong` CSPF/HSPF metric sub-tabs unchanged.
  - `SASO T3` dedicated section with required-only 3-point vs optional-min 4-point comparison.
  - 190-b SASO T3 manual smoke completed with no issues found.
  - 192-b detail/trace/graph design slice completed.
  - 192-c input-point detail foundation was reverted; it did not match the intended PyQt parity target.
  - 192-d ISO/ISEER `bin_details` trace table parity implemented.
  - 192-d manual smoke completed with no issues found.
  - 193-a SASO T3 `bin_details` trace table implemented; Hong Kong CSPF/HSPF trace availability audited.
  - 193-a manual smoke completed with no issues found.
  - 193-b result surface/export boundary note added.
  - 193-c table CSV export foundation implemented for ISO/ISEER and SASO table-shaped result/trace surfaces.
  - 193-c manual smoke completed with no issues found.
  - 193-d selected Hong Kong CSPF trace implementation as the next slice.
  - 194-a Hong Kong CSPF/HSPF section naming cleanup completed.
  - 194-b Hong Kong CSPF bin trace implementation completed.
  - 194-c Excel-like table contract recovery audit/design completed.
  - 194-d table copy UX recovery foundation implemented for read-only result/trace tables.
  - 194-e PyQt-style detail panel IA recovery implemented for ISO/ISEER, SASO T3, and Hong Kong CSPF.
- Next: 194-e manual smoke, then choose multi-monitor geometry audit/hotfix or graph/detail follow-up.

## Next Actions

1. **194-e manual smoke**
   - Check `상세 보기 ↓ / 상세 닫기 ↑`, source selector, summary, graph selector, Canvas graph, detail copy, detail CSV export, and absence of main-screen `Trace` wording.
2. **Multi-monitor geometry audit/hotfix**
   - Investigate screen clipping separately without changing detail/result semantics.
3. **Graph polish/export after graph parity**
   - Refine graph parity first; graph export may use SPOT-style HTML export later.
4. **ResultPanel summary export/copy alignment**
   - Add Hong Kong summary TSV/CSV-compatible data hook if the label-card path still needs copy/export parity.
5. **194-f MetricInputTable full-table copy enhancement**
   - Preserve existing edit/paste/drag behavior while adding header-included whole-table copy.
6. **Hong Kong HSPF heating trace schema design**
   - Define heating-specific trace columns before any HSPF trace implementation.

## Active Constraints

- Use Design First Gate for larger UI/profile/result work; hotfix and micro cleanup stay scoped exceptions.
- Apply Diff / Read Budget: reuse already-confirmed policy/design context, inspect targeted functions/sections only, and avoid long compliance reprints.
- For SASO follow-ups, avoid core calculator, profile registry, region config, golden, and fixture changes unless a separate design slice approves them.
- Do not run full pytest unless explicitly requested; use focused smoke and relevant tests.
- Keep comparison result surfaces section-local until repeated reuse proves a shared framework is necessary.
- Do not change `ResultPanel` for SASO/2-point comparison unless a later design slice explicitly chooses that path.
- Result surface/export boundary owner: `docs/designs/2026-05-30-tkinter-result-surface-export-boundary.md`.
- Excel-like table contract recovery owner: `docs/designs/2026-05-30-tkinter-excel-like-table-contract-recovery.md`.
- Read-only result/detail table copy uses `table_export_data()` through `ui_tk/table_clipboard.py`; result comparison tables provide TSV copy only, while detail/bin tables keep TSV copy plus CSV export.
- Main result surfaces should expose `상세 보기 ↓ / 상세 닫기 ↑` rather than user-visible `Trace` controls.
- Do not introduce `BaseSection` or a shared result framework for the CSV export foundation.
- CSV export is currently limited to detail/bin table surfaces and table-shaped export hooks already approved for the Tkinter calculator.

## Deferred / Hold

- PyQt calculator source retirement remains on hold.
- Windows PyInstaller size measurement remains pending until a Windows host is available.
- SASO follow-up polish is on hold (no concrete issue after 190-b smoke).
- Bin graph polish/export is deferred until after detail panel manual smoke; graph export follows graph parity and may use SPOT-style HTML export.
- ResultPanel summary export/copy alignment is deferred unless manual smoke shows summary copy/export parity is still needed.
- MetricInputTable full-table copy enhancement is deferred after ResultPanel alignment.
- Multi-monitor geometry clipping is a separate audit/hotfix candidate.
- Hong Kong HSPF needs a separate heating trace schema decision.
- Internal formula trace still needs a separate core/data contract.
- Multi/batch calculator result structure is deferred.
- EN/AHRI Tkinter expansion is deferred.
- AS/NZS Excel compatibility Z-phase remains deferred.
- Historical ISO/KS/ASNZS workbook compatibility details stay outside this execution board.

## Recent Summaries

- `result_reports/summaries/165_summary-pyqt-retirement-tkinter-ui-matrix-rules.md`
  - Covers PyQt retirement hold, Tkinter matrix input, result surface rules, and UI/UX SSOT adoption through reports 154~164.
- `result_reports/summaries/180_summary-tkinter-calculator-ux-implementation-arc.md`
  - Covers Tkinter calculator UX implementation, Excel-like table behavior, metric sub-tabs, and smoke-loop lessons through reports 166~179e.
- `result_reports/summaries/191_summary-tkinter-iso-profile-expansion-arc.md`
  - Covers portable geometry, ISO/ISEER 2-point adoption, profile switch polish, Design First Gate use, and SASO T3 design through reports 184~190a2.
- `result_reports/active/190b_saso-t3-tkinter-implementation.md`
  - Tracks the current SASO T3 implementation slice until manual smoke/lifecycle cleanup.
- `result_reports/active/192d_iso-iseer-bin-details-trace-table-parity.md`
  - Tracks ISO/ISEER `bin_details` trace table parity and completed manual smoke closeout.
- `result_reports/active/193a_saso-trace-and-hk-trace-availability.md`
  - Tracks SASO T3 `bin_details` trace implementation, Hong Kong trace availability audit, and completed manual smoke.
- `result_reports/active/193b_result-surface-export-boundary.md`
  - Tracks the docs-only result surface/export boundary note before 193-c CSV export foundation.
- `result_reports/active/193c_table-csv-export-foundation.md`
  - Tracks table CSV export foundation and completed manual smoke.
- `result_reports/active/193d_csv-export-closeout-next-slice.md`
  - Tracks CSV export closeout, report commit/push recording principle, and next slice selection.
- `result_reports/active/194a_hong-kong-section-naming-cleanup.md`
  - Tracks Hong Kong section owner rename before CSPF trace implementation.
- `result_reports/active/194b_hong-kong-cspf-bin-trace.md`
  - Tracks Hong Kong CSPF bin trace implementation until manual smoke.
- `result_reports/active/194c_excel-like-table-contract-recovery.md`
  - Tracks Excel-like table contract recovery audit/design and next copy UX slice.
- `result_reports/active/194d_table-copy-ux-recovery-foundation.md`
  - Tracks read-only result/trace table header-included TSV copy recovery until manual smoke.
- `result_reports/active/194e_pyqt-style-detail-panel-ia-recovery.md`
  - Tracks PyQt-style detail panel IA recovery until manual smoke.

## Historical Notes / References

- Detailed completed task reports are archived in `result_reports/archive/`.
- Milestone decisions and lessons are in `project_log.md`.
- Compact recall facts are in `result_reports/memory/project_memory_seed.md`.
- UI/UX active SSOT starts at `docs/ui_ux/00_UI_UX_SYSTEM.md`.
- Current SASO T3 design owner: `docs/designs/2026-05-29-tkinter-saso-t3-profile-design.md`.
