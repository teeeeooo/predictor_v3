# Arc 14D-R - Data Mapping XLSX Export / UI Polish

## Purpose

Add a read-only XLSX review snapshot option to Data Mapping Manager export and
polish related UI/status wording without changing import, save semantics,
runtime cascade behavior, schema contracts, ML, model, or calculator logic.

## Implemented Export Path

JSON and XLSX export are split by owner:

- `core/mapping/editor_export.py` builds a read-only snapshot payload and writes
  pretty JSON or an `openpyxl` XLSX workbook.
- `DataMappingService.export_snapshot()` exports the current draft, including
  dirty draft edits, without saving `mapping.json` or clearing dirty state.
- `DataMappingController.export_snapshot()` converts export success/failure
  into UI state and adds an Export issue row on failure.
- `DataMappingPanel._export()` opens a save-file dialog and calls the
  controller based on JSON/XLSX file extension or selected filter; the UI does
  not build raw JSON payloads or workbook content.

The JSON payload already marks:

- `snapshot_type: mapping_editor_review_snapshot`
- `read_only: true`
- `import_contract: false`

## XLSX Dependency Audit

The original blocked Arc 14D audit found no project dependency manifest:

- no `pyproject.toml`
- no `requirements*.txt`
- no `setup.py` / `setup.cfg`
- no `Pipfile`, `poetry.lock`, or `uv.lock`

`openpyxl` is installed in the current Python environment, but it is not
declared as a project dependency and current production code does not import it.
Existing `openpyxl` imports are only under archived reverse-engineering scripts.

That blocker is now resolved by Bundle 2A and Bundle 2A-F. Do not implement
XLSX by hand with raw zip/XML.

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

Arc 14D-R now implements the generated XLSX writer with `openpyxl`. `xlwings`
remains reserved for future Windows user Excel read workflows and is not used
by this export implementation.

## UI / Status Results

Data Mapping UI wording changes:

- The panel and helper docstrings now describe an editable Data Mapping Manager.
- Internal action keys remain stable, but user-facing text does not expose CSV
  v2 implementation wording.
- Import remains disabled with the reason: "Import is not supported. Edit
  mappings in this screen."
- Export offers JSON and XLSX filters and marks the output as a read-only review
  snapshot that cannot be imported back.

Predict mapping status findings:

- `DropdownOptionAdapter.mapping_status()` can now return `invalid`.
- `mapping_status_badge_state()` maps invalid to `invalid` / `error`, distinct
  from missing.
- `PredictWorkspace._handle_input_cell_edited()` distinguishes missing mapping
  file messaging from invalid mapping data messaging.

## Export Contract

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

## Completion Scope

Bundle 2A and 2A-F resolved the dependency gate. Arc 14D-R completed the
generated XLSX export, JSON/XLSX export selection, stale Data Mapping wording
cleanup, and invalid mapping status wording polish.

Out of scope remains unchanged: Import, XLSX edit/reimport, Excel read,
`xlwings` implementation, Runtime Cascade changes, Predict schema CSV changes,
Feature Catalog changes, ML/model/calculator changes, and dependency structure
changes.
