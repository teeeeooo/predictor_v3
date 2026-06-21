# 468 Centralize Calculator Cell Backgrounds

## Goal

Give calculator table surfaces one semantic background policy while leaving
editability and invalid-state ownership with each surface.

## Scope

- Added a pure `editable` / `invalid` presentation helper under the table owner.
- Routed metric-input, batch-matrix, and batch-case cell backgrounds through it.
- Preserved EN14825 invalid-state resolution through the metric table boundary.
- Added focused policy tests and regenerated the code reference map.

## Non-goals

- No calculation, schema, fixture, golden, lifecycle, role enum, or table data
  behavior changed.
- No pass/unavailable coloring or visual redesign was introduced.

## Results

- Editable cells resolve to the editable token, read-only/result/disabled cells
  resolve to the static token, and invalid state overrides either role.
- The shared helper imports no Tk, model, section, `CellRole`,
  `BatchColumnRole`, or `MatrixCellKind` type.
- Each table surface still decides whether a concrete cell is editable.

## Verification

- Focused cell policy, metric table, batch table, EN14825 SEER, and EN14825
  SCOP suites: 110 tests passed.
- Structure guard passed hard rules with the existing four soft warnings.
- Code map was stale from the preceding commit and regenerated once.
- Diff check passed; cached staged gate recorded at commit closeout.

## Changed Files

- `apps/calculator/ui/table/cell_background.py`
- `apps/calculator/ui/metric_input_table.py`
- `apps/calculator/ui/batch/matrix_table.py`
- `apps/calculator/ui/batch/case_table.py`
- `tests/test_apps_calculator_ui_cell_background.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/468_centralize-calculator-cell-backgrounds.md`

## Architecture Judgment

The helper is a presentation policy, not a controller or domain abstraction.
Its two booleans are the smallest stable interface shared by all three table
shapes. Keeping role interpretation in each surface preserves MVC/SoC and
avoids coupling unrelated table models through a new role hierarchy.

## Known Risks

- Existing section and adapter soft-size warnings remain; this slice adds no
  responsibility to those hotspots.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  code_map_check: regenerated
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- allowed table surfaces and EN14825 background call sites: matched ranges;
  reason: locate editability owners and all dynamic background decisions.
- focused table and EN14825 tests: matched test ranges; reason: preserve the
  role/invalid contract.
- latest active report and code-map status: focused ranges; reason: report and
  regeneration continuity.
- broad read: none.
- repeated read: none.

`hotspot_delta: accepted-for-slice` is limited to replacing presentation-token
selection calls in `metric_input_table.py`; no responsibility or behavior was
added to the existing hotspot.

## Commit / Push

This slice is committed independently. All arc commits are pushed together
after final validation.

## Next Suggested Action

Remove remaining live `app_calculator_tk` naming and stale guide wording.
