# 427 Polish AHRI SEER2 Main Result

## Goal

Align the AHRI SEER2 success status with existing calculator result behavior
and expose existing seasonal totals without changing core equations.

## Scope

- Show `자동 계산 완료` in the successful SEER2 result status row.
- Map existing core total cooling and energy values into the UI summary.
- Extend focused adapter and result-surface coverage.

## Non-goals

- No SEER2 batch or HSPF2 implementation.
- No core equation, result contract, config, schema, fixture, or golden change.
- No common `ResultPanel`, EN14825 behavior, or unrelated refactor.

## Changed Files

- `apps/calculator/ui/ahri/seer2_adapter.py`
- `apps/calculator/ui/sections/ahri_seer2_section.py`
- `tests/test_apps_calculator_ui_ahri_seer2.py`
- `result_reports/active/427_polish-ahri-seer2-main-result.md`

## Task Results

- Successful calculation now renders `자동 계산 완료` instead of an empty
  white status row.
- The existing `total_cooling_Btu` and `total_energy_Wh` core outputs are
  converted at the adapter boundary to kBtu and kWh by dividing by 1000.
- The compact result surface displays SEER2, Total Cooling [kBtu], and Total
  Energy [kWh], each at three decimal places.

## Verification

- `python3 -B -m pytest tests/test_apps_calculator_ui_ahri_seer2.py`
  — 4 passed.
- `python3 -B tools/check_code_structure.py`
  — passed with two pre-existing EN14825 soft-LOC warnings and the expected
  code-map metadata warning.
- `python3 -B tools/code_checker/build_reference_map.py --check`
  — stale because the generated metadata records the parent SHA of the commit
  that publishes the map; no regeneration because this polish adds no file or
  top-level symbol structure.
- `git diff --check`
  — passed.
- `python3 -B tools/check_agent_change_gate.py --cached`

## Known Risks

- Precision is a UI presentation choice; the underlying returned values and
  equations remain unchanged.
- Manual platform visual smoke remains part of the later AHRI lifecycle
  closeout.

## Scope Compliance

- Only the approved AHRI SEER2 adapter, section, focused test, and this report
  changed.
- `docs/WORK_PLAN.md` and `project_brief.md` already point to AHRI SEER2 batch,
  so no status edit was necessary.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: checked
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `AGENT_TASK_ROUTER.md`: UI/source/report routes already reviewed in this
  session; reason: applicable workflow gates.
- `core/calculator_ahri_seer2.py`: return dictionary only; reason: confirm
  existing total keys and native Btu/Wh units.
- `apps/calculator/ui/ahri/seer2_adapter.py`: summary and result mapping;
  reason: unit conversion owner.
- `apps/calculator/ui/sections/ahri_seer2_section.py`: result rendering only;
  reason: status and fields.
- `tests/test_apps_calculator_ui_ahri_seer2.py`: existing focused test surface;
  reason: extend without broad suite expansion.
- `docs/WORK_PLAN.md` and `project_brief.md`: current AHRI milestone ranges;
  reason: documentation-sync judgment.
- broad read: none
- repeated read: none

## Next Action

AHRI SEER2 batch.
