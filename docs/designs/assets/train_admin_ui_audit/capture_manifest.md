# Train/Admin UI Capture Manifest

## Environment

- Base commit: `cbc054a95ba5a39fecb35681b16251e05a51ce4b` (`origin/main` on 2026-07-13)
- OS: macOS 26.5.2, arm64
- Display resolution: Built-in Retina 4.5K `4480 x 2520` (main); secondary display `1920 x 1080`
- App window size: `1154 x 768` capture resolution
- Python / environment: Python 3.14.4, `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`
- Launch command: `python3 app_train.py`
- Capture date: 2026-07-13 (Asia/Seoul)
- App launch result: Window opened successfully as `HVAC Training Studio`.
- Launch warning: stderr reported twice that `data/mapping.json` was missing and the basic UI would be constructed.

## Resource Status

- `model.pkl`: Missing at `model/model.pkl`; shell status showed `model.pkl 없음`.
- training CSV: No runtime training CSV found in the checkout; shell status showed `학습 데이터: 없음`.
- `mapping.json`: Missing at `data/mapping.json`; Data Mapping showed a load error.
- `schema.csv`: Present at `config/predict/schema.csv` (5,627 bytes; SHA-256 `0a165f95f6867badf6885b42817b9d6b45a299c75f077fbebf8f9c435a4b09104`).
- `features.csv`: Present at `config/ml/features.csv` (1,883 bytes; SHA-256 `0a6cc9df3bdb5fd9faebe82b2a8e1d7b9e2c49a0e3a87aabd4448a669292e704`).

## Capture Index

### 01_train_shell.png

- Selected tab: `Predict` (first tab on launch)
- Scroll position: Not applicable
- Screen state: Full shell immediately after launch.
- Visible behavior: Top status showed `model.pkl 없음`, preprocessing `v1.0`, `학습 데이터: 없음`, and `데이터 매핑: 없음`. Tabs `Predict`, `Train / Model`, `Data Definition`, and `Data Mapping` were visible.
- Notes: The Predict table contained three empty cases; no Predict or Train action was run.

### 02_data_definition_top.png

- Selected tab: `Data Definition`
- Scroll position: `0`
- Screen state: First entry with command bar, Summary, and Draft table start.
- Visible behavior: `Refresh`, `Reset Draft`, and `Save` were visible. Summary showed report `ready`, 28 projected features, 28 current catalog features, 0 parity issues, 8 mapping requirements, and 2 one-hot relationships.
- Notes: No Data Definition cell was edited and `Save` was not clicked.

### 03_data_definition_draft_left.png

- Selected tab: `Data Definition`
- Scroll position: `0`
- Screen state: Draft table left-side columns.
- Visible behavior: Draft rows showed `Source`, `Order`, `Column Key`, `Label`, `Role`, `Editor`, `Data Type`, `Visible`, `Required`, `Readonly`, `Value Source`, `Mapping Entity`, `Mapping Attribute`, and `Trigger Column`. Rows visibly mixed manual and rule-based value sources, with some blank mapping cells.
- Notes: This is the unedited in-memory draft; no save was performed.

### 04_data_definition_draft_right.png

- Selected tab: `Data Definition`
- Scroll position: `0`, Draft table horizontally scrolled right.
- Screen state: Draft table right-side columns.
- Visible behavior: The table showed `Mapping Attribute`, `Trigger Column`, `Rule ID`, `Model Input`, `ML Name`, `One-hot Group`, `Active`, and `Notes`, including rule IDs and feature notes.
- Notes: Horizontal scrolling changed the visible columns only; no cell value was changed.

### 05_data_definition_changes_and_save.png

- Selected tab: `Data Definition`
- Scroll position: `624`
- Screen state: Lower diagnostic area.
- Visible behavior: `Draft Changes` showed `No draft changes.`; `Save Plan Preview` showed `schema_csv no_op` and blocked `features_csv` / `derived_policy` rows; `Save Blockers` showed `No save blockers.`
- Notes: `Save Result` was not yet visible in this frame; the Save command remained unused.

### 06_data_definition_projection.png

- Selected tab: `Data Definition`
- Scroll position: `1248`
- Screen state: Save result and projection area.
- Visible behavior: `Save Result` showed `No save attempted.`. `Projected Features` listed active rows such as Cooling Capa, Heating Capa, ID Volume, Evap Area, Evap Volume, OD Volume, Cond Area, and Cond Volume. `Mapping Requirements` began below.
- Notes: This is a read-only observation of the current report.

### 07_data_definition_onehot_and_readiness.png

- Selected tab: `Data Definition`
- Scroll position: `1872`
- Screen state: Lower mapping, one-hot, and readiness area.
- Visible behavior: Mapping requirement rows included `cond_specs` / `cond_specs_lookup`; `One-hot Relationships` showed `exp_type` and `ref_type` relationships with parity `OK`; Readiness listed `training_headers`, `model_activation`, and `restart_impact` as `not_evaluated`.
- Notes: The readiness messages stated that no training data path was provided, model artifacts are not inspected by Arc 15A, and schema changes remain restart-required with no live reload attempted.

### 08_data_definition_issues.png

- Selected tab: `Data Definition`
- Scroll position: `2182`
- Screen state: Bottom of the report.
- Visible behavior: Readiness remained visible above `Issues`. Issues contained three informational rows for training headers, model activation, and restart impact.
- Notes: No validation issue was created by this audit; these were the existing report issues.

### 09_data_mapping_default_and_issue.png

- Selected tab: `Data Mapping`
- Scroll position: Not applicable; default view.
- Screen state: Runtime mapping load failure.
- Visible behavior: `Groups` had no rows; `Fields` and `Data` were empty; `Refresh` was enabled while `Add Row`, `Duplicate`, `Delete`, `Export`, `Save`, and `Reload` were disabled. `Issues` showed an error that runtime mapping data was empty or unavailable at `data/mapping.json`.
- Notes: This single frame is also the available Data Mapping issue state.

## Unavailable Capture States

- General group (`IDU` or `Evap Index`): Not captured because the runtime `data/mapping.json` file was absent and the Groups table had no selectable rows.
- Complex group (`ODU Cond Specs`): Not captured for the same reason; no group selection was possible.
- Data Mapping selected-group state, row-selected Duplicate/Delete state, and dirty state: Not captured because the table had no data, the row actions remained disabled, and no temporary data was introduced.

## Temporary Interaction Record

- Temporary draft edits: None.
- Validation issue created: None. The Data Mapping load error was pre-existing and caused by the missing runtime file; it was not created by editing.
- Save performed: No.
- Runtime files modified: No. `model/model.pkl` and `data/mapping.json` were missing before and after; the SHA-256 values of `config/predict/schema.csv` and `config/ml/features.csv` were unchanged.
- Draft reset/discard method: No dirty draft was created. The app was quit after capture so any in-memory state was discarded.
- Model retraining / Predict execution: Not performed.

## Observations

- `Data Definition` presents a visible `Save` command while its Summary reports `Schema save preview: Not allowed` and the Save Plan contains blocked targets.
- `Data Mapping` shows an active `Refresh` button alongside disabled Add/Duplicate/Delete/Export/Save/Reload controls while the Groups, Fields, and Data areas are empty.
- The selected tab is shown by the tab styling; no group selection indicator could be observed because the Groups table had no rows.
- The Data Definition report is split across vertical scroll positions `0`, `624`, `1248`, `1872`, and `2182`; the Draft table also requires horizontal scrolling to see its right-side columns.
- Tables visibly use internal-style values such as `schema_row`, `readiness_training_headers`, and `cond_specs_lookup` in the current screen.
- The Readiness section explicitly states `restart_impact not_evaluated` and that schema changes remain restart-required with no live reload attempted.
- The Data Mapping source path is shown in the panel as `.../data/mapping.json`, and the Issues table repeats the missing/empty runtime mapping error.
