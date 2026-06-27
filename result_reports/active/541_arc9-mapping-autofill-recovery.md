# 541 Arc 9 Mapping Autofill Recovery

## Goal

Recover PySide6 Predict dropdown/autofill behavior through the `core.mapping`
owner and app-side controller boundaries.

## Changes

- Implemented Qt-free `core/mapping/autofill.py` pure logic:
  - simple dropdown-to-auto mapping from schema `source` / `mapping_key`
  - IDU-style autofill
  - ODU upstream dependent clears for `fin_type`, `pi`, `row`, `cond_area`,
    and `cond_volume`
  - ODU cascade option extraction
  - `cond_specs` lookup for `Cond Area` / `Cond Volume`
- Updated `core/mapping/repository.py` to default to
  `core.mapping.paths.MAPPING_JSON_FILE`.
- Added `apps/predict/mapping/mapping_repository.py` as the app boundary around
  core mapping loading.
- Added `apps/predict/controllers/input_edit_controller.py` to coordinate edit
  event -> autofill -> state update -> result clear.
- Wired `PredictWorkspace` / `InputTableModel` edit callbacks through the input
  edit controller.
- Added focused tests for core autofill and app-side controller behavior.

## Boundary Decision

- `core.mapping.autofill` is pure and imports no PySide6, PyQt5, tkinter, or
  widget APIs.
- Table models do not load mapping JSON and do not call prediction services.
- Workspace/controller owns edit side effects; table model only reports the
  edited case/key.
- Mapping JSON schema is unchanged.
- Dynamic dropdown option rendering is recorded as a remaining PySide6 table
  adapter gap; this slice computes dependent options but does not implement a
  dropdown delegate.

## Validation Notes

- `data/mapping.json` is absent in this checkout, so file-backed real mapping
  smoke is limited to safe load/import behavior.
- Unit/controller tests use sample mapping data to cover legacy IDU simple
  autofill, ODU cascade clearing, and `cond_specs` fill behavior.

## UI/UX Contract Check

- Mapping updates preserve row identity through row headers and internal
  `case_id`.
- Intentionally deferred table parity gaps remain: dropdown delegate rendering,
  TSV copy, TSV paste, Delete/Backspace clear, grouped undo, Tab/Enter
  navigation, click/type replace-on-type, and validation rendering.

## Verification

- `python3 -B -m py_compile core/mapping/*.py apps/predict/**/*.py`
- `python3 -B -c "from core.mapping.autofill import build_autofill_updates"`
- `python3 -B -c "from core.mapping.repository import load_mapping_data; from core.mapping.paths import MAPPING_JSON_FILE; assert MAPPING_JSON_FILE"`
- `rg -n "PyQt5|PySide6|tkinter|QApplication|QFileDialog" core/mapping || true`
- `python3 -B -m pytest tests/test_core_mapping_autofill.py tests/test_apps_predict_mapping_controller.py tests/test_apps_predict_table_models.py`
- `git diff --check`
- `git status --short`

## Excluded Scope

- No mapping JSON schema changes.
- No ML algorithm, model artifact, feature list, target list, preprocessing
  formula, calculator formula/config/fixture/golden, or public result contract
  changes.
- No worker/progress/cancel implementation.
- No Trainer foundation implementation.
- No legacy PyQt behavior refactor.

## Next Action

Arc 9 Slice 5 - Row-to-ML input adapter and prediction result adapter recovery.
