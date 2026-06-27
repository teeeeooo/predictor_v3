# 494 Project Brief PySide6 Phase Rewrite

## Goal

Rewrite `project_brief.md` so it reflects the current ML / Predictor
Continuation phase with PySide6 Train/Predict rewrite as the active arc map.

## Scope

- Docs-only update.
- Local checkout state was checked first; report `493`, the PySide6 design
  gate/spec, and both visual reference assets exist locally.
- Updated `project_brief.md` only for the brief rewrite.

## Changed Files

- `project_brief.md`
- `result_reports/active/494_project-brief-pyside6-phase-rewrite.md`

## Project Brief Rewrite Summary

- Kept the Purpose / ownership section.
- Set current phase to `ML / Predictor Continuation — PySide6 Train/Predict
  Rewrite`.
- Compressed completed EN14825/AHRI/calculator-helper work into a Previous
  Completed Phase section with summary anchors only.
- Removed detailed completed calculator milestone lists from the active arc map.
- Rebuilt the current arc map around:
  - PySide6 Train/Predict design alignment;
  - PySide6 package skeleton and app boundary;
  - reusable variable-size `PredictWorkspace`;
  - prediction execution/result mapping;
  - Trainer admin app;
  - ML pipeline stabilization;
  - later calculator-to-predictor integration.
- Preserved the boundary that legacy PyQt5 `ui/` Train/Predict files are
  reference-only until a later retirement slice.

## WORK_PLAN Consistency

No `docs/WORK_PLAN.md` edit was needed for this task. It already points next to
PySide6 Train/Predict rewrite implementation preflight followed by the skeleton
slice.

## Verification

- `git diff --check` - passed.
- `git status --short` - checked. The working tree also contains the prior
  uncommitted PySide6 docs alignment files from report `493`.
- Targeted project-state search - checked stale calculator-phase terms and
  PySide6 boundary wording. The brief now points to the PySide6 Train/Predict
  phase and no longer keeps the detailed completed calculator arc map.

Skipped:

- pytest: docs-only work.
- GUI smoke: no implementation work.
- packaging check: no dependency/package work.

## Excluded Scope

- No production code changes.
- No tests, fixtures, golden data, model artifacts, or dependency files changed.
- No PySide6 implementation started.
- No legacy PyQt5 `ui/` files deleted or moved.
- No design-doc body rewrite beyond previously existing local docs.
- No report lifecycle movement.
- No memory seed update.

## Memory Seed

Not updated. This brief rewrite may become a memory seed sync candidate after a
future summary closes the PySide6 preflight/skeleton phase.

## Next Action

Run PySide6 Train/Predict rewrite implementation preflight.
