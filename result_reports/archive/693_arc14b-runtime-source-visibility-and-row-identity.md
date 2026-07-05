# Arc 14B-2F Runtime Source Visibility and Row Identity

## Goal

Stabilize the Arc 14B-2 read-only runtime mapping surface before Arc 14B-3 by
preserving source/path visibility on runtime load failure and making row
identity display unambiguous.

## Modified Files

- `apps/train/services/data_mapping_service.py`
- `apps/train/controllers/data_mapping_controller.py`
- `tests/test_apps_train_data_mapping_service.py`
- `tests/test_apps_train_data_mapping_controller.py`
- `tests/test_apps_train_data_mapping_ui_models.py`
- `docs/designs/2026-07-05-arc14b-runtime-mapping-repository-read-adapter.md`
- `docs/WORK_PLAN.md`

## Source Failure Visibility

- Added `DataMappingService.source_label` so the controller can read the
  configured provider source before `load_snapshot()` succeeds.
- `DataMappingController.refresh()` now preserves that source label in the
  error state when runtime loading fails.
- Missing runtime mapping paths remain errors and do not fall back to the
  foundation sample provider.
- Error state now emits a `load_failed` validation row instead of allowing the
  validation table to render an OK placeholder.

## Row Identity Display Policy

- Selected policy: A.
- Internal identity remains `MappingEntityRow.row_key`.
- Entity `key_attribute` remains catalog metadata for future edit/export
  contracts.
- The read-only row value table shows one identity column, `Row Key`, and the
  controller excludes the selected entity `key_attribute` from row value
  headers.
- Arc 14B-3 must still decide persisted edit/export key-attribute semantics.

## UI/Test Impact

- Service tests verify default runtime source labels are available before load.
- Controller tests verify missing runtime source/path survives load failure and
  row value headers omit key attributes.
- UI tests verify the panel shows source/path on load error, shows `load_failed`
  in validation, preserves no initial entity selection, and displays row
  identity through `Row Key`.

## Validation

- `python3 -m py_compile core/mapping/entity_runtime_adapter.py apps/train/services/data_mapping_service.py apps/train/controllers/data_mapping_controller.py apps/train/ui/data_mapping_view_models.py apps/train/ui/data_mapping_panel.py`: OK
- `python3 -m pytest tests/test_core_mapping_entity_runtime_adapter.py -q`: OK, 5 passed
- `python3 -m pytest tests/test_apps_train_data_mapping_service.py tests/test_apps_train_data_mapping_controller.py tests/test_apps_train_data_mapping_ui_models.py -q`: OK, 15 passed
- `git diff --check`: OK
- `python3 -B tools/check_code_structure.py`: OK with warnings; no new source file was added. Existing `apps/train/services/data_mapping_service.py` soft class-count warning remains accepted from Arc 14B-2.
- `python3 -B tools/code_checker/build_reference_map.py --check`: OK command, status STALE; regeneration skipped because this follow-up reused the existing service/controller/view-model owners.

## Onscreen / Computer Use Smoke

- DataMappingPanel standalone temp runtime data display: OK.
- Missing runtime source display: OK; source label showed
  `/tmp/arc14b2f_missing_mapping.json`, status message included the same path,
  and validation table showed `load_failed`.
- Row identity display: OK; empty runtime error state row table showed `Row Key`,
  `Active`, `Notes`, with no duplicated key-attribute value column.
- Computer Use `get_app_state`: OK.
- Computer Use keyboard substitute (`type_text`): OK.
- Computer Use click: OK with one Refresh click.
- Crash guard: OK; no initial `selectRow()` was restored.

## Structure

```yaml
change_gate:
  new_source: none
  hotspot_delta: small
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

Reference parity:
- Reused existing service/controller/view-model boundaries.
- UI still does not parse raw JSON.
- Runtime repository owner remains `core.mapping.repository`.

Structure Warnings:
- No new changed-file warning was introduced beyond the existing
  `apps/train/services/data_mapping_service.py` top-level class-count warning
  accepted in Arc 14B-2.

Read Ledger:
- `AGENT_TASK_ROUTER.md`: Result Report, UI, Coding, Smoke/Validation sections.
- `docs/WORK_PLAN.md`: Arc 14B status and next action.
- `docs/designs/2026-07-05-arc14b-runtime-mapping-repository-read-adapter.md`:
  Arc 14B-2 boundary and follow-up section.
- `result_reports/active/692_arc14b-runtime-mapping-repository-read-adapter.md`:
  runtime adapter/source and smoke evidence.
- `result_reports/active/691_data-mapping-panel-composition-slice-isolation.md`:
  AX crash guard evidence.
- Target source and tests listed in the prompt, narrowed to source label,
  controller error state, and row value projection paths.

## Excluded Scope

- No editable CRUD.
- No CSV v2 import/export.
- No mapping JSON write/save.
- No runtime reload.
- No cascade runtime integration.
- No Predict Schema Catalog or Feature Catalog changes.
- No schema/public API change.
- No UI layout rewrite.
- No initial entity row `selectRow()` restoration.
- No dependency changes.

## Manual Check Required

No manual check is required for the standalone DataMappingPanel path. Full
TrainShell smoke remains optional for a later shell-touching slice.

## Next Action

Arc 14B-3 - Data Mapping Manager editable CRUD or CSV v2 loader/exporter
boundary decision.

## Commit / Push Note

Final commit/push result will be reported in terminal output.
