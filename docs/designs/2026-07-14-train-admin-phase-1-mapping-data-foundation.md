# Train/Admin Phase 1 — Mapping/Data Foundation

Status: implemented; audit correction pending final re-audit
Date: 2026-07-14  
Depends on: Train/Admin UI/UX Overhaul Governing Design

## 1. Goal

Create the stable data foundation required to redesign Data Mapping and Data
Definition with meaningful populated states.

This phase establishes:

- a strict one-time bootstrap path from the legacy wide mapping fixture;
- repository-safe runtime-equivalent mapping fixture data;
- dynamic mapping attribute projection and persistence;
- consistency between schema fixtures, mapping fixtures, and mock training data;
- validation evidence that the current runtime and editor boundaries can support
  the later UI overhaul.

This phase is not the visual overhaul itself.

## 2. Current Problem

The default repository checkout may not contain `data/mapping.json`, so Data
Mapping is often limited to an empty/error state. This prevents reliable UX
design and validation of the actual editing workflow.

The mapping editor also contains fixed assumptions, especially around ODU
condenser specification attributes. A future attribute such as
`Cond Inner Area` must be defined in Data Definition and then appear and persist
through Data Mapping without hard-coded column changes.

The repository intentionally lacks real company data, so fixtures and mock data
must form a structurally coherent validation set.

## 3. Confirmed Decisions

- The legacy wide CSV is bootstrap-only.
- Current fixture values are synthetic validation data.
- Fixture structure, relationships, names, and types mirror the real local contract.
- The bootstrap is a migration/parser path, not a normal Import button.
- Bootstrap output must pass current editor/runtime validation.
- Mapping values remain owned by `mapping.json` and Data Mapping.
- Mapping attribute definition remains owned by Data Definition.
- Dynamic attributes must survive projection, display, validation, save, reload,
  and export without special-case loss.
- No production-readiness or model-quality claim may be made from mock data.

## 4. Legacy Bootstrap Contract

### Input

```text
tests/fixtures/mapping/mapping_tables_legacy_wide.csv
```

### Output

A runtime-equivalent mapping object or fixture that can be projected into the
existing Data Mapping editor and, when a write is requested, persisted through
the existing validated save path.

### Explicit block mapping

| Legacy block | Runtime/editor target |
| --- | --- |
| `Compressor`, `EER`, `cc` | `compressor` |
| `Size`, `Evap Index`, `Evap area`, `Evap Volume` | `evap_index` |
| `IDU`, `Volume`, `Size` | `idu` |
| first `ODU`, `Volume` block | `odu` |
| second `ODU`, `Fin type`, `Pi`, `Row`, condenser values | ODU condenser-spec editor group and derived runtime sections |
| `Ref type` | refrigerant option group / `ref_type` |
| `Exp type` | expansion option group / `exp_type` |

### Alias rules

```text
EER          -> Comp EER
cc           -> Comp cc
Evap area    -> Evap Area
IDU Volume   -> ID Volume
ODU Volume   -> OD Volume
Fin type     -> Fin Type
```

### Condenser identity rule

Runtime condenser identity is conditional on Fin Type:

```text
F&T: ODU + Fin Type + Pi + Row
PFC: ODU + Fin Type + Row
```

The legacy PFC value in the fixed `Pi` column is a layout placeholder and is
normalized to an absent Pi value. Runtime/editor projection must not duplicate
`PFC` into both Fin Type and Pi or create an `ODU PFC PFC Row` key.

`Cond Index` is a legacy Excel VLOOKUP helper column. It is required as part of
the recognized legacy layout but is ignored during bootstrap normalization; it
is neither a runtime identity source nor consistency-validation evidence.

### Strictness

Bootstrap rejects:

- duplicate primary keys;
- duplicate condenser combinations;
- invalid numeric values;
- unexpected or missing layout/header contracts;
- duplicate conditional condenser identities.

Rows with a blank key for one block are ignored only for that block, because the
legacy file stores multiple independent tables side by side.

`Pi`, `Row`, identifiers, and option values remain strings unless the current
owned contract requires otherwise.

## 5. Projection and Persistence Direction

Preferred direction:

```text
legacy parser
    -> editor draft or equivalent owned intermediate
    -> existing editor validation
    -> existing runtime mapping projection
    -> atomic save when a write is requested
```

Do not create a parallel JSON writer that can drift from Data Mapping persistence.

Audit and correct fixed-field behavior where ODU Cond Specs currently retains
only known fields such as `Cond Area` and `Cond Volume`.

## 6. Dynamic Mapping Attribute Foundation

A Data Definition requirement may add an attribute to an existing group.

Example:

```text
Group: ODU Cond Specs
Attribute: Cond Inner Area
Type: Number
Required: Optional or Required according to definition
```

The foundation must support:

1. The definition requirement reaches the correct mapping group.
2. The group exposes the additional column.
3. Existing rows receive an empty value unless data exists.
4. Validation distinguishes optional empty from missing required values.
5. Save retains the attribute in the owned runtime section.
6. Reload restores it.
7. Export includes it automatically.
8. Existing unowned runtime sections remain preserved under current policy.

The same definition-backed payload contract applies to the Refrigerant and
Expansion option groups. Their runtime section keys remain the Predict option
identity, while declared payload attributes are restored, edited, validated,
persisted, reloaded, and exported. Raw payload keys remain row backing data but
do not become visible columns or schema unless Data Definition declares them.

Undeclared runtime row payload is existing data, not schema, and is not deleted
by an unrelated edit or Save. Persistence begins from the current editor row's
backing payload, removes only that group's key/identity control fields, and then
overlays visible definition-backed values using their canonical types. Visible
values are authoritative, including an optional visible field deliberately set
to empty. Hidden payload follows its row through rename/reorder/duplicate and
is removed only when that row is deleted; persistence never re-reads an old
`source_key` and therefore cannot retain both old and renamed runtime keys.

This preservation policy applies to IDU, Evap Index, ODU, Compressor,
Refrigerant, Expansion, and ODU Cond Specs. Hidden payload remains absent from
Data Mapping columns and JSON/XLSX review exports. If Data Definition later
declares the same attribute, the preserved backing value becomes visible.

Definition-backed `boolean` values use canonical JSON booleans. Actual booleans
and the explicit case-insensitive `true`/`false`, `1`/`0`, and `yes`/`no`
representations are accepted; ambiguous values are rejected. Required `False`
is present and valid. Every built-in or dynamic numeric mapping value must be a
finite JSON number, so NaN and positive/negative infinity are rejected before
atomic persistence. Validation and persistence share these coercion policies.

Data Mapping edits values for the attribute; it does not define the attribute.

## 7. Fixture and Mock Data Contract

Treat the following as one validation set:

```text
schema fixture
+ mapping fixture
+ mock training data
```

The set must remain consistent in these dimensions:

- mapping-backed values used by mock training rows exist in mapping fixtures;
- ODU/Fin/Pi/Row combinations used by mock data exist in condenser mappings;
- schema names, order, roles, and types match mock training headers;
- one-hot selectors and emitted mock features follow the active compatibility contract;
- mapped numeric values use expected types;
- mock model/training workflows preserve feature names and order.

Mock values need not reproduce real thermodynamic distributions unless a later
test explicitly requires synthetic trend behavior.

## 8. Implementation Slices

### Slice 1A — Bootstrap rule finalization and parser

- Implement the strict legacy-wide parser.
- Produce deterministic, validated mapping output.
- Cover aliases, blank-block rows, duplicates, numeric failures, and condenser
  conditional identity normalization.
- Ignore `Cond Index` values while preserving the required legacy layout.
- Do not expose normal Train/Admin import.

### Slice 1B — Populated mapping fixture state

- Establish repository-safe populated mapping data for UI and integration tests.
- Prove all seven user-facing mapping groups can be projected and displayed.
- Keep fixture data separate from production/default user data.
- Store the deterministic runtime-equivalent projection at
  `tests/fixtures/mapping/mapping_runtime_equivalent.json` and compare it
  exactly with the approved bootstrap output so projection drift is visible.
- Use that same fixture path for Data Mapping and Predict integration tests;
  never install it as `data/mapping.json`.

### Slice 1C — Dynamic attribute round-trip

- Remove fixed-attribute loss from ODU condenser and other affected paths.
- Prove definition-required attributes appear, validate, save, reload, and export.
- Preserve existing runtime cascade behavior.
- Carry Data Definition `data_type` and `required` metadata on the mapping
  requirement and editor group so validation, presentation metadata, and
  persistence share the same definition-owned contract.
- Preserve runtime payload values for later requirement-backed projection, but
  never turn unknown raw attributes into editor columns without a requirement.
- Merge persistence from current row backing payload and visible canonical
  overlays so undeclared runtime values survive unrelated save/reload cycles.
- Persist every non-identity ODU Cond Specs column from the editor group;
  condenser identity remains limited to ODU, Fin Type, canonical Pi, and Row.
- Preserve and round-trip Data Definition-backed Refrigerant/Expansion payload
  attributes without changing their key-based Predict option contract.
- Persist boolean attributes as canonical JSON booleans and accept only finite
  values for every built-in or definition-backed numeric mapping field.

### Slice 1D — Cross-fixture consistency

- Add structural checks linking schema, mapping, and mock training data.
- Prove the mock training pipeline can consume the projected contract.
- Keep model quality outside the result.
- Keep selector rows as DEV validation metadata paired by row with the existing
  numeric/one-hot training frame; do not add selector columns to the strict ML
  training-header contract.
- Resolve every mapping-backed numeric and one-hot value from the Slice 1B
  runtime-equivalent fixture, including both F&T and PFC condenser rows.
- Fail fast on invalid base options, invalid condenser combinations,
  Fin-Type-dependent Pi violations, missing schema-backed attributes, and
  training values that differ from their mapping resolution.

Each slice is one logical commit and is pushed to the phase branch. The phase is
merged only after all slices and phase acceptance checks pass.

## 9. Acceptance Scenarios

- Legacy fixture produces deterministic runtime-equivalent mapping rather than a
  generic `Sheet1` result.
- Data Mapping opens with all seven populated fixture-backed groups.
- A definition-owned `Cond Inner Area` appears, accepts values, survives
  save/reload, and exports without special-case code.
- Duplicate keys, duplicate conditional condenser identities, invalid numerics,
  and malformed layouts fail with exact block/row context.
- PFC condenser rows project without a Pi selection or duplicated PFC key segment.
- Mock training consumes only valid mapping options and the active projected
  schema with preserved feature order and types.
- Refrigerant/Expansion declared payload values round-trip while undeclared raw
  payload keys remain hidden and do not create schema.
- Invalid booleans and non-finite built-in or dynamic numbers block Save without
  replacing the existing mapping file.
- Undeclared row payload survives edit/save/reload and key rename without
  becoming a visible/exported column; row deletion removes its payload.
- A non-finite value already present in hidden payload fails atomic Save instead
  of being silently discarded or written as non-standard JSON.

## 10. Validation Purpose

This phase proves that later UI work has stable representative data and that the
definition/value boundary supports dynamic fields.

It does not prove real mapping correctness, production completeness, model
accuracy, or production readiness.

## 11. Non-goals

- Data Mapping visual overhaul.
- Data Definition wizard implementation.
- Mapping bundle export/import.
- Real company data migration in the repository.
- Automatic retraining.
- Schema live reload.
- General-purpose legacy CSV import.
- Calculator changes.

## 12. Phase 1 Closeout

Phase 1 is complete for repository-automated scope on Draft PR #14 and remains
unmerged pending final audit.

- The checked-in populated mapping is synthetic runtime-equivalent fixture
  evidence, not production mapping truth.
- Data Definition-backed dynamic attributes carry type/required metadata and
  round-trip through Data Mapping projection, validation, persistence, reload,
  and review export without entering condenser identity.
- That round-trip includes Refrigerant/Expansion option payloads while Predict
  continues to consume section keys as options; undeclared raw payload remains
  hidden, survives persistence from its editor row backing data, and never
  auto-creates schema or review-export columns.
- Boolean attributes persist as canonical JSON booleans and all mapping numbers
  are finite; invalid boolean or NaN/infinite inputs block atomic Save.
- The aligned validation set links the active schema, repository mapping
  fixture, DEV selector metadata, and unchanged ML training headers.
- Phase 2 Data Mapping UX, later Train/Admin phases, production migration, and
  real-data/model-quality work remain outside this closeout.
- Company-local follow-up must validate real mapping completeness, real
  training headers/values, actual training execution, accuracy, physical
  behavior, feature quality, model artifacts, and production readiness.
