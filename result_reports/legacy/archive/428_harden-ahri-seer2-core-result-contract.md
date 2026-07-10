# 428 Harden AHRI SEER2 Core Result Contract

## Goal

Fail explicitly when the calculator behind `AhriSeer2Adapter` violates the
required SEER2 result contract.

## Scope

- Add one adapter-local required-float reader.
- Validate required `SEER2`, `total_cooling_Btu`, and `total_energy_Wh` values.
- Cover missing and non-numeric required totals in the focused adapter tests.

## Non-goals

- No fallback values, optional treatment, core equation, or public core result
  contract changes.
- No SEER2 batch, HSPF2, section, shared result panel, docs, or unrelated
  refactor changes.

## Changed Files

- `apps/calculator/ui/ahri/seer2_adapter.py`
- `tests/test_apps_calculator_ui_ahri_seer2.py`
- `result_reports/active/428_harden-ahri-seer2-core-result-contract.md`

## Task Results

- Required core values are converted through one adapter-local helper.
- Missing, non-numeric, or otherwise non-convertible values raise a keyed
  `ValueError` instead of leaking `KeyError` or silently substituting data.
- The existing section boundary can continue blanking the result through its
  current `ValueError` handling.

## Verification

- `python3 -B -m pytest tests/test_apps_calculator_ui_ahri_seer2.py`
  — 6 passed.
- `python3 -B tools/check_code_structure.py`
  — passed with two pre-existing EN14825 soft-LOC warnings and the expected
  code-map metadata warning.
- `python3 -B tools/code_checker/build_reference_map.py --check`
  — stale only by existing generated-SHA metadata; no regeneration because
  this private method change does not alter the map's indexed structure.
- `git diff --check`
  — passed.
- `python3 -B tools/check_agent_change_gate.py --cached`

## Known Risks

- The adapter intentionally treats all three keys as required; future custom
  calculators must preserve this contract or fail visibly through blank UI
  results.

## Scope Compliance

- Only the approved adapter, focused test, and this report changed.
- `docs/WORK_PLAN.md` remains correctly pointed at AHRI SEER2 batch.

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

- `apps/calculator/ui/ahri/seer2_adapter.py`: core-result mapping only;
  reason: required contract owner.
- `tests/test_apps_calculator_ui_ahri_seer2.py`: adapter tests only; reason:
  focused mismatch coverage.
- broad read: none
- repeated read: none

## Next Action

AHRI SEER2 batch.
