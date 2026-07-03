# Arc 14B-1 - Data Mapping Manager UI Foundation

Status: active reference

## Purpose

Arc 14B-1 starts the Train/Admin Data Mapping Manager as a read-only foundation
surface. It also tightens two Arc 14A model/validation decisions before CSV v2,
editable CRUD, mapping JSON generation, or runtime cascade integration build on
the model.

## Arc 14A Minor Follow-up Decisions

### Active flag semantics

- `active` is management visibility/eligibility metadata.
- Blank key, duplicate key, and key attribute definition checks are structural
  validation and run regardless of active status.
- Inactive attributes remain defined but are skipped for row required/type
  value validation.
- Inactive rows remain visible to management surfaces but are skipped for row
  required/type value validation.
- Inactive entities remain definitions. Future export/runtime generation may
  exclude them, but Arc 14B-1 does not implement that policy.

### row_key / key_attribute relationship

- `MappingEntityRow.row_key` is the canonical row identity.
- `MappingEntityDefinition.key_attribute` describes which attribute/header
  represents the row key during import/export/UI display.
- `row.values` may omit the key attribute.
- If `row.values` includes the key attribute, its trimmed string value must
  match `row_key`; otherwise validation returns
  `row_key_attribute_mismatch`.

## UI Foundation Scope

The Data Mapping tab is now a read-only Mapping Entity / Master Data surface:

- entity list;
- selected entity attribute table;
- selected entity row-value table;
- validation summary;
- disabled future action surface for CSV v2 import/export, mapping JSON save,
  and runtime reload.

The surface uses a foundation sample provider for UI wiring tests only. It does
not read current `mapping.json` data yet.

## Current UI / Service / Controller Boundary

| Layer | Current responsibility |
| --- | --- |
| `core.mapping.entity_model` | Generic mapping entity/attribute/row/catalog DTOs. |
| `core.mapping.entity_validation` | Generic structural and basic value validation. |
| `apps.train.services.data_mapping_service` | Read-only catalog provider boundary, validation snapshot, disabled future action metadata. |
| `apps.train.controllers.data_mapping_controller` | UI-facing state projection for entity list, attributes, rows, validation, actions. |
| `apps.train.ui.data_mapping_models` | Read-only `QAbstractTableModel` adapter. |
| `apps.train.ui.data_mapping_view_models` | Presentation row/header helpers. |
| `apps.train.ui.data_mapping_panel` | Widget composition and selection/refresh wiring only. |

## What Changed

- Clarified active flag and key-attribute identity semantics in model docstrings.
- Added validation for key attribute value mismatch.
- Added inactive attribute/row validation policy tests.
- Replaced the Train/Admin Data Mapping placeholder with a read-only foundation
  panel.
- Added read-only service/controller/UI model tests and a small offscreen panel
  construction smoke.

## What Did Not Change

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

## Disabled / Future Actions

The UI exposes disabled action metadata for:

- Import CSV v2;
- Export CSV v2;
- Save mapping.json;
- Reload runtime mapping.

These are intentionally disabled because the current slice is read-only.

## MVC / SoC / Hexagonal Assessment

The UI does not parse raw CSV or raw mapping JSON and does not call the legacy
converter. It consumes a controller state created from service snapshots. Core
mapping validation stays Qt-free. The panel owns widget composition only, while
table models are UI adapters and not validation owners.

## Manual GUI Smoke

Manual GUI smoke is required before treating the Data Mapping tab as visually
accepted in a real desktop session. Automated offscreen tests cover table model
data and panel construction but not visual layout quality.

## Remaining Gaps

- Current `mapping.json` is not adapted into `MappingEntityCatalog`.
- CSV v2 loader/exporter is not implemented.
- Editable CRUD is not implemented.
- Safe mapping JSON write/reload policy is not implemented.
- Generic runtime cascade integration remains Arc 14C.
- Full spreadsheet edit/copy/paste parity is not complete because the surface
  is intentionally read-only in this slice.

## Next Action

Arc 14B-2 should implement a runtime mapping repository read adapter first.
Because Arc 14B-1 still uses a foundation sample provider, the next slice should
show current mapping data read-only before editable CRUD or CSV v2 import/export
is added.
