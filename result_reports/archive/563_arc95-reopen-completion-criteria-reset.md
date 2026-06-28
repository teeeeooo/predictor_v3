# 563 - Arc 9.5 Reopen Completion Criteria Reset

## Goal

Reopen Arc 9.5 because the previous closeout is not accepted as final
visual/table UX parity. Reset current project state from Arc 10 ready back to
Arc 9.5 Reopen and promote deferred spreadsheet baseline items to completion
blockers.

## Scope

- Reset `docs/WORK_PLAN.md` current slice, next actions, blockers, hold items,
  and reference anchors.
- Reset `project_brief.md` current phase and Arc 9.5 status.
- Correct the visual/table harvest so split input/result panes are not read as
  final acceptance.
- Include the user-provided local B-option `predict_ref_img.png` replacement as
  the current visual reference without editing its contents.

## Decision

Arc 9.5 remains active.

The previous Arc 9.5 closeout implemented useful visual foundation work, but it
deferred spreadsheet UX baseline items that must be completed before final
acceptance:

- grouped undo
- Tab / Shift+Tab / Enter / Shift+Enter navigation
- click/type replace-on-type
- mapping-backed per-row dropdown option updates

The user also replaced local `docs/designs/assets/predict_ref_img.png` with the
B-option unified case table reference. The split input/result table structure is
not accepted as the final Predict case-table UX.

## Changed Files

- `docs/WORK_PLAN.md`
- `project_brief.md`
- `docs/designs/2026-06-27-pyside6-visual-table-parity-harvest.md`
- `docs/designs/assets/predict_ref_img.png`
- `result_reports/active/563_arc95-reopen-completion-criteria-reset.md`

## Verification

- `git diff --check`: passed.
- `git status --short`: checked; Slice 1 docs, user-provided visual reference,
  and this report were dirty before commit.

Skipped:

- pytest: docs/reference reset only.
- GUI smoke: no code change.
- `tools/check_code_structure.py`: no source structure change.

## Known Risks

- Source still uses the split Predict table surface until later implementation
  slices.
- Real model success smoke remains blocked if `model/model.pkl` is absent.

## Commit / Push

- Commit: pending.
- Push: not run; Slice 11 only.

## Next

Slice 2 - Unified Case Table Design Contract.
