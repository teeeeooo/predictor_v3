# 221A — Window Geometry Policy Nested Refit

## Goal

Document the nested notebook / dynamic sub-tab refit rule before changing the
Hong Kong Tkinter implementation.

## Checked Documents

- `result_reports/active/220_selected-range-fill-paste-and-main-sizing-follow-up.md`
- `docs/ui_ux/00_UI_UX_SYSTEM.md`
- `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`
- `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`
- `ACTIVE_DOCUMENTS.md`
- `docs/WORK_PLAN.md`
- recent `project_log.md` entries

## 220 Smoke Issue

220 resolved selected-range fill paste, but Windows smoke still found the Hong
Kong CSPF main screen lower blank space. The issue persists after profile
switching back to Hong Kong, while opening and closing detail restores a better
height. That points to nested notebook / dynamic sub-tab geometry settling
rather than a one-off Hong Kong sizing constant.

## Policy Update

`docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md` now defines a
toolkit-neutral nested notebook / dynamic sub-tab refit rule:

- hidden tab width may be protected, but automatic fit height should follow the
  currently visible sub-tab;
- profile switch, nested tab switch, and detail toggle should share the same
  refit scheduling policy;
- a later settled refit is allowed when the first post-render fit is not
  stable enough;
- nested tab changes are refit triggers;
- hidden-tab measurement must suppress tab-change refit callbacks;
- measurement and mutation must not create synchronous configure loops;
- preferred-size/refit scheduling should be guarded by helper or fake-trigger
  tests where possible.

The acceptance checklist now includes nested notebook refit and hidden-tab
measurement behavior.

## ACTIVE_DOCUMENTS Update

`ACTIVE_DOCUMENTS.md` now registers
`docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md` as the active owner for
window geometry, viewport, and auto-fit policy. The entry maps inbound usage
from UI/UX root, layout/window geometry tasks, and nested notebook/detail refit
tasks to toolkit adapters and app shell/window geometry helpers.

## WORK_PLAN Update

`docs/WORK_PLAN.md` now marks selected-range fill paste as resolved by 220 and
sets the next action to Hong Kong nested notebook refit scheduling correction.
The next implementation scope is limited to metric notebook tab-change refit,
settled refit scheduling, measurement suppress guard, and profile / metric tab /
detail toggle refit paths.

## Project Log

`project_log.md` received a compact decision entry noting that lower blank
space recovery after detail toggle indicates a layout-settle/refit scheduling
problem, and that the policy belongs in the 07 window geometry document while
the Hong Kong code correction remains a separate follow-up.

## Code Changes

None. This task intentionally did not modify `ui_tk/`, tests, calculator core,
region config, or table foundation code.

## Excluded Scope

- no Hong Kong refit scheduling implementation;
- no `window_geometry.py` or `iso16358_tab.py` changes;
- no table foundation changes;
- no main table migration;
- no docs/designs or archive work;
- no report lifecycle/archive maintenance.

## Validation

- `git diff --check` — passed.
- `python3 -B tools/check_code_structure.py` — passed with the existing soft
  warning that `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `git status --short` — reviewed before commit.

Not run:

- pytest — documentation-only task with no code/test changes.
- GUI smoke — no UI code changes.

## Next Action

Hong Kong nested notebook refit scheduling correction.
