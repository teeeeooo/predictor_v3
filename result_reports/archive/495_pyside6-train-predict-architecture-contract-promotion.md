# 495 PySide6 Train/Predict Architecture Contract Promotion

## Goal

Promote the PySide6 Train/Predict implementation-facing spec from a design
record path into the governing architecture contract path, and align active
routing so future Train/Predict work discovers the contract without repeating a
prompt-specific read task.

## Scope

- Docs-only move and routing cleanup.
- No production code, tests, fixtures, golden data, model artifacts, dependency
  files, or legacy PyQt5 file moves/deletions.
- No PySide6 implementation started.
- No report lifecycle movement.
- No memory seed edit.

## Moved File

- From: `docs/designs/2026-06-27-pyside6-train-predict-ui-implementation-spec.md`
- To: `docs/architecture/pyside6_train_predict_architecture.md`

## Changed Files

- `ACTIVE_DOCUMENTS.md`
- `project_brief.md`
- `docs/WORK_PLAN.md`
- `docs/agent_workflows/ML_PREDICTOR_WORKFLOW.md`
- `docs/architecture/project_architecture.md`
- `docs/architecture/pyside6_train_predict_architecture.md`
- `docs/designs/2026-06-27-pyside6-train-predict-rewrite-design-gate.md`
- `docs/designs/README.md`
- `result_reports/active/493_pyside6-train-predict-doc-alignment.md`
- `result_reports/active/495_pyside6-train-predict-architecture-contract-promotion.md`

## Architecture Contract Judgment

The moved document defines package boundaries, entrypoint contracts, dependency
direction, PredictWorkspace ownership, state/controller/service/adapter/worker
responsibilities, implementation slices, and legacy `ui/` reference-only
policy. That scope is architecture contract ownership rather than a standalone
design reference.

## Routing Updates

- `ACTIVE_DOCUMENTS.md` now lists the new architecture contract as an active
  owner for app entrypoints, `apps/predict/`, `apps/train/`, PredictWorkspace,
  and responsibility boundaries.
- `ML_PREDICTOR_WORKFLOW.md`, `project_architecture.md`, `WORK_PLAN.md`, and
  `project_brief.md` now point Train/Predict implementation work to the new
  architecture contract path.
- `docs/designs/README.md` keeps the design gate as the design record and no
  longer lists the moved contract as a design record.
- The design gate now points to the architecture contract for governing
  implementation rules.
- Active report `493` was path-corrected because it remains in the active
  report set and was part of stale-path search scope.

## Verification

- `rg` stale-path/routing search - checked.
- `git diff --check` - passed during closeout.
- `git status --short` - checked during closeout.
- Cached change gate - passed against the staged docs-only scope.

Skipped:

- pytest: docs-only move/routing work.
- GUI smoke: no implementation or launch work.
- packaging check: no dependency/package changes.

## Known Risks

- This task only promotes and routes the contract. It does not validate PySide6
  imports, skeleton runtime behavior, or GUI smoke paths.
- The visual reference assets remain under `docs/designs/assets/` as
  non-binding layout references.

## Memory Seed

Not updated. This is a docs routing/ownership promotion. A future memory sync
could record the final architecture contract path after the PySide6 skeleton
slice confirms it in implementation.

## Next Action

PySide6 Train/Predict app skeleton implementation.

## Commit / Push

Final commit, push, and remote SHA match are reported in the terminal response
to avoid a self-referential report update loop.
