# Arc 13.5R - Predict Schema / Mapping Manager Foundation

Status: active reference

## Purpose

이 문서는 Arc 13.5 Feature Catalog Manager와 Arc 14 Data Mapping Manager를 별도 기능으로만 보지 않고, 다음 세 가지 계약으로 다시 정렬한 설계 결정을 보존한다.

| Layer | Target role | Why it matters |
| --- | --- | --- |
| Predict Schema Catalog v2 | Predict UI column, role, mapping reference, template rule의 상위 계약 | 새 입력 column group을 안전하게 추가하기 위한 기준이다. |
| Mapping Master Data | IDU, Evap, ODU, Cond, Compressor, Ref/Exp option data의 master CRUD | dropdown/autofill option과 spec 값을 관리한다. |
| Runtime Cascade | schema/template-aware dependent update engine | 선택 값 변경 시 slot별 clear, option filter, autofill을 일관되게 적용한다. |

다음 agent는 이 문서를 읽고 Arc 14 Data Mapping Manager 구현 전에 왜 Arc 13.5R Predict Schema Catalog v2 design/audit이 필요한지 이해할 수 있어야 한다.

## Context

Arc 13.5A까지 `app_train.py` Feature Catalog tab은 `config/ml/features.csv` 직접 편집을 대체하는 Train/Admin 관리 화면으로 확장되었다. 현재 기능은 viewer, validation, Excel-safe export, editable save, add/delete/duplicate, dropdown, help, dirty-state, model fingerprint guard를 포함한다.

이 구조는 Data Mapping Manager 구현의 좋은 참조 모델이다. UI가 CSV를 직접 파싱하거나 저장하지 않고 controller, service, core/file-adapter boundary를 거치는 방향도 유지해야 한다.

하지만 Feature Catalog Manager는 현재 ML feature 중심이다. Predict UI에서 사용자가 원하는 column 관리는 ML feature만으로 끝나지 않는다. 특히 dropdown-only input, helper/autofill column, result/rule column, cascade rule, template slot이 하나의 schema contract 안에서 함께 해석되어야 한다.

## Current Problem

현재 구조는 다음 세 책임이 분리되어 있으나, 서로를 묶는 상위 contract가 충분하지 않다.

| Area | Current shape | Gap |
| --- | --- | --- |
| Feature Catalog | ML feature/target 중심 catalog | dropdown-only input과 helper/result column 전체를 대표하지 못한다. |
| Data Mapping | mapping JSON/source update 대상으로 예정 | 새 Predict column 자체를 만들 책임이 아니다. |
| Runtime Cascade | 현재 column key와 mapping owner에 의존 | `IDU2` 같은 slot 추가 시 규칙을 template 단위로 복제/적용할 계약이 부족하다. |

따라서 Arc 14를 바로 Data Mapping Manager UI로 구현하면 column group, `mapping_section` / `mapping_key`, cascade/template behavior가 어디서 정의되는지 불명확해진다. Arc 13.5R은 이 gap을 먼저 문서화하고 audit하는 설계 slice다.

## Decisions

| Decision | Resulting boundary |
| --- | --- |
| Feature Catalog Manager는 장기적으로 Predict Schema Manager로 확장/승격한다. | ML feature row 관리만이 아니라 Predict UI column 전체 계약을 다루는 상위 owner가 필요하다. |
| Predict Schema Catalog는 `input`, `auto`, `helper`, `result` columns 전체를 관리해야 한다. | column role, visibility, order, required, data type, editor, mapping reference, cascade/template rule이 catalog에서 설명되어야 한다. |
| Data Mapping Manager는 column 정의가 아니라 mapping master data를 관리한다. | IDU/Evap/ODU/Cond/Compressor/Ref/Exp option/spec CRUD, import/export, validation, safe write, reload가 책임이다. |
| 새 option/spec 추가와 새 column/feature 추가를 분리한다. | `Comp D`, `IDU B`, `Evap 1-2` 추가는 Mapping Manager 영역이고, `idu_2`, `evap_area_2` 같은 column group 추가는 Predict Schema Manager 영역이다. |
| IDU와 Evap은 직접 종속이 아니라 IDU Size를 통해 연결된다. | Evap Area/Volume은 IDU가 아니라 선택된 Evap Index에서 온다. |
| IDU-Evap Slot은 template/group 단위로 추가되어야 한다. | slot별 column set은 늘어날 수 있지만 master mapping data는 공유한다. |
| Mapping data 변경은 live reload 가능하게 설계한다. | `mapping.json` save 후 repository reload와 dropdown/autofill option refresh가 가능해야 한다. |
| Schema/column 변경은 초기 정책을 restart-required로 둔다. | live schema rebuild는 row migration, table model rebuild, mapping reload, cascade rule reload가 필요하므로 별도 future work다. |
| ML feature activation은 Arc 15 readiness audit 대상이다. | 새 column이 추가되어도 training header, preprocessing list, retrain, artifact compatibility가 준비되기 전에는 Model active가 아니다. |

## Correct Dependency Model

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

## Target Architecture

| Component | Owns | Does not own |
| --- | --- | --- |
| Predict Schema Catalog v2 | Predict column keys, roles, order, visibility, editor type, mapping section/key, slot template, cascade rule reference | Raw master data row CRUD |
| Predict Schema Manager | column/group/template add/update validation and safe save | Mapping option/spec CRUD |
| Mapping Master Data Model | IDU, Evap, ODU, Cond spec, Compressor, Ref/Exp option records | Predict column definitions |
| Data Mapping Manager | master data CRUD, CSV import/export, validation, `mapping.json` safe write, mapping reload | Feature activation, model retrain, schema rebuild |
| Runtime Cascade Engine | slot-aware dependent clear, option filter, autofill application | Persistent schema editing |
| Predict Workspace | render schema, store row data, request cascade application | Direct mapping JSON parsing or schema mutation |

Predict Schema Catalog v2 should eventually express enough metadata for both UI table projection and cascade wiring. The exact storage format remains an Arc 13.5R audit/design output, not a decision in this record.

## Manager Responsibilities

### Predict Schema Manager

| Responsibility | Examples |
| --- | --- |
| Column role management | `input`, `auto`, `helper`, `result` |
| UI metadata | order, label/header, visibility, required, data type, editor type |
| Mapping reference | `mapping_section=idu`, `mapping_key=ID Volume` style references |
| Template/group creation | IDU-Evap Slot 1, IDU-Evap Slot 2, ODU-Cond Slot N |
| Schema save policy | initial restart-required for table schema changes |
| ML state classification | UI only, Mapping ready, Model active |

### Data Mapping Manager

| Responsibility | Examples |
| --- | --- |
| Master data CRUD | IDU, Evap, ODU, Cond spec, Compressor, Ref option, Exp option |
| Import/export | CSV import/export for mapping master data |
| Validation | required columns, duplicate keys, Size consistency, cond spec combinations |
| Safe write | validated `mapping.json` generation/update |
| Runtime refresh | `PredictMappingRepository.reload()` and next-dropdown option refresh |

Data Mapping Manager is not the place to add new Predict columns.

## Runtime Apply Policy

### IDU-Evap Slot Rule

| Event | Runtime action |
| --- | --- |
| `idu_n` changes | Lookup selected IDU in the IDU table. |
| IDU lookup succeeds | Set `id_volume_n` and `id_size_n`. |
| IDU changed | Clear `evap_index_n`, `evap_area_n`, and `evap_volume_n`. |
| Evap options needed | Filter Evap Index options where `Size == id_size_n`. |
| `evap_index_n` changes | Lookup selected Evap Index and set `evap_area_n`, `evap_volume_n`. |

### ODU-Cond Slot Rule

| Event | Runtime action |
| --- | --- |
| `odu_n` changes | Set `od_volume_n`; update `fin_type_n`, `pi_n`, `row_n` options. |
| ODU or cond selector changes | Clear `cond_area_n` and `cond_volume_n` until a complete spec key exists. |
| `fin_type_n + pi_n + row_n` complete | Lookup cond spec and autofill `cond_area_n`, `cond_volume_n`. |

### Save / Refresh Policy

| Change type | Initial policy | Future option |
| --- | --- | --- |
| Mapping data only | Save `mapping.json`, reload mapping repository, refresh dropdown/autofill options live. | Keep live refresh as the expected Data Mapping Manager behavior. |
| Schema/column/template | Save Predict Schema Catalog, mark restart-required. | Implement `PredictWorkspace.reload_schema()` as a separate slice after row migration and table rebuild policy exist. |
| ML model activation | Do not activate automatically. | Arc 15 audit confirms training data header, preprocessing, retrain, and artifact compatibility. |

## Revised Arc Plan

| Arc | Revised purpose |
| --- | --- |
| Arc 13.5R | Predict Schema Catalog v2 design/audit before implementing Data Mapping Manager. |
| Arc 14A | Mapping Master Data Model Foundation. |
| Arc 14B | Data Mapping Manager UI for mapping master data CRUD/import/export/validation/save. |
| Arc 14C | Runtime Cascade Integration with schema/template-aware rules. |
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
| Which template scopes are first-class? | At minimum IDU-Evap Slot and ODU-Cond Slot need explicit audit. |
| When should live schema reload be implemented? | Keep restart-required initially; split live rebuild into later work. |
| What is the canonical CSV v2 format for Data Mapping Manager import/export? | Do not infer it from the legacy wide fixture. Define separately in Arc 14A/14B. |
| How are UI only, Mapping ready, and Model active states represented? | Treat as a required readiness classification for schema-managed columns. |

## Next Action

Run Arc 13.5R as a design/audit slice:

1. Audit current `core.predictor_schema.columns`, UI-only dropdown insertion, Feature Catalog projection, mapping adapter, and Predict table schema adapter.
2. Define the Predict Schema Catalog v2 field set and owner boundary.
3. Define IDU-Evap Slot and ODU-Cond Slot templates without implementing runtime cascade.
4. Decide restart-required save wording for schema changes.
5. Keep Data Mapping Manager implementation deferred until the schema contract is clear.

Reference fixture:

| Fixture | Use |
| --- | --- |
| `tests/fixtures/mapping/mapping_tables_legacy_wide.csv` | Legacy wide CSV import compatibility fixture only. Do not treat it as the canonical manager export format. |
