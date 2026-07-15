# Train/Admin Phase 3 Slice 3F — Task-oriented Definition Workspace

Status: active design amendment  
Date: 2026-07-16  
Branch: `phase/train-admin-data-definition-ux`  
Audit baseline: Slice 3E implementation at `6aa9c277b5d1151cfcdecae09a30ced2a0bf6440`  
Depends on: accepted Slice 3A–3D contracts and technically completed Slice 3E interaction/accessibility work

## 1. Decision

Slice 3E completed the requested keyboard, focus, accessibility, state, responsive,
and bounded native-evidence work without changing the accepted Data Definition or
Data Mapping contracts. That implementation remains valid technical foundation.

The resulting native visual states do not, however, satisfy the original Phase 3
product goal. The screen is still organized like a refined diagnostics console
rather than an intent-driven Definition Manager. Phase 3 final approval, merge,
and Phase 4 are therefore held while Slice 3F replaces the default presentation
composition.

This document amends the default-workspace and inventory/detail direction in
`2026-07-14-train-admin-phase-3-data-definition-ux-overhaul.md`. Where the two
documents conflict on presentation composition, this Slice 3F design is
authoritative. Existing domain, command, validation, save, handoff, mapping,
compatibility, and persistence ownership from the Phase 3 design remains
unchanged.

## 2. Evidence-based problem statement

Review of the Slice 3E native evidence identified four structural problems.

### 2.1 The inventory table is too wide for its role

The default inventory currently exposes eight columns:

- Label
- Category
- Data Type
- Value Source
- Mapping / Trigger
- Predict
- Model Input
- State

The common Data Definition table policy also stretches the last section across
remaining width. In the current split workspace this produces either an
unnaturally wide last column or horizontal scrolling. This is not a transient
rendering defect; it follows from the current column and header policy.

### 2.2 Inventory and Focused Detail compete for horizontal space

Both surfaces are tables placed side by side. The inventory needs width to compare
rows, while the detail table needs width to expose property values. At normal size
both become cramped; at compact size both require horizontal scrolling. A user
must move left/right and up/down merely to understand one definition.

### 2.3 Focused Detail is still a diagnostics table

The selected-definition surface is a `Property / Value` table containing internal
metadata. It answers which fields exist, but not the engineer's practical
questions:

1. What is this definition?
2. Where does its value come from?
3. Is it used in Predict?
4. Is it a model input?
5. Does it require Data Mapping work?
6. Can it currently be edited or saved?

### 2.4 Impact and commands dominate ordinary browsing

Refresh, Reset Draft, Add Definition, Add Mapping Attribute, Edit, Save schema,
and Review blockers have nearly equal visual priority. The full Impact Preview is
also rendered during ordinary clean-state browsing. The screen communicates many
capabilities but does not make the next user action obvious.

The Slice 3E evidence is native onscreen visual evidence prepared through Qt public
APIs and captured from the native widget backing store. It verifies rendered
states and safe programmatic workflows, but it is not physical usability
acceptance. The visual review therefore remains a valid reason to hold final UX
approval.

## 3. Slice 3F goal

Build a task-oriented default Data Definition workspace in which an engineer can:

```text
find a definition
    -> understand it without opening raw schema diagnostics
    -> add or edit through one clear intent entry
    -> see only the change, blocker, or next step relevant to the current state
    -> save safely
    -> continue to Data Mapping when concrete values are required
```

Slice 3F is a presentation correction. It must reuse the accepted controller,
command, validation, save-plan, writer, handoff, coverage, and mapping owners.

## 4. Target information architecture

The default workspace is arranged vertically in the following order:

```text
1. Current state and primary actions
2. Search and filters
3. Full-width Definition Inventory
4. Selected Definition summary
5. Conditional change / blocker / next-step surface
6. Advanced Diagnostics
```

Inventory and selected detail are not placed in a horizontal table splitter.

### 4.1 Layer 1 — Current state and primary actions

The top surface communicates one current state and the actions relevant to it.

#### Clean

```text
No unsaved changes                                  [Add ▾] [Edit]
```

#### Dirty and saveable

```text
1 unsaved change · Predict restart required    [Review changes] [Save schema]
```

#### Blocked

```text
Save blocked · Model compatibility update required
                                          [Review blocker] [Reset change]
```

#### Saved

```text
Schema saved · Restart Predict to use this change
```

Action hierarchy:

| Priority | Actions |
| --- | --- |
| Primary | Add, Edit, Save schema |
| Contextual | Review changes, Review blocker, Open Data Mapping |
| Secondary | Refresh, Reset Draft |
| Advanced | Advanced Diagnostics |

Refresh and Reset Draft must not have the same default visual prominence as Add,
Edit, and Save.

### 4.2 Unified Add entry

The default surface exposes one `Add` entry that asks what the engineer wants to
create:

```text
Add
├─ Manual Predict input
├─ Mapping-backed Predict input
└─ Data Mapping attribute
```

This is presentation orchestration only. It must route to the existing supported
Add Definition and Add Mapping Attribute command paths. It does not introduce a
new schema intent, generic rule authoring, or a second command owner.

### 4.3 Layer 2 — Search and filters

Search and existing category/value-source/state filters remain directly above the
inventory. Search/filter behavior remains deterministic and non-mutating.

At compact width, search may occupy its own row and filters may wrap below it.
Filter state and selected identity must remain stable across responsive reflow.

### 4.4 Layer 3 — Full-width Definition Inventory

The inventory uses the full workspace width.

Default columns:

| Column | Purpose |
| --- | --- |
| Label | Engineer-facing definition name |
| Kind | Predict Input, Mapping-backed Input, Mapping Attribute, One-hot, Status, or other user-facing category |
| Value source | Manual, Mapping, Derived, One-hot, Status, or equivalent user-facing source |
| Predict | Used / Not used |
| Model input | Used / Not used |
| Status | Active, Changed, Blocked, Inactive, or equivalent current state |

The following fields move out of the default table:

- Data Type
- Mapping / Trigger
- internal key
- ML name
- role/editor
- rule ID
- raw source kind

They remain available in the selected summary's technical disclosure or Advanced
Diagnostics.

#### Width policy

- Label is the only default stretch column.
- Kind and Value source use bounded readable widths.
- Predict, Model input, and Status use content-based or bounded widths.
- The last visible column must not automatically consume all remaining width.
- At representative 1280×820 and 900×640 logical sizes, the default inventory must
  not require horizontal scrolling.
- Compact layout may hide the lowest-priority comparison column, but must not
  squeeze every column into unreadable widths.
- Tooltip or accessible description may expose internal key and ML name without
  adding default columns.

### 4.5 Layer 4 — Selected Definition summary

The current `Property / Value` table is replaced by a purpose-built summary card.

Representative structure:

```text
Selected Definition

Cooling Capacity                                      Active
cooling_capa

Manual numeric input used by Predict and the active model.

Value source        Manual input
Used in Predict     Yes
Model input         Yes
Required            Yes
Data Mapping        None

Technical details ▸                                      [Edit]
```

The summary answers the six practical questions from section 2.3. It may use a
small responsive label/value grid, but it must not use a horizontally scrolling
property table.

`Technical details` contains lower-priority information such as:

- data type
- internal key
- schema origin
- role/editor
- mapping entity, attribute, trigger, and rule
- ML name and one-hot metadata
- direct edit policy
- structured compatibility evidence

At normal width the summary facts may use multiple columns. At compact width they
stack vertically.

### 4.6 Layer 5 — Conditional change, blocker, and next-step surface

A large Impact Preview is not permanently visible.

#### Clean browsing

Show only a concise clean-state message. The detailed impact body remains hidden.

#### Dirty and saveable

Show:

- affected definition count or names
- restart requirement
- concise mapping/retraining/compatibility impact
- Review changes action
- Save schema action

The detailed structured impact is disclosed on demand.

#### Blocked

Show the most actionable blocker first in user-facing language, with:

- affected definition
- what operation is blocked
- why it is blocked
- the next supported recovery action

Raw issue codes, targets, fingerprint details, and full cross-source evidence stay
inside Review blocker or Advanced Diagnostics.

#### Saved

Show the successful schema result and restart guidance. When the saved result
contains Mapping Requirements, show the next step directly:

```text
Mapping values are required for Cond Inner Area.   [Open Data Mapping]
```

The existing saved-only handoff authority and exact Data Mapping navigation remain
unchanged.

### 4.7 Layer 6 — Advanced Diagnostics

One collapsed `Advanced Diagnostics` entry remains at the end of the workspace.
It preserves:

- Raw Draft
- Summary
- Draft Changes
- Save Plan
- Save Blockers
- Save Result
- Projected Features
- Mapping Requirements
- One-hot Relationships
- Readiness
- Issues

These surfaces remain diagnostic evidence, not the default workflow.

## 5. State and action rules

The presentation consumes current controller/application state; it does not
recompute save or compatibility policy.

| State | Primary presentation | Enabled actions |
| --- | --- | --- |
| Clean | Definition browsing | Add, supported Edit |
| Dirty/saveable | Concise change summary | Review changes, Save schema, Reset |
| Dirty/blocked | Actionable blocker summary | Review blocker, Reset; Save disabled |
| Write error | Error plus retained dirty state | Retry Save when existing owner allows |
| Saved | Saved/restart result | Contextual Open Data Mapping when applicable |
| No match | Recovery guidance | Clear search/filter |
| No selection | Empty selected-summary state | Add or select a definition |
| Load error | Existing recovery path | Refresh/retry according to current owner |

Selection, focus, shortcut, accessibility, and dialog behavior completed in Slice
3E must continue to work after the composition changes.

## 6. Responsive behavior

Representative logical sizes:

- normal: 1280×820
- compact: 900×640

Required behavior:

- Inventory remains full width in both modes.
- Selected summary appears below the inventory in both modes.
- No horizontal inventory scroll is required at either representative size.
- Primary actions remain visible and reachable.
- Secondary actions may move into a secondary menu or second row.
- Long state and blocker messages wrap without hiding actions.
- Conditional change/next-step surfaces do not consume large empty vertical space.
- Advanced Diagnostics remains collapsed by default.
- No nested horizontal scrollbar is introduced in the default workspace.

## 7. Ownership and implementation boundary

Slice 3F may change:

- Data Definition workspace composition
- inventory UI-facing projection and default columns
- selected-definition summary projection
- action grouping and responsive placement
- conditional impact/blocker/saved-next-step presentation
- table header/width policy for the affected Data Definition surfaces
- focused automated UI tests and bounded native visual evidence

Slice 3F must not change:

- schema row or Mapping Requirement contracts
- Add/Edit command semantics
- role, identity, order, ML, one-hot, or relation policy
- candidate validation or save-plan rules
- schema writer, backup, retry, or atomicity
- shared-cell mapping contract
- Data Mapping value, draft, undo, coverage, import/export, or persistence semantics
- Predict restart boundary
- production configuration, data, training data, or model artifacts

Complex presentation decisions should remain in bounded UI-facing projection or
workspace-composition owners. Widgets must not acquire domain or persistence
policy.

## 8. Validation purpose

### 8.1 Presentation projection

Prove:

- six-column default inventory semantics
- stable identity and canonical order
- user-facing Kind, Value source, Predict, Model input, and Status text
- selected summary answers the six practical questions
- technical details retain omitted metadata
- clean/dirty/blocked/saved/no-match/load-error state projection
- primary/contextual/secondary action enablement remains controller-owned

### 8.2 Offscreen workflow

Prove at normal and compact sizes:

- inventory uses full width
- selected summary is below inventory
- no default horizontal inventory scrollbar
- last-column stretch defect is absent
- clean state does not render the full impact body
- dirty state exposes concise review/save actions
- blocked state exposes the direct actionable blocker
- saved Mapping Requirement exposes Open Data Mapping
- keyboard selection, focus restoration, shortcuts, dialogs, and exact handoff still work
- Advanced Diagnostics remains reachable and collapsed by default

### 8.3 Impacted regression

Retain coverage for:

- inventory/search/filter/selection
- controlled Add/Edit
- blocker attribution and candidate validation
- schema Save, retry, backup, and restart guidance
- saved handoff lifecycle
- shared-cell Mapping Requirement contract
- Data Mapping coverage/navigation/draft/undo/persistence/import/export
- Train shell four-tab contract
- Predict schema/mapping adapters
- ML compatibility/parity
- protected-file invariants

### 8.4 Bounded native visual review

After automated behavior is stable, capture representative native onscreen states
for:

1. clean full-width inventory and selected summary
2. dirty saveable concise change state
3. blocked actionable state
4. saved Mapping next step
5. compact layout

Use the existing safe native scenario approach. Do not use the known AppKit Qt
table accessibility click/hit-test path. Evidence must accurately distinguish
programmatic interaction, Computer Use inspection, backing-store capture, desktop
capture, and physical interaction.

## 9. Slice 3F acceptance

Slice 3F is accepted only when:

- an engineer can identify what the screen is for and what to do next without
  reading Advanced Diagnostics;
- the default inventory is full width and readable without horizontal scrolling at
  normal and compact representative sizes;
- the selected definition is explained through a summary card rather than a
  property table;
- clean-state browsing is not dominated by Impact Preview;
- dirty, blocked, saved, and mapping-next-step states each show distinct concise
  actions;
- Add begins from one intent-oriented entry while preserving existing commands;
- all accepted Slice 3A–3E functional, safety, focus, accessibility, and mapping
  behavior remains intact;
- native visual evidence demonstrates the redesigned hierarchy honestly;
- Phase 3 final audit approves both code behavior and product usability.

## 10. Non-goals

- New definition intents or schema contracts
- Schema row deletion, identity migration, role migration, or order migration
- Feature Catalog writer or canonical `features.csv` writes
- Derived-policy persistence
- Predict live reload or Predict UI overhaul
- Model retraining or activation
- Data Mapping spreadsheet redesign
- Mapping bundle format or merge changes
- General design-system or architecture rewrite
- Reopening deferred Phase 2 table-click native acceptance
- Production data or model-quality validation

## 11. Delivery

Slice 3F is one independently auditable presentation commit on the existing Phase
3 branch and Draft PR.

```text
implement task-oriented workspace
    -> focused presentation/offscreen validation
    -> impacted regression and protected-path check
    -> bounded native visual review
    -> Slice 3F audit
    -> Phase 3 final audit
```

PR #16 remains Draft/Open. Merge and Phase 4 remain on hold until Slice 3F and the
Phase 3 final audit are approved.
