# 233F Guard - UI Source-of-truth Reuse and Soft LOC Preflight

## Goal

Strengthen the UI workflow so new table/viewport/dialog work first checks existing working surfaces as source-of-truth evidence and treats soft LOC limits as preflight triggers rather than late rework signals.

## 233F Smoke NG Cause

233F added internal viewport containment for the Hong Kong CSPF batch table. Windows smoke then showed a parity gap: mouse-wheel scrolling did not work when the pointer was over table/cell/entry content, while an existing main surface already had normal wheel scrolling UX.

The failure was not only missing wheel validation. The workflow did not strongly require checking an existing working surface as source-of-truth evidence before creating a new helper.

233F also initially let `BatchCaseTable` cross the 400 LOC soft limit before helper extraction. The structure guard worked as a commit-time check, but it was applied too late to avoid rework.

## Table Surface Gate Update

Updated `docs/agent_workflows/UI_SURFACE_WORKFLOW.md` so table-shaped UI work must:

- check existing surfaces that already implement the same or similar user-visible behavior before creating a new helper/adapter;
- treat table scroll, wheel routing, paste/copy, selection, export, and viewport containment as user-behavior parity requirements;
- prefer the existing owner/helper/adapter when it fits;
- record incompatibility or reuse-blocking reasons before implementation if not reused;
- keep Windows/manual smoke parity gaps as validation gaps with automated guard candidates.

This is not a mandatory-reuse rule. It is a source-of-truth/reuse/parity decision gate.

## Preflight Structure Guard Update

Updated the same workflow so soft LOC limits are explicit preflight triggers:

- 400 LOC-style warnings are not hard failures;
- soft limit proximity or excess does not automatically require extraction;
- before implementation, decide whether the new responsibility is a distinct helper/adapter concern, likely to repeat, or likely to mix owner boundaries;
- extract only when responsibility boundaries are clear;
- do not split code merely to satisfy a line-count number;
- `check_code_structure.py` may be used as a preflight guard for structure-impacting UI work, not only as a commit-time validator.

## WORK_PLAN / Project Log

Updated `docs/WORK_PLAN.md`:

- recorded the 233F mouse-wheel parity NG;
- changed next action to `233F-fix batch viewport reuse/parity correction`;
- kept 234A two-row matrix preflight after the fix/smoke path.

Merged the lesson into the current `project_log.md` entry rather than creating a duplicate dated section.

## MVC / SoC Judgment

The guard reinforces owner-boundary practice:

- working UI surfaces can be source-of-truth evidence for behavior;
- new helpers must prove user-visible parity, not just structural similarity;
- soft LOC guard is a preflight signal for boundary analysis, not a line-count-only refactor trigger.

## Excluded Scope

Not changed:

- code;
- tests;
- batch viewport/mouse-wheel implementation;
- table/export/two-row matrix work;
- UI/UX 03/05/07 policy docs;
- AGENTS or router;
- report lifecycle/archive.

## Validation

Executed:

- `git diff --check` - passed.
- `python3 -B tools/check_code_structure.py` - passed with one pre-existing soft warning: `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `git status --short` - expected modified/new docs files only.

Pytest and GUI smoke were not run because this was a documentation/workflow guard update.

## Next Action

233F-fix - batch viewport reuse/parity correction.
