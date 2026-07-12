# Provenance: ahri210240_triple_capacity_northern_hspf2_synthetic_01

- Official source: AHRI Analytics calculation app
- Calculation URL: https://seerhspf2.ahrianalytics.org/app/seerhspf2
- Calculation date: 2026-07-12
- Calculator/version displayed: not displayed
- Product type: HSPF → Northern Heat Pump → Triple Stage Northern Heat Pump
- Mode: heating
- DHR/DOE setting: {"dhr_selection": "Minimum", "doe_region": "Region 4"}

## Screen headline values

| Result | Screen value | Raw CSV field | Raw value |
|---|---:|---|---:|
| M | 10.65 | `M.HSPF` | 10.6480406437411 |
| M1 | 10.05 | `M1.HSPF` | 10.0473265237749 |

## UI options and input row

| Field | Value |
|---|---|
| `compressorDesignStage` | `Triple Stages` |
| `indoorBlowerType` | `Fixed Speed/PSC` |
| `needCoilOnlyAdjust` | `False` |
| `isMobileHomeAndSpaceConstrained` | `False` |
| `isNonmobileHomeAndNonSpaceConstrained` | `True` |
| `lockOutLowCapacityOps` | `False` |
| `ODTempWhenLockOut` | `-20` |
| `H23Tested` | `True` |
| `H21Tested` | `True` |
| `H31Tested` | `True` |
| `compOperationTemp_k1_lower` | `40` |
| `compOperationTemp_k1_upper` | `65` |
| `compOperationTemp_k2_lower` | `20` |
| `compOperationTemp_k2_upper` | `50` |
| `compOperationTemp_k3_lower` | `-20` |
| `compOperationTemp_k3_upper` | `30` |
| `T_off` | `-45` |
| `T_on` | `-45` |
| `isDemandDefrost` | `True` |
| `demandDefrostCredit` | `1.028571429` |
| `degCoeffHeatBoost` | `0.18` |
| `degCoeffHeatFull` | `0.22` |
| `degCoeffHeatMin` | `0.28` |
| `coolCapacity95Full` | `30000` |
| `heatCapacity62min` | `26000` |
| `heatCapacity47full` | `28000` |
| `heatCapacity47min` | `21000` |
| `heatCapacity35boost` | `30000` |
| `heatCapacity35full` | `25500` |
| `heatCapacity35min` | `18500` |
| `heatCapacity17boost` | `28000` |
| `heatCapacity17full` | `22000` |
| `heatCapacity17min` | `14500` |
| `heatCapacity5boost` | `25000` |
| `powerConsumption62min` | `1350` |
| `powerConsumption47full` | `1850` |
| `powerConsumption47min` | `1300` |
| `powerConsumption35boost` | `2400` |
| `powerConsumption35full` | `2050` |
| `powerConsumption35min` | `1550` |
| `powerConsumption17boost` | `3000` |
| `powerConsumption17full` | `2350` |
| `powerConsumption17min` | `1750` |
| `powerConsumption5boost` | `3400` |
| `scfm95full` | `800` |
| `scfm62min` | `800` |
| `scfm47full` | `800` |
| `scfm47min` | `800` |
| `scfm35boost` | `800` |
| `scfm35full` | `800` |
| `scfm35min` | `800` |
| `scfm17boost` | `800` |
| `scfm17full` | `800` |
| `scfm17min` | `800` |
| `scfm5boost` | `800` |

## Activated operating cases

- case1, case2, case3, case8

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
4. Confirm the UI options and Test 1 input row.
5. Run Calculate/Update.
6. Download Full Results (M) and Full Results (M1) as `result_m.csv` and `result_m1.csv`.

## Known limitations

- Calculator/version was not displayed.
- Raw result CSV does not expose explicit bin temperatures or bin hours; bin keys are preserved without an inferred temperature mapping.
- This fixture is official-calculator evidence for future engine comparison, not a certification claim.
