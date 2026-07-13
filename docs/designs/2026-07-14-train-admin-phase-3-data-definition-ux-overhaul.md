# Train/Admin Phase 3 — Data Definition UX Overhaul

Status: proposed phase design  
Date: 2026-07-14  
Depends on: Phase 1 foundation and Phase 2 Data Mapping workflow

## 1. Goal

Replace the current diagnostics-first Data Definition surface with an
intent-driven manager that lets an engineer add and modify supported Predict,
mapping, and ML-related definitions without manually coordinating internal schema
and feature files.

The UI may be rebuilt substantially. Existing projection, validation, save, and
readiness owners remain authoritative.

## 2. Target User Workflow

```text
choose Add or Edit
    -> describe intended column/attribute behavior
    -> review generated definition and cross-contract impact
    -> resolve blockers
    -> Save
    -> follow restart/retrain/Data Mapping handoff guidance
```

The default view focuses on definitions and actions rather than exposing all
internal reports simultaneously.

## 3. Information Architecture

The target surface should provide:

- searchable/filterable definition inventory;
- clear definition categories and roles;
- Add Definition / Add Mapping Attribute workflows;
- focused detail/editor panel or dialog;
- change summary and dirty state;
- impact preview;
- blockers and warnings;
- save result and restart/retrain state;
- direct handoff to Data Mapping when values are required;
- advanced projection/readiness details on demand.

Existing summary, draft, save plan, blockers, projected features, mapping
requirements, one-hot relationships, readiness, and issues remain useful state,
but should be reorganized around the user's task.

## 4. Supported Definition Intents

### Manual input column

Example:

```text
Fan Diameter
numeric
user editable
optional or required
Predict-visible
optionally a model input
```

### Mapping-backed automatic column

Example:

```text
Evap Inner Surface Area
source group: Evap Index
mapping attribute: Inner Surface Area
triggered by Evap Index
Predict-visible auto value
optionally a model input
```

### Mapping attribute without immediate ML activation

Example:

```text
Cond Inner Area
group: ODU Cond Specs
numeric
value managed in Data Mapping
not necessarily an active ML feature
```

### Controlled existing-definition edits

Allowed edits must be classified by compatibility impact. Operations that cannot
be made safe remain blocked rather than being partially applied.

## 5. Structural Ownership

Data Definition owns:

- definition identity and display label;
- data type and editor behavior;
- visibility, required, and read-only intent;
- value source;
- mapping group/entity and mapping attribute requirement;
- mapping trigger/rule reference;
- model input intent and ML name when supported;
- one-hot selector/emission metadata according to the active owner-switch stage;
- unit/help metadata where supported;
- restart, training-header, and model-activation impact.

Data Definition does not own concrete mapping row values.

When a mapping attribute is saved, Data Mapping exposes the corresponding column
and reports value coverage.

## 6. Add Mapping Attribute Workflow

For a new `Cond Inner Area`, the user specifies only the information needed to
express intent:

- target mapping group;
- display label;
- stable internal identity under current naming policy;
- data type;
- unit/help text where supported;
- required versus optional;
- Predict exposure;
- model-input activation intent.

The impact preview explains:

- Data Mapping will gain a new column;
- existing mapping rows initially have empty values;
- whether empty values block mapping save;
- whether Predict receives a new automatic column;
- whether the ML compatibility contract changes;
- whether training headers require change;
- whether the current model becomes inactive;
- whether restart and retraining are required.

After save, provide a direct action to open Data Mapping at the affected group.

## 7. Save and Compatibility Model

The surface distinguishes:

- draft changes;
- warnings;
- blockers;
- save plan;
- saved result;
- restart required;
- retraining required;
- model incompatible/inactive;
- Data Mapping values incomplete.

Persistence remains atomic across definition artifacts owned by the active slice.
Partial writes are not acceptable.

Do not silently change `config/ml/features.csv`, model contracts, or one-hot
runtime ownership beyond the active approved stage.

## 8. Supported and Blocked Operations

### Required supported scenarios

- add non-ML manual column;
- add mapping attribute to an existing group;
- add mapping-backed Predict column using a supported current rule;
- mark optional versus required mapping coverage;
- preview training-header and model impact;
- save and report restart requirement;
- open Data Mapping for required value entry.

### Initially blocked unless proven safe

- rename or delete active ML features;
- change feature order in a way that invalidates a model without an explicit plan;
- generic one-hot owner switch outside the approved stage;
- automatic model retraining;
- arbitrary rule-expression authoring;
- live schema reload;
- structural creation from imported Mapping CSV;
- partial writes while schema and ML projection disagree.

Blocked operations explain why and what prerequisite is missing.

## 9. Interaction and Visual Direction

The surface should feel like an admin workflow, not a raw schema grid.

- The inventory shows information users actually compare.
- Internal keys and compatibility metadata remain available but secondary.
- Add/Edit uses constrained controls for enums, roles, types, and mapping groups.
- Impact explanations use engineering terminology without requiring file-level
  implementation knowledge.
- Blockers and warnings are visually distinct.
- Save reflects actual save-enabled state.
- Save must not be enabled merely because draft rows exist.
- Advanced projection/readiness views remain available without dominating.
- Editable table-shaped surfaces follow the active table UX contract.

## 10. Implementation Slices

### Slice 3A — Information architecture and definition inventory

- Replace the report-stack default view with a usable inventory.
- Preserve access to projection/readiness diagnostics.
- Add search/filter and focused detail presentation.

### Slice 3B — Intent-driven Add/Edit workflow

- Implement controlled workflows for supported manual and mapping-backed cases.
- Generate draft changes through existing owners.
- Keep unsupported cases visibly blocked.

### Slice 3C — Impact preview and save workflow

- Integrate blockers, warnings, save plan, atomic persistence, restart, training,
  and model-activation impact.
- Correct save-enabled behavior.
- Preserve current compatibility staging.

### Slice 3D — Data Mapping handoff

- Identify the affected group and missing value coverage after structural changes.
- Provide direct navigation to Data Mapping.
- Prove the `Cond Inner Area` end-to-end scenario.

### Slice 3E — Editing quality and polish

- Bring editable inventory/table behavior and shared visuals to the accepted
  Train/Admin standard.
- Complete keyboard, recovery, empty-state, and labeling behavior.

Each slice is one logical commit and is pushed to the phase branch. The phase is
merged only after supported intent scenarios pass.

## 11. Acceptance Scenarios

- A user adds a non-ML numeric Predict input without manually editing schema CSV.
- A user defines `Cond Inner Area`, saves, opens Data Mapping, fills values, and
  sees coverage become ready.
- A user defines a supported mapping lookup and sees Predict, mapping,
  training-header, restart, and model impact before save.
- An unsafe active ML feature rename/delete is blocked with no partial write.
- Restart-required, training-header-required, retrain-required, and
  current-model-inactive are distinguished.

## 12. Validation Purpose

This phase proves that supported structural changes can be expressed safely
through the GUI and projected consistently across current contracts.

Mock data validates workflow and compatibility transitions. Real model quality
remains company-local validation.

## 13. Non-goals

- Editing concrete mapping values in Data Definition.
- Automatic migration of real training data.
- Automatic retraining.
- Predict internal redesign.
- Unbounded generic rule authoring.
- Silent import-driven schema creation.
- Calculator changes.
