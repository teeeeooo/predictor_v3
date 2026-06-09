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

## Current Focus

- Tkinter ISO profile/detail/copy/graph arc is summarized in `result_reports/summaries/195_summary-tkinter-detail-panel-copy-graph-arc.md`.
- Window geometry, viewport policy, input replace-on-type, and UI pivot prep arc is summarized in `result_reports/summaries/200_summary-window-geometry-viewport-ui-pivot-prep-arc.md`.
- Architecture/UI-UX boundary and window refit arc is summarized in `result_reports/summaries/231_summary-architecture-uiux-boundary-and-window-refit-arc.md`.
- Window/dialog/table/batch viewport closeout arc is summarized in `result_reports/summaries/236_summary-window-dialog-batch-viewport-arc.md`.
- Batch two-row matrix and reference parity arc (237-248) is summarized in `result_reports/summaries/249_summary-batch-two-row-matrix-and-reference-parity-arc.md`.
- Implemented state:
  - ISO/ISEER and SASO T3 comparison result tables.
  - ISO/ISEER, SASO T3, and Hong Kong CSPF PyQt-style detail panels.
  - Header-included TSV copy for result/detail tables.
  - Detail/bin table CSV export.
  - Lightweight Canvas graph with `Outdoor Temp [°C]` x-axis, selected-series y-axis, and selected-series min/max scale text.
  - Batch two-row matrix: `BatchMatrixSpec` + `BatchMatrixTable` + `TkTableController` + `HongKongCspfMatrixController` adapter.
  - Hong Kong CSPF batch migrated to two-row matrix; row-per-case fallback preserved.
  - MxN paste repeat-fill fixed in `interaction_core` common helper.
  - Same-shape in-place restore preserves widget continuity (reference parity with `BatchCaseTable`).
  - Copy-all and CSV export parity using existing `table_clipboard` / `table_csv_export` helpers.
- User manual smoke result:
  - 196-a through 199-c completed and archived under summary 200.
  - 201-b resolved the 201-a archived-doc whitespace blocker; merge readiness checks now pass.
  - 202 merged `work/ui-ux-ssot-adoption` into `main`.
  - 203 added a lightweight architecture triage rule to the task router before the C# WPF spike branch.
  - 204 closes the C# WPF spike as an experiment only; no C# WPF code is merged to `main`.
  - 206 adds the first Hong Kong CSPF row-per-case batch slice for `calculator_tk`; Windows/manual GUI smoke remains before treating batch UX as stable.
  - MetricInputTable replace-on-type, multi-monitor geometry, first-launch/detail auto-fit, 80% height cap, top-safe y policy, and UI/UX window geometry policy numbering are closed for this arc.
  - Windows calculator_tk packaged size was measured at approximately 11 MB and is acceptable for the current deployment candidate.
  - 216 Windows smoke kept table interaction/layout gaps as input to the next table foundation arc.
  - 221C through 228 and 230A through 230D are summarized under summary 231.
  - 229, 231, 232, 233A through 233F guard, 234, and 235 are summarized under summary 236.
  - 236 closes the window/dialog/table/batch viewport arc.
  - 237-248 are summarized under summary 249.
  - 251: result/detail/export common contract audit completed.
  - 252: Hong Kong HSPF detail/bin trace schema preflight completed.
  - 253: configurable bin-detail schema extraction (foundation for HSPF detail).
  - 254: cleanup legacy cooling constants after schema extraction.
  - 255: Hong Kong HSPF single-case detail/bin panel wiring completed.
  - 256: shared Tk content-hugging refit/minsize lifecycle repair completed.
  - 257: side-effect-free visible content measurement policy repair completed.
  - 258: nested notebook current-state width/height replacement repair completed.
  - 259: nested notebook width replacement using chrome-width estimate repair completed.
  - 260: HSPF detail/schema + window lifecycle arc summarized and archived after Windows smoke OK.
  - 262: main table migration candidate check with paste/validation policy audit completed.
  - 263: MetricInputTable TkTableSurface adapter compatibility completed.
  - 264: MetricInputTable visible invalid-field validation foundation completed.
  - 265: main paste policy aligned to raw text paste + visible validation + execution blocking.
  - 266: focused tests corrected for validation/paint semantics.
  - 267: Windows-discovered stale tests/import/event simulation issues fixed.
  - 268: callback-count failure audited; test expectation corrected after contract decision.
  - 269: main paste policy / validation arc closed after Windows validation.
  - 270: code checker reference map foundation design completed.
  - 271: repo reference map MVP implementation completed.
  - 272: repo reference map calibration completed.
  - 273: reference evidence gate hook policy adopted into DIFF_READ_BUDGET.md and AGENT_TASK_ROUTER.md.
  - 274: ui_tk cleanup preflight completed using Reference Evidence Gate.
  - 276: extract section-level result formatting helpers completed.
  - 277: BinDetailPanel cleanup preflight completed.
  - 278: BinDetailPanel.__init__ setup helper split completed.
  - 279: controller switch design preflight completed.
  - 280: MetricInputTable clipboard protocol compatibility check completed.
  - 281: controller switch parity test foundation completed.
  - 282: controller parity readonly paste test corrected (real behavior test with mixed editable/readonly fixture).
  - 283: Windows parity test closeout — 13 passed, 2 skipped (Tcl/Tk install), 0 failures.
  - 284: Controller switch pilot implemented for HongKongCspfSection (TkTableController migration, 5 new pilot tests pass under Xvfb, 15 parity tests pass).
  - 285: Diagnosed ResultPanel flicker root cause — redundant focus_set() in TkTableController._type_replace; callback/render counts identical between CSPF and HSPF.
  - 286: Removed redundant focus_set() from TkTableController._type_replace; 9 diagnostic + 15 parity + 5 pilot tests pass under Xvfb.
  - 287: Implemented stable ResultPanel summary update — same-shape summaries now update value/status text in place without full widget destroy/recreate; 39 tests pass under Xvfb.
- Next: Post-focus-preservation GUI smoke passed; invalid text undo resolved. Controller switch expansion blocker cleared.
- 289: Narrowed ResultPanel focus helper exception handling from broad `except Exception` to `except tk.TclError`; behavior unchanged.
- 290: Enforced active report count check in agent output workflow; AGENTS.md, AGENT_TASK_ROUTER.md, RESULT_REPORT_WORKFLOW.md updated.
- 292-295: Active report lifecycle cleanup completed; 28 reports archived under 4 summaries; 3 reports remain active (262, 274, 275).
- 299: HongKongHspfSection controller switch migrated to TkTableController; 6 new focused tests pass.
- 300: TkTableController type-replace selection carryover fixed; select_clear() clears selection after first-char replacement; regression test added.
- 301: Post-type-replace selection fix GUI smoke passed on iMac; type-replace carryover resolved; undo/paste/clear/flicker intact.
- 302: IsoIseer2PointSection controller switch migrated to TkTableController; 6 new focused tests pass.
- 303: Post-2-point controller switch GUI smoke passed on iMac; type-replace/undo/paste/clear/Treeview updates verified.
- 304: IsoSasoT3Section controller switch migrated to TkTableController; 7 new focused tests pass.
- 305: Code checker and reference map gate audit completed; gaps categorized and follow-up slices proposed.
- 306: Aligned 305 code checker audit with original 270-272 reference map intent; proposed corrected follow-up order.
- 307: Aligned SASO T3 section input validation with MetricInputTable visual marking; preserved optional 35 Min partial behavior.

## Next Actions

1. **Post-SASO T3 controller switch & validation GUI smoke**
   - Perform iMac GUI smoke testing to close out both controller switch and validation alignment.
   - Note: active report count is 15 (>10), lifecycle cleanup is pending and deferred.
2. **Reference Evidence Gate semantic check patch**
   - Update agent workflow instructions to turn the read budget gate into a semantic check (checking for owner-bypass, duplication, and hotspot expansion).
3. **code_checker metadata & freshness check improvement**
   - Address task number hardcoding and map staleness detection options.
4. **Regenerate reference map and commit milestone changes**
   - Re-run `build_reference_map.py` to sync the codebase reference map with all completed controller switch sections and test suites.
5. **Main table migration check**
   - Assess how existing table surfaces can converge on the common table foundation and define a safe migration slice.
6. **ui_tk folder cleanup**
   - Review compatibility wrappers, root table file sprawl, owner locations, and duplicate helpers after window/table foundations stabilize.
5. **EN14825 / AHRI 210/240 / KS profile expansion**

## Active Constraints

- Use Design First Gate for larger UI/profile/result work; hotfix and micro cleanup stay scoped exceptions.
- Apply Diff / Read Budget: reuse already-confirmed policy/design context, inspect targeted functions/sections only, and avoid long compliance reprints.
- For SASO follow-ups, avoid core calculator, profile registry, region config, golden, and fixture changes unless a separate design slice approves them.
- Do not run full pytest unless explicitly requested; use focused smoke and relevant tests.
- Keep comparison result surfaces section-local until repeated reuse proves a shared framework is necessary.
- Do not change `ResultPanel` for SASO/2-point comparison unless a later design slice explicitly chooses that path.
- Result surface/export rules are owned by `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`; `docs/designs/2026-05-30-tkinter-result-surface-export-boundary.md` is decision evidence.
- Excel-like interaction rules are owned by `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` and `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md`; `docs/designs/2026-05-30-tkinter-excel-like-table-contract-recovery.md` is decision evidence.
- Read-only result/detail table copy uses `table_export_data()` through `ui_tk/table_clipboard.py`; result comparison tables provide TSV copy only, while detail/bin tables keep TSV copy plus CSV export.
- Main result surfaces should expose `상세 보기 ↓ / 상세 닫기 ↑` rather than user-visible `Trace` controls.
- Detail graph x-axis is outdoor temperature `tj` shown as `Outdoor Temp [°C]`; `Bin Hours [h]` is a selectable y-series backed by `nj`.
- Do not introduce `BaseSection` or a shared result framework for the CSV export foundation.
- CSV export is currently limited to detail/bin table surfaces and table-shaped export hooks already approved for the Tkinter calculator; batch export parity should prefer CSV helper reuse over xlsx export.
- Batch table layout preflight should prioritize a unified two-row matrix layout for future profile expansion. Status is not a default output column; output columns should be actual profile result metrics, while blank/error state stays in row state, styling, or a compact status label.

## Deferred / Hold

- PyQt calculator source retirement remains on hold.
- Windows calculator_tk packaged size is approximately 11 MB and acceptable for the current deployment candidate.
- SASO follow-up polish is on hold (no concrete issue after 190-b smoke).
- Graph export/HTML export is deferred until after graph parity is stable.
- ResultPanel summary export/copy alignment is deferred unless manual smoke shows summary copy/export parity is still needed.
- MetricInputTable full-table copy enhancement is deferred after ResultPanel alignment.
- Internal formula trace is outside the current project execution scope and remains long-hold unless a separate core/data contract is approved.
- xlsx export is deferred; CSV parity is the current export target.
- Hong Kong HSPF detail/bin, EN/AHRI/KS detail/bin expansion, and batch calculator result are required follow-up work under Next Actions, but profile expansion should wait until result/detail/export common contracts, two-row batch foundation, main table migration candidate review, and ui_tk cleanup direction are checked.
- AS/NZS Excel compatibility Z-phase remains deferred.
- Historical ISO/KS/ASNZS workbook compatibility details stay outside this execution board.
- Code quality guardrail backlog is tracked in `docs/REFACTOR_PLAN.md`; revisit after ui_tk cleanup / controller switch slices expose real checker needs.

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
- `result_reports/summaries/221_summary-post-main-table-window-refit-arc.md`
  - Covers reports 202 through 221-b: main merge closeout, WPF spike closeout, calculator_tk batch/table foundation arc, selected-range fill paste, window refit policy, and 221-b local refit attempt. Report 221-c stays active as direct next-decision evidence.
- `result_reports/summaries/231_summary-architecture-uiux-boundary-and-window-refit-arc.md`
  - Covers reports 221-c through 228 plus 230-a through 230-d: dynamic refit stabilization, common refit owner, content-hugging shell/template, Clean Architecture boundary policy, and portable UI/UX document neutralization. Report 229 was kept active at that time and is now covered by summary 236.
- `result_reports/summaries/236_summary-window-dialog-batch-viewport-arc.md`
  - Covers reports 229, 231, 232, 233A through 233F guard, 234, and 235: visible measurement adapter, mapped-surface lifecycle, hidden-first window/dialog policy, batch dialog sizing/state/viewport wheel parity, router workflow slimming, and report self-reference workflow correction. No active reports are intentionally kept after this cleanup.

## Historical Notes / References

- Detailed completed task reports are archived in `result_reports/archive/`.
- Milestone decisions and lessons are in `project_log.md`.
- Compact recall facts are in `result_reports/memory/project_memory_seed.md`.
- UI/UX active SSOT starts at `docs/ui_ux/00_UI_UX_SYSTEM.md`.
- Current SASO T3 design reference: `docs/designs/2026-05-29-tkinter-saso-t3-profile-design.md`.
