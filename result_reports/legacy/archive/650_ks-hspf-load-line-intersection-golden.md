# Goal

- Strengthen KS C 9306 HSPF official calculator oracle coverage.
- Fix `rated_maximum` handling and the remaining frost-region official oracle mismatch without changing CSPF, ISO16358, AHRI, EN, public schema, or `korea.json`.

# Scope

- Changed `core/calculators/standards/ks_c9306.py`.
- Changed `tests/helpers/iso16358_hspf_samples.py` in the previous oracle slice.
- Changed `tests/test_iso16358_hspf_validation.py`.
- Updated this active result report.

# Non-goals

- No CSPF logic change.
- No ISO16358 HSPF official exact/golden fixture change.
- No AHRI/EN calculator change.
- No public schema or `korea.json` schema change.
- No PRH `Pheater * frunning` implementation.
- No `tj <= 2.0 and load > max_stage["capacity"]` special-case change.
- No direct bin-energy override, arbitrary correction factor, unrelated refactor, or merge.

# Verification

- `python3 -m py_compile core/calculators/standards/ks_c9306.py`: OK.
- `python3 -m pytest tests/test_iso16358_hspf_validation.py -q`: OK, 40 passed.
- `python3 -m pytest tests/test_iso16358_hspf_validation.py tests/test_iso16358_hspf_official_exact_golden.py -q`: OK, 57 passed.
- `python3 -B tools/check_code_structure.py`: OK with existing soft warnings, including `ks_c9306.py` LOC and stale code-map reminder.
- `git diff --check`: OK.
- `python3 -m pytest tests/test_iso16358_hspf_validation.py tests/test_iso16358_hspf_official_exact_golden.py tests/test_iso16358_hspf_ks_oracle.py -q`: OK, 59 passed.
- `git status --short`: modified calculator, validation test, and this report before commit.

# Task Results

- task 1: OK - added `_ks_hspf_frost_def_over_nof_ratio()` for KS HSPF frost-region defrost/no-frost ratio resolution.
- task 2: OK - non-max min/intermediate/rated frost capacity and power curves now use the rounding-aware effective ratio; max-stage curve behavior is unchanged.
- task 3: OK - added a regression test fixing effective ratios to `4165 / 4665` for capacity and `1604 / 1700` for power under `round_test_values=true`.
- task 4: OK - strict KS total and bin-level official oracle tests now pass without changing expected values.
- task 5: OK - report updated with effective-ratio cause, validation outcome, and remaining non-impact gaps.
- task 6: OK - validation, commit, and push were requested; final commit/push details are reported in terminal output to avoid a self-referential report update loop.

# Test Results

Current official full-bin output:

- `HSTL`: `6651225.0 Wh` (expected `6651225.0 Wh`)
- `HSEC`: `1802769.6230012567 Wh` (expected `1802769.7 Wh`)
- `heat_pump_energy`: `1785292.5674457005 Wh` (expected `1785292.6 Wh`)
- `auxiliary_energy`: `17477.05555555556 Wh` (expected `17477.1 Wh`)
- `rounded_hspf`: `3.689` (expected `3.689`)

Key bin-level regression points:

- `-8°C heat_pump_energy`: `36554.0 Wh`; auxiliary `0.0 Wh`.
- `-7°C heat_pump_energy`: `51810.0 Wh`; auxiliary `0.0 Wh`.
- `-6°C heat_pump_energy`: `63914.14565251955 Wh`; auxiliary `0.0 Wh`.

# Effective Ratio Decision

The remaining mismatch after `rated_maximum` branch fixes was not caused by the E.2.36~E.2.40 branch structure. It came from applying exact config ratios directly in the frost-region non-max curves when `round_test_values=true`.

Applied official-calculator-compatible effective ratios:

- capacity: `round_half_up(4165.3) / round_half_up(round_half_up(4165.3) / (1 / 1.12)) = 4165 / 4665`
- power: `round_half_up(1603.9) / round_half_up(round_half_up(1603.9) / (1 / 1.06)) = 1604 / 1700`

When `round_test_values=false`, the helper returns the existing config/default exact ratio.

# Changed Files

- `core/calculators/standards/ks_c9306.py`
- `tests/helpers/iso16358_hspf_samples.py`
- `tests/test_iso16358_hspf_validation.py`
- `result_reports/active/650_ks-hspf-load-line-intersection-golden.md`

# Known Failures / Risks

- PRH `Pheater * frunning` remains intentionally unimplemented. Current product has no auxiliary heater, so this remains a known non-impact gap for this golden.
- The `tj <= 2.0 and load > max_stage["capacity"]` special case was left unchanged by request.
- Full pytest was not run; requested focused and optional KS/ISO HSPF suites passed.

# Next Suggested Action

- Track the PRH `Pheater * frunning` gap as a separate schema/API task if products with auxiliary heaters need official KS coverage.

# Scope Compliance

- CSPF path unchanged.
- ISO16358 official exact/oracle values unchanged.
- AHRI/EN paths unchanged.
- Public schema and `korea.json` schema unchanged.
- No direct bin-energy override or arbitrary correction factor was added.

# Structure Warnings

- `core/calculators/standards/ks_c9306.py` still exceeds the LOC soft limit; this is pre-existing and accepted for this narrow calculator fix.
- Code map freshness warning remains. `code_map_check`: skipped because no new source structure, helper package, adapter, or reusable boundary was added.

# Warning Triage

- accepted for this slice with reason: narrow in-place calculator fix avoids a larger KS HSPF split outside the requested scope.

# Commit / Push

- Commit: requested after implementation; final commit hash is reported in terminal output.
- Push: requested after implementation; final remote match is reported in terminal output.

# Project Memory Delta

- type: decision
- topic: KS C 9306 HSPF frost effective ratio
- content: For `round_test_values=true`, KS HSPF non-max frost curves use rounding-aware effective defrost/no-frost ratios derived from rounded max defrost anchors: capacity `4165 / 4665`, power `1604 / 1700`. This matches strict KS official total and bin-level oracle without changing expected fixtures or overriding bin energy.
- keywords: KS C 9306, HSPF, official oracle, frost, defrost ratio, round_test_values, effective ratio
