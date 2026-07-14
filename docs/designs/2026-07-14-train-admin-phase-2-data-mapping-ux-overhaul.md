# Train/Admin Phase 2 — Data Mapping UX Overhaul

Status: active — Slice 2A audit corrections and native evidence complete; re-audit pending
Date: 2026-07-14  
Depends on: Phase 1 — Mapping/Data Foundation

## 1. Goal

Replace the current Data Mapping surface with a production-usable value management
workflow built around populated groups, spreadsheet-quality editing, clear
validation, safe persistence, and human-friendly exchange files.

The user should manage mapping values without reading raw JSON and without
confusing structural changes with value changes.

## 2. Target User Workflow

```text
select mapping group
    -> inspect/filter rows
    -> edit or paste values
    -> resolve field-level issues
    -> optionally export/import exchange data
    -> review dirty state and changes
    -> Save mapping.json
    -> confirm runtime/reload state
```

The default view prioritizes the selected group's table and immediate actions.

## 3. Information Architecture

The implementation may substantially replace the current layout. The target
surface should contain:

- group navigation with row/issue/dirty indicators;
- primary spreadsheet-like mapping table;
- focused toolbar for add, duplicate, delete, import, export, save, reload, and
  undo/redo where supported;
- concise source and status information;
- validation summary with issue-to-cell navigation;
- contextual field/definition details in a secondary or collapsible region;
- explicit empty, missing-resource, load-error, and populated states.

Internal field diagnostics must not dominate the default workspace.

## 4. Required Group Behavior

The seven user-facing groups remain:

1. IDU
2. Evap Index
3. ODU
4. Compressor
5. Refrigerant
6. Expansion
7. ODU Cond Specs

Group selection remains stable after refresh, validation, row edits, and
non-destructive state updates whenever the group still exists.

Columns come from the current editor/definition contract and are not separately
hard-coded in the panel. A definition-added attribute such as `Cond Inner Area`
appears automatically.

ODU Cond Specs has conditional Pi editing behavior:

- a PFC row renders its Pi cell read-only or disabled;
- changing Fin Type from F&T to PFC immediately clears the existing Pi value;
- paste and inline edit cannot insert a Pi value into a PFC row;
- every Fin Type other than PFC keeps Pi editable and required by default;
- core PFC Pi normalization remains mandatory independently of these UI guards.

## 5. Spreadsheet Interaction

Editable tables follow the active spreadsheet UX contract as applicable:

- cell and rectangular selection;
- TSV copy/paste;
- single-column multi-row paste;
- Delete/Backspace clear;
- grouped undo for edit/paste/clear;
- Tab/Enter and shifted navigation;
- arrow navigation outside edit mode;
- replace-on-type and partial-edit entry;
- read-only mutation prevention;
- invalid and empty states distinguished;
- responsive sizing.

Paste validation uses the same column rules as inline edits.
Pasting across ODU Cond Specs must skip or reject mutation of a PFC Pi cell
without shifting values into adjacent cells.

## 6. State and Action Semantics

### Dirty state

Show whether the draft differs from the loaded source and, where practical, the
number of affected rows or cells.

### Refresh

Refreshes rendered or derived state without replacing the in-memory draft.

### Reload from file

Reads the mapping source and discards the current draft only after explicit
confirmation when dirty.

### Save

- saves only a valid draft;
- preserves atomic write and backup behavior;
- reports destination and backup outcome;
- keeps issues actionable;
- does not imply definition changes are live when restart is required.

### Issues

Each issue identifies severity, group, row, field, and corrective message.
Selecting it focuses the corresponding group and cell when possible.

## 7. Mapping Exchange Export

One export operation creates seven group-wide CSV files and one sectioned bundle
CSV from the same in-memory draft:

```text
idu.csv
evap_index.csv
odu.csv
compressor.csv
refrigerant.csv
expansion.csv
odu_cond_specs.csv
<user-selected bundle name>.csv
```

The implementation selects an appropriate folder/package workflow after auditing
current UI conventions. The bundle file name is never the format contract.

### Group CSVs

Each group file is a conventional rectangular CSV whose headers match current
user-facing columns.

```csv
Compressor,Comp EER,Comp cc
Comp A,3.5,13
```

```csv
ODU,Fin Type,Pi,Row,Cond Area,Cond Volume,Cond Inner Area
N-V2MD,F&T,7,1,10,10,8.5
```

Dynamic definition-owned attributes appear as ordinary columns.

### Bundle CSV

```csv
__FORMAT__,mapping_bundle_v1

__SECTION__,compressor
Compressor,Comp EER,Comp cc
Comp A,3.5,13

__SECTION__,odu_cond_specs
ODU,Fin Type,Pi,Row,Cond Area,Cond Volume
N-V2MD,F&T,7,1,10,10
```

Rules:

- users may choose any valid file name;
- import does not inspect the file name for identity or version;
- `mapping_bundle_v1` is the format version;
- section identity is explicit and independent of header guessing;
- section order is not semantically significant;
- blank lines are allowed for readability;
- standard CSV quoting must preserve commas and text safely.

## 8. Mapping Exchange Import

Initial official input is the sectioned bundle format.

```text
select file
    -> detect internal format/version
    -> parse sections
    -> validate structure and values
    -> show replacement/change preview
    -> apply to unsaved Data Mapping draft
    -> user reviews and Saves
```

Import never directly writes `mapping.json`.

Block import without changing the current draft when the bundle contains:

- missing or unsupported format marker;
- duplicate or unknown sections;
- missing required sections under the selected snapshot policy;
- unknown columns;
- duplicate primary keys;
- duplicate condenser combinations;
- invalid types or required values;
- malformed CSV.

Unknown columns are not treated as new definitions. The user is directed to
Data Definition.

Initial import is full-snapshot replacement. Automatic merge, individual group
CSV import, and implicit schema creation are deferred.

Before applying a valid import, show meaningful counts such as groups affected,
rows added, rows removed, rows changed, and blockers or warnings.

## 9. Visual Direction

The surface should feel like a focused engineering data editor rather than an
internal diagnostics console.

Required qualities:

- primary table dominance;
- consistent table/header treatment;
- compact readable toolbar;
- clear selected group;
- restrained status color usage;
- intentionally designed empty/loading/error states;
- technical metadata available without occupying the main editing area;
- dialogs and banners consistent with later Train/Admin phases.

Reusable common PySide6 components are preferred over panel-specific styling.

## 10. Implementation Slices

### Slice 2A — Populated-state information architecture

- Restructure the panel around group navigation and the primary table.
- Preserve group selection and draft state.
- Implement clear normal, empty, missing-resource, and error states.

Implemented on `phase/train-admin-data-mapping-ux`:

- concise group navigation with label, row count, and selected state;
- dominant definition-backed primary mapping table;
- compact status/source/action area and collapsible secondary field/issue details;
- distinct populated, empty-group, missing-resource, and load-error surfaces;
- selection-preserving non-destructive refresh and current-draft projection;
- repository-fixture-backed offscreen verification for representative states.

Audit correction on Draft PR #15 additionally establishes:

- cached service-owned drafts remain visible and dirty when source availability
  changes to missing;
- Refresh reprojects current state without provider reload, while Reload retains
  provider-read semantics and preserves the draft on failure;
- empty-message load/reload exceptions use a stable class-name fallback;
- native macOS onscreen evidence for populated, dynamic, empty, missing,
  load-error, dirty-source-missing, compact, and collapsed-detail states under
  `assets/train-admin-phase2-slice2a-native-audit/`;
- safe deferred view reprojection after Qt delegate commit.

The panel and controller exceed the structure guard's 400 LOC soft limit. The
correction extracted status/workspace presentation policy into the existing UI
model owner. Before Slice 2B adds spreadsheet interaction, split toolbar/action
composition plus selection/model binding from the panel, and split controller
presentation-state projection from command orchestration. This is the concrete
trigger; Slice 2A does not prebuild a spreadsheet or generic composition
framework.

### Slice 2B — Spreadsheet interaction and CRUD

- Reach the required spreadsheet interaction baseline.
- Integrate add, duplicate, delete, clear, paste, validation, and undo grouping.

### Slice 2C — Validation, dirty, save, reload

- Add issue-to-cell navigation.
- Clarify Refresh versus Reload.
- Strengthen dirty/discard/save feedback.
- Prove atomic save and reload round-trip.

### Slice 2D — Exchange export

- Generate seven group CSVs and one bundle from the same draft.
- Support free bundle file naming.
- Add deterministic export and round-trip fixtures.

### Slice 2E — Bundle import

- Parse and validate `mapping_bundle_v1`.
- Show change preview.
- Apply only to the unsaved draft.
- Block unknown structural columns and unsupported merge cases.

Each slice is one logical commit and is pushed to the phase branch. The phase is
merged only after populated-state and exchange validation pass.

## 11. Acceptance Scenarios

- Editing one value marks the draft dirty and Save clears it after success.
- Reload warns before discarding unsaved edits.
- Multi-row TSV paste lands in valid cells and reports invalid values.
- A PFC ODU Cond Specs row disables Pi editing, clears Pi when changed from F&T,
  and cannot acquire a Pi value through paste or inline edit.
- F&T and future non-PFC Fin Types retain required Pi editing and navigation.
- Issue selection focuses the correct group and field.
- `Cond Inner Area` works without panel-specific code changes.
- Export creates seven readable group CSVs and one internally versioned bundle.
- A freely renamed bundle imports successfully.
- A bundle with an undefined column is rejected and points to Data Definition.
- Import preview applies to draft only; cancel leaves the current draft unchanged.
- Export -> import -> save preserves owned values and dynamic attributes.

## 12. Non-goals

- Structural definition creation from Data Mapping.
- Legacy wide CSV as normal import.
- Automatic import merge.
- Schema or model live reload.
- Predict UI redesign.
- Real company mapping values in repository tests.
- Raw JSON editor as the primary workflow.
