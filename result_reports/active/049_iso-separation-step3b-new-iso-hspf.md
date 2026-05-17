# 049 ISO Separation Step 3b New ISO HSPF

## Goal

`iso_seperation_plan.md` Step 3b 범위에서 새 `core/calculator_iso16358.py`에 ISO 16358-2 HSPF common path를 활성화한다.

## Scope

- 새 ISO calculator에 HSPF Phase 1 helper, variable heating helper, ISO 16358-2 common helper, `calculate_hspf_iso16358_common()`, `calculate_hspf()`를 추가했다.
- Active HSPF tests 중 새 ISO common path 검증에 해당하는 파일을 `core.calculator_iso16358` import로 되돌렸다.
- KS delegation, AS/NZS workbook helper, case3 converted-workbook trace-only method는 새 ISO calculator에 추가하지 않았다.

## Modified Files

- `core/calculator_iso16358.py`
- `tests/test_iso16358_hspf_smoke.py`
- `tests/test_iso16358_hspf_formula_micro.py`
- `tests/test_iso16358_hspf_compatibility_boundary.py`
- `tests/test_iso16358_hspf_hong_kong_config.py`
- `tests/test_iso16358_hspf_pure_iso_track_a.py`
- `tests/test_iso16358_hspf_validation.py`
- `tests/test_iso16358_hspf_ks_oracle.py`
- `project_log.md`

## Verification

- `python3 -B -m py_compile core/calculator_iso16358.py` passed.
- `rg -n "KSC9306|_ks_|ASNZS|asnzs|workbook|CH48|BN|BP|BY|CA|CC|calculate_hspf_iso16358_y_min_y_extd_trace" core/calculator_iso16358.py` returned no matches.
- Targeted Step 3b HSPF files:
  - `python3 -B -m pytest tests/test_iso16358_hspf_smoke.py tests/test_iso16358_hspf_formula_micro.py tests/test_iso16358_hspf_compatibility_boundary.py tests/test_iso16358_hspf_hong_kong_config.py tests/test_iso16358_hspf_pure_iso_track_a.py tests/test_iso16358_hspf_validation.py tests/test_iso16358_hspf_ks_oracle.py -q`
  - Result: `68 passed, 6 failed, 4 xfailed`.
  - The 6 failures are part of the pre-existing ISO HSPF baseline group and were not hidden by expected/tolerance/xfail changes.
- HSPF suite:
  - `python3 -B -m pytest tests/test_iso16358_hspf_*.py tests/_legacy/test_iso16358_hspf_h8_trace.py -q`
  - Result: `93 passed, 16 failed, 11 xfailed`.
- Full suite:
  - `python3 -B -m pytest tests -q`
  - Result: `269 passed, 16 failed, 13 xfailed`.

## Remaining Risk

- ISO HSPF workbook/golden discrepancies remain the known 16-failure baseline.
- `tests/test_iso16358_hspf_golden.py` remains on legacy because it includes converted-workbook/case3 trace diagnostics. A later cleanup can split pure ISO common golden assertions from legacy trace-only diagnostics.
