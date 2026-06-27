# PySide6 Train/Predict Rewrite Design Gate

## 1. Purpose

This document records the design decision for the next Train/Predict workstream in `predictor_v3`.

The decision is to stop treating the existing PyQt5 Train/Predict UI as the long-term implementation target and to create a new PySide6-based Train/Predict application structure.

This is a design gate document. It records the decision, scope, non-goals, and architectural direction. Detailed implementation rules are defined in:

- `docs/designs/2026-06-27-pyside6-train-predict-ui-implementation-spec.md`

## 2. Background

The current repository has two legacy PyQt5 entrypoints:

- `app_predict.py`: launches the existing Predict UI.
- `app_train.py`: launches the existing Train UI.

The existing `app_predict.py` is directionally close to the intended user workflow because it provides a spreadsheet-like batch prediction screen.

The existing `app_train.py` is not aligned with the intended product contract. The intended contract is:

- `app_predict.py` = prediction-only application.
- `app_train.py` = prediction application plus training, model-management, and data-mapping capabilities.

The current `app_train.py` is closer to a separate training-only utility. It does not include the predictor workspace as the main reusable workflow.

Separately, PyQt5 is no longer an acceptable long-term toolkit choice because of licensing direction. Therefore, a direct PyQt5-to-PySide6 migration of the existing files would preserve an incorrect application structure.

## 3. Decision Summary

### 3.1 Primary decision

Do not migrate the existing PyQt5 Train/Predict UI in place.

Instead, create a new PySide6 Train/Predict UI under new application package boundaries:

- `apps/predict/`
- `apps/train/`

The existing `ui/` package remains legacy/reference-only until a later retirement slice.

### 3.2 App contract

`app_predict.py` remains the user-facing prediction entrypoint, but it should become a thin wrapper around the new PySide6 package:

- `app_predict.py` → `apps.predict.app.main`

`app_train.py` becomes the administrator/developer entrypoint and should be a thin wrapper around the new PySide6 package:

- `app_train.py` → `apps.train.app.main`

The Train app must include the same predictor workspace used by the Predict app.

Final product meaning:

- Predict app: batch prediction workspace.
- Trainer app: Predict workspace + Train / Model tab + Data Mapping tab.

## 4. Superseded Prior Contract

Previous project documents described the Train/Predict PyQt5 path as retained until a future rewrite.

That statement is now stale.

The new direction is:

- Existing Train/Predict PyQt5 code is legacy/reference-only.
- New Train/Predict implementation targets PySide6.
- PyQt6 migration remains out of scope and is not the selected path.
- Calculator UI remains separate and continues on its current Tkinter calculator path.

This design gate should be reflected later in:

- `PROJECT_CHARTER.md`
- `docs/architecture/project_architecture.md`
- `docs/WORK_PLAN.md`
- `ACTIVE_DOCUMENTS.md` if the active-document index needs a direct pointer to this design/spec pair.

`project_memory_seed.md` should not be edited as part of ordinary implementation work unless a later explicit memory seed sync task is approved.

## 5. UX Decision

Visual reference assets are available as non-binding layout references:

- `docs/designs/assets/predict_ref_img.png`
- `docs/designs/assets/train_ref_img.png`

They are not pixel-perfect requirements. Use them only to preserve the broad
workspace layout, split-table intent, and Trainer tab composition while applying
the implementation spec and active UI/UX owner documents.

### 5.1 Predict app UX

The Predict app should keep the strongest part of the old UI: spreadsheet-style batch engineering input.

The new Predict UI is not a single-case form. It is a variable-size batch prediction workspace.

Target workflow:

1. User inputs or pastes N cases.
2. User runs prediction for all, selected, or changed cases.
3. Results are shown for all relevant cases in a separate synchronized result table.
4. User compares results across cases.
5. User copies or exports results.
6. User reviews warnings/errors for failed cases.

N is not fixed. It may be 1, 10, 300, 1,284, or more. The UI must not assume a fixed row count.

### 5.2 Input and result table split

The Predict workspace uses two synchronized tables:

- Left: `Input Cases` table.
- Right: `Prediction Results` table.

The input table is editable. The result table is read-only and remains visible while the user scrolls through many input columns.

This replaces the old pattern where result columns sit far to the right of a single wide table and can become difficult to review.

### 5.3 Detail panel role

A selected-row detail panel is not the primary result review surface.

If added later, a detail panel is only for debugging or explaining a selected case, such as:

- missing input cause
- mapping failure cause
- model target availability
- feature alignment issue
- warning details

The primary result review surface is the synchronized `Prediction Results` table.

### 5.4 Train app UX

The Train app uses tabs:

- `Predict`
- `Train / Model`
- `Data Mapping`

The `Predict` tab reuses the same `PredictWorkspace` component used by `app_predict.py`.

The `Train / Model` tab manages:

- training data selection
- model training execution
- progress
- target-level summary
- training log
- model artifact status

The `Data Mapping` tab manages:

- mapping source file selection
- mapping update execution
- mapping status review

## 6. Architecture Decision

### 6.1 New package boundaries

New PySide6 code should be placed under:

- `apps/predict/`
- `apps/train/`

Do not add new Train/Predict PySide6 source files directly under the legacy `ui/` package.

Do not mix new PySide6 Train/Predict UI with the Tkinter calculator UI under `apps/calculator/`.

### 6.2 Allowed dependency direction

Allowed:

- `app_predict.py` → `apps.predict.app`
- `app_train.py` → `apps.train.app`
- `apps.train` → `apps.predict` for reuse of `PredictWorkspace`
- `apps.predict` → `core.predictor`, `core.constants`, `core.models`, `core.data_pipeline`
- `apps.train` → `core.trainer`, `scripts.update_mapping` through application services

Forbidden:

- `core` → `apps`
- `core` → PySide6
- `core.predictor` → `core.trainer`
- `apps.predict` → `apps.train`
- `apps.predict` or `apps.train` → legacy `ui.*` in production code
- calculator UI → predict/train UI
- predict/train UI → calculator UI, unless a later explicit adapter design for calculator integration is approved

### 6.3 Core reuse

Reuse existing core modules where possible:

- `core/predictor.py`
- `core/trainer.py`
- `core/data_pipeline.py`
- `core/models.py`
- `core/constants.py`
- `core/utils.py`

The rewrite is a UI/application-shell rewrite, not an ML algorithm rewrite.

## 7. Reuse and Retirement Policy

### 7.1 Reuse

Reusable concepts from the existing PyQt5 Predict UI:

- spreadsheet-like batch input
- hardware selection dropdowns
- auto-filled hardware columns
- model status visibility
- one-row-per-case workflow

Reusable core behavior:

- model loading and preprocess-version guard
- `predict_row()` inference path
- `train_all_models()` training path
- `MODEL_REGISTRY` target orchestration
- `COLUMNS` as existing column metadata source, subject to future cleanup

### 7.2 Reference-only legacy code

The following legacy PyQt5 package can be read for behavior reference during design and migration, but new PySide6 code must not depend on it:

- `ui/predict_window.py`
- `ui/train_window.py`
- `ui/base_model.py`
- `ui/base_view.py`
- `ui/theme.py`
- `ui/spreadsheet_table.py`

### 7.3 Retirement timing

Do not delete or move the legacy `ui/` package in the first PySide6 skeleton slice.

Retirement should be a later explicit slice after the new PySide6 Predict/Train apps have working import smoke and minimum manual GUI smoke evidence.

## 8. Data and State Decisions

### 8.1 Variable-size batch

The new Predict workspace must not rely on fixed row count constants such as a UI-level `NUM_ROWS = 10` behavior.

Rows are owned by a prediction session/state layer.

### 8.2 Case identity

Prediction results should be associated with stable `case_id` values rather than only row index.

Rationale:

- row insertion/deletion must not break result mapping
- filtering/sorting may be added later
- selected-row and dirty-row prediction should remain stable
- input/result table synchronization should remain robust

### 8.3 Dirty case handling

The state layer should be able to mark edited cases as dirty.

This allows later support for:

- predict all cases
- predict selected cases
- predict changed cases only

The first skeleton does not need to implement all scopes, but the design should not block them.

## 9. Non-goals

The following are out of scope for the first design/implementation sequence unless separately approved:

- changing ML feature definitions
- adding new ML model targets
- changing `model.pkl` artifact schema
- changing calculator public APIs
- changing region config semantics
- implementing calculator ↔ predictor seasonal metric integration
- implementing inverse search
- deleting legacy PyQt5 UI immediately
- migrating calculator UI to PySide6
- large refactor of `core/trainer.py` or `core/predictor.py`
- replacing Optuna/RFECV training strategy
- changing golden fixtures or calculator expected values

## 10. Open Questions

These should remain explicit follow-up decisions:

- Should result export be CSV only at first, or TSV copy plus CSV export?
- Should sorting/filtering be implemented in the first result table slice or deferred?
- Should prediction worker cancellation be implemented in the first executable slice or deferred?
- Should `core/constants.py` gain dedicated option-list constants for refrigerant and expansion-device one-hot mapping?
- Should the old `ui/` package be deleted, moved to `_legacy`, or kept as archived reference after replacement?
- What is the first manual smoke checklist for PySide6 Predict and Trainer apps on Windows/macOS?

## 11. Recommended Implementation Sequence

1. Docs alignment slice
   - Add this design gate.
   - Add implementation spec.
   - Update charter/architecture/work plan references.
   - No production code changes.

2. PySide6 package skeleton
   - Add `apps/predict` and `apps/train` package skeletons.
   - Add thin entrypoint wrappers.
   - Add shell windows and empty tabs.
   - Verify import smoke.

3. Predict workspace skeleton
   - Add command bar, input table placeholder, result table placeholder, status bar.
   - Implement variable-size session state stub.

4. Predict table model slice
   - Implement input/result table models using session state.
   - Implement row count, basic editing, result display, and table sync.

5. Prediction execution slice
   - Add model service, row-to-ML adapter, prediction service, result adapter.
   - Run prediction for all valid rows.

6. Trainer panels slice
   - Add Train / Model panel.
   - Add Data Mapping panel.
   - Add TrainWorker and progress/log wiring.

7. Legacy retirement audit
   - Confirm new apps cover required behavior.
   - Decide whether to delete, move, or archive legacy PyQt5 UI.

## 12. Result Report Expectations

Any implementation slice based on this design should include a compact report with:

- goal
- modified files
- boundary decisions
- reuse/commonization decision
- change gate block if source structure changes
- verification commands actually run
- manual smoke required or completed
- excluded scope
- next action
