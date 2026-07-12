# Provenance: ahri210240_dual_stage_hspf2_synthetic_01

- Official source: AHRI Analytics calculation app
- Calculation URL: https://seerhspf2.ahrianalytics.org/app/seerhspf2
- Calculation date: 2026-07-12
- Calculator/version displayed: not displayed
- Product type: HSPF → Dual Stage
- Mode: heating
- DHR/DOE setting: {"dhr_selection": "Minimum", "doe_region": "Region 4"}

## Screen headline values

| Result | Screen value | Raw CSV field | Raw value |
|---|---:|---|---:|
| M | 9.47 | `M.HSPF` | 9.46530640542776 |
| M1 | 8.57 | `M1.HSPF` | 8.5695257081792 |

## UI options and input row

| Field | Value |
|---|---|
| `compressorDesignStage` | `Dual Stage` |
| `indoorBlowerType` | `Fixed Speed/PSC` |
| `needCoilOnlyAdjust` | `False` |
| `isMobileHomeAndSpaceConstrained` | `False` |
| `isNonmobileHomeAndNonSpaceConstrained` | `True` |
| `lockOutLowCapacityOps` | `False` |
| `ODTempWhenLockOut` | `40` |
| `H4Tested` | `False` |
| `H21Tested` | `True` |
| `T_off` | `blank` |
| `T_on` | `blank` |
| `isDemandDefrost` | `True` |
| `demandDefrostCredit` | `1.03` |
| `degCoeffHeatFull` | `0.22` |
| `degCoeffHeatMin` | `0.18` |
| `coolCapacity95Full` | `30000` |
| `heatCapacity62min` | `22000` |
| `heatCapacity47full` | `25000` |
| `heatCapacity47min` | `18000` |
| `heatCapacity35full` | `21500` |
| `heatCapacity35min` | `14500` |
| `heatCapacity17full` | `19500` |
| `heatCapacity17min` | `10500` |
| `heatCapacity5full` | `17000` |
| `powerConsumption62min` | `1450` |
| `powerConsumption47full` | `1800` |
| `powerConsumption47min` | `1350` |
| `powerConsumption35full` | `1900` |
| `powerConsumption35min` | `1450` |
| `powerConsumption17full` | `2100` |
| `powerConsumption17min` | `1600` |
| `powerConsumption5full` | `2300` |
| `scfm95full` | `800` |
| `scfm62min` | `800` |
| `scfm47full` | `800` |
| `scfm47min` | `800` |
| `scfm35full` | `800` |
| `scfm35min` | `800` |
| `scfm17full` | `800` |
| `scfm17min` | `800` |
| `scfm5full` | `800` |

## Activated operating cases

- k1, k2

## Raw evidence checksums

| File | SHA-256 |
|---|---|
| `input_template.csv` | `0a7d124814a2cb94e1fcda11d314dc6884d5196012e2365bc2d217db31259c81` |
| `input.csv` | `824418810d57f1535e5ce853ca9e1a5081034abe3814c8806303c9888e5657ed` |
| `result_m.csv` | `ae4ad2744f7ccffa74e1b6a05c51bfd767838cf8682c889200b7552e474882ad` |
| `result_m1.csv` | `9d45be22698c9982c5728c405dc238073a2849d32aae55e534f317f3149ce424` |

## Reproduction procedure

1. Open the official calculator URL in Chrome.
2. Select `HSPF → Dual Stage`.
3. Upload `input.csv` and choose Replace Input Table.
4. Confirm the UI options and Test 1 input row.
5. Run Calculate/Update.
6. Download Full Results (M) and Full Results (M1) as `result_m.csv` and `result_m1.csv`.

## Known limitations

- Calculator/version was not displayed.
- Raw result CSV does not expose explicit bin temperatures or bin hours; bin keys are preserved without an inferred temperature mapping.
- This fixture is official-calculator evidence for future engine comparison, not a certification claim.
