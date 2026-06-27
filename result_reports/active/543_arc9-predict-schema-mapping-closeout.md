# 543 Arc 9 Predict Schema Mapping Closeout

## Goal

Close Arc 9 after recovering the PySide6 Predict path against the current
predictor schema, mapping, and ML package owners.

## Schema Recovery

- Added Qt-free Predict schema adapter under `apps/predict/schema/`.
- PySide6 input/result table models now display schema adapter columns instead
  of local mock column definitions.
- Core predictor schema metadata now includes the minimal ML feature/target
  references needed by app adapters.

## Mapping / Autofill Recovery

- Implemented Qt-free `core.mapping.autofill` for simple dropdown autofill,
  ODU dependent clears, ODU cascade options, and `cond_specs` area/volume fill.
- Added app-side `PredictMappingRepository` and `InputEditController` so table
  models do not load mapping JSON or own mapping side effects.
- `data/mapping.json` is absent in this checkout; file-backed mapping success
  smoke is therefore limited to safe load/import behavior.

## Row-to-ML / Result Adapter Recovery

- Row-to-ML conversion now derives numeric features from
  `COLUMNS[*].ml_feature`.
- Recovered legacy one-hot behavior for `ref_type` and `exp_type`.
- Prediction result mapping now derives result keys from schema `ml_target`
  metadata and `core.ml.features.TARGETS`.
- Missing targets produce controlled `partial` result state instead of a crash.

## Integration Smoke

- `app_predict.py` remains a thin Predict entrypoint.
- `app_train.py` remains a thin Trainer/admin entrypoint.
- `PredictWorkspace` opens offscreen with schema-driven input/result tables.
- `TrainShell` opens offscreen and reuses `PredictWorkspace` in the Predict tab.
- Row add/delete/reset smoke passed through the table model tests.
- Missing `model/model.pkl` is handled as a controlled prediction service error;
  real model success smoke remains blocked until a valid artifact is present.
- Root compatibility wrapper imports were not reintroduced in active code/docs.
  The first root-wrapper search found only `docs/archive` historical references;
  the active-range rerun excluding archive paths was clean.

## Docs Updated

- `docs/WORK_PLAN.md` now points next action to Arc 10.
- `project_brief.md` marks Arc 9 complete and Arc 10 ready.
- `docs/architecture/pyside6_train_predict_architecture.md` now reflects the
  recovered package-owner import path instead of pre-recovery wording.

## UI/UX Contract Check

- Compliant:
  - row headers remain user-facing row identity;
  - internal `case_id` remains the result lookup identity;
  - input/result split table remains variable-size and synchronized.
- Corrected in this arc:
  - local mock column definitions were removed from table models;
  - schema/mapping logic moved out of table model ownership.
- Intentionally deferred:
  - PySide6 table adapter does not yet exist.
- Remaining table UX parity gap:
  - TSV copy;
  - TSV paste;
  - Delete/Backspace clear;
  - grouped undo;
  - Tab/Enter navigation;
  - click/type replace-on-type;
  - dropdown delegate rendering;
  - validation rendering.

## Verification

- `python3 -B -m py_compile core/ml/*.py core/predictor_schema/*.py core/mapping/*.py core/common/*.py apps/predict/**/*.py apps/train/**/*.py app_predict.py app_train.py`
- `python3 -B -c "import app_predict; import app_train"`
- `python3 -B -c "from PySide6.QtWidgets import QApplication; import os; os.environ.setdefault('QT_QPA_PLATFORM','offscreen'); app=QApplication.instance() or QApplication([]); from apps.predict.ui.workspace import PredictWorkspace; w=PredictWorkspace(); assert w is not None; assert w.input_model.columnCount() > 0; assert w.result_model.columnCount() > 0"`
- `python3 -B -c "from apps.train.ui.shell import TrainShell; from PySide6.QtWidgets import QApplication; import os; os.environ.setdefault('QT_QPA_PLATFORM','offscreen'); app=QApplication.instance() or QApplication([]); w=TrainShell(); assert w.tabs.count() == 3"`
- Root wrapper absence search over active code/docs excluding archive paths.
- `python3 -B -m pytest tests -k "predict or mapping or schema"`
- `git diff --check`
- `git status --short`

## Excluded Scope

- No ML algorithm, feature list, target list, preprocessing formula, model
  artifact, mapping JSON schema, calculator formula/config/fixture/golden, or
  public result contract changes.
- No root compatibility wrapper recreation.
- No worker/progress/cancel implementation.
- No Trainer foundation implementation.
- No legacy PyQt behavior refactor.
- No report lifecycle cleanup.

## Next Action

Arc 10 - Prediction Worker / Progress.
