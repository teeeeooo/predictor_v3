# Arc 14B-2 Runtime Mapping Repository Read Adapter

## Goal

Switch the Data Mapping Manager read-only source from the foundation sample
provider to the existing runtime mapping repository data, adapted into
`MappingEntityCatalog`.

## Scope

- Added a Qt-free runtime mapping adapter under `core.mapping`.
- Changed `DataMappingService()` default provider to runtime mapping.
- Kept foundation sample provider as explicit test/fallback injection only.
- Updated focused service/controller/UI tests to use deterministic injection.
- Added adapter tests for representative runtime mapping shapes.
- Added design note and updated the near-term work plan.

## Non-goals

- No mapping JSON write/save implementation.
- No CSV v2 import/export.
- No runtime reload.
- No editable CRUD.
- No cascade runtime integration.
- No Predict Schema Catalog or Feature Catalog changes.
- No UI layout rewrite.
- No initial entity `selectRow()` restoration.

## Runtime Mapping Shape Summary

- Runtime path owner remains `core.mapping.paths.MAPPING_JSON_FILE`, currently
  `data/mapping.json`.
- Runtime loader owner remains `core.mapping.repository.load_mapping_data()`.
- This checkout does not contain `data/mapping.json`; missing/empty runtime data
  now surfaces as a runtime provider load error rather than a silent sample
  fallback.
- Runtime mapping data is expected as a top-level object of section/table keys.
- Row keys are nested mapping keys; `cond_specs` uses a composite row key such
  as `ODU-A F&T 7 1`.
- Row values are usually attribute dictionaries. Cascade sections may contain
  list values such as available fins, pis, and rows.
- Nested dictionaries are not flattened; rows record notes for skipped nested
  values.

## Adapter Summary

- New owner: `core/mapping/entity_runtime_adapter.py`.
- `load_runtime_mapping_catalog()` calls the existing runtime loader, rejects
  empty/missing data, and adapts the loaded mapping.
- `adapt_runtime_mapping_data()` builds deterministic entities, attributes, and
  rows from table-shaped sections.
- Entity keys preserve runtime section keys.
- Key attributes use `<section_key>_key`; row identity remains the canonical
  `row_key`.
- Attribute type inference is conservative: boolean, number, then string.
- Existing `validate_mapping_entity_catalog()` remains the validation path via
  `DataMappingService.load_snapshot()`.

## Service Default Change

`DataMappingService()` now defaults to `RuntimeMappingCatalogProvider`.
`FoundationMappingCatalogProvider` remains available, but tests and fallback
harnesses must inject it explicitly.

## UI/Test Impact

- Controller and UI tests with foundation sample expectations now inject
  `DataMappingService(FoundationMappingCatalogProvider())`.
- Service tests verify the runtime default provider and a temp mapping JSON path.
- Adapter tests cover deterministic entity ordering, composite keys, list values,
  nested dict notes, repository-loader path use, and missing mapping rejection.
- Data Mapping UI still only renders read-only tables and disabled future
  actions.

## Validation

- `python3 -m py_compile core/mapping/entity_model.py core/mapping/entity_validation.py core/mapping/entity_runtime_adapter.py apps/train/services/data_mapping_service.py apps/train/controllers/data_mapping_controller.py apps/train/ui/data_mapping_panel.py apps/train/ui/data_mapping_models.py`: OK
- `python3 -m pytest tests/test_core_mapping_entity_model.py tests/test_core_mapping_entity_validation.py -q`: OK, 21 passed
- `python3 -m pytest tests/test_core_mapping_entity_runtime_adapter.py -q`: OK, 5 passed
- `python3 -m pytest tests/test_apps_train_data_mapping_service.py tests/test_apps_train_data_mapping_controller.py tests/test_apps_train_data_mapping_ui_models.py -q`: OK, 13 passed
- `git diff --check`: OK
- `python3 -B tools/check_code_structure.py`: OK with warnings; changed-file warning triaged below.
- `python3 -B tools/code_checker/build_reference_map.py --check`: OK command, status STALE; code map not regenerated for this slice.

## Onscreen / Computer Use Smoke

- DataMappingPanel standalone: OK with `/tmp/arc14b2_mapping.json` temp runtime
  provider; source label displayed `Runtime mapping repository:
  /tmp/arc14b2_mapping.json`; entity count was 3.
- TrainShell Data Mapping tab: not run; this checkout lacks production
  `data/mapping.json`, so full-shell default would intentionally show the
  runtime load error state.
- Computer Use `get_app_state`: OK; AX tree showed runtime source label,
  entities, attributes, rows, validation OK, and disabled future actions.
- Computer Use keyboard: OK with one `Tab` action.
- Computer Use click: OK with one Refresh button click.
- Crash guard: OK; no initial row `selectRow()` was restored.

## Structure

```yaml
change_gate:
  new_source: small
  hotspot_delta: small
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

Reference parity:
- Checked existing runtime mapping owners: `core.mapping.repository`,
  `core.mapping.paths`, `apps.predict.mapping.mapping_repository`, and
  `core.mapping.autofill`.
- Reused the existing core loader instead of creating a duplicate JSON parser.
- Kept Train UI provider wrapping in `apps.train.services` and core adaptation
  in `core.mapping`.

Structure Warnings:
- `apps/train/services/data_mapping_service.py` now defines 6 top-level classes,
  above the soft limit of 5.

Warning Triage:
- Current responsibilities remain service DTOs, provider protocol/providers,
  and snapshot orchestration for one narrow Data Mapping surface.
- The new provider class is thin and delegates all runtime mapping shape work to
  the core adapter.
- Action: accepted for this slice with reason; split provider classes only if a
  future CRUD/reload/persistence slice adds more provider responsibility.

Code map judgment:
- `code_map_check`: checked.
- The reference map is stale, but bounded keyword/source checks found the
  existing loader/provider owners needed for this slice.
- Regeneration was skipped because this implementation reused existing owners
  and the stale map is a broad repo maintenance issue.

Read Ledger:
- `AGENT_TASK_ROUTER.md`: Result Report, UI, Coding, Smoke/Validation sections.
- `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`: table/smoke validation and
  structure warning guidance.
- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`: report, validation,
  commit/push, and active report count policy.
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`: structured change gate and
  reuse/commonization fields.
- `docs/agent_workflows/DIFF_READ_BUDGET.md`: code map reuse gate.
- `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`: service/adapter
  dependency direction.
- `docs/WORK_PLAN.md`: Arc 14B current/next action.
- `docs/designs/2026-07-03-arc14a-mapping-entity-master-data-foundation.md`:
  core mapping entity boundary.
- `docs/designs/2026-07-03-arc14b-data-mapping-manager-ui-foundation.md`:
  read-only UI/service foundation.
- Reports `682`, `683`, `691`: prior foundation and AX crash guard evidence.
- Source/test files listed in the prompt, narrowed to owner functions/classes.

## Excluded Scope

All requested exclusions were preserved. The adapter is read-only; no
`mapping.json` write, runtime reload, CSV v2, CRUD, cascade runtime integration,
Predict Schema Catalog, Feature Catalog, dependency, or UI layout rewrite was
implemented.

## Manual Check Required

No manual check is required for the standalone DataMappingPanel path. Full
TrainShell runtime-data smoke still requires a real `data/mapping.json` in the
checkout.

## Next Action

Arc 14B-3 - choose and implement either Data Mapping editable CRUD boundaries or
CSV v2 loader/exporter, with write/reload policy decided before runtime
persistence changes.

## Commit / Push

Final commit/push result will be reported in terminal output.

## Project Memory Delta

- Data Mapping Manager production default is now runtime repository read-only,
  not the foundation sample provider.
- Missing runtime mapping data is an error state, not a sample fallback.
