# Audit Report: ISO 16358-2 HSPF vs Official XLSM

## Goal
Verify that `core/calculator_iso16358.py`'s HSPF common engine matches the official ISO 16358-2 AMD1 XLSM calculation formulas for variable-capacity (inverter) units.

## Scope
- **Target:** `core/calculator_iso16358.py` HSPF common path (lines 829–1601)
- **Reference:** `reference_files/iso16358_test_sheet.xlsx` — `Inverter AC` sheet, ISO 16358 zone
  - Formulas extracted directly from Excel cells using `openpyxl` (formula mode)
  - Not interpreted from project internal docs
- **Out of scope:** CSPF (cooling), KS C 9306 profile path, legacy fallback

## Changed Files
- `reference_files/audit_iso16358_hspf_xlsm.md` — detailed audit report
- This report file

## Verification

### Method
1. Extracted actual Excel formulas (not values) from the XLSM `Inverter AC` sheet
2. Cross-mapped each XLSM formula against the corresponding Python function
3. Verified numeric constants (test points, default factors, bin hours) against both XLSM and code

### Results (19/19 Pass)

| # | Item | XLSM Formula | Code | Result |
|---|------|-------------|------|--------|
| 1 | Load line | `BL = 3589.14 × (17 - tj) / 17` | `_iso_hspf_evaluate_common_bin` | Pass |
| 2 | Non-frost capacity | `cap(-7) + (cap(7)-cap(-7))×(tj+7)/14` | `_iso_hspf_capacity_curve` | Pass |
| 3 | Frost capacity | `cap(-7) + (cap(2f)-cap(-7))×(tj+7)/9` | `_iso_hspf_capacity_curve` | Pass |
| 4 | Non-frost power | Same linear interpolation | `_iso_hspf_power_curve` | Pass |
| 5 | Frost power | Same linear interpolation | `_iso_hspf_power_curve` | Pass |
| 6 | Frost判定 | `tj < 5.5 AND tj > -7` | `frost_lower < tj < frost_upper` | Pass |
| 7 | Cycling PLF | `X=BL/φmin, FPL=1-Cd(1-X), P=X·Pmin/FPL` | `_iso_hspf_calculate_common_branch_power` | Pass |
| 8 | Min→Half (F44/48) | Boundary COP interp, `P=BL/COP` | `_iso_hspf_min_half_power_by_formula_44_48` | Pass |
| 9 | Half→Full (F45/49) | Boundary COP interp, `P=BL/COP` | `_iso_hspf_half_full_power_by_formula_45_49` | Pass |
| 10 | Full→Extended (F47) | Boundary COP interp, `P=BL/COP` | `_iso_hspf_formula47_*` | Pass |
| 11 | Full→Extended frost (F50) | Boundary COP interp, `P=BL/COP` | `_iso_hspf_formula50_*` | Pass |
| 12 | Saturated / Auxiliary | `P=P_max, aux=BL-φmax` | saturated branch | Pass |
| 13 | Without-min fallback | Cycling on φhalf | `active_stages` logic | Pass |
| 14 | HSTL | `Σ BL×nj` | `hstl += bl_h * nj` | Pass |
| 15 | HSEC | `Σ (heat_pump + auxiliary) × nj` | `hsec += E_j` | Pass |
| 16 | HSPF | `HSTL / HSEC` | `hspf = hstl / hsec` | Pass |
| 17 | Test points | H1: 4377/1313, 2280/448, 684/151 | `_iso_hspf_normalize_common_points` | Pass |
| 18 | −7°C default | `0.64×cap, 0.82×pow` | `_iso_hspf_minus7_fallback_factors` | Pass |
| 19 | 2°C footnote d | −7↔7 line calculation | `_iso_hspf_point_on_minus7_to_7_line` | Pass |

### XLSM Golden Values (for this fixture)
- LHST = 4,972,859 Wh
- CHSE = 1,145,363 Wh
- HSPF = 4.342 W/W

## Known Risks
- **None.** No formula mismatches found.
- The `iso16358_test_sheet.xlsx` Inverter AC sheet can serve as a direct golden oracle for regression testing.
- Above-extended saturated behavior is not fully specified by ISO 16358-2; both XLSM and code fall back to the highest available stage.

## Scope Compliance
- Did not modify any source code, golden values, or project internal docs.
- Used only the external XLSM reference file as authority.
- All comparisons are formula-structure checks, not golden value assertions.

## Commit / Push
- `report: audit ISO 16358-2 HSPF against official XLSM formulas`
