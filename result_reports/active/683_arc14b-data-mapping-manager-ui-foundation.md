# Arc 14B-1 Data Mapping Manager UI Foundation

## Goal

Add a read-only Train/Admin Data Mapping Manager foundation surface and complete
small Arc 14A follow-up decisions for `active` semantics and
`row_key`/`key_attribute` identity.

## Modified Files

| File | Change |
| --- | --- |
| `core/mapping/entity_model.py` | Documented active and row-key/key-attribute semantics. |
| `core/mapping/entity_validation.py` | Added key attribute mismatch validation and inactive row required/type skip behavior. |
| `tests/test_core_mapping_entity_model.py` | Added canonical row identity test. |
| `tests/test_core_mapping_entity_validation.py` | Added inactive attribute/row/entity and key-attribute relation tests. |
| `apps/train/services/data_mapping_service.py` | Added read-only Data Mapping service, provider protocol, sample provider, snapshot, disabled action metadata. |
| `apps/train/controllers/data_mapping_controller.py` | Added UI-facing Data Mapping controller state projection. |
| `apps/train/ui/data_mapping_models.py` | Added read-only Qt table model for Data Mapping tables. |
| `apps/train/ui/data_mapping_view_models.py` | Added presentation row/header helpers. |
| `apps/train/ui/data_mapping_panel.py` | Replaced placeholder with read-only entity/attribute/row/validation/action surface. |
| `tests/test_apps_train_data_mapping_service.py` | Added service foundation tests. |
| `tests/test_apps_train_data_mapping_controller.py` | Added controller foundation tests. |
| `tests/test_apps_train_data_mapping_ui_models.py` | Added table model/view-model and offscreen panel construction tests. |
| `docs/designs/2026-07-03-arc14b-data-mapping-manager-ui-foundation.md` | Added Arc 14B-1 design record. |
| `docs/designs/README.md` | Indexed the new design record. |
| `docs/WORK_PLAN.md` | Updated current slice and next actions. |
| `result_reports/active/683_arc14b-data-mapping-manager-ui-foundation.md` | Added this report. |

## Minor Follow-up Decisions

- `active` is management visibility/eligibility metadata.
- Structural validation runs regardless of active status.
- Inactive attributes and inactive rows are skipped for required/type value
  validation only.
- `row_key` is canonical row identity.
- `key_attribute` describes the import/export/UI header for that identity.
- Row values may omit the key attribute; if present, the trimmed value must
  match `row_key`.

## UI Foundation Scope

- Read-only entity list.
- Read-only selected entity attributes table.
- Read-only selected entity row values table.
- Validation summary.
- Disabled future action metadata for CSV v2 import/export, mapping JSON save,
  and runtime reload.
- Foundation sample provider for UI wiring tests only.

## Verification

- `python3 -m py_compile core/mapping/entity_model.py core/mapping/entity_validation.py apps/train/services/data_mapping_service.py apps/train/controllers/data_mapping_controller.py apps/train/ui/data_mapping_models.py apps/train/ui/data_mapping_view_models.py apps/train/ui/data_mapping_panel.py`: OK
- `python3 -m pytest tests/test_core_mapping_entity_model.py tests/test_core_mapping_entity_validation.py`: OK, 21 passed
- `python3 -m pytest tests/test_apps_train_data_mapping_service.py tests/test_apps_train_data_mapping_controller.py tests/test_apps_train_data_mapping_ui_models.py`: OK, 9 passed
- `python3 -m pytest tests/test_core_mapping_autofill.py tests/test_apps_predict_mapping_backed_dropdown.py`: OK, 14 passed
- `python3 -m pytest tests/test_apps_train_feature_catalog.py`: OK, 21 passed
- `git diff --check`: OK
- `python3 -B tools/check_code_structure.py --verbose`: NG, pre-existing unrelated `apps/calculator/ui/calculator_app.py` raw hex literal error plus existing calculator/standards LOC warnings and stale code-map warning. No changed/new Arc 14B-1 file emitted a structure warning after controller DTO reuse adjustment.
- `python3 -B tools/code_checker/build_reference_map.py --check`: STALE, checked only; regeneration was not part of this slice.

## Manual Check

GUI manual smoke is required for visual acceptance in a real desktop session.
Automated offscreen tests cover panel construction and model data, not final
visual layout quality.

## Excluded Scope

- No full CRUD.
- No CSV v2 import/export.
- No mapping JSON generation/update execution.
- No runtime cascade engine.
- No IDU Size -> Evap Index filter.
- No Predict column/schema generation.
- No `config/predict/schema.csv` or `config/ml/features.csv` changes.
- No Predict UI behavior change.
- No one-hot adapter owner switch.
- No ML training/retraining/model artifact changes.
- No existing fixture/golden expected changes.

## Reference Parity / Reuse

Feature Catalog Manager was checked as the local Train/Admin reference pattern.
Data Mapping reused the same service/controller/table-model/panel direction but
did not copy Feature Catalog editable/save/export complexity because this slice
is read-only.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
```

- `reuse_commonization`: checked Feature Catalog Manager and existing static
  table model patterns. Data Mapping needed local DTO/view-model helpers because
  its entity/attribute/row shape differs from Feature Catalog rows.
- `code_map_check`: checked; reference map is stale, but regeneration was not
  part of this slice.
- Structure warnings: none for changed/new source files. The remaining guard
  error and warnings are pre-existing/unrelated calculator/code-map issues.

Read Ledger:

- `AGENT_TASK_ROUTER.md`: lines 42-190 and 294-350, reason: ML/UI/architecture/report route.
- `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`: lines 1-160, reason: table-shaped UI surface gate.
- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`: lines 1-270, reason: report/commit/push policy.
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`: lines 1-220, reason: new source and read ledger policy.
- `docs/agent_workflows/ML_PREDICTOR_WORKFLOW.md`: lines 1-90, reason: Train/Admin boundary.
- `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`: lines 1-180, reason: service/controller/view boundary.
- `docs/ui_ux/README.md`: lines 1-35, reason: UI/UX document routing.
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`: lines 1-125, reason: table-shaped surface scope.
- `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md`: lines 1-120, reason: Qt table implementation pattern.
- `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`: lines 1-145, reason: status/result surface shape.
- `docs/WORK_PLAN.md`: lines 1-150, reason: current slice and next actions.
- `docs/designs/2026-07-03-arc13-5r-predict-schema-mapping-manager-foundation.md`: lines 1-220, reason: Data Mapping boundary.
- `docs/designs/2026-07-03-arc13-5r-projection-owner-switch.md`: lines 1-115, reason: runtime-owned paths.
- `docs/designs/2026-07-03-arc14a-mapping-entity-master-data-foundation.md`: lines 1-140, reason: core mapping foundation.
- `result_reports/active/682_arc14a-mapping-entity-master-data-foundation.md`: lines 1-135, reason: Arc 14A decisions.
- `docs/designs/README.md`: lines 1-140, reason: design index update.
- `app_train.py`: lines 1-8, reason: root entrypoint boundary.
- `apps/train/app.py`: lines 1-25, reason: Train shell creation boundary.
- `apps/train/ui/shell.py`: lines 1-140, reason: Data Mapping tab connection.
- `apps/train/ui/data_mapping_panel.py`: lines 1-147, reason: current placeholder replacement.
- `apps/train/controllers/feature_catalog_controller.py`: lines 1-160, reason: controller reference pattern.
- `apps/train/application/feature_catalog/models.py`: lines 1-120, reason: DTO reference pattern.
- `apps/train/application/feature_catalog/service.py`: lines 1-220, reason: service reference pattern.
- `apps/train/ui/feature_catalog/table_model.py`: lines 1-190, reason: Qt table model reference pattern.
- `apps/train/ui/models/static_table_model.py`: lines 1-60, reason: read-only table model reference.
- `tests/test_apps_train_feature_catalog.py`: lines 1-220, reason: Train/Admin test style.
- `core/mapping/entity_model.py`: lines 1-125, reason: core model follow-up.
- `core/mapping/entity_validation.py`: lines 1-250, reason: validation follow-up.
- `core/mapping/repository.py`, `core/mapping/update.py`, `core/mapping/autofill.py`, `scripts/update_mapping.py`: targeted owner audit, reason: not touched runtime/converter paths.
- `tests/test_core_mapping_entity_model.py`, `tests/test_core_mapping_entity_validation.py`: targeted test extension, reason: Arc 14A follow-up guards.
- `tests/test_apps_predict_mapping_backed_dropdown.py`: targeted existing runtime regression reference.
- broad read: none.
- repeated read: none.

## Next Action

Arc 14B-2 - Data Mapping runtime mapping repository read adapter. The current
UI foundation still uses a sample provider, so the next slice should display
current mapping data read-only before editable CRUD or CSV v2 import/export.

## Commit / Push Note

Final commit/push result will be reported in terminal output.
