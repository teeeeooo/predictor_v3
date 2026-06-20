# 433 Implement AHRI HSPF2 Batch

## Goal

Add the dynamic AHRI HSPF2 batch surface using the established two-row matrix
contract while preserving optional-point drafts and hidden case inputs.

## Scope

- Add a headless HSPF2 batch spec, handler, and superset session owner.
- Add the HSPF2 batch profile/dialog and thin main-section lifecycle access.
- Map existing core result metadata to measured/calculated/not-provided source
  labels at the HSPF2 adapter boundary.
- Add focused headless, dynamic rebuild, snapshot, dialog, and lifecycle tests.

## Non-goals

- No core equation, config, schema, fixture, golden, SEER2, EN14825, shared
  batch framework, or unrelated main-UI change.

## Changed Files

- `apps/calculator/ui/ahri/hspf2_adapter.py`
- `apps/calculator/ui/ahri/hspf2_batch.py`
- `apps/calculator/ui/ahri/hspf2_batch_access.py`
- `apps/calculator/ui/ahri/hspf2_batch_session.py`
- `apps/calculator/ui/batch_dialogs/profiles/ahri_hspf2.py`
- `apps/calculator/ui/batch_dialogs/profiles/ahri_hspf2_dialog.py`
- `apps/calculator/ui/sections/ahri_hspf2_section.py`
- `tests/test_apps_calculator_ui_ahri_hspf2.py`
- `tests/test_ui_tk_ahri_hspf2_batch.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/433_implement-ahri-hspf2-batch.md`

## Task Results

- The matrix uses Capacity/Power physical rows and the exact A2, H01, H11,
  H1N, H2Int, H32, H42, H12, H22 point order.
- H42/H12/H22 remain visible; disabled point cells are read-only blanks and are
  omitted from adapter/core input.
- Results appear only on the first physical row as HSPF2, H12, H22, and H42;
  source labels use measured, calculated, and not provided.
- Draft common values, last valid active options, and superset cases have
  separate owners. Invalid drafts survive snapshots, disabled inputs survive
  rebuilds, and result values are excluded.
- Main-section access prevents duplicate dialogs, restores close/reopen state,
  and closes the dialog during section destruction.

## Verification

- `python3 -B -m pytest tests/test_ui_tk_ahri_hspf2_batch.py tests/test_apps_calculator_ui_ahri_hspf2.py`
  — 14 passed.
- `python3 -B tools/check_code_structure.py` — passed with only two pre-existing
  EN14825 soft-LOC warnings and the expected pre-regeneration map reminder.
- `python3 -B tools/code_checker/build_reference_map.py --check` — stale as
  expected for new source modules; regenerated once with
  `python3 -B tools/code_checker/build_reference_map.py`.
- `git diff --check` — passed.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed.

## Known Risks

- Tk visual density at minimum window size remains a manual smoke item for the
  AHRI lifecycle closeout.
- DEV sample ownership remains unchanged in
  `apps/calculator/ui/ahri/hspf2_mock_data.py`; removal still means deleting
  that file/import and only the main-section sample-population loop.

## Scope Compliance

- The large main section receives only a batch-access helper, button alias, and
  destroy hook and remains within the 250 LOC soft limit.
- Dynamic state is profile-local; no shared batch behavior was refactored.
- `project_brief.md` does not require a milestone pointer change for this
  implementation slice.

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

- `AGENT_TASK_ROUTER.md`: UI/source/report routes already reviewed this
  session; reason: applicable implementation gates.
- AHRI UI/Batch design specification: HSPF2 batch and snapshot sections only;
  reason: exact matrix, source, and dynamic-state contract.
- EN14825 SCOP batch session/profile/dialog: dynamic owner ranges only; reason:
  rebuild and superset snapshot parity.
- AHRI SEER2 batch spec/profile/dialog/section/tests: targeted ranges only;
  reason: matrix, actions, dialog shell, and lifecycle parity.
- AHRI HSPF2 adapter/section/core return metadata: targeted ranges only;
  reason: optional omission and existing source metadata mapping.
- `docs/WORK_PLAN.md`: current-slice range; reason: next-action sync.
- active reports 431-432: report structure and current next action only.
- broad read: none
- repeated read: none

## Next Action

AHRI calculator lifecycle closeout.
