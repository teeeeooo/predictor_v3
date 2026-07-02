# Audit Report: ISO 16358-2 HSPF vs Official XLSM Formulas

## Goal
Verify that `core/calculator_iso16358.py`'s ISO 16358-2 HSPF common engine (`calculate_hspf_iso16358_common`) accurately implements the variable-capacity heating calculation formulas defined in the official ISO 16358-2 AMD1 Calculation Tool XLSM.

## Scope
- **Target file:** `core/calculator_iso16358.py` (HSPF common path, lines 829–1601)
- **Reference source:** `reference_files/iso16358_test_sheet.xlsx`, sheet `Inverter AC`
  - This is the official ISO 16358-1/2 seasonal performance calculation workbook, distributed by ISO/TC 86/SC 6.
  - Formulas were directly extracted from Excel cells (not data values, but the actual `=...` formulas).
- **Focus:** Variable-capacity (inverter) heating path, ISO 16358 zone.
- **Out of scope:** Cooling (CSPF), KS C 9306 profile path, legacy flat-config fallback.

## Non-goals
- No code changes were made during this audit.
- No golden values or test fixtures were modified.
- No internal project interpretation documents (`docs/iso16358/*.md`) were used as authority.

## Verification
- Direct formula extraction from XLSM using `openpyxl` (formula mode, not `data_only`).
- Line-by-line mapping between XLSM cell formulas and Python functions.
- All numerical constants (test points, default factors, bin hours) cross-checked against XLSM active values.

---

## Executive Summary

`core/calculator_iso16358.py`'s HSPF common engine **exactly matches** the official ISO 16358-2 AMD1 XLSM calculation methodology. All 19 inspected formula structures—capacity curves, power curves, load line, frost判定, cycling PLF, boundary-COP interpolation (Formula 44–50), saturated/auxiliary handling, and seasonal accumulation—are structurally identical to the XLSM reference.

No discrepancies were found.

---

## 1. Reference Source: Official ISO 16358-2 XLSM

### 1.1 Source Identity

| Item | Value |
|------|-------|
| **File** | `reference_files/iso16358_test_sheet.xlsx` |
| **Sheet** | `Inverter AC` |
| **Zone selector** | `E5 = "ISO 16358"` |
| **Heating test points** | H1 Full/Half/Min, H2 Ext_f/Full_f/Half_f, H3 Ext/Full/Half (ISO 16358-2 Table 1) |
| **Degradation coefficient** | `E59 = 0.25` |
| **Climate** | ISO 16358 generic heating bin hours from `Temp Bin hrs` sheet |

### 1.2 XLSM Output (Golden Values for This Fixture)

| Metric | Value |
|--------|-------|
| LHST (Heating Seasonal Total Load) | 4,972,859 Wh |
| CHSE (Cooling/Heating Seasonal Energy Consumption) | 1,145,363 Wh |
| HSPF (FHSP) | 4.342 W/W |
| Active heating hours | 2,866 h |

---

## 2. Formula-by-Formula Comparison

### 2.1 Building Load Line

| # | XLSM Formula | Code Location | Verdict |
|---|-------------|---------------|---------|
| 1 | `BL(tj) = IF(tj >= 17, 0, 3589.14 * (17 - tj) / (17 - 0))` | `_iso_hspf_evaluate_common_bin` line 1487–1489 | **Pass** |

**Notes:**
- `t0_load = 17°C` (zero heating load temperature) — ISO 16358-2 default.
- `t100_load = 0°C` (full heating load temperature) — ISO 16358-2 default.
- `L_h_ref = 3589.14 W` — derived from `rated_capacity_factor = 0.82` × H1 Full capacity `4377 W`.
- Code uses `load_line_info["l_h_ref"]` calculated from the same `rated_capacity_factor` and `rated_heating_capacity`.

### 2.2 Capacity / Power Curves

| # | XLSM Formula | Code Location | Verdict |
|---|-------------|---------------|---------|
| 2 | Non-frost capacity: `cap(tj,stage) = cap(-7) + (cap(7) - cap(-7)) * (tj + 7) / 14` | `_iso_hspf_capacity_curve` lines 836–838 | **Pass** |
| 3 | Frost capacity: `cap(tj,stage) = cap(-7) + (cap(2_f) - cap(-7)) * (tj + 7) / 9` | `_iso_hspf_capacity_curve` lines 840–842 | **Pass** |
| 4 | Non-frost power: `P(tj,stage) = P(-7) + (P(7) - P(-7)) * (tj + 7) / 14` | `_iso_hspf_power_curve` lines 851–853 | **Pass** |
| 5 | Frost power: `P(tj,stage) = P(-7) + (P(2_f) - P(-7)) * (tj + 7) / 9` | `_iso_hspf_power_curve` lines 855–857 | **Pass** |

### 2.3 Frost / Non-frost Determination

| # | XLSM Formula | Code Location | Verdict |
|---|-------------|---------------|---------|
| 6 | Frost: `AND(tj < 5.5, tj > -7)` | `_iso_hspf_evaluate_common_bin` lines 1493–1495 | **Pass** |

### 2.4 Cycling Branch (Formula 9/10)

| # | XLSM Formula | Code Location | Verdict |
|---|-------------|---------------|---------|
| 7 | `X = BL / φmin`, `FPL = 1 - Cd * (1 - X)`, `P = X * Pmin / FPL` | `_iso_hspf_calculate_common_branch_power` lines 1353–1373 | **Pass** |

### 2.5 Min↔Half Interpolation (Formula 44 / 48)

| # | XLSM Formula | Code Location | Verdict |
|---|-------------|---------------|---------|
| 8 | Boundary temp: intersection of load line and min/half capacity lines → `COP_mh` linear between boundary COPs → `P = BL / COP_mh` | `_iso_hspf_min_half_power_by_formula_44_48` lines 899–918 | **Pass** |

### 2.6 Half↔Full Interpolation (Formula 45 / 49)

| # | XLSM Formula | Code Location | Verdict |
|---|-------------|---------------|---------|
| 9 | Boundary temp: intersection of load line and half/full capacity lines → `COP_hf` linear between boundary COPs → `P = BL / COP_hf` | `_iso_hspf_half_full_power_by_formula_45_49` lines 920–953 | **Pass** |

### 2.7 Full↔Extended Interpolation (Formula 47 / 50)

| # | XLSM Formula | Code Location | Verdict |
|---|-------------|---------------|---------|
| 10 | Non-frost: boundary COP between full and extended → `P = BL / COP_fe` | `_iso_hspf_formula47_full_extended_non_frost_power` lines 1048–1086 | **Pass** |
| 11 | Frost: boundary COP between full_f and ext_f → `P = BL / COP_fe_f` | `_iso_hspf_formula50_full_extended_frost_power` lines 1015–1046 | **Pass** |

### 2.8 Saturated / Auxiliary Branch

| # | XLSM Formula | Code Location | Verdict |
|---|-------------|---------------|---------|
| 12 | `P = P_max(tj)`, `aux_heat = BL - φmax(tj)` | `_iso_hspf_calculate_common_branch_power` saturated branch lines 1455–1468 | **Pass** |

### 2.9 Without-Min Fallback

| # | XLSM Formula | Code Location | Verdict |
|---|-------------|---------------|---------|
| 13 | When no `7_min` measured, cycling uses `φhalf` as lowest stage | `active_stages` logic; cycling selects `"half"` if `"min"` not in stages | **Pass** |

### 2.10 Seasonal Accumulation

| # | XLSM Formula | Code Location | Verdict |
|---|-------------|---------------|---------|
| 14 | HSTL = Σ `BL(tj) * nj` | `calculate_hspf_iso16358_common` line 1576 | **Pass** |
| 15 | HSEC = Σ `P_total(tj) * nj` (heat pump + auxiliary) | `calculate_hspf_iso16358_common` line 1577 | **Pass** |
| 16 | HSPF = HSTL / HSEC | `calculate_hspf_iso16358_common` line 1590 | **Pass** |

### 2.11 Test Point Resolution

| # | XLSM Value / Rule | Code Location | Verdict |
|---|-------------------|---------------|---------|
| 17 | H1: Full 4377/1313, Half 2280/448, Min 684/151 | `_iso_hspf_normalize_common_points` | **Pass** |
| 18 | −7°C default: `cap = 0.64 × H1_full_cap`, `pow = 0.82 × H1_full_pow` | `_iso_hspf_minus7_fallback_factors` lines 955–959 | **Pass** |
| 19 | 2°C `full` / `half`: calculated from −7↔7 line (footnote d) | `_iso_hspf_point_on_minus7_to_7_line` lines 1148–1165 | **Pass** |

---

## 3. What Was NOT Verified from the XLSM

The following items were **outside the scope** of this direct XLSM comparison:

1. **Cooling (CSPF)** — This audit targeted HSPF only. CSPF verification is covered by the existing T1/T3 XLSM extraction in `docs/iso16358/iso16358_dev_notes.md` §15.
2. **Extended non-frost Formula 47 canonical inputs** — The XLSM requires `7_ext` and `-7_ext` for non-frost extended branch. The code enables this only when both are present (`_iso_hspf_has_non_frost_extended_candidate`).
3. **Above-extended saturated behavior** — ISO 16358-2 does not fully specify `BL > φext` in the Formula 50 context. Both XLSM and code fall back to saturated at the highest available stage.
4. **KS C 9306 profile path** — This is a separate profile branch (`_calculate_ks_c9306_hspf`), not the ISO 16358-2 common engine.

---

## 4. Risk Assessment

| Risk | Finding |
|------|---------|
| Formula mismatch between XLSM and code | **None found.** All 19 inspected structures are identical. |
| Boundary temperature precision drift | Both use the same linear intersection algebra. Divergence would only occur from floating-point rounding, not structural differences. |
| Test point schema drift | Code explicitly requires `7_full` and `7_half`; optional `7_min`, `2_ext`, `-7_ext`. This matches the XLSM measured/default toggle structure. |

---

## 5. Recommendations

1. **No code changes are required** for ISO 16358-2 HSPF variable-capacity logic.
2. The `iso16358_test_sheet.xlsx` Inverter AC sheet, when set to `ISO 16358` zone, can serve as a direct golden oracle for regression testing.
3. If future ISO amendments change the XLSM formulas, this audit should be re-run by extracting the new XLSM formulas and comparing against the same code paths.

---

## 6. Verification Method

1. Loaded `reference_files/iso16358_test_sheet.xlsx` with `openpyxl` in formula mode (`data_only=False`).
2. Extracted cell formulas from the `Inverter AC` sheet for rows 12–40 (heating bin loop) and columns 49–100 (heating calculation area).
3. Extracted column headers from rows 8–11 to map XLSM column meanings.
4. Cross-mapped each XLSM formula against the corresponding Python function in `calculator_iso16358.py`.
5. Verified numeric constants (test point temperatures, default factors `0.64/0.82`, `Cd = 0.25`, load-line anchor temperatures `17/0`) against both XLSM active cells and the code.

---

*Report generated: 2026-05-17*  
*Auditor: Agent (OpenCode)*  
*Reference: `reference_files/iso16358_test_sheet.xlsx` — Inverter AC sheet, ISO 16358 zone*  
*Target: `core/calculator_iso16358.py` HSPF common path (lines 829–1601)*
