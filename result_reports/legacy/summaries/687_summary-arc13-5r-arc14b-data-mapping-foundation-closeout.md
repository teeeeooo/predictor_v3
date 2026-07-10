# 687 Summary - Arc 13.5R / Arc 14B Data Mapping Foundation Closeout

## Goal

Summarize the Arc 13.5R Predict Schema Catalog v2 owner switch and the Arc
14A/14B Data Mapping foundation workstream, then archive the completed active
reports.

Covered reports:

- `674_pre-arc14-numbering-status-sync.md`
- `675_predict-schema-mapping-foundation-docs.md`
- `676_predict-schema-generic-mapping-design-correction.md`
- `677_arc13-5r-current-predict-schema-inventory.md`
- `678_arc13-5r-predict-schema-v2-field-spec-confirmation.md`
- `679_arc13-5r-readonly-schema-v2-projection-parity.md`
- `680_arc13-5r-projection-owner-switch.md`
- `681_arc13-5r-schema-v2-followup-guards.md`
- `682_arc14a-mapping-entity-master-data-foundation.md`
- `683_arc14b-data-mapping-manager-ui-foundation.md`
- `684_arc14b-data-mapping-entity-list-width-polish.md`
- `685_calculator-ui-tab-color-token-owner.md`
- `686_data-mapping-computer-use-accessibility-stabilization.md`

## Major Decisions

- Arc 14 became the Data Mapping Manager / Mapping Update Execution arc, while
  ML catalog-aligned real dataset readiness moved to Arc 15.
- Predict Schema Catalog v2 is the Predict core column/schema owner. Runtime
  `COLUMNS` assembly now projects from `config/predict/schema.csv`, while
  Feature Catalog remains the ML feature/target/one-hot compatibility source.
- Predict Schema v2 uses generic mapping semantics: `mapping_entity`,
  `mapping_attribute`, `trigger_column`, and `rule_id` are semantic fields;
  legacy `mapping`, `source`, and `mapping_key` remain compatibility projection
  fields for current adapters.
- `template_id`, `slot_id`, and `cascade_role` remain optional preset/group
  helpers, not core schema boundaries.
- One-hot selector behavior is ML input projection concern, not a cascade
  primitive.
- Schema/column/rule changes remain restart-required.
- Mapping Entity / Master Data is a generic Qt-free core model, not an
  IDU/ODU-specific boundary.
- Predict Schema Catalog v2 owns Predict column/schema metadata; Mapping Entity
  Model owns mapping row/master data.
- Existing `mapping.json` repository, converter, and runtime autofill/cascade
  paths remain compatibility owners until later execution slices.
- Data Mapping Manager currently has a read-only Train/Admin UI foundation with
  disabled future action metadata for CSV v2 import/export, mapping JSON save,
  and runtime reload.
- Data Mapping row identity is `row_key`; `key_attribute` is the import/export
  and UI header for that identity. Row values may omit the key attribute, but if
  present the trimmed value must match `row_key`.
- `active` is management visibility/eligibility metadata. Structural validation
  still runs regardless of active status; inactive attributes and rows are
  skipped only for required/type value validation.

## Runtime Behavior

- Predict UI and adapter behavior was intended to stay behavior-compatible
  through the schema owner switch.
- `status` and `message` remain adapter-local virtual columns, not core
  `COLUMNS` entries.
- Current dropdown/autofill, ODU cascade, one-hot ML projection, and mapping
  JSON read behavior remain compatibility paths, not the new generic rule
  engine.
- Data Mapping UI uses a sample provider for read-only foundation wiring. It
  does not yet display repository-backed `mapping.json` data.
- Data Mapping table surfaces use Qt table models and explicit accessibility
  names/object names for external inspection.

## Corrections And Stabilization

- The Predict Schema foundation docs were corrected so IDU-Evap and ODU-Cond
  are representative presets/examples, not fixed core schema boundaries.
- Read-only schema v2 projection parity covered the current core column count,
  order, header/group/dropdown/read-only metadata, mapping compatibility fields,
  one-hot groups, and status/message exclusions.
- Follow-up guards added explicit current core schema snapshots and Feature
  Catalog ML-visible alignment checks so owner switch protection is not only
  self-referential.
- Data Mapping entity list width was widened and guarded by a focused UI
  construction test.
- Calculator UI selected tab color ownership moved to the existing visual token
  owner, resolving the raw hex literal structure guard error.
- Data Mapping refresh/selection churn was reduced, and accessibility metadata
  was added, but Computer Use still crashed the Python/Qt app while reading the
  macOS accessibility hierarchy.

## Excluded Scope

- No Train/Predict shell merge.
- No Data Mapping CRUD.
- No CSV v2 import/export implementation.
- No mapping JSON write/update execution.
- No generic runtime cascade engine.
- No IDU Size -> Evap Index filter.
- No one-hot adapter owner switch.
- No ML training/retraining/model artifact changes.
- No Predict UI behavior change intended beyond owner-compatible schema
  projection.
- No broad code-map regeneration.

## Validation

- Arc 13.5R slices ran focused Predict Schema Catalog v2 loader/projection,
  Predict schema adapter, case-table adapter, mapping-backed dropdown,
  prediction adapter, and core mapping autofill tests recorded in the source
  reports.
- Arc 14A/14B slices ran focused core mapping entity model/validation,
  Train/Admin Data Mapping service/controller/UI model, Feature Catalog, and
  mapping dropdown/autofill tests recorded in the source reports.
- Lifecycle cleanup validation:
  - `git diff --check`: OK.
  - Active report count is below lifecycle threshold after archive movement.
  - Memory seed summary registration and compact durable entries were updated.
- Known weaker verification:
  - `tools/code_checker/build_reference_map.py --check` remained stale in
    source reports and was not regenerated for this lifecycle cleanup.
  - Computer Use onscreen smoke for Data Mapping remained NG due to a macOS
    AppKit/Qt accessibility crash.

## Lifecycle

- Covered active reports are archived under `result_reports/archive/`.
- This summary is registered in `result_reports/memory/project_memory_seed.md`.
- Memory seed gained compact durable entries for the Predict Schema v2 owner
  switch and Data Mapping foundation state.

## Project Memory Seed Sync Judgment

- Registered under Source Coverage because this is a summary lifecycle task.
- Added summary-level durable decision/error entries because later Predict
  schema and Data Mapping work depends on the owner split, current
  compatibility boundaries, and unresolved Computer Use accessibility failure.

## Next Action

Arc 14B-2 - Data Mapping runtime mapping repository read adapter. The current
read-only UI foundation should display current mapping data before editable CRUD
or CSV v2 import/export work proceeds.
