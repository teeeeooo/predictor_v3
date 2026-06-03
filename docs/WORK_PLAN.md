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

- Tkinter ISO profile/detail/copy/graph arc is summarized in `result_reports/summaries/195_summary-tkinter-detail-panel-copy-graph-arc.md`.
- Window geometry, viewport policy, input replace-on-type, and UI pivot prep arc is summarized in `result_reports/summaries/200_summary-window-geometry-viewport-ui-pivot-prep-arc.md`.
- Implemented state:
  - ISO/ISEER and SASO T3 comparison result tables.
  - ISO/ISEER, SASO T3, and Hong Kong CSPF PyQt-style detail panels.
  - Header-included TSV copy for result/detail tables.
  - Detail/bin table CSV export.
  - Lightweight Canvas graph with `Outdoor Temp [°C]` x-axis, selected-series y-axis, and selected-series min/max scale text.
- User manual smoke result:
  - 196-a through 199-c completed and archived under summary 200.
  - 201-b resolved the 201-a archived-doc whitespace blocker; merge readiness checks now pass.
  - MetricInputTable replace-on-type, multi-monitor geometry, first-launch/detail auto-fit, 80% height cap, top-safe y policy, and UI/UX window geometry policy numbering are closed for this arc.
  - Windows calculator_tk packaged size was measured at approximately 11 MB and is acceptable for the current deployment candidate.
- Next: main merge execution.

## Next Actions

1. **Main merge execution**
   - Merge `work/ui-ux-ssot-adoption` to `main` after user approval.
2. **UI technology pivot design gate**
   - Decide C# WPF calculator shell / reusable grid direction before implementation.
3. **Hong Kong HSPF heating trace schema/implementation**
   - Define heating-specific detail columns before any HSPF detail implementation.
4. **Graph export/HTML export after graph parity stable**
   - Keep export deferred until graph readability/parity is stable.

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
- Detail graph x-axis is outdoor temperature `tj` shown as `Outdoor Temp [°C]`; `Bin Hours [h]` is a selectable y-series backed by `nj`.
- Do not introduce `BaseSection` or a shared result framework for the CSV export foundation.
- CSV export is currently limited to detail/bin table surfaces and table-shaped export hooks already approved for the Tkinter calculator.

## Deferred / Hold

- PyQt calculator source retirement remains on hold.
- Windows calculator_tk packaged size is approximately 11 MB and acceptable for the current deployment candidate.
- SASO follow-up polish is on hold (no concrete issue after 190-b smoke).
- Graph export/HTML export is deferred until after graph parity is stable.
- ResultPanel summary export/copy alignment is deferred unless manual smoke shows summary copy/export parity is still needed.
- MetricInputTable full-table copy enhancement is deferred after ResultPanel alignment.
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
- `result_reports/summaries/195_summary-tkinter-detail-panel-copy-graph-arc.md`
  - Covers active reports 190-b through 194-e plus the 194-f graph axis label hotfix.
- `result_reports/summaries/200_summary-window-geometry-viewport-ui-pivot-prep-arc.md`
  - Covers active reports 196-a through 199-c: graph label closeout, input replace-on-type, multi-monitor geometry, launch/detail auto-fit, viewport policy documentation, and UI/UX doc numbering cleanup.

## Historical Notes / References

- Detailed completed task reports are archived in `result_reports/archive/`.
- Milestone decisions and lessons are in `project_log.md`.
- Compact recall facts are in `result_reports/memory/project_memory_seed.md`.
- UI/UX active SSOT starts at `docs/ui_ux/00_UI_UX_SYSTEM.md`.
- Current SASO T3 design owner: `docs/designs/2026-05-29-tkinter-saso-t3-profile-design.md`.
