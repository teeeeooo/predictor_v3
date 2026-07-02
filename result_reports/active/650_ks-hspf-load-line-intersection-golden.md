# Goal

- Strengthen KS C 9306 HSPF official calculator oracle coverage.
- Fix the confirmed `rated_maximum` frost hardcoding and `tj <= -7.0` maximum-power behavior without changing CSPF, ISO16358, AHRI, EN, public schema, or `korea.json`.

# Scope

- Changed `core/calculators/standards/ks_c9306.py`.
- Changed `tests/helpers/iso16358_hspf_samples.py`.
- Changed `tests/test_iso16358_hspf_validation.py`.
- Updated this active result report.

# Non-goals

- No CSPF logic change.
- No ISO16358 HSPF official exact/golden fixture change.
- No AHRI/EN calculator change.
- No public schema or `korea.json` schema change.
- No PRH `Pheater * frunning` implementation.
- No unrelated refactor or merge.

# Verification

- `python3 -m py_compile core/calculators/standards/ks_c9306.py`: OK.
- `python3 -m pytest tests/test_iso16358_hspf_validation.py -q`: NG, 37 passed / 2 failed. The two failures are the new strict KS official total and bin-level oracle assertions.
- `python3 -B tools/check_code_structure.py`: OK with existing soft warnings, including `ks_c9306.py` LOC and stale code-map reminder.
- `git diff --check`: OK.
- `python3 -m pytest tests/test_iso16358_hspf_validation.py tests/test_iso16358_hspf_official_exact_golden.py -q`: NG, 54 passed / 2 failed. The same two KS official oracle assertions fail.
- `git status --short`: modified source, helper fixture, validation test, and this report.

# Task Results

- task 1: OK - added `KS_C9306_GOLDEN_BIN_EXPECTED` as KS C 9306 official calculator bin-level oracle, separate from ISO16358 official fixtures. `GOLDEN_EXPECTED` is documented as the KS total oracle.
- task 2: NG - full-bin total golden test now uses `rated_cooling_capacity = 3600.0`, verifies `rounded_hspf`, and keeps official totals. `HSTL` and rounded HSPF pass, but `HSEC` and energy totals still miss the strict oracle.
- task 3: NG - bin-level official oracle test was added and confirms all active bins and `load_line_used=True`, but strict heat-pump energy checks still fail from `-6°C` onward.
- task 4: PARTIAL - removed `rated_maximum` `frost=True` hardcoding and uses runtime frost region. Added `tj <= -7.0` maximum-power behavior for `rated_maximum`; this fixes the critical `-8°C`/`-7°C` no-auxiliary regression path after KS test-value rounding.
- task 5: OK - added `rounded_hspf = round(hspf, 3)` while preserving raw `HSPF` and `hspf` for compatibility.
- task 6: OK - this report records the official oracle, load-line source, bin-level regression points, implemented fixes, and remaining mismatch.

# Test Results

Current focused output after this slice:

- `HSTL`: `6651225.0 Wh` (expected `6651225.0 Wh`)
- `HSEC`: `1802566.0508617363 Wh` (expected `1802769.7 Wh`)
- `rounded_hspf`: `3.689` (expected `3.689`)

The strict bin-level oracle now fails first at `-6°C`:

- actual `heat_pump_energy`: `63912.32481624158 Wh`
- expected `heat_pump_energy`: `63914.1 Wh`

# Changed Files

- `core/calculators/standards/ks_c9306.py`
- `tests/helpers/iso16358_hspf_samples.py`
- `tests/test_iso16358_hspf_validation.py`
- `result_reports/active/650_ks-hspf-load-line-intersection-golden.md`

# Known Failures / Risks

- Official strict KS C 9306 total/bin oracle is still not fully matched. The remaining mismatch is not solved by the requested `rated_maximum` hardcoding fix alone.
- HSPF path now applies the existing KS `round_test_values` policy to HSPF stage values, matching the KS owner docs. This improved the low-temperature auxiliary trace but did not fully match official bin-level heat-pump energy.
- PRH `Pheater * frunning` remains intentionally unimplemented. Current product has no auxiliary heater, so this is a known non-impact gap for this golden.
- The `tj <= 2.0 and load > max_stage["capacity"]` special case was left unchanged; current evidence still indicates no result impact for the official golden shortage bins.

# Next Suggested Action

- Audit KS C 9306 Equation E.2.36 / rated-maximum and E.2.37~E.2.40 intersection details against the official calculator trace before adding any correction factor or bin-energy override.

# Scope Compliance

- CSPF path unchanged.
- ISO16358 official exact/oracle values unchanged.
- AHRI/EN paths unchanged.
- Public schema and `korea.json` schema unchanged.
- No direct bin-energy override or arbitrary total correction was added.

# Structure Warnings

- `core/calculators/standards/ks_c9306.py` still exceeds the LOC soft limit; this is pre-existing and accepted for this narrow calculator fix.
- Code map freshness warning remains. `code_map_check`: skipped because no new source structure, helper package, adapter, or reusable boundary was added.

# Warning Triage

- accepted for this slice with reason: narrow in-place calculator fix avoids a larger KS HSPF split outside the requested scope.

# Commit / Push

- Commit: requested after implementation; final commit hash is reported in terminal output to avoid a self-referential report update loop.
- Push: requested after implementation; final remote match is reported in terminal output.

# Project Memory Delta

- type: open_question
- topic: KS C 9306 HSPF official bin-level mismatch after rated_maximum fix
- content: KS official full-bin oracle is now active in tests. Runtime frost flag and `tj <= -7.0` maximum-power behavior are implemented, and raw `HSPF` plus `rounded_hspf` are returned. Strict official total/bin energy still fails without direct bin override; further audit of E.2.36~E.2.40 intersection details is needed.
- keywords: KS C 9306, HSPF, official oracle, bin-level, rated_maximum, round_test_values, intersection
