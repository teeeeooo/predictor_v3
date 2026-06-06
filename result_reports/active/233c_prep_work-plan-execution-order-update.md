# 233C-prep - Work Plan Execution Order Update

## Goal

Update the execution order after 233B Windows smoke and the batch layout
decision. This is a planning/log update only.

## Work Plan Update

- Recorded that 233B resolved Hong Kong lower blank space and preserved the
  no-loop state.
- Recorded that profile/detail flicker remains visible, so the next window task
  is 233C lifecycle orchestration unification.
- Reordered Next Actions around:
  1. profile switch / reselect / detail toggle lifecycle orchestration;
  2. batch dialog sizing under the same window shell policy;
  3. Windows smoke for main and batch sizing;
  4. two-row batch matrix layout preflight and foundation;
  5. batch copy-all / CSV export parity;
  6. result/detail/export contract checks, main table migration candidate
     review, ui_tk cleanup, and later profile expansion.

## Batch Layout Decision

- Batch layout should evaluate a unified case-level two-row matrix shape before
  HSPF/EN14825/AHRI/KS profile expansion.
- Status is not a default batch output column.
- Result columns should be actual profile metrics. Current Hong Kong CSPF batch
  output columns are CSPF and CSEC.
- Blank/error state should stay in internal row state, styling, or compact
  status labeling.

## Export Decision

- Batch table copy/export is a table/export arc, not a window sizing arc.
- CSV export should reuse the existing clipboard/CSV helper direction.
- xlsx export stays deferred.

## Project Log

Merged the decision into the existing 2026-06-06 architecture/window-boundary
entry instead of adding a new heading.

## Excluded

- No code changes.
- No tests changed.
- No UI/UX or architecture policy document changes.
- No 233C implementation.
- No batch two-row matrix implementation.
- No batch export implementation.

## Validation

- `git diff --check`: passed.
- `python3 -B tools/check_code_structure.py`: passed with existing warning:
  `ui_tk/sections/bin_detail_panel.py` exceeds the 400 LOC soft limit.
- `git status --short`: showed only expected planning/report changes before
  commit.

## Next Action

233C - profile switch / reselect / detail toggle lifecycle orchestration
unification.
