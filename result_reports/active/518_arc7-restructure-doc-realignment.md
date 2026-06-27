# 518 Arc 7 Restructure Doc Realignment

## Goal

Realign the project arc map before starting Arc 7 package restructuring.

## Scope

- Reframed Arc 7 as Core ML / Schema / Mapping Package Restructure.
- Moved calculator package movement to separate Arc 8.
- Kept PySide6 Predictor recovery, prediction worker/progress, and Trainer work
  after Arc 7/8.
- Updated near-term next action in `docs/WORK_PLAN.md`.
- Added a short Architecture SSOT note that ML/schema/mapping restructure and
  calculator engine movement are separate arcs.

## Changed Files

- `project_brief.md`
- `docs/WORK_PLAN.md`
- `docs/architecture/project_architecture.md`
- `result_reports/active/518_arc7-restructure-doc-realignment.md`

## Excluded

- No production code changes.
- No `core/`, `apps/`, `ui/`, `scripts/`, `tests/`, `data/`, or `model/`
  implementation changes.
- No calculator engine movement.
- No PySide6 Predictor recovery, worker/progress, or Trainer implementation.

## Verification

- `git diff --check`: run.
- `git status --short`: run.

Skipped:

- pytest: docs-only slice.
- GUI smoke: docs-only slice.
- packaging check: no dependency/package change.

## Next Action

Slice 2 - Package shell and boundary imports.
