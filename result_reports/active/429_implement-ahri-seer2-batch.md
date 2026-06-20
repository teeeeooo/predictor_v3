# 429 Implement AHRI SEER2 Batch

## Goal

Add the approved AHRI SEER2 batch workflow using the shared two-row calculator
matrix and dialog lifecycle.

## Scope

- Add the exact five-point Capacity/Power headless matrix specification.
- Add a Type-aware automatic row handler with SEER2-only results.
- Add the batch profile, dialog, input-only snapshot, Copy/CSV actions, and
  parent-section lifecycle wiring.
- Add focused headless, real-adapter, matrix, dialog, and lifecycle tests.

## Non-goals

- No HSPF2 main or batch implementation.
- No core equation, config, schema, fixture, golden, or EN14825 change.
- No common batch framework refactor, new palette, or unrelated UI redesign.

## Changed Files

- `apps/calculator/ui/ahri/seer2_batch.py`
- `apps/calculator/ui/batch_dialogs/profiles/ahri_seer2.py`
- `apps/calculator/ui/sections/ahri_seer2_section.py`
- `tests/test_ui_tk_ahri_seer2_batch.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/429_implement-ahri-seer2-batch.md`

## Task Results

- One logical case renders Capacity and Power physical rows in that order.
- Point order and compact labels are exactly A_Full (35.0°C), B_Full
  (27.8°C), B_Low (27.8°C), E_Int (23.9°C), and F_Low (17.2°C).
- Type is dialog-owned HP/AC common input; complete cases auto-calculate one
  SEER2 result on the Capacity row and incomplete/invalid cases remain blank.
- The Power-row result is blank/read-only and no Status, Message, ERROR, or
  PENDING result column exists.
- Add/Remove, Copy All, and Export CSV reuse the common batch implementation.
- Snapshot close/reopen preserves Type and case inputs, excludes calculated
  SEER2, recalculates on restore, and prevents duplicate parent dialogs.

## Table Parity Evidence

- Reused `BatchMatrixSpec`, `BatchMatrixTable`, and `TkTableController`; no
  standalone table or interaction controller was introduced.
- Shared table styling retains existing header, editable, read-only, result,
  blank-read-only, clipboard, paste, undo, navigation, and CSV behavior.
- Focused tests verify exact physical rows, labels, cell roles, first-row-only
  result, export headers, actions, and lifecycle behavior.

## Verification

- `python3 -B -m pytest tests/test_ui_tk_ahri_seer2_batch.py`
  — 6 passed.
- `python3 -B tools/check_code_structure.py`
  — passed with two pre-existing EN14825 soft-LOC warnings and the
  pre-regeneration code-map stale reminder.
- `python3 -B tools/code_checker/build_reference_map.py --check`, followed by
  regeneration because new production modules change indexed structure.
  — regenerated successfully.
- `git diff --check`
  — passed.
- `python3 -B tools/check_agent_change_gate.py --cached`

## Known Risks

- Final platform-level dialog sizing and keyboard smoke remains part of AHRI
  lifecycle closeout; common controller behavior is covered by its existing
  test owners.
- `project_brief.md` remains outside this task's explicit modification allow
  list; `docs/WORK_PLAN.md` is the synchronized current-slice owner.

## Scope Compliance

- New responsibility is split between headless handler/spec and profile/dialog
  files, both below the 250 LOC soft limit.
- Parent section changes are limited to button, dialog reference, snapshot,
  open/close, and destroy cleanup wiring.
- No HSPF2, core, config, schema, fixture, golden, EN14825, or common framework
  file changed.

## Change Gate

```yaml
change_gate:
  new_source: split
  hotspot_delta: wiring-only
  code_map_check: regenerated
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `AGENT_TASK_ROUTER.md`: UI/source/report routes already reviewed in this
  session; reason: applicable implementation gates.
- `docs/designs/2026-06-20-ahri-210-240-ui-batch-design-specification.md`:
  common batch, SEER2 batch, ownership, parity, acceptance, and slice ranges;
  reason: approved contract.
- `apps/calculator/ui/en14825/seer_batch.py`: spec and handler only; reason:
  headless reference parity.
- `apps/calculator/ui/batch_dialogs/profiles/en14825_seer.py`: snapshot,
  section, action, adapter, and dialog ranges; reason: profile/lifecycle parity.
- `apps/calculator/ui/batch/matrix_models.py` and `matrix_table.py`: public spec,
  role, snapshot, result, Copy/export APIs; reason: common framework reuse.
- `apps/calculator/ui/batch_dialogs/shell.py`: lifecycle API only; reason:
  hidden-first and close/focus behavior.
- `apps/calculator/ui/sections/en14825_seer_section.py`: batch wiring and destroy
  ranges only; reason: thin parent pattern.
- Existing EN14825 headless/dialog focused tests: corresponding assertions
  only; reason: test style.
- Existing AHRI SEER2 adapter and section: public calculate and lifecycle
  insertion ranges; reason: product integration.
- `docs/WORK_PLAN.md`: current slice range; reason: next-action sync.
- broad read: none
- repeated read: none

## Next Action

AHRI HSPF2 main UI foundation.
