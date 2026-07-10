# Arc 13.5R-4 - Projection Owner Switch

Status: active reference

## Purpose

이 문서는 Arc 13.5R-3 read-only parity evidence를 받아 Predict core column schema owner를 Predict Schema Catalog v2 projection으로 전환한 결과를 기록한다. 목표는 현재 public behavior를 유지하면서 `core.predictor_schema.columns.COLUMNS` 조립 경로를 `config/predict/schema.csv` 기반 v2 projection으로 좁게 전환하고, Arc 14A Mapping Entity / Master Data Model Foundation으로 넘어가기 전 남은 runtime-owned path를 분리하는 것이다.

## Readiness Decision

| Check | Decision |
| --- | --- |
| 28 core columns parity | Arc 13.5R-3 focused tests가 count, key order, header/group, dropdown, mapping compatibility, ML metadata parity를 증명했다. |
| Runtime behavior risk | Owner switch는 `COLUMNS` assembly owner만 바꾸고 Predict UI adapter, mapping/autofill, one-hot ML adapter behavior는 바꾸지 않는다. |
| Status/message handling | `status` / `message`는 v2 schema row로 표현되지만 core `COLUMNS` projection에서는 제외한다. Case table adapter-local virtual columns로 유지한다. |
| Compatibility hard-code | Legacy dropdown/autofill fields는 v2 semantic fields와 분리된 compatibility projection helper로 유지한다. |

Readiness decision: narrow owner switch를 수행한다.

## Owner Switch Result

| Surface | Result |
| --- | --- |
| `config/predict/schema.csv` | Predict core column projection source가 되었다. 아직 runtime-editable source나 live reload source는 아니다. |
| `core/predictor_schema/catalog_v2.py` | v2 draft schema loader and validator로 유지된다. |
| `core/predictor_schema/catalog_v2_projection.py` | v2 rows를 current `COLUMNS`-like metadata로 project하는 runtime helper가 되었다. |
| `core/predictor_schema/columns.py` | Feature Catalog + `ui_columns.py` merge path 대신 `load_projected_columns_v2()`에서 `COLUMNS`를 로드한다. Public constants는 유지한다. |
| `core/predictor_schema/ui_columns.py` | Runtime owner에서는 제외되었지만, cleanup/removal 대상은 아니다. Historical compatibility/reference로 남는다. |
| Feature Catalog | ML feature/target/one-hot contract source로 남는다. v2 schema hidden one-hot rows는 Feature Catalog one-hot groups와 parity를 검증한다. |

## Compatibility Hard-code Cleanup

| Area | Cleanup |
| --- | --- |
| Presentation metadata | Width and background defaults were moved into `core/predictor_schema/presentation.py` so v2 projection does not duplicate presentation defaults independently. |
| Dropdown compatibility | `_legacy_dropdown_mapping(row)` now names the current adapter compatibility field explicitly. It returns `column_key` because current `DROPDOWN_TARGET = {k: k}` behavior still depends on that legacy shape. |
| Mapping semantics | v2 semantic fields remain on schema rows as `mapping_entity`, `mapping_attribute`, `trigger_column`, and `rule_id`; current projected dicts still expose legacy `mapping`, `source`, and `mapping_key` only where current adapters require them. |
| Cond specs | `cond_area` / `cond_volume` keep current compatibility `source=odu` and `mapping_key` values while v2 rows record `mapping_entity=cond_specs` and `rule_id=cond_specs_lookup`. |

## What Changed

- `COLUMNS` is now loaded from the v2 projection helper.
- Derived constants such as `INPUT_COLS`, `AUTO_COLS`, `RESULT_COLS`, `DROPDOWN_COLS`, `DROPDOWN_TARGET`, `NUM_ROWS`, and column index constants continue to derive from `COLUMNS`.
- Focused tests now assert that `columns.COLUMNS` equals `load_projected_columns_v2()`.

## What Did Not Change

- Predict UI behavior is unchanged.
- Mapping data shape is unchanged.
- `core.mapping.autofill` still owns simple lookup plus hard-coded ODU cascade behavior.
- `DropdownOptionAdapter` still consumes current `mapping` / `dropdown_target` compatibility fields.
- `RowToMlInputAdapter` still owns current hard-coded one-hot selector mapping.
- `status` / `message` still come from the case table adapter rather than core `COLUMNS`.
- Live schema reload is not implemented; schema/column/rule changes remain restart-required.

## MVC / SoC / Hexagonal Boundary Assessment

The switch keeps schema loading/projection in Qt-free `core.predictor_schema` helpers and leaves UI adapters under `apps/predict` as consumers. It narrows the schema owner without moving mapping/autofill rules, ML input projection, or table virtual column policy into the loader. This keeps the change within the existing core schema boundary and avoids coupling v2 schema parsing to PySide6 widgets.

## Remaining Runtime-owned Paths

| Path | Remaining responsibility |
| --- | --- |
| `core.mapping.autofill` | Runtime lookup, ODU clear/options cascade, and cond specs composite lookup. |
| `apps.predict.adapters.dropdown_option_adapter` | Base dropdown option resolution from fallback values or mapping sections. |
| `apps.predict.adapters.row_to_ml_input_adapter` | Numeric ML input projection and one-hot selector expansion. |
| `apps.predict.schema.case_table_schema_adapter` | Virtual `status` and `message` columns. |
| Feature Catalog | ML feature/target/one-hot compatibility source until a later explicit owner switch. |

## Remaining Gaps

- Generic cascade primitives are documented but not implemented.
- IDU Size -> Evap Index filtering is still not implemented.
- Data Mapping Manager canonical CSV v2 format is still undecided.
- Mapping Entity / Master Data Model Foundation is still needed before Data Mapping Manager UI implementation.
- One-hot ML adapter owner switch remains deferred.
- Broad ML Catalog-Aligned Real Dataset Readiness remains Arc 15.

## Next Action

Proceed to Arc 14A: Mapping Entity / Master Data Model Foundation. Arc 14A should design generic mapping entity definitions, key columns, attributes, row validation, canonical CSV v2 shape, and mapping.json generation/update boundaries without assuming IDU-Evap or ODU-Cond are the schema boundary.
