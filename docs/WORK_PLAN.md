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
- Next: 193-a manual smoke, then choose the next trace/export follow-up slice.

## Next Actions

1. **193-a manual smoke**
   - Check SASO trace expand/collapse, optional 35 Min states, and profile switching.
2. **Table CSV export foundation**
   - Add export for table-shaped result/trace surfaces after trace behavior settles.
3. **Bin graph parity**
   - Graph implementation remains a later slice; graph export follows graph parity.
4. **Hong Kong trace implementation**
   - Split CSPF and HSPF based on the 193-a availability audit.

## Active Constraints

- Use Design First Gate for larger UI/profile/result work; hotfix and micro cleanup stay scoped exceptions.
- Apply Diff / Read Budget: reuse already-confirmed policy/design context, inspect targeted functions/sections only, and avoid long compliance reprints.
- For SASO follow-ups, avoid core calculator, profile registry, region config, golden, and fixture changes unless a separate design slice approves them.
- Do not run full pytest unless explicitly requested; use focused smoke and relevant tests.
- Keep comparison result surfaces section-local until repeated reuse proves a shared framework is necessary.
- Do not change `ResultPanel` for SASO/2-point comparison unless a later design slice explicitly chooses that path.

## Deferred / Hold

- PyQt calculator source retirement remains on hold.
- Windows PyInstaller size measurement remains pending until a Windows host is available.
- SASO follow-up polish is on hold (no concrete issue after 190-b smoke).
- Hong Kong CSPF/HSPF trace availability audit completed in 193-a; CSPF can likely use `BinTraceTable`, while HSPF needs a heating trace schema decision.
- Graph export follows graph parity and may use SPOT-style HTML export.
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
  - Tracks SASO T3 `bin_details` trace implementation and Hong Kong trace availability audit until manual smoke.

## Historical Notes / References

- Detailed completed task reports are archived in `result_reports/archive/`.
- Milestone decisions and lessons are in `project_log.md`.
- Compact recall facts are in `result_reports/memory/project_memory_seed.md`.
- UI/UX active SSOT starts at `docs/ui_ux/00_UI_UX_SYSTEM.md`.
- Current SASO T3 design owner: `docs/designs/2026-05-29-tkinter-saso-t3-profile-design.md`.
