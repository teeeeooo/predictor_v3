# 432 Align AHRI SEER2 Seasonal Total Scale

## Goal

Align SEER2 main-result totals with the HSPF2 seasonal display scale without
changing core calculations or configuration.

## Scope

- Read required `cooling_season_hours` from the existing calculator config.
- Scale fractional-bin cooling and energy totals for UI display only.
- Fail explicitly for missing, non-numeric, or non-positive season hours.
- Update focused adapter and result expectations.

## Non-goals

- No core equation, config, fixture, golden, HSPF2, SEER2 batch, EN14825,
  shared UI/result/table framework, or unrelated refactor change.

## Changed Files

- `apps/calculator/ui/ahri/seer2_adapter.py`
- `tests/test_apps_calculator_ui_ahri_seer2.py`
- `result_reports/active/432_align-ahri-seer2-seasonal-total-scale.md`

## Task Results

- `SEER2` remains the unchanged core result.
- Total Cooling [kBtu] is `total_cooling_Btu * cooling_season_hours / 1000`.
- Total Energy [kWh] is `total_energy_Wh * cooling_season_hours / 1000`.
- `cooling_season_hours` is read from the calculator's existing
  `config.constants` contract and must be a positive numeric value.
- Missing or invalid values raise a named adapter-boundary `ValueError`; no
  silent fallback or plausible-looking zero is displayed.

## Verification

- `python3 -B -m pytest tests/test_apps_calculator_ui_ahri_seer2.py`
  — 9 passed.
- `python3 -B tools/check_code_structure.py`
  — passed with two pre-existing EN14825 soft-LOC warnings and the existing
  code-map metadata reminder.
- `git diff --check`
  — passed.
- `python3 -B tools/check_agent_change_gate.py --cached`

## Known Risks

- Custom calculators injected into the UI adapter must expose the same config
  contract as the production calculator.
- Seasonal totals are presentation values; core fractional-bin return values
  remain unchanged.

## Scope Compliance

- Only the approved adapter, focused test, and this report changed.
- `docs/WORK_PLAN.md` already points to AHRI HSPF2 batch and required no edit.
- No file or top-level symbol structure changed; code-map regeneration was not
  required by this task's verification contract.

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

- `AGENT_TASK_ROUTER.md`: UI/source/report routes already reviewed in this
  session; reason: applicable implementation gates.
- `core/calculator_ahri_seer2.py`: constructor config ownership and unchanged
  result keys only; reason: existing calculator/config boundary.
- `data/region_configs/usa.json`: constants key location/value only; reason:
  verify existing required season-hour source without modification.
- `apps/calculator/ui/ahri/seer2_adapter.py`: summary scaling boundary; reason:
  UI-only conversion.
- `tests/test_apps_calculator_ui_ahri_seer2.py`: existing focused boundary;
  reason: seasonal expectations and failure cases.
- broad read: none
- repeated read: none

## Next Action

AHRI HSPF2 batch.
