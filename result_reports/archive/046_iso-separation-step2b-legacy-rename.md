# 046_iso-separation-step2b-legacy-rename

## Goal
- Execute `iso_seperation_plan.md` Step 2b as one atomic source/test change.
- Demote the current ISO calculator implementation to a legacy module, add a new ISO skeleton, and retarget existing callers to the legacy module so behavior remains unchanged.

## Scope
- Rename current implementation:
  - `core/calculator_iso16358.py` → `core/calculator_iso16358_legacy.py`.
- Create new `core/calculator_iso16358.py` skeleton:
  - `ISO16358Calculator.__init__`, `calculate_cspf`, and `calculate_hspf` raise `NotImplementedError`.
  - No alias or fallback import to legacy.
- Retarget tests/UI:
  - `from core.calculator_iso16358 import ISO16358Calculator` → `from core.calculator_iso16358_legacy import ISO16358Calculator`.
  - `import core.calculator_iso16358 as iso` → `import core.calculator_iso16358_legacy as iso`.
  - `ui/calculators_2point.py` now imports the legacy calculator during transition.
- Move diagnostic/mixed tests:
  - `tests/test_iso16358_cspf_profile_calculation.py` → `tests/_legacy/test_iso16358_cspf_profile_calculation.py`.
  - `tests/test_iso16358_cspf_profile_resolver.py` → `tests/_legacy/test_iso16358_cspf_profile_resolver.py`.
  - `tests/test_iso16358_cspf_iso_t1_default_diagnostics.py` → `tests/_legacy/test_iso16358_cspf_iso_t1_default_diagnostics.py`.
  - `tests/test_iso16358_hspf_h8_trace.py` → `tests/_legacy/test_iso16358_hspf_h8_trace.py`.
  - Added `tests/_legacy/__init__.py`.
- Update `project_log.md` with Step 2b result and decision.

## Non-goals
- No new ISO implementation beyond the explicit skeleton.
- No ISO profile/dispatcher registration.
- No UI dispatcher/profile conversion.
- No KS factory dead-code removal; Step 2c remains separate.
- No region config changes.
- No workbook/reference file changes.
- No golden expected, tolerance, or xfail-pass changes.
- No external web search was needed for this rename/import routing step; user request to web-search missing information is carried forward for Step 3+ implementation gaps.

## Verification
- `python3 -B -m py_compile core/calculator_iso16358.py core/calculator_iso16358_legacy.py core/calculator_ks_c9306.py ui/calculators_2point.py tests/_legacy/test_iso16358_cspf_iso_t1_default_diagnostics.py` → passed.
- `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`.
- `rg -n "from core\\.calculator_iso16358 import|import core\\.calculator_iso16358 as iso" tests ui core` → 0 matches.
- `rg -n "calculator_iso16358_legacy" tests ui core | wc -l` → 36 matches.
- `git status --short --branch` after source push → clean, tracking `origin/work/iso-separation-plan`.

## Task Results
- The legacy implementation now lives at `core/calculator_iso16358_legacy.py`.
- The new `core/calculator_iso16358.py` is intentionally non-functional until Step 3 and fails fast if accidentally used.
- Existing tests and UI transition callers explicitly import `core.calculator_iso16358_legacy`.
- Diagnostic/mixed tests are isolated under `tests/_legacy/`.
- The moved `test_iso16358_cspf_iso_t1_default_diagnostics.py` fixture path was updated from local `tests/_legacy/fixtures` lookup to `tests/fixtures`, preserving behavior after the move.
- Full-suite failure count returned to the expected baseline after fixture path correction.

## Changed Files
- `core/calculator_iso16358.py`
- `core/calculator_iso16358_legacy.py`
- `project_log.md`
- `tests/_legacy/__init__.py`
- `tests/_legacy/test_iso16358_cspf_iso_t1_default_diagnostics.py`
- `tests/_legacy/test_iso16358_cspf_profile_calculation.py`
- `tests/_legacy/test_iso16358_cspf_profile_resolver.py`
- `tests/_legacy/test_iso16358_hspf_h8_trace.py`
- `tests/test_asnzs_hspf_excel_compat_component_accumulation.py`
- `tests/test_asnzs_hspf_excel_compat_component_energy.py`
- `tests/test_asnzs_hspf_excel_compat_component_row_mapping.py`
- `tests/test_asnzs_hspf_excel_compat_helper_column_reconstruction.py`
- `tests/test_asnzs_hspf_excel_compat_helper_columns.py`
- `tests/test_asnzs_hspf_excel_compat_helper_cop.py`
- `tests/test_asnzs_hspf_excel_compat_output_anchors.py`
- `tests/test_asnzs_hspf_excel_compat_partial_impl.py`
- `tests/test_asnzs_hspf_excel_compat_result_envelope.py`
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
- `tests/test_iso16358_hspf_compatibility_boundary.py`
- `tests/test_iso16358_hspf_formula_micro.py`
- `tests/test_iso16358_hspf_golden.py`
- `tests/test_iso16358_hspf_hong_kong_config.py`
- `tests/test_iso16358_hspf_ks_oracle.py`
- `tests/test_iso16358_hspf_pure_iso_track_a.py`
- `tests/test_iso16358_hspf_smoke.py`
- `tests/test_iso16358_hspf_validation.py`
- `ui/calculators_2point.py`
- `result_reports/active/046_iso-separation-step2b-legacy-rename.md`

## Known Failures / Risks
- Full-suite baseline still has 16 pre-existing ISO HSPF failures:
  - `tests/test_iso16358_hspf_formula_micro.py` — 4.
  - `tests/test_iso16358_hspf_golden.py` — 10.
  - `tests/test_iso16358_hspf_pure_iso_track_a.py` — 1.
  - `tests/test_iso16358_hspf_validation.py` — 1.
- UI smoke was not run as an interactive PyQt window in this environment; `py_compile` covered syntax/import availability only. The UI remains intentionally pointed at legacy until Step 5.
- ASNZS negative assertion tests still target legacy in Step 2. Step 4 must reassess whether each assertion should target new ISO or legacy residue.
- Step 2c should now remove `KSC9306Calculator.from_iso_calculator(...)` and `_iso_calculator_ref` after grep confirmation.

## Commit / Push
- source commit: `a677e60 refactor: rename ISO calculator legacy path`
- source push: `origin/work/iso-separation-plan`
- report commit: pending at report creation time.
