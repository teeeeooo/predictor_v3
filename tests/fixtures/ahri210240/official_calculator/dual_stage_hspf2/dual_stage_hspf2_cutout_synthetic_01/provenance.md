# Provenance: ahri210240_dual_stage_hspf2_cutout_synthetic_01

- Official source: AHRI Analytics official calculation app
- Official standard/oracle scope: AHRI 210/240 (2023), Appendix M and Appendix M1
- Calculation URL: https://seerhspf2.ahrianalytics.org/app/seerhspf2
- Calculation date: 2026-07-12
- Calculator/version displayed: not displayed
- Product type: HSPF → Dual Stage
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
| M | 4.28 | `M.HSPF` | 4.28461472949153 | 200 |
| M1 | 3.89 | `M1.HSPF` | 3.89179789143965 | 199 |

## Input options and normalized test-point groups

- Performance curve groups: k1, k2 (raw curve groups only).
- Activated operating cases: load_at_or_below_low_stage, between_low_and_high_stage, above_high_stage, high_stage_with_auxiliary_heat.
- Operating-case source: Reclassified from raw building load against raw low/high stage capacity; k1/k2 remain performance curve groups.

| Group | Raw fields / values |
|---|---|
| `ui_options` | `compressorDesignStage`='Dual Stage', `indoorBlowerType`='Fixed Speed/PSC', `needCoilOnlyAdjust`=False, `isMobileHomeAndSpaceConstrained`=False, `isNonmobileHomeAndNonSpaceConstrained`=True, `lockOutLowCapacityOps`=False, `ODTempWhenLockOut`=40 |
| `tested_optional_points` | `H4Tested`=True, `H21Tested`=True, `T_off`=35, `T_on`=45, `isDemandDefrost`=False, `demandDefrostCredit`=1.03 |
| `compressor_cut_in_cut_out` | `ODTempWhenLockOut`=40, `T_off`=35, `T_on`=45 |
| `degradation_coefficients` | `degCoeffHeatFull`=0.22, `degCoeffHeatMin`=0.18 |
| `input_test_points` | `lockOutLowCapacityOps`=False, `coolCapacity95Full`=30000, `heatCapacity62min`=22000, `heatCapacity47full`=25000, `heatCapacity47min`=18000, `heatCapacity35full`=21500, `heatCapacity35min`=14500, `heatCapacity17full`=19500, `heatCapacity17min`=10500, `heatCapacity5full`=17000, `powerConsumption62min`=1450, `powerConsumption47full`=1800, `powerConsumption47min`=1350, `powerConsumption35full`=1900, `powerConsumption35min`=1450, `powerConsumption17full`=2100, `powerConsumption17min`=1600, `powerConsumption5full`=2300, `scfm95full`=800, `scfm62min`=800, `scfm47full`=800, `scfm47min`=800, `scfm35full`=800, `scfm35min`=800, `scfm17full`=800, `scfm17min`=800, `scfm5full`=800 |

## Regime and raw-result projections

- Regime distribution: `{"M": {"load_at_or_below_low_stage": 8, "between_low_and_high_stage": 3, "high_stage_with_auxiliary_heat": 4, "above_high_stage": 3}, "M1": {"load_at_or_below_low_stage": 6, "between_low_and_high_stage": 2, "high_stage_with_auxiliary_heat": 7, "above_high_stage": 3}}`

### M

- DHR raw field/value: `M.DHR` / `25000`.
- Building-load raw fields: 18.
- Resistance/auxiliary raw fields: 18; sum `1593.5442914347102`.
- Northern raw case names: `{}`.
- Cutout delta distribution: `{"cutOut_delta_prime": {"raw_columns": ["M.cutOut_delta_prime1", "M.cutOut_delta_prime2", "M.cutOut_delta_prime3", "M.cutOut_delta_prime4", "M.cutOut_delta_prime5", "M.cutOut_delta_prime6", "M.cutOut_delta_prime7", "M.cutOut_delta_prime8", "M.cutOut_delta_prime9", "M.cutOut_delta_prime10", "M.cutOut_delta_prime11", "M.cutOut_delta_prime12", "M.cutOut_delta_prime13", "M.cutOut_delta_prime14", "M.cutOut_delta_prime15", "M.cutOut_delta_prime16", "M.cutOut_delta_prime17", "M.cutOut_delta_prime18"], "raw_values": [1, 1, 1, 1, 0.5, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "counts": {"one": 4, "fractional": 2, "zero": 12, "other": 0, "blank": 0}}, "cutOut_delta": {"raw_columns": ["M.cutOut_delta1", "M.cutOut_delta2", "M.cutOut_delta3", "M.cutOut_delta4", "M.cutOut_delta5", "M.cutOut_delta6", "M.cutOut_delta7", "M.cutOut_delta8", "M.cutOut_delta9", "M.cutOut_delta10", "M.cutOut_delta11", "M.cutOut_delta12", "M.cutOut_delta13", "M.cutOut_delta14", "M.cutOut_delta15", "M.cutOut_delta16", "M.cutOut_delta17", "M.cutOut_delta18"], "raw_values": [1, 1, 1, 1, 0.5, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "counts": {"one": 4, "fractional": 2, "zero": 12, "other": 0, "blank": 0}}}`.
- Seasonal aggregate columns and sums:

| Normalized name | Raw columns | Sum | Unit |
|---|---|---:|---|
| `raw_ratio_total_heating` | 18 columns | 7675.937499999999 | `not exposed` |
| `raw_ratio_total_resist_heating` | 18 columns | 1593.5442914347102 | `not exposed` |
| `raw_ratio_total_power` | 18 columns | 197.9674277323762 | `not exposed` |

### M1

- DHR raw field/value: `None` / `None`.
- Building-load raw fields: 18.
- Resistance/auxiliary raw fields: 18; sum `2504.2572516847345`.
- Northern raw case names: `{}`.
- Cutout delta distribution: `{"cutOut_delta_prime": {"raw_columns": ["M1.cutOut_delta_prime1", "M1.cutOut_delta_prime2", "M1.cutOut_delta_prime3", "M1.cutOut_delta_prime4", "M1.cutOut_delta_prime5", "M1.cutOut_delta_prime6", "M1.cutOut_delta_prime7", "M1.cutOut_delta_prime8", "M1.cutOut_delta_prime9", "M1.cutOut_delta_prime10", "M1.cutOut_delta_prime11", "M1.cutOut_delta_prime12", "M1.cutOut_delta_prime13", "M1.cutOut_delta_prime14", "M1.cutOut_delta_prime15", "M1.cutOut_delta_prime16", "M1.cutOut_delta_prime17", "M1.cutOut_delta_prime18"], "raw_values": [1, 1, 1, 1, 0.5, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "counts": {"one": 4, "fractional": 2, "zero": 12, "other": 0, "blank": 0}}, "cutOut_delta": {"raw_columns": ["M1.cutOut_delta1", "M1.cutOut_delta2", "M1.cutOut_delta3", "M1.cutOut_delta4", "M1.cutOut_delta5", "M1.cutOut_delta6", "M1.cutOut_delta7", "M1.cutOut_delta8", "M1.cutOut_delta9", "M1.cutOut_delta10", "M1.cutOut_delta11", "M1.cutOut_delta12", "M1.cutOut_delta13", "M1.cutOut_delta14", "M1.cutOut_delta15", "M1.cutOut_delta16", "M1.cutOut_delta17", "M1.cutOut_delta18"], "raw_values": [1, 1, 1, 1, 0.5, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "counts": {"one": 4, "fractional": 2, "zero": 12, "other": 0, "blank": 0}}}`.
- Seasonal aggregate columns and sums:

| Normalized name | Raw columns | Sum | Unit |
|---|---|---:|---|
| `raw_ratio_total_heating` | 18 columns | 10398.99 | `not exposed` |
| `raw_ratio_total_resist_heating` | 18 columns | 2504.2572516847345 | `not exposed` |
| `raw_ratio_total_power` | 18 columns | 167.7699938393656 | `not exposed` |

## Raw evidence checksums

| File | SHA-256 |
|---|---|
| `input_template.csv` | `0a7d124814a2cb94e1fcda11d314dc6884d5196012e2365bc2d217db31259c81` |
| `input.csv` | `43063541c2739de9be7dcf748fc291af0ad26912553125ca1be38043589b3e7c` |
| `result_m.csv` | `045360950de236133abc4c6235fdcd373c629e1eb0671ecf728802c540b20f09` |
| `result_m1.csv` | `ef744d3d4a541564cef07d88553684d2d28dbc1ba541f17b36efc8b9906ae7e6` |

## Reproduction procedure

1. Open the official calculator URL in Chrome.
2. Select `HSPF → Dual Stage`.
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
