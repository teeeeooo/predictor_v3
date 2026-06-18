# 403 SCOP result surface status row fill

## Goal

Make the SCOP result surface status row fill its complete table width without
changing status text alignment, calculation, data, or layout structure.

## Scope

- Changed the status label grid stickiness from `w` to `ew` across its existing
  full-table column span.
- Preserved the label's left text anchor and existing result-value background.
- Added focused assertions to the existing SCOP GUI integration test.
- Updated `docs/WORK_PLAN.md` with the completed correction.

## Verification

- `python3 -B -m py_compile apps/calculator/ui/sections/en14825_scop_result_surface.py`
  OK.
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825_scop.py` OK:
  29 passed.
- `git diff --check` OK.
- `git status --short` reviewed.

## Next Action

EN14825 SCOP UI point availability manual smoke.
