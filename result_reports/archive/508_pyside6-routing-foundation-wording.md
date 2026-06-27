# 508 PySide6 Routing Foundation Wording

## Goal

Correct PySide6 Train/Predict wording from disposable `skeleton` language toward
production `foundation` language, and strengthen ML/Predictor to UI surface
cross-routing before Arc 4.

## Scope

- Docs-only update.
- No production code, tests, fixtures, golden data, model artifacts, dependency
  files, data files, or legacy `ui/` files changed.
- No PySide6 implementation or Arc 4 implementation started.
- No report lifecycle movement.

## Changed Files

- `AGENT_TASK_ROUTER.md`
- `project_brief.md`
- `docs/WORK_PLAN.md`
- `docs/agent_workflows/ML_PREDICTOR_WORKFLOW.md`
- `docs/architecture/pyside6_train_predict_architecture.md`
- `result_reports/active/507_archive-pyside6-train-predict-arc3-reports.md`
- `result_reports/active/508_pyside6-routing-foundation-wording.md`

## Wording Correction

- Updated current/next execution wording in `docs/WORK_PLAN.md` to
  `foundation`.
- Updated project brief Arc 2 wording from package `skeleton` to package
  `foundation`.
- Updated architecture contract first-slice wording to describe first production
  foundation structures and slices.
- Updated active report `507` next-action wording to Arc 4 prediction execution
  and result mapping foundation.

Archived report filenames and historical report wording were not renamed or
rewritten.

## Cross-routing

- `docs/agent_workflows/ML_PREDICTOR_WORKFLOW.md` now routes Train/Predict UI
  surface work to `UI_SURFACE_WORKFLOW.md` and relevant `docs/ui_ux/` owners.
- Table surfaces now point to
  `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`.
- Input/result surfaces now point to
  `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`.
- Missing PySide6 table adapter coverage must be reported as an adapter gap
  while using the toolkit-neutral table contract as acceptance criteria.
- `AGENT_TASK_ROUTER.md` received only a short ML/Predictor conditional routing
  line so the router remains a route map.

## Architecture Boundary Note

`docs/architecture/pyside6_train_predict_architecture.md` now states that it
owns package/dependency/state/controller/service/adapter/worker/entrypoint
boundaries, while user-facing behavior, table parity, terminology, and
input/result surface acceptance remain owned by UI/UX contracts.

## Verification

- `git diff --check` - passed.
- `git status --short` - checked.
- Targeted wording/routing search - checked.
- Cached change gate - passed.

Skipped:

- pytest: docs-only work.
- GUI smoke: docs-only work.
- packaging check: no dependency/package changes.

## Known Risks

- Archived report filenames still contain `skeleton` where that was the original
  committed artifact name; those were not renamed to avoid report lifecycle
  churn.
- PySide6-specific table adapter remains a future gap; current routing points
  to the toolkit-neutral table contract.

## Next Action

Arc 4 - prediction execution and result mapping foundation.

## Commit / Push

Commit and push are performed for this docs-only closeout.
