# 233C Closeout - Hidden-first Window/Dialog Lifecycle Policy

## Goal

Document the lifecycle policy learned from the 233B/233C/233C-2 window work so
new windows, dialogs, Toplevels, and dynamic profile/page surfaces do not repeat
visible build/measure/resize flicker.

## Smoke / Audit Judgment

- 233B resolved Hong Kong lower blank space and kept the no-loop state.
- 233C unified profile switch, reselect, and detail toggle around one lifecycle
  refit request path.
- 233C-2 reused the valid Hong Kong metric surface on same-region return.
- Remaining flicker is soft but still visible. Further reduction would require
  hidden/offscreen first-show, transition freeze, or larger lifecycle-controller
  work, so it is accepted for the current arc unless future smoke identifies a
  specific remaining visible mutation owner.

## 07 Policy Update

Updated `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md` with:

- hidden-first lifecycle for new windows/dialogs/Toplevel-style shell surfaces:
  build, settle, snapshot measure, geometry/center apply, show;
- a distinction between preparing before first show and repeatedly hiding an
  already-visible shell;
- stable-container guidance for dynamic profile/page switches;
- a warning that repeated content-hugging on visible profile switches can
  flicker when content mutation and geometry mutation are not coalesced;
- acceptance checklist items for hidden-first first show and stable-container
  dynamic surfaces.

Concrete screen/toolkit names are treated as evidence, not scope boundaries.

## Router Update

Updated `AGENT_TASK_ROUTER.md` so UI work that creates or changes a window,
dialog, Toplevel, dynamic profile/page surface, viewport, or content-hugging
behavior must check 07 before implementation.

The router now asks agents to verify hidden-first or stable-container lifecycle
instead of ad hoc visible content build/measure/resize.

## README / Work Plan / Project Log

- `docs/ui_ux/README.md` now maps 07 as the owner for window/dialog geometry,
  viewport, hidden-first first-show lifecycle, and dynamic surface refit policy.
- `docs/WORK_PLAN.md` moves the next action to 233D batch dialog sizing/UX under
  the same window shell policy.
- `project_log.md` records that remaining soft flicker is accepted for this arc
  and future surfaces should use 07 hidden-first/stable-container lifecycle.

## MVC / SoC Judgment

This is a policy closeout. It keeps implementation ownership separate:

- shell lifecycle policy belongs in UI/UX 07;
- task routing belongs in the router;
- implementation stays out of this slice.

## Excluded

- No code changes.
- No tests changed.
- No batch dialog sizing implementation.
- No window shell/refit/measurement code changes.
- No architecture boundary rewrite.
- No report lifecycle/archive movement.

## Validation

- `git diff --check`: passed.
- `python3 -B tools/check_code_structure.py`: passed with existing warning:
  `ui_tk/sections/bin_detail_panel.py` exceeds the 400 LOC soft limit.
- `git status --short`: showed only expected policy/report changes before
  commit.

## Next Action

233D - batch dialog sizing/UX under the same window shell policy.
