# 250 Correct Summary 249 Windows Smoke Status Wording

## Goal

Update summary 249 to reflect that the 247 copy-all / CSV export Windows smoke
was confirmed, replacing the stale "pending user confirmation" wording.

## Scope

- Correct one line in `result_reports/summaries/249_summary-batch-two-row-matrix-and-reference-parity-arc.md`.
- No code, test, or UI changes.

## Corrected Wording

**Before:**
- 247 Windows smoke checklist (copy-all / CSV export) is pending user confirmation; no code blockers remain.

**After:**
- 247 Windows smoke: copy-all / CSV export behavior confirmed; no remaining manual smoke blocker for this arc.

## Files Changed

- `result_reports/summaries/249_summary-batch-two-row-matrix-and-reference-parity-arc.md`

## Validation

- `git diff --check`: clean
- `git status --short`: 1 file modified

## Excluded Scope

- No WORK_PLAN.md or project_log.md changes (no stale pending wording found there).
- No memory seed changes.
- No code/test/UI changes.

## Next

Result/detail/export common contract check.
