---
name: ml-predictor
description: Use for predictor_v3 Train, Predict, ML features, inference/training boundaries, runtime Target authority, Data Definition compatibility, and model-validation work. Do not use for calculator-only work.
---

# ML / Predictor

Use this skill only for predictor_v3 ML, Train, and Predict work. The user's explicit task takes precedence over this skill.

## Hard boundaries

- Keep `app_train.py` and `app_predict.py` separate thin entrypoints.
- New Train/Predict UI code targets PySide6 under `apps/train/` and `apps/predict/`; production code does not depend on the retired `ui/` package.
- Predict inference stays under `core/ml/inference.py`; do not pull training/tuning-only dependencies into the Predict runtime.
- Canonical Data Definition/runtime generation owns Feature/Target definitions and target-level policy. Compatibility projections such as `MODEL_REGISTRY`, `COLUMNS`, and generated feature catalogs do not become writable SSOTs.
- Preserve `feature_names_in_`; do not add `.values` before `model.fit()`.
- Cooling and Heating models remain independent; do not combine them with MultiOutput.
- Preserve monotone and physical constraints over statistical convenience.

## Owner routing

- Train/Predict architecture: `docs/architecture/pyside6_train_predict_architecture.md`.
- Project-wide dependency direction: `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`.
- ML feature/data reasoning: `docs/knowledge/README.md` and the matching knowledge owner.
- Training-header compatibility only: `docs/workflows/ml_feature_catalog_workflow.md`.
- DEV-only mock smoke: `tools/dev/mock_smoke/README.md`; it cannot prove model accuracy or physical quality.
- UI changes also use the repo-local `ui-surface` skill and matching `docs/ui_ux/` owner.

## Work flow

1. Inspect the changed feature/model/registry/service owner and the materially adjacent dependency boundary.
2. Confirm feature names, target leakage risk, Cooling/Heating separation, Target authority, and monotonicity before changing behavior.
3. Keep ML feature schema separate from calculator core, region config, and UI table schemas.
4. For runtime-generation, prediction-session, Target applicability, model lifecycle, or training-execution changes, preserve the current owner and persisted/public compatibility unless the task explicitly changes it.
5. Do not use `docs/knowledge/` as authority for calculator formulas, fixtures, region configs, or golden values.

## Verification

Use focused tests for the changed model, feature, inference/training boundary, runtime descriptor, or application owner. Run UI validation only when the user-facing surface changes. Broaden or repeat a passing suite only after a later source change, a failure, or unresolved evidence invalidates the earlier result.

Manual or native-platform validation is appropriate only when the relevant behavior cannot be adequately proven by repository automation. DEV mocks prove workflow readiness, not accuracy, feature importance, physical trends, or production model quality.