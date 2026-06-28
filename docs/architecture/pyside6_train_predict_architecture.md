# PySide6 Train/Predict Architecture Contract

## 1. Purpose

This document is the governing architecture contract for the new PySide6 Train/Predict UI in `predictor_v3`.

It is intended for Codex/agent implementation work. It defines the target package structure, file responsibilities, dependency boundaries, state model, UI layout, workflow, and verification expectations.

The design decision behind this architecture contract is recorded in:

- `docs/designs/2026-06-27-pyside6-train-predict-rewrite-design-gate.md`
- `docs/designs/2026-06-28-arc10-prediction-worker-progress-design.md`

Non-binding visual references:

- `docs/designs/assets/predict_ref_img.png`
- `docs/designs/assets/train_ref_img.png`

These images are layout references, not pixel-perfect implementation targets.
Preserve the broad Predict batch-workspace and Trainer tab intent; resolve
specific sizing, tokens, states, and behavior through this architecture contract
and active UI/UX owner documents.

Arc 9.5 Reopen replaces the earlier split input/result table target with a
unified case table target. The local `docs/designs/assets/predict_ref_img.png`
is the B-option reference for this correction arc: one visible row is one
prediction case, and input, auto-fill/calculated, prediction result, and
status/warning fields are grouped inside one spreadsheet-like table. The
earlier split table foundation remains implementation history only.

Arc 9.1 retired the legacy `ui/` path. Arc 9.2 moved the project-specific
legacy visual/table harvest to
`docs/designs/2026-06-27-pyside6-visual-table-parity-harvest.md` as the Arc 9.5
design reference. Visual token ownership for Arc 9.5 belongs to
`ui_common.visual_tokens`.

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
- PySide6 Predictor schema/mapping recovery follows the project-wide
  architecture SSOT in `docs/architecture/project_architecture.md` and the
  restructuring plan in
  `docs/architecture/project_wide_architecture_restructuring_plan.md`.
  The recovered Predict path imports `core/predictor_schema`, `core/mapping`,
  and `core/ml` package owners directly.
- PySide6 Train/Predict follows the project-wide target package boundary. New
  PySide6 code must not deepen dependency on the current flat `core/` root
  beyond approved adapters. Current local schemas/mappings/adapters in PySide6
  are recovery targets.

## 2. Implementation Principle

The new Train/Predict UI is a rewrite, not an in-place migration.

Use PySide6 for new Train/Predict UI code.

Do not add new PySide6 Train/Predict production code under the retired legacy
`ui/` package.

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
              case_table_model.py
              case_table_view.py
              group_header.py
              input_table_model.py
              input_table_view.py
              result_table_model.py
              result_table_view.py
              delegates.py
              table_sync.py

          controllers/
            __init__.py
            predict_controller.py
            input_edit_controller.py
            table_edit_controller.py

          schema/
            __init__.py
            case_table_schema_adapter.py

          services/
            __init__.py
            model_service.py
            prediction_service.py

          adapters/
            __init__.py
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
              case_table_model.py
              case_table_view.py
              input_table_model.py
              result_table_model.py
              table_sync.py
          schema/
            __init__.py
            case_table_schema_adapter.py
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
          controllers/
            __init__.py
            train_controller.py
          services/
            __init__.py
            training_service.py
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
- Must not import retired legacy `retired Predict window module`.
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
- Must not import retired legacy `retired Train window module`.
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
- new `apps.predict` or `apps.train` production code importing retired legacy
  `ui.*`.
- calculator UI importing predict/train UI.
- predict/train UI importing calculator UI without a later approved adapter design.

## 6. Predict App UI Specification

### 6.1 Window

Title:

- `HVAC V3 Predictor`

Primary regions:

- Header/status line.
- Command bar.
- Main unified case table workspace.
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

Target:

- Predict uses one unified case table.
- One visible row represents one prediction case.
- Input, auto-fill/calculated, prediction result, and status/warning fields are
  presented as column groups in the same table.
- The table is spreadsheet-like and supports visible-as-selected copy/paste
  behavior.
- The user should be able to drag-select across input, auto-fill, result, and
  status columns and copy the selected visible rectangle as TSV.
- Result and status cells are read-only but selectable and copyable.
- Write paths such as edit, paste, clear, and undo target only editable input
  cells.
- Internal `case_id` remains hidden and is used only for state/result lookup.
- Row headers remain the user-facing case identity.

Historical note:

- The earlier PySide6 foundation used split input/result tables to keep result
  visibility while scrolling input columns.
- Arc 9.5 Reopen replaces that final UX target with a unified case table
  because the split design conflicts with Excel-like full-case row
  selection/copy and would require hidden joined-copy behavior.

### 6.5 Unified Case Table columns

Column groups:

1. Input
   - user-editable or dropdown-selected values
   - sourced from `CaseRow.input_values`

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

2. Auto-fill / Calculated
   - mapping/autofill values
   - sourced from `CaseRow.autofill_values`
   - read-only by default

Auto-filled columns:

- `ID Volume`
- `Evap Area`
- `Evap Volume`
- `OD Volume`
- `Cond Area`
- `Cond Volume`
- `Comp EER`
- `Comp cc`

3. Prediction Results
   - model/rule result display values
   - sourced from `ResultRow.result_values`
   - read-only, selectable, copyable

Prediction result columns:

- `냉방 소비전력`
- `EER`
- `CSPF`
- `난방 소비전력`
- `COP`
- `HSPF2`
- `냉매량`
- `냉방 Hz`
- `난방 Hz`

4. Status / Warning
   - row status and user-facing message
   - sourced from `ResultRow.status` and `ResultRow.message`
   - read-only, selectable, copyable
   - app-side virtual display columns, not core schema additions

Status/warning columns:

- `상태`
- `오류/경고`

Column names may be sourced from `core.predictor_schema.columns.COLUMNS`
through the app-side unified case table schema adapter. Status/warning columns
are virtual display columns owned by the app-side adapter.

Do not hard-code UI header-to-ML feature conversion in table model classes.

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

Predict dropdown/status wording should describe the current app adapter and
core mapping owners, such as `DropdownOptionAdapter` plus `core.mapping`, rather
than raw UI/repository ownership.

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

### 9.1 Unified case table model

File:

- `apps/predict/ui/tables/case_table_model.py`

Responsibility:

- subclass PySide6 `QAbstractTableModel`
- expose one row per `PredictSession.case_order`
- expose unified column descriptors from the app-side schema adapter
- read input values from `CaseRow.input_values`
- read auto-fill values from `CaseRow.autofill_values`
- read prediction results from `ResultRow.result_values`
- read row status/message from `ResultRow.status` and `ResultRow.message`
- support editable input cells only
- keep auto/result/status cells read-only but selectable/copyable
- report validation/status states for rendering
- notify views when one case row changes

Must not:

- call `core.ml.inference`
- call prediction service
- call mapping repository
- call training execution
- call calculator APIs
- own model artifact loading
- hard-code core result behavior beyond display schema adaptation
- restore visible `case_id` columns

### 9.2 Unified case table view

File:

- `apps/predict/ui/tables/case_table_view.py`

Responsibility:

- provide spreadsheet-like selection, copy/paste, clear, undo, navigation, and
  edit/replace behavior
- copy selected visible rectangle as TSV
- paste TSV to editable cells while skipping read-only cells
- keep result/status cells selectable/copyable but mutation-protected
- implement grouped undo for edit/paste/clear
- implement Tab/Enter and shifted navigation
- implement click/type replace-on-type behavior
- provide or coordinate grouped column header visual affordance

Must not:

- call mapping repository directly
- call prediction service directly
- call training execution
- call calculator APIs
- implement hidden joined-copy behavior across separate tables

### 9.3 Historical split table foundation

Files:

- `apps/predict/ui/tables/input_table_model.py`
- `apps/predict/ui/tables/result_table_model.py`
- `apps/predict/ui/tables/table_sync.py`

These files may remain during migration for compatibility and rollback
evidence, but they are not the current Arc 9.5 final UX target. The final
workspace must not depend on split table synchronization or hidden joined-copy
behavior.

If still present, split table sync must stay local to legacy/foundation paths
and must not become the active workspace interaction contract.

## 10. Adapter Specification

### 10.1 Unified case table schema adapter

File:

- `apps/predict/schema/case_table_schema_adapter.py`

Responsibility:

- build app-side unified table display schema from
  `core.predictor_schema.columns.COLUMNS`
- preserve core schema order for input/auto/result columns
- add app-side virtual status/message columns
- classify columns into input, auto-fill/calculated, prediction result, and
  status/warning groups
- expose editability, copyability, dropdown capability, width, and rendering
  role metadata

Must not:

- mutate `core.predictor_schema.columns.COLUMNS`
- add core schema keys for app-only status columns
- encode ML or calculator behavior

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
- expose lightweight model status for UI/controller display without requiring
  widgets or eager model load unless explicitly requested

Must not:

- own PySide6 widgets
- mutate `PredictSession` directly
- import `PySide6`
- know progress bars, command buttons, or table models

### 11.3 Prediction worker

File:

- `apps/predict/workers/prediction_worker.py`

Responsibility:

- execute prediction for valid case requests without freezing UI
- receive immutable job data such as `PredictionJob(run_id, requests, total)`
- call `PredictionService.predict_one()` or equivalent per request
- emit row result payloads for completed/error service results
- emit progress payloads after each processed row
- emit finished summary payloads
- support cooperative cancellation between rows

Recommended payloads:

- `PredictionProgress(run_id, completed, total, current_case_id, message)`
- `PredictionWorkerSummary(run_id, total, complete, error, cancelled)`

Signals may use `Signal(object)` with dataclass payloads.

Arc 11 correction: the QThread worker is a PySide adapter implementation, not
the final UI/runtime-neutral application-usecase boundary. Future non-PySide
interfaces must reuse prediction orchestration through a usecase/execution port
without importing PySide6.

Must not:

- own or mutate `PredictSession`
- own or mutate widgets, table models, or selection state
- contain ML algorithms or row-to-ML mapping logic
- use thread kill/terminate patterns for cancellation

### 11.4 Training service

File:

- `apps/train/services/training_service.py`

Responsibility:

- wrap `core.ml.training.train_all_models`
- own training configuration object
- provide a clean call boundary for worker/controller
- remain Qt-free
- validate the training data path before execution
- return structured request/log/progress/result/resource-status contracts
- keep production training as the default path

Production service must not change core ML algorithms, preprocessing,
`MODEL_REGISTRY`, target behavior, or the single `model/model.pkl` artifact
contract. It may translate exceptions into structured error results.

Arc 11 correction: production Train execution must not be accepted as a direct
in-process `train_all_models()` call behind QThread. Production training must
flow through an execution port and killable process runner adapter. The visible
`중지` action must stop the running process, and cancelled/error runs must not
leave partial final model artifacts.

DEV-only fast training smoke belongs under `tools/dev/mock_smoke/`, not under
production `apps/` or `core/`. The DEV backend may create an
inference-compatible mock model artifact by reusing the existing mock artifact
generator, and it must not claim real training quality or metrics.

### 11.5 Train worker

File:

- `apps/train/workers/train_worker.py`

Responsibility:

- run training off the UI thread
- emit log lines
- emit progress updates if available
- emit finished status
- receive immutable training requests
- call the training service boundary
- support cooperative cancellation without `terminate()` or thread kill
- remain a PySide adapter or compatibility layer after the production execution
  port/process runner exists

Must not:

- contain ML training algorithms
- duplicate `core.ml.training` logic
- mutate Train / Model widgets directly
- leave orphan threads after finish, error, or cancel

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

- `apps/predict/controllers/prediction_controller.py`

Responsibility:

- handle command bar actions
- choose prediction scope
- coordinate session, adapters, services, and worker
- build requests from `PredictSession` using row adapters on the UI thread
- apply invalid and running result rows on the UI thread before worker start
- start and own the QThread / worker lifecycle
- receive worker row/progress/finish/cancel/failure events on the UI thread
- apply result updates to `PredictSession` on the UI thread
- request table model refresh through callbacks or signals
- expose model/run status to the workspace without making the workspace inspect
  raw model artifact paths

Initial public methods may include:

- `start_all()`
- `start_case_ids()`
- `cancel()`
- `is_running`
- `clear_results()`

Must not:

- become a QWidget
- put ML algorithms in the controller
- let the worker mutate `PredictSession` directly
- leave orphan worker threads after finish/cancel/failure

### 12.2 Table edit controller

File:

- `apps/predict/controllers/input_edit_controller.py`

Responsibility:

- handle paste/clear/row insert/row delete behavior
- update `CaseStore`
- preserve table model responsibility boundaries
- own mapping/autofill updates and dependent value clearing through state
  boundaries, not direct mapping repository calls from table model/view

First production foundation may defer this file until paste/row operations are implemented.

### 12.3 Train controller

File:

- `apps/train/controllers/train_controller.py`

Responsibility:

- handle training command actions
- coordinate train worker/service
- update Train / Model panel state
- expose `start(...)`, `cancel()`, `is_running`, and resource status
- reject double start
- validate training data path before worker start
- own QThread/worker lifecycle and cleanup
- forward log/progress/result events to the panel through callbacks or signals

Must not become a QWidget, call core training internals directly, write logs
directly to QTextEdit, or own Data Mapping update execution.

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

Predict input/result/status surface is table-first and unified.

Split table synchronization is not the final UX target.

Result visibility should be achieved through table layout, grouped columns,
horizontal scrolling inside the table, and optional frozen/result-column
strategy in a later explicit slice if needed.

Do not reintroduce hidden joined-copy behavior.

### 13.4 Variable-size batch behavior

UI must remain usable for small and large case counts.

Do not design around a fixed 10-row table.

Do not hard-code example counts such as 300. Counts shown in mockups are examples only.

### 13.5 Progress, cancel, and resource status

The workspace owns UI rendering only:

- run/cancel button state
- progress text or percentage
- row refresh and summary labels
- model/mapping/preprocess/schema badges

The workspace must not call core ML directly and should not own direct
`MODEL_FILE` / raw model-path existence checks after Arc 10 cleanup. Model
status should come through `PredictionService` or `PredictionController`.
Mapping status should come through the mapping repository, adapter, or
controller boundary.

The Train / Model tab follows the same separation. It renders training controls,
paths, progress, log output, target summary, and result state, but production
training execution must flow through `TrainingService`, `TrainWorker`, and
`TrainController`. Data Mapping update controls remain deferred until their
own service/controller boundary is explicitly scoped.

While prediction is running, row mutation commands should initially be disabled
unless a later explicit design protects running case IDs with equivalent
coverage.

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
- legacy Qt binding deletion

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
- no UI-thread or QThread direct `train_all_models` call accepted as production
  Train execution

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
