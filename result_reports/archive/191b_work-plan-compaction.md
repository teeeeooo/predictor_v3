# 191-b WORK_PLAN Compaction

## Background

`docs/WORK_PLAN.md` had grown into a combined execution board, task log, decision history, and next-action archive. After 191-a summarized reports 184~190a2 and moved covered reports to archive, the detailed checkpoint chain no longer needed to stay in WORK_PLAN.

## Change

- Rebuilt WORK_PLAN as a compact current execution board.
- Added a short update rule that keeps detailed history in `project_log.md` and `result_reports/`.
- Preserved current focus on Tkinter ISO profile expansion.
- Preserved the next implementation action: `190-b SASO T3 implementation slice`.
- Kept only the active constraints and hold items needed for near-term execution.

## New WORK_PLAN Structure

- Purpose
- Work Plan Update Rule
- Current Focus
- Next Actions
- Active Constraints
- Deferred / Hold
- Recent Summaries
- Historical Notes / References

## Preserved Next Action

Next action remains **190-b SASO T3 implementation slice**:

- Dedicated `SASO T3` Tkinter section.
- Existing `saso_t3_cspf` profile/config path.
- Required-only 3-point vs optional-min 4-point section-local result comparison.
- No core/config/golden/fixture changes in the UI implementation slice.

## Reference Strategy

Closed details are traced through:

- `project_log.md`
- `result_reports/summaries/165_summary-pyqt-retirement-tkinter-ui-matrix-rules.md`
- `result_reports/summaries/180_summary-tkinter-calculator-ux-implementation-arc.md`
- `result_reports/summaries/191_summary-tkinter-iso-profile-expansion-arc.md`
- `result_reports/archive/`

## Excluded Scope

- No Python source changes.
- No tests changes.
- No SASO implementation.
- No summary/archive lifecycle move.
- No changes to project memory, project log, design docs, or router rules.

## Verification

- `python3 -B tools/check_code_structure.py`
- `git diff --check`
- `git status --short`
- `git diff --name-only`
- `git diff --stat`

## Next Action

Proceed to **190-b SASO T3 implementation slice**.
