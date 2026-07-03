# Arc 14A - Mapping Entity / Master Data Model Foundation

Status: active reference

## Purpose

Arc 14A adds the Qt-free core foundation needed before Data Mapping Manager UI
work. The goal is to represent mapping data as generic mapping entities,
attribute definitions, and row values instead of treating IDU/ODU fixed tables
as the schema boundary.

## Current Mapping Runtime Owner Summary

| Path | Current owner |
| --- | --- |
| `core/mapping/repository.py` | Loads the existing `mapping.json` runtime data. |
| `core/mapping/update.py` | Converts current Excel/CSV mapping sources into the existing JSON shape. |
| `scripts/update_mapping.py` | CLI wrapper for the existing converter. |
| `core/mapping/autofill.py` | Runtime simple lookup, ODU cascade options, and cond specs lookup policy. |
| `tests/fixtures/mapping/mapping_tables_legacy_wide.csv` | Legacy import-compat evidence, not canonical CSV v2. |

These owners were audited and not changed in Arc 14A.

## Mapping Entity / Master Data Model Boundary

New Qt-free core model objects live under `core.mapping`:

| Object | Responsibility |
| --- | --- |
| `MappingEntityDefinition` | Entity key/name, label, key attribute, attributes, active flag, notes. |
| `MappingAttributeDefinition` | Attribute key/label, data type, required flag, active flag, notes. |
| `MappingEntityRow` | Entity key, row key, row values, active flag, notes. |
| `MappingEntityCatalog` | Aggregate lookup by entity, row key, and attribute key. |
| `MappingValidationError` | Small validation DTO for UI/runtime reuse. |

This model does not import Qt, Predict UI adapters, mapping repository, or
mapping JSON writers.

## Predict Schema Catalog v2 Responsibility Split

Predict Schema Catalog v2 owns Predict table column definitions: `column_key`,
role, editor, value source, mapping entity/attribute references, trigger column,
rule reference, visibility, and ML projection metadata.

Mapping Entity / Master Data owns the referenced data: entity definitions,
attribute definitions, row keys, row values, required/type metadata, active
flags, and operational notes.

Adding `Inner Surface Area` to `evap_index` is Mapping Entity work. Adding a
new Predict column that displays or trains on that value is Predict Schema
Catalog work.

## Data Mapping Manager UI Responsibility Split

Arc 14B Data Mapping Manager UI should consume this core model and validation
boundary. It should not parse raw mapping JSON inside views, and it should not
own Predict column creation. CSV import/export, safe save, and mapping JSON
generation remain UI/controller/adapter follow-up work, not Arc 14A runtime.

## Runtime Cascade Engine Responsibility Split

Arc 14C Runtime Cascade Integration should consume validated entity data plus
Predict Schema Catalog references to implement lookup/filter/clear/composite
lookup primitives. Arc 14A does not switch `core.mapping.autofill`, implement
IDU Size -> Evap Index filtering, or reload mapping data at runtime.

## Canonical CSV v2 Direction

Canonical CSV v2 should be entity/attribute/row based, not one single fixed wide
CSV. The initial direction is three logical files or sections:

| Logical CSV | Minimum fields |
| --- | --- |
| Entity definitions | `entity_key`, `entity_label`, `key_attribute`, `active`, `notes`. |
| Attribute definitions | `entity_key`, `attribute_key`, `attribute_label`, `data_type`, `required`, `active`, `notes`. |
| Row data | `entity_key`, `row_key`, attribute value columns or normalized `attribute_key`/`value`, `active`, `notes`. |

The legacy wide CSV is not canonical because it stores unrelated entity tables
side by side, repeats blank separator columns, and cannot express future
entities/attributes without table-specific column-block rules.

Arc 14A does not implement CSV v2 import/export.

## Validation Scope Implemented Now

- Entity key must not be blank.
- Entity key must be unique.
- Attribute key must be unique within an entity.
- Entity key attribute must be defined as an attribute.
- Row entity must reference a defined entity.
- Row key must not be blank.
- Row key must be unique within an entity.
- Required attribute values must be present.
- Unknown row value attributes are rejected.
- Basic `string`, `number`, and `boolean` value validation is enforced.

## Validation Scope Deferred

- Range, unit, and enum consistency.
- Cross-entity reference validation.
- Composite key completeness.
- Filter/rule primitive consistency.
- Mapping JSON write policy and runtime reload.
- CSV v2 import/export validation.

## Existing Legacy Wide Fixture

`tests/fixtures/mapping/mapping_tables_legacy_wide.csv` remains compatibility
evidence for current converter/runtime behavior. It is not the canonical export
contract for Data Mapping Manager.

## What Changed

- Added generic mapping entity model DTOs under `core/mapping/entity_model.py`.
- Added reusable validation under `core/mapping/entity_validation.py`.
- Exported the model/validator from `core.mapping`.
- Added focused tests for generic entities, row lookup, and validation errors.

## What Did Not Change

- No Data Mapping Manager UI.
- No runtime cascade engine.
- No mapping JSON generation/update execution.
- No changes to `scripts/update_mapping.py` or `core.mapping.update`.
- No changes to `config/predict/schema.csv` or `config/ml/features.csv`.
- No Predict UI behavior change.
- No ML training, retraining, or artifact change.
- No existing fixture/golden expected changes.

## MVC / SoC / Hexagonal Assessment

The model and validator are pure core/domain objects. They are reusable by UI
controllers and future runtime integration without depending on Qt, file I/O,
or app-side adapters. Existing mapping repository/converter/runtime paths remain
separate infrastructure/runtime owners.

## Next Action

Proceed to Arc 14B - Data Mapping Manager UI. CSV v2 loader/exporter can be
implemented inside Arc 14B or a narrow Arc 14A follow-up only if UI work needs a
file-adapter slice before screens are built.
