# UI Resolver Audit Result

## Objective

Audit `app_calculator.py` / `ui/calc_window.py` before ML or inverse-search work resumes, and separate what can remain local UI behavior from what should move to calculator profile resolver/dispatcher.

## Files Checked

- `app_calculator.py`
- `ui/calc_window.py`
- `ui/calculators_2point.py`
- `core/calculator_profiles.py`
- `core/calculator_dispatcher.py`

## Current State

- `app_calculator.py` is a thin Qt entrypoint that instantiates `CalculatorWindow`.
- `ui/calculators_2point.py` already uses `create_calculator_for_profile(...)` for ISO / India / Hong Kong / SASO CSPF calculators.
- `core/calculator_profiles.py` has enabled profiles for AHRI SEER2/HSPF2, KS CSPF/HSPF, ISO CSPF variants, and a disabled AS/NZS compatibility profile.
- `core/calculator_dispatcher.py` can construct calculator instances by resolved `calculator_id`.

## Remaining Non-Resolver UI Paths

| Location | Current behavior | Audit judgment |
| --- | --- | --- |
| `ui/calc_window.py::scan_configs()` | Scans `data/region_configs/*.json` directly and populates EN/AHRI combo boxes by JSON `standard` text. | Keep temporarily for EN until EN profiles exist; replace AHRI population with profile list when UI wiring is changed. |
| `ui/calc_window.py::on_region_changed_ahri()` | Builds `AHRICalculator(path)` directly from selected JSON filename. | Move to `create_calculator_for_profile(profile_id="ahri_usa_seer2")` in the implementation step. |
| `ui/calc_window.py::_load_hspf2_calc()` | Already uses `create_calculator_for_profile(profile_id="ahri_usa_hspf2")`. | Keep; this is the target pattern. |
| `ui/calc_window.py::on_region_changed_en()` | Stub, with old direct `EN14825Calculator(path)` comment. | Keep as deferred until EN profiles are registered. |
| `ui/calc_window.py::on_region_changed_iso()` | Stub. ISO tab delegates to `IsoCspfSingleWidget`. | Keep; ISO CSPF is handled in `ui/calculators_2point.py`. |

## Implementation Boundary

The immediate implementation should be limited to AHRI SEER2 UI construction:

- Use `create_calculator_for_profile(profile_id="ahri_usa_seer2")`.
- Keep HSPF2 profile construction as-is.
- Do not change EN tab behavior until EN14825 profiles exist.
- Do not change ISO CSPF behavior because `IsoCspfSingleWidget` already uses profile dispatcher.
- Do not introduce ML schema, calculator result adapter, or inverse-search behavior in this UI cleanup.

## Verification For Implementation Step

- `python3 -B -m py_compile app_calculator.py ui/calc_window.py ui/calculators_2point.py core/calculator_dispatcher.py core/calculator_profiles.py`
- `python3 -B -m pytest tests/test_calculator_profiles.py tests/test_calculator_dispatcher.py -q`

## Remaining Follow-Up

- Register EN14825 profiles before converting EN tab config selection.
- Design calculator result envelope / ML adapter boundary before ML or inverse-search implementation.
- Run interactive Qt smoke before claiming UI production readiness.
