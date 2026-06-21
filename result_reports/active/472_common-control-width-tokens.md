# 472 Common Control Width Tokens

## Goal

Name repeated calculator input and selector widths by semantic control role
without conflating them with table-column sizing.

## Results

- Added distinct tokens for numeric entries, appliance-type selectors,
  equipment-type selectors, short region codes, and detail-series selectors.
- Applied them to matching EN14825/AHRI main and batch controls plus the shared
  detail graph selector.
- Kept wider profile/region label selectors and auxiliary profile-local widths
  out of the common set because their vocabulary and role differ.
- No table width, label, default value, schema, calculation, or spacing changed.

## Verification

- Focused AHRI/EN main, batch, and detail construction suites: 106 tests passed.
- Width relation assertions now guard the EN appliance and AHRI equipment
  selectors against raw literal regression.
- Structure guard passed hard rules with existing hotspot warnings.
- Code map was stale after the preceding commit and regenerated once.
- Diff check passed; cached staged gate recorded at commit closeout.

## Changed Files

- `apps/calculator/ui/layout_constants.py`
- matching AHRI/EN section and batch profile control constructors
- `apps/calculator/ui/sections/bin_detail_panel.py`
- three focused main-section tests
- `docs/designs/2026-06-21-ui-magic-literal-legacy-inventory.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/472_common-control-width-tokens.md`

## Architecture Judgment

Tokens are split by control meaning rather than numeric value. Main and batch
surfaces reuse a token only when they expose the same option vocabulary and
font/character-width assumption. This keeps presentation policy in the token
owner without creating a universal width abstraction or leaking profile state.

## Known Risks

- EN section hotspots gained import/wiring lines only. Their existing size is
  accepted for this bounded slice; no responsibility was added.
- The AHRI HSPF2 main region selector moves from four to the shared five
  character region-code width used by its batch peer, improving parity without
  changing values or behavior.
- Active-report cleanup remains explicitly out of scope.

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

`hotspot_delta: accepted-for-slice` covers token imports and one constructor
argument in each EN section only; it adds no calculation or orchestration.

Read Ledger:

- calculator section/batch `Entry` and `Combobox` width matches: targeted
  constructor ranges; reason: classify semantic control roles.
- focused AHRI/EN construction tests: selected initialization ranges; reason:
  anchor actual widget widths.
- legacy inventory control section: targeted paragraph; reason: record resolved
  and deferred categories.
- broad read: none.
- repeated read: none.

## Commit / Push

This slice is committed independently and pushed once with the complete arc.

## Next Suggested Action

Name main metric-table and result-surface widths by their distinct roles.
