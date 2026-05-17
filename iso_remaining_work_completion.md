# ISO Remaining Work Completion

## Summary

- Finished the active ISO HSPF remaining work from `iso_separation_result.md`.
- Archived the old mixed ISO implementation at `core/_legacy/calculator_iso16358_legacy.py`.
- Added current local AS/NZS workbook CSPF compatibility coverage alongside existing HSPF compatibility coverage.
- Updated maintained docs to reflect the new state.

## Implemented

- `core/calculator_iso16358.py`
  - Branch routing now uses Formula 44/45/47/48/49/50 helper paths.
  - Frost extended routing can use canonical `2_ext` plus the configured/default `-7_ext` fallback.
- `core/calculator_asnzs_hspf_excel.py`
  - Existing HSPF workbook snapshot behavior remains under `ASNZS_EXCEL_COMPAT`.
  - Added `calculate_cspf()` for current workbook cooling snapshot rows.
- Legacy calculator
  - Moved from `core/calculator_iso16358_legacy.py` to `core/_legacy/calculator_iso16358_legacy.py`.
  - Remaining legacy diagnostic imports now use the archived namespace.
- Tests
  - Added current workbook CSPF exact-match coverage.
  - Updated ISO formula micro and Hong Kong HSPF expected values to match active formula routing.
  - Marked pre-separation workbook diagnostic expectations as explicit xfail.

## AS/NZS Scope Decision

Web/public evidence was enough to confirm that the Energy Rating workbook is an AS/NZS 3823.4:2014 A1 estimation tool, but not enough to reconstruct an independent official production calculator. Therefore this completion implements repo-local workbook compatibility, not a claim of full official standards-body formula parity.

Source checked: Energy Rating SEER Calculator, `https://www.energyrating.gov.au/industry-information/publications/seasonal-energy-efficiency-ratios-seer-calculator`.

## Verification

- Targeted ISO/ASNZS checks: `81 passed, 21 xfailed`.
- Full suite: `288 passed, 23 xfailed`.

## Remaining Risk

- Historical AS/NZS case3 full-dump exact parity remains deferred until the matching workbook/full dump is available.
- Calculator UI exposure still needs interactive Qt smoke before production use.
