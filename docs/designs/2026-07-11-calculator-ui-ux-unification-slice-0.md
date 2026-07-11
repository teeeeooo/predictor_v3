# Calculator UI/UX Unification — Slice 0 Audit

## Goal

Active Tkinter Calculator surfaces at main HEAD
`6487935729c3be97e3655fcac0aa629e199d0346` were audited to define a shared
table visual policy, preserve profile-local contracts, and sequence later
implementation slices. This record changes no Calculator source, tests,
formula, fixture, config, schema, palette, or public API.

## Confirmed target table visual policy

The Brazil CSPF single result table and Rule table are the visual reference,
not a pixel specification.

- Table boundaries use the existing low-contrast `border.default` binding as
  thin dividers; a strong black outer frame is not part of the target.
- Headers use the existing neutral `table.header` background, bold table
  header font, and consistent internal padding.
- Bodies sit flat inside their section and use consistent row height/padding.
  They must not read as a second heavy panel nested inside a section.
- Alignment follows column role: row identity and descriptive text left;
  numeric/input/result values centered by default; dense numeric result/detail
  columns may use right alignment when the whole column does so consistently.
- The audit does not introduce or replace any concrete palette value.
- Existing meanings remain distinct: editable, fixed/read-only, calculated,
  OK/Pass, NG/Fail, invalid, pending/blank, selected, active/focus.
- Visual flattening must not weaken selection versus active cell, selection
  versus edit mode, invalid feedback, or read-only protection.

## Active surface inventory

### Entry, navigation, and lifecycle

| Surface | Active user-visible behavior | Current owner | Guard evidence |
| --- | --- | --- | --- |
| App shell | Hidden-first Tk root titled `Seasonal Efficiency Calculator`; top notebook exposes ISO 16358, EN14825, AHRI 210/240, and KS C 9306. | `apps/calculator/ui/calculator_app.py`, `theme.py` | `test_ui_tk_calculator_foundation.py` |
| ISO profile navigation | Profile combo selects ISO/ISEER 2-point, Hong Kong, SASO T3, or Brazil CSPF. Hong Kong adds region selection and CSPF/HSPF metric tabs. Cached independent mode surfaces are reused; Hong Kong region sections are rebuilt only when region changes. | `tabs/iso16358_tab.py`, application profile resolver | foundation and profile/controller-switch tests |
| Other profile navigation | EN14825 has SEER/SCOP tabs, AHRI has SEER2/HSPF2, and Korea has CSPF/HSPF. | `tabs/en14825_tab.py`, `ahri210240_tab.py`, `korea_tab.py` | tab, profile-switch, and refit tests |
| Main viewport | Each top-level tab uses `ScrollableFrame`; vertical scrolling appears on overflow and mouse-wheel routing is scoped to the surface. | `scrollable_frame.py` | calculator foundation tests |
| Main refit | One lifecycle controller owns measurement, settle scheduling, selected-profile refit, detail-open refit, and scroll reset. | `ui/lifecycle/`, window measurement/refit/shell modules | profile lifecycle, window lifecycle, measurement/refit tests |
| Batch dialog lifecycle | One Toplevel shell builds hidden, measures natural content, applies min/screen-capped parent-centered geometry, then shows. Close snapshots input and destroys the shell; reopen restores state. | `batch_dialogs/shell.py`, `dialog_handle.py`, `batch/viewport.py` | batch shell, handle, content-sizing, viewport tests |

The production path is `apps.calculator.app` to the Tk package above. The old
PyQt Calculator under `ui/` is reference/retired for this workstream and must
not be treated as an active surface. `batch/compat_table.py` is a compatibility
alias into the active table controller contract, not a second user-visible
table. Disabled compatibility-only calculator profiles such as AS/NZS Excel
HSPF are not selectable active Calculator UI surfaces.

### Shared surface families

| Family | Active behavior | Current implementation and visual behavior | Gaps |
| --- | --- | --- | --- |
| Single input matrix | Immediate/debounced calculation; spreadsheet selection/edit/paste/clear/undo/navigation; editable/static/read-only/invalid roles. | `MetricInputTable` builds nested `tk.Frame` cells on a one-pixel grid-color gutter inside a `borderwidth=1`, `relief=SOLID` outer frame. Header is neutral/bold; editable/static semantic backgrounds come from layout tokens. | Interaction is shared and guarded, but the outer frame remains visually boxed. Visual construction is embedded in the large input widget rather than a named Tk table-surface policy. Focus is represented mainly by controller active color; owner language calls for focus and active semantics to remain explicitly distinguishable. |
| Generic single result summary | Compact title/header/value/status blocks; stable in-place value update preserves external focus; hidden text buffer provides copy compatibility. | `ResultPanel` repeats the same one-pixel cell gutters and solid one-pixel outer card per summary. | Common summary structure exists, but section-local result tables do not all use it; no shared result/export visual surface contract binds Treeview and cell-rendered variants. |
| Read-only comparison result | Profile comparison/scenario rows with Copy/select-all and status. | ISO/ISEER 2-point and SASO T3 use native `ttk.Treeview` with fixed pixel widths. Brazil uses flat cell-rendered grids. | Treeview header/border/row density are theme-native and visually diverge from Brazil and `ResultPanel`; fixed columns are profile-local sizing, not shared policy. |
| Rule/Pass/Fail/Final | Brazil renders a Rule table, semantic judgement cells, and explicit final status. Other profiles generally expose result status text rather than a rule matrix. | Brazil `result_surface.py` uses low-contrast grid gutters with semantic Pass/Fail backgrounds. SCOP separately highlights Tested rows with the existing result color. | Brazil is the reference visual implementation, but its rule columns, decision semantics, final status, and sectioned export are profile-local. There is no basis for forcing a Rule table on profiles that do not expose rules. |
| Detail/bin table and graph | Summary first; collapsed detail toggle; optional source selector; read-only table, Copy, CSV, and lightweight Canvas graph. | Shared `BinDetailPanel` and `BinTraceTable`; Treeview supplies the table visuals, Canvas colors include local graph literals. | Behavior and schema adapter are shared; Treeview styling does not yet match the target table surface. Graph palette is outside the first table migration and should not be pulled into it. |
| Batch input/result matrix | Add/remove case, auto-calc valid rows, result/read-only protection, rectangular TSV interaction, Copy All, CSV, and local two-axis scrolling. | `BatchCaseTable` and `BatchMatrixTable` use cell frames, shared semantic backgrounds, and the common controller. Both keep a one-pixel solid outer content frame. Profile dialogs repeat action rows and status labels. | Core behavior is strongly guarded. Visual cell creation is duplicated between single and batch tables; action label/order and English/Korean status copy vary by profile. |
| Pending/error/blank | Single surfaces clear stale results or show concise status; batch calculates valid rows independently and reports valid/pending/blank/invalid counts. | Status is spread across `ResultPanel`, section-local result surfaces, `BinDetailPanel`, and each batch profile's `StringVar`. | Meanings are broadly consistent but wording, placement, language, and whether blank/pending appears in a table or adjacent label remain local and unowned. Do not standardize domain wording in the visual slice. |
| Copy/CSV | Single comparison/result/detail and every active batch path expose table/export actions where applicable. | Shared low-level clipboard/CSV helpers exist; Brazil adds a sectioned export document. Several generic `ResultPanel` profiles have copy-compatible text but no visible single-result Copy button. | Transport helpers are shared; visible action availability and ordering lack a common presentation policy. Brazil sectioned export must remain local. |

## Profile behavior matrix

All single input matrices below use `MetricInputTable` and
`TkTableController` unless stated otherwise. Therefore they share semantic
input colors and spreadsheet behavior, while their schema, labels, optional
cells, precision, and domain status remain profile-local.

| Profile | Single input and frequency | Result / rule / status | Detail and export | Batch and lifecycle | Focused guard status |
| --- | --- | --- | --- | --- | --- |
| ISO/ISEER 2-point | One 2x2 capacity/power matrix; auto-calc. | Native Treeview comparison for ISO/India rows; adjacent status; no Rule/Final surface. | Collapsed shared bin detail with source selector, Copy/CSV. Single result supports keyboard/table copy but has no explicit Copy/CSV action row. | Active dialog with generic case table and snapshot restore. | Good profile/controller, auto-calc, batch, detail guards; no focused target-visual assertion. |
| Hong Kong CSPF | Rated singleton table plus 2x2 test matrix; auto-calc under Hong Kong region/metric navigation. | Generic `ResultPanel` summary and status; no explicit Rule table. | Collapsed shared detail, one source, Copy/CSV. | Active batch matrix; state restored on reopen. | Good resolver, matrix migration, interaction, batch/detail and lifecycle coverage. |
| Hong Kong HSPF | Rated and repeated heating matrices; auto-calc with profile-specific availability. | Generic summary/status. | Collapsed shared heating bin detail. | Two-physical-row logical case matrix, Copy All/CSV, snapshot restore. | Good controller switch, detail, batch matrix and state coverage. |
| SASO T3 | 2x4 capacity/power matrix; 35 Min optional state changes cell role/presentation; auto-calc. | Native Treeview scenario comparison for required/optional paths and adjacent status. | Shared multi-source detail and graph; Copy/CSV. | Active case dialog. | Good optional/read-only controller and batch guards; target visual parity missing. |
| Brazil CSPF | 3-point/2-point-capable input matrix; auto-calc. | Cell-rendered two-row result comparison, cell-rendered Rule table, Pass/Fail judgement cells, explicit Final OK/NG, stale-result clearing. This is the visual reference. | Explicit single-result Copy and Export CSV plus shared detail Copy/CSV; sectioned Brazil export remains local. | Active Brazil-specific schema/presentation with snapshot restore and semantic result-state repaint. | Strong focused result/rule/export, snapshot, stale-state, overlay, and semantic NG guards. |
| KOREA CSPF | Rated singleton plus cooling test matrix; auto-calc. | Generic summary/status plus profile-local midpoint guide table. | Shared bin detail. | Active generic case table with Copy All/CSV and state summary. | Good tab/profile/batch/detail contract coverage; midpoint guide visual policy has only local guards. |
| KOREA HSPF | Rated singleton plus heating matrix; auto-calc. | Generic summary/status plus midpoint guide. | Shared heating detail. | Active case table and snapshot lifecycle. | Good batch/profile/detail coverage; target visual assertions absent. |
| EN14825 SEER | Shared common-input matrix, design matrix, and A-D declared/tested matrix; auto-calc; auxiliary type selector. | Generic summaries for Declared/Tested with localized pending/error statuses. | Shared schema-driven bin detail. | Active dynamic matrix dialog with common inputs, Copy All/CSV, apply/draft status, snapshot restore. | Strong single/batch/detail and profile-switch fit coverage; large section is an implementation-risk hotspot. |
| EN14825 SCOP | Shared common-input matrix, design inputs, three climate cards, availability/read-only cells, and per-climate matrices; auto-calc. | Per-climate cell-rendered Declared/Tested surface plus generic summary/error status; Tested row uses existing semantic result background. | Shared schema-driven detail. | Active dynamic conditions/common-input batch matrix, apply/draft state, Copy All/CSV. | Strong state, result, detail, batch, and refit coverage; largest section and highest migration risk. |
| AHRI SEER2 | Options plus repeated point matrix; auto-calc. | Generic summary/status. | Shared AHRI bin detail. | Active matrix batch with options/common inputs, Copy All/CSV and pending/error counts. | Good single/batch/detail coverage. |
| AHRI HSPF2 | Options plus numeric, A2 anchor, and heating point matrices with conditional read-only cells; auto-calc. | Generic summary/status. | Shared heating bin detail. | Active matrix batch with option apply/draft state, Copy All/CSV. | Good optional-role, batch, detail, refit, and lifecycle coverage. Multi-capacity remains deferred and is not an active surface. |

Usage-frequency ranking for migration risk is: single input/result on every
edit (highest), profile/tab switch and action row (frequent), batch dialog
(periodic), detail/bin review (secondary/collapsed), graph (secondary). This
supports proving the policy on one single surface before batch/detail rollout.

## Semantic state inventory and precedence

Concrete values remain owned by `ui_common.visual_tokens.py` through
`layout_constants.py`; this Slice does not list or replace hex values.

| Priority | State | Current binding / behavior | Preservation rule |
| --- | --- | --- | --- |
| 1 | Invalid | `table.invalid`; editable content retained. | Must remain visible and editable. Selection/active overlays may temporarily cover fill, so the implementation guard must prove invalid returns when the overlay moves. |
| 2 | Active/focus | `table.active` painted by controller; Tk focus/caret distinguishes edit mode. | Must remain distinct from selected range and invalid/default roles. Do not remove visible keyboard focus while flattening borders. |
| 3 | Selected | `table.selected` rectangular overlay. | Preserve range shape and active-cell distinction. |
| 4 | OK/Pass and NG/Fail | Existing `table.result` and `table.invalid` bindings on result-only cells/final labels. | Preserve text plus semantic background; never infer domain pass/fail inside a visual owner. |
| 5 | Fixed/read-only/calculated | `table.fixed`, muted foreground, mutation blocked by role. | Preserve copyability and mutation protection. |
| 6 | Editable | `table.input`. | Preserve normal edit/paste/clear paths. |
| 7 | Pending/blank | Usually `-`, empty result, or adjacent neutral status. | Remain distinct from zero, invalid, and failed calculation. |

This order describes visual conflict handling, not a new palette. Domain result
states apply only on result surfaces; interaction overlays temporarily take
precedence on selectable tables and must restore the underlying semantic role.

## Owner document to source gap audit

### Policy already followed

- Tk is isolated from the retired PyQt Calculator; core does not import UI.
- Repeated inputs are matrix-shaped and schemas stay in profile UI/application
  adapters rather than Calculator core.
- Selection, edit, TSV copy/paste, clear, grouped undo, navigation, per-cell
  roles, and read-only protection have shared owners and focused tests.
- Semantic colors are token-backed; meaningful result/invalid colors survive
  neutral-first chrome.
- Summary-first, collapsed detail, shared detail/export helpers, auto-calc,
  stateful batch reopen, hidden-first dialog construction, and lifecycle refit
  are active shared policies.

### Owner policy not uniformly applied

- The low-contrast divider policy is token-backed, but both single and batch
  input surfaces still add a solid outer frame and read as boxed grids.
- Header/body density is close but not governed by one named Tk visual binding
  across `MetricInputTable`, batch tables, `ResultPanel`, Brazil grids,
  Treeview results, and detail tables.
- Alignment is declared locally; descriptive/numeric role alignment is not a
  shared policy API.
- Focus, active, selected, and invalid meanings exist, but the concrete Tk
  binding does not expose a first-class focus role separate from active fill.
- Result/status/export policy does not define consistent visible Copy/CSV
  availability, action ordering, or bilingual label convention.

### Repeated source policy without a common owner

- Cell frame creation, one-pixel divider gutters, header font/padding, body
  padding, and outer-frame relief repeat across input, batch, result, SCOP, and
  Brazil implementations.
- Section action rows repeatedly order Batch, Detail, Copy, Export differently
  or omit some actions.
- Batch profiles repeat `Add Case`, `Remove Case`, `Copy All`, `Export CSV`, and
  status placement, with variants for apply/options controls.
- Pending/error count phrasing is profile-local despite common state classes.

### Brazil-local policy

- Brazil's lightweight result and Rule grid construction is reusable visual
  evidence.
- Brazil result columns, rule columns, rule interpretation, judgement mapping,
  final status, sectioned export document, filenames, and labels remain local.
- Brazil's explicit single-result Copy/CSV buttons are evidence for a later
  presentation decision, not permission to add them to every profile silently.

### Similarity that must not be commonized

- Profile field maps, row/column labels, precision, visible result schema,
  optional-point logic, climate/scenario grouping, midpoint guide, and domain
  pass/fail calculation.
- Treeview versus cell-rendered choice cannot be erased solely for appearance;
  migration must retain selection/copy/accessibility and viewport behavior.
- Batch `CaseTable` and two-row `MatrixTable` represent different logical
  schemas even when their cells look alike.

## Common policy and profile-local policy

| Concern | Shared candidate | Profile-local remainder |
| --- | --- | --- |
| Border/divider/header/body | Thin divider, no heavy outer frame, header/body fonts, padding and density | Column widths needed by a schema; section-specific grouping breaks |
| Semantic cell binding | Map framework-neutral roles to current Tk tokens | Which cell has which role; domain OK/NG decision |
| Alignment | Alignment by descriptive, numeric-input, numeric-result, status role | Explicit exceptions required by profile content |
| Result summary | Common flat metric/value/status primitives | Fields, order, labels, unit, precision, rule structure |
| Rule/Final | Visual primitives for rule header/body and semantic outcome | Whether rules exist, rule schema, decision text, final calculation |
| Status/error/pending | Placement and neutral/error surface roles | Exact domain message and state transition |
| Copy/CSV | Shared action presentation convention and existing transport helpers | Export document/schema, filename, sectioned Brazil output |
| Action rows | Spacing and proposed order: profile/batch action, detail, copy, export | Controls that do not apply; profile-specific Apply/Options actions |
| Detail toggle | Existing shared visibility controller and label convention | Detail sources, schema, series, summary |
| Section spacing | Shared spacing tokens and heading hierarchy | Legitimate climate/scenario sub-sections |
| Window/dialog | Existing lifecycle/sizing owners | Profile natural content size and minimum justified by content |

## Shared owner recommendation

Do not create a universal Calculator table widget. Extend the existing owners
with one small visual-policy seam:

1. Keep framework-neutral semantic roles in `apps/calculator/ui/table/roles.py`
   (or a toolkit-neutral owner only if a later non-Tk consumer actually needs
   it). Do not add profile schemas here.
2. Keep concrete token values in `ui_common/visual_tokens.py` and the Calculator
   binding aliases in `layout_constants.py`.
3. Add a small Tk table visual-policy/binding owner under
   `apps/calculator/ui/table/` for cell/header/body construction options:
   divider thickness, outer-edge policy, padding/font, and alignment by visual
   role. It returns/configures presentation values; it does not own data,
   calculation, selection, clipboard, validation, or widgets for every table.
4. Keep spreadsheet behavior in `table/controller.py`,
   `interaction_core.py`, and the existing surface protocol. Visual migration
   consumes default/overlay backgrounds but does not change state transitions.
5. Keep `MetricInputTable`, batch table types, `ResultPanel`, profile result
   tables, and detail table as their current schema/view owners. Adopt the
   visual binding incrementally.
6. Keep result/export presentation helpers separate from table interaction.
   A later bounded action-row policy may standardize placement/labels while
   preserving profile export documents.
7. Keep lifecycle in `ui/lifecycle/`, batch shell/viewport, and window owners;
   visual policy must not measure or resize windows.

Dependency direction:

```text
semantic roles + visual tokens
             |
             v
   Tk table visual binding
      |       |       |
      v       v       v
 single view batch view result/detail view
      \       |       /
       existing interaction controller

profile schema/use case/export document -> profile view only
lifecycle controller/shell/viewport      -> composition only
```

This is a repeated-responsibility owner decision, but it does not alter public
or domain contracts. The first implementation Slice must confirm whether this
small seam is sufficient before any broader abstraction is proposed.

## Migration risks

| Risk | Impact | Mitigation / proof |
| --- | --- | --- |
| Flattening removes active/focus clarity | Keyboard users cannot tell selection from edit target | Keep controller overlay contract; add exact background/focus assertions and interactive state-transition tests. |
| Visual repaint hides invalid or result state permanently | Incorrect state meaning | Guard overlay apply/remove and auto-calc repaint restoration for single and batch tables. |
| Shared builder absorbs schema | Domain coupling and broad regressions | Visual policy accepts roles/options only; profile views continue to declare rows, columns, labels, precision. |
| Treeview replacement changes copy/selection/viewport | User-visible regression | Do not replace Treeview in the first Slice; treat it as a later bounded migration with parity tests. |
| Row padding changes initial geometry | Window grows, clips, or scrollbars oscillate | Run focused preferred-size, refit, viewport, and reopen tests in each visual migration Slice. |
| Large EN14825 sections amplify change | Hard-to-localize regression | Migrate after representative and simpler profiles; do not refactor the sections during visual adoption. |
| Action-row unification changes exports | Missing or altered user output | Separate action presentation from export transport/document tests. |
| New token values change semantics | Palette regression | Reuse existing tokens only; no palette changes in this workstream without separate approval. |

## Recommended implementation slices

### Slice 1 — Representative single input and result

- **Purpose:** prove the small Tk visual binding on one editable matrix and one
  read-only result surface.
- **Target:** ISO/ISEER 2-point single screen: `MetricInputTable` input plus its
  comparison result table. Use Brazil result/Rule tables as review reference,
  but do not edit Brazil domain presentation.
- **Shared change:** thin low-contrast dividers, remove heavy outer impression,
  consistent neutral/bold header, body padding/row density, role alignment.
- **Local:** ISO/India rows, labels, widths, precision, status and copy schema.
- **Preserve:** auto-calc, selection/edit/TSV/paste/clear/undo/navigation,
  invalid state, Treeview copy/select-all, detail toggle, refit.
- **Dependency:** visual roles/tokens -> small Tk visual binding -> input and
  ISO result views; controller and use case remain unchanged.
- **Risk:** a Treeview restyle may not reach Brazil-like visual parity without
  replacement. First attempt style-only; if replacement is required, stop for
  a bounded parity decision rather than expanding Slice 1.
- **Verification purpose:** prove visual structure and all interaction overlays
  on the input; prove result copy/status and lifecycle sizing remain stable.

Why first: it is small, default-visible, exercises editable and read-only
surfaces together, and already has strong controller/auto-calc/profile guards.
It tests the owner choice before touching Brazil, batch, or large profiles.

### Slice 2 — Shared generic result summaries and Brazil conformance check

- Migrate `ResultPanel` visual construction to the proven binding and confirm
  Brazil result/Rule tables already conform or need only adapter-level cleanup.
- Keep all summary fields, rule/final logic, copy text, and Brazil sectioned
  export local.
- Verify stable in-place update, focus preservation, pending/error display,
  and Brazil OK/NG/stale-result guards.

### Slice 3 — Remaining simple single input/result profiles

- Apply the proven input binding to Hong Kong, SASO T3, Korea, and AHRI single
  matrices; bring SASO Treeview and Korea midpoint guide into the result policy
  only through bounded view-local changes.
- Preserve optional/read-only cell switching and every profile schema.
- Verify profile-focused controller, auto-calc, detail, and result tests.

### Slice 4 — Batch tables and action/status rows

- Apply the visual binding to `BatchCaseTable` and `BatchMatrixTable`; define a
  shared presentation convention for common Add/Remove/Copy/CSV/status actions
  without changing profile adapters or export schemas.
- Preserve two-row logical cases, per-cell roles, overlay repaint, snapshot,
  local scrolling, natural sizing, and close/reopen state.
- Verify controller parity, batch matrix/case table, dialog sizing, viewport,
  and each profile's export tests.

### Slice 5 — Detail/bin tables

- Restyle the shared Treeview detail table and its action row; graph styling is
  excluded unless separately approved.
- Preserve schema variants, source selection, summary, copy/CSV, collapsed
  default state, and detail-triggered refit.

### Slice 6 — EN14825 complex surfaces and final parity audit

- Migrate shared/common/design/climate matrices and SCOP result blocks after
  the binding has proven stable elsewhere.
- Keep climate activation, availability, result schema, precision and dynamic
  conditions local. Do not combine with section splitting or architecture
  refactoring.
- Run focused SEER/SCOP state, detail, batch, profile-switch and sizing guards;
  finish with a source-level surface/parity inventory delta.

## Compatibility conditions for every implementation Slice

- No numeric result, formula, golden, fixture, region config, capability,
  profile ID, visible schema, public API, or diagnostics change.
- No input loss on dialog close/reopen and no lifecycle ownership movement.
- No change to Copy/CSV data, order, precision, headers, or filenames unless a
  separate explicit approval names that contract.
- Selection, active/focus, edit mode, TSV copy/paste, Delete/Backspace,
  grouped undo, navigation, read-only protection, validation and auto-calc
  remain guarded.
- Existing semantic roles and concrete palette values remain unchanged.
- Each Slice is independently reviewable and stops on an abstraction or
  Treeview parity question that would broaden its boundary.

## Required validation for the first implementation Slice

- Existing focused `MetricInputTable` controller parity and invalid-state tests.
- Existing common table controller/per-cell-role tests.
- ISO/ISEER controller switch, auto-calc, result copy/status, and detail tests.
- Focused visual assertions for no heavy outer border, divider/header/body
  bindings, alignment, selected versus active, invalid restoration, and
  read-only result presentation.
- Existing Calculator foundation/profile lifecycle/window refit tests that
  cover the changed surface; no broad pytest by default.
- Structure guard for changed source plus a changed-file gate confirming no
  formula/schema/export drift.

## Open questions requiring user decision

1. Approve ISO/ISEER 2-point as Slice 1, or choose Brazil single as the first
   implementation surface. Recommendation: ISO/ISEER because it tests a real
   migration rather than merely polishing the reference.
2. If native Treeview styling cannot meet the target without platform-specific
   divergence, approve a cell-rendered read-only replacement with explicit
   copy/selection/accessibility parity, or accept a controlled Treeview visual
   exception. Recommendation: decide only after the Slice 1 style-only spike.
3. Should visible single-result Copy/CSV buttons become a common Calculator
   rule, or remain profile-specific? Recommendation: defer to the result/action
   presentation Slice because adding actions changes the visible workflow even
   when export data does not change.
4. Should user-facing batch action/status text be unified in Korean, English,
   or intentionally follow each standard's current terminology? Recommendation:
   choose one language policy before Slice 4; do not mix copy changes into the
   table visual Slice.

## Non-goals

- Calculator or test implementation in Slice 0.
- Formula, golden, fixture, region config, public API/schema, profile, ML,
  Predictor, Web, packaging, deployment, or AHRI multi-capacity changes.
- A universal table widget, broad architecture refactor, legacy UI revival,
  palette replacement, or pixel-perfect Brazil copy.

## Next action

Review and approve the Slice 1 representative surface and the stop condition
for native Treeview styling. Implementation must start in a separate approved
Slice.
