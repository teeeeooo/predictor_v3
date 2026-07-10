# 048_iso-separation-step3a-new-iso-cspf

## Goal
- Execute `iso_seperation_plan.md` Step 3a.
- Implement the new `core/calculator_iso16358.py` CSPF path for ISO 16358-1 without KS, AS/NZS, workbook, or legacy diagnostic responsibilities.

## Scope
- `core/calculator_iso16358.py`
  - Implement CSPF config parsing, point resolution, interpolation, ISO boundary EER, T3 piecewise boundary EER, bin accumulation, and result envelope.
  - Keep `calculate_hspf()` as `NotImplementedError` for Step 3b.
  - Do not import `KSC9306Calculator`.
  - Do not implement KS-only `round_test_values`, `rounding_method`, or `ks_intersection`.
- Active CSPF tests
  - Retarget active `tests/test_iso16358_cspf_*.py` imports from legacy to new ISO calculator.
  - Keep moved diagnostic/mixed files under `tests/_legacy/` on legacy imports.
- `project_log.md`
  - Record Step 3a result and decision.

## Non-goals
- No HSPF implementation.
- No ASNZS implementation.
- No profile/dispatcher registration.
- No UI swap from legacy to new ISO.
- No data/region config changes.
- No golden expected, tolerance, or xfail marker changes.
- No external web search was needed; repo docs and existing legacy implementation supplied enough CSPF details for this step.

## Verification
- `python3 -B -m py_compile core/calculator_iso16358.py` → passed.
- Representative Step 3a CSPF set:
  - `python3 -B -m pytest tests/test_iso16358_cspf_iso_t1_default_config.py tests/test_iso16358_cspf_iso_t1_default_golden.py tests/test_iso16358_cspf_iso_t1_2point_control_samples.py tests/test_iso16358_cspf_iso_boundary_eer_control_regression.py tests/test_iso16358_cspf_hong_kong_config.py tests/test_iso16358_cspf_india_iseer_config.py tests/test_iso16358_cspf_saso_config.py tests/test_iso16358_cspf_saso_t3_regression.py tests/test_iso16358_cspf_t3_profile.py tests/test_iso16358_cspf_asean_report_examples.py -q` → `22 passed`.
- All active CSPF tests:
  - `python3 -B -m pytest tests/test_iso16358_cspf_*.py -q` → `30 passed`.
- Full suite:
  - `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`.
- Boundary grep:
  - `rg -n "KSC9306|ks_|KS C|ASNZS|asnzs|workbook|round_test_values|rounding_method|ks_intersection|calculator_iso16358_legacy" core/calculator_iso16358.py || true` → 0 matches.

## Task Results
- New ISO CSPF supports:
  - flat `points` + `derived_rules` configs.
  - `cspf_test_profile` T1/T3 resolver path.
  - `building_load_source=measured` and `building_load_source=declared`.
  - `iso_boundary_eer` and capacity-linear fallback.
  - India `iso_boundary_temperature_rounding=excel_round_0`.
  - T3 piecewise boundary EER for SASO.
- Active CSPF tests now exercise `core.calculator_iso16358.ISO16358Calculator`.
- Legacy CSPF profile resolver/calculation diagnostics remain under `tests/_legacy/`.

## Changed Files
- `core/calculator_iso16358.py`
- `project_log.md`
- `tests/test_iso16358_cspf_asean_report_examples.py`
- `tests/test_iso16358_cspf_clause67_bin_diagnostics.py`
- `tests/test_iso16358_cspf_hong_kong_config.py`
- `tests/test_iso16358_cspf_india_iseer_config.py`
- `tests/test_iso16358_cspf_iso_boundary_eer_control_regression.py`
- `tests/test_iso16358_cspf_iso_t1_2point_control_samples.py`
- `tests/test_iso16358_cspf_iso_t1_default_config.py`
- `tests/test_iso16358_cspf_iso_t1_default_golden.py`
- `tests/test_iso16358_cspf_official_tool_formula_diagnostics.py`
- `tests/test_iso16358_cspf_saso_config.py`
- `tests/test_iso16358_cspf_saso_t3_regression.py`
- `tests/test_iso16358_cspf_t3_profile.py`
- `result_reports/active/048_iso-separation-step3a-new-iso-cspf.md`

## Known Failures / Risks
- Full-suite baseline still has 16 pre-existing ISO HSPF failures. Step 3a does not address HSPF.
- `calculate_hspf()` in the new ISO calculator intentionally raises `NotImplementedError` until Step 3b.
- UI still imports the legacy ISO calculator. Step 5 will reconnect UI/profile/dispatcher after ISO HSPF is restored.

## Commit / Push
- source commit: `c7156cc feat: implement new ISO CSPF calculator path`
- source push: `origin/work/iso-separation-plan`
- report commit: pending at report creation time.
