# Train/Admin Phase 3 — Data Definition UX Overhaul

Status: accepted complete phase design
Date: 2026-07-14  
Audit baseline: merged `main` at `f381c90960153600b5e218528e36914e5b093d1a`  
Closeout: Phase 3 final audit approved and PR #16 merged on 2026-07-16
Depends on: accepted Phase 1 foundation and merged Phase 2 Data Mapping workflow

## 1. Goal

Replace the current diagnostics-first Data Definition surface with an
intent-driven manager that lets an engineer understand, add, and modify the
supported Predict and mapping definition types without manually coordinating
internal schema and compatibility files.

The presentation may be rebuilt substantially. Existing Qt-free draft,
edit-policy, projection, validation, save-plan, schema-writer, and readiness
owners remain authoritative. Phase 3 adds user workflows around those owners; it
does not duplicate their rules in the UI.

## 2. Audited Current State

### 2.1 Existing user surface

The current Data Definition tab is already editable; it is not merely a read-only
report. It exposes Refresh, Reset Draft, and Save actions plus one editable raw
draft grid.

The default body is a vertical scroll stack containing:

1. Summary
2. Draft
3. Draft Changes
4. Save Plan Preview
5. Save Blockers
6. Save Result
7. Projected Features
8. Mapping Requirements
9. One-hot Relationships
10. Readiness
11. Issues

The draft grid exposes about twenty internal schema fields at once. This is useful
as compatibility and diagnostic evidence, but it is not an effective default
engineering workflow. Internal source kinds, keys, projection metadata, and save
diagnostics dominate the screen before the user has selected a definition or an
action.

The current Save button is enabled from the presence of draft rows rather than
the controller's actual `can_save_schema` state. A clean or blocked draft can
therefore appear to offer a valid primary Save action even though the guarded
writer will no-op or reject it. Phase 3 must make visible action state match the
existing save-plan owner.

### 2.2 Existing application owners

The current boundaries are usable and must be reused:

| Area | Current owner and behavior |
| --- | --- |
| Draft lifecycle | Data Definition controller owns the in-memory draft and routes Refresh, cell edit, Reset, and Save. |
| Application operations | Data Definition service loads reports/drafts, applies field edit policy, previews save plans, and invokes the guarded writer. |
| Draft model | Qt-free immutable draft holds schema rows plus derived-policy rows, immutable baseline rows, issues, stable identities, and field-level changes. |
| Edit policy | Schema-backed metadata fields may be edited; identity/order/role require a controlled command; derived-policy and mapping-value edits are blocked. |
| Projection and validation | Schema rows project to the ML compatibility shape and are checked against schema, one-hot, mapping-requirement, readiness, and Feature Catalog parity rules. |
| Save planning | Save plan classifies blockers, schema targets, restart impact, retrain impact, and unsupported target ownership. |
| Persistence | Guarded schema writer validates a temporary candidate, creates a backup, and atomically replaces `config/predict/schema.csv`. |
| Mapping projection | Data Mapping reads current Data Definition mapping requirements and dynamically exposes definition-backed columns. |

Slice work must extend UI-facing projections or add controlled command owners
where needed. It must not move validation, compatibility, or file-write policy
into widgets.

### 2.3 Current canonical and compatibility sources

- `config/predict/schema.csv` is the canonical Data Definition and Predict schema
  source.
- `config/ml/features.csv` is a legacy ML compatibility/parity surface. Canonical
  default writes to it are already blocked.
- `data/mapping.json` remains the concrete Data Mapping value source of truth.
- Derived feature policy is readable and projected, but has no Phase 3 persistence
  owner.

The current schema writer owns only `schema.csv`. Phase 3 must not describe or
implement a multi-artifact atomic save until an explicit owner exists for every
additional write target.

### 2.4 Current supported mutation boundary

Existing direct editing can safely modify schema-backed fields only when the save
plan and candidate validation allow the resulting schema write. It cannot safely
perform raw row creation/deletion, identity changes, display-order changes, role
changes, derived-policy edits, or mapping-value edits.

A controlled Add workflow is therefore a new command responsibility. It must
construct complete valid schema rows and preserve the raw row add/delete guard;
it must not bypass the guard by mutating draft tuples directly from a widget.

### 2.5 Current ML compatibility boundary

A draft change that alters the projected ML compatibility fingerprint is blocked
because no canonical Feature Catalog projection writer is owned by Data
Definition. This is an intentional safety boundary, not a missing Save-button
feature.

Initial supported Add/Edit intents must therefore remain projection-neutral:

- Predict-visible manual or mapping-backed columns may be added with
  `model_input_enabled=false`;
- definition-backed mapping attributes may be represented by active,
  non-model-input schema rows whose mapping requirement is projected to Data
  Mapping;
- existing schema metadata edits are allowed only when they do not require an
  unsupported compatibility write.

Model-input activation, active ML identity/order changes, and generic one-hot
ownership changes remain previewable but blocked unless a later explicit design
adds the required persistence and compatibility owner.

### 2.6 Current Data Mapping handoff gap

Data Mapping already reloads definition-owned mapping requirements and can expose
new dynamic columns. However, the Train shell has no public command that opens the
Data Mapping tab at a requested group. Phase 3 must add a deliberate shell/panel
navigation contract in Slice 3D rather than reaching into private Data Mapping
selection state.

## 3. Target User Workflow

```text
browse or search definitions
    -> select one definition and understand its role
    -> choose a supported Add or Edit intent
    -> enter constrained intent fields
    -> review generated definition and cross-contract impact
    -> resolve blockers
    -> Save schema atomically
    -> restart when required
    -> open Data Mapping at the affected group when values are required
```

The default view focuses on definitions and next actions. Projection, parity,
one-hot, readiness, raw draft, and write diagnostics remain available through
progressive disclosure.

## 4. Structural Ownership

| Area | Phase 3 responsibility |
| --- | --- |
| Data Definition | Definition identity, label, role, editor, type, visibility, required/read-only intent, value source, mapping requirement metadata, rule reference, model-input intent, ML name, one-hot metadata, notes/help where currently supported, and impact classification. |
| Data Mapping | Concrete rows and values for definition-owned mapping structures. |
| Predict | Consumes the saved schema after restart; Phase 3 does not add live schema reload or redesign Predict. |
| ML compatibility | Existing projection/parity owners remain authoritative. Unsupported projected changes stay blocked. |
| Train / Model | Later consumes readiness and artifact impact; Phase 3 reports impact but does not retrain automatically. |

Data Definition never writes concrete values to `mapping.json`. Data Mapping never
creates an undefined attribute from imported CSV content.

## 5. Target Information Architecture

### 5.1 Default workspace

The default Data Definition workspace contains three primary regions:

1. **Status and actions**
   - concise clean/dirty/blocked/saved state;
   - Refresh, Reset Draft, Add Definition, Add Mapping Attribute, Edit, and Save;
   - actions enabled from actual controller/application state.

2. **Definition inventory**
   - searchable and filterable list;
   - compact user-facing comparison columns;
   - stable selection by definition identity;
   - clear empty, no-match, load-error, and blocked states.

3. **Focused definition detail**
   - purpose and user-facing label;
   - definition category and data type;
   - visibility/editability/required intent;
   - value source and mapping relationship;
   - model-input state and compatibility status;
   - current editability or blocker explanation;
   - relevant impact summary.

Advanced diagnostics remain available in a secondary/collapsible area rather
than the default vertical report stack.

### 5.2 Inventory projection

The inventory is a presentation projection of the existing controller state and
draft. It does not become a second domain model or persistence format.

Default columns should prioritize what engineers compare, such as:

- label;
- definition category;
- data type;
- value source;
- mapping group or trigger where applicable;
- Predict visibility;
- model-input state;
- active/blocked state.

Internal identity, source kind, rule ID, ML name, and ordering remain available in
the detail or advanced diagnostics but do not dominate the default table.

### 5.3 Search and filters

Slice 3A provides non-mutating client-side search/filter over the loaded
inventory. At minimum, users can search by label/key and filter by meaningful
category/source/state. Search and selection must not alter the draft, baseline,
change list, save plan, or schema file.

When filtering hides the selected row, selection resolves predictably to the
first visible match or a no-selection detail state. Clearing filters restores the
same underlying inventory order.

### 5.4 Advanced diagnostics

The following existing evidence remains accessible:

- current raw schema draft editor;
- draft changes;
- save plan and blockers;
- save result;
- projected features and Feature Catalog parity;
- mapping requirements;
- one-hot relationships;
- readiness;
- issues.

Slice 3A may reorganize these into tabs, collapsible panels, or a secondary
splitter. It must preserve the current controller/service behavior and tests. The
raw draft editor remains a compatibility path until controlled Add/Edit workflows
replace frequent direct-grid use in later slices.

## 6. Supported Definition Intents

### 6.1 Manual Predict input without ML activation

Example:

```text
Fan Diameter
numeric manual input
Predict-visible
optional or required
model input disabled
```

This is schema-only and projection-neutral. Enabling it as a model input is a
separate impact that remains blocked without an approved compatibility writer.

### 6.2 Mapping-backed Predict column without ML activation

Example:

```text
Evap Inner Surface Area
numeric read-only Predict column
mapping group: Evap Index
mapping attribute: Inner Surface Area
trigger: Evap Index
supported current lookup rule
model input disabled
```

The intent must use existing supported schema enums and rule templates. Arbitrary
rule-expression authoring is not introduced.

### 6.3 Mapping attribute without immediate Predict or ML activation

Example:

```text
Cond Inner Area
mapping group: ODU Cond Specs
numeric
values managed in Data Mapping
not Predict-visible
model input disabled
```

The initial implementation must resolve this intent to a valid current
schema-row representation that projects a Mapping Requirement without changing
the ML compatibility fingerprint. No independent mapping-attribute registry is
introduced silently. If a requested intent cannot be represented safely by the
current schema contract, it remains blocked with an explanation.

### 6.4 Controlled existing-definition edits

Existing schema-backed edits use the current field edit policy and save plan.
Identity, role, and order are not converted to unrestricted grid edits. Active ML
feature rename/delete, feature-order change, derived-policy edit, and generic
one-hot changes remain blocked unless a later design explicitly supplies their
owners and migration behavior.

## 7. Impact and Save Model

The UI distinguishes:

- clean versus unsaved draft;
- warnings versus blocking errors;
- schema write planned/no-op/blocked;
- restart required;
- training-header or compatibility impact;
- retrain required;
- current model potentially inactive/incompatible;
- Data Mapping values incomplete;
- saved result and backup path.

Initial persistence is atomic for `schema.csv` only. The existing candidate
validation, backup, and replace workflow remains authoritative.

Save is enabled only when:

```text
draft changed
and save_plan.can_save_schema
and no UI/application operation is in progress
```

A clean draft does not present an active Save action. A blocked draft shows the
reason and performs no write. Phase 3 does not silently write
`config/ml/features.csv`, derived policy, `mapping.json`, model artifacts, or
training data.

## 8. Implementation Slices

### Slice 3A — Information architecture and definition inventory

Purpose: replace the report-stack default view without changing schema, command,
or persistence contracts.

Required behavior:

- introduce an inventory/search/filter/focused-detail presentation;
- classify existing schema and derived-policy rows into user-facing categories;
- preserve stable identity and current schema order beneath filtering;
- keep raw draft editing and all existing diagnostics accessible through advanced
  disclosure;
- bind Save enabled state to `can_save_schema` and dirty state;
- preserve current Refresh, Reset, guarded Save, draft, baseline, validation, and
  save-result behavior;
- represent clean, dirty, blocked, empty, no-match, and load-error states;
- avoid adding Add/Edit command behavior beyond disabled or clearly staged entry
  points where necessary for the approved layout.

Implementation boundary:

- use a dedicated UI-facing inventory/detail projection owner rather than adding
  another responsibility cluster to the existing panel or state builder;
- reuse existing common style/layout/table components where they fit;
- no `config/**`, `data/**`, model, or runtime artifact writes in Slice 3A tests;
- no native Computer Use table-click acceptance is required for the initial code
  slice; automated and programmatic rendering evidence comes first.

Slice 3A acceptance:

- default screen is inventory-first, not eleven stacked reports;
- search/filter and selection are deterministic and non-mutating;
- selected detail matches the underlying draft identity;
- advanced diagnostics remain reachable;
- existing guarded edit/reset/save tests remain valid;
- Save is disabled when clean or blocked and enabled for an allowed dirty draft;
- the four-tab Train shell contract is unchanged.

### Slice 3B — Controlled intent commands and Add/Edit workflow

- add explicit command/application owners for supported schema-row creation and
  controlled edits;
- support non-ML manual Predict input, projection-neutral mapping-backed Predict
  column, and safely representable standalone mapping attribute intents;
- use constrained choices from current schema enums and supported rule templates;
- preserve raw row add/delete, identity/order/role, derived-policy, and unsupported
  ML-operation guards;
- apply each accepted user intent as one draft command with deterministic identity
  and order allocation;
- keep unsupported cases visible and actionable rather than partially applying
  them.

### Slice 3C — Impact preview and schema save workflow

- turn the current save plan, blockers, projection parity, restart, retrain, and
  model-activation information into one user-facing impact preview;
- keep schema candidate validation and atomic writer authoritative;
- ensure Save state and feedback reflect the actual plan;
- keep ML projection-changing operations blocked unless a separately approved
  persistence design exists;
- preserve no-op and failed-write behavior without partial artifacts.

### Slice 3D — Data Mapping handoff and coverage

- define a public Train shell/Data Mapping navigation contract;
- after a saved mapping requirement, open Data Mapping at the affected group
  without accessing private widget state;
- refresh definition-backed columns through the existing mapping-requirement
  provider;
- report required/optional value coverage and direct the user to unresolved rows;
- prove the `Cond Inner Area` structure-to-value flow with synthetic fixtures;
- keep Predict activation restart-required; do not add live schema reload.

### Slice 3E — Editing quality and native polish

- complete keyboard, focus, selection, recovery, empty-state, terminology,
  accessible labeling, and responsive layout behavior;
- reconcile common table/dialog conventions without changing definition
  contracts;
- perform bounded native visual/interaction acceptance after automated behavior is
  stable, avoiding the known deferred Data Mapping accessibility-click path.

Each slice was one independently auditable logical commit on the Phase 3 branch.
The Phase 3 final audit is approved and PR #16 is merged; subsequent work starts
from the merged-main current-state audit for Phase 4.

## 9. Validation Purpose

Repository validation proves:

- inventory/detail projection and filter semantics;
- draft and baseline preservation;
- controlled intent construction;
- schema candidate validation and atomic save behavior;
- projection/parity and impact classification;
- Data Mapping requirement handoff and synthetic value coverage;
- UI state and workflow behavior.

Mock data does not prove real mapping completeness, prediction accuracy, model
quality, or production readiness. Those remain company-local validation.

## 10. Phase Acceptance Scenarios

- An engineer can find and understand an existing definition without reading the
  raw schema grid.
- A clean or blocked draft never presents an enabled Save action.
- A user adds a non-ML numeric Predict input and saves it without manually editing
  `schema.csv`.
- A user defines a safely representable `Cond Inner Area` mapping requirement,
  saves it, opens Data Mapping at ODU Cond Specs, fills synthetic values, and sees
  coverage become ready.
- A user adds a supported mapping-backed Predict column and sees mapping, restart,
  training-header, and model impact before Save.
- Attempting to activate or rename an unsupported active ML feature produces a
  blocker and no partial write.
- Restart-required, compatibility/training-header impact, retrain-required,
  current-model-inactive, and Data Mapping-incomplete states are distinct.

## 11. Non-goals

- Editing concrete mapping values in Data Definition.
- Direct canonical writes to `config/ml/features.csv`.
- Derived-policy persistence without a separate owner design.
- Automatic migration of real training data.
- Automatic retraining or model activation.
- Predict internal redesign.
- Live schema reload.
- Unbounded generic rule authoring.
- Silent import-driven schema creation.
- Individual Mapping CSV import or Mapping merge changes.
- Calculator changes.
- Reopening deferred Phase 2 native acceptance.
