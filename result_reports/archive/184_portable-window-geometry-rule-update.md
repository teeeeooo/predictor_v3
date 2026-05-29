# 184 Portable Window Geometry Rule Update

## Goal

Document the window geometry / scroll container / resize stability
learnings from the Tkinter calculator UI smoke-loop as portable UI/UX
rules.

## Scope

- Update `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md` §8 with initial
  geometry order of operations, separation of concerns, and event-loop
  safety rules.
- Add a gate to `AGENT_TASK_ROUTER.md` §8 requiring agents to check the
  window geometry rule before modifying GUI app shell, initial window
  geometry, scroll container, resize handling, or scrollbar visibility.
- Add a documentation checkpoint entry to `docs/WORK_PLAN.md`.

## Non-goals

- No Python source or test changes.
- No lifecycle summary/archive maintenance.
- No project_log.md or project_memory_seed.md updates.

## Changed Files

1. `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`
   - §8.1 Initial geometry order of operations (render → measure →
     content safety margin → screen cap → center).
   - §8.2 Separation of concerns (initial geometry vs resize minimum
     vs screen cap vs scrollbar visibility).
   - §8.3 Event-loop safety (no geometry/pack/sync loop inside
     Configure handler).
2. `AGENT_TASK_ROUTER.md`
   - §8 UI 수정 route: added conditional document reference to
     `02_DESIGN_TOKENS_AND_LAYOUT.md` §8 for window geometry work.
   - Added step 6 in the procedure: gate check for root requested size,
     preferred size, separation of concerns, and Configure loop
     prevention.
3. `docs/WORK_PLAN.md`
   - Added task 4g-m (184) entry documenting the portable rule update.

## Verification

- `python3 -B tools/check_code_structure.py`: OK (no findings).
- `git diff --check`: clean.
- No Python source/test changes.

## Next Action

- Continue manual smoke verification for the Tkinter calculator.
- Evaluate whether an active report lifecycle summary is needed.
