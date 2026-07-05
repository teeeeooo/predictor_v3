# Arc 14B-4 Legacy Mapping CSV To JSON Rule Reconstruction Audit

## Goal

Audit whether the old "single CSV to mapping.json" mapping update flow can be
reconstructed from current repo evidence, and decide whether the next Data
Mapping Manager work should pursue import/export or UI CRUD.

## Files Read

- `AGENT_TASK_ROUTER.md`: Work Contract, Design First Gate, Result Report,
  docs sync, and commit routing.
- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`
- `docs/agent_workflows/DOCUMENT_SYNC_AND_LIFECYCLE.md`
- `docs/WORK_PLAN.md`
- `docs/designs/README.md`
- `docs/designs/2026-07-03-arc13-5r-predict-schema-mapping-manager-foundation.md`
- `docs/designs/2026-07-03-arc14a-mapping-entity-master-data-foundation.md`
- `docs/designs/2026-07-03-arc14b-data-mapping-manager-ui-foundation.md`
- `docs/designs/2026-07-05-arc14b-runtime-mapping-repository-read-adapter.md`
- `result_reports/active/692_arc14b-runtime-mapping-repository-read-adapter.md`
- `result_reports/active/693_arc14b-runtime-source-visibility-and-row-identity.md`
- `result_reports/active/696_data-mapping-user-facing-copy-simplification.md`
- `result_reports/memory/project_memory_seed.md` mapping-related entries only.
- `core/mapping/paths.py`, `repository.py`, `update.py`, `autofill.py`,
  `entity_runtime_adapter.py`, `entity_model.py`, `entity_validation.py`
- `apps/predict/mapping/mapping_repository.py`
- `apps/predict/adapters/dropdown_option_adapter.py`
- `apps/predict/controllers/input_edit_controller.py`
- `apps/train/services/data_mapping_service.py`
- `apps/train/controllers/data_mapping_controller.py`
- `apps/train/ui/data_mapping_panel.py`
- `config/predict/schema.csv`
- `config/ml/features.csv`
- `tests/fixtures/mapping/mapping_tables_legacy_wide.csv`
- Focused mapping tests and mock smoke mapping generator.
- Limited git history for mapping/csv filenames, current converter origin, and
  the legacy wide fixture introduction.

## Evidence Found

| Evidence | Result |
| --- | --- |
| Runtime path/reader | `core.mapping.paths.MAPPING_JSON_FILE` points to `data/mapping.json`; `load_mapping_data()` returns `{}` on missing/invalid JSON. |
| Predict consumers | Dropdown options read section keys; autofill reads section and attribute keys directly. |
| Train Data Mapping consumer | Data Mapping Manager adapts runtime mapping into `MappingEntityCatalog` read-only and surfaces missing data as a load error. |
| Current converter | `core.mapping.update.update_mapping_to_json()` supports Excel sheets and CSV, but CSV becomes one `Sheet1` section. Only a sheet named `ODU` gets two-track `odu_cascade` / `cond_specs` conversion. |
| Fixture | `tests/fixtures/mapping/mapping_tables_legacy_wide.csv` exists, but no parser or test consumes it. |
| History | No deleted dedicated single-wide-CSV parser, tracked `data/mapping.json` sample, or authoritative header alias contract was found in the limited file/history search. |

## Mapping Shape Summary

Current runtime consumers expect section-shaped JSON:

- `idu`: row key -> `ID Volume` and optional future attributes such as `Size`.
- `evap_index`: row key -> `Evap Area`, `Evap Volume`, optional `Size`.
- `odu`: row key -> `OD Volume`.
- `compressor`: row key -> `Comp EER`, `Comp cc`.
- `odu_cascade`: ODU row key -> `Available_Fins`, `Available_Pis`,
  `Available_Rows` lists.
- `cond_specs`: composite `ODU Fin Pi Row` key -> `Cond Area`, `Cond Volume`.
- `fin_type`, `pi`, `row`: optional base dropdown sections.
- `ref_type`, `exp_type`: optional because current fallback options exist.

The legacy wide fixture does not exactly match this shape: it uses headers such
as `Volume`, `Evap area`, `EER`, `cc`, duplicate `ODU` blocks, and `Cond Index`.
Those require new alias and composite-key decisions.

## Legacy CSV Reconstruction Feasibility

Judgment: C - not feasible as a recovered legacy import.

Partial evidence exists for a human-readable wide table, but the executable
legacy rule is absent. Current converter behavior would not create useful
runtime sections from a single CSV; it would create `Sheet1`.

If a wide CSV compatibility parser is ever required, it must be designed as a
new explicit contract with aliases, duplicate-block handling, `Cond Index`
policy, validation, and no promise that old spreadsheets are automatically
safe.

## Export Role Decision

Export should be a read-only review snapshot, not an editable import contract.

- Avoid single CSV as the primary export because it recreates the ambiguous
  wide shape.
- Prefer a one-file XLSX workbook snapshot for human review when export is
  implemented.
- Keep pretty JSON snapshot as the exact/dependency-light fallback.
- Do not promise export -> edit -> reimport.

## Recommendation

C - proceed with UI CRUD workflow design. Keep Import disabled or remove it
from the first editable flow. Keep Export scoped to read-only review snapshots.

## Validation

- `git diff --check`: OK.
- `python3 -B tools/check_code_structure.py`: OK with existing soft warnings
  only; this slice changed docs/report files and added no source files.
- `git status --short`: expected docs/design/report changes only before
  staging.
- `py_compile` / `pytest`: not run because this task changes docs/report only
  and production code/tests/data fixtures remain untouched.

## Excluded Scope

- No CSV import implementation.
- No export implementation.
- No editable CRUD implementation.
- No mapping JSON write/save.
- No runtime reload.
- No multi-file package.
- No `groups.csv` / `fields.csv` / `data/<group>.csv`.
- No normalized `values.csv`.
- No production code, tests, fixtures, schema, UI, Predict Schema Catalog,
  Feature Catalog, golden expected, or core calculation changes.

## Manual Check Required

No manual GUI check is required for this audit-only slice. A future CRUD design
or implementation will need its own UI validation plan.

## Next Action

Arc 14B-5 - Data Mapping Manager UI CRUD workflow design with Import disabled
and Export scoped to read-only review snapshots.

## Commit / Push Note

Final commit/push result will be reported in terminal output.

## Project Memory Delta

- type: decision
  topic: Arc 14B Data Mapping import/export direction
  content: Legacy single CSV to mapping.json reconstruction is not recoverable enough for implementation; proceed with UI CRUD workflow design, keep Import disabled, and scope Export to read-only review snapshots.
  keywords: predictor_v3, Arc 14B, Data Mapping, mapping.json, CSV import, export snapshot
