# Goal

- Make KS C 9306 HSPF stage interpolation use the same resolved load line as bin load calculation.
- Add an active official golden assertion for the Korea full-bin config path.

# Scope

- Changed `core/calculators/standards/ks_c9306.py`.
- Changed `tests/test_iso16358_hspf_validation.py`.
- No CSPF, config schema, public API, UI, legacy diagnostic, or unrelated refactor changes.

# Non-goals

- Did not change `data/region_configs/korea.json`.
- Did not tune golden expected values to current code output.
- Did not merge, push, or update legacy xfail diagnostics.

# Verification

- `python3 -m py_compile core/calculators/standards/ks_c9306.py`: OK.
- `python3 -m pytest tests/test_iso16358_hspf_validation.py -q`: NG, new active full-bin golden assertion fails.
- `python3 -B tools/check_code_structure.py`: OK with existing soft warnings, including `ks_c9306.py` LOC and stale code map warning.
- `git diff --check`: OK.
- `git status --short`: modified source, test, and this report.

# Task Results

- task 1: OK - `_calculate_ks_c9306_hspf()` now resolves a load line once and passes it to both `_ks_hspf_bin_load()` and `_ks_hspf_bin()`. `_ks_hspf_bin()` keeps an optional defaulted `load_line` argument, so existing private helper calls remain valid.
- task 2: NG - active golden test was added with provided expected values, but full-bin Korea config output does not match the expected energy/HSPF values.
- task 3: NG - focused validation fails on the new golden assertion; static checks pass.

# Test Results

New active full-bin test uses `rated_cooling_capacity = 3600.0` because the provided HSTL expected value is exactly implied by Korea full bin hours and `BLh(0) = rated_cooling_capacity * 0.82`.

Observed full-bin output after the load-line forwarding fix:

- `HSPF`: `3.698455716648536`
- `HSTL`: `6651225.0`
- `HSEC`: `1798378.9747865908`
- `heat_pump_energy`: `1780876.6858977017`
- `auxiliary_energy`: `17502.288888888907`

Provided expected:

- `HSPF`: `3.689`
- `HSTL`: `6651225.0`
- `HSEC`: `1802769.7`
- `heat_pump_energy`: `1785292.6`
- `auxiliary_energy`: `17477.1`

The load-line propagation fix is active: manual sanity output showed all 31 bin details with `load_line_used == True`.

# Changed Files

- `core/calculators/standards/ks_c9306.py`
- `tests/test_iso16358_hspf_validation.py`
- `result_reports/active/650_ks-hspf-load-line-intersection-golden.md`

# Known Failures / Risks

- The new active full-bin golden test fails. HSTL matches, but HSEC and energy breakdown do not. The remaining mismatch appears to be formula/detail interpretation beyond load-line forwarding, especially in stage interpolation/maximum-side behavior.
- Full pytest was not run because the requested focused suite already fails.

# Next Suggested Action

- Audit KS C 9306 HSPF E.2.36/E.2.40 rated-maximum and shortage behavior against an accepted bin-level official trace before changing formulas further.

# Scope Compliance

- CSPF path unchanged.
- `korea.json` schema unchanged.
- Public API unchanged; `_ks_hspf_bin()` signature change is defaulted and internal/private.
- UI/UX unchanged.
- Legacy diagnostics unchanged.
- No merge or push performed.

# Structure Warnings

- `core/calculators/standards/ks_c9306.py` still exceeds the LOC soft limit; this is pre-existing and accepted for this narrow fix.
- Code map freshness warning remains; skipped regeneration because this task only changed a narrow existing calculator/test path and did not add source structure.

# Warning Triage

- accepted for this slice with reason: fixing the existing KS HSPF method in place avoids a broader calculator split outside the requested scope.

# Commit / Push

- Commit: not requested.
- Push: not requested.

# Project Memory Delta

- type: open_question
- topic: KS C 9306 HSPF full-bin golden mismatch
- content: After forwarding resolved Korea config load line into `_ks_hspf_bin()`, full-bin HSTL matches the provided golden when `rated_cooling_capacity=3600.0`, and all bins use load-line interpolation, but HSEC/heat-pump/auxiliary expected values still differ. Further formula audit needs accepted bin-level evidence.
- keywords: KS C 9306, HSPF, load line, full-bin golden, rated_maximum, HSEC
