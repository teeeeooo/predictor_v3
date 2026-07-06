# Arc 14D - Data Mapping XLSX Export / UI Polish Audit

## Purpose

Add a read-only XLSX review snapshot option to Data Mapping Manager export and
polish related UI/status wording without changing import, save semantics,
runtime cascade behavior, schema contracts, ML, model, or calculator logic.

## Current Export Path

Current JSON export is already split by owner:

- `core/mapping/editor_export.py` builds a read-only snapshot payload and writes
  pretty JSON.
- `DataMappingService.export_snapshot()` exports the current draft, including
  dirty draft edits, without saving `mapping.json`.
- `DataMappingController.export_json()` converts export success/failure into
  UI state and adds an Export issue row on failure.
- `DataMappingPanel._export()` opens a save-file dialog and calls the
  controller; the UI does not build raw JSON payloads.

The JSON payload already marks:

- `snapshot_type: mapping_editor_review_snapshot`
- `read_only: true`
- `import_contract: false`

## XLSX Dependency Audit

No project dependency manifest was found:

- no `pyproject.toml`
- no `requirements*.txt`
- no `setup.py` / `setup.cfg`
- no `Pipfile`, `poetry.lock`, or `uv.lock`

`openpyxl` is installed in the current Python environment, but it is not
declared as a project dependency and current production code does not import it.
Existing `openpyxl` imports are only under archived reverse-engineering scripts.

Decision for this slice: Arc 14D implementation is blocked until the project
explicitly approves and records a workbook writer dependency such as
`openpyxl` or `xlsxwriter`. Do not implement XLSX by hand with raw zip/XML.

## Dependency Approval Update

Bundle 2A and Bundle 2A-F record the dependency foundation required to resume
Arc 14D-R:

- `requirements/excel.txt` declares `openpyxl` for predictor_v3-generated XLSX
  write/export.
- `requirements/excel.txt` declares `xlwings` for Windows user Excel read
  workflows, especially DRM-sensitive reads.
- `requirements/ml_runtime.txt` separates Train/Predict shared ML runtime so
  `requirements/predict.txt` can support real `model.pkl` inference without
  adding training-only `optuna`.
- DRM-sensitive user-provided Excel files must not be read directly with
  `openpyxl` unless a future task explicitly changes that policy.
- Arc 14D-R may use `openpyxl` for generated read-only XLSX snapshot export.
- XLSX export implementation is still not done in Bundle 2A or Bundle 2A-F.

## UI / Status Findings

Data Mapping UI stale wording candidates:

- `DataMappingPanel` docstring still says "Read-only Mapping Entity / Master
  Data admin surface" even though the manager is now editable.
- Action keys still include internal `import_csv_v2` / `export_csv_v2`; user
  labels are currently generic Import / Export.
- Import disabled reason is currently "Read-only mode.", which is stale for an
  editable Data Mapping Manager.
- Export dialog currently offers JSON only.

Predict mapping status findings:

- `DropdownOptionAdapter.mapping_status()` can now return `invalid`.
- `mapping_status_badge_state()` currently maps all non-loaded/non-exists states
  to missing, so invalid appears like missing.
- `PredictWorkspace._handle_input_cell_edited()` distinguishes only missing vs
  normal mapping status.

## Intended Contract After Dependency Approval

- JSON export remains unchanged.
- XLSX export is a read-only review/share/report snapshot, not an import
  contract.
- XLSX export is generated with `openpyxl`; `xlwings` remains out of scope
  because this is not a user-provided Excel read workflow.
- XLSX workbook sheets should be user-facing groups first: IDU, Evap Index,
  ODU, Compressor, Refrigerant, Expansion, ODU Cond Specs, Issues, and a
  Snapshot Info or README sheet.
- Core owns workbook generation.
- Service owns export workflow.
- Controller owns result-to-state conversion.
- UI owns file path/filter selection only.
- Export targets the current draft, does not save `mapping.json`, and does not
  clear dirty state.

## Resume Scope

Bundle 2A and 2A-F resolved the dependency gate. Arc 14D-R resumes the blocked
implementation with generated XLSX export, JSON/XLSX export selection, stale
Data Mapping wording cleanup, and invalid mapping status wording polish.

Out of scope remains unchanged: Import, XLSX edit/reimport, Excel read,
`xlwings` implementation, Runtime Cascade changes, Predict schema CSV changes,
Feature Catalog changes, ML/model/calculator changes, and dependency structure
changes.
