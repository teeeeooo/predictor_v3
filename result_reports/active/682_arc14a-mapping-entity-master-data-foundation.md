# Arc 14A Mapping Entity / Master Data Model Foundation

## Goal

Add a Qt-free core foundation for generic mapping entity definitions, attribute
definitions, row values, catalog lookup, and reusable validation before Data
Mapping Manager UI work.

## Modified Files

| File | Change |
| --- | --- |
| `core/mapping/entity_model.py` | Added mapping entity/attribute/row/catalog DTOs and validation error DTO. |
| `core/mapping/entity_validation.py` | Added small reusable validation boundary. |
| `core/mapping/__init__.py` | Exported model and validation types. |
| `tests/test_core_mapping_entity_model.py` | Added generic model/lookup tests. |
| `tests/test_core_mapping_entity_validation.py` | Added validation guard tests. |
| `docs/designs/2026-07-03-arc14a-mapping-entity-master-data-foundation.md` | Added Arc 14A design record. |
| `docs/designs/README.md` | Indexed the new design record. |
| `docs/WORK_PLAN.md` | Updated current slice and next action. |
| `result_reports/active/682_arc14a-mapping-entity-master-data-foundation.md` | Added this report. |

## Key Decisions

- Mapping Entity / Master Data is a generic core model, not an IDU/ODU-specific
  class boundary.
- Predict Schema Catalog v2 remains the Predict column/schema owner; Mapping
  Entity Model owns mapping row/master data.
- Existing `mapping.json` repository, converter, and runtime autofill/cascade
  paths remain the current compatibility owners and were not changed.
- Canonical CSV v2 direction is entity/attribute/row based; the legacy wide CSV
  fixture is import-compat evidence, not the export contract.

## Validation Scope

Implemented now:

- Duplicate and blank entity keys.
- Duplicate attribute keys within an entity.
- Missing key attribute definitions.
- Unknown row entity references.
- Blank and duplicate row keys within an entity.
- Missing required attribute values.
- Unknown row value attributes.
- Basic `string`, `number`, and `boolean` value validation.

Deferred:

- Range/unit/reference consistency.
- Composite key completeness and rule primitive consistency.
- CSV v2 import/export validation.
- Mapping JSON write policy and runtime reload.

## Verification

- `python3 -m py_compile core/mapping/entity_model.py core/mapping/entity_validation.py`: OK
- `python3 -m pytest tests/test_core_mapping_entity_model.py tests/test_core_mapping_entity_validation.py`: OK, 14 passed
- `python3 -m pytest tests/test_core_mapping_autofill.py tests/test_apps_predict_mapping_backed_dropdown.py`: OK, 14 passed
- `python3 -m pytest tests/test_predict_schema_catalog_v2.py tests/test_predict_schema_catalog_v2_projection.py`: OK, 18 passed
- `git diff --check`: OK
- `python3 -B tools/check_code_structure.py`: NG, pre-existing unrelated `apps/calculator/ui/calculator_app.py` raw hex literal error plus existing LOC/code-map warnings. Arc 14A changed files are not the reported error/warning paths.
- `python3 -B tools/code_checker/build_reference_map.py --check`: STALE, checked only; map regeneration was not part of this slice.

## Excluded Scope

- No Data Mapping Manager UI.
- No runtime cascade engine.
- No mapping JSON generation/update execution.
- No large converter changes.
- No Predict column/schema generation.
- No `config/predict/schema.csv` or `config/ml/features.csv` changes.
- No Predict UI behavior change.
- No one-hot adapter owner switch.
- No ML training/retraining/model artifact changes.
- No existing fixture/golden expected changes.

## Boundary Audit

| Surface | Decision |
| --- | --- |
| `core/mapping/repository.py` | Current `mapping.json` loader owner; not touched. |
| `core/mapping/update.py` | Current Excel/CSV-to-JSON converter owner; not touched. |
| `scripts/update_mapping.py` | Current CLI wrapper owner; not touched. |
| `core/mapping/autofill.py` | Current runtime lookup/cascade owner; not touched. |
| `core/predictor_schema/catalog_v2*.py` | Predict column/schema owner; not touched. |
| legacy wide CSV fixture | Compatibility evidence only; not canonical CSV v2. |

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

- `reuse_commonization`: checked existing `core/mapping` and
  `core/predictor_schema/catalog_v2` owners; no existing generic mapping entity
  model/validator existed to reuse.
- `code_map_check`: checked; reference map is stale, but regeneration was not
  requested and no changed source file adds broad cross-owner structure.

Read Ledger:

- `AGENT_TASK_ROUTER.md`: lines 42-155 and 320-370, reason: route guardrails.
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`: lines 1-220, reason: new source/report gate.
- `docs/agent_workflows/ML_PREDICTOR_WORKFLOW.md`: lines 1-90, reason: ML/Predictor boundary.
- `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`: lines 1-220, reason: core boundary.
- `docs/architecture/project_architecture.md`: lines 1-180, reason: mapping/predict schema owner split.
- `docs/WORK_PLAN.md`: lines 1-140, reason: current slice and next action.
- `docs/designs/README.md`: lines 1-135, reason: design index update.
- `docs/designs/2026-07-03-arc13-5r-predict-schema-mapping-manager-foundation.md`: lines 1-240, reason: mapping entity boundary.
- `docs/designs/2026-07-03-arc13-5r-predict-schema-v2-field-spec-confirmation.md`: lines 1-220, reason: Predict Schema v2 field split.
- `docs/designs/2026-07-03-arc13-5r-readonly-schema-v2-projection-parity.md`: lines 1-90, reason: runtime owner not switched.
- `docs/designs/2026-07-03-arc13-5r-projection-owner-switch.md`: lines 1-115, reason: remaining Arc 14A gap.
- `result_reports/active/680_arc13-5r-projection-owner-switch.md`: lines 1-95, reason: prior owner switch report.
- `result_reports/active/681_arc13-5r-schema-v2-followup-guards.md`: lines 1-45, reason: follow-up guard status.
- `core/mapping/repository.py`: lines 1-25, reason: current loader owner.
- `core/mapping/update.py`: lines 1-105, reason: current converter owner.
- `core/mapping/autofill.py`: lines 1-145, reason: current runtime cascade owner.
- `scripts/update_mapping.py`: lines 1-35, reason: current CLI owner.
- `tests/fixtures/mapping/mapping_tables_legacy_wide.csv`: lines 1-23, reason: legacy fixture shape.
- `tests/test_core_mapping_autofill.py`: lines 1-70, reason: existing runtime behavior guard.
- `tests/test_apps_predict_mapping_backed_dropdown.py`: lines 1-245, reason: existing dropdown/runtime integration guard.
- `core/predictor_schema/catalog_v2.py`: lines 1-205, reason: Predict Schema v2 owner boundary.
- `core/predictor_schema/catalog_v2_projection.py`: lines 1-100, reason: projection compatibility boundary.
- `config/predict/schema.csv`: lines 1-35, reason: Predict schema mapping reference fields.
- broad read: none.
- repeated read: none.

## Next Action

Arc 14B - Data Mapping Manager UI, because the core model and validation
foundation are stable enough for UI/controller work. A narrow Arc 14A follow-up
for CSV v2 loader/exporter is only needed if Arc 14B must start with file
adapter implementation before screens.

## Commit / Push Note

Final commit/push result will be reported in terminal output.
