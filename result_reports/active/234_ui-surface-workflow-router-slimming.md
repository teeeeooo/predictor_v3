# 234 - UI Surface Workflow Router Slimming

## Goal

Move detailed UI surface workflow rules out of `AGENT_TASK_ROUTER.md` so the
router remains a short routing gate map and future UI table/window rules do not
keep accumulating in the router.

## Scope

Changed documentation only:

- new UI surface workflow owner;
- router slimming;
- active document inventory registration;
- compact work-plan/log synchronization.

No code or tests changed.

## Changes

- Added `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`.
  - Owns table surface gates.
  - Owns window/dialog/Toplevel/dynamic profile/page lifecycle gates.
  - Owns result/input/export surface gates.
  - Owns focused UI validation guidance.
- Slimmed `AGENT_TASK_ROUTER.md`.
  - Added a UI Surface Workflow quick route.
  - Replaced detailed UI table/window checklist text with owner routing.
  - Kept hard UI prohibitions and boundary routing.
- Updated `ACTIVE_DOCUMENTS.md`.
  - Registered the new workflow owner.
- Updated `docs/WORK_PLAN.md`.
  - Recorded that UI surface workflow details moved out of the router.
- Updated `project_log.md`.
  - Recorded the decision to move accumulating route checklist content into
    owner workflow documents.

## Rationale

The router was still too large after earlier workflow extraction because the UI
route carried detailed table, window/dialog, and validation checklists. Those
details are useful, but they are workflow content, not routing content. Keeping
them in a dedicated owner document reduces recurring token overhead when a task
only needs the route gate.

## Verification

- `git diff --check`: passed.
- `python3 -B tools/check_code_structure.py`: passed with existing warning:
  `ui_tk/sections/bin_detail_panel.py` exceeds the 400 LOC soft limit.
- `git status --short`: showed only expected workflow/router/report changes
  before commit.

Pytest and GUI smoke were not run because this is a documentation/router
cleanup with no code or test changes.

## Known Risks

- Future UI-specific checklist additions should go to
  `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`, not back into the router.
- The router still has shared guardrails and route-specific hard gates; this
  slice intentionally did not perform a full router rewrite.

## Commit / Push

Pending until final commit/push.
