# 465 Remove Calculator Batch Sample Defaults

## Goal

Make ISO/ISEER, Hong Kong CSPF, and SASO T3 batch matrices open without
product-performance demo values while preserving their five-case shape,
automatic calculation, result formatting, and snapshot restoration contracts.

## Scope

- Replaced the first populated default case with an empty case in the ISO/ISEER
  and SASO profile specs.
- Replaced the Hong Kong CSPF common BatchMatrix spec default sample with an
  empty case at its actual shared spec owner.
- Kept five initial logical cases for every affected matrix.
- Updated focused tests to inject explicit samples only where calculation,
  copy, undo, or export behavior requires them.

## Non-goals

- No EN14825 cell-background work, entrypoint migration, UI token cleanup,
  equation, schema, config, fixture, golden, lifecycle, or snapshot behavior
  changed.

## Task Results

- ISO/ISEER and SASO batch dialogs expose blank performance inputs on first
  open; their result keys may still be materialized as blank by auto-calc.
- Hong Kong CSPF now follows the same production empty-state contract.
- EN14825 and AHRI batch specs were audited and already had no product sample
  default cases, so they were not changed.
- Restored user snapshots remain authoritative and are not treated as defaults.

## Verification

- Focused batch suite: 58 collected; 56 passed and two dialog assertions were
  corrected to distinguish blank input keys from blank result keys created by
  auto-calc. The two affected files then passed all 8 tests.
- Structure guard passed hard rules with existing soft warnings. The code map
  was stale from the preceding commit and was regenerated once; diff check
  passed. The staged cached gate is recorded at task closeout.

## Reference Parity

The existing main-profile empty-state policy was applied to batch matrices:
blank product inputs, retained structural cases, automatic waiting results, and
unchanged explicit snapshot restoration. Test samples remain test-owned.

## Changed Files

- `apps/calculator/ui/batch/matrix_models.py`
- `apps/calculator/ui/batch_dialogs/profiles/iso_iseer_2point.py`
- `apps/calculator/ui/batch_dialogs/profiles/saso_t3.py`
- focused ISO/ISEER, SASO, Hong Kong CSPF, and common BatchMatrix tests
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/465_remove-batch-sample-defaults.md`

## Known Risks

- Visual confirmation of initially blank batch dialogs remains a manual smoke
  item; focused widget/spec tests guard the input contract.
- `matrix_models.py` was required even though the initial candidate list focused
  on profile modules, because it is the actual owner of the production Hong
  Kong CSPF BatchMatrix spec.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: regenerated
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Structure Warnings: existing warnings only; this slice removes default mapping
entries and adds no production responsibility.

Read Ledger:

- batch profile specs: default-case ranges only; reason: locate production
  sample ownership.
- `apps/calculator/ui/batch/matrix_models.py`: Hong Kong CSPF spec range;
  reason: confirm the shared spec is the real default owner.
- focused batch tests: default-case, snapshot, calculation, copy/export ranges;
  reason: move sample dependence into test setup.
- broad read: none.
- repeated read: two dialog assertions after auto-calc materialized blank result
  keys in otherwise empty cases.

## Commit / Push

Task A is committed independently. Push is intentionally deferred until Task C
and final validation complete.

## Project Memory Delta

No memory update is needed; this implements the existing calculator empty-state
policy without changing it.

## Next Suggested Action

Task B: correct EN14825 editable-cell backgrounds through the existing common
cell-role/style owner.
