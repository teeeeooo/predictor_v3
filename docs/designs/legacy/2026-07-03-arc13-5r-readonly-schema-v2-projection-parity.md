# Arc 13.5R-3 - Read-only Schema v2 Projection Parity

Status: active reference

## Purpose

이 문서는 Arc 13.5R-3 read-only Predict Schema Catalog v2 draft/projection parity prototype 결과를 기록한다. 목적은 Arc 13.5R-2에서 확정한 field/spec contract가 현재 core predictor schema의 28개 `COLUMNS`를 동일한 순서와 핵심 metadata로 재현할 수 있음을 확인하고, Arc 13.5R-4 projection owner switch 여부를 판단할 수 있게 남은 gap을 정리하는 것이다.

## Implemented Prototype Scope

| Artifact | Role |
| --- | --- |
| `config/predict/schema.csv` | Read-only v2 draft schema. Runtime source of truth가 아니다. |
| `core/predictor_schema/catalog_v2.py` | Qt-free loader and minimum validator for the draft schema. |
| `core/predictor_schema/catalog_v2_projection.py` | Draft schema rows to current `COLUMNS`-like metadata projection helper. |
| `tests/test_predict_schema_catalog_v2.py` | Loader/validation, one-hot, and status-row checks. |
| `tests/test_predict_schema_catalog_v2_projection.py` | Current `COLUMNS` parity, dropdown parity, one-hot parity, cond compatibility checks. |

The existing runtime owner remains unchanged:

- `core/predictor_schema/columns.py` still assembles the runtime `COLUMNS`.
- Predict UI adapters still consume the existing runtime schema.
- No runtime code path imports the v2 draft helper as source of truth.

## Confirmed Parity Coverage

| Coverage | Result |
| --- | --- |
| Core column count | v2 projection returns 28 rows, matching current `COLUMNS`. |
| Core column key order | v2 projection matches current `COLUMNS` key order. |
| Header/group metadata | v2 projection matches current headers and groups. |
| Dropdown metadata | v2 projection reproduces current dropdown keys and `type=dropdown` rows. |
| Read-only metadata | v2 projection preserves current result readonly metadata. |
| Mapping compatibility | v2 projection preserves current `mapping`, `source`, and `mapping_key` compatibility fields needed by current adapters/tests. |
| ML metadata | v2 projection preserves current `ml_feature` and `ml_target` metadata. |
| One-hot selector mapping | v2 selector rows match current `RowToMlInputAdapter._ONE_HOT_INPUT_GROUPS`. |
| Hidden one-hot feature rows | v2 hidden one-hot rows match Feature Catalog one-hot groups. |

## Runtime-owned Paths Not Switched

| Path | Status |
| --- | --- |
| `core/predictor_schema/columns.py` | Still owns runtime `COLUMNS`. |
| `apps/predict/schema/column_schema_adapter.py` | Still adapts current runtime schema. |
| `apps/predict/schema/case_table_schema_adapter.py` | Still appends virtual status/message rows. |
| `core/mapping/autofill.py` | Still owns current simple lookup and hard-coded ODU cascade behavior. |
| `apps/predict/adapters/row_to_ml_input_adapter.py` | Still owns current hard-coded one-hot selector map. |

## Status / Message Handling

`status` and `message` are represented in `config/predict/schema.csv` as `role=status` rows so the v2 contract can describe the full visible case table. They are intentionally excluded from the 28-row core projection parity helper because current `core.predictor_schema.columns.COLUMNS` does not include them.

Arc 13.5R-4 must decide whether status/message rows remain adapter-local or become projected from v2 into the case table adapter.

## One-hot Handling

The draft schema separates selector rows from emitted one-hot feature rows:

| Row type | Example | Projection behavior |
| --- | --- | --- |
| Selector row | `ref_type`, `exp_type` | Projects as visible dropdown input rows; `value_source=one_hot`; `one_hot_group` records selector-to-group mapping. |
| Emitted feature row | `R410A`, `R32`, `R290`, `EEV`, `Capi` | Stored as `role=one_hot_feature`, `visible=false`; excluded from core table projection; used to verify Feature Catalog one-hot parity. |

Runtime one-hot projection is not switched in this slice.

## Known Gaps For Arc 13.5R-4

- Owner switch is not done. Current runtime still uses `core/predictor_schema/columns.py`.
- `source` / `mapping_key` compatibility fields are synthesized from v2 fields for parity, but current adapters still depend on the legacy shape.
- `cond_area` / `cond_volume` preserve current compatibility metadata while v2 records `cond_specs` as the target mapping entity. Runtime behavior is not changed.
- `DROPDOWN_TARGET = {k: k}` remains in the current runtime owner.
- IDU Size -> Evap Index filtering remains unimplemented.
- ODU cascade and one-hot selector mapping remain hard-coded in runtime paths.
- Live schema reload remains out of scope; schema/column/rule changes remain restart-required.

## Next Action

Arc 13.5R-4 should decide and implement the projection owner switch only after accepting this parity evidence. The owner switch slice should keep current behavior stable, preserve existing focused tests, and add any missing parity guards before replacing runtime `COLUMNS` assembly.
