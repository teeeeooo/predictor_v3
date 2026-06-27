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
  `apps/train/`; legacy PyQt5 `ui/` code is reference-only until a later
  retirement slice.
- Do not import `optuna`, `sklearn`, `shap`, or `matplotlib` from
  `core/predictor.py`.
- Keep `COLUMNS` in `core/constants.py`.
- Keep `MODEL_REGISTRY` in `core/models.py`.
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
- Train/Predict PySide6 rewrite design/spec:
  `docs/designs/2026-06-27-pyside6-train-predict-rewrite-design-gate.md` and
  `docs/designs/2026-06-27-pyside6-train-predict-ui-implementation-spec.md`.
- Project-wide responsibility boundaries:
  `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`.

## Flow

1. Search for the target feature, model, predictor, or registry first.
2. Read only the needed function/class range.
3. Confirm feature names, target leakage risk, cooling/heating separation, and
   monotonicity before editing.
4. Keep ML feature schema separate from calculator core, region config, and UI
   table schemas.
5. Run focused model/feature tests or import smoke for the changed owner.

## Forbidden Evidence Use

Do not use `docs/knowledge` content as authority to change calculator formulas,
fixtures, region configs, or golden expected values. Knowledge docs are ML
evidence, not calculator standards.
