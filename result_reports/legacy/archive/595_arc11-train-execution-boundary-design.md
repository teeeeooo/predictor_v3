# Arc 11 Train Execution Boundary Design

## Goal

Define the Arc 11 Train execution boundary before implementation.

## Scope

- Added the Arc 11 design record.
- Updated the PySide6 Train/Predict architecture contract with Train service,
  worker, controller, UI, cancellation, and DEV-only smoke backend boundaries.
- Updated the near-term work plan to move from boundary design to service
  contracts.

## Non-goals

- No production code changes.
- No tests changed.
- No mock generator changes.
- No core ML, calculator, mapping schema, or Data Mapping execution changes.

## Decisions

- Production default path wraps `core.ml.training.train_all_models` through a
  Qt-free `TrainingService`.
- Train execution is owned by `apps/train/services`, `apps/train/workers`, and
  `apps/train/controllers`, with UI limited to rendering and action forwarding.
- DEV-only Train E2E smoke belongs under `tools/dev/mock_smoke/` and reuses the
  existing mock artifact generation contract.
- Production cancellation is cooperative/requested only unless the core training
  backend later exposes a safe interruption contract.

## Code Map Reuse Gate

- `reuse_commonization`: checked
- Checked `controller`, `worker`, `training`, and `mock_smoke` references in
  `docs/code_map/CODEBASE_REFERENCE_MAP.md`.
- Reuse candidate: Predict controller/worker lifecycle and existing mock smoke
  generator/smoke runner patterns.
- No common controller/worker extraction in this slice because Train result,
  progress, cancellation, and artifact semantics differ from row prediction.

## Verification

- `git diff --check`: PASS
- `git status --short`: PASS, only intended Slice 1 docs/report files changed
- `python3 -B tools/check_code_structure.py`: skipped for docs-only slice

## Changed Files

- `docs/designs/2026-06-28-arc11-train-execution-boundary-design.md`
- `docs/architecture/pyside6_train_predict_architecture.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/595_arc11-train-execution-boundary-design.md`

## Known Risks

- Implementation slices still need to prove thread cleanup, UI wiring, and
  DEV-only E2E smoke behavior.
- Real production training smoke remains optional and expensive.

## Next Suggested Action

Arc 11 Slice 2 — Training Service Contracts.

## Commit / Push

- Commit: included in Slice 1 commit
- Push: not pushed
