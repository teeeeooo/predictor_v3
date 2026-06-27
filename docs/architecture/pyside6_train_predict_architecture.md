# PySide6 Train/Predict Architecture Contract

## 1. Purpose

This document is the governing architecture contract for the new PySide6 Train/Predict UI in `predictor_v3`.

It is intended for Codex/agent implementation work. It defines the target package structure, file responsibilities, dependency boundaries, state model, UI layout, workflow, and verification expectations.

The design decision behind this architecture contract is recorded in:

- `docs/designs/2026-06-27-pyside6-train-predict-rewrite-design-gate.md`

Non-binding visual references:

- `docs/designs/assets/predict_ref_img.png`
- `docs/designs/assets/train_ref_img.png`

These images are layout references, not pixel-perfect implementation targets.
Preserve the broad Predict split-workspace and Trainer tab intent; resolve
specific sizing, tokens, states, and behavior through this architecture contract
and active UI/UX owner documents.

Boundary note:

- This document owns package, dependency, state, controller, service, adapter,
  worker, and entrypoint boundaries.
- User-facing UI/UX behavior, spreadsheet table parity, terminology, and
  input/result surface acceptance are owned by `docs/ui_ux/` and the UI Surface
  Workflow.
- This architecture contract does not replace the UI/UX contracts. When a
  table-shaped or input/result surface is created or modified, apply
  `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`,
  `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`, and
  `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` as applicable. If a
  PySide6 table adapter does not exist yet, record that adapter gap in the
  report and use the toolkit-neutral table contract as the acceptance contract.
- PySide6 Predictor schema/mapping recovery depends on the project-wide
  architecture SSOT in `docs/architecture/project_architecture.md` and the
  restructuring plan in
  `docs/architecture/project_wide_architecture_restructuring_plan.md`.
  Recovery starts after `core/predictor_schema`, `core/mapping`, and `core/ml`
  package boundaries are introduced.
- PySide6 Train/Predict follows the project-wide target package boundary. New
  PySide6 code must not deepen dependency on the current flat `core/` root
  beyond approved adapters. Current local schemas/mappings/adapters in PySide6
  are recovery targets.

## 2. Implementation Principle

The new Train/Predict UI is a rewrite, not an in-place migration.

Use PySide6 for new Train/Predict UI code.

Do not add new PySide6 Train/Predict production code under the legacy `ui/` package.

Do not change core ML behavior unless a later slice explicitly authorizes it.

## 3. Target Package Structure

### 3.1 Full target structure

    predictor_v3/
      app_predict.py
      app_train.py

      apps/
        predict/
          __init__.py
          app.py

          ui/
            __init__.py
            shell.py
            workspace.py
            command_bar.py
            status_bar.py

            tables/
              __init__.py
              input_table_model.py
              input_table_view.py
              result_table_model.py
              result_table_view.py
              delegates.py
              table_sync.py

          controllers/
            __init__.py
            predict_controller.py
            table_edit_controller.py

          services/
            __init__.py
            model_service.py
            prediction_service.py

          adapters/
            __init__.py
            column_schema_adapter.py
            row_to_ml_input_adapter.py
            prediction_result_adapter.py
            mapping_adapter.py
            cascade_adapter.py

          workers/
            __init__.py
            prediction_worker.py

          state/
            __init__.py
            case_row.py
            result_row.py
            case_store.py
            predict_session.py

        train/
          __init__.py
          app.py

          ui/
            __init__.py
            shell.py
            train_model_panel.py
            data_mapping_panel.py
            train_log_panel.py

          controllers/
            __init__.py
            train_controller.py
            mapping_controller.py

          services/
            __init__.py
            training_service.py
            mapping_service.py

          workers/
            __init__.py
            train_worker.py

### 3.2 First production foundation structure

The first production foundation slices may use this smaller structure:

    predictor_v3/
      app_predict.py
      app_train.py

      apps/
        predict/
          __init__.py
          app.py
          ui/
            __init__.py
            shell.py
            workspace.py
            tables/
              __init__.py
              input_table_model.py
              result_table_model.py
              table_sync.py
          state/
            __init__.py
            predict_session.py
          services/
            __init__.py
            model_service.py
            prediction_service.py
          adapters/
            __init__.py
            row_to_ml_input_adapter.py
            prediction_result_adapter.py

        train/
          __init__.py
          app.py
          ui/
            __init__.py
            shell.py
            train_model_panel.py
            data_mapping_panel.py
          workers/
            __init__.py
            train_worker.py

Do not create all files in the full target structure unless the current slice needs them.

## 4. Entrypoint Contract

### 4.1 `app_predict.py`

Responsibility:

- Thin compatibility entrypoint.
- Imports and calls `apps.predict.app.main`.
- Must not create widgets directly.
- Must not import legacy `ui.predict_window`.
- Must not load the ML model directly.

Expected shape:

    from apps.predict.app import main

    if __name__ == "__main__":
        main()

### 4.2 `app_train.py`

Responsibility:

- Thin compatibility entrypoint.
- Imports and calls `apps.train.app.main`.
- Must not create widgets directly.
- Must not import legacy `ui.train_window`.
- Must not run training directly.

Expected shape:

    from apps.train.app import main

    if __name__ == "__main__":
        main()

### 4.3 `apps.predict.app`

Responsibility:

- Create `QApplication`.
- Register global exception handler through existing core utility if available.
- Set style or application metadata.
- Create and show `PredictShell`.
- Start event loop.

Must not:

- Call `core.ml.inference.predict_row` directly.
- Own table data.
- Own training behavior.

### 4.4 `apps.train.app`

Responsibility:

- Create `QApplication`.
- Register global exception handler through existing core utility if available.
- Create and show `TrainShell`.
- Start event loop.

Must not:

- Call `core.ml.training.train_all_models` directly.
- Own Predict table data.
- Duplicate Predict workspace implementation.

## 5. Dependency Rules

### 5.1 Allowed imports

Allowed:

- `apps.predict` imports PySide6.
- `apps.predict` imports `core.ml.inference`, `core.predictor_schema.columns`, `core.ml.registry`, `core.ml.preprocessing`, `core.utils` through services/adapters where possible.
- `apps.train` imports PySide6.
- `apps.train` imports `apps.predict.ui.workspace.PredictWorkspace`.
- `apps.train` imports `core.ml.training` through `training_service` or `train_worker`.
- `apps.train` imports `scripts.update_mapping` only through `mapping_service`.

### 5.2 Forbidden imports

Forbidden:

- `core` importing PySide6.
- `core` importing `apps`.
- `core.ml.inference` importing `core.ml.training`.
- `apps.predict` importing `apps.train`.
- new `apps.predict` or `apps.train` production code importing legacy `ui.*`.
- calculator UI importing predict/train UI.
- predict/train UI importing calculator UI without a later approved adapter design.

## 6. Predict App UI Specification

### 6.1 Window

Title:

- `HVAC V3 Predictor`

Primary regions:

- Header/status line.
- Command bar.
- Main split workspace.
- Bottom status bar.

### 6.2 Header/status line

Displays concise status items:

- model status, e.g. `모델 상태: model.pkl loaded`
- preprocess version, e.g. `preprocess: v1.0`
- mapping status, e.g. `mapping: loaded`

This is a status display only. Model loading behavior belongs to `ModelService`.

### 6.3 Command bar

Initial button set:

- `예측 실행`
- `초기화`
- `행 추가`
- `행 삭제`
- `입력 붙여넣기`
- `결과 복사`
- `Export CSV`

First production foundation may implement buttons as disabled placeholders except for actions in scope.

Button responsibilities:

- Buttons emit signals or call controller methods.
- Buttons do not mutate `PredictSession` directly.
- Buttons do not call `core.ml.inference` directly.

### 6.4 Main workspace

Use two synchronized panes:

- Left: `Input Cases`
- Right: `Prediction Results`

Input table is editable.

Result table is read-only.

The result table should remain visible while the input table scrolls horizontally.

### 6.5 Input Cases columns

Input/user-editable or user-selected columns:

- `냉방능력`
- `난방능력`
- `실내기`
- `증발기`
- `실외기`
- `FIN종류`
- `PI`
- `ROW`
- `압축기`
- `냉매종류`
- `팽창장치`

Auto-filled columns:

- `ID Volume`
- `Evap Area`
- `Evap Volume`
- `OD Volume`
- `Cond Area`
- `Cond Volume`
- `Comp EER`
- `Comp cc`

Column names may be sourced from `core.predictor_schema.columns.COLUMNS` through a column schema adapter.

Do not hard-code UI header-to-ML feature conversion in table model classes.

### 6.6 Prediction Results columns

Read-only result columns:

- `상태`
- `냉방 소비전력`
- `EER`
- `CSPF`
- `난방 소비전력`
- `COP`
- `HSPF2`
- `냉매량`
- `냉방 Hz`
- `난방 Hz`
- `오류/경고`

Initial implementation may leave CSPF/HSPF2 blank or status-only if calculator integration is not in scope.

Do not implement seasonal calculator integration in the first PySide6 Predict UI slice unless separately approved.

### 6.7 Bottom status bar

Displays variable-size batch summary:

- total cases
- predicted cases
- error cases
- dirty/changed cases
- model status or last prediction time

Example:

    전체 1,284건 | 예측 완료 1,260건 | 오류 24건 | 변경됨 12건

Values must come from session/controller state, not hard-coded text.

## 7. Train App UI Specification

### 7.1 Window

Title:

- `HVAC V3 Trainer`

Primary regions:

- Header/status line.
- Tab bar.
- Active tab content.
- Bottom status bar.

### 7.2 Tabs

The Trainer app uses exactly these top-level tabs at first:

- `Predict`
- `Train / Model`
- `Data Mapping`

### 7.3 Predict tab

The Predict tab embeds the same `PredictWorkspace` used by `apps.predict.ui.shell`.

Do not duplicate Predict UI code under `apps/train`.

### 7.4 Train / Model tab

The Train / Model tab includes:

- command bar
- training configuration panel
- progress panel
- training log panel
- target-level training summary
- model/training info summary

Command bar buttons:

- `학습 데이터 선택`
- `학습 실행`
- `중지`
- `모델 열기`
- `로그 저장`

Training configuration fields:

- data file path
- model artifact path
- preprocess version
- target count
- active target list

Target list initially follows existing target names:

- `Cooling Power`
- `Heating Power`
- `Ref Qty`
- `Cooling Hz`
- `Heating Hz`

Training summary displays per target:

- target name
- R2 or R² value if available
- RMSE if available
- selected feature count if available
- status
- elapsed time

Training log displays emitted log lines from training worker/service.

### 7.5 Data Mapping tab

The Data Mapping tab includes:

- source mapping file selection
- mapping update execution
- mapping output path/status
- mapping load status
- log or validation result area

The tab may call existing mapping update functionality through `MappingService`.

Do not call `scripts.update_mapping` directly from a QWidget.

## 8. State Model

### 8.1 `CaseRow`

Represents one input case.

Recommended fields:

- `case_id: str`
- `values: dict[str, object]`
- `dirty: bool`
- `errors: list[str]`
- `warnings: list[str]`

No PySide6 dependency.

### 8.2 `ResultRow`

Represents one prediction result.

Recommended fields:

- `case_id: str`
- `status: pending | running | success | warning | error`
- `values: dict[str, object]`
- `error_message: str | None`
- `warning_messages: list[str]`

No PySide6 dependency.

### 8.3 `CaseStore`

Owns dynamic case list and case order.

Recommended responsibilities:

- append rows
- insert rows
- remove rows
- update cell value
- mark dirty
- resolve case by row index
- return case IDs by scope

Supported scopes to design for:

- all
- selected
- dirty
- valid_only

First implementation may only support all rows.

### 8.4 `PredictSession`

Owns prediction workspace state.

Recommended fields:

- `case_store`
- `results_by_case_id`
- `selected_case_ids`
- `model_status`
- `mapping_status`
- `run_state`
- `last_prediction_timestamp`

No direct PySide6 widget ownership.

## 9. Table Model Specification

### 9.1 Input table model

File:

- `apps/predict/ui/tables/input_table_model.py`

Responsibility:

- subclass PySide6 `QAbstractTableModel`
- expose case rows from `PredictSession`
- support editable input cells
- expose auto-filled cells as read-only or controlled cells
- mark dirty on user edits
- report validation states for rendering

Must not:

- call `core.ml.inference`
- call `core.ml.training`
- own model artifact loading
- hard-code model result keys

### 9.2 Result table model

File:

- `apps/predict/ui/tables/result_table_model.py`

Responsibility:

- subclass PySide6 `QAbstractTableModel`
- expose read-only result rows from `PredictSession`
- align row count/order with input table through session case order
- show pending/running/success/warning/error status
- show error/warning message

Must not:

- mutate input case values
- call prediction service directly
- implement export logic directly

### 9.3 Table sync

File:

- `apps/predict/ui/tables/table_sync.py`

Responsibility:

- synchronize vertical scroll between input and result views
- synchronize row selection
- synchronize row height if needed
- avoid infinite signal loops

Initial sort/filter behavior:

- Sorting and filtering should be disabled in the first table sync slice unless both tables share the same proxy model/order.

## 10. Adapter Specification

### 10.1 Column schema adapter

File:

- `apps/predict/adapters/column_schema_adapter.py`

Responsibility:

- read column metadata from `core.predictor_schema.columns.COLUMNS`
- classify columns into input, auto-filled, and result groups
- expose UI column descriptors for table models

Must not:

- mutate `COLUMNS`
- add model-specific behavior

### 10.2 Row-to-ML input adapter

File:

- `apps/predict/adapters/row_to_ml_input_adapter.py`

Responsibility:

- convert `CaseRow` to ML input dict
- use `COLUMNS` `ml_feature` metadata where available
- convert refrigerant and expansion-device selections into one-hot inputs
- perform type normalization for numeric inputs
- return validation errors for missing required input

Must not:

- call model `.predict()`
- call calculator APIs
- infer seasonal metrics

### 10.3 Prediction result adapter

File:

- `apps/predict/adapters/prediction_result_adapter.py`

Responsibility:

- convert `core.ml.inference.predict_row()` result dict to `ResultRow`
- map model target keys to UI result fields
- handle missing target predictions
- produce warning/error status for partial results

Must not:

- write to table widgets directly
- hard-code values in `PredictWorkspace`

### 10.4 Mapping adapter

File:

- `apps/predict/adapters/mapping_adapter.py`

Responsibility:

- load mapping data for UI dropdown/autofill use
- normalize mapping access for predict UI
- hide raw mapping JSON structure from table model/view classes

### 10.5 Cascade adapter

File:

- `apps/predict/adapters/cascade_adapter.py`

Responsibility:

- resolve ODU → Fin → PI → Row cascading choices
- resolve condition specs from selected hardware combinations
- return changes to be applied through controller/state

Must not:

- mutate QTableView directly
- call prediction service

## 11. Service and Worker Specification

### 11.1 Model service

File:

- `apps/predict/services/model_service.py`

Responsibility:

- load `model.pkl`
- call `core.ml.inference.load_model`
- expose model status
- expose preprocess version compatibility status

### 11.2 Prediction service

File:

- `apps/predict/services/prediction_service.py`

Responsibility:

- call `core.ml.inference.predict_row`
- accept ML input dict and loaded model data
- return raw prediction dict or structured service result

Must not:

- own PySide6 widgets
- mutate `PredictSession` directly

### 11.3 Prediction worker

File:

- `apps/predict/workers/prediction_worker.py`

Responsibility:

- execute prediction for many case IDs without freezing UI
- support progress signal
- support row success/failure signal
- support finished signal
- support cancellation when implemented

First production foundation may defer worker and run synchronously for small smoke only, but production batch prediction should use worker execution.

### 11.4 Training service

File:

- `apps/train/services/training_service.py`

Responsibility:

- wrap `core.ml.training.train_all_models`
- own training configuration object
- provide a clean call boundary for worker/controller

### 11.5 Train worker

File:

- `apps/train/workers/train_worker.py`

Responsibility:

- run training off the UI thread
- emit log lines
- emit progress updates if available
- emit finished status

Must not:

- contain ML training algorithms
- duplicate `core.ml.training` logic

### 11.6 Mapping service

File:

- `apps/train/services/mapping_service.py`

Responsibility:

- wrap mapping update logic
- expose mapping update status
- keep script-level details out of QWidgets

## 12. Controller Specification

### 12.1 Predict controller

File:

- `apps/predict/controllers/predict_controller.py`

Responsibility:

- handle command bar actions
- choose prediction scope
- coordinate session, adapters, services, and worker
- apply result updates to session
- request table model refresh

Initial public methods may include:

- `predict_all()`
- `predict_selected()`
- `predict_dirty()`
- `cancel_prediction()`
- `clear_results()`

### 12.2 Table edit controller

File:

- `apps/predict/controllers/table_edit_controller.py`

Responsibility:

- handle paste/clear/row insert/row delete behavior
- update `CaseStore`
- preserve table model responsibility boundaries

First production foundation may defer this file until paste/row operations are implemented.

### 12.3 Train controller

File:

- `apps/train/controllers/train_controller.py`

Responsibility:

- handle training command actions
- coordinate train worker/service
- update Train / Model panel state

### 12.4 Mapping controller

File:

- `apps/train/controllers/mapping_controller.py`

Responsibility:

- handle mapping file selection and update actions
- call `MappingService`
- update Data Mapping tab state

## 13. Visual and UX Rules

### 13.1 Table density

The UI is for HVAC engineering batch work. It should be data-dense and spreadsheet-like.

Avoid large card-only interfaces for Predict input. Forms are not the primary Predict UX.

### 13.2 Color semantics

Use subtle semantic tinting:

- user-editable input cells
- auto-filled cells
- read-only result cells
- warning/error rows
- selected row

Do not scatter hard-coded color literals across many files. If color tokens are needed, place them in a local theme/token owner for the PySide6 package or reuse an existing approved token owner after checking project policy.

### 13.3 Result visibility

Prediction results must remain visible while the user navigates wide input cases.

The split table structure is a core UX requirement.

### 13.4 Variable-size batch behavior

UI must remain usable for small and large case counts.

Do not design around a fixed 10-row table.

Do not hard-code example counts such as 300. Counts shown in mockups are examples only.

## 14. Implementation Slices

### Slice 1: Docs alignment

Allowed:

- add design gate document
- add architecture contract document
- update charter/architecture/work plan active references
- add result report

Forbidden:

- production code changes
- dependency changes
- PyQt5 deletion

Verification:

- markdown presence check
- link/path sanity check
- git diff check

### Slice 2: PySide6 package foundation

Allowed:

- add `apps/predict` and `apps/train` foundation packages
- add thin entrypoint wrappers
- add empty shell windows
- add tab shell in Trainer

Forbidden:

- model training logic changes
- prediction logic changes
- table implementation beyond placeholders
- deleting old `ui/`

Verification:

- `python3 -B -m py_compile app_predict.py app_train.py`
- import smoke for `apps.predict.app` and `apps.train.app`
- structure guard
- manual launch smoke if environment supports GUI

### Slice 3: Predict workspace foundation

Allowed:

- add command bar
- add input/result table placeholders
- add status bar
- add `PredictSession` basic state

Forbidden:

- core prediction execution
- training panels
- paste/export implementation

Verification:

- import smoke
- focused UI construction smoke if available
- structure guard

### Slice 4: Predict table models

Allowed:

- implement input table model
- implement result table model
- implement basic table sync
- implement row append/delete if scoped

Forbidden:

- calling `core.ml.inference.predict_row`
- training logic
- calculator integration

Verification:

- focused table model tests
- row count/order tests
- session/result alignment tests

### Slice 5: Prediction execution

Allowed:

- implement model service
- implement row-to-ML input adapter
- implement prediction service
- implement result adapter
- wire predict-all action

Forbidden:

- model artifact schema change
- feature definition change
- calculator integration
- inverse search

Verification:

- adapter unit tests
- model service failure tests
- prediction service smoke with fixture or stub model data
- GUI manual smoke if possible

### Slice 6: Trainer panels

Allowed:

- implement Train / Model tab
- implement Data Mapping tab
- implement train worker
- wire training log/progress

Forbidden:

- changing `core.ml.training` algorithm
- changing Optuna/RFECV settings unless explicitly scoped
- changing model artifact schema

Verification:

- worker signal smoke
- service boundary tests
- import smoke
- manual training-panel smoke if possible

### Slice 7: Legacy retirement audit

Allowed:

- audit old `ui/` usage
- confirm no new app imports legacy `ui.*`
- propose deletion/move/archive plan

Forbidden:

- deleting files without explicit approval
- changing new app behavior

Verification:

- import graph search
- structure guard
- git status/diff check

## 15. Verification Matrix

### Always run for source changes

- `python3 -B tools/check_code_structure.py`
- `git diff --check`
- focused py_compile/import smoke for changed package
- focused tests matching modified owner

### Run for Predict table changes

- table row count/order test
- case_id/result alignment test
- editable/read-only role test
- table sync smoke if testable headlessly

### Run for ML adapter changes

- row-to-ML dict conversion test
- one-hot mapping test
- missing input validation test
- prediction result adapter test
- leakage/feature guard tests if feature boundary changes

### Run for Trainer changes

- train worker import smoke
- train service boundary test
- log signal smoke if feasible
- no UI-thread direct `train_all_models` call in QWidgets

### Manual smoke candidates

Manual smoke should be separate from automated verification.

Predict app:

- launch window
- add rows
- paste sample cases
- run prediction with available model
- confirm input/result row alignment
- confirm error row display
- copy/export result if implemented

Trainer app:

- launch window
- confirm tabs
- confirm Predict tab reuses predictor workspace
- select training file
- start training smoke or stub run
- confirm log/progress display
- cancel/finish behavior if implemented

## 16. Coding Guardrails

- Keep entrypoints thin.
- Keep shell classes thin.
- Keep table models focused on model/view data presentation.
- Keep core prediction/training calls behind services.
- Keep schema conversion in adapters.
- Keep mutable session state outside QWidget subclasses where possible.
- Do not mix train and predict core logic.
- Do not import training dependencies into prediction runtime paths unnecessarily.
- Do not add feature-specific flat files directly under broad roots if a package owner is needed.
- Do not change public calculator APIs in this workstream.
- Do not change fixtures/golden expected values in this workstream.

## 17. Result Report Requirements

Each implementation slice should produce a result report with:

- task goal
- files modified
- architecture boundary decision
- reuse/commonization decision
- validation commands and results
- manual smoke status
- excluded scope
- known risks
- next action

For structure-impacting source changes, include a change gate block according to current project workflow.
