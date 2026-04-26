# EN 14825 SCOP Notes

Source file: `EN14825-병합됨.pdf`

This note summarizes the SCOP-specific pages used for implementation review.
It is not a full transcription of the standard.

## Pages Checked

- PDF rendered page 3: Clause 5.2 air-to-air heating part-load condition tables for average and warmer climates.
- PDF rendered page 4: Clause 5.2 air-to-air heating part-load condition table for colder climate.
- PDF rendered page 9: Clause 7.1 reference SCOP and Clause 7.2 reference annual heating demand.
- PDF rendered page 10: Clause 7.3 reference SCOPon and SCOPnet.
- PDF rendered page 11: Table 37 heating bin hours for warmer, average, colder seasons.
- PDF rendered page 12: heating load line, COPPL/capacity interpolation, TOL behavior, Clause 7.4.1 and 7.4.2.1.
- PDF rendered page 13: Clause 7.4.2.2 variable-capacity closest-step logic and water/brine formula branches.
- PDF rendered page 16: Annex D Table D.2 and Table D.4 operational hours for reference SCOP.

## Current Scope

Current code target:

- `core/calculator_en14825.py`
- `data/region_configs/en14825_scop.json`

Current supported path:

- EN 14825:2012 SCOP for air-to-air variable-capacity reversible units.
- User provides already resolved part-load declared points:
  - `A`, `B`, `C`, `D`, `TOL`, `Tbiv`
  - each as capacity and power.
- User provides:
  - `p_design_h`
  - `p_to`, `p_sb`, `p_ck`, `p_off`
  - climate: `average`, `warmer`, or `colder`.

## Implemented Formula Summary

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

## Still Needed For Full Standard Match

The current calculator assumes A/B/C/D/TOL/Tbiv are already resolved EN 14825 declared part-load points.
For a complete standard-identical implementation, add raw capacity-control-step support for Clause 7.4.2.2:

- User input schema for capacity-control steps around each required load.
- For each part-load condition, select the closest step or increment that reaches the required heat load.
- If the selected step cannot reach required heat load within +/-10%, use the declared capacity and COPPL at the defined part-load temperatures for steps on either side.
- Interpolate capacity and COPPL at the required heating load between those two step results.
- If the smallest control step is higher than required heating load, apply the fixed-capacity Equation 11 cycling degradation formula.

Also needed:

- Add explicit optional `-15 C` calculation point for colder climate when `TOL < -20 C`.
- Decide whether to expose `SCOPnet` Equation 10 as an optional output.
- Add verified reference example values from the standard or a known certification worksheet.
- Add unit tests for:
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
- PDF 요약은 `docs/en14825_scop_notes.md`에 있다.

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
