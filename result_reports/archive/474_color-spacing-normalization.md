# 474 Color and Spacing Normalization

## Goal

Centralize the audited graph palette and repeated calculator option-row spacing
without redesigning the UI or mechanically tokenizing every number.

## Results

- Added semantic bin-detail graph tokens for canvas, border, axis, grid, and
  series colors while preserving the exact existing appearance.
- Added semantic option-row tokens for vertical rhythm and label/group gaps.
- Applied spacing tokens only to repeated EN14825/AHRI main option-bar roles.
- Left profile card spacing, table gaps, graph geometry, and runtime canvas
  sentinels local because their shared meaning was not established.

## Verification

- Focused AHRI/EN main and four detail suites: 90 tests passed.
- A graph construction assertion verifies canvas and border colors resolve to
  their semantic tokens.
- Structure guard passed hard rules with existing hotspot warnings.
- Code map was stale after the preceding commit and regenerated once.
- Diff check passed; cached staged gate recorded at commit closeout.

## Changed Files

- `apps/calculator/ui/layout_constants.py`
- `apps/calculator/ui/sections/bin_detail_panel.py`
- AHRI SEER2/HSPF2 and EN14825 SEER/SCOP main sections
- `tests/test_ui_tk_en14825_seer_detail.py`
- `docs/designs/2026-06-21-ui-magic-literal-legacy-inventory.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/474_color-spacing-normalization.md`

## Architecture Judgment

Graph palette and option-row rhythm are presentation policies owned by shared
tokens. Graph coordinate/margin arithmetic remains with the graph view because
it is layout geometry, not a cross-surface design token. This boundary improves
extension without introducing a theme framework or spacing DSL.

## Known Risks

- EN sections gained bounded token wiring in existing hotspots; no behavior or
  responsibility was added.
- Named Tk colors preserve current rendering but remain platform-resolved, just
  as before this migration.
- Active report cleanup is explicitly excluded from the arc.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  code_map_check: regenerated
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

`hotspot_delta: accepted-for-slice` covers existing constructor spacing
arguments in EN sections only; it adds no section responsibility.

Read Ledger:

- graph/detail color matches: targeted constructor/draw ranges; reason: migrate
  complete palette roles without altering data or graph math.
- AHRI/EN main option-bar spacing matches: targeted constructor ranges; reason:
  confirm repeated semantic rhythm.
- focused main/detail tests and inventory paragraphs: selected ranges; reason:
  preserve construction and record exclusions.
- broad read: none.
- repeated read: none.

## Commit / Push

This slice is committed independently and pushed once with the complete arc.

## Next Suggested Action

Formalize the remaining profile-specific UI literal exceptions.
