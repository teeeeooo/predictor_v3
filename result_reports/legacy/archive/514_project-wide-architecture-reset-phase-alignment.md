# 514 Project-wide Architecture Reset Phase Alignment

## Goal

Realign project phase docs before further PySide6 Predictor recovery.

Recent review found the next issue is not only inside the PySide6 app: current
`core/` mixes ML pipeline, calculator engines, shared utilities, and
constants/schema in a flat public surface. Continuing PySide6 schema/mapping
recovery first would harden that structure into new code.

## Scope

- Reordered the near-term project arc sequence around a project-wide
  architecture audit.
- Marked Arc 4 prediction execution/result mapping as production foundation
  with a remaining schema/mapping recovery gap.
- Clarified that `core/` flat structure is accepted as current public surface,
  not final target structure.
- Added a PySide6 architecture dependency note: schema/mapping recovery waits
  for project-wide architecture audit and core package boundary decisions.

## Changed Files

- `project_brief.md`
- `docs/WORK_PLAN.md`
- `docs/architecture/project_architecture.md`
- `docs/architecture/pyside6_train_predict_architecture.md`
- `result_reports/active/514_project-wide-architecture-reset-phase-alignment.md`

## New Phase / Arc Order

1. Project-wide architecture audit / restructuring plan.
2. Architecture SSOT update.
3. Core package boundary foundation: no behavior change, compatibility
   wrappers, focused tests/import smoke.
4. PySide6 Predictor schema/mapping recovery.
5. Prediction worker/progress.
6. Trainer app foundation.

## Decision

PySide6 recovery is paused because the current Predictor schema/mapping path is
not aligned enough with the existing ML pipeline and project-wide core
ownership. The audit must decide package boundaries and wrapper strategy before
more recovery code depends on today’s flat `core/` layout.

## Excluded

- No production code changes.
- No `core/`, `apps/`, `ui/`, `scripts/`, `tests/`, `data/`, or `model/` file
  changes.
- No calculator, ML pipeline, PySide6 recovery, worker/progress, Trainer, or
  package-boundary implementation.
- No report lifecycle movement.

## Verification

- `rg` stale/target wording check: run.
- `git diff --check`: run.
- `git status --short`: run.

Skipped:

- `pytest`: docs-only phase alignment.
- GUI smoke: docs-only phase alignment.
- packaging check: no dependency/package change.

## Known Risks

- The architecture audit still needs to decide the actual target package tree;
  this report intentionally does not define it.
- Active report count remains above the usual cleanup comfort zone; lifecycle
  cleanup can be handled as a separate follow-up.

## Commit / Push

Completed in the task closeout; final local/remote SHA match is reported in the
terminal response.

## Next Action

Project-wide architecture audit / restructuring plan.
