# Arc 14B-2 - Runtime Mapping Repository Read Adapter

## Goal

Show the current runtime mapping repository through the read-only Data Mapping
Manager surface instead of the foundation sample provider.

## Boundary

- Runtime loading stays owned by `core.mapping.repository.load_mapping_data()`
  and `core.mapping.paths.MAPPING_JSON_FILE`.
- The adapter is Qt-free and lives in `core.mapping.entity_runtime_adapter`.
- Train UI consumes `DataMappingService` and `DataMappingController`; it does
  not parse raw JSON.
- `FoundationMappingCatalogProvider` remains an explicit test/fallback provider.

## Runtime Mapping Shape Summary

- Default path: `data/mapping.json` via `core.mapping.paths.MAPPING_JSON_FILE`.
- This checkout does not currently contain `data/mapping.json`; missing or empty
  runtime data is surfaced as a load error instead of falling back to samples.
- Runtime loader shape is a top-level JSON object of section/table keys.
- Typical sections are table-shaped dictionaries such as `idu`, `odu`,
  `compressor`, `odu_cascade`, and `cond_specs`.
- Row identity is the nested dictionary key. `cond_specs` uses a composite row
  key such as `ODU-A F&T 7 1`.
- Row values are usually dictionaries of attribute keys to scalar values. The
  cascade section also stores list values such as available fins, pis, and rows.
- Nested dictionaries are not flattened; affected rows record a note.

## Adapter Rules

- `entity_key` is the runtime section key.
- `label` is a readable label derived from the section key while preserving the
  original key.
- `key_attribute` is `<section_key>_key`; row identity remains `row_key`.
- Attribute keys are collected deterministically from row values.
- Attribute type inference is conservative: boolean, number, then string.
- Required is always false unless a future metadata owner supplies stronger
  evidence.
- Rows preserve visible runtime values and are active by default.
- The catalog is validated with the existing `validate_mapping_entity_catalog()`
  path through `DataMappingService.load_snapshot()`.

## DataMappingService Default Provider Change

`DataMappingService()` now defaults to `RuntimeMappingCatalogProvider`. Tests
that depend on the foundation sample explicitly inject
`FoundationMappingCatalogProvider`.

## Read-only Scope

The runtime adapter only reads repository data and creates an in-memory
`MappingEntityCatalog`. It does not save, mutate, reload, or normalize
`mapping.json`.

## Disabled Future Actions

These actions remain disabled:

- Import CSV v2
- Export CSV v2
- Save mapping.json
- Reload runtime mapping

## UI Smoke Result

Focused offscreen UI tests passed with explicit foundation provider injection.
Onscreen runtime-data smoke is bounded by the missing `data/mapping.json` in
this checkout; a temp runtime provider smoke can render data without writing the
production mapping file.

## Arc 14B-2F Follow-up

Runtime source failure visibility:

- `DataMappingService.source_label` exposes the configured provider source
  before loading.
- `DataMappingController` preserves that source label on load failure so the UI
  shows which runtime mapping path failed.
- The load failure message remains separate from source display and includes
  the useful path/context from the runtime adapter.
- Missing or empty runtime mapping data still does not fall back to the
  foundation sample provider.

Row identity display policy:

- Internal catalog identity remains `MappingEntityRow.row_key`.
- Entity `key_attribute` remains part of the catalog definition for future
  import/export/edit semantics.
- The read-only row value table uses one visible identity column: `Row Key`.
- The controller omits the selected entity `key_attribute` from row value
  headers, avoiding an adjacent empty duplicate identity column.

Open Arc 14B-3 decision:

- Editable CRUD and CSV v2 export/import must decide whether persisted row-data
  formats include key attributes explicitly or derive them from row identity.
  This follow-up only defines read-only UI display behavior.

## Excluded Scope

- No mapping.json write/save implementation.
- No CSV v2 import/export.
- No runtime reload.
- No editable CRUD.
- No cascade runtime integration.
- No Predict Schema Catalog or Feature Catalog changes.
- No UI layout rewrite.
- No initial entity `selectRow()` restoration.

## Next Action

Arc 14B-3 should implement either editable CRUD boundaries or the CSV v2
loader/exporter, with the chosen write/reload policy decided before touching
runtime persistence.
