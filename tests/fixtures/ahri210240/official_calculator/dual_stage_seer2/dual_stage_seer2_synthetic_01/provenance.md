# Provenance: ahri210240_dual_stage_seer2_synthetic_01

- Official source: AHRI Analytics official calculation app
- Official standard/oracle scope: AHRI 210/240 (2023), Appendix M and Appendix M1
- Calculation URL: https://seerhspf2.ahrianalytics.org/app/seerhspf2
- Calculation date: 2026-07-12
- Calculator/version displayed: not displayed
- Product type: SEER → Dual Stage
- Mode: cooling
- DHR/DOE setting: {"dhr_selection": null, "doe_region": null}
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
| M | 12.45 | `M.SEER` | 12.4540352056775 | 66 |
| M1 | 12.45 | `M1.SEER` | 12.4540352056775 | 66 |

## Input options and normalized test-point groups

- Performance curve groups: k1, k2 (raw curve groups only).
- Activated operating cases: load_at_or_below_low_stage, between_low_and_high_stage, above_high_stage.
- Operating-case source: Reclassified from raw building load against raw low/high stage capacity; k1/k2 remain performance curve groups.

| Group | Raw fields / values |
|---|---|
| `ui_options` | `compressorDesignStage`='Dual Stage', `indoorBlowerType`='Fixed Speed/PSC', `needCoilOnlyAdjust`=False, `isMobileHomeAndSpaceConstrained`=False, `isNonmobileHomeAndNonSpaceConstrained`=True, `lockOutLowCapacityOps`=False, `ODTempWhenLockOut`=None |
| `tested_optional_points` |  |
| `compressor_cut_in_cut_out` | `ODTempWhenLockOut`=None |
| `degradation_coefficients` | `degCoeffCoolFull`=0.18, `degCoeffCoolMin`=0.24 |
| `input_test_points` | `lockOutLowCapacityOps`=False, `coolCapacity95full`=48000, `coolCapacity82full`=52000, `coolCapacity82min`=30000, `coolCapacity67min`=34000, `powerConsumption95full`=4300, `powerConsumption82full`=3900, `powerConsumption82min`=2200, `powerConsumption67min`=2500, `scfm95full`=800, `scfm82full`=800, `scfm82min`=650, `scfm67min`=650 |

## Regime and raw-result projections

- Regime distribution: `{"M": {"load_at_or_below_low_stage": 4, "between_low_and_high_stage": 3, "above_high_stage": 1}, "M1": {"load_at_or_below_low_stage": 4, "between_low_and_high_stage": 3, "above_high_stage": 1}}`

### M

- DHR raw field/value: `None` / `None`.
- Building-load raw fields: 8.
- Resistance/auxiliary raw fields: 0; sum `0`.
- Northern raw case names: `{}`.
- Cutout delta distribution: `{}`.
- Seasonal aggregate columns and sums:

| Normalized name | Raw columns | Sum | Unit |
|---|---|---:|---|
| `raw_ratio_total_cooling` | 8 columns | 17117.2027972028 | `not exposed` |
| `raw_ratio_total_power` | 8 columns | 1374.4302560987992 | `not exposed` |

### M1

- DHR raw field/value: `None` / `None`.
- Building-load raw fields: 8.
- Resistance/auxiliary raw fields: 0; sum `0`.
- Northern raw case names: `{}`.
- Cutout delta distribution: `{}`.
- Seasonal aggregate columns and sums:

| Normalized name | Raw columns | Sum | Unit |
|---|---|---:|---|
| `raw_ratio_total_cooling` | 8 columns | 17117.2027972028 | `not exposed` |
| `raw_ratio_total_power` | 8 columns | 1374.4302560987992 | `not exposed` |

## Raw evidence checksums

| File | SHA-256 |
|---|---|
| `input_template.csv` | `cd493cae7b1ced34eb9198cdcd21034fda92c804fd5393c9141d98cdeb00fc1e` |
| `input.csv` | `c2fddce738ec49aad88644cda594495003909f705bc258d223b24094d131438d` |
| `result_m.csv` | `63b62c877dab7865e7fd9c8a3a7bbe3bca868c43377dd505c32fd3312b21bb26` |
| `result_m1.csv` | `0764bab0e123713abc7617e8b6ffe4371fa866749beb9f03c4175fec896e5e6e` |

## Reproduction procedure

1. Open the official calculator URL in Chrome.
2. Select `SEER → Dual Stage`.
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
