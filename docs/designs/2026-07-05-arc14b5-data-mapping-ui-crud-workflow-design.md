# Arc 14B-5A - Data Mapping UI CRUD Workflow Design

Status: active reference

## Goal

Define the user-facing Data Mapping Manager CRUD workflow before implementation.
The manager is a Predict input mapping administration screen: it manages
dropdown options, autofill source values, and ODU condition options used by the
Predict workspace.

This design does not implement UI, editing, import, export, save, reload,
runtime cascade integration, schema changes, tests, fixtures, or `mapping.json`
writes.

## Design Principles

- Users edit mapping groups, not raw `mapping.json` sections.
- The main screen is not a generic low-level entity/attribute/value editor.
- The main screen is not a spreadsheet export/import editor.
- Import is excluded from the editable workflow unless a future explicit
  compatibility parser is designed.
- Export is a read-only review snapshot, not a file that users edit and import
  back.
- `mapping.json` is the SSOT for all mapping-backed Predict dropdown options.
  Hard-coded Predict dropdown fallback options are legacy behavior and should
  be removed.
- The UI does not parse or write raw JSON. Core/service boundaries own runtime
  JSON projection, validation, save, reload, and export workflows.
- Keep the first editable workflow small: one draft, one selected group table,
  one Issues surface, validation-gated Save.

The complex package-style import/export direction is superseded because it
asks users to keep multiple files or implicit section relationships aligned by
memory. The UI workflow should make the relationships visible and let the app
generate the internal runtime shape.

## User-facing Workflow

The user opens the Data Mapping tab, sees the active mapping file, chooses a
group, edits rows in a simple table, reviews Issues, and saves only when there
are no blocking issues.

User-facing groups:

- IDU
- Evap Index
- ODU
- Compressor
- Refrigerant
- Expansion
- ODU Cond Specs

These group names are the user contract. Internal sections such as
`odu_cascade`, `cond_specs`, `fin_type`, `pi`, and `row` are generated from the
ODU Cond Specs group and should not be exposed as separate edit targets.

## Main Screen Structure

Main toolbar:

- `Save`
- `Reload`
- `Export`

Import should be removed from the first editable toolbar or left long-term
disabled with wording that it is not available.

Status messages:

- `Ready.`
- `Issues found.`
- `Unable to load data.`
- `Unsaved changes.`

File display:

- `File: data/mapping.json`

Main layout:

| Region | Content |
| --- | --- |
| Left | `Groups` list with the user-facing groups above. |
| Right | `Data` table for the selected group. |
| Lower panel | `Issues` table with user-fixable problems. |

`Fields` should not be a prominent main editing table. If implementation needs
metadata, place it in a small detail/help area for the selected group. Editable
tables should avoid the term `Row Key`; the first visible column should use the
domain label such as `IDU`, `Evap Index`, `ODU`, or `Compressor`.

## User-facing Groups

| Group | User edits | Runtime section(s) |
| --- | --- | --- |
| IDU | IDU options and IDU-derived specs. | `idu` |
| Evap Index | Evap options and evaporator specs. | `evap_index` |
| ODU | ODU options and ODU-derived specs. | `odu` |
| Compressor | Compressor options and compressor specs. | `compressor` |
| Refrigerant | Refrigerant options. | `ref_type` |
| Expansion | Expansion-device options. | `exp_type` |
| ODU Cond Specs | ODU-specific fin/pi/row combinations and condenser specs. | `odu_cascade`, `cond_specs`, `fin_type`, `pi`, `row` |

## Group Table Contracts

| Group | Columns | Maps to |
| --- | --- | --- |
| IDU | `IDU`, `ID Volume`, `Size` | `idu` |
| Evap Index | `Evap Index`, `Size`, `Evap Area`, `Evap Volume` | `evap_index` |
| ODU | `ODU`, `OD Volume` | `odu` |
| Compressor | `Compressor`, `Comp EER`, `Comp cc` | `compressor` |
| Refrigerant | `Refrigerant` | `ref_type` |
| Expansion | `Expansion` | `exp_type` |
| ODU Cond Specs | `ODU`, `Fin Type`, `Pi`, `Row`, `Cond Area`, `Cond Volume` | derived sections listed below |

Decision: Refrigerant and Expansion are normal mapping groups owned by
`mapping.json`, not fallback-backed options.

- Refrigerant projects to the required `ref_type` section.
- Expansion projects to the required `exp_type` section.
- Predict dropdowns must read `ref_type` and `exp_type` from `mapping.json`
  only.
- Missing or empty `ref_type` / `exp_type` sections are validation issues.
- The current hard-coded Predict dropdown fallback options are legacy behavior
  and should be removed in implementation.

## ODU Cond Specs Derived Mapping

Users edit one ODU Cond Specs table:

| ODU | Fin Type | Pi | Row | Cond Area | Cond Volume |
| --- | --- | --- | --- | --- | --- |
| ODU-A | F&T | 7 | 1 | 10 | 10 |
| ODU-A | F&T | 7 | 2 | 20 | 15 |
| ODU-B | PFC | PFC | 1 | 39 | 50 |

Save projection generates these runtime sections:

- `odu_cascade`
- `cond_specs`
- `fin_type`
- `pi`
- `row`

`odu_cascade` generation:

- group rows by `ODU`;
- collect unique nonblank `Fin Type` values as sorted `Available_Fins`;
- collect unique nonblank `Pi` values as sorted `Available_Pis`;
- collect unique nonblank `Row` values as sorted `Available_Rows`.

`cond_specs` generation:

- key = `"{ODU} {Fin Type} {Pi} {Row}"`;
- value = `{"Cond Area": <value>, "Cond Volume": <value>}`.

Base option section generation:

- `fin_type`: unique nonblank `Fin Type` values;
- `pi`: unique nonblank `Pi` values;
- `row`: unique nonblank `Row` values.

Users do not edit `Available_Fins`, `Available_Pis`, `Available_Rows`, or the
composite key directly. Duplicate composite keys are blocking issues.

## CRUD Behavior

Add Row:

- Adds one empty draft row in the selected group.
- For ODU Cond Specs, the `ODU` cell should eventually use ODU group values as
  dropdown options.

Duplicate:

- Copies the selected row into a new draft row.
- Any key or composite-key collision appears in Issues.

Delete:

- Removes the selected draft row.
- References from other groups are checked by validation and shown in Issues.

Edit Cell:

- Applies immediately to the draft.
- Re-runs validation.
- Sets dirty state to true.

Save boundary:

- Draft changes do not touch runtime `mapping.json` until Save succeeds.

Undo is outside the first editable slice. Keep it as an open question rather
than designing it into the initial implementation.

## Issues and Validation

Issues are a user repair list, not a developer log. Default UI columns:

| Column | Purpose |
| --- | --- |
| Level | Error or warning if warnings are introduced. |
| Group | User-facing group name. |
| Row | User-facing row label/key. |
| Field | User-facing column name. |
| Message | Actionable issue text. |

Internal codes may remain in debug/report data, but should be hidden by default
in the main Issues table.

Common blocking issues:

- blank key;
- duplicate key;
- required field missing;
- invalid number;
- referenced row missing.
- missing or empty required section, including `ref_type` and `exp_type`.

ODU Cond Specs blocking issues:

- `ODU` is not present in the ODU group;
- duplicate `ODU + Fin Type + Pi + Row` combination;
- `Cond Area` or `Cond Volume` blank;
- `Cond Area` or `Cond Volume` numeric invalid;
- `Fin Type`, `Pi`, or `Row` blank.

Save enable policy:

- no blocking issue -> Save enabled;
- any blocking issue -> Save disabled.

Open question: whether the first implementation needs both warning and error
levels, or whether every issue can start as blocking.

## Save / Reload / Export / Import Policy

Save:

- enabled only after validation passes;
- create a backup of the existing `mapping.json`;
- write a temp file;
- atomically replace the runtime file;
- set dirty to false after success;
- never let the GUI layer write raw JSON directly.

Reload:

- discards the current draft and reloads `mapping.json`;
- if dirty is true, require confirmation;
- suggested unsaved-change wording: `Unsaved changes will be discarded. Reload
  from file?`

Export:

- read-only review snapshot;
- not an edit/reimport contract;
- XLSX workbook snapshot is the best human-review candidate;
- pretty JSON snapshot is the exact backup/debug candidate;
- implementation belongs to a later slice.

Import:

- excluded from this workflow;
- if required later, design an explicit compatibility parser as its own slice.

## Internal Boundary

Candidate responsibilities for implementation. Names below are suggestions, not
approved public APIs.

| Layer | Owns |
| --- | --- |
| `core/mapping` | Runtime JSON load/save owner, editor draft model candidate, draft to runtime JSON projection, runtime JSON to draft projection, validation, ODU Cond Specs derived section generation. |
| `apps/train/services` | Load draft, apply edit commands, provide validation result, dirty state, save/reload/export workflow. |
| `apps/train/controllers` | Convert service state into UI table state and forward UI commands. |
| `apps/train/ui` | Display, selection, cell editing, and buttons only. No raw JSON parse/write. |

Possible helper/model names for a future implementation:

- `MappingEditorDraft`
- `MappingUserGroup`
- `MappingUserRow`
- `RuntimeMappingProjection`
- `OduCondSpecsProjection`
- `DataMappingEditCommand`

These names are placeholders to guide boundary thinking. The next code slice
should still choose names that fit the actual module/package split.

## Implementation Slices

| Slice | Scope |
| --- | --- |
| Arc 14B-5B | Editor draft projection: runtime `mapping.json` -> user-facing groups, read-only projection only; include required `ref_type` / `exp_type` projection and remove Predict dropdown hard-coded fallback behavior. |
| Arc 14B-5C | Draft validation, Issues generation, and Save enable judgment only. |
| Arc 14B-5D | Editable table commands: Add Row, Duplicate, Delete, Edit Cell, dirty state. Save may remain disabled. |
| Arc 14B-5E | Save with backup and atomic write. |
| Arc 14B-5F | Export read-only snapshot. |

Import remains excluded until an explicit future compatibility-parser decision.

## Excluded Directions

- Raw `mapping.json` editor.
- Generic entity/attribute/value editor as the main UX.
- CSV import/export contract.
- Multi-file import/export package.
- Normalized `values.csv`.
- Export-edit-reimport workflow.
- Runtime cascade integration.
- Predict Schema Catalog or Feature Catalog changes.
- Production code, tests, fixtures, or schema changes in this design slice.

## Open Questions

- Should warnings exist in the first editable implementation, or should all
  issues start as blocking?
- Should Undo be a later command stack, or should early slices rely on Reload
  and unsaved draft discard?
- Should the first Export implementation ship XLSX only, JSON only, or both?

## Next Action

Arc 14B-5B - implement editor draft projection from runtime `mapping.json` to
the seven user-facing groups in read-only mode, with `ref_type` / `exp_type`
owned by mapping data and Predict dropdown fallback options removed.
