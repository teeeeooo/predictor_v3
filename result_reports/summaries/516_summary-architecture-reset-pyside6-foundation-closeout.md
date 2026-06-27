# 516 Summary - Architecture Reset and PySide6 Foundation Closeout

## Goal

Close out completed active reports after the Architecture SSOT update and keep
the active report folder focused on current blockers and next decisions.

## Covered Reports

- `491_report-lifecycle-cleanup-closeout.md`
- `492_calculator-final-closeout-audit.md`
- `507_archive-pyside6-train-predict-arc3-reports.md`
- `508_pyside6-routing-foundation-wording.md`
- `509_prediction-route-adapter-foundation.md`
- `510_prediction-result-mapping-foundation.md`
- `511_prediction-controller-foundation.md`
- `512_predict-workspace-execution-integration.md`
- `513_prediction-execution-arc4-closeout.md`
- `514_project-wide-architecture-reset-phase-alignment.md`
- `515_architecture-ssot-restructuring-plan-update.md`

## Completed Calculator Closeout Scope

- Calculator helper/batch/detail/manual-smoke lifecycle was summarized in
  `490_summary-calculator-helper-batch-lifecycle-closeout.md`.
- Final calculator audit in report `492` found no remaining calculator blocker.
- Calculator behavior, schema, config, fixture, golden data, public APIs, tests,
  and tools were not changed by this cleanup scope.

## Completed PySide6 Foundation Scope

- PySide6 Train/Predict routing now treats the work as production foundation,
  not disposable skeleton work.
- `app_predict.py` remains the Predict-only thin entrypoint.
- `app_train.py` remains the administrator/developer thin entrypoint that
  reuses Predict workspace in the Train app.
- New Train/Predict production UI code belongs under `apps/predict/` and
  `apps/train/`; legacy PyQt5 `ui/` remains reference-only.
- UI surface work routes through the UI Surface Workflow and relevant
  `docs/ui_ux/` contracts.

## Arc 4 Prediction Execution / Result Mapping Foundation

Completed foundation:

- `RowToMlInputAdapter` converts `CaseRow` input/autofill values toward the
  existing predictor route.
- `PredictionService` wraps `core.predictor.load_model(MODEL_FILE)` and
  `core.predictor.predict_row(...)`.
- `PredictionResultAdapter` maps service outcomes into `ResultRow` display data.
- `PredictionController` coordinates validation, service execution, result
  mapping, and `PredictSession` updates without letting widgets/table models
  call core ML directly.
- `PredictWorkspace` run button is connected to the controller/service
  foundation.
- Result lookup remains internal `case_id` based; Case ID is not user-facing.

## Schema / Mapping Recovery Gap

Remaining gap:

- PySide6 local schema/mapping/adapter drift remains a recovery target.
- Current PySide6 Predictor schema/mapping is not yet aligned with the existing
  ML pipeline and project-wide package ownership.
- Selected-row and dirty-row execution scopes remain follow-ups.
- Worker/progress/cancel UI is not implemented.
- Real-model prediction success smoke remains blocked in this checkout because
  `model/model.pkl` is absent.
- Spreadsheet table parity remains deferred: TSV copy/paste, clear, undo,
  Tab/Enter navigation, click/type replace-on-type, and validation rendering.

## Project-wide Architecture Reset Decision

- `core/` flat root is current compatibility surface, not final target.
- Continuing PySide6 Predictor recovery before architecture reset would deepen
  dependency on the wrong boundary.
- Architecture SSOT update is complete from
  `docs/architecture/project_wide_architecture_restructuring_plan.md`.

## Architecture SSOT Update Decision

Final target package owners:

- `core/common`
- `core/predictor_schema`
- `core/mapping`
- `core/ml`
- `core/calculators`

Compatibility wrapper lifetime rule:

- Compatibility wrappers are transition safety only.
- Wrappers preserve existing imports during migration.
- Wrappers are not final architecture and require explicit retirement planning
  after caller migration.

Migration order:

1. Core package boundary foundation.
2. ML implementation move.
3. Predictor schema / mapping move.
4. Calculator implementation move.
5. PySide6 Predictor schema/mapping recovery.
6. Prediction worker/progress.
7. Trainer app foundation.

## Active Retention Decision

The covered reports are completed history. This summary contains the durable
next-decision evidence needed for the next slice, so the covered active reports
can move to archive.

## Memory Seed

Not updated in this cleanup because the task explicitly disallowed direct memory
seed edits. Sync candidate: register this summary as the compact source for the
Architecture SSOT update, final package owners, compatibility-wrapper lifetime
rule, and PySide6 recovery dependency.

## Next Action

Core package boundary foundation planning or implementation slice.
