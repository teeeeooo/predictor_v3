# 466 Fix EN14825 Editable Cell Background

## Goal

Ensure EN14825 table backgrounds follow cell roles: editable empty/filled cells
use the editable background, read-only/computed cells use the static background,
and invalid cells retain the validation background.

## Scope

- Added one role-based background resolver to the existing common
  `MetricInputTable` presentation owner.
- Routed SEER and SCOP model-state overrides through that owner.
- Removed pass/unavailable tint precedence that painted editable cells according
  to calculation state rather than editability.
- Added focused SEER and SCOP guards for empty, filled, computed, and invalid
  cells.

## Non-goals

- No batch-default, entrypoint, token cleanup, calculation, schema, fixture,
  golden, result surface, or detail payload behavior changed.

## Task Results

- Editable cells remain white whether empty or populated.
- Read-only/computed cells remain gray even when their computed state is pass or
  unavailable.
- Invalid model/input state remains visibly marked with the existing error token.
- Selection/active colors remain controller-owned and unchanged.

## Verification

- Focused EN14825 SEER/SCOP UI suites: 49 tests passed.
- Structure guard passed hard rules with existing soft warnings. The code map
  was stale after Task A and was regenerated once; diff check passed. The staged
  cached gate is recorded at task closeout.

## Reference Parity

The change follows the toolkit table adapter contract: editability determines
the base background, while invalid is a separate visual state. The common table
owner is reused instead of introducing EN-specific color literals or a parallel
style resolver.

## Changed Files

- `apps/calculator/ui/metric_input_table.py`
- `apps/calculator/ui/sections/en14825_seer_section.py`
- `apps/calculator/ui/sections/en14825_scop_section.py`
- focused EN14825 SEER/SCOP UI tests
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/466_fix-en14825-editable-cell-background.md`

## Known Risks

- Final color appearance should still be visually confirmed on the target macOS
  theme; automated tests assert the semantic token values applied to frames and
  widgets.

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

Hotspot reason: the already-large common input table gains only a cohesive
role-to-background helper, while the large EN sections lose duplicated branch
logic and responsibility.

Structure Warnings: the existing EN section and SCOP adapter soft warnings are
unchanged; no new responsibility was added to those sections.

Read Ledger:

- `metric_input_table.py`: cell role/default background and invalid-state ranges;
  reason: confirm the common presentation owner.
- EN14825 SEER/SCOP sections: `_resolve_cell_bg` ranges only; reason: identify
  state precedence causing gray editable cells.
- EN table models: `get_state` ranges; reason: confirm empty inputs are reported
  as unavailable before role resolution.
- UI table contract/toolkit adapter cell-state sections; reason: preserve
  editable/read-only/invalid semantics.
- focused EN tests: existing tint and section fixture ranges; reason: add
  relationship guards without pixel assertions.
- broad read: none.
- repeated read: none.

## Commit / Push

Task B is committed independently. Push is intentionally deferred until Task C
and final validation complete.

## Project Memory Delta

No memory update is needed; this is a narrow correction to the existing table
role contract.

## Next Suggested Action

Task C: migrate live references to the canonical calculator entrypoint and
delete `app_calculator_tk.py`.
