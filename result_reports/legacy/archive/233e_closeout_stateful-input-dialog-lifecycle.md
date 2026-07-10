# 233E Closeout - Stateful Input Dialog Lifecycle Lesson

## Goal

Document the 233E design lesson so future batch tables, structured input dialogs, and stateful input surfaces do not lose user-entered rows/values on close/reopen.

## 233E UX Result

233E fixed the Hong Kong CSPF batch dialog state-loss issue:

- the parent CSPF section owns a session-local batch snapshot;
- the dialog remains the `Toplevel` shell / close lifecycle owner;
- the table remains the snapshot/restore owner;
- close stores the table snapshot and reopen restores it;
- app restart disk persistence was intentionally not introduced;
- the dialog was not kept alive with a withdraw/hide workaround.

The UX principle is now explicit: closing a stateful input shell is not reset/clear.

## 05 Policy Update

Updated `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` with a new `Stateful Input Surface Lifecycle` section:

- widget/shell lifecycle and user input state lifecycle must be separate;
- destroy-on-close requires a parent/controller/state owner to preserve a session-local snapshot;
- Reset/Clear must be an explicit user action;
- dialog shell, table/input snapshot behavior, and parent/controller state ownership have separate responsibilities;
- the rule applies to batch tables, repeated input matrices, structured input dialogs, and future profile-specific input surfaces;
- app restart persistence remains a separate product decision.

Acceptance/anti-pattern bullets were also updated so close/reopen state loss is directly checkable.

## UI Workflow Gate Update

Updated `docs/agent_workflows/UI_SURFACE_WORKFLOW.md` so UI surface work that touches stateful input dialogs or batch surfaces checks close/reopen state ownership before implementation.

The workflow now requires keeping dialog shell lifecycle, table/input snapshot behavior, and parent/controller state ownership separate.

## 07 Cross-reference

Updated `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md` with a one-line cross-reference to 05.

07 remains the geometry/viewport/shell lifecycle owner; user input state lifetime stays owned by 05.

## WORK_PLAN / Project Log

Updated `docs/WORK_PLAN.md` with the 233E closeout policy checkpoint while keeping the next action as 233F batch table viewport/scroll containment.

Merged a short lesson into the existing 2026-06-06 `project_log.md` entry instead of creating a duplicate entry.

## MVC / SoC Judgment

The documented boundary is:

- Shell/dialog: show/close lifecycle.
- Table/input surface: snapshot/restore behavior.
- Parent/controller state owner: session-local state lifetime.
- Reset/Clear: explicit user action.

This avoids mixing dialog lifecycle with calculation, export, viewport, or table layout responsibilities.

## Excluded Scope

Not changed:

- code;
- tests;
- batch viewport/scroll containment;
- copy/export/two-row matrix work;
- app restart persistence;
- reset/clear button design;
- result report lifecycle/archive.

## Validation

Executed:

- `git diff --check` - passed.
- `python3 -B tools/check_code_structure.py` - passed with one pre-existing soft warning: `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `git status --short` - expected modified/new docs files only.

Pytest and GUI smoke were not run because this was a documentation/policy workflow update.

## Next Action

233F - batch table viewport/scroll containment.
