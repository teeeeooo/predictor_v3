# 234 - Agent Router Workflow Slimming

## Goal

Move detailed workflow rules out of `AGENT_TASK_ROUTER.md` so the router remains
a short route/gate map. The target was to reduce the router from roughly 500
lines toward the 200-300 line range while preserving hard gates and owner
routing.

## Scope

Changed documentation only:

- new UI surface, calculator, ML/Predictor, and packaging workflow owners;
- router rewrite to compact route/gate map form;
- active document inventory registration;
- compact work-plan/log synchronization.

No code or tests changed.

## Changes

- Added `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`.
  - Owns table surface gates.
  - Owns window/dialog/Toplevel/dynamic profile/page lifecycle gates.
  - Owns result/input/export surface gates.
  - Owns focused UI validation guidance.
- Added `docs/agent_workflows/CALCULATOR_WORKFLOW.md`.
  - Owns calculator, region, golden, validation, and Excel COM packet workflow.
- Added `docs/agent_workflows/ML_PREDICTOR_WORKFLOW.md`.
  - Owns ML/Predictor route details and hard feature/model boundaries.
- Added `docs/agent_workflows/PACKAGING_WORKFLOW.md`.
  - Owns packaging and deployment-build route details.
- Slimmed `AGENT_TASK_ROUTER.md`.
  - Replaced detailed route bodies with compact owner routing and hard gates.
  - Reduced the router to 275 lines.
- Updated `ACTIVE_DOCUMENTS.md`.
  - Registered the new workflow owners.
- Updated `docs/WORK_PLAN.md`.
  - Recorded that router details moved into workflow owners.
- Updated `project_log.md`.
  - Recorded the decision to keep router as compact route/gate map.

## Rationale

The router was still too large after earlier workflow extraction because
multiple routes carried detailed procedures. Those details are useful, but they
belong in workflow owners, not in the routing map. Moving them reduces recurring
token overhead when a task only needs the route gate.

## Verification

- `git diff --check`: passed.
- `python3 -B tools/check_code_structure.py`: passed with existing warning:
  `ui_tk/sections/bin_detail_panel.py` exceeds the 400 LOC soft limit.
- `wc -l AGENT_TASK_ROUTER.md`: 275 lines.
- `git status --short`: showed only expected workflow/router/report changes
  before commit.

Pytest and GUI smoke were not run because this is a documentation/router
cleanup with no code or test changes.

## Known Risks

- Future route-specific checklist additions should go to the matching
  `docs/agent_workflows/*` owner, not back into the router.
- Router hard gates are intentionally compact; details now require following the
  linked workflow owner.

## Commit / Push

Pending until final commit/push.
