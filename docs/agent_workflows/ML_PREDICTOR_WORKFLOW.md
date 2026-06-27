# ML / Predictor Workflow

## Role

This document owns ML/Predictor route details. `AGENT_TASK_ROUTER.md` only keeps
the short routing gate.

## Hard Boundaries

- Keep `app_train.py` and `app_predict.py` separate.
- For the approved Train/Predict rewrite, treat `app_predict.py` as the
  Predict-only thin entrypoint and `app_train.py` as the administrator/developer
  thin entrypoint for Predict + Train / Model + Data Mapping.
- New Train/Predict UI code targets PySide6 under `apps/predict/` and
  `apps/train/`; the legacy `ui/` path is retired and must not be imported by
  production Train/Predict code.
- Do not import `optuna`, `sklearn`, `shap`, or `matplotlib` from
  `core/predictor.py`.
- Until package-boundary migration changes the approved owner, keep `COLUMNS`
  in `core/constants.py` and `MODEL_REGISTRY` in `core/models.py`.
- After the core package boundary foundation exists, new ML/Predictor code must
  follow the approved package owner paths from `docs/architecture/project_architecture.md`.
- Preserve `feature_names_in_`; do not add `.values` conversion before
  `model.fit()`.
- Cooling and Heating models remain independent; do not combine them with
  MultiOutput.
- Preserve monotone constraints and physical constraints over purely
  statistical convenience.

## Owner Documents

- Feature engineering, physical constraints, data quality, monotonicity,
  target leakage, and extrapolation risk:
  `docs/knowledge/README.md` and relevant knowledge docs.
- ML schema/feature boundary or calculator input/output boundary:
  `docs/architecture/project_architecture.md`.
- Project-wide architecture restructuring source input:
  `docs/architecture/project_wide_architecture_restructuring_plan.md`.
- Train/Predict PySide6 rewrite architecture contract:
  `docs/architecture/pyside6_train_predict_architecture.md`; design decision
  record:
  `docs/designs/2026-06-27-pyside6-train-predict-rewrite-design-gate.md`.
- Train/Predict UI surface work also applies
  `docs/agent_workflows/UI_SURFACE_WORKFLOW.md` and relevant `docs/ui_ux/`
  owners. Table surfaces use
  `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`; input/result surfaces use
  `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`. If no PySide6 table
  adapter exists yet, report the adapter gap and use the toolkit-neutral table
  contract as the acceptance contract.
- Project-wide responsibility boundaries:
  `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`.

## Flow

1. Search for the target feature, model, predictor, or registry first.
2. Read only the needed function/class range.
3. Confirm feature names, target leakage risk, cooling/heating separation, and
   monotonicity before editing.
4. Keep ML feature schema separate from calculator core, region config, and UI
   table schemas.
5. For `apps/predict/ui`, `apps/train/ui`, table, input/result/detail/export,
   or user-facing surface changes, apply the UI Surface Workflow and UI/UX owner
   docs alongside the architecture contract.
6. Run focused model/feature tests or import smoke for the changed owner.

## Forbidden Evidence Use

Do not use `docs/knowledge` content as authority to change calculator formulas,
fixtures, region configs, or golden expected values. Knowledge docs are ML
evidence, not calculator standards.
