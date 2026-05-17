# ISO Remaining Work Completion

## Scope

- Finish the active ISO HSPF formula routing work left by `iso_separation_result.md`.
- Move the old mixed ISO implementation out of the active calculator namespace.
- Complete the current local AS/NZS Energy Rating workbook compatibility snapshot for both HSPF and CSPF.

## Boundary

- `core/calculator_iso16358.py` remains ISO 16358 common logic only.
- `core/_legacy/calculator_iso16358_legacy.py` is archived reference code. Active production callers must not import it.
- `core/calculator_asnzs_hspf_excel.py` remains an opt-in `ASNZS_EXCEL_COMPAT` workbook compatibility calculator. It may reproduce local workbook snapshot rows, but must not become the ISO common expected source.

## AS/NZS Evidence Decision

Public web evidence is sufficient to identify the Energy Rating SEER workbook as an AS/NZS 3823.4:2014 A1 estimation tool, but not sufficient to reconstruct the full official standard formulas independently. Therefore this completion treats "AS/NZS complete" as current workbook compatibility completion, not as an official standards-body production calculator.

Source checked: Energy Rating, "Seasonal Energy Efficiency Ratios SEER Calculator" (`https://www.energyrating.gov.au/industry-information/publications/seasonal-energy-efficiency-ratios-seer-calculator`).

## Implementation Decisions

- ISO HSPF active branch routing calls Formula 44/45/47/48/49/50 helper paths instead of branch-local capacity-linear power interpolation.
- Frost extended branch selection accepts a canonical `2_ext` candidate and uses the configured/default `-7_ext` fallback when the workbook/config does not provide an explicit `-7_ext` point.
- Current workbook CSPF exact-match uses the `Inverter AC` cooling rows and anchors from `reference_files/iso16358_test_sheet.xlsx`.
- Historical case3 workbook diagnostics remain xfail because they depend on pre-separation workbook-oracle expectations and a matching full workbook dump that is not present.

## Verification Contract

- Targeted ISO HSPF formula/validation tests must pass.
- AS/NZS HSPF and CSPF current workbook snapshot tests must pass.
- Legacy ISO imports must point to `core._legacy.calculator_iso16358_legacy`.
- Full suite must not contain unexpected failures.
