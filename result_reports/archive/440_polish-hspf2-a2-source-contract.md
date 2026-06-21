# 440 Polish HSPF2 A2 and Source Contract

## Goal

Make AHRI HSPF2 A2 capacity-only in main and batch UI while preserving the
current core point-tuple contract and stable source display labels.

## Scope

- Remove A2 Power/COP from main UI and DEV sample input.
- Make the batch A2 Power physical row read-only blank and remove it from
  session/user input.
- Inject a positive A2 tuple placeholder only at the adapter/core boundary.
- Audit and test all v3 H12/H22/H42 source values.

## Non-goals

- No core equation/config/schema/fixture/golden, SEER2, EN14825/ISO,
  window-sizing, table width/color/token, batch label compacting, or unrelated
  refactor change.

## Changed Files

- `apps/calculator/ui/ahri/hspf2_adapter.py`
- `apps/calculator/ui/ahri/hspf2_batch.py`
- `apps/calculator/ui/ahri/hspf2_batch_session.py`
- `apps/calculator/ui/ahri/hspf2_mock_data.py`
- `apps/calculator/ui/sections/ahri_hspf2_section.py`
- `tests/test_apps_calculator_ui_ahri_hspf2.py`
- `tests/test_ui_tk_ahri_hspf2_batch.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/440_polish-hspf2-a2-source-contract.md`

## Task Results

- Main A2 now exposes only `Capacity [Btu/h]`; Power and display-only COP rows
  are removed.
- Batch A2 remains one matrix column: Capacity is editable, Power is a blank
  not-applicable cell, and `a2_power` is absent from visible/session snapshots.
- The adapter requires and validates only `a2_capacity`. It sends
  `(a2_capacity, 1.0)` to core. A2 power is not used by the HSPF2 formula; the
  positive placeholder only satisfies the current core point-tuple validation
  contract.
- DEV sample data no longer owns `a2_power`; legacy snapshot/user values with
  that key are discarded or ignored.

## Source Mapping Audit

The v3 AHRI path returns:

- H12: `tested`, `eq_11_183`, or `eq_11_185`;
- H22: `tested` or `eq_11_44_11_50`;
- H42: `provided` or `not_provided`.

The adapter maps `tested` to `measured`, nonempty equation identifiers to
`calculated`, `provided` to `measured`, and `not_provided` to `not provided`.
Legacy/helper `extrapolated` is not added to the v3 H42 UI contract. User-facing
batch labels remain the existing full words.

## Mock Data Lifecycle

`apps/calculator/ui/ahri/hspf2_mock_data.py` remains the temporary DEV sample
owner. Its removal procedure is unchanged; A2 now contributes only
`a2_capacity`.

## Verification

- `python3 -B -m pytest tests/test_apps_calculator_ui_ahri_hspf2.py tests/test_ui_tk_ahri_hspf2_batch.py`
  — 17 passed.
- `python3 -B tools/check_code_structure.py` — passed with only two pre-existing
  EN14825 soft-LOC warnings and the expected code-map metadata reminder.
- `python3 -B tools/code_checker/build_reference_map.py --check` — stale only
  by parent-SHA/dirty-tree metadata; no top-level file or symbol structure
  changed, so regeneration was not required.
- `git diff --check` — passed.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed.

## Known Risks

- The `1.0` placeholder is intentionally coupled to the current core positive
  tuple validator; if core later accepts a capacity-only A2 shape, the adapter
  placeholder should be removed in that separately approved contract change.
- Existing external callers of the UI adapter that supplied `a2_power` continue
  to work because the field is ignored, not rejected.

## Scope Compliance

- Core/config/schema/fixture/golden and all prohibited UI surfaces are
  unchanged.
- No new UI sizing/color/style literal was added.
- The main HSPF2 section shrinks and remains below its soft LOC limit.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `AGENT_TASK_ROUTER.md`: UI/source/report routes already reviewed this
  session; reason: applicable implementation/report gates.
- HSPF2 adapter/batch/session/mock/main section: A2 and source-related ranges
  only; reason: exact contract owners.
- HSPF2 main/batch focused tests: matching A2/source/snapshot ranges; reason:
  regression update.
- `core/calculator_ahri_hspf2.py`: v3 required-point, A2 read, and source-return
  ranges only; reason: confirm unchanged core contract and actual source values.
- `docs/WORK_PLAN.md`: current-slice range; reason: next-action sync.
- broad read: none
- repeated read: none

## Next Action

AHRI batch compact label and token usage cleanup.
