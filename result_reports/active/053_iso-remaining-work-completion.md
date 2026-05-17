# 053 ISO Remaining Work Completion

## Goal

Finish `iso_separation_result.md` remaining work, archive the legacy mixed ISO implementation, and complete current AS/NZS workbook compatibility coverage.

## Scope

- Active ISO HSPF formula routing.
- Legacy calculator namespace cleanup.
- Current workbook HSPF/CSPF compatibility.
- Maintained docs and result markdown.

## Changes

- Connected ISO HSPF active branch routing to Formula 44/45/47/48/49/50 helper paths.
- Allowed frost extended branch routing from canonical `2_ext` with the existing `-7_ext` fallback rule.
- Moved legacy ISO code to `core/_legacy/calculator_iso16358_legacy.py` and retargeted remaining diagnostic imports.
- Added `calculate_cspf()` to the AS/NZS compatibility calculator and current workbook cooling snapshot tests.
- Updated active formula/golden expectations affected by the formula route change.
- Marked pre-separation workbook diagnostic expectations as explicit xfail.
- Updated project docs and wrote `iso_remaining_work_completion.md`.

## Verification

- `python3 -B -m pytest tests/test_iso16358_hspf_formula_micro.py tests/test_iso16358_hspf_pure_iso_track_a.py tests/test_iso16358_hspf_validation.py tests/test_iso16358_hspf_golden.py tests/test_asnzs_cspf_excel_compat_workbook_current_exact_match.py tests/test_asnzs_hspf_excel_compat_workbook_current_exact_match.py tests/test_asnzs_hspf_excel_compat_result_envelope.py -q`
  - `81 passed, 21 xfailed`
- `python3 -B -m pytest -q`
  - `288 passed, 23 xfailed`

## Remaining Risk

- AS/NZS official production formula parity is not claimed. The implemented scope is current local Energy Rating workbook compatibility.
- Historical AS/NZS case3 full-dump exact parity still requires the matching workbook/full dump.
- Interactive Qt smoke was not run.

## External Source

- Energy Rating SEER Calculator: `https://www.energyrating.gov.au/industry-information/publications/seasonal-energy-efficiency-ratios-seer-calculator`
