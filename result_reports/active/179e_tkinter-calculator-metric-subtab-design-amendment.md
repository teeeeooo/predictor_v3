# 179e: Tkinter Calculator Metric Sub-tab Design Amendment

## Goal

Amend the Tkinter calculator final UX contract so that metric sub-tabs (or
equivalent segmented metric navigation) inside a standard tab are permitted
when content density makes a single vertical view impractical.

## Scope

- Audit existing decisions in the Tkinter final UX contract, matrix/result
  surface rules, and summary reports.
- Update `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md`
  to allow metric sub-tabs while keeping top-level standard tabs, region
  selector, and rejected alternatives (no per-region tabs, no standard-tab
  replacement).
- Update `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` to clarify
  that metric navigation is outside the surface-shaping rule scope.
- Add task 179-e to `docs/WORK_PLAN.md`.

## Non-goals

- No Python source or test changes.
- No graph/detail surface implementation.
- No theme, packaging, or PyQt retirement actions.

## Changed Files

1. `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md`
   - Information Architecture: same-view remains the default, but metric
     sub-tabs are permitted for high-density cases.
   - Rejected alternatives updated: metric sub-tabs inside a standard tab
     are no longer classified as rejected nested tabs.
   - EN 14825 and AHRI 210/240 explicitly linked to the same principle.
2. `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`
   - Scope: added note that metric navigation (sub-tabs/segmented controls)
     is an IA/design-contract concern, not a surface-shaping rule concern.
3. `docs/WORK_PLAN.md`
   - Added task 4g-l (179-e) entry with amendment rationale and next actions.

## Verification

- `git diff --check`: clean.
- `python3 -B tools/check_code_structure.py`: OK (no findings).
- Only docs files modified; no source/test changes.

## Known Risks

- Amendment does not resolve the underlying geometry/scroll issues by itself;
  implementation smoke will be needed after the metric sub-tab code change.

## Next Suggested Action

1. **ISO Hong Kong CSPF/HSPF metric sub-tab implementation** — introduce a
   metric sub-tab inside `ui_tk/tabs/iso16358_tab.py` and run manual smoke.
2. Continue geometry/scroll refinement (tasks 178/179-b/c/d) in parallel if
   width/height ratio fixes are still needed after sub-tab separation.
