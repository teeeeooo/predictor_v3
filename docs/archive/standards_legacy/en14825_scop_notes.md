# EN 14825 SEER/SCOP Notes

Source file: `EN14825-병합됨.pdf`

This note summarizes implementation-relevant SEER/SCOP pages used for review.
It is not a full transcription of the standard.

## Pages Checked

- PDF rendered page 1: Clause 4 cooling part-load conditions and Table 2 for air-to-air units.
- PDF rendered page 2: Clause 5 heating part-load general conditions and Tdesignh definitions.
- PDF rendered page 3: Clause 5.2 air-to-air heating part-load condition tables for average and warmer climates.
- PDF rendered page 4: Clause 5.2 air-to-air heating part-load condition table for colder climate.
- PDF rendered page 5: Clause 6.1 reference SEER general formula.
- PDF rendered page 6: Clause 6.1 formula, Clause 6.2 Qc, Clause 6.3 SEERon.
- PDF rendered page 7: Table 36 cooling bin hours, cooling demand line, Clause 6.4.1 and 6.4.2.1.
- PDF rendered page 8: Clause 6.4.2.2 variable-capacity cooling logic and water/brine formula branches.
- PDF rendered page 9: Clause 7.1 reference SCOP and Clause 7.2 reference annual heating demand.
- PDF rendered page 10: Clause 7.3 reference SCOPon and SCOPnet.
- PDF rendered page 11: Table 37 heating bin hours for warmer, average, colder seasons.
- PDF rendered page 12: heating load line, COPPL/capacity interpolation, TOL behavior, Clause 7.4.1 and 7.4.2.1.
- PDF rendered page 13: Clause 7.4.2.2 variable-capacity closest-step logic and water/brine formula branches.
- PDF rendered page 14: Annex D assumptions for annual demand and mode hours.
- PDF rendered page 15: Annex D Table D.1 cooling operation hours.
- PDF rendered page 16: Annex D Table D.2 and Table D.4 operational hours for reference SCOP.

## Current Scope

Current code target:

- `core/calculator_en14825.py`
- `data/region_configs/en14825_scop.json`

Current supported path:

- Existing SEER path in `calculate_seer()`.
- EN 14825:2012 SCOP for air-to-air variable-capacity reversible units.
- User provides already resolved part-load declared points:
  - `A`, `B`, `C`, `D`, `TOL`, `Tbiv`
  - each as capacity and power.
- User provides:
  - `p_design_h`
  - `p_to`, `p_sb`, `p_ck`, `p_off`
  - climate: `average`, `warmer`, or `colder`.

## SEER Reference Notes

Cooling part-load conditions for air-to-air units:

| Point | Outdoor dry bulb C | Nominal part-load ratio |
| --- | ---: | ---: |
| A | 35 | 100% |
| B | 30 | 74% |
| C | 25 | 47% |
| D | 20 | 21% |

Cooling bin hours from Table 36:

| Tj C | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30 | 31 | 32 | 33 | 34 | 35 | 36 | 37 | 38 | 39 | 40 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| hj h | 205 | 227 | 225 | 225 | 216 | 215 | 218 | 197 | 178 | 158 | 137 | 109 | 88 | 63 | 39 | 31 | 24 | 17 | 13 | 9 | 4 | 3 | 1 | 0 |

Reference annual cooling demand:

```text
Qc = Pdesignc * Hce
```

For air-to-air units up to 12 kW, `Hce = 350 h`.

Cooling demand line:

```text
Pc(Tj) = Pdesignc * (Tj - 16) / (35 - 16)
```

Reference SEER structure:

```text
SEER = Qc / (Qc / SEERon + Hto*Pto + Hsb*Psb + Hck*Pck + Hoff*Poff)
```

Reference SEERon structure:

```text
SEERon = sum(hj * Pc(Tj)) / sum(hj * (Pc(Tj) / EERPL(Tj)))
```

EER values at bins:

- Interpolate `EERPL` from A/B/C/D part-load conditions.
- Above condition A, use condition A EER.
- Below condition D, use condition D EER.

Clause 6.4 cooling part-load handling:

- At full-load condition A, declared capacity is considered equal to cooling load `Pdesignc`.
- For B/C/D, if declared capacity matches or is lower than required cooling load, use corresponding `EERDC`.
- If declared capacity is higher than required load, cycling degradation applies for fixed-capacity behavior.
- For air-to-air and water-to-air fixed-capacity units:

```text
EERPL = EERDC * (1 - Cd * (1 - CR))
```

- `CR = Pc / DC`.
- Default `Cd = 0.25` if not determined by test.

Clause 6.4.2.2 cooling variable-capacity handling:

- Select the closest capacity-control step or increment that reaches required cooling load.
- If that step does not reach the required load within +/-10%, use the steps on either side of the required load.
- Interpolate part-load capacity and `EERPL` at the required cooling load between those two step results.
- If the smallest control step is higher than required cooling load, use the fixed-capacity degradation equation.

Cooling operational hours from Annex D Table D.1:

| Mode | Cooling only h | Reversible h |
| --- | ---: | ---: |
| Total hours/year | 8760 | 8760 |
| Off mode Hoff | 5088 | 0 |
| Season difference | 3672 | 3672 |
| Thermostat off Hto | 221 | 221 |
| Standby Hsb | 2142 | 2142 |
| Active hours without setback correction | 1309 | 1309 |
| Setback correction | 355 | 355 |
| Active hours corrected | 954 | 954 |
| Equivalent active hours Hce | 350 | 350 |

Crankcase heater hours for reference SEER from Annex D Table D.3:

| Unit type | Hck h |
| --- | ---: |
| Cooling only | 7760 |
| Reversible | 2672 |

## SCOP Reference Notes

Reference annual heating demand:

```text
Qh = Pdesignh * Hhe
```

Heating demand at bin:

```text
Ph(Tj) = Pdesignh * (Tj - 16) / (Tdesignh - 16)
```

Reference SCOP:

```text
SCOP = Qh / (Qh / SCOPon + Hto*Pto + Hsb*Psb + Hck*Pck + Hoff*Poff)
```

Reference SCOPon implemented from Equation 9 structure:

```text
SCOPon = sum(hj * Ph(Tj)) / sum(hj * ((Ph(Tj) - elbu(Tj)) / COPPL(Tj) + elbu(Tj)))
```

Electric backup behavior:

```text
elbu(Tj) = max(0, Ph(Tj) - Pdh(Tj))
```

Below TOL:

```text
Pdh(Tj) = 0
COPPL(Tj) = 0
elbu(Tj) = Ph(Tj)
```

`Pdh(Tj)` and `COPPL(Tj)` are interpolated from the user-entered A/B/C/D/TOL/Tbiv points.

Heating climate definitions:

| Climate | Tdesignh C | Tbiv maximum C |
| --- | ---: | ---: |
| average | -10 | 2 |
| warmer | 2 | 7 |
| colder | -22 | -7 |

Air-to-air heating part-load condition temperatures:

| Point | Average C | Warmer C | Colder C |
| --- | ---: | ---: | ---: |
| A | -7 | not applicable | -7 |
| B | 2 | 2 | 2 |
| C | 7 | 7 | 7 |
| D | 12 | 12 | 12 |
| E | TOL | TOL | TOL |
| F | Tbiv | Tbiv | Tbiv |

Heating bin hours from Table 37 are stored in `data/region_configs/en14825_scop.json`.

SCOP operational hours from Annex D Table D.2:

| Climate | Reversible Hto | Reversible Hsb | Reversible Hoff | Reversible Hhe |
| --- | ---: | ---: | ---: | ---: |
| average | 179 | 0 | 0 | 1400 |
| warmer | 755 | 0 | 0 | 1400 |
| colder | 131 | 0 | 0 | 2100 |

Crankcase heater hours for reference SCOP from Annex D Table D.4:

| Climate | Reversible Hck |
| --- | ---: |
| average | 179 |
| warmer | 755 |
| colder | 131 |

Heating-only hours are also stored in JSON for future use.

## Still Needed For Full Standard Match

The current calculator assumes A/B/C/D/TOL/Tbiv are already resolved EN 14825 declared part-load points.
For a complete standard-identical implementation, add raw capacity-control-step support for Clause 6.4.2.2 and Clause 7.4.2.2:

- User input schema for capacity-control steps around each required load.
- For each part-load condition, select the closest step or increment that reaches the required load.
- If the selected step cannot reach required load within +/-10%, use declared capacity and EERPL/COPPL at the defined part-load temperatures for steps on either side.
- Interpolate capacity and EERPL/COPPL at the required load between those two step results.
- If the smallest control step is higher than required load, apply the fixed-capacity degradation formula.

Also needed:

- Add explicit optional `-15 C` calculation point for colder climate when `TOL < -20 C`.
- Decide whether to expose `SCOPnet` Equation 10 as an optional output.
- Decide whether to expose a corrected SEER implementation that follows the PDF `EERPL` interpolation structure exactly, because current `calculate_seer()` was pre-existing and not rewritten in this task.
- Add verified reference example values from the standard or a known certification worksheet.
- Add unit tests for:
  - SEER Table 36 bin behavior
  - average, warmer, colder climates
  - TOL below bin temperature
  - heat pump capacity shortfall with electric backup
  - colder climate `TOL < -20 C` fail-fast until the `-15 C` point is supported
  - invalid Tbiv/TOL limits

## Prompt For Next Codex

```text
AGENTS.md를 먼저 읽고 준수하라.

목표:
EN14825 SCOP 계산기를 규격 PDF(`EN14825-병합됨.pdf`) 기준으로 완전 구현에 가깝게 보강한다.

범위:
- `core/calculator_en14825.py`
- `data/region_configs/en14825_scop.json`
- 필요 시 SCOP 전용 테스트 파일 1개
- predictor/UI/ML/AHRI/HSPF2 파일은 수정 금지

현재 상태:
- `calculate_scop()`은 EN14825 식 (7), (8), (9), Table 37, Annex D Table D.2/D.4 기반으로 동작한다.
- 현재 API는 A/B/C/D/TOL/Tbiv capacity/power를 이미 resolved declared part-load point로 간주한다.
- PDF 요약은 `docs/en14825_scop_notes.md`에 있으며 SEER 참고 내용도 포함되어 있다.

해야 할 일:
1. PDF Clause 7.4.2.2 variable-capacity closest-step / +/-10% 로직을 구현하기 위해 필요한 입력 스키마를 설계한다.
2. 기존 단순 A/B/C/D/TOL/Tbiv 입력 경로는 하위 호환으로 유지한다.
3. raw capacity-control-step 입력이 있을 때는 Clause 7.4.2.2 기준으로 COPPL과 capacity를 산정한다.
4. colder climate에서 TOL < -20 C일 때 필요한 -15 C 추가 계산점을 지원한다.
5. 규격 근거가 불명확한 부분은 추정 구현하지 말고 TODO/ValueError 또는 result note로 남긴다.
6. 계산 로직 변경 후 smoke assert를 추가/실행한다.

검증:
- `python3 -B -m py_compile core/calculator_en14825.py`
- 기존 SEER smoke 유지
- SCOP smoke assert 실행
- 테스트 기대값은 임의 변경 금지

완료 보고는 AGENTS.md 형식을 따른다.
```
