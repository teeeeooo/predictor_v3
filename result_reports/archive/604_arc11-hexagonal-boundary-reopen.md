# Arc 11 Hexagonal Boundary Reopen

## Goal

Formalize `Arc 11 Reopen - Slice 0: Acceptance Reset / Hexagonal Boundary
Formalization` as a docs-only correction.

## Scope

- Reopened Arc 11 final architecture acceptance.
- Corrected Phase > Arc > Slice hierarchy.
- Routed Calculator boundary correction to Arc 12.
- Moved ML Pipeline Stabilization from Arc 12 to Arc 13.
- Created the active Arc 11 reopen design record.

## Audit Sources

- Work spec: `arc11_reopen_predict_train_hexagonal_boundary_work_spec_v2.md`.
- Owner docs: `AGENTS.md`, `AGENT_TASK_ROUTER.md`,
  `docs/agent_workflows/DIFF_READ_BUDGET.md`,
  `docs/agent_workflows/DOCUMENT_SYNC_AND_LIFECYCLE.md`,
  `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`,
  `docs/agent_workflows/ML_PREDICTOR_WORKFLOW.md`.
- Representative source confirmation: Predict controller/worker PySide/QThread
  ownership and Train service direct `train_all_models()` call.

## Findings

- Predict execution orchestration remains PySide6/QThread-bound.
- Production Train execution is not behind a killable outbound process adapter.
- Calculator has a real application-usecase boundary issue, but it belongs to
  Arc 12 and is excluded from Arc 11.

## Changed Files

- `docs/designs/2026-06-28-arc11-predict-train-hexagonal-boundary-reopen.md`
- `docs/designs/README.md`
- `docs/designs/2026-06-28-arc10-prediction-worker-progress-design.md`
- `docs/designs/2026-06-28-arc11-train-execution-boundary-design.md`
- `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`
- `docs/architecture/project_architecture.md`
- `docs/architecture/pyside6_train_predict_architecture.md`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `docs/REFACTOR_PLAN.md`
- `project_log.md`

## ACTIVE_DOCUMENTS Judgment

No change. The new file is a design record inventoried by
`docs/designs/README.md`; it does not create a new active owner relationship.

## Verification

- `git diff --check`: OK.
- `git status --short`: OK, only Slice 0 docs/report changes present before
  commit.
- `pytest`: skipped, docs-only.
- `py_compile`: skipped, docs-only.

## Known Risks

- Slice 0 does not implement Train process execution or Predict usecase ports.
- Manual smoke remains on hold until Slices 1-3 complete.

## Next Action

Arc 11 Slice 1 - Train Execution Port + QProcess Hard Stop.

## Project Memory Delta

- type: decision
  topic: Arc 11 hexagonal boundary reopen
  content: Arc 11 is reopened for Predict/Train execution boundary correction; Calculator usecase correction moves to Arc 12; former ML Pipeline Stabilization moves to Arc 13.
  keywords: arc11, hexagonal-boundary, train-execution, predict-usecase, calculator-arc12

## Commit / Push

- Commit: pending at report write time.
- Push: deferred until all Arc 11 slices complete.
