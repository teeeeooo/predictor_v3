# Calculator Table Architecture Design

**Status:** Approved design
**Scope:** Tkinter Calculator table surfaces
**Primary implementation sequence:** Table foundation → representative ISO/ISEER migration → progressive Calculator-wide adoption
**Proposed canonical location:** `docs/designs/2026-07-12-calculator-table-architecture-design.md`

---

## 1. Purpose

This document defines the target table architecture for the active Tkinter Calculator.

The goal is not to reproduce one existing screen pixel-for-pixel. The goal is to make Calculator tables visually modern and consistent while also reducing duplicated table-construction helpers and aligning each table with an implementation appropriate to its behavior.

The architecture must support three outcomes at the same time:

1. Calculator tables use a shared visual language.
2. Tables with the same interaction character use the same implementation family.
3. Existing calculation, interaction, export, profile, and lifecycle behavior remains unchanged unless a later explicitly approved slice changes it.

This document is the implementation design for the table-unification workstream. Later agents should not re-audit the table-family decision unless implementation evidence proves that a defined contract is impossible or materially unsafe.

---

## 2. Background

The active Calculator currently uses several table implementations:

- editable `Frame` / `Entry` matrices,
- row-per-case and logical-matrix batch tables,
- small read-only `ttk.Treeview` result tables,
- cell-rendered read-only result and Rule grids,
- generic result summary panels,
- large scrollable detail `Treeview` tables.

The difference is partly intentional because the surfaces have different behaviors. It is also partly historical: profiles were added incrementally, and visual construction helpers such as cell frames, headers, dividers, padding, alignment, and outer borders were implemented locally in multiple owners.

The main structural problem is therefore not that every table uses a different widget. The main problem is that:

- table-family boundaries are implicit,
- visual policy is repeated inside individual views,
- small result tables use more than one implementation pattern,
- semantic cell state and interaction state are not expressed through one shared visual contract,
- local helper duplication makes Calculator-wide visual correction expensive.

The target architecture preserves legitimate implementation differences while making those differences explicit and bounded.

---

## 3. Design Principles

### 3.1 Same behavior family, same implementation family

Tables are unified by interaction character, not by superficial appearance.

- Editable spreadsheet-like matrices use one family.
- Small fixed read-only results use one family.
- Large scrollable data tables use one family.

### 3.2 Same visual policy across all families

Different widgets may remain, but they must consume the same visual policy for:

- header identity,
- body density,
- dividers,
- outer-edge treatment,
- alignment,
- typography,
- semantic colors,
- selection and focus visibility.

### 3.3 Shared rendering, local meaning

The shared layer owns how a table is rendered.

Each profile continues to own:

- row and column labels,
- visible schema,
- precision,
- optional or unavailable point logic,
- Rule definitions,
- OK/NG decisions,
- status wording,
- export document shape,
- CSV filenames.

### 3.4 Preserve proven interaction owners

Existing spreadsheet interaction controllers remain the owners of:

- selection,
- edit mode,
- paste,
- clear,
- grouped undo,
- navigation,
- read-only mutation protection,
- active-cell transitions.

Visual migration must consume controller state; it must not reimplement controller behavior.

### 3.5 Avoid a universal table widget

Do not create one option-heavy component that tries to handle editable matrices, compact results, Rule tables, batch tables, and large detail tables.

The architecture uses:

- shared policy,
- small shared primitives,
- three explicit table families,
- profile-local composition.

---

## 4. Target Table Families

## 4.1 Editable Matrix Table

### Purpose

Structured tables where users edit cells and expect spreadsheet behavior.

### Active target surfaces

- single-case test input matrices,
- batch case tables,
- batch logical matrices,
- EN14825 condition and climate matrices,
- AHRI test-point matrices,
- any future Calculator surface requiring rectangular selection and cell editing.

### Required behavior

- single and rectangular selection,
- selection mode and edit mode,
- replace-on-type,
- inline editing,
- TSV copy and paste,
- single-cell and repeated-row paste behavior,
- Delete/Backspace clear,
- grouped undo,
- Tab/Enter/arrow navigation,
- read-only/result mutation prevention,
- invalid-cell indication,
- active-cell distinction,
- auto-calculation callbacks,
- state restoration where the containing dialog is stateful.

### Implementation direction

Keep the existing editable table models and interaction controllers.

The migration changes only the visual construction seam:

- table surface construction,
- cell container construction,
- header construction,
- divider placement,
- outer-edge treatment,
- padding,
- font,
- alignment,
- semantic background binding.

### Ownership

The editable table view owns:

- row and column schema consumption,
- field-to-cell mapping,
- Entry/Label creation,
- controller adapter/protocol implementation,
- value snapshots and view-level updates.

The shared visual layer owns:

- visual options and small rendering primitives.

The interaction controller owns:

- state transitions and spreadsheet behavior.

---

## 4.2 Compact Read-only Result Grid

### Purpose

Small, fixed, read-only result tables that do not need a scrolling data widget.

### Active target surfaces

- ISO/ISEER result comparison,
- SASO scenario comparison,
- Brazil calculation result,
- Brazil Rule table,
- generic CSPF/HSPF result summaries,
- Korea midpoint guide,
- small EN14825 result blocks,
- similar future result or judgement surfaces with a bounded number of rows and columns.

### Selection rule

A compact result grid is not an editable spreadsheet.

Its default contract is:

- values are read-only,
- the logical table can be copied as a whole,
- keyboard focus remains visible where the surface is focusable,
- per-cell semantic tones are supported,
- row selection is not required unless the profile has a real user behavior that depends on it,
- multi-cell drag selection is not part of the default compact-result contract.

### Required behavior

- render column headers and rows,
- support per-cell visual roles and semantic tones,
- update values without changing the profile result schema,
- clear and show pending/error/empty states,
- expose logical headers and rows for copy/export adapters,
- support Ctrl/Cmd+C whole-table copy,
- preserve existing `as_text()` or equivalent compatibility where currently used,
- preserve profile-local status placement and export document behavior.

### Implementation direction

Introduce a shared cell-rendered compact result foundation.

Small result `ttk.Treeview` surfaces should migrate to this family. A Treeview style-only exception is not the long-term target for small fixed results.

The shared foundation may provide:

- a compact grid surface,
- reusable header/body cell rendering,
- row and value registries,
- whole-table copy support,
- role/tone binding,
- clear/re-render or stable in-place update support where justified.

It must not own:

- domain result objects,
- Rule interpretation,
- pass/fail calculation,
- profile-specific text formatting,
- profile export documents.

### Brazil relationship

The Brazil result and Rule grids are reference evidence for the desired lightweight visual result.

Their local calculation, Rule, Final, and export behavior remain local.

Only generic rendering concerns may be extracted:

- cell creation,
- header/body styling,
- divider placement,
- per-cell tone application,
- registry/update mechanics.

---

## 4.3 Scrollable Data Table

### Purpose

Read-only tables with enough rows or columns to require scrolling, viewport management, or efficient row management.

### Active target surfaces

- bin detail tables,
- trace/detail result tables,
- large read-only result collections,
- future long diagnostic tables approved for user display.

### Required behavior

- stable column headers,
- vertical and horizontal scrolling where applicable,
- row selection where currently supported,
- copy and CSV behavior,
- source/schema switching where currently supported,
- viewport containment,
- large-data rendering appropriate to Tkinter.

### Implementation direction

Retain `ttk.Treeview`.

Introduce or extend one shared Treeview style adapter that applies the Calculator table visual policy without taking ownership of:

- data insertion,
- detail schema,
- source selection,
- scrollbars,
- viewport measurement,
- copy/export schema.

Treeview remains an implementation choice for large data surfaces only.

---

## 5. Common Visual Architecture

```text
Existing visual tokens
        |
        v
Tk Table Visual Policy
        |
        +-- Grid cell primitives
        |      |
        |      +-- Editable Matrix views
        |      |
        |      +-- Compact Result Grid
        |
        +-- Treeview style adapter
               |
               +-- Scrollable Data Table
```

The shared visual layer is a Tkinter presentation owner.

It must not depend on:

- Calculator core,
- capability execution,
- profile resolvers,
- region configuration,
- ML,
- export document models,
- window lifecycle controllers.

Profile views depend on the shared visual layer. The shared visual layer does not depend on profile views.

---

## 6. Visual Policy Contract

The visual policy translates semantic roles into concrete Tk presentation values and construction options.

### 6.1 Visual policy responsibilities

The policy owns:

- internal divider thickness and color,
- outer-edge policy,
- header and row-header presentation,
- body density,
- header/body padding,
- font roles,
- default text alignment,
- cell background lookup,
- foreground lookup where needed,
- active/selected/focus presentation inputs,
- Treeview style configuration values.

### 6.2 Visual policy exclusions

The policy does not own:

- widget data,
- row/column schema,
- profile identity,
- numeric formatting,
- Rule calculation,
- status text,
- clipboard payload construction,
- window sizing,
- scroll behavior,
- selection state transitions.

### 6.3 Outer-edge rule

The target visual language does not use a strong black `SOLID` outer frame around ordinary tables.

The default is:

- low-contrast internal dividers,
- no heavy nested-card appearance,
- a flat surface integrated into its section,
- an outer boundary only when needed for readability, using the same restrained divider language.

### 6.4 Alignment roles

Alignment is based on content role, not one global table setting.

Recommended roles:

- `IDENTITY_TEXT`: left
- `DESCRIPTIVE_TEXT`: left
- `NUMERIC_INPUT`: center
- `NUMERIC_RESULT`: center by default
- `DENSE_NUMERIC_RESULT`: right when the complete column uses the same rule
- `STATUS_TEXT`: center or left according to the surface contract
- `HEADER_IDENTITY`: left
- `HEADER_VALUE`: center

Profile views may declare a justified exception, but they must not duplicate alignment logic when an existing role fits.

### 6.5 Density

The default density should be compact but not cramped.

The policy must keep:

- readable click targets,
- visible focus,
- consistent row height,
- sufficient padding for Korean and English labels,
- content-hugging behavior for small tables,
- responsive behavior only where the existing surface contract requires it.

No fixed pixel size should be introduced merely to reproduce one screenshot.

---

## 7. Cell State Model

Cell behavior, semantic meaning, and interaction overlay are separate dimensions.

## 7.1 Interaction Role

Interaction Role describes what the user can do with a cell.

```text
HEADER
ROW_HEADER
EDITABLE
READONLY
RESULT
DISABLED
```

The existing role vocabulary may be extended only as needed to express this separation. Existing controller-facing meanings must remain compatible.

## 7.2 Semantic Tone

Semantic Tone describes the engineering or validation meaning of the displayed content.

```text
DEFAULT
CALCULATED
PASS
FAIL
INVALID
WARNING
PENDING
```

Important distinctions:

- `INVALID` means user input requires correction.
- `FAIL` means a domain or compliance judgement failed.
- `PENDING` means calculation is incomplete or not yet available.
- `CALCULATED` means derived/read-only result, not necessarily good or bad.

A shared tone may map to an existing concrete color token. This design does not approve new palette values.

## 7.3 Interaction Overlay

Interaction Overlay describes temporary user interaction state.

```text
SELECTED
ACTIVE
FOCUS
```

### Overlay precedence

The visual layer must apply temporary interaction emphasis without losing the underlying role or tone.

Conceptual precedence:

```text
FOCUS / ACTIVE
      >
SELECTED
      >
INVALID / PASS / FAIL / WARNING / PENDING
      >
base Interaction Role
```

When an overlay is removed, the exact underlying semantic presentation must return.

The visual implementation must not infer underlying state from the current rendered color. The view/controller path must retain the logical role and tone.

---

## 8. Shared Grid Primitives

The shared grid primitive layer is intentionally small.

### 8.1 Accepted inputs

A primitive may receive presentation information such as:

- parent,
- grid row and column,
- interaction role,
- semantic tone,
- alignment role,
- header/body variant,
- outer-edge position,
- section-break position,
- density variant,
- text and text variable where appropriate.

### 8.2 Returned or configured presentation

A primitive may:

- create/configure a cell container,
- create/configure a Label,
- configure pack/grid padding,
- apply fonts,
- apply background/foreground,
- apply divider spacing,
- attach presentation metadata needed by tests or overlays.

### 8.3 Forbidden inputs

A shared primitive must not receive:

- profile IDs,
- calculator result objects,
- region codes,
- Rule formulas,
- full export documents,
- capability responses,
- profile-specific field maps.

### 8.4 Helper cleanup targets

The following repeated concerns should migrate to the shared visual seam when each owning surface is migrated:

- local cell-frame construction,
- local header-cell construction,
- local one-pixel gutter placement,
- local outer `SOLID` table frame,
- repeated header/body font and padding application,
- repeated alignment decisions that match a shared role,
- repeated Treeview style setup.

Local helpers are removed only when their owning surface has migrated and parity is proven.

---

## 9. Compact Result Grid Contract

The Compact Result Grid is a reusable read-only presentation component, not a profile result model.

### 9.1 Logical data contract

The component receives or exposes logical data equivalent to:

```text
headers: tuple[str, ...]
rows: tuple[tuple[str, ...], ...]
cell presentation metadata: optional role/tone/alignment map
```

The exact Python API is selected after reviewing current sibling owners, but the contract must remain this narrow.

### 9.2 Required operations

The family must support:

- set or render rows,
- clear,
- show empty/pending/error state through the profile owner,
- expose logical headers and rows,
- whole-table TSV copy,
- profile-local `as_text()` compatibility where currently required,
- per-cell semantic tone,
- stable focus behavior,
- test-visible cell registry or equivalent inspection seam.

### 9.3 Update strategy

Stable in-place updates are preferred when the table shape is unchanged and current focus behavior requires preservation.

Full rebuild is acceptable when:

- the shape changes,
- focus is not inside the surface,
- the current owner already rebuilds safely,
- focused tests prove no user-flow regression.

The architecture does not require one update strategy for every profile.

### 9.4 Export boundary

The component may expose logical headers and rows.

It must not define:

- CSV filenames,
- multi-section export documents,
- Brazil Rule/Final export structure,
- profile-specific report text.

Existing export adapters continue to own those contracts.

---

## 10. Editable Matrix Integration Contract

Editable Matrix surfaces adopt the shared visual seam without replacing their behavior owners.

### 10.1 Preserve

- current table protocols,
- editable address mapping,
- field-key mapping,
- controller state machine,
- selection and edit behavior,
- Entry widget behavior,
- invalid-state ownership,
- read-only presentation switching,
- change callback behavior,
- batch snapshot and restore,
- auto-calculation triggers.

### 10.2 Change

- table surface construction,
- cell container construction,
- header/row-header construction,
- divider placement,
- outer-edge presentation,
- alignment lookup,
- padding and font lookup,
- base background resolution through shared policy.

### 10.3 Batch relationship

Single and Batch editable tables should consume the same visual primitives and policy.

They may retain separate table classes because:

- row-per-case and two-row logical matrix schemas differ,
- batch viewport behavior differs,
- batch model/snapshot behavior differs.

Visual commonality does not justify merging their table models or controllers.

---

## 11. Treeview Style Adapter Contract

The Treeview adapter applies the shared visual language to large read-only data tables.

It may own:

- style-name creation,
- Treeview and Heading font,
- row height,
- selection foreground/background,
- border and relief minimization,
- platform-supported header/background configuration,
- fallback behavior where a Tk theme ignores a style option.

It must not own:

- column definitions,
- row insertion,
- selection semantics,
- scrollbars,
- detail schemas,
- copy/export payloads,
- window measurement.

A platform limitation may result in a documented controlled visual exception for large Treeview surfaces. It must not push small fixed result tables back into Treeview.

---

## 12. Current-to-Target Migration Map

| Current surface | Target family | Direction |
| --- | --- | --- |
| Single `MetricInputTable` | Editable Matrix | Keep behavior and schema; adopt shared visual primitives |
| Batch row-per-case table | Editable Matrix | Keep model/controller/viewport; adopt shared visual primitives |
| Batch logical matrix table | Editable Matrix | Keep logical schema/controller/viewport; adopt shared visual primitives |
| ISO/ISEER small result Treeview | Compact Result Grid | Replace Treeview implementation; preserve result/copy/status contracts |
| SASO small result Treeview | Compact Result Grid | Replace after representative ISO migration |
| Brazil result grid | Compact Result Grid | Adopt common rendering primitives; preserve Brazil logic/export |
| Brazil Rule grid | Compact Result Grid | Adopt common rendering primitives with per-cell tones |
| Generic `ResultPanel` summaries | Compact result surface/grid | Adopt common primitives; preserve in-place update/focus/copy compatibility |
| Korea midpoint guide | Compact Result Grid | Migrate as a read-only bounded grid |
| EN14825 small result blocks | Compact Result Grid | Migrate after simpler profiles prove the foundation |
| Bin/detail Treeview | Scrollable Data Table | Keep Treeview; apply shared style adapter |
| Large trace tables | Scrollable Data Table | Keep Treeview; apply shared style adapter |

---

## 13. Ownership and Dependency Direction

```text
visual tokens
    |
    v
Tk table visual policy
    |
    +-- grid primitives
    |      |
    |      +-- editable matrix views
    |      +-- compact result views
    |
    +-- Treeview style adapter
           |
           +-- detail/trace views

profile schema / labels / precision / status
    |
    v
profile view composition

interaction controller
    |
    v
editable table protocol and overlays

profile export adapter/document
    |
    v
profile view action/copy/export path

lifecycle / viewport / shell
    |
    v
surface composition only
```

The visual layer must never become a route from UI into calculator core.

---

## 14. Migration and Helper Cleanup Rules

### 14.1 Incremental migration

Use this sequence for each surface:

```text
shared foundation exists
        |
        v
one target surface adopts it
        |
        v
focused behavior and visual parity proven
        |
        v
obsolete local visual helper removed
```

### 14.2 Do not pre-delete local helpers

Do not remove local helpers from surfaces that have not migrated.

A temporarily duplicated implementation is acceptable during staged migration when:

- only one path is active for the migrated surface,
- the remaining local helper still belongs to an unmigrated surface,
- the migration plan names its removal slice.

### 14.3 Do not mix architecture cleanup with profile behavior change

A migration slice must not also change:

- result fields,
- result ordering,
- visible headings,
- precision,
- optional test-point logic,
- pass/fail rules,
- calculation timing,
- export payloads,
- action availability,

unless a separate approved scope explicitly names that change.

---

## 15. Implementation Slices

## Slice 1 — Table Foundation and ISO Representative Migration

### Purpose

Prove the architecture with one editable input matrix and one compact read-only result table.

### Scope

- add the small Tk table visual-policy owner,
- add shared grid-cell primitives,
- add Compact Result Grid foundation,
- migrate the ISO/ISEER 2-point single input matrix visual construction,
- replace the ISO/ISEER small result Treeview with Compact Result Grid,
- remove only the ISO-local visual helper/code made obsolete by this migration,
- add focused visual and behavior guards for the new foundation.

### Preserve

- all ISO/ISEER numeric results,
- visible result columns and row order,
- status text,
- `as_text()` output,
- table export data,
- whole-table copy,
- auto-calculation,
- selection/edit/paste/clear/undo/navigation,
- invalid-state restoration,
- detail toggle,
- profile switching,
- window refit and viewport behavior.

### Exclude

- Brazil migration,
- generic ResultPanel migration,
- Batch migration,
- detail Treeview styling,
- other profile migration,
- visible Copy/CSV button additions,
- palette changes,
- formula/schema/public API changes.

### Completion evidence

- ISO input no longer uses the heavy outer boxed-grid presentation,
- ISO result no longer uses a small Treeview,
- both surfaces consume the shared visual foundation,
- spreadsheet behavior remains unchanged,
- result copy/status/output remains unchanged,
- no profile or calculation contract changed.

---

## Slice 2 — Generic Result Surfaces and Brazil Adoption

### Scope

- migrate generic result summary rendering to shared compact-result primitives,
- preserve stable in-place updates and external focus behavior,
- migrate Brazil result and Rule rendering to common primitives,
- remove Brazil-local generic cell-rendering duplication,
- preserve Brazil Rule, Final, and sectioned export behavior exactly.

---

## Slice 3 — Remaining Simple Single Surfaces

### Scope

- migrate SASO small result Treeview,
- migrate simple Hong Kong, Korea, and AHRI single input/result surfaces,
- migrate Korea midpoint guide,
- preserve all optional/read-only role switching and profile-local schemas.

---

## Slice 4 — Batch Tables

### Scope

- migrate row-per-case and logical-matrix batch visual construction,
- remove repeated batch header/body cell construction,
- preserve controllers, overlays, snapshots, scroll containment, auto-calc, pending/error counts, and export behavior.

Visible action-row wording/order remains a separate presentation concern unless explicitly included in the approved Slice 4 prompt.

---

## Slice 5 — Detail and Trace Tables

### Scope

- apply Treeview style adapter to shared detail/trace tables,
- preserve detail schemas, source selectors, copy/CSV, collapsed default state, and viewport/refit behavior,
- leave graphs unchanged.

---

## Slice 6 — EN14825 Complex Surfaces and Final Parity

### Scope

- migrate EN14825 common/design/climate matrices and compact result blocks,
- preserve dynamic climate/availability behavior,
- finish the active surface migration inventory,
- remove remaining migrated-surface visual helper duplication,
- confirm every active table maps to one of the three families.

---

## 16. Compatibility Conditions

Every implementation slice must preserve the following unless the slice explicitly states otherwise:

- calculator numeric results,
- formulas and goldens,
- fixtures and region configurations,
- capability/profile contracts,
- public result keys and diagnostics,
- visible table schema,
- labels and precision,
- auto-calculation timing,
- single/batch input behavior,
- selection/edit/paste/clear/undo/navigation,
- invalid/read-only/result role behavior,
- dialog close/reopen state,
- Copy/CSV payload, order, headings, precision, and filename,
- detail and graph data,
- lifecycle ownership,
- viewport and window refit behavior,
- existing semantic palette values.

---

## 17. Validation Matrix

## 17.1 Shared visual foundation

Prove:

- no heavy outer boxed-grid default,
- low-contrast divider policy,
- header/body font and padding policy,
- alignment-role mapping,
- semantic role/tone mapping,
- overlay application and underlying-state restoration,
- no dependency on profile or calculator core.

## 17.2 Editable Matrix

Prove:

- selection and active cell remain distinct,
- edit mode remains distinct from selection mode,
- invalid appearance returns after selection moves,
- read-only cells cannot be mutated,
- copy/paste/clear/undo/navigation remain unchanged,
- auto-calc callback behavior remains unchanged,
- preferred size and refit remain stable.

## 17.3 Compact Result Grid

Prove:

- exact headers and rows,
- whole-table TSV copy,
- clear/pending/error behavior,
- per-cell tone application,
- focus behavior,
- `as_text()` and export compatibility,
- no accidental row/column reordering.

## 17.4 Scrollable Data Table

Prove:

- style adapter does not alter data schema,
- scrolling and viewport containment remain stable,
- copy/CSV remains stable,
- source switching remains stable,
- platform fallback is bounded and documented.

## 17.5 Migration boundary

For each slice, prove:

- only named surfaces migrated,
- no calculation or schema drift,
- obsolete local helpers were removed only from migrated surfaces,
- no new duplicate visual helper was introduced outside the shared owner.

---

## 18. Closed Decisions

The following Slice 0 questions are closed by this design.

### 18.1 Small result Treeview treatment

**Decision:** Small fixed result Treeviews migrate to Compact Result Grid.

Style-only Treeview is not the long-term architecture for ISO/ISEER or SASO result comparison.

### 18.2 Brazil design fidelity

**Decision:** Brazil is a visual reference, not a pixel specification.

The target is a comparable level of refinement, consistency, and semantic clarity.

### 18.3 One universal table widget

**Decision:** Rejected.

Use three table families and shared primitives/policy.

### 18.4 Single-result Copy/CSV buttons

**Decision:** Capability and visual action availability remain separate.

All relevant result surfaces may expose shared copy capability, but visible Copy/CSV buttons are not added or removed during table-family migration unless a separate presentation slice approves the workflow change.

### 18.5 Palette replacement

**Decision:** Deferred.

Reuse current semantic color values. Evaluate palette modernization only after structural visual unification is complete.

---

## 19. Deferred Decisions

These are intentionally outside this architecture design:

- global language policy for batch actions/status text,
- Calculator-wide action-row ordering,
- adding visible Copy/CSV controls to profiles that currently lack them,
- graph visual redesign,
- palette replacement,
- non-Calculator UI adoption,
- packaging and deployment validation,
- AHRI multi-capacity UI additions.

---

## 20. Final Acceptance Criteria

The table-architecture migration is complete when:

1. Every active Calculator table is classified as Editable Matrix, Compact Read-only Result Grid, or Scrollable Data Table.
2. Tables in the same family use the same shared visual foundation.
3. Small fixed result tables no longer use Treeview.
4. Large scrollable detail tables continue to use Treeview through the shared style adapter.
5. Editable Single and Batch tables share visual primitives while retaining their existing models and controllers.
6. Migrated surfaces no longer retain duplicate local header/cell/divider helpers.
7. Profile schema, calculation, status, and export meanings remain profile-local.
8. Existing semantic colors and interaction behavior remain intact.
9. Calculator tables present one coherent, modern visual language without depending on one screenshot or one operating-system theme.
10. Focused automated evidence protects behavior and visual-role restoration for each migrated family.

---

## 21. Repository Integration Note

When this document is first added to the repository:

- place it in the active design-document location selected by the repository’s current design lifecycle,
- update the active design index if required,
- update the current work plan only if the active slice or next action changes,
- treat this document as the design owner for the Calculator table-architecture migration,
- use the existing Slice 0 audit as inventory evidence rather than duplicating that audit here.

The next implementation prompt should direct the agent to implement **Slice 1 only** from this design after placing and indexing the document.
