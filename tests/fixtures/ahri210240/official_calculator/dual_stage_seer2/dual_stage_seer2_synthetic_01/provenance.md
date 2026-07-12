# Provenance: ahri210240_dual_stage_seer2_synthetic_01

- Official source: AHRI Analytics calculation app
- Calculation URL: https://seerhspf2.ahrianalytics.org/app/seerhspf2
- Calculation date: 2026-07-12
- Calculator/version displayed: not displayed
- Product type: SEER → Dual Stage
- Mode: cooling
- DHR/DOE setting: {"dhr_selection": null, "doe_region": null}

## Screen headline values

| Result | Screen value | Raw CSV field | Raw value |
|---|---:|---|---:|
| M | 12.45 | `M.SEER` | 12.4540352056775 |
| M1 | 12.45 | `M1.SEER` | 12.4540352056775 |

## UI options and input row

| Field | Value |
|---|---|
| `compressorDesignStage` | `Dual Stage` |
| `indoorBlowerType` | `Fixed Speed/PSC` |
| `needCoilOnlyAdjust` | `False` |
| `isMobileHomeAndSpaceConstrained` | `False` |
| `isNonmobileHomeAndNonSpaceConstrained` | `True` |
| `lockOutLowCapacityOps` | `False` |
| `ODTempWhenLockOut` | `blank` |
| `degCoeffCoolFull` | `0.18` |
| `degCoeffCoolMin` | `0.24` |
| `coolCapacity95full` | `48000` |
| `coolCapacity82full` | `52000` |
| `coolCapacity82min` | `30000` |
| `coolCapacity67min` | `34000` |
| `powerConsumption95full` | `4300` |
| `powerConsumption82full` | `3900` |
| `powerConsumption82min` | `2200` |
| `powerConsumption67min` | `2500` |
| `scfm95full` | `800` |
| `scfm82full` | `800` |
| `scfm82min` | `650` |
| `scfm67min` | `650` |

## Activated operating cases

- k1, k2

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
4. Confirm the UI options and Test 1 input row.
5. Run Calculate/Update.
6. Download Full Results (M) and Full Results (M1) as `result_m.csv` and `result_m1.csv`.

## Known limitations

- Calculator/version was not displayed.
- Raw result CSV does not expose explicit bin temperatures or bin hours; bin keys are preserved without an inferred temperature mapping.
- This fixture is official-calculator evidence for future engine comparison, not a certification claim.
