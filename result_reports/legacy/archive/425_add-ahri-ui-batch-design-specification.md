# 425 Add AHRI UI and Batch Design Specification

## Goal

Preserve the approved AHRI 210/240 SEER2/HSPF2 main and batch design as the
implementation contract for the next coding slices.

## Scope

- Add the AHRI UI/Batch design record and index it as an active reference.
- Advance the execution board and Arc 2 milestone map to SEER2 main UI.
- Record supersession of conflicting AHRI-specific legacy table sketches.

## Non-goals

- No source, test, calculator, config, schema, fixture, golden, EN14825, or
  workflow-tool changes.

## Changed Files

- `docs/designs/2026-06-20-ahri-210-240-ui-batch-design-specification.md`
- `docs/designs/README.md`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `result_reports/active/425_add-ahri-ui-batch-design-specification.md`

## Task Results

- Main UI is split into SEER2 and HSPF2 metric surfaces.
- SEER2 and dynamic HSPF2 batch contracts use the EN14825 two-row matrix model.
- HSPF2 optional-point omission, source display, hidden defaults, and
  draft/active/superset snapshot rules are fixed before coding.
- Visual parity reuses EN14825 and active UI/UX owners without a new palette.
- The next approved coding slice is SEER2 main UI foundation only.

## Reference Evidence

- Required source reviewed in full:
  `/Users/sunjaekim/Downloads/AHRI210240_calculator_design.md`.
- Existing AHRI table/unit archaeology checked:
  `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`.
- Existing auto-calc decision checked:
  `docs/designs/2026-05-22-calculator-action-model-alignment.md`.
- The new contract explicitly supersedes conflicting AHRI-specific sketches
  while retaining active UI/UX and architecture owners.

## Verification

- `git diff --check`
- `python3 -B tools/check_agent_change_gate.py --cached` against the final
  staged task scope.
- Pytest, structure guard, and code-map regeneration skipped as required for
  this docs-only task.

## Known Risks

- SEER2 Type defaults to HP for the first implementation; a later product
  decision may change the default without changing the HP/AC option contract.
- The design fixes UI/handler boundaries but does not claim formula parity or
  approve core/public-contract changes.

## Scope Compliance

- Only design/index, execution-board, milestone-map, and report files changed.
- No report lifecycle cleanup was performed.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: not_required
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `/Users/sunjaekim/Downloads/AHRI210240_calculator_design.md`: lines 1-1010;
  reason: mandatory source design evidence.
- `docs/designs/README.md`: lines 1-75; reason: design record lifecycle/index.
- `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`: AHRI
  boundary, risk, and slice ranges; reason: conflict/supersession check.
- `docs/designs/2026-05-22-calculator-action-model-alignment.md`: auto-calc
  decision range; reason: behavior reference parity.
- `docs/WORK_PLAN.md`: current AHRI slice range; reason: next-action sync.
- `project_brief.md`: Arc 2 milestone range; reason: milestone sync.
- broad read: mandatory download design only
- repeated read: none

## Project Log Judgment

No update. The new design record owns this implementation contract, while the
project milestone map and execution board carry current status and next action.

## Project Memory Delta

- type: decision
  topic: ahri-210-240-ui-batch-contract
  content: AHRI is split into SEER2/HSPF2 metric surfaces; batch uses two-row
    matrices, and HSPF2 optional points use omission plus dynamic snapshot rules.
  keywords:
    - ahri-210-240
    - seer2
    - hspf2
    - batch-matrix
  assertionStatus: accepted
  source: result_reports/active/425_add-ahri-ui-batch-design-specification.md

## Next Suggested Action

Implement the AHRI SEER2 main UI foundation only.

## Commit / Push

- The design, planning documents, and report are committed together.
- Final publication SHA evidence is reported in the terminal response to avoid
  a self-referential report update.
