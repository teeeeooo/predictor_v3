# 473 Main Table and Result Width Tokens

## Goal

Replace raw main metric-table and result-column widths with role-specific
tokens while preserving table shape, result schema, and exports.

## Results

- Named EN compact row/data, AHRI descriptive row, point, A2 anchor, and
  heating data widths separately.
- Named ISO/ISEER and SASO comparison value, profile-label, and scenario-label
  pixel widths and minimums separately.
- Did not introduce one universal table-width token or touch BatchMatrix.
- Hidden text-copy buffer sizes and runtime geometry sentinels were excluded
  because they are not visible column presentation policy.

## Verification

- Focused AHRI/EN main and ISO/SASO result/export suites: 124 tests passed.
- Relation assertions verify value/profile/scenario Treeview columns resolve to
  their semantic tokens.
- Structure guard passed hard rules with existing hotspot warnings.
- Code map was stale from the prior commit and regenerated once.
- Diff check passed; cached staged gate recorded at commit closeout.

## Changed Files

- `apps/calculator/ui/layout_constants.py`
- four AHRI/EN main section table constructors
- `apps/calculator/ui/sections/iso_iseer_2point_result_table.py`
- `apps/calculator/ui/sections/iso_saso_t3_result_table.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `docs/designs/2026-06-21-ui-magic-literal-legacy-inventory.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/473_main-table-result-width-tokens.md`

## Architecture Judgment

Character widths belong to metric table composition; pixel widths belong to
Treeview result presentation. Keeping these units and content roles separate
prevents token reuse by coincidental numeric equality. Existing section/model
and export ownership remains unchanged.

## Known Risks

- EN section hotspots gained token import/wiring lines only. No new
  responsibility was introduced; the delta is accepted for this slice.
- Platform Treeview rendering remains font-dependent, so tests assert configured
  relationships rather than screenshots.
- Active report cleanup remains out of scope.

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

`hotspot_delta: accepted-for-slice` is limited to semantic token imports and
constructor arguments in the existing EN section hotspots.

Read Ledger:

- raw row/data/Treeview width search in allowed main/result surfaces: matched
  ranges; reason: separate role and unit owners.
- ISO/ISEER and SASO result constructors/tests: focused ranges; reason: preserve
  visible and export shapes.
- inventory main/result paragraphs: targeted headings; reason: record completed
  classification.
- broad read: none.
- repeated read: none.

## Commit / Push

This slice is committed independently and pushed once with the complete arc.

## Next Suggested Action

Normalize only shared graph/canvas colors and repeated spacing rhythms.
