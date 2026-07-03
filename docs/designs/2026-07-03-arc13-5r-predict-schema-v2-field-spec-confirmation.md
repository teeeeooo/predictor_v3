# Arc 13.5R-2 - Predict Schema Catalog v2 Field Spec Confirmation

Status: active reference

## Purpose

이 문서는 Arc 13.5R-1 current inventory를 바탕으로 Predict Schema Catalog v2의 초기 field/spec contract를 확정한다. 목적은 Arc 13.5R-3에서 read-only `schema.csv` draft/projection parity prototype을 만들 수 있게, 현재 Feature Catalog, `ui_columns.py`, case-table virtual columns, mapping/autofill, one-hot ML input을 v2 schema에서 어떻게 표현할지 선명하게 정리하는 것이다.

Predict Schema Catalog v2의 core boundary는 IDU-Evap / ODU-Cond 같은 HVAC-specific template이 아니라 generic mapping entity / mapping attribute / cascade rule expression이다. IDU-Evap과 ODU-Cond는 representative examples 또는 default presets로만 다룬다.

## Inputs

| Input | Role |
| --- | --- |
| `docs/designs/2026-07-03-arc13-5r-predict-schema-mapping-manager-foundation.md` | Generic mapping entity / attribute / rule boundary decision. |
| `docs/designs/assets/current_predict_schema_inventory.md` | Current Predict schema owner split, current columns, v2 draft mapping, gaps. |
| `config/ml/features.csv` | Current ML feature/target/one-hot catalog source. |
| `core/ml/feature_catalog*.py` | Feature Catalog load, validation, projection, one-hot group behavior. |
| `core/predictor_schema/columns.py` and `ui_columns.py` | Current `COLUMNS` assembly and hard-coded UI-only columns. |
| `apps/predict/schema/*_adapter.py` | Current Qt-free DTO projection and virtual status/message columns. |
| `core/mapping/autofill.py` | Current lookup/cascade behavior that v2 rules must model. |
| `apps/predict/adapters/row_to_ml_input_adapter.py` | Current numeric ML input and hard-coded one-hot selector behavior. |

## Non-goals

- Do not implement `config/predict/schema.csv`.
- Do not change source code, runtime behavior, tests, fixtures, or ML artifacts.
- Do not make Data Mapping Manager create Predict columns.
- Do not define the Arc 14A/14B canonical mapping entity CSV/import format.
- Do not implement live schema reload.
- Do not turn v2 into a free-form DSL. The initial contract is a bounded field set plus named primitive rules.

## Confirmed v2 Field Set

The initial Predict Schema Catalog v2 row contract is:

| Field | Required | Definition |
| --- | --- | --- |
| `display_order` | required | Integer ordering for visible and projected Predict columns. |
| `column_key` | required | Stable Predict row/table key. It must be unique among active schema rows and must not be assumed to equal `mapping_entity`. |
| `label` | required for visible rows | User-facing table header or label. |
| `role` | required | Column role in Predict UI/projection. Initial values are defined below. |
| `editor` | required | Editing surface for user-facing cells. |
| `data_type` | required | Value type expected by UI validation and downstream projection. |
| `visible` | required | Whether the column is part of the default visible Predict table. |
| `required` | required | Whether blank value is invalid for the workflow before prediction or rule application. |
| `readonly` | required | Whether the user can edit this column directly. |
| `value_source` | required | How the value is produced. |
| `mapping_entity` | optional | Mapping entity/table used by dropdown option or lookup. |
| `mapping_attribute` | optional | Attribute read from the mapping entity for a target value. |
| `trigger_column` | optional | Column whose selected value triggers lookup/filter/clear behavior. |
| `rule_id` | optional | Named rule reference for non-trivial lookup/filter/clear/composite behavior. |
| `model_input_enabled` | required | Whether this schema row contributes to ML model input projection. |
| `ml_name` | optional | ML feature/target name. Required when `model_input_enabled=true` for numeric/model feature rows or when `role=result` maps to an ML target. |
| `one_hot_group` | optional | One-hot group name used for selector rows or one-hot feature rows. |
| `active` | required | Whether this schema row participates in projection. |
| `notes` | optional | Human-readable operational notes. |

Optional helper fields are allowed only as preset/group helpers, not core boundary:

| Helper | Status |
| --- | --- |
| `template_id` | Optional preset helper for repeated column groups. |
| `slot_id` | Optional preset instance helper. |
| `cascade_role` | Optional human-readable helper; runtime applies `rule_id` and primitive specs. |

## Allowed Initial Enum Values

| Field | Initial allowed values |
| --- | --- |
| `role` | `input`, `auto`, `helper`, `result`, `status`, `one_hot_feature`, `hidden` |
| `editor` | `text`, `number`, `dropdown`, `readonly`, `status` |
| `data_type` | `string`, `number`, `boolean`, `status` |
| `value_source` | `manual`, `mapping_lookup`, `formula`, `result`, `one_hot`, `status`, `rule_options` |

Enum notes:

- Current Feature Catalog roles are not identical to v2 roles. Existing catalog `one_hot` rows become v2 `one_hot_feature` rows, while selector columns such as `ref_type` / `exp_type` are v2 `role=input`, `editor=dropdown`, `value_source=one_hot`.
- `helper` is reserved for future non-model-visible support columns. It is not required for the current 28 core columns.
- `status` is for app-side virtual status/message rows.

## Field Rules

| Rule | Requirement |
| --- | --- |
| Identity | Active `column_key` values must be unique. |
| Ordering | Active projected rows sort by `display_order`; adapters may append virtual/status rows only when those rows are represented in v2 or adapter-local virtual metadata. |
| Mapping separation | `mapping_entity` and `trigger_column` are separate fields. Do not reuse legacy `source` as both meanings. |
| Column/entity separation | `column_key` and `mapping_entity` may match, but this is never a contract. |
| Model projection | `model_input_enabled=true` requires enough metadata for ML projection: `ml_name` for numeric feature/target rows or `one_hot_group` for selector rows. |
| Lookup | `value_source=mapping_lookup` requires `mapping_entity`, `mapping_attribute`, and `trigger_column` unless `rule_id` owns the full lookup contract. |
| Rule reference | `rule_id` must point to a known primitive rule in the schema/rule companion spec for non-trivial cascade behavior. |
| Readonly | `role=auto`, `role=result`, and `role=status` are readonly by default. |
| Active | Inactive rows do not project to runtime schema, dropdowns, rule targets, or ML input. |

## Current-to-v2 Mapping Summary

| Current owner | Current shape | v2 representation |
| --- | --- | --- |
| Feature Catalog `input` rows | `ui_key`, `label`, `ml_name`, `role=input` | `role=input`, `editor=number` unless explicitly string, `value_source=manual`, `model_input_enabled=true`, `ml_name=<catalog ml_name>`. |
| Feature Catalog `auto` rows | `source`, `mapping_key`, `ml_name` | `role=auto`, `readonly=true`, `value_source=mapping_lookup`, `mapping_entity=<former source if same as entity>`, `mapping_attribute=<mapping_key>`, `trigger_column=<explicit trigger>`, `model_input_enabled=true`. |
| Feature Catalog `result` rows | `ui_key`, `label`, `ml_target` projection | `role=result`, `readonly=true`, `value_source=result`, `ml_name=<target name>`, `model_input_enabled=false` for input projection. |
| Feature Catalog `one_hot` rows | no direct table column; group feature names | `role=one_hot_feature`, `visible=false`, `value_source=one_hot`, `ml_name=<one-hot feature>`, `one_hot_group=<group>`, `model_input_enabled=true`. |
| `ui_columns.py` dropdown inputs | hard-coded `key`, `header`, `mapping`, `type=dropdown` | `role=input`, `editor=dropdown`, `value_source=manual` or `one_hot` or `rule_options`, explicit `mapping_entity` when options come from mapping. |
| `ui_columns.py` rule result columns | hard-coded read-only result columns without `ml_target` | `role=result`, `editor=readonly`, `value_source=formula`, `readonly=true`, `model_input_enabled=false`, `rule_id` if a rule owner exists. |
| Case table virtual status/message | adapter-local virtual columns | `role=status`, `editor=status`, `value_source=status`, `visible=true`, `readonly=true`, `model_input_enabled=false`; may remain adapter-local in Arc 13.5R-3 if parity scope requires it. |

## Feature Catalog Relationship

Feature Catalog remains the current ML contract source for `ml_name`, target names, one-hot feature names, zero-fill policy, and model fingerprint behavior. Predict Schema Catalog v2 does not delete this responsibility in Arc 13.5R-3.

Initial relationship:

- v2 schema rows may be generated from Feature Catalog rows for parity.
- v2 rows must preserve ML feature and target names through `ml_name`.
- Feature Catalog `source` maps only as legacy evidence. v2 must split it into `mapping_entity` and `trigger_column`.
- Feature Catalog `one_hot_group` remains the source of one-hot feature grouping until a later owner switch is explicitly designed.

## UI-only Dropdown Relationship

Current dropdown-only columns from `ui_columns.py` become first-class v2 schema rows.

| Current column | v2 direction |
| --- | --- |
| `idu` | `role=input`, `editor=dropdown`, `value_source=manual`, `mapping_entity=idu`, `model_input_enabled=false`. |
| `evap_index` | `role=input`, `editor=dropdown`, `value_source=manual`, `mapping_entity=evap_index`; future filter rule can constrain options by IDU Size. |
| `odu` | `role=input`, `editor=dropdown`, `value_source=manual`, `mapping_entity=odu`, `rule_id=odu_cond_clear_filter` or equivalent. |
| `fin_type`, `pi`, `row` | `role=input`, `editor=dropdown`, `value_source=rule_options`, options produced by filter rule. |
| `compressor` | `role=input`, `editor=dropdown`, `value_source=manual`, `mapping_entity=compressor`. |
| `ref_type`, `exp_type` | `role=input`, `editor=dropdown`, `value_source=one_hot`, `one_hot_group=<group>`. |

## Case-table Virtual Status/Message Columns

The unified case table currently appends `status` and `message` outside core `COLUMNS`. In v2, they are represented as status rows so the full visible table can be described by one schema contract.

| column_key | role | value_source | notes |
| --- | --- | --- | --- |
| `status` | `status` | `status` | Maps to result status display; not core ML schema. |
| `message` | `status` | `status` | Maps to warning/error display; not core ML schema. |

Arc 13.5R-3 may keep these adapter-local if the prototype explicitly documents that status rows are outside read-only `schema.csv` parity scope. The target contract is still v2-representable status rows.

## One-hot Selector Representation

One-hot selector columns are not cascade primitives. They are ML input projection concerns.

| Selector | v2 representation |
| --- | --- |
| `ref_type` | `role=input`, `editor=dropdown`, `value_source=one_hot`, `one_hot_group=refrigerant`, `model_input_enabled=true`, `ml_name` blank or selector-local. |
| `exp_type` | `role=input`, `editor=dropdown`, `value_source=one_hot`, `one_hot_group=expansion_device`, `model_input_enabled=true`, `ml_name` blank or selector-local. |
| `R410A`, `R32`, `R290`, `EEV`, `Capi` | `role=one_hot_feature`, `visible=false`, `value_source=one_hot`, `one_hot_group=<group>`, `model_input_enabled=true`, `ml_name=<feature name>`. |

The selector row owns the selected raw option. The one-hot feature rows own emitted ML feature names. RowToMlInputAdapter should eventually derive selector-to-group mapping from v2 rather than `_ONE_HOT_INPUT_GROUPS`.

## Mapping Lookup Representation

Simple mapping-backed autofill rows use this shape:

| Field | Requirement |
| --- | --- |
| `role` | `auto` |
| `editor` | `readonly` |
| `value_source` | `mapping_lookup` |
| `mapping_entity` | Entity to read, such as `compressor` or `evap_index`. |
| `mapping_attribute` | Attribute to copy, such as `Comp EER` or `Evap Area`. |
| `trigger_column` | Column whose selected value is the lookup key, such as `compressor` or `evap_index`. |
| `rule_id` | Empty for direct simple lookup; set when rule owns selection/filter/composite behavior. |

Examples:

| Target column | mapping_entity | mapping_attribute | trigger_column |
| --- | --- | --- | --- |
| `comp_eer` | `compressor` | `Comp EER` | `compressor` |
| `comp_cc` | `compressor` | `Comp cc` | `compressor` |
| `evap_area` | `evap_index` | `Evap Area` | `evap_index` |
| `evap_volume` | `evap_index` | `Evap Volume` | `evap_index` |

## Rule Primitive Representation

Rules are referenced by `rule_id` from schema rows and defined in a bounded rule companion representation. Arc 13.5R-3 only needs read-only draft/projection parity, but it must preserve these fields so Arc 14C can implement runtime behavior without hard-coding new paths.

### lookup

| Item | Spec |
| --- | --- |
| Purpose | Copy one or more attributes from a mapping entity row selected by a trigger column. |
| Required schema fields | Target row: `value_source=mapping_lookup`, `mapping_entity`, `mapping_attribute`, `trigger_column`. |
| Optional schema/rule fields | `rule_id`, default-on-missing policy, clear-on-missing target list. |
| Current behavior example | `compressor` selection fills `comp_eer` and `comp_cc`; `evap_index` selection fills `evap_area` and `evap_volume`. |
| Future implementation note | Multiple target rows can share one trigger and entity; engine should collect affected targets from schema. |
| Out of scope | Cross-entity joins, expression evaluation, fuzzy matching, or creating mapping rows. |

### filter

| Item | Spec |
| --- | --- |
| Purpose | Restrict target dropdown options using a parent selected value or a parent lookup attribute. |
| Required schema fields | Target dropdown row with `editor=dropdown`; `rule_id` referencing a filter rule; rule defines parent/trigger column and target option entity. |
| Optional schema/rule fields | Parent attribute name, fallback options, clear target on parent change, empty option behavior. |
| Current behavior example | Current ODU cascade filters `fin_type`, `pi`, and `row` from `odu_cascade` available lists. |
| Required future example | `idu` lookup provides `id_size`; `evap_index` options are filtered where Evap `Size == id_size`. |
| Future implementation note | Filter result should flow through the existing row-specific dropdown option channel. |
| Out of scope | Arbitrary SQL-like predicates or UI-specific delegate logic. |

### clear

| Item | Spec |
| --- | --- |
| Purpose | Clear dependent input/auto columns after a parent value changes. |
| Required schema fields | `rule_id` on parent/affected rows; rule defines trigger column and dependent target columns. |
| Optional schema/rule fields | Clear only if value changed, preserve-if-compatible policy, result invalidation flag. |
| Current behavior example | `odu` change clears `fin_type`, `pi`, `row`, `cond_area`, and `cond_volume`. |
| Required future example | `idu` change should clear `evap_index`, `evap_area`, and `evap_volume` if current Evap selection is no longer compatible. |
| Future implementation note | Clear should be deterministic and should invalidate prediction result for that case. |
| Out of scope | Row deletion, schema migration, or model artifact invalidation. |

### composite_lookup

| Item | Spec |
| --- | --- |
| Purpose | Use several column values to build or resolve a mapping entity key and copy attributes to target columns. |
| Required schema fields | Target rows with `value_source=mapping_lookup` or `value_source=rule_options`, `mapping_entity`, `mapping_attribute`, and `rule_id`; rule defines key parts. |
| Optional schema/rule fields | Key join format, missing-part clear targets, not-found policy. |
| Current behavior example | `odu + fin_type + pi + row` resolves `cond_specs` and fills `cond_area`, `cond_volume`. |
| Future implementation note | Current string join key can be preserved for parity, but rule spec should not require every future composite lookup to use the same join format. |
| Out of scope | Generating `cond_specs`, validating master data file format, or UI manager editing. |

## Restart-required Schema Change Policy

Initial schema/column/rule changes are restart-required.

Rationale:

- Schema changes affect `COLUMNS`, adapter DTOs, table model columns, existing row data, dropdown delegates, mapping/autofill rules, ML input projection, and result invalidation.
- Live schema reload requires row migration, table model rebuild, mapping reload, cascade rule reload, and one-hot projection reload.
- Arc 13.5R-3 should prove read-only projection parity before any owner switch or live reload work.

Mapping data-only changes remain designed for live reload through mapping repository refresh and next-dropdown option reads. Schema/rule contract changes do not share that policy yet.

## Arc 13.5R-3 Readiness Criteria

Arc 13.5R-3 may proceed when this document is used as the accepted field/spec contract.

Read-only prototype scope:

- Create a draft schema representation only in the approved Arc 13.5R-3 scope.
- Project the draft schema to the current 28 core `COLUMNS` order with parity.
- Preserve dropdown column order and `DROPDOWN_COLS`.
- Preserve adapter-visible metadata required by current tests: key, header, group, editable, dropdown, mapping/dropdown target equivalent, `ml_feature`, `ml_target`, source/mapping_key compatibility as needed.
- Preserve unified case table status/message behavior or explicitly keep it adapter-local with documented parity.
- Do not switch runtime owner until parity tests exist and pass.

## Deferred Open Questions

| Deferred to | Question |
| --- | --- |
| Arc 13.5R-3 | Exact read-only draft file shape and projection adapter mechanics. |
| Arc 13.5R-4 | Runtime owner switch timing and parity test acceptance. |
| Arc 14A | Mapping Entity / Master Data model, entity definition schema, canonical CSV/import format. |
| Arc 14B | Data Mapping Manager UI workflows, validation UX, import/export UX. |
| Arc 14C | Runtime cascade engine implementation, rule storage format, row-specific dropdown state lifecycle. |
| Arc 15 | Model activation readiness, real dataset header readiness, retraining and artifact compatibility policy. |

## Next Action

Proceed to Arc 13.5R-3: read-only `schema.csv` draft/projection parity prototype. The prototype should not change Predict runtime behavior; it should prove that this v2 field contract can reproduce the current schema before any owner switch.
