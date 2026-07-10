# 422 Wire EN14825 SCOP Batch Parent Section

## Goal

Expose the implemented EN14825 SCOP batch dialog through its parent calculator
section while preserving profile-local rebuild and snapshot ownership.

## Scope

- Add the SCOP batch action to `En14825ScopSection`.
- Keep only dialog reference, snapshot handoff, open/close, and destroy cleanup
  in the parent section.
- Add focused headless parent lifecycle coverage.
- Advance the execution board to EN14825 smoke / lifecycle closeout.

## Changed Files

- `apps/calculator/ui/sections/en14825_scop_section.py`
- `tests/test_apps_calculator_ui_en14825_batch.py`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `result_reports/active/422_wire-en14825-scop-batch-parent-section.md`

## Results

- The SCOP section now exposes a `SCOP Batch` button using the established SEER
  lifecycle pattern.
- Reopening an existing dialog focuses it instead of creating a duplicate.
- Closing preserves the latest SCOP batch snapshot for the next open.
- Destroying the parent section disposes auto-calculation and closes an open
  batch dialog.
- `En14825ScopBatchSection`, `En14825ScopBatchDialog`, session state, core,
  config, schema, fixture, golden, and calculator behavior remain unchanged.

## Verification

- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825_batch.py`:
  15 passed.
- `python3 -B tools/check_code_structure.py`: completed with existing hotspot
  warnings and a stale reference-map reminder; the SCOP source delta is
  wiring-only and remains below the +40 hotspot decision threshold.
- `python3 -B tools/code_checker/build_reference_map.py --check`: completed;
  reference map remains stale relative to the pre-task HEAD and was not
  regenerated for this non-structural wiring slice.
- `git diff --check`: passed.
- `python3 -B tools/check_agent_change_gate.py --cached`: run against an
  isolated staged index during final verification.

## Known Risks

- A manual UI smoke remains for visible button placement, dialog launch, and
  close/reopen behavior in the calculator shell.
- The reference map was already stale at task start; this slice does not add a
  module or change an owner boundary, so regeneration remains outside scope.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: wiring-only
  code_map_check: checked
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `apps/calculator/ui/sections/en14825_scop_section.py`: lines 1-76, 270-325,
  and 548-580; reason: target imports, action placement, lifecycle, and cleanup.
- `apps/calculator/ui/sections/en14825_seer_section.py`: lines 1-78, 195-270,
  and 438-455; reason: accepted thin lifecycle and snapshot reference parity.
- `tests/test_apps_calculator_ui_en14825_batch.py`: lines 1-36 and 360-410;
  reason: focused test imports and extension point.
- `docs/WORK_PLAN.md`: lines 1-72; reason: completed slice and next-action sync.
- `project_brief.md`: lines 36-62; reason: Arc 1 milestone status sync.
- broad read: none
- repeated read: none

## Project Log Judgment

No update. This slice implements the already accepted parent/profile ownership
decision and introduces no new architecture or contract decision.

## Next Action

Run the focused EN14825 calculator smoke / lifecycle closeout.

## Commit / Push

- The product, test, documentation, and report changes are committed together.
- The final pushed commit hash and push result are reported in the terminal
  response to avoid a self-referential report update loop.
