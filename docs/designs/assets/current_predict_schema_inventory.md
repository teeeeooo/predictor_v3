# Current Predict Schema Inventory

## Purpose

이 문서는 Arc 13.5R-1 audit 산출물이다. 현재 Predict table schema가 어떤 파일에서 생성되고 어떤 runtime adapter가 어떤 metadata에 의존하는지 inventory로 남겨, Predict Schema Catalog v2 field/spec 확정의 입력 자료로 사용한다.

이 문서는 새 schema implementation이 아니다. `config/predict/schema.csv`를 만들지 않고, current main branch의 owner split과 v2 migration target만 기록한다.

## Source Files Audited

| Area | Files |
| --- | --- |
| Active planning/design docs | `ACTIVE_DOCUMENTS.md`, `docs/WORK_PLAN.md`, `docs/designs/2026-07-03-arc13-5r-predict-schema-mapping-manager-foundation.md`, `project_brief.md` relevant Arc 14/15 range |
| Feature catalog | `config/ml/features.csv`, `core/ml/feature_catalog.py`, `core/ml/feature_catalog_projection.py`, `core/ml/feature_catalog_validation.py` |
| Core predict schema | `core/predictor_schema/columns.py`, `core/predictor_schema/ui_columns.py` |
| Predict schema adapters | `apps/predict/schema/column_schema_adapter.py`, `apps/predict/schema/case_table_schema_adapter.py` |
| Predict UI/runtime usage | `apps/predict/ui/tables/case_table_model.py`, `apps/predict/ui/workspace.py`, `apps/predict/controllers/input_edit_controller.py` |
| Mapping/autofill and ML input | `core/mapping/autofill.py`, `apps/predict/adapters/dropdown_option_adapter.py`, `apps/predict/adapters/row_to_ml_input_adapter.py` |
| Test evidence | `tests/test_ml_feature_catalog.py`, `tests/test_apps_predict_schema_adapter.py`, `tests/test_apps_predict_case_table_schema_adapter.py`, `tests/test_apps_predict_mapping_backed_dropdown.py`, `tests/test_core_mapping_autofill.py`, `tests/test_apps_predict_prediction_adapters.py`, `tests/test_apps_train_feature_catalog.py` |

## Current Schema Assembly Flow

```text
config/ml/features.csv
-> core.ml.feature_catalog.load_feature_catalog()
-> core.ml.feature_catalog_validation.validate_feature_catalog()
-> core.ml.feature_catalog_projection.predictor_columns_projection()
-> core.predictor_schema.ui_columns inserts dropdown-only input and rule result columns
-> core.predictor_schema.columns.COLUMNS / INPUT_COLS / AUTO_COLS / RESULT_COLS / DROPDOWN_COLS
-> apps.predict.schema.column_schema_adapter.PredictColumn
-> apps.predict.schema.case_table_schema_adapter.UnifiedCaseColumn
-> apps.predict.ui.tables.case_table_model.CaseTableModel
-> apps.predict.ui.workspace.PredictWorkspace
```

Current assembly details:

| Step | Current behavior |
| --- | --- |
| `config/ml/features.csv` | Stores ML feature/target/one-hot rows with `role`, `ui_key`, `label`, `source`, `mapping_key`, `one_hot_group`, `active`, and notes. |
| `core.ml.feature_catalog` | Loads canonical CSV rows into `FeatureCatalogRow`; exposes active rows, predictor rows, training headers, targets, and one-hot groups. |
| `core.ml.feature_catalog_projection` | Projects active `input`, `auto`, and `result` rows into predictor column metadata. `one_hot` rows do not become direct table columns. |
| `core.predictor_schema.ui_columns` | Hard-codes dropdown-only input columns and rule result columns, then defines insertion points. |
| `core.predictor_schema.columns` | Combines Feature Catalog projection with hard-coded UI-only columns into `COLUMNS`; derives key lists and `DROPDOWN_TARGET = {k: k}`. |
| `column_schema_adapter` | Converts core dict metadata into Qt-free `PredictColumn`; preserves `mapping`, `dropdown_target`, `ml_feature`, `ml_target`, `source`, and `mapping_key`. |
| `case_table_schema_adapter` | Converts `PredictColumn` into unified table columns and appends virtual status/message columns. It maps group to row storage source: input, autofill, result, or status. |
| `case_table_model` | Uses `UnifiedCaseColumn` to route cell values to `CaseRow.input_values`, `autofill_values`, `result_values`, or status/message. |
| `workspace` | Builds the model, dropdown adapter, and dropdown delegate. It asks row-specific options from `InputEditController` and base options from `DropdownOptionAdapter`. |

## Owner Split Summary

| Current owner | Owns now | v2 direction |
| --- | --- | --- |
| Feature Catalog | ML feature / target / one-hot rows; projected input/auto/result columns with `ml_feature`, `ml_target`, `source`, and `mapping_key`. | Keep as ML projection input or absorb as a Predict Schema Manager section. ML contract fields remain important but should not be the only Predict schema owner. |
| `core/predictor_schema/ui_columns.py` | Dropdown-only input columns and rule result columns hard-coded outside Feature Catalog. | Move to Predict Schema Catalog v2 rows with editor, value source, mapping entity, and rule metadata. |
| `core/predictor_schema/columns.py` | Merges catalog projection and UI-only columns; derives `INPUT_COLS`, `AUTO_COLS`, `RESULT_COLS`, `DROPDOWN_COLS`, and `DROPDOWN_TARGET`. | Replace ad hoc assembly with projection from a single Predict Schema Catalog v2 owner after parity. |
| `apps.predict.schema.*_adapter` | Qt-free DTO projection for Predict UI/table. | Continue as adapter layer, but preserve v2 fields needed by mapping/rule/ML projections. |
| `core.mapping.autofill` | Simple lookup based on `source` / `mapping_key` plus hard-coded ODU cascade. | Move toward a rule primitive engine using `lookup`, `filter`, `clear`, and `composite_lookup`. |
| `dropdown_option_adapter` | Base dropdown options from fallback constants or mapping sections keyed by dropdown target. | Use schema-provided `mapping_entity`, fallback policy, and row-specific filter results. |
| `row_to_ml_input_adapter` | Numeric ML row input projection from `ml_feature`; hard-coded one-hot input group map. | Use schema projection fields such as `model_input_enabled`, `ml_name`, and `one_hot_group`. |

## Current Column Inventory

The current core `COLUMNS` order has 28 columns. The unified case table appends virtual `status` and `message` columns after these.

| # | column_key | label | current_owner | current_group | current_editor | current_mapping | current_source | current_mapping_key | ml_feature | ml_target | v2_role | v2_editor | v2_value_source | v2_mapping_entity | v2_mapping_attribute | v2_trigger_column | v2_rule_id | notes |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `cooling_capa` | 냉방능력 | Feature Catalog | input | text/numeric input |  |  |  | Cooling Capa |  | input | numeric/manual | manual |  |  |  |  | Required by RowToMlInputAdapter; zero-fill policy is catalog-owned. |
| 2 | `heating_capa` | 난방능력 | Feature Catalog | input | text/numeric input |  |  |  | Heating Capa |  | input | numeric/manual | manual |  |  |  |  | Feature Catalog input projected before UI dropdown inserts. |
| 3 | `idu` | 실내기 | `ui_columns.py` | input | dropdown | idu |  |  |  |  | input | dropdown | manual | idu |  |  |  | Dropdown-only input; no direct ML feature. |
| 4 | `evap_index` | 증발기 | `ui_columns.py` | input | dropdown | evap_index |  |  |  |  | input | dropdown | manual | evap_index |  |  |  | Dropdown-only input; currently not filtered by IDU Size. |
| 5 | `odu` | 실외기 | `ui_columns.py` | input | dropdown | odu |  |  |  |  | input | dropdown | manual | odu |  |  | odu_cascade | Triggers simple ODU lookup plus hard-coded dependent clear/options. |
| 6 | `fin_type` | FIN종류 | `ui_columns.py` | input | dropdown | fin_type |  |  |  |  | input | dropdown | rule_options | odu_cascade | Available_Fins | odu | odu_cond_filter | Base lookup assumes section `fin_type`; row-specific options come from ODU cascade. |
| 7 | `pi` | PI | `ui_columns.py` | input | dropdown | pi |  |  |  |  | input | dropdown | rule_options | odu_cascade | Available_Pis | odu | odu_cond_filter | Same row-specific option rule as `fin_type`. |
| 8 | `row` | ROW | `ui_columns.py` | input | dropdown | row |  |  |  |  | input | dropdown | rule_options | odu_cascade | Available_Rows | odu | odu_cond_filter | Column key `row` overlaps with row concept; v2 may need careful naming. |
| 9 | `compressor` | 압축기 | `ui_columns.py` | input | dropdown | compressor |  |  |  |  | input | dropdown | manual | compressor |  |  |  | Dropdown-only input; triggers compressor lookup for auto columns. |
| 10 | `ref_type` | 냉매종류 | `ui_columns.py` | input | dropdown | ref_type |  |  |  |  | input | dropdown | one_hot | ref_type |  |  | one_hot_refrigerant | Dropdown has fallback options; one-hot group is hard-coded in ML adapter. |
| 11 | `exp_type` | 팽창장치 | `ui_columns.py` | input | dropdown | exp_type |  |  |  |  | input | dropdown | one_hot | exp_type |  |  | one_hot_expansion_device | Dropdown has fallback options; one-hot group is hard-coded in ML adapter. |
| 12 | `id_volume` | ID Volume | Feature Catalog | auto | readonly/autofill |  | idu | ID Volume | ID Volume |  | auto | readonly | mapping_lookup | idu | ID Volume | idu |  | Current `source` means trigger column and mapping section. |
| 13 | `evap_area` | Evap Area | Feature Catalog | auto | readonly/autofill |  | evap_index | Evap Area | Evap Area |  | auto | readonly | mapping_lookup | evap_index | Evap Area | evap_index |  | No IDU Size filter currently protects compatible Evap choices. |
| 14 | `evap_volume` | Evap Volume | Feature Catalog | auto | readonly/autofill |  | evap_index | Evap Volume | Evap Volume |  | auto | readonly | mapping_lookup | evap_index | Evap Volume | evap_index |  | Simple lookup from selected `evap_index`. |
| 15 | `od_volume` | OD Volume | Feature Catalog | auto | readonly/autofill |  | odu | OD Volume | OD Volume |  | auto | readonly | mapping_lookup | odu | OD Volume | odu |  | Simple lookup when `odu` changes. |
| 16 | `cond_area` | Cond Area | Feature Catalog | auto | readonly/autofill |  | odu | Cond Area | Cond Area |  | auto | readonly | composite_lookup | cond_specs | Cond Area | fin_type/pi/row/odu | cond_specs_lookup | Current simple lookup metadata says `source=odu`, but runtime final value is hard-coded `cond_specs` composite lookup. |
| 17 | `cond_volume` | Cond Volume | Feature Catalog | auto | readonly/autofill |  | odu | Cond Volume | Cond Volume |  | auto | readonly | composite_lookup | cond_specs | Cond Volume | fin_type/pi/row/odu | cond_specs_lookup | Same mismatch as `cond_area`. |
| 18 | `comp_eer` | Comp EER | Feature Catalog | auto | readonly/autofill |  | compressor | Comp EER | Comp EER |  | auto | readonly | mapping_lookup | compressor | Comp EER | compressor |  | Width override applied in `columns.py`. |
| 19 | `comp_cc` | Comp cc | Feature Catalog | auto | readonly/autofill |  | compressor | Comp cc | Comp cc |  | auto | readonly | mapping_lookup | compressor | Comp cc | compressor |  | Width override applied in `columns.py`. |
| 20 | `cooling_power` | 냉방 소비전력 | Feature Catalog | result | readonly |  |  |  |  | Cooling Power | result | readonly | result |  |  |  |  | ML target result column. |
| 21 | `eer` | EER (rule) | `ui_columns.py` | result | readonly |  |  |  |  |  | result | readonly | formula/result |  |  |  | rule_result | Rule result column; not an ML target. |
| 22 | `cspf` | CSPF | `ui_columns.py` | result | readonly |  |  |  |  |  | result | readonly | formula/result |  |  |  | rule_result | Rule result column; not an ML target. |
| 23 | `heating_power` | 난방 소비전력 | Feature Catalog | result | readonly |  |  |  |  | Heating Power | result | readonly | result |  |  |  |  | ML target result column. |
| 24 | `cop` | COP (rule) | `ui_columns.py` | result | readonly |  |  |  |  |  | result | readonly | formula/result |  |  |  | rule_result | Rule result column; not an ML target. |
| 25 | `hspf2` | HSPF2 | `ui_columns.py` | result | readonly |  |  |  |  |  | result | readonly | formula/result |  |  |  | rule_result | Rule result column; not an ML target. |
| 26 | `ref_qty` | 냉매량 | Feature Catalog | result | readonly |  |  |  |  | Ref Qty | result | readonly | result |  |  |  |  | ML target result column. |
| 27 | `cooling_hz` | 냉방 주파수 | Feature Catalog | result | readonly |  |  |  |  | Cooling Hz | result | readonly | result |  |  |  |  | ML target result column. |
| 28 | `heating_hz` | 난방 주파수 | Feature Catalog | result | readonly |  |  |  |  | Heating Hz | result | readonly | result |  |  |  |  | ML target result column. |
| 29 | `status` | Status | case table adapter | status | readonly |  | result_status | status |  |  | status | readonly | status |  |  |  |  | App-side virtual column, not in core `COLUMNS`. |
| 30 | `message` | Warning / Error | case table adapter | status | readonly |  | result_message | message |  |  | status | readonly | status |  |  |  |  | App-side virtual column, not in core `COLUMNS`. |

## v2 Field Mapping Draft

| v2 field | Current source candidate | Gap / note |
| --- | --- | --- |
| `display_order` | `features.csv` `order` for catalog rows; insertion order in `ui_columns.py`; status append order in case table adapter | No single owner for all columns. |
| `column_key` | `FeatureCatalogRow.ui_key` or hard-coded `key`; virtual status metadata key | One-hot rows have no direct UI column key today. |
| `label` | `FeatureCatalogRow.label`, hard-coded `header`, or status header | Existing labels mix Korean UI labels and English technical labels. |
| `role` | `group` from projected/hard-coded metadata; status group added by case table adapter | Current catalog roles include `one_hot`, `derived`, `hidden`, but only input/auto/result become table columns. |
| `editor` | `type=dropdown`, group/editability, readonly flags | Numeric/text editor is inferred rather than explicit. |
| `data_type` | Not represented; numeric validation inferred from `ml_feature` conversion | Needs v2 field. |
| `visible` | Not represented; all current core columns are visible | Needs v2 field for future hide/show. |
| `required` | Partly in adapter logic (`cooling_capa` required), validation, or workflow docs | Needs v2 field or rule. |
| `readonly` | `readonly` metadata or group-derived adapter behavior | Auto columns become read-only through group mapping, not explicit catalog data. |
| `value_source` | Inferred from role, `ml_feature`, `source`, `mapping_key`, hard-coded rule columns, one-hot adapter map | Needs explicit `manual`, `mapping_lookup`, `formula`, `result`, `one_hot`, `status`. |
| `mapping_entity` | `mapping`, `dropdown_target`, or `source` depending on context | Current `source` overloads trigger column and mapping entity. |
| `mapping_attribute` | `mapping_key` for auto rows; hard-coded cond spec attribute names | Rule result and one-hot do not use this field. |
| `trigger_column` | Usually `source` for simple lookup; hard-coded changed key for ODU cascade | Needs explicit field separate from mapping entity. |
| `rule_id` | Not represented; implicit in `core.mapping.autofill` branches and rule result columns | Needs v2 rule reference. |
| `model_input_enabled` | Implied by `ml_feature` or one-hot adapter group | Needs explicit boolean to distinguish UI-only, mapping-ready, and model-active. |
| `ml_name` | `ml_feature`, `ml_target`, or one-hot catalog `ml_name` | Input and target paths use different metadata names today. |
| `one_hot_group` | Feature Catalog rows and `_ONE_HOT_INPUT_GROUPS` adapter map | The selected input column to group relationship is hard-coded. |
| `active` | Feature Catalog active rows | UI-only and virtual columns have no active flag. |
| `notes` | Feature Catalog notes | UI-only columns and rule result columns have no notes field. |

## Cascade / Autofill Inventory

| Current behavior | Owner | Current trigger | Current output | v2 primitive direction |
| --- | --- | --- | --- | --- |
| Simple mapping lookup | `core.mapping.autofill._simple_mapping_updates` | `changed_key` maps through `DROPDOWN_TARGET`; auto columns match `source == changed_key` | Fills auto columns from `mapping_data[section][selected][mapping_key]` or clears them if missing | `lookup` with explicit `mapping_entity`, `mapping_attribute`, `trigger_column`. |
| ODU dependent clear | `build_autofill_updates` hard-coded `changed_key == "odu"` branch | `odu` | Clears `fin_type`, `pi`, `row`, `cond_area`, `cond_volume` | `clear` rule with dependent targets. |
| ODU dropdown options | `_odu_dropdown_options` | `odu` | Row-specific options for `fin_type`, `pi`, `row` from `odu_cascade` fields | `filter` rule with parent lookup attributes. |
| Cond spec composite lookup | `_cond_spec_updates` | `fin_type`, `pi`, `row`; also after ODU path once values exist | `cond_area`, `cond_volume` from `mapping_data["cond_specs"][f"{odu} {fin} {pi} {row}"]` | `composite_lookup` with explicit key parts and target attributes. |
| Row-specific dropdown options | `InputEditController` and `DropdownOptionAdapter` | Result dropdown options from autofill are stored by case id | Dropdown delegate uses row-specific options before base options | Keep row-specific option channel, but source it from rule primitive output. |
| IDU Size -> Evap Index filter | Not implemented in current runtime | TBD | None | Needs `lookup` plus `filter` primitive; current `evap_index` base options are all mapping keys. |

Current gaps in cascade/autofill:

- There is no generic primitive contract for `lookup`, `filter`, `clear`, or `composite_lookup`.
- `DROPDOWN_TARGET = {k: k}` assumes dropdown column key equals mapping section.
- `source` currently means both trigger column and mapping section for simple auto rows.
- `cond_area` and `cond_volume` metadata suggest simple `source=odu` / `mapping_key=Cond Area|Cond Volume`, but runtime final value is driven by `cond_specs` composite lookup.
- IDU Size filtering for Evap Index is absent.

## One-hot / ML Input Inventory

| Area | Current behavior | v2 direction |
| --- | --- | --- |
| Numeric ML input | `RowToMlInputAdapter` iterates input/auto schema columns and sends only columns with `ml_feature`; values are converted to float. | Use `model_input_enabled=true`, `ml_name`, and `data_type` instead of only presence of `ml_feature`. |
| Required capacity | `cooling_capa` is explicitly required in adapter logic. | Represent required fields in schema/rule metadata. |
| One-hot groups | Feature Catalog owns one-hot rows and groups: `refrigerant` -> `R410A`, `R32`, `R290`; `expansion_device` -> `EEV`, `Capi`. | Preserve catalog one-hot ML feature list or absorb it into schema manager's ML section. |
| One-hot input selector | `_ONE_HOT_INPUT_GROUPS = {"ref_type": "refrigerant", "exp_type": "expansion_device"}` is hard-coded in `RowToMlInputAdapter`. | Express the selector as schema rows with `column_key`, `value_source=one_hot`, `one_hot_group`, and `model_input_enabled=true`. |
| Unknown one-hot selection | Adapter zeroes group features, sets matching selected feature to `1.0`, and warns on unsupported option. | Preserve behavior through schema-driven one-hot projection and validation. |

## Gaps

- Predict UI 전체 column owner가 없다. Feature Catalog, `ui_columns.py`, and case table virtual metadata each own part of the table.
- `ui_columns.py` hard-code blocks extension of new dropdown-only inputs and rule result columns without code edits.
- `source` overloads trigger column and mapping entity meaning.
- `DROPDOWN_TARGET = {k: k}` assumes dropdown key equals mapping entity/section.
- ODU cascade is hard-coded rather than rule primitive-driven.
- One-hot input group mapping is hard-coded in `RowToMlInputAdapter`.
- Current adapters preserve only current metadata; v2 fields such as `value_source`, `data_type`, `required`, `model_input_enabled`, `rule_id`, and explicit `trigger_column` do not exist.
- `cond_area` / `cond_volume` current metadata and runtime lookup path are not aligned.
- IDU Size -> Evap Index filtering is not represented.
- Live schema reload is currently too broad for an initial slice because schema changes affect row data migration, table model rebuild, dropdown options, mapping reload, cascade rules, and ML input projection. Initial restart-required remains appropriate.
- Data Mapping Manager implementation needs v2 schema contract first; otherwise it may hard-code the current mapping tables instead of managing generic mapping entities and attributes.

## Recommendations

| Recommended slice | Scope |
| --- | --- |
| Arc 13.5R-2 | Predict Schema Catalog v2 field/spec confirmation after current schema inventory. |
| Arc 13.5R-3 | Read-only `schema.csv` draft/projection parity prototype; no runtime owner switch. |
| Arc 13.5R-4 | Projection owner switch only after parity tests prove current `COLUMNS`, adapters, dropdowns, autofill, and ML input behavior are preserved. |
| Arc 14A | Mapping Entity / Master Data Model Foundation. |
| Arc 14B | Data Mapping Manager UI. |
| Arc 14C | Runtime Cascade Integration. |

## Next Action

Use this inventory as Arc 13.5R-2 input. The next design slice should confirm the Predict Schema Catalog v2 fields, define how current Feature Catalog rows relate to schema rows, decide how one-hot selector rows are represented, and write the initial rule primitive spec for `lookup`, `filter`, `clear`, and `composite_lookup`.
