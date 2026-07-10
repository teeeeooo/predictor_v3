# 431 Polish AHRI HSPF2 Main UI

## Goal

Align visible HSPF2 terminology with SEER2, add display-only COP rows, and
expose existing seasonal totals in the compact result.

## Scope

- Replace abbreviated Cap/Pow labels with Capacity/Power and shorten the A2
  column label.
- Add read-only COP rows to A2 and heating-point tables.
- Map existing core total heating and energy values into the HSPF2 summary.
- Extend focused adapter and UI tests and advance the current-slice owner.

## Non-goals

- No HSPF2 batch or SEER2 implementation change.
- No core equation/result contract, config, schema, fixture, golden, EN14825,
  shared table/result framework, or unrelated redesign change.

## Changed Files

- `apps/calculator/ui/ahri/hspf2_adapter.py`
- `apps/calculator/ui/sections/ahri_hspf2_section.py`
- `tests/test_apps_calculator_ui_ahri_hspf2.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/431_polish-ahri-hspf2-main-ui.md`

## Task Results

- A2 now uses the short `A2` column with Capacity [Btu/h], Power [W], and COP
  rows; heating points use Condition / Temp, Capacity [Btu/h], Power [W], and
  COP.
- COP is computed by the adapter's display-only helper from valid positive
  capacity/power pairs. Incomplete, invalid, or inactive optional points remain
  blank, and no COP value enters the core envelope.
- Existing `total_heating_btu` and `total_energy_wh` outputs are required and
  converted at the adapter boundary to kBtu and kWh.
- The compact result displays HSPF2, Total Heating [kBtu], and Total Energy
  [kWh] with the existing automatic-success status.

## Mock Data Lifecycle

- Existing owner remains `apps/calculator/ui/ahri/hspf2_mock_data.py` with
  symbol `HSPF2_DEV_SAMPLE_VALUES`; the file was not changed in this slice.
- Removal remains: delete the mock file, remove its section import, and remove
  only the A2/heating sample-population loop in `_populate_initial_values`.
- Keep numeric-option defaults. The UI then starts with blank measurement/COP
  cells without changing structure, optional behavior, or calculation logic.

## Verification

- `python3 -B -m pytest tests/test_apps_calculator_ui_ahri_hspf2.py`
  — 7 passed.
- `python3 -B tools/check_code_structure.py`
  — passed with two pre-existing EN14825 soft-LOC warnings and the expected
  code-map metadata reminder.
- `python3 -B tools/code_checker/build_reference_map.py --check`
  — stale only by generated parent-SHA metadata; no regeneration because this
  polish changes no indexed file or top-level symbol structure.
- `git diff --check`
  — passed.
- `python3 -B tools/check_agent_change_gate.py --cached`

## Known Risks

- COP precision is display-only at two decimals; seasonal result fields remain
  three-decimal presentation values.
- DEV sample data remains intentionally visible until the documented cleanup.
- Platform visual smoke remains part of later AHRI lifecycle closeout.

## Scope Compliance

- The HSPF2 section remains below the 250 LOC soft limit.
- No new source file or top-level symbol changes the code-map structure, so the
  map is checked but not regenerated.
- `project_brief.md` remains outside the explicit modification allow list;
  `docs/WORK_PLAN.md` is the synchronized current-slice owner.

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
  session; reason: applicable implementation gates.
- `core/calculator_ahri_hspf2.py`: production result return dictionary only;
  reason: confirm existing total keys and Btu/Wh units.
- `apps/calculator/ui/ahri/hspf2_adapter.py`: summary and parsing boundary;
  reason: COP helper and total conversion owner.
- `apps/calculator/ui/sections/ahri_hspf2_section.py`: A2/heating/result ranges;
  reason: label, static-row, and rendering polish.
- `tests/test_apps_calculator_ui_ahri_hspf2.py`: existing focused boundary;
  reason: extend without broad test expansion.
- `docs/WORK_PLAN.md`: current-slice range; reason: next-action sync.
- broad read: none
- repeated read: none

## Next Action

AHRI HSPF2 batch.
