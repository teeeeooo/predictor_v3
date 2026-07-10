# UI Magic Literal Legacy Inventory

## Status

Formalized legacy disposition record. This is an audit/design record, not the
active gate policy owner.

Active policy remains in
`docs/agent_workflows/AGENT_CHANGE_GATES.md`; shared Tkinter tokens currently
live in `apps/calculator/ui/layout_constants.py`.

## Goal

Separate grandfathered production UI presentation literals from domain values,
classify reusable token candidates versus justified profile-local values, and
define reviewable cleanup slices that do not attempt a broad mechanical rewrite.

## Audit Boundary and Method

- Baseline: main at closeout commit `380626d`.
- Production scope: Python files under `apps/calculator/ui/`.
- Token-owner exclusions: `layout_constants.py` and `*token*.py`.
- Method: pattern-first `rg` inventory, per-file hotspot counts, then only the
  matching owner ranges for semantic classification.
- Excluded as domain/behavior values: standard temperatures, point order,
  region identifiers, calculator defaults, conversion factors, debounce timing,
  mock/sample input, and core/config/schema values.

Counts are search evidence, not a promise that every numeric match is a token
candidate. Generic `width=` and `height=` include canvas allocation and widget
state values that require owner review before migration.

## Inventory Snapshot

| Category | Grandfathered matches | Current gate coverage | Primary owners/hotspots | Classification |
| --- | ---: | --- | --- | --- |
| `row_header_chars` / `data_column_chars` numeric arguments | 16 | Phase 1 blocks newly staged lines | AHRI HSPF2 (6), EN14825 SCOP (4), AHRI SEER2 (2), EN14825 SEER (2), EN14825 tab (2) | High-confidence table token candidates; preserve distinct semantic roles rather than one universal number. |
| Legacy `width_chars` arguments | 7 | Not covered by Phase 1 | Hong Kong CSPF legacy batch spec | Profile-schema candidates until that legacy batch surface joins the common BatchMatrix token model. |
| Profile `min_size` pairs | 7 | Phase 1 blocks newly staged property/assignment/keyword pairs | AHRI SEER2/HSPF2, EN14825 SEER/SCOP, HK CSPF, ISO ISEER, SASO T3 dialogs | Audit against natural-content fitting first; remove redundant minima or name only true safety floors. |
| Fixed `geometry("WxH")` | 0 | Phase 1 blocks new calls | none | No legacy migration needed. Keep zero. |
| Numeric `padx` / `pady` assignments | 171 | Not covered by Phase 1 | EN14825 SCOP section (16), SCOP batch (12), AHRI HSPF2 section/batch (10 each), result/detail/common profile surfaces | Repeated rhythm candidates; local asymmetric tuples may remain composition-specific. |
| Generic numeric `width=` assignments | 39 | Not covered by Phase 1 | common input controls, result text/Treeview columns, canvas/window allocation helpers | Mixed: control/readability tokens, profile result-schema widths, and non-token runtime allocation. |
| Numeric height assignments | 9 | Not covered by Phase 1 | ISO/SASO result tables, result/detail panels, viewport/scrollable helpers | Separate row-count semantics from pixel presentation and runtime allocation. |
| Hex colors outside token owner | 0 | Phase 1 blocks new `#RRGGBB` | none | Centralization is already complete for scanned hex colors. |
| Hex colors in `layout_constants.py` | 14 | Token owner exempt | common table/result palette | Existing shared palette; do not duplicate per profile. |
| Named colors outside token owner | 0 | Not covered by Phase 1 | none in audited graph/detail surfaces | Bin detail graph canvas, border, axis/grid, and series colors now have semantic tokens with appearance preserved. |
| Raw font tuples outside token owner | 0 | Not covered by Phase 1 | none found | Existing table fonts are centralized; preserve owner. |

## Hotspot Interpretation

### Main metric tables

- AHRI option, point, A2 anchor, and heating matrices now use distinct semantic
  row/data width tokens rather than a universal table width.
- EN14825 SEER/SCOP compact label/data roles now share tokens only where the
  same table font, padding, and content role are present.
- ISO/ISEER and SASO comparison result columns use pixel tokens separated into
  value, profile-label, and scenario-label roles; result schema/export order is
  unchanged.

### Batch and dialog surfaces

- Common BatchMatrix point/result/leading-column widths are already tokenized.
- Hong Kong CSPF's older `BatchColumnSpec.width_chars` declarations remain a
  profile-schema exception until its owner is deliberately migrated; copying
  those values into common BatchMatrix tokens would conflate table models.
- The seven former profile-specific dialog `min_size` pairs were audited
  against requested/preferred content size. Their width and initial-height
  roles were redundant with natural-content fitting, so they now share one
  shell-role safety floor; initial geometry remains content-owned.

### Controls, results, and detail surfaces

- Repeated numeric entry, appliance/equipment type selector, short region-code
  selector, and detail-series selector widths now use semantic control-role
  tokens. Wider profile/region label selectors and profile-local auxiliary
  widths remain inventory items because their vocabulary differs.
- ISO/SASO result Treeview column pixels and result text widths are comparison
  schema/presentation values. They need result-surface tokens, not batch tokens.
- Canvas/viewport `width=0/1` and related height sentinels are runtime geometry
  state, not presentation tokens. They are excluded unless an audit shows a
  stable visual policy meaning.
- Shared option-row vertical rhythm and label/group gaps now use control-role
  spacing tokens in EN14825/AHRI main surfaces. Profile card/table spacing that
  only happens to share a number remains local.

## Token Taxonomy

| Family | Owner and naming rule | Intended examples | Exclusions |
| --- | --- | --- | --- |
| Common table | `layout_constants.py`; name the role and unit (`*_CHARS`, `*_PX`) | row label, numeric data, result data, header/body padding | standard point labels and values |
| BatchMatrix | existing `BATCH_MATRIX_*` family | leading columns, point columns, primary/secondary result | legacy non-BatchMatrix schemas |
| Dialog/window | common geometry owner for ratios/caps; tokens only for genuine safety floors | screen ratios, visible margins, fallback minimum | profile natural content dimensions copied as constants |
| Common input/control | shared control role plus content class | compact selector, numeric entry, long profile selector | one-off widths justified by unique vocabulary |
| Color/font/spacing | semantic surface role, not hue or number | graph canvas background, compact control gap, section inset | names such as `BLUE_1`, `PAD_6` without meaning |
| Profile-specific | feature-local `*tokens.py` only after reuse evidence inside that profile | comparison-result schema columns, specialized graph viewport | single-use literals moved only to silence a gate |

### Promotion rule

Promote a literal when at least two consumers share the same semantic role,
unit, font/padding assumptions, and resize behavior. A repeated number alone is
not reuse evidence. Token names describe why the value exists; they do not
encode the value (`PAD_6`) or a temporary implementation (`AHRI_WIDTH`).

### Profile exception rule

Keep a value profile-local when its required width derives from profile-owned
label vocabulary, column schema, or visualization density and changing it has
no cross-profile contract. Document the reason beside the profile token owner.
Do not use profile-local tokens to override a common surface merely because a
profile currently clips; fix the common owner first.

## Gate and Grandfathering Boundary

Phase 1 scans only newly added staged production UI lines. It currently rejects
numeric row/data character widths, numeric-pair min sizes, fixed geometry calls,
and hex colors. The snapshot above is grandfathered evidence, not an exemption
catalog and not permission to copy values.

The following remain outside Phase 1 and therefore rely on inventory-driven
cleanup/review: legacy `width_chars`, generic control width/height, spacing,
named colors, and semantic misuse of an existing token. Gate expansion must be
warning-first or pattern-focused with false-positive tests; do not turn this
inventory into an all-numeric linter.

## Final Exception and Exclusion Ledger

| Owner | Remaining value family | Disposition and reason | Revisit trigger |
| --- | --- | --- | --- |
| Hong Kong CSPF legacy batch spec | seven `BatchColumnSpec.width_chars` values | Profile-schema exception: this row-per-case schema has vocabulary and column roles different from `BatchMatrixSpec`; copying common matrix tokens would couple models. | Deliberate migration of this profile to a common batch model. |
| ISO profile/mode selectors | selector widths for long profile and region labels | Profile vocabulary exception: character widths are derived from the registered display labels, not compact code selectors. | Shared long-label selector component with a second consumer. |
| EN14825 common-input tab table | local 8/8 row/data widths | Profile composition exception: the sole top-level standby/off-mode input surface has a unique one-row/four-column density and no second consumer with the same role. | A second top-level common-input table with the same font/padding/resize contract. |
| EN14825 SCOP batch/common labels | auxiliary numeric entry, fixed appliance label, and Tdesign label widths | Profile vocabulary exception: widths are tied to this profile's condition labels and fixed option text. | Vocabulary expansion or reuse in another profile. |
| ISO/ISEER and SASO result tables | hidden copy-buffer text widths/heights | Non-visible implementation state: Treeview presentation now uses result tokens; hidden text dimensions do not size the visible surface. | The text buffer becomes visible UI. |
| Common ResultPanel fallback text | local text width/height | Owner-local single-use fallback presentation, not a repeated cross-surface role. | A second fallback text surface with identical behavior. |
| Bin detail graph | stroke width, point radius, margins, canvas height | Visualization geometry exception: these values jointly define one compact graph and are not spacing/palette tokens. | A second graph implementation or a graph sizing policy redesign. |
| Viewport/scroll helpers | zero/one widths and dynamic heights | Runtime allocation state, not presentation policy. | Evidence that a value controls stable visual appearance rather than widget state. |
| Remaining asymmetric `padx`/`pady` | profile card, table, and action composition | Composition-local exception: numeric equality alone does not prove a shared rhythm. | Two consumers with the same role, unit, font, and resize assumptions. |

This ledger is the grandfathering disposition for the audited scope. It does
not authorize copying any listed literal into new staged code; new use still
requires a semantic owner or an approved gate exemption.

## Completed Cleanup Slices

### Slice 1 — Batch dialog minimum-size audit

- Allow: seven BatchDialog adapter `min_size` properties, shell sizing tests,
  geometry token owner if a genuine shared safety floor is proven.
- Forbid: changing natural fitting, adding fixed geometry/horizontal scroll,
  shrinking point/result tokens, or unrelated profile layout.
- Verify: focused shell/content-sizing and all affected dialog profile tests;
  relation assertions, not exact platform pixels.

### Slice 2 — Common input/control width tokens

- Allow: repeated numeric entry and compact selector widths plus focused profile
  UI tests; introduce semantic control-role tokens.
- Forbid: table column widths, label text changes, domain defaults, and broad
  spacing edits.
- Verify: focused AHRI/EN/ISO profile construction and label/readability checks.

### Slice 3 — Main table and result width tokens

- Allow: raw row/data character widths, result text/Treeview column widths, and
  role-specific table tokens.
- Forbid: BatchMatrix behavior, point order, result schema, or one universal
  table-width token.
- Verify: focused table structure/export/result-shape tests plus code structure
  and UI literal gate.

### Slice 4 — Color and spacing normalization

- Allow: named graph background and repeated section/control rhythm values with
  semantic palette/spacing tokens.
- Forbid: palette redesign, screenshot-driven restyling, or mass replacement of
  every `3/4/6/8/10` occurrence.
- Verify: focused result/detail/table construction tests and manual visual smoke
  only where token equivalence cannot prove appearance preservation.

### Slice 5 — Profile-specific exception formalization

- Allow: remaining HK/ISO/SASO schema widths and specialized graph/result values
  in feature-local token owners, each with an ownership note.
- Forbid: cross-profile commonization without shared-role evidence and legacy
  batch-model migration hidden inside token cleanup.
- Verify: profile-focused tests and a final inventory delta; remaining literals
  must be explicitly classified, not merely unscanned.

## Exit Criteria Result

The five slices completed in order without changing calculation, schema, point
order, export content, or public API. Every remaining audited match is now
classified as runtime/hidden state, owner-local single use, or a documented
profile/composition exception with a revisit trigger.

## Next Action

Detail formatting helper structure audit.
