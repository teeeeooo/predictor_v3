# 200 Active Report Lifecycle Cleanup

## Goal

- Clean `result_reports/active/` before the UI technology pivot design gate.
- Summarize the completed 196-a through 199-c arc and archive only reports covered by that summary.
- Leave active focused on the next decision target.

## Active Report Review

- Reviewed the active report list and compact headings/sections for goal, scope, manual check, verification, and next-action state.
- Covered arc classification:
  - input table replace-on-type hotfix
  - multi-monitor/window geometry hotfix
  - launch/detail auto-fit height cap
  - top-safe y policy cleanup
  - viewport UX policy documentation
  - UI/UX document numbering cleanup
- No reviewed report needed to remain active after summary coverage.

## Summary Created

- `result_reports/summaries/200_summary-window-geometry-viewport-ui-pivot-prep-arc.md`
  - Covers graph label closeout, MetricInputTable replace-on-type, geometry role split, 80% auto-fit cap, vertical/top-safe y policy, viewport policy documentation, calculator_tk packaging size closeout, and 199-c numbering cleanup.
  - Leaves UI technology pivot design gate as the next decision.

## Archived Reports

- `result_reports/archive/196a_graph-min-max-scale-label-hotfix.md`
- `result_reports/archive/197a_input-table-replace-on-type-hotfix.md`
- `result_reports/archive/197a2_input-table-replace-on-type-windows-followup.md`
- `result_reports/archive/197b_multi-monitor-geometry-role-split-hotfix.md`
- `result_reports/archive/198a_tkinter-launch-fit-saso-default-router-output-budget.md`
- `result_reports/archive/198b_detail-open-vertical-clamp-hotfix.md`
- `result_reports/archive/198c_auto-fit-height-cap-packaging-closeout.md`
- `result_reports/archive/198d_detail-open-vertical-clamp-bottom-margin-hotfix.md`
- `result_reports/archive/199a_window-geometry-top-safe-cleanup.md`
- `result_reports/archive/199b_window-geometry-viewport-policy.md`
- `result_reports/archive/199c_ui-ux-doc-numbering-cleanup.md`

## Active Left

- Before this report was created, `result_reports/active/` was empty after covered reports moved to archive.
- This 200 cleanup report remains active.

## Work Plan / Memory / Log

- `docs/WORK_PLAN.md`
  - Replaced detailed 196-a through 199-c bullets with a summary reference.
  - Kept next action as UI technology pivot design gate.
- `result_reports/memory/project_memory_seed.md`
  - Marked the older multi-monitor clipping open question as resolved/superseded.
  - Added one compact decision entry for the finalized window geometry/viewport policy and next UI pivot gate.
- `project_log.md`
  - Not updated; the summary plus memory seed entry is sufficient and avoids duplicating lifecycle detail.

## Verification

- Process check found no leftover pytest/python process beyond the check command itself.
- `python3 -B tools/check_code_structure.py`
  - Passed with existing soft-limit warning: `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- Lifecycle guard discovery found no report/archive/summary-specific tool under `tools/`.
- `ls result_reports/active`
  - Empty before creating this 200 cleanup report.
- `ls result_reports/archive | tail`
  - Showed the archived 197-a2 through 199-c reports.
- `ls result_reports/summaries | tail`
  - Showed `200_summary-window-geometry-viewport-ui-pivot-prep-arc.md`.
- `git diff --check`
  - Passed.
- `git status --short`, `git diff --name-only`, `git diff --stat`
  - Confirmed docs/report lifecycle-only changes.
- Pytest was not run because this was docs/report lifecycle-only.

## Excluded

- No code changes.
- No `ui_tk/`, C# WPF, PySide/PyQt migration, seasonal detail/trace adapter, router, AGENTS, UI/UX policy rewrite, or unrelated refactor changes.

## Project Memory Delta

- Updated `result_reports/memory/project_memory_seed.md` as described above.
