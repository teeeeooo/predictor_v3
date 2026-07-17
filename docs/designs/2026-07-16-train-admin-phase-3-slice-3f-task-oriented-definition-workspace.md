# Train/Admin Phase 3 Slice 3F — Task-oriented Definition Workspace

Status: accepted design amendment — Slice 3F table-first correction
Date: 2026-07-16
Branch: `phase/train-admin-data-definition-ux`
Correction baseline: `1f3d9d973f7e97a1ed123a88fd757016ccbc34ab`
Depends on: accepted Slice 3A–3D contracts and technically completed Slice 3E interaction/accessibility work

Follow-up (2026-07-17): this amendment remains accepted Phase 3 foundation and
its historical scope is unchanged. Complete Feature lifecycle/ordering, ML
persistence, Derived and One-hot group authoring, Target/registry management, and
live reload are owned by Phase 4 — Unified Feature Manager; Phase 3 final audit
and PR #16 merge history remain intact.

## 1. Decision

Slice 3E completed the requested keyboard, focus, accessibility, state, responsive,
and bounded native-evidence work without changing the accepted Data Definition or
Data Mapping contracts. That implementation remains valid technical foundation.

The resulting native visual states did not, however, satisfy the original Phase 3
product goal. The screen was still organized like a refined diagnostics console
rather than a table-first Feature Manager: Label owned the remaining width,
Selected Definition consumed default height, and clean-state surfaces competed
with inventory browsing. The bounded Slice 3F correction replaced the default
presentation composition; the Phase 3 final audit was approved and PR #16 was
merged. Phase 4 now starts with a current-state audit and design finalization.

This document amends the default-workspace and inventory/detail direction in
`2026-07-14-train-admin-phase-3-data-definition-ux-overhaul.md`. The earlier
Slice 3F composition in this document is superseded as follows:

- no inventory column owns all remaining width;
- the always-visible Selected Definition Summary Card is removed from the
  default composition;
- Summary information is reused through an on-demand Details modal;
- clean browsing has no separate lower state panel;
- Inventory is the default viewport's primary vertical stretch owner.

Where the documents conflict on presentation composition, this correction is
authoritative. Existing domain, command, validation, save, handoff, mapping,
compatibility, and persistence ownership from the Phase 3 design remains
unchanged.

## 2. Evidence-based problem statement

Review of the Slice 3F native evidence identified the following table-first
correction needs. The existing evidence remains valid historical evidence for
the superseded composition; it is not evidence for this correction's acceptance.

### 2.1 Label owns the remaining width

The current inventory has a user-facing six-column projection, but its Label
section is still configured as the only stretch section. This makes the primary
feature-name column consume all remaining width and weakens comparison across
Kind, source, usage, and status. The correction keeps the existing readable
projection and adds the missing feature-management columns without allowing one
column to dominate the viewport.

### 2.2 The default workspace is still summary-led

The Selected Definition Summary Card is useful on demand, but its permanent
description, fact grid, and technical disclosure consume vertical space after
every row selection. The primary user task is to find a feature in the table and
then Add, Edit, or inspect Details. The default composition therefore removes
the card and opens its normalized projection only through Details.

### 2.3 Clean-state surfaces compete with inventory

Clean browsing does not require a lower impact or empty-state panel. The concise
state in the header is sufficient; dirty, blocked, write-error, and saved mapping
states alone earn a conditional lower surface.

### 2.4 Table interaction is the primary workflow

The default workflow is:

```text
feature search
    -> table selection
    -> Add / Edit / Details
    -> change-state review
    -> Save schema
    -> Data Mapping when the saved handoff requires it
```

Enter and double-click use the existing controlled Edit path for editable schema
rows and the read-only Details path for unsupported or read-only definitions.
They never enter raw grid editing.

## 3. Slice 3F goal

Build a table-first default Data Definition workspace in which an engineer can:

```text
find a feature
    -> select it in the inventory
    -> Add, Edit, or open read-only Details
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
3. Full-width Definition Inventory — primary vertical stretch owner
4. Conditional dirty / blocked / saved next-step surface
5. Advanced Diagnostics — collapsed by default
```

Inventory and selected detail are not placed in a horizontal table splitter.
The default content is not wrapped in an unnecessary vertical `QScrollArea` that
limits inventory height. Diagnostics and Details own scrolling only when their
expanded content requires it.

### 4.1 Layer 1 — Current state and primary actions

The top surface communicates one current state and the actions relevant to it.

#### Clean

```text
No unsaved changes            [Add ▾] [Edit] [Save schema] [More ▾]
```

#### Dirty and saveable

```text
1 unsaved change · Restart required [Review changes] [Save schema] [More ▾]
```

#### Blocked

```text
Save blocked · Model compatibility update required
                             [Review blocker] [More ▾]
```

#### Saved

```text
Schema saved · Restart Predict to use this change
                                      [Open Data Mapping] [More ▾]
```

Action hierarchy:

| Priority | Actions |
| --- | --- |
| Primary | Add, Edit, Save schema |
| Contextual | Review changes, Review blocker, Open Data Mapping |
| Secondary | More, Refresh, Reset Draft |
| On-demand | Details, Advanced Diagnostics |

Refresh and Reset Draft must not have the same default visual prominence as Add,
Edit, and Save. `More` contains at least Details, Refresh, Reset Draft, and
Advanced Diagnostics. Details is disabled when no row is selected.

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

Normal default columns:

| Column | Purpose |
| --- | --- |
| Label | Engineer-facing definition name |
| Kind | Predict Input, Mapping-backed Input, Mapping Attribute, One-hot Feature, Status, or other user-facing category |
| Data Type | number, string, boolean, or equivalent user-facing type |
| Value source | Manual, Mapping, Derived, One-hot, Status, or equivalent user-facing source |
| Predict | Used / Not used |
| Model input | Used / Not used |
| Required | Yes / No |
| Status | Active, Changed, Blocked, Inactive, Read-only, or equivalent current state |

Compact default columns:

```text
Label · Kind · Data Type · Value source · Predict · Status
```

`Model input` and `Required` are hidden in compact mode as lower-priority
comparison columns. Visibility is owned by the inventory presentation owner and
is not reimplemented as scattered widget indexes.

The following fields move out of the default table:

- Mapping / Trigger
- internal key
- ML name
- role/editor
- rule ID
- raw source kind
- schema origin
- one-hot group
- compatibility fingerprint
- raw issue code

They remain available in the on-demand Details technical disclosure or Advanced
Diagnostics.

#### Width policy

- No default column is a stretch owner and the last visible column never
  automatically consumes all remaining width.
- Every visible column receives a realistic initial bounded width and remains
  user-resizable through the header's Interactive policy.
- Label uses a bounded initial width; unused space may remain as table whitespace.
- `stretchLastSection=True` is forbidden for this inventory.
- Width policy is reapplied after model replacement, filter, refresh, responsive
  mode change, and compact-column restoration.
- At representative 1280×820 and 900×640 logical sizes, the default inventory must
  not require horizontal scrolling.
- Normal shows all eight columns; compact shows the six columns above without a
  default horizontal scrollbar.
- Tooltip or accessible description may expose internal key and ML name without
  adding default columns.

### 4.5 On-demand Details surface

The always-visible Selected Definition Summary Card is removed from the default
composition. Its Qt-free information is preserved through a dedicated
`DataDefinitionDetailsProjection` assembled by the presentation owner from the
existing `DataDefinitionSummaryProjection` and `DataDefinitionDetailState`.
Summary fields are the authority for overlapping user-facing values; detail rows
are reserved for the Technical details disclosure.

Details opens only from the selected row through the `Details` action in `More`,
or through Enter/double-click when the selected definition is read-only or edit is
unsupported. It is a read-only modal `QDialog.exec()` surface:

```text
Definition Details

<fixed title and identity/status>
<single vertical QScrollArea>
  <description and practical facts>
  Technical details ▸
<fixed Close button>
```

The dialog has no edit controls. Edit remains the existing separate controlled
modal workflow and is opened only after Details is closed. Escape and Close are
non-mutating. The dialog captures an immutable projection snapshot at open time;
draft, filters, selection identity, and focus do not change while it is open.

Minimum practical content:

- label
- internal key
- current status
- user-facing description
- Kind
- Data Type
- Value source
- Predict use
- Model Input use
- Required
- Data Mapping relation
- editing availability
- current change/blocker summary

Technical details retain role/editor/origin, trigger/rule, ML and one-hot
metadata, compatibility evidence, edit policy, and raw supporting fields. The
dialog uses one outer vertical `QScrollArea`; technical tables do not own a
nested vertical scrollbar. Long values wrap. A technical table may expose a
horizontal scrollbar only when its content cannot otherwise fit. The Close
button remains outside the scroll area. On close, Inventory selection and focus
are restored; no multi-definition comparison workflow is introduced.

### 4.6 Layer 4 — Conditional change, blocker, and next-step surface

A large Impact Preview is not permanently visible. The concise header state is
the only clean-state status surface.

#### Clean browsing

Do not render a separate lower state panel. Inventory uses the available height.

#### Dirty and saveable

Show a small banner or concise panel containing:

- affected definition count or names
- restart requirement
- concise mapping/retraining/compatibility impact
- Review changes action
- Save schema action

The detailed structured impact is disclosed through Review changes and remains
owned by the existing impact/diagnostics path.

#### Blocked

Show a concise blocker banner containing the most actionable blocker first in
user-facing language, with:

- affected definition
- what operation is blocked
- why it is blocked
- the next supported recovery action

Raw issue codes, targets, fingerprint details, and full cross-source evidence stay
inside Review blocker or Advanced Diagnostics. Save is disabled and Reset Draft
remains available through the secondary action hierarchy.

#### Saved

Show only the successful schema result and restart guidance when there is no
Mapping Requirement. When the saved result contains Mapping Requirements, show a
short saved-only next step directly:

```text
Mapping values are required for Cond Inner Area.   [Open Data Mapping]
```

The existing saved-only handoff selector is retained only when multiple
requirements need selection. The existing saved-only handoff authority and exact
Data Mapping navigation remain unchanged.

### 4.7 Layer 5 — Advanced Diagnostics

One collapsed `Advanced Diagnostics` entry remains at the end of the workspace.
It is not required for ordinary feature browsing and may also be opened from
`More`; both routes use the same toggle/action owner.
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
| Clean | Definition browsing | Add, supported Edit, More/Details |
| Dirty/saveable | Concise change summary | Review changes, Save schema, Reset |
| Dirty/blocked | Actionable blocker summary | Review blocker, Reset; Save disabled |
| Write error | Error plus retained dirty state | Retry Save when existing owner allows |
| Saved | Saved/restart result | Contextual Open Data Mapping when applicable |
| No match | Recovery guidance | Clear search/filter |
| No selection | Empty inventory-selection state | Add or select a definition |
| Load error | Existing recovery path | Refresh/retry according to current owner |

Selection, focus, shortcut, accessibility, and dialog behavior completed in Slice
3E must continue to work after the composition changes.

## 6. Responsive behavior

Representative logical sizes:

- normal: 1280×820
- compact: 900×640

Required behavior:

- Inventory remains full width in both modes.
- No Selected Definition Summary Card appears in the default composition.
- Inventory owns the remaining vertical stretch in both modes.
- No horizontal inventory scroll is required at either representative size.
- Primary actions remain visible and reachable.
- Secondary actions move into `More` or a compact second row without competing
  with Add/Edit/Save.
- Long state and blocker messages wrap without hiding actions.
- Conditional change/next-step surfaces do not consume large empty vertical space;
  clean has no lower panel.
- Advanced Diagnostics remains collapsed by default.
- No nested horizontal scrollbar is introduced in the default workspace.

## 7. Ownership and implementation boundary

Slice 3F may change:

- Data Definition workspace composition
- inventory UI-facing projection and normal/compact column policy
- normalized read-only Details projection and modal presentation
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
workspace-composition owners. The Details dialog renders a normalized immutable
DTO and does not interpret schema fields, policy, or raw issue codes. Widgets must
not acquire domain or persistence policy. The Inventory view owns column
visibility and width policy; the Panel owns composition and lifecycle; the
workspace behavior owner owns keyboard/focus routing.

## 8. Validation purpose

### 8.1 Presentation projection

Prove:

- normal eight-column and compact six-column inventory semantics
- Data Type and Required meanings
- stable identity and canonical order
- user-facing Kind, Value source, Predict, Model input, and Status text
- normalized Details projection retains Summary and technical metadata without
  duplicate authority
- Details snapshot content and read-only state
- clean/dirty/blocked/saved/no-match/load-error state projection
- primary/contextual/secondary action enablement remains controller-owned

### 8.2 Offscreen workflow

Prove at normal and compact sizes:

- inventory uses full width
- Summary Card is absent from the default composition
- Inventory is the main vertical stretch owner
- no default horizontal inventory scrollbar
- Label and last column are not stretch sections
- clean state does not render the full impact body
- clean state has no lower panel
- Details opens only on demand and closes with selection/focus restored
- editable Enter/double-click uses Edit; read-only Enter/double-click uses Details
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

1. clean normal table-first workspace
2. on-demand Details modal with Technical details disclosure
3. dirty saveable concise change banner
4. blocked actionable banner
5. saved Mapping next step
6. compact table-first workspace

Correction assets belong under
`docs/designs/assets/phase-3-slice-3f-table-first-correction/`; the prior
`docs/designs/assets/phase-3-slice-3f/` captures remain superseded historical
evidence.

Use the existing safe native scenario approach. Do not use the known AppKit Qt
table accessibility click/hit-test path. Evidence must accurately distinguish
programmatic interaction, Computer Use inspection, backing-store capture, desktop
capture, and physical interaction. Each correction manifest records commit SHA,
native onscreen status, capture source, logical/pixel size, fixture/provider,
programmatic/Computer Use/physical classification, actual interaction,
protected/runtime fixture changes, known accessibility-path use, and that prior
Slice 3F evidence is superseded historical evidence.

## 9. Slice 3F acceptance

This table-first correction is accepted only when:

- an engineer can find a feature and identify Add/Edit/Details without reading
  Advanced Diagnostics;
- the default inventory is the primary vertical surface, full width, and readable
  without horizontal scrolling at normal and compact representative sizes;
- no default Summary Card or clean lower panel consumes inventory height;
- normal shows the required eight columns and compact shows the required six;
- no inventory column owns remaining width or uses stretch-last policy;
- Details preserves Summary and technical evidence on demand, is read-only, and
  restores selection/focus after Close/Escape;
- Enter/double-click routes editable rows to Edit and read-only rows to Details;
- clean-state browsing is not dominated by Impact Preview;
- dirty, blocked, saved, and mapping-next-step states each show distinct concise
  actions;
- Add begins from one intent-oriented entry while preserving existing commands;
- all accepted Slice 3A–3E functional, safety, focus, accessibility, and mapping
  behavior remains intact;
- native correction evidence demonstrates the redesigned hierarchy honestly;
- the existing Slice 3F evidence is retained only as superseded historical
  evidence;
- Phase 3 final audit approval and PR #16 merge are complete; this amendment does
  not change the Phase 4 Train/Model user-flow direction.

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

This correction was one independently auditable logical presentation commit on
the existing Phase 3 branch and Draft PR.

```text
Slice 3F design amendment
    -> table-first presentation correction
    -> focused/offscreen validation
    -> impacted regression and protected-file diff
    -> bounded native correction evidence
    -> logical commit and branch push
    -> PR #16 correction record/body update
    -> Phase 3 final audit approval
    -> PR #16 merge
    -> Phase 4 current-state audit and design finalization
```
