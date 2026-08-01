# PySide6 Train/Predict Architecture Contract

## 1. Purpose

This document is the governing architecture contract for the new PySide6 Train/Predict UI in `predictor_v3`.

It is intended for Codex/agent implementation work. It defines the target package structure, file responsibilities, dependency boundaries, state model, UI layout, workflow, and verification expectations.

The design decision behind this architecture contract is recorded in:

- `docs/designs/2026-06-27-pyside6-train-predict-rewrite-design-gate.md`
- `docs/designs/legacy/2026-06-28-arc10-prediction-worker-progress-design.md`

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
`docs/designs/legacy/2026-06-27-pyside6-visual-table-parity-harvest.md` as the Arc 9.5
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
          composition.py

          application/
            __init__.py
            models.py
            prediction_usecase.py

          ports/
            __init__.py
            prediction_execution_port.py
            prediction_workflow_ports.py

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
              delegates.py

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
            pyside_prediction_runner.py
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
            data_definition_panel.py
            data_mapping_panel.py

          controllers/
            __init__.py
            train_controller.py
            data_definition_controller.py
            data_mapping_controller.py

          services/
            __init__.py
            training_service.py
            data_definition_service.py
            data_mapping_service.py

          ports/
            __init__.py
            training_execution_port.py

          adapters/
            __init__.py
            qprocess_training_runner.py

          jobs/
            __init__.py
            train_job.py

### 3.2 First production foundation structure

The first production foundation slices may use this smaller structure:

    predictor_v3/
      app_predict.py
      app_train.py

      apps/
        predict/
          __init__.py
          app.py
          composition.py
          application/
            __init__.py
            models.py
            prediction_usecase.py
          ports/
            __init__.py
            prediction_execution_port.py
            prediction_workflow_ports.py
          ui/
            __init__.py
            shell.py
            workspace.py
            tables/
              __init__.py
              case_table_model.py
              case_table_view.py
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
            pyside_prediction_runner.py

        train/
          __init__.py
          app.py
          ui/
            __init__.py
            shell.py
            train_model_panel.py
            data_definition_panel.py
            data_mapping_panel.py
          controllers/
            __init__.py
            train_controller.py
            data_definition_controller.py
            data_mapping_controller.py
          services/
            __init__.py
            training_service.py
            data_definition_service.py
            data_mapping_service.py
          ports/
            __init__.py
            training_execution_port.py
          adapters/
            __init__.py
            qprocess_training_runner.py
          jobs/
            __init__.py
            train_job.py

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
- Build the concrete Predict object graph through `apps.predict.composition`.
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

### 4.5 Runtime generation composition

Production embedded and standalone Predict composition must receive an immutable
generation-bound runtime snapshot. That snapshot is the execution owner for
schema/input mapping, Derived evaluation, One-hot encoding, ordered ML input,
zero-fill, active Target/result mapping, preprocessing, and compatibility
fingerprints. Default constructors and static catalogs are compatibility facades;
they must not be re-read by a production generation transition.

TrainShell owns one coordinator for equal Data Definition, Predict, Train, and
Data Mapping participants. Prepare is non-mutating, commit follows all-ready, and
rollback restores actual owner state. Participant revision evidence includes the
mutable user or resource boundary it prepared: Predict session/running state,
Train selection/file/header, Definition draft/base/controller state, and Mapping
draft/provider state. Standalone Predict uses the same Predict snapshot owner and
performs its own persisted-generation check at startup, Refresh, and immediately
before prediction.

Predict generation prepare asks the canonical session to issue one sealed
migration projection: case order, input/autofill/dirty fields and revisions,
typed results, destination Target descriptors, execution semantics, and loaded
model identity. Result keys migrate only through stable Result Feature identity.
The session validates the current canonical source, source-to-destination result
lineage, destination contract, revision, and case structure before any mutation.
The destination runtime snapshot is the generation-bound projection owner, but
its typed Target descriptors are not self-authoritative. It retains the
Data Definition Target registry's immutable ordered `RuntimeTarget` projection;
the application validator derives expected identity, ML name, Result Feature,
current Feature-owned key, the closed canonical unit, and fixed model-prediction
source from those existing owners. Supplied descriptors, active Target names,
and Target/result-key pairs must match that derived contract exactly before
composition or artifact issue, even when the session has zero results.
A presentation-only projection may keep a valid result current; a semantic
projection preserves its typed evidence as stale. Caller-constructed, altered,
or replayed projection DTOs are not install artifacts.

Rollback uses a distinct sealed snapshot issued from previously validated
canonical state. It restores that exact case/result/runtime contract, session
revision, and allowed-execution state, then consumes the artifact. Projection or
rollback rejection is atomic: case values, case revisions, results, run
authority, and session revision remain unchanged.

Sealed artifacts have an explicit transaction lifecycle. Participant abort
releases an unused migration artifact. Commit consumes migration and retains its
prior snapshot through the coordinator rollback window. Failed commit rolls back
and consumes that snapshot; successful whole-transaction completion calls
participant finalize to release it. Standalone generation refresh applies the
same finalize step. Repeated prepare/abort and successful cutovers therefore do
not retain full case/result/provenance projections for the session lifetime.

The generation-bound Predict runtime snapshot also owns an immutable
`PredictRuntimeColumnDescriptor` tuple. Each descriptor binds canonical
`FeatureDefinition.identity` to the current generation key, label, role,
visibility, Predict display order, value-source, Mapping, editor, and ML
metadata. The runtime builds identity association from the manifest and its
identity ordering, then fail-fast cross-checks the existing identity-free
generated Predict projection. Key, label, and position are never identity
fallbacks. Standalone and embedded composition consume this same tuple.

Train Target presentation consumes `TrainController.registry_snapshot()`. When
idle, list, order, count, waiting metrics, and Summary rows refresh together. A
running request keeps its frozen Target presentation; a newer process registry is
shown as distinct status and becomes the idle presentation after terminal state.

## 5. Dependency Rules

### 5.1 Allowed imports

Allowed:

- `apps.predict` imports PySide6.
- `apps.predict` imports `core.ml.inference`, `core.predictor_schema.columns`, `core.ml.registry`, `core.ml.preprocessing`, `core.utils` through services/adapters where possible.
- `apps.train.ui` and `apps.train.adapters` import PySide6; Train ports,
  controllers, services, and state remain Qt-free.
- `apps.train` imports `apps.predict.ui.workspace.PredictWorkspace`.
- `apps.train.jobs.train_job` imports `core.ml.training` inside the child process.
- Data Mapping repository access stays behind `DataMappingService`.

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

- model status, e.g. `모델 상태: model.pkl 로드됨`
- preprocess version, e.g. `preprocess: v1.0`
- mapping status, e.g. `데이터 매핑: 로드됨`

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
- `Data Definition`
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

Training log displays emitted log lines from the execution port.

### 7.5 Data Definition tab

The Data Definition tab is the current schema/feature-definition manager. It
owns guarded schema draft edits, validation/readiness projection, and explicit
save/restart/retrain feedback. The retired Feature Catalog manager is not a
top-level UI surface.

The existing table-first workspace also hosts the Basic Feature Manager actions:
controlled Add/Edit/Rename/Duplicate/Remove/Enable/Disable, explicit Predict or
ML Move, dependency Impact Preview, Reset Draft, and canonical Save. Selection
uses stable Feature identity; the view does not insert, delete, reorder, or
persist rows directly.

### 7.6 Data Mapping tab

The Data Mapping tab includes:

- runtime mapping source/status
- group, field, and value tables
- validation issues
- bounded add/duplicate/delete/edit commands
- review export, guarded save, and reload

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
- `input_values: dict[str, object]`
- `autofill_values: dict[str, object]`
- `dirty: bool`
- `input_revision: int` for prediction-relevant row-local mutation evidence

No PySide6 dependency.

### 8.2 `ResultRow`

Represents one accepted prediction result. The application contract stores raw
target outcomes; `result_values` is only the existing table-formatting facade.

Recommended fields:

- `case_id: str`
- `status: pending | running | complete | partial | error | invalid | cancelled`
- immutable `target_outcomes`, each identified by stable Target identity and
  result Feature identity with current result key, canonical unit, value source,
  and either finite raw numeric value or bounded unavailable/failed reason
- immutable execution context with session/case/run identity, case input
  revision, runtime generation trace, existing scoped semantic fingerprints,
  loaded Candidate identity, Active revision, and loaded-model generation
- `freshness: current | stale` plus a bounded stale reason, independent from
  the row execution status

No PySide6 dependency.

The current canonical unit catalog is a closed Predict application mapping for
the five validated stable Target identities (`W`, `Hz`, and `kg`). An unknown
active Target identity fails runtime composition rather than inventing a unit.
The unit and fixed `model_prediction` source are bound to the authoritative
runtime Target identity; a non-empty descriptor value is not acceptance
evidence. `PredictionTargetDescriptor` consumes this projection and never owns
Target semantics.
Adding unit authoring to Feature Definition is a separately approved schema
change and is not implied by this contract.

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
- one immutable session identity
- case-scoped input revisions and currently allowed execution context per case
- the immutable runtime-owned expected-target descriptor projection pinned with
  each allowed execution
- bounded stale-result rejection diagnostics
- `selected_case_ids`
- `model_status`
- `mapping_status`
- `run_state`
- `last_prediction_timestamp`

No direct PySide6 widget ownership.

`PredictSession` is the application-owned result acceptance gate. An executed
result attaches only if the active session, existing `case_id`, allowed run,
request input revision, pinned execution semantics, and pinned loaded model all
match. The same canonical gate also requires exactly one outcome for each pinned
Target identity, matching result Feature identity/key/unit/source metadata, and
an aggregate status consistent with the available/unavailable/failed set.
Target-derived errors carry the complete expected set; row-wide errors and
cancelled requests carry no synthetic target outcomes but retain immutable
execution context. Executed terminal rows cannot use the legacy direct result
setter, including empty, message-only, legacy-value, typed-only, context-only,
and bulk-setter forms. Direct session storage is an explicit allowlist for
non-executed `pending`, `running`, and `invalid` rows. Rejection does not mutate
input, result, row status, accepted progress, or counts.
Editing another case is unrelated; editing the same case increments only that
case revision, makes an existing typed result stale (or a running row pending),
and causes the old request result to fail closed.

This is a canonical state invariant, not an API-specific convention. The
session exposes its result map read-only and classifies every production
mutation as non-executed state creation, fresh executed-result acceptance,
validated canonical migration, sealed rollback/restore, freshness
transformation, or deletion. Every stored row must be a valid non-executed state
or a provenance-bearing executed terminal state. Fresh acceptance validates the
pinned request contract; migration validates both prior canonical lineage and
the destination runtime contract; rollback restores only a session-issued prior
snapshot. No private helper, bulk facade, generation projection, UI model, or
test fixture may install arbitrary terminal state.

`CaseStore` remains the case-order owner, but a bound session cleanup runs before
supported case deletion. It removes dependent result and allowed-execution
authority before the store publishes the new case order; one store mutation then
advances the session revision. Callback failure occurs before either boundary is
changed. Direct CaseStore removal, table-controller removal, and reset therefore
cannot expose a dangling result or terminal counts greater than total cases.

Generation and model transitions preserve typed outcomes and provenance. A
presentation-only generation change may update current keys by Feature identity
while remaining current because generation ID is trace-only for freshness.
Changes to ordered ML input, preprocessing, Derived, One-hot, Target registry,
Candidate identity, or Active revision mark the preserved result stale. Failed
reload and generation rollback restore/preserve the old usable environment and
must not change currentness.

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

The former split-table files were retired after the unified `CaseTableModel` /
`CaseTableView` path reached behavior parity:

- `apps/predict/ui/tables/input_table_model.py`
- `apps/predict/ui/tables/input_table_view.py`
- `apps/predict/ui/tables/result_table_model.py`
- `apps/predict/ui/tables/result_table_view.py`
- `apps/predict/ui/tables/table_sync.py`

Do not restore these modules as compatibility code. Regressions belong in the
unified table owner, and toolkit-neutral TSV helper coverage stays attached to
the unified Predict table tests.

## 10. Adapter Specification

### 10.1 Unified case table schema adapter

File:

- `apps/predict/schema/case_table_schema_adapter.py`

Responsibility:

- consume the generation-bound Predict application column descriptors
- preserve canonical Feature identity together with the current key, label,
  role, visibility, display order, value-source, Mapping, and adapter metadata
- preserve active-generation order for input/auto/result columns
- add app-side virtual status/message columns
- classify columns into input, auto-fill/calculated, prediction result, and
  app-virtual status/warning groups; app-virtual columns have no Feature identity
- expose editability, copyability, dropdown capability, width, and rendering
  role metadata

Must not:

- create identity or reconcile Features by key, label, or column position
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
- return the application-owned `PredictionInputOutcome` /
  `PredictionInputRequest` contracts
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
- consume the application-owned `PredictionServiceResult` contract
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
- accept application-owned `PredictionInputRequest` values
- return application-owned `PredictionServiceResult` values
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

`PredictionJob`, `PredictionProgress`, `PredictionWorkerSummary`, and the
`PredictionExecutionPort` contract are owned by
`apps/predict/ports/prediction_execution_port.py`; the worker and PySide runner
consume them rather than re-exporting adapter-owned DTOs.

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

- provide Qt-free training request validation and resource status
- provide a clean call boundary for the controller
- remain Qt-free
- validate the training data path before execution
- return structured validation/resource-status contracts

The validation service must not run training or change core ML algorithms,
preprocessing, or canonical Target registry semantics. Production composition
freezes the immutable canonical registry snapshot into `TrainingRequest`.
`apps/train/application/training_lifecycle.py` is the shared Qt-free application
boundary that coordinates validation, execution, cancellation, terminal results,
and Candidate publication. `TrainController` is a UI adapter over that boundary.

Arc 11 correction: production Train execution must not be accepted as a direct
in-process `train_all_models()` call behind QThread. Production training must
flow through an execution port and killable process runner adapter. The visible
`중지` action must stop the running process, and cancelled/error runs must not
leave partial final model artifacts.

DEV-only fast training smoke belongs under `tools/dev/mock_smoke/`, not under
production `apps/` or `core/`. The DEV backend may create an
inference-compatible mock model artifact by reusing the existing mock artifact
generator, and it must not claim real training quality or metrics.

### 11.5 Training execution port and process adapter

Files:

- `apps/train/ports/training_execution_port.py`
- `apps/train/adapters/qprocess_training_runner.py`
- `apps/train/jobs/train_job.py`

Responsibility:

- keep the controller dependent on a Qt-free `TrainingExecutionPort`
- let the `QProcessTrainingRunner` adapter own `QProcess`, Qt signal wiring,
  cancellation escalation, and Qt resource disposal
- run real core training only in the child-process job
- write the completed bundle only to the caller-provided Candidate staging path
  and remove process-owned temporary output on cancellation or failure
- compose the production adapter in `apps/train/app.py`

The controller must not import PySide6 or a concrete process runner. A runner
instance is single-run and is disposed after a terminal callback.

### 11.5A Model lifecycle repository and application boundary

Files:

- `apps/common/model_lifecycle/`
- `apps/predict/application/model_lifecycle.py`
- `apps/train/application/training_lifecycle.py`
- `apps/train/application/candidate_publication.py`

Responsibility:

- resolve one default workspace below the platform user-state root without using
  the repository path as permanent workspace identity
- publish hash-checked, deserializable, versioned Candidate bundles through
  same-filesystem staging, fsync, writer serialization, and atomic rename
- reject symlinked or non-regular staging, Candidate, model, and metadata
  objects, and verify lexical plus resolved containment beneath the exact
  lifecycle workspace before reads, writes, or publication
- keep Candidate publication separate from Active selection
- store an atomic revision-guarded Active reference with traceable activation
  history
- require every Active mutation, including first activation, rollback, and
  legacy continuity, to supply the caller-observed current revision; omission,
  null, and stale revisions fail closed
- revalidate current Definition/runtime fingerprints, preprocessing, production
  Targets, feature order, experimental-feature policy, deserialize integrity, and
  bounded prediction smoke before promotion or rollback re-promotion
- import a legacy `model.pkl` idempotently without moving, deleting, or modifying
  the original, and activate it only when full compatibility is proven
- report known corruption of an existing deterministic legacy Candidate as a
  controlled retraining-required state rather than a startup exception
- resolve Predict startup to one immutable Active Candidate path or a controlled
  missing/invalid Active status
- compare the process-loaded Candidate plus Active revision with the current
  lifecycle Active through a Predict application owner, without UI filesystem
  reads or automatic hot-swap
- prepare a replacement service against one complete immutable runtime snapshot,
  fully validate and deserialize it off to the side, then install it under a
  final Active revision guard only while Predict is idle
- preserve the prior loaded service and identity on every reload preparation,
  compatibility, recovery, corruption, or Active-race failure
- assign every refresh and explicit reload a monotonic application-owned
  observation identity; only the current operation may install a service or
  publish shared lifecycle status, stale callers may retain their observed
  result, and controller/UI adapters render the read-only authoritative current
  status instead of starting an unguarded replacement refresh
- return structured reload/export reason codes, preservation state, recommended
  action, raw diagnostic, and diagnostic traceback; default UI consumes only
  the user guidance and retains internal detail in its diagnostics state
- route prediction-running reload and unexpected export failures through those
  application-owned outcomes; UI event containment does not parse exception
  strings and never exposes raw internal details in the default message
- derive immutable deployment exports only from a guarded current Active
  Candidate, publish them from verified staging without overwrite, and leave
  Candidate, Active, history, and source artifacts unchanged

Core ML writes one multi-target bundle to a caller-selected staging path and does
not import lifecycle infrastructure. The QProcess adapter, child job, Train UI,
and Predict UI do not write the Active reference. An already constructed
`PredictionService` retains its loaded model/path when Active changes. Phase 5E
status observation only marks reload required; an idle explicit reload installs
one fully prepared replacement under the final Active guard, while failure
keeps the prior service usable.

The QProcess adapter owns one terminal arbiter. Accepted cancellation produces
exactly one `cancelled` callback even when error and finished signals race;
genuine launch failure produces `failed`, and terminal cleanup releases the
process and its escalation timer before application callbacks run.

### 11.5B Shared experiment and headless boundary

Files:

- `apps/train/application/experiments/`
- `apps/train/adapters/subprocess_training_runner.py`
- `apps/train/interfaces/headless/cli.py`
- `apps/train/composition/experiments.py`
- `app_experiment.py`

Responsibility:

- resolve one strict versioned Experiment Specification for GUI and headless
  callers with explicit defaults and reject unknown/future fields
- freeze Definition/runtime registry and Derived evaluator, preprocessing,
  optimization, evaluation, and build identities into each run
- convert the resolved contract to the existing immutable `TrainingRequest`
  and delegate to `TrainingLifecycleService`, never a second training pipeline
- persist immutable run records and atomic current-version campaign records
  below the lifecycle workspace without caller-selected output paths
- execute only explicitly configured bounded campaign experiments and attempts
- treat the child job's structured Core-training-start acknowledgement as the
  sole iteration-consumption event; accepted requests, adapter construction,
  and process launch are preflight
- preserve pause-after-current, cancel-current, resume, retry, and terminal
  evidence outside Core ML
- serialize GUI, single-run, campaign, and resume writers through one
  non-stealable OS advisory lock acquired after validation and before staging;
  expose owner, process, timestamps/heartbeat, stage, run, and campaign
- expose versioned JSON output and stable exit classes without treating natural
  language as the decision contract
- derive identifiable clean/dirty build identity from the application
  repository root rather than caller `cwd`; uncertain saved/current identity
  blocks resume without mutating the stored campaign
- construct headless services without Bootstrap publication; `validate` is pure
  contract validation and `resolve` reads an existing generation only, while
  validated training mutation explicitly initializes Bootstrap when required

The headless adapter has no promotion, caller-triggered Definition publication,
Active mutation, deployment replacement, cleanup, arbitrary-code, or
arbitrary-output command. GUI keeps its visible training flow; its data
selection uses the shared resolver, and a concise label projects external
Campaign status.

### 11.5C Agent-assisted campaign decision boundary

Files:

- `apps/train/application/experiments/agent_*.py`
- `apps/train/application/experiments/candidate_gate.py`
- `apps/train/application/experiments/leaderboard.py`
- `apps/train/application/experiments/recommendation.py`
- `apps/train/application/experiments/campaign_operator.py`

Responsibility:

- accept only externally supplied versioned proposals one step at a time
- own total iteration allowance, allowed categories, baseline classification,
  configured metric direction/tolerance, guardrails, and instability thresholds
- persist hypothesis plus resolved before/delta/after evidence before invoking
  the Phase 5F execution owner
- retain accepted proposal identity and a training-meaning-derived execution
  key across pre-start failure/resume, so proposal ID or descriptive metadata
  cannot reset the persisted total attempt allowance
- project lifecycle/result evidence into hard gates and deterministic
  leaderboard/incumbent state without changing Active
- fail closed when a configured guardrail or instability requirement lacks
  resolvable evidence, while keeping the Candidate as exploratory/history
  evidence
- normalize every selection-critical metric through one finite-number
  projection boundary; non-finite current/baseline evidence remains
  diagnostically distinguishable but cannot enter aggregation, ranking,
  recommendation, or machine-readable numeric output
- preserve immutable approval-required recommendation history
- expose budget increase only through a separate operator command with
  before/after approval evidence

This boundary does not generate experiments, call an LLM, publish canonical
Definitions, promote Active, replace deployment, delete artifacts, or perform
Phase 5H final confirmation. The existing Train surface is a read-only
projection of the same campaign store.

### 11.6 Data Mapping service

File:

- `apps/train/services/data_mapping_service.py`

Responsibility:

- load and validate the runtime mapping draft
- expose mapping resource status and bounded edit/save/export/reload operations
- keep filesystem and mapping repository details out of QWidgets

## 12. Controller Specification

### 12.1 Predict controller

File:

- `apps/predict/controllers/prediction_controller.py`

Responsibility:

- handle command bar actions
- choose prediction scope
- coordinate session, application usecase, service port, and execution port
- prepare requests through the injected application usecase on the UI thread
- apply invalid and running result rows on the UI thread before worker start
- start execution through `PredictionExecutionPort`
- receive worker row/progress/finish/cancel/failure events on the UI thread
- apply result updates to `PredictSession` on the UI thread
- ignore late row/progress/terminal events whose run identity is not active;
  executed rows still pass the session-owned acceptance gate
- treat worker progress and terminal summaries as transport evidence: advance
  user-facing progress once per canonically accepted case and calculate the
  final application summary from accepted complete/partial/error/cancelled
  dispositions plus pre-run invalid rows; expose unresolved rows when accepted
  dispositions do not cover the requested total
- send cooperative cancellation and infrastructure failure through the same
  context-preserving canonical acceptance path before revoking run authority
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
- import concrete prediction adapters or PySide runner classes

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
- coordinate request validation/service and the training execution port
- update Train / Model panel state
- expose `start(...)`, `cancel()`, `is_running`, and resource status
- reject double start
- validate training data path before execution start
- clear the active port after terminal execution
- forward log/progress/result events to the panel through callbacks or signals

Must not import PySide6 or a concrete runner, become a QWidget, call core
training internals directly, write logs directly to QTextEdit, or own Data
Mapping update execution.

### 12.4 Data Mapping controller

File:

- `apps/train/controllers/data_mapping_controller.py`

Responsibility:

- handle Data Mapping table actions
- call `DataMappingService`
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
training execution must flow through `TrainingService`, `TrainController`, the
`TrainingExecutionPort`, and its process adapter. The adapter owns concrete Qt
process lifecycle; the controller owns application state only. Data Mapping
resource checks and operations flow through its service/controller boundary.

While prediction is running, row mutation commands should initially be disabled
unless a later explicit design protects running case IDs with equivalent
coverage.

Idle prediction execution is enabled only when `PredictionController` reports
that the current process has a usable loaded prediction service. Lifecycle
labels such as reload-required, reload-failed, or Active-unavailable are not
execution blockers when the prior loaded model remains usable. The workspace
projects this controller-owned capability without inspecting Active references,
model paths, or Train UI.

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
- implement Data Definition tab
- implement Data Mapping tab
- implement the training execution port and process adapter
- wire training log/progress

Forbidden:

- changing `core.ml.training` algorithm
- changing Optuna/RFECV settings unless explicitly scoped
- changing model artifact schema

Verification:

- execution port/process-adapter smoke
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

- training execution port/controller test
- process adapter smoke
- train service boundary test
- log/progress callback smoke if feasible
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
