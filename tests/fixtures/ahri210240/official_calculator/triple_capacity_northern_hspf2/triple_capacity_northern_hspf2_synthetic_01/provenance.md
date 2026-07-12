# Provenance: ahri210240_triple_capacity_northern_hspf2_synthetic_01

- Official source: AHRI Analytics official calculation app
- Official standard/oracle scope: AHRI 210/240 (2023), Appendix M and Appendix M1
- Calculation URL: https://seerhspf2.ahrianalytics.org/app/seerhspf2
- Calculation date: 2026-07-12
- Calculator/version displayed: not displayed
- Product type: HSPF → Northern Heat Pump → Triple Stage Northern Heat Pump
- Mode: heating
- DHR/DOE setting: {"dhr_selection": "Minimum", "doe_region": "Region 4"}
- Certification claim: false; raw result evidence only
- 2023/2026 boundary: AHRI 210/240-2026 final formula is not established by this fixture; direct golden use requires a standards audit.

## Corrected normalized schema

- `input_fields` preserves every input CSV header, including booleans and blanks.
- `raw_fields` preserves every M/M1 result CSV header/value; missing raw fields are integrity failures.
- `performance_curve_groups` labels raw `k1/k2/k3` curve groups only; they are not operating cases.
- `seasonal_aggregates` uses `normalized_name`, `unit: not exposed`, and candidate interpretation metadata without inventing raw-header semantics.

## Screen headline values

| Result | Screen value | Raw CSV field | Raw value | Raw field count |
|---|---:|---|---:|---:|
| M | 10.65 | `M.HSPF` | 10.6480406437411 | 276 |
| M1 | 10.05 | `M1.HSPF` | 10.0473265237749 | 275 |

## Input options and normalized test-point groups

- Performance curve groups: k1, k2, k3 (raw curve groups only).
- Activated operating cases: case1, case2, case3, case8, 0.
- Operating-case source: Northern official raw case_name fields retained verbatim; k1/k2/k3 are performance curve groups.

| Group | Raw fields / values |
|---|---|
| `ui_options` | `compressorDesignStage`='Triple Stages', `indoorBlowerType`='Fixed Speed/PSC', `needCoilOnlyAdjust`=False, `isMobileHomeAndSpaceConstrained`=False, `isNonmobileHomeAndNonSpaceConstrained`=True, `lockOutLowCapacityOps`=False, `ODTempWhenLockOut`=-20 |
| `tested_optional_points` | `H23Tested`=True, `H21Tested`=True, `H31Tested`=True, `T_off`=-45, `T_on`=-45, `isDemandDefrost`=True, `demandDefrostCredit`=1.028571429 |
| `compressor_cut_in_cut_out` | `ODTempWhenLockOut`=-20, `compOperationTemp_k1_lower`=40, `compOperationTemp_k1_upper`=65, `compOperationTemp_k2_lower`=20, `compOperationTemp_k2_upper`=50, `compOperationTemp_k3_lower`=-20, `compOperationTemp_k3_upper`=30, `T_off`=-45, `T_on`=-45 |
| `degradation_coefficients` | `degCoeffHeatBoost`=0.18, `degCoeffHeatFull`=0.22, `degCoeffHeatMin`=0.28 |
| `input_test_points` | `coolCapacity95Full`=30000, `heatCapacity62min`=26000, `heatCapacity47full`=28000, `heatCapacity47min`=21000, `heatCapacity35boost`=30000, `heatCapacity35full`=25500, `heatCapacity35min`=18500, `heatCapacity17boost`=28000, `heatCapacity17full`=22000, `heatCapacity17min`=14500, `heatCapacity5boost`=25000, `powerConsumption62min`=1350, `powerConsumption47full`=1850, `powerConsumption47min`=1300, `powerConsumption35boost`=2400, `powerConsumption35full`=2050, `powerConsumption35min`=1550, `powerConsumption17boost`=3000, `powerConsumption17full`=2350, `powerConsumption17min`=1750, `powerConsumption5boost`=3400, `scfm95full`=800, `scfm62min`=800, `scfm47full`=800, `scfm47min`=800, `scfm35boost`=800, `scfm35full`=800, `scfm35min`=800, `scfm17boost`=800, `scfm17full`=800, `scfm17min`=800, `scfm5boost`=800 |

## State and raw-result projections

- Official raw case-name distribution: `{"M": {"case1": 5, "case2": 4, "case3": 3, "case8": 5, "0": 1}, "M1": {"case1": 5, "case2": 4, "case3": 1, "case8": 7, "0": 1}}`

### M

- DHR raw field/value: `M.DHR` / `30000`.
- Building-load raw fields: 18.
- Resistance/auxiliary raw fields: 18; sum `3.7342513917374784`.
- Raw case-name fields: `{"M.case_name1": "case1", "M.case_name2": "case1", "M.case_name3": "case1", "M.case_name4": "case1", "M.case_name5": "case1", "M.case_name6": "case2", "M.case_name7": "case2", "M.case_name8": "case2", "M.case_name9": "case2", "M.case_name10": "case3", "M.case_name11": "case3", "M.case_name12": "case3", "M.case_name13": "case8", "M.case_name14": "case8", "M.case_name15": "case8", "M.case_name16": "case8", "M.case_name17": "case8", "M.case_name18": "0"}`.
- Cutout delta distribution: `{"cutOut_delta_doublePrime": {"raw_columns": ["M.cutOut_delta_doublePrime1", "M.cutOut_delta_doublePrime2", "M.cutOut_delta_doublePrime3", "M.cutOut_delta_doublePrime4", "M.cutOut_delta_doublePrime5", "M.cutOut_delta_doublePrime6", "M.cutOut_delta_doublePrime7", "M.cutOut_delta_doublePrime8", "M.cutOut_delta_doublePrime9", "M.cutOut_delta_doublePrime10", "M.cutOut_delta_doublePrime11", "M.cutOut_delta_doublePrime12", "M.cutOut_delta_doublePrime13", "M.cutOut_delta_doublePrime14", "M.cutOut_delta_doublePrime15", "M.cutOut_delta_doublePrime16", "M.cutOut_delta_doublePrime17", "M.cutOut_delta_doublePrime18"], "raw_values": [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], "counts": {"one": 14, "fractional": 0, "zero": 4, "other": 0, "blank": 0}}, "cutOut_delta_prime": {"raw_columns": ["M.cutOut_delta_prime1", "M.cutOut_delta_prime2", "M.cutOut_delta_prime3", "M.cutOut_delta_prime4", "M.cutOut_delta_prime5", "M.cutOut_delta_prime6", "M.cutOut_delta_prime7", "M.cutOut_delta_prime8", "M.cutOut_delta_prime9", "M.cutOut_delta_prime10", "M.cutOut_delta_prime11", "M.cutOut_delta_prime12", "M.cutOut_delta_prime13", "M.cutOut_delta_prime14", "M.cutOut_delta_prime15", "M.cutOut_delta_prime16", "M.cutOut_delta_prime17", "M.cutOut_delta_prime18"], "raw_values": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], "counts": {"one": 18, "fractional": 0, "zero": 0, "other": 0, "blank": 0}}, "cutOut_delta": {"raw_columns": ["M.cutOut_delta1", "M.cutOut_delta2", "M.cutOut_delta3", "M.cutOut_delta4", "M.cutOut_delta5", "M.cutOut_delta6", "M.cutOut_delta7", "M.cutOut_delta8", "M.cutOut_delta9", "M.cutOut_delta10", "M.cutOut_delta11", "M.cutOut_delta12", "M.cutOut_delta13", "M.cutOut_delta14", "M.cutOut_delta15", "M.cutOut_delta16", "M.cutOut_delta17", "M.cutOut_delta18"], "raw_values": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], "counts": {"one": 18, "fractional": 0, "zero": 0, "other": 0, "blank": 0}}}`.
- Seasonal aggregate columns and sums:

| Normalized name | Raw columns | Sum | Unit |
|---|---|---:|---|
| `raw_ratio_total_heating` | 18 columns | 9211.125 | `not exposed` |
| `raw_ratio_total_resist_heating` | 18 columns | 3.7342513917374784 | `not exposed` |
| `raw_ratio_total_power` | 18 columns | 886.0597954190388 | `not exposed` |

### M1

- DHR raw field/value: `None` / `None`.
- Building-load raw fields: 18.
- Resistance/auxiliary raw fields: 18; sum `89.26457661881034`.
- Raw case-name fields: `{"M1.case_name1": "case1", "M1.case_name2": "case1", "M1.case_name3": "case1", "M1.case_name4": "case1", "M1.case_name5": "case1", "M1.case_name6": "case2", "M1.case_name7": "case2", "M1.case_name8": "case2", "M1.case_name9": "case2", "M1.case_name10": "case3", "M1.case_name11": "case8", "M1.case_name12": "case8", "M1.case_name13": "case8", "M1.case_name14": "case8", "M1.case_name15": "case8", "M1.case_name16": "case8", "M1.case_name17": "case8", "M1.case_name18": "0"}`.
- Cutout delta distribution: `{"cutOut_delta_doublePrime": {"raw_columns": ["M1.cutOut_delta_doublePrime1", "M1.cutOut_delta_doublePrime2", "M1.cutOut_delta_doublePrime3", "M1.cutOut_delta_doublePrime4", "M1.cutOut_delta_doublePrime5", "M1.cutOut_delta_doublePrime6", "M1.cutOut_delta_doublePrime7", "M1.cutOut_delta_doublePrime8", "M1.cutOut_delta_doublePrime9", "M1.cutOut_delta_doublePrime10", "M1.cutOut_delta_doublePrime11", "M1.cutOut_delta_doublePrime12", "M1.cutOut_delta_doublePrime13", "M1.cutOut_delta_doublePrime14", "M1.cutOut_delta_doublePrime15", "M1.cutOut_delta_doublePrime16", "M1.cutOut_delta_doublePrime17", "M1.cutOut_delta_doublePrime18"], "raw_values": [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], "counts": {"one": 14, "fractional": 0, "zero": 4, "other": 0, "blank": 0}}, "cutOut_delta_prime": {"raw_columns": ["M1.cutOut_delta_prime1", "M1.cutOut_delta_prime2", "M1.cutOut_delta_prime3", "M1.cutOut_delta_prime4", "M1.cutOut_delta_prime5", "M1.cutOut_delta_prime6", "M1.cutOut_delta_prime7", "M1.cutOut_delta_prime8", "M1.cutOut_delta_prime9", "M1.cutOut_delta_prime10", "M1.cutOut_delta_prime11", "M1.cutOut_delta_prime12", "M1.cutOut_delta_prime13", "M1.cutOut_delta_prime14", "M1.cutOut_delta_prime15", "M1.cutOut_delta_prime16", "M1.cutOut_delta_prime17", "M1.cutOut_delta_prime18"], "raw_values": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], "counts": {"one": 18, "fractional": 0, "zero": 0, "other": 0, "blank": 0}}, "cutOut_delta": {"raw_columns": ["M1.cutOut_delta1", "M1.cutOut_delta2", "M1.cutOut_delta3", "M1.cutOut_delta4", "M1.cutOut_delta5", "M1.cutOut_delta6", "M1.cutOut_delta7", "M1.cutOut_delta8", "M1.cutOut_delta9", "M1.cutOut_delta10", "M1.cutOut_delta11", "M1.cutOut_delta12", "M1.cutOut_delta13", "M1.cutOut_delta14", "M1.cutOut_delta15", "M1.cutOut_delta16", "M1.cutOut_delta17", "M1.cutOut_delta18"], "raw_values": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], "counts": {"one": 18, "fractional": 0, "zero": 0, "other": 0, "blank": 0}}}`.
- Seasonal aggregate columns and sums:

| Normalized name | Raw columns | Sum | Unit |
|---|---|---:|---|
| `raw_ratio_total_heating` | 18 columns | 10398.99 | `not exposed` |
| `raw_ratio_total_resist_heating` | 18 columns | 89.26457661881034 | `not exposed` |
| `raw_ratio_total_power` | 18 columns | 975.3371449127085 | `not exposed` |

## Raw evidence checksums

| File | SHA-256 |
|---|---|
| `input_template.csv` | `c5bb39c862478f38ad8dd17f9d5105147f71cf4bcfdf5ef12d8c8aef4a5c0fa2` |
| `input.csv` | `17cf4b3596e1a7e1130c2c8fd785d274c7f12cb5375e39ebb63654d7743d3550` |
| `result_m.csv` | `cf745158e57a8b929d9515a0335e600a70c0157a2d72b2bc1369eb1ca554003f` |
| `result_m1.csv` | `f0ffa31e331fcac536b482e968a52bc0c91534ff40059c867b36c752054ce588` |

## Reproduction procedure

1. Open the official calculator URL in Chrome.
2. Select `HSPF → Northern Heat Pump → Triple Stage Northern Heat Pump`.
3. Upload `input.csv` and choose Replace Input Table.
4. Confirm the normalized input options and test-point row.
5. Run Calculate/Update.
6. Download Full Results (M) and Full Results (M1) as `result_m.csv` and `result_m1.csv`.

## Known limitations

- Calculator/version information was not displayed in the UI.
- Downloaded result CSVs do not expose explicit bin temperature or bin-hour columns; raw field names and values are retained.
- Raw headers without an official semantic mapping are preserved with normalized_name/unit/interpretation candidate metadata only.
- M1 HSPF result CSVs do not expose a separate DHR field; the input DHR/DOE selection is retained above.
- This is official-calculator evidence, not a certification claim or production formula fixture.
- AHRI 210/240-2026 final formula is not established by this fixture; direct golden use requires a standards audit.
