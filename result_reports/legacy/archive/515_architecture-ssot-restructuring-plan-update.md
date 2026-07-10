# 515 Architecture SSOT Restructuring Plan Update

## Goal

Update project-wide architecture SSOT documents from the approved restructuring
plan.

## Source Document

- `docs/architecture/project_wide_architecture_restructuring_plan.md`

The plan was treated as source input, not re-decided.

## Changed Files

- `docs/architecture/project_wide_architecture_restructuring_plan.md`
- `docs/architecture/project_architecture.md`
- `docs/architecture/pyside6_train_predict_architecture.md`
- `project_brief.md`
- `docs/WORK_PLAN.md`
- `ACTIVE_DOCUMENTS.md`
- `docs/agent_workflows/ML_PREDICTOR_WORKFLOW.md`
- `result_reports/active/515_architecture-ssot-restructuring-plan-update.md`

## Reflected Architecture Decisions

- `core/` flat root is current compatibility surface, not final target.
- Final target package owners are `core/common`, `core/predictor_schema`,
  `core/mapping`, `core/ml`, and `core/calculators`.
- Compatibility wrappers are transition safety, not final architecture.
- Migration proceeds in no-behavior-change slices.
- ML implementation moves toward `core/ml`.
- Predictor schema and mapping move toward `core/predictor_schema` and
  `core/mapping`.
- Calculator implementation moves toward `core/calculators`, with engines under
  `core/calculators/standards`.
- PySide6 Predictor schema/mapping recovery resumes only after package
  boundaries are introduced.

## Excluded

- No production code changes.
- No `core/`, `apps/`, `ui/`, `scripts/`, `tests/`, `data/`, or `model/`
  implementation changes.
- No file moves, wrappers, PySide6 recovery, worker/progress, Trainer work,
  calculator behavior changes, ML algorithm changes, schema changes, fixture,
  golden, or public API changes.
- No report lifecycle movement.

## Verification

- Targeted restructuring wording search: run.
- `git diff --check`: run.
- `git status --short`: run.

Skipped:

- `pytest`: docs-only SSOT update.
- GUI smoke: docs-only SSOT update.
- packaging check: no dependency/package change.

## Next Action

Core package boundary foundation planning or implementation slice.
