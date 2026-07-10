# Arc 13.5R - Predict Schema / Mapping Manager Foundation

Status: active reference

## Purpose

이 문서는 Arc 13.5 Feature Catalog Manager와 Arc 14 Data Mapping Manager를 별도 기능으로만 보지 않고, 다음 세 가지 계약으로 다시 정렬한 설계 결정을 보존한다.

| Layer | Target role | Why it matters |
| --- | --- | --- |
| Predict Schema Catalog v2 | Predict UI column, role, mapping entity/attribute reference, rule reference의 상위 계약 | 새 column, 새 mapping attribute, 새 mapping entity를 안전하게 연결하기 위한 기준이다. |
| Mapping Entity / Master Data | mapping entity definition, key column, attributes, row data CRUD | dropdown/autofill option과 spec 값을 IDU/ODU에 고정하지 않고 관리한다. |
| Runtime Cascade | schema/rule-aware dependent update engine | lookup, filter, clear, composite lookup을 generic primitive로 일관되게 적용한다. |

다음 agent는 이 문서를 읽고 Arc 14 Data Mapping Manager 구현 전에 왜 Arc 13.5R Predict Schema Catalog v2 design/audit이 필요한지 이해할 수 있어야 한다.

## Context

Arc 13.5A까지 `app_train.py` Feature Catalog tab은 `config/ml/features.csv` 직접 편집을 대체하는 Train/Admin 관리 화면으로 확장되었다. 현재 기능은 viewer, validation, Excel-safe export, editable save, add/delete/duplicate, dropdown, help, dirty-state, model fingerprint guard를 포함한다.

이 구조는 Data Mapping Manager 구현의 좋은 참조 모델이다. UI가 CSV를 직접 파싱하거나 저장하지 않고 controller, service, core/file-adapter boundary를 거치는 방향도 유지해야 한다.

하지만 Feature Catalog Manager는 현재 ML feature 중심이다. Predict UI에서 사용자가 원하는 column 관리는 ML feature만으로 끝나지 않는다. 특히 dropdown-only input, helper/autofill column, result/rule column, mapping entity/attribute reference, cascade rule이 하나의 schema contract 안에서 함께 해석되어야 한다.

## Current Problem

현재 구조는 다음 세 책임이 분리되어 있으나, 서로를 묶는 상위 contract가 충분하지 않다.

| Area | Current shape | Gap |
| --- | --- | --- |
| Feature Catalog | ML feature/target 중심 catalog | dropdown-only input과 helper/result column 전체를 대표하지 못한다. |
| Data Mapping | mapping JSON/source update 대상으로 예정 | 새 Predict column 자체를 만들 책임이 아니다. |
| Runtime Cascade | 현재 column key와 mapping owner에 의존 | 새 mapping entity, 새 attribute, 새 종속 dropdown을 generic rule로 표현할 계약이 부족하다. |

따라서 Arc 14를 바로 Data Mapping Manager UI로 구현하면 column group뿐 아니라 `mapping_entity`, `mapping_attribute`, `trigger_column`, `rule_id`, cascade/autofill primitive가 어디서 정의되는지 불명확해진다. Arc 13.5R은 이 gap을 먼저 문서화하고 audit하는 설계 slice다.

## Decisions

| Decision | Resulting boundary |
| --- | --- |
| Feature Catalog Manager는 장기적으로 Predict Schema Manager로 확장/승격한다. | ML feature row 관리만이 아니라 Predict UI column 전체 계약을 다루는 상위 owner가 필요하다. |
| Predict Schema Catalog는 `input`, `auto`, `helper`, `result` columns 전체를 관리해야 한다. | column role, visibility, order, required, data type, editor, mapping entity/attribute reference, cascade/autofill rule이 catalog에서 설명되어야 한다. |
| Data Mapping Manager는 column 정의가 아니라 Mapping Entity / Master Data를 관리한다. | `idu`, `evap_index`, `odu`, `cond_specs`뿐 아니라 future entity인 `fan_motor`, `tube_geometry`, `tube_diameter`, `motor_specs`도 같은 방식으로 다룰 수 있어야 한다. |
| 새 option/spec/attribute 추가와 새 column/feature 추가를 분리한다. | `Comp D`, `IDU B`, `Evap 1-2`, `Inner Surface Area` 추가는 Mapping Entity Manager 영역이고, 이를 표시/학습에 쓰는 Predict column 추가는 Predict Schema Manager 영역이다. |
| IDU와 Evap은 직접 종속이 아니라 IDU Size를 통해 연결된다. | Evap Area/Volume은 IDU가 아니라 선택된 Evap Index에서 온다. |
| IDU-Evap / ODU-Cond는 representative example 또는 default preset일 뿐이다. | core schema boundary는 특정 HVAC 부품 조합 template이 아니라 generic mapping entity / attribute / rule expression이다. |
| `template_id`, `slot_id`, `cascade_role`는 optional preset/group helper로 격하한다. | 사용 편의를 위해 둘 수 있지만 v2의 핵심 contract는 `mapping_entity`, `mapping_attribute`, `trigger_column`, `rule_id`다. |
| Mapping data 변경은 live reload 가능하게 설계한다. | `mapping.json` save 후 repository reload와 dropdown/autofill option refresh가 가능해야 한다. |
| Schema/column 변경은 초기 정책을 restart-required로 둔다. | live schema rebuild는 row migration, table model rebuild, mapping reload, cascade rule reload가 필요하므로 별도 future work다. |
| ML feature activation은 Arc 15 readiness audit 대상이다. | 새 column이 추가되어도 training header, preprocessing list, retrain, artifact compatibility가 준비되기 전에는 Model active가 아니다. |

## Correct Dependency Model

이 section은 IDU-Evap dependency를 바로잡기 위한 representative example이다. IDU-Evap / ODU-Cond는 default preset 후보일 수 있지만 Predict Schema Catalog v2의 boundary 자체는 아니다. v2 boundary는 임의의 mapping entity, mapping attribute, cascade/autofill rule을 표현할 수 있는 generic contract다.

잘못된 이해는 Evap Area / Evap Volume이 IDU에 직접 종속된다는 것이다. 올바른 모델은 IDU가 ID Volume과 Size를 제공하고, 그 Size가 Evap Index 후보를 필터링하며, Evap Index가 Evap Area와 Evap Volume을 제공한다.

```text
IDU
-> ID Volume
-> ID Size

ID Size
-> Evap Index dropdown filter

Evap Index
-> Evap Area
-> Evap Volume
```

예시는 다음과 같다.

| Table | Key | Size | Provided values |
| --- | --- | ---: | --- |
| IDU | A | 1 | ID Volume 40 |
| IDU | B | 1 | ID Volume 42 |
| Evap Index | 1-1 | 1 | Evap Area 5, Evap Volume 0.512 |

가능한 결과:

| Selection | ID Volume | ID Size | Evap Area | Evap Volume |
| --- | ---: | ---: | ---: | ---: |
| A + 1-1 | 40 | 1 | 5 | 0.512 |
| B + 1-1 | 42 | 1 | 5 | 0.512 |

A와 B는 서로 다른 IDU지만 같은 Size 1을 가지므로 같은 Evap Index 1-1을 선택할 수 있다. Evap Area와 Evap Volume 값은 IDU가 아니라 선택된 Evap Index에서 온다.

## Generic Extension Cases

### Case A - Add an attribute to an existing mapping entity

Evap Index에 `Inner Surface Area` attribute가 추가될 수 있다.

Mapping data example:

| mapping_entity | key | Size | Evap Area | Evap Volume | Inner Surface Area |
| --- | --- | ---: | ---: | ---: | ---: |
| `evap_index` | `S1-2` | 1 | 5 | 10 | 8.2 |

Predict column example:

| Field | Value |
| --- | --- |
| `column_key` | `evap_inner_surface_area` |
| `role` | `auto` |
| `value_source` | `mapping_lookup` |
| `mapping_entity` | `evap_index` |
| `mapping_attribute` | `Inner Surface Area` |
| `trigger_column` | `evap_index` |
| `model_input_enabled` | `true` |
| `ml_name` | `Evap Inner Surface Area` |

의미: `evap_index` column에서 선택된 값을 기준으로 `evap_index` mapping entity를 lookup하고, `Inner Surface Area` attribute 값을 `evap_inner_surface_area` column에 입력한다.

### Case B - Add a new mapping entity

완전히 새로운 `fan_motor` mapping entity가 추가될 수 있다.

| mapping_entity | key | Motor Efficiency | Motor Power |
| --- | --- | ---: | ---: |
| `fan_motor` | `FM-A` | 0.82 | 35 |
| `fan_motor` | `FM-B` | 0.86 | 42 |

Predict columns:

| column_key | role | value_source | mapping_entity | mapping_attribute | trigger_column |
| --- | --- | --- | --- | --- | --- |
| `fan_motor` | `input` | `manual` | `fan_motor` |  |  |
| `motor_efficiency` | `auto` | `mapping_lookup` | `fan_motor` | `Motor Efficiency` | `fan_motor` |
| `motor_power` | `auto` | `mapping_lookup` | `fan_motor` | `Motor Power` | `fan_motor` |

Cascade/autofill:

```text
fan_motor 선택
-> motor_efficiency 자동입력
-> motor_power 자동입력
```

### Case C - Add a dependent dropdown relationship

새 종속 dropdown 관계도 특정 IDU-Evap template이 아니라 generic filter + lookup rule로 표현해야 한다.

```text
tube_type 선택
-> 가능한 tube_diameter만 표시
-> tube_diameter 선택
-> Inner Area / Pressure Loss Factor 자동입력
```

이 케이스는 `filter` primitive와 `lookup` primitive를 조합한다. 복합 key 또는 여러 입력 column이 필요한 경우에는 `composite_lookup` rule을 참조한다.

## Predict Schema Catalog v2 Field Candidates

v2 storage format은 Arc 13.5R audit/design에서 확정해야 하지만, 핵심 후보는 특정 slot/template이 아니라 generic mapping expression을 중심으로 둔다.

| Field | Meaning |
| --- | --- |
| `column_key` | Predict row/table에서 쓰는 stable column key. |
| `label` | 사용자-facing header/label. |
| `role` | `input`, `auto`, `helper`, `result` 등 column role. |
| `editor` | manual 입력, dropdown, readonly display 등 editor type. |
| `data_type` | string, number, boolean 등 value type. |
| `visible` | 기본 표시 여부. |
| `required` | 사용자 입력 또는 lookup 결과 필수 여부. |
| `readonly` | 사용자가 직접 수정할 수 없는 column 여부. |
| `value_source` | `manual`, `mapping_lookup`, `formula`, `result`, `one_hot`. |
| `mapping_entity` | 참조할 mapping table/entity. 예: `evap_index`, `fan_motor`. |
| `mapping_attribute` | 가져올 attribute. 예: `Inner Surface Area`. |
| `trigger_column` | lookup 기준 column. 예: `evap_index`, `fan_motor`. |
| `rule_id` | 복잡한 filter, clear, composite lookup rule 참조. |
| `model_input_enabled` | 실제 ML input으로 보낼지 여부. |
| `ml_name` | 모델 feature name. |
| `one_hot_group` | one-hot encoding group. |
| `display_order` | UI 표시 순서. |
| `active` | schema row 활성 여부. |
| `notes` | 운영 메모. |

Optional preset/group helper:

| Optional helper | Status |
| --- | --- |
| `template_id` | 반복 column set을 빠르게 만들기 위한 preset helper. Core boundary가 아니다. |
| `slot_id` | preset이 만든 반복 instance 식별용 helper. Core boundary가 아니다. |
| `cascade_role` | rule authoring 편의를 위한 label/helper. 실제 적용은 `rule_id`와 primitive 정의가 기준이다. |

## Target Architecture

| Component | Owns | Does not own |
| --- | --- | --- |
| Predict Schema Catalog v2 | Predict column keys, roles, order, visibility, editor type, `value_source`, `mapping_entity`, `mapping_attribute`, `trigger_column`, `rule_id` | Raw master data row CRUD |
| Predict Schema Manager | column/group/preset add/update validation and safe save | Mapping entity row CRUD |
| Mapping Entity / Master Data Model | entity definition, key column, attributes, row data for existing and future mapping entities | Predict column definitions |
| Data Mapping Manager | entity/attribute/row CRUD, CSV import/export, validation, `mapping.json` safe write, mapping reload | Feature activation, model retrain, schema rebuild |
| Runtime Cascade Engine | rule-aware lookup, filter, clear, composite lookup application | Persistent schema editing |
| Predict Workspace | render schema, store row data, request cascade application | Direct mapping JSON parsing or schema mutation |

Predict Schema Catalog v2 should eventually express enough metadata for both UI table projection and cascade wiring. The exact storage format remains an Arc 13.5R audit/design output, not a decision in this record.

## Manager Responsibilities

### Predict Schema Manager

| Responsibility | Examples |
| --- | --- |
| Column role management | `input`, `auto`, `helper`, `result` |
| UI metadata | order, label/header, visibility, required, data type, editor type |
| Mapping reference | `mapping_entity=evap_index`, `mapping_attribute=Inner Surface Area`, `trigger_column=evap_index` style references |
| Rule reference | `rule_id` for filter, clear, composite lookup, or other future rule owners |
| Preset/group creation | Optional IDU-Evap or ODU-Cond default presets; not the core boundary |
| Schema save policy | initial restart-required for table schema changes |
| ML state classification | UI only, Mapping ready, Model active |

### Data Mapping Manager / Mapping Entity Manager

| Responsibility | Examples |
| --- | --- |
| Entity definition | `idu`, `evap_index`, `odu`, `cond_specs`, `fan_motor`, `tube_geometry`, `tube_diameter`, `motor_specs` |
| Key column and attributes | entity key plus attributes such as `Size`, `Evap Area`, `Inner Surface Area`, `Motor Efficiency` |
| Row data CRUD | add/update/delete option/spec rows inside an entity |
| Import/export | CSV import/export for mapping entity data |
| Validation | required attributes, duplicate keys, type/range constraints, reference/filter consistency, composite key completeness |
| Safe write | validated `mapping.json` generation/update |
| Runtime refresh | `PredictMappingRepository.reload()` and next-dropdown option refresh |

Data Mapping Manager is not the place to add new Predict columns.

## Runtime Apply Policy

Runtime cascade/autofill should be expressed through a small set of generic primitives. The project should not encode every future entity as a one-off hard-coded path when a schema/rule reference can describe it.

| Primitive | Meaning | Example |
| --- | --- | --- |
| `lookup` | selected column value로 mapping entity를 조회하고 attribute를 target column에 입력한다. | `fan_motor` -> `motor_efficiency`, `motor_power` |
| `filter` | parent lookup attribute 값으로 target dropdown options를 제한한다. | IDU `Size` -> allowed `evap_index` options |
| `clear` | parent 변경 시 dependent columns를 비운다. | `idu` 변경 -> `evap_index`, `evap_area`, `evap_volume` clear |
| `composite_lookup` | 여러 column 값을 조합해 mapping entity/spec를 조회한다. | `odu + fin_type + pi + row` -> `cond_specs` |

### IDU-Evap Example / Default Preset

| Event | Runtime action |
| --- | --- |
| `idu_n` changes | Lookup selected IDU in the IDU table. |
| IDU lookup succeeds | Set `id_volume_n` and `id_size_n`. |
| IDU changed | Clear `evap_index_n`, `evap_area_n`, and `evap_volume_n`. |
| Evap options needed | Filter Evap Index options where `Size == id_size_n`. |
| `evap_index_n` changes | Lookup selected Evap Index and set `evap_area_n`, `evap_volume_n`. |

This is a representative preset built from `lookup`, `filter`, and `clear`. It is not the schema boundary.

### ODU-Cond Example / Default Preset

| Event | Runtime action |
| --- | --- |
| `odu_n` changes | Set `od_volume_n`; update `fin_type_n`, `pi_n`, `row_n` options. |
| ODU or cond selector changes | Clear `cond_area_n` and `cond_volume_n` until a complete spec key exists. |
| `fin_type_n + pi_n + row_n` complete | Lookup cond spec and autofill `cond_area_n`, `cond_volume_n`. |

This is a representative preset built from `lookup`, `filter`, `clear`, and `composite_lookup`. It is not the schema boundary.

### Save / Refresh Policy

| Change type | Initial policy | Future option |
| --- | --- | --- |
| Mapping data only | Save `mapping.json`, reload mapping repository, refresh dropdown/autofill options live. | Keep live refresh as the expected Data Mapping Manager behavior. |
| Schema/column/rule contract | Save Predict Schema Catalog, mark restart-required. | Implement `PredictWorkspace.reload_schema()` as a separate slice after row migration and table/rule rebuild policy exist. |
| ML model activation | Do not activate automatically. | Arc 15 audit confirms training data header, preprocessing, retrain, and artifact compatibility. |

## Revised Arc Plan

| Arc | Revised purpose |
| --- | --- |
| Arc 13.5R | Predict Schema Catalog v2 design/audit for generic mapping entity / attribute / rule contract before implementing Data Mapping Manager. |
| Arc 14A | Mapping Entity / Master Data Model Foundation. |
| Arc 14B | Data Mapping Manager UI for mapping entity CRUD/import/export/validation/save. |
| Arc 14C | Runtime Cascade Integration with schema/rule-aware primitives. |
| Arc 15 | ML Catalog-Aligned Real Dataset Readiness Audit. |

Arc 14 should not be treated as a single Data Mapping tab implementation until the schema/catalog boundary is clear.

## Out of Scope

- Calculation logic changes.
- Predict UI implementation changes.
- Feature Catalog Manager code changes.
- Mapping converter implementation.
- Data Mapping Manager UI implementation.
- Runtime cascade code changes.
- `mapping.json` generation from the fixture in this task.
- Canonical manager export format definition.
- ML model training, retraining, or feature activation.

## Open Questions

| Question | Initial direction |
| --- | --- |
| What is the exact Predict Schema Catalog v2 storage format? | Decide in Arc 13.5R after auditing current catalog projection and UI-only columns. |
| Which fields form the core schema boundary? | Treat `mapping_entity`, `mapping_attribute`, `trigger_column`, and `rule_id` as core candidates; treat template/slot helpers as optional presets unless audit proves otherwise. |
| Which cascade/autofill primitives are enough for initial runtime integration? | Audit at least `lookup`, `filter`, `clear`, and `composite_lookup`. |
| When should live schema reload be implemented? | Keep restart-required initially; split live rebuild into later work. |
| What is the canonical CSV v2 format for Data Mapping Manager import/export? | Do not infer it from the legacy wide fixture. Define an entity/attribute-based format separately in Arc 14A/14B. |
| How are UI only, Mapping ready, and Model active states represented? | Treat as a required readiness classification for schema-managed columns. |

## Next Action

Run Arc 13.5R as a design/audit slice:

1. Audit current `core.predictor_schema.columns`, UI-only dropdown insertion, Feature Catalog projection, mapping adapter, and Predict table schema adapter.
2. Define the Predict Schema Catalog v2 field set and owner boundary around generic mapping entity / attribute / rule expression.
3. Define cascade/autofill primitive scope for `lookup`, `filter`, `clear`, and `composite_lookup`.
4. Treat IDU-Evap and ODU-Cond as representative examples/default presets, not core schema boundaries.
5. Decide restart-required save wording for schema changes.
6. Keep Data Mapping Manager implementation deferred until the generic schema contract is clear.

Reference fixture:

| Fixture | Use |
| --- | --- |
| `tests/fixtures/mapping/mapping_tables_legacy_wide.csv` | Legacy wide CSV import compatibility fixture only. Do not treat it as the canonical manager export format. |
