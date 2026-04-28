# EN14825 Dev Notes

## 1. Purpose

이 문서는 EN14825 계산 경로를 수정하거나 검증하는 개발자와 AI Agent를 위한 구현 지침이다. 기준 동작은 `core/calculator_en14825.py`, `data/region_configs/en14825_scop.json`, `tests/test_en14825_golden.py`와 반드시 일치해야 한다. PDF는 Clause/Table/Equation 번호 확인용 Secondary 자료로만 사용한다.

핵심 목적은 계산 순서, 입력 단위, 보간 규칙, Cd 적용 조건, golden 검증을 재현 가능하게 만드는 것이다. EN14825는 bin hour와 운전 모드 시간이 최종 지표에 직접 들어가므로, 작은 schema 오해가 SEER/SCOP 전체를 바꿀 수 있다. 근거: EN14825:2012 Table 36, Table 37, Annex D Table D.1~D.4.

## 2. Top Implementation Pitfalls

| Pitfall | Symptom | Cause | Prevention | Reference |
| --- | --- | --- | --- | --- |
| W 단위 보조전력을 kW 입력에 그대로 전달 | SEER/SCOP가 비정상적으로 낮아진다. | `Pto`, `Psb`, `Pck`, `Poff` API 단위는 kW다. | 입력 전 W/1000 변환을 명시한다. | EN14825:2012 Annex D |
| SCOP declared point를 raw capacity-control step으로 오해 | Cd 적용 조건과 COPPL이 규격 step selection과 다르게 보인다. | 현재 schema는 raw step list를 받지 않는다. | A/B/C/D/TOL/Tbiv를 이미 resolved declared point로 문서화한다. | EN14825:2012 Clause 7.4.2.2 |
| TOL 아래 bin에서 히트펌프 용량을 보간 | 저온 SCOP가 과대평가된다. | TOL cut-off 처리를 누락한다. | `Tj < TOL`이면 `Pdh=0`, `COPPL=0`, `elbu=Ph`를 유지한다. | EN14825:2012 Equation 9 |
| Table 37 bin hour 총합 누락 | 기후별 SCOPon이 전체적으로 틀어진다. | JSON 입력 오류 또는 길이 불일치 | temperature/hour 길이와 총합을 fail-fast 검증한다. | EN14825:2012 Table 37 |
| `Qh`와 bin numerator를 같은 값으로 가정 | 최종 SCOP와 SCOPon 관계가 깨진다. | Clause 7.2의 annual demand와 Equation 9의 bin 합산을 혼동한다. | `Qh = Pdesignh * Hhe`, `SCOPon`은 별도 bin 합산으로 유지한다. | EN14825:2012 Clause 7.2, Equation 9 |
| colder climate의 특수 저온점을 암묵 구현 | 검증되지 않은 결과가 나온다. | -15 °C 추가 운전점 schema가 없다. | 명시 입력 schema 추가 전에는 미지원으로 둔다. | EN14825:2012 Clause 7.4 |

## 3. Correct Calculation Order

### SEER

1. `_validate_test_points()`로 A/B/C/D capacity와 power를 검증한다.
2. `Qc = Pdesignc * Hce`를 계산한다. `Hce = 350 h`는 가역식 기준이다. 근거: EN14825:2012 Clause 6.2, Annex D Table D.1.
3. `_build_cooling_eerpl_points()`에서 A/B/C/D 부하와 EERPL point를 만든다.
4. A는 degradation을 적용하지 않는다. B/C/D는 `capacity > load`이면 `_part_load_performance()`의 Cd degradation 경로를 탄다. 근거: EN14825:2012 Clause 6.4.2.1.
5. `_calculate_seer_on()`에서 Table 36 bin을 순회하며 `Pc(Tj)`와 보간된 `EERPL(Tj)`를 사용한다.
6. `calculate_seer()`에서 보조전력 에너지를 더해 최종 SEER를 반환한다.

### SCOP

1. `_normalize_climate()`로 climate alias를 정규화한다.
2. `_get_scop_climate_data()`로 JSON의 Table 37 data를 검증한다.
3. `_parse_scop_point()`와 `_validate_scop_points()`로 A/B/C/D/TOL/Tbiv를 구성한다.
4. `_heating_part_load()`로 각 declared point의 `Ph`를 계산한다. 근거: EN14825:2012 Clause 7.2.
5. `_scop_pl_at_declared_point()`로 `COPDC`, `COPPL`, `CR`, degradation factor를 계산한다.
6. `_build_scop_points()`에서 capacity curve와 COPPL curve를 만든다.
7. `_calculate_scop_on()`에서 Table 37 bin을 순회한다.
8. `Tj < TOL`이면 electric backup only로 처리한다. 근거: EN14825:2012 Equation 9.
9. `Tj >= TOL`이면 capacity와 COPPL을 보간하고, 부족분을 `elbu`로 둔다.
10. `calculate_scop()`에서 `Qh`, active energy, standby energy, total energy, SCOP를 계산한다.

## 4. Data Model Notes

| Data | Location | Meaning | Validation |
| --- | --- | --- | --- |
| cooling bin temps/hours | `core/calculator_en14825.py` constants | Table 36 냉방 bin | 현재 상수로 고정 |
| cooling test points | `calculate_seer(test_points=...)` | A/B/C/D capacity/power | key 누락, 0 이하 값 금지 |
| SCOP climate data | `data/region_configs/en14825_scop.json` | Table 37, Tdesignh, Tbiv/TOL limits | length, non-negative hour, total hour 검증 |
| SCOP operational hours | `data/region_configs/en14825_scop.json` | Annex D Table D.2/D.4 | appliance_type/climate key 검증 |
| SCOP test points | `calculate_scop(test_points=...)` | A/B/C/D/TOL/Tbiv declared point | dict 또는 tuple 허용, capacity/power 0 이하 금지 |
| SCOP source metadata | `calculate_scop()` return | JSON source block | 문서와 결과 추적용 |

SCOP dict point는 `{"capacity": kW, "power": kW, "temp_c": optional}` 형식이다. tuple point는 `(capacity, power)`만 받으므로 온도는 schema 또는 별도 `tbiv_temp_c`, `tol_temp_c`에서 결정된다.

## 5. Interpolation / Extrapolation Rules

| Path | Rule | Boundary behavior | Reference |
| --- | --- | --- | --- |
| SEER EERPL | A/B/C/D 온도 point 사이 선형 보간 | 최저/최고 밖은 끝점 clamp | EN14825:2012 Clause 6.4 |
| SCOP capacity | A/B/C/D/TOL/Tbiv capacity curve 선형 보간 | 최저/최고 밖은 끝점 clamp | EN14825:2012 Clause 7.4 |
| SCOP COPPL | A/B/C/D/TOL/Tbiv 중 온도 중복 제거 후 선형 보간 | 상단 밖은 마지막 두 점으로 외삽 가능 | EN14825:2012 Clause 7.4 |
| 동일 온도 SCOP point | priority 선택 | `TOL > Tbiv > A > B > C > D` | Project rule |

외삽은 성능값을 과대평가할 수 있으므로 변경 시 golden 테스트뿐 아니라 bin_details의 `cop_source`를 확인해야 한다. 특히 warm bin에서 COPPL 외삽이 발생하면 final SCOP 영향이 클 수 있다.

## 6. Degradation / Correction Factor Rules

| Path | Current rule | Why | Reference |
| --- | --- | --- | --- |
| SEER A | Cd degradation 미적용 | A는 full-load condition으로 취급한다. | EN14825:2012 Clause 6.4 |
| SEER B/C/D | `capacity > load`일 때 Cd degradation 적용 | fixed-capacity style cycling correction | EN14825:2012 Clause 6.4.2.1 |
| SCOP declared point | `capacity > load and load_gap_ratio > 0.10`일 때 Cd degradation 적용 | declared-point schema에서 ±10% closest step 개념을 반영 | EN14825:2012 Clause 7.4.2.2 |
| SCOP declared point within +10% | Cd degradation 미적용 | 입력 point를 acceptable closest step으로 본다. | EN14825:2012 Clause 7.4.2.2 |
| SCOP capacity shortfall | Cd degradation 미적용 | 용량 부족 또는 full-load operation으로 본다. | EN14825:2012 Clause 7.4 |

현재 SCOP API는 raw capacity-control step list를 받지 않는다. 따라서 Clause 7.4.2.2의 완전한 closest-step selection은 구현할 수 없고, 현재 조건은 declared point만으로 가능한 보수적 해석이다. raw step schema가 추가되면 `_scop_pl_at_declared_point()`의 조건은 실제 step 선택 로직으로 대체해야 한다.

## 7. Debugging Checklist

| Check | What to inspect | Expected |
| --- | --- | --- |
| 단위 | `p_to`, `p_sb`, `p_ck`, `p_off` | kW 입력 |
| climate | normalized climate key | `average`, `warmer`, `colder` 중 하나 |
| Table 37 | temps/hours length and total | JSON expected total과 일치 |
| TOL/Tbiv | point temperature limits | `TOL <= Tbiv`, 기후별 maximum 이하 |
| point COP | capacity/power | 모두 양수, COPDC 양수 |
| Cd path | `degradation_factor` | SCOP +10% 이내는 1.0이어야 함 |
| below TOL bins | `bin_details.operating_case` | `below_tol_electric_backup_only` |
| backup heat | `elbu` | capacity shortfall에서만 양수 |
| energy denominator | `denominator_contribution` | 0보다 크고 bin hour와 함께 증가 |
| final rounding | return values | 최종 출력은 3자리 또는 2자리 반올림 |

## 8. Test Strategy

| Change type | Required checks |
| --- | --- |
| 문서만 변경 | markdown 구조와 기준 문서 일치 여부 확인 |
| 주석만 변경 | `python3 -B -m py_compile core/calculator_en14825.py` |
| SEER 계산 변경 | `tests/test_en14825_golden.py::test_en14825_golden_seer` 및 Table 36 edge check |
| SCOP 계산 변경 | average/warmer/colder golden 전체 실행 |
| JSON 기후 데이터 변경 | bin hour total 검증과 SCOP golden 전체 실행 |
| Cd 조건 변경 | declared capacity/load gap 경계 케이스 추가 |
| TOL/Tbiv validation 변경 | invalid limit fail-fast 케이스 추가 |

기본 검증 명령:

```bash
python3 -B -m py_compile core/calculator_en14825.py
python3 -B -m pytest tests/test_en14825_golden.py -v --runxfail
```

## 9. Golden Case Strategy

현재 golden 기준은 `tests/test_en14825_golden.py`에 있다.

| Case | Expected | Purpose |
| --- | ---: | --- |
| SEER | 9.104 | 냉방 Table 36, EERPL 보간, Annex D 보조전력 합산 확인 |
| SCOP average | 5.108 | 평균 기후 Table 37, TOL/Tbiv, backup heat 경로 확인 |
| SCOP warmer | 6.008 | warmer 기후의 높은 운전 시간과 Tbiv 제한 확인 |
| SCOP colder | 4.190 | colder 기후의 저온 bin과 전기 백업 영향 확인 |

향후 golden을 강화할 때는 인증 리포트 또는 공식 worksheet처럼 입력과 기대값이 완전한 자료를 사용해야 한다. 단순히 현재 출력값을 expected로 복사하면 계산 오류를 고정하는 결과가 된다.

## 10. Future Refactor Notes

| Topic | Keep current behavior until | Refactor direction | Reference |
| --- | --- | --- | --- |
| SCOP raw step selection | raw capacity-control step schema가 정의될 때까지 | Clause 7.4.2.2 closest-step selection으로 대체 | EN14825:2012 Clause 7.4.2.2 |
| SEER variable capacity exact handling | cooling raw step schema가 정의될 때까지 | Clause 6.4.2.2 closest-step/interpolation 구조 반영 | EN14825:2012 Clause 6.4.2.2 |
| SCOPnet | 출력 요구가 생길 때까지 | Equation 10 별도 optional output 추가 | EN14825:2012 Equation 10 |
| colder special point | 입력 schema가 확장될 때까지 | -15 °C point를 명시 입력으로 받기 | EN14825:2012 Clause 7.4 |
| common part-load helper | 계산 결과가 바뀌지 않는 테스트 보호 후 | SEER/SCOP 공통 Cd 경로를 더 명확히 분리 | EN14825:2012 Clause 6.4.2.1, Clause 7.4.2.1 |

리팩토링은 계산 결과가 바뀌지 않는다는 golden 보호가 먼저 있어야 한다. 이 프로젝트의 Lite 규칙상 명시 요청 없는 구조 변경은 금지다.

## 11. PDF 확인 페이지 및 원문 체크 포인트

통합 전 SCOP 노트에 정리되어 있던 PDF 확인 범위는 아래와 같다. PDF는 전체 전사가 아니라 구현 검토에 필요한 Clause/Table/Equation 확인용 Secondary 근거다.

| 확인 범위 | 핵심 내용 |
| --- | --- |
| rendered page 1 | Clause 4 냉방 부분부하 조건과 공기 대 공기 장비 Table 2 |
| rendered page 2~4 | Clause 5 난방 부분부하 일반 조건, Tdesignh, average/warmer/colder 기후별 공기 대 공기 조건 |
| rendered page 5~8 | Clause 6.1~6.4, Table 36, 냉방 부하선, 냉방 fixed/variable capacity 부분부하 처리 |
| rendered page 9~13 | Clause 7.1~7.4, Equation 9, Equation 10, Table 37, 난방 보간, TOL 동작, fixed/variable capacity 부분부하 처리 |
| rendered page 14~16 | Annex D 연간 수요 가정, Table D.1, Table D.2, Table D.3, Table D.4 운전 모드 시간 |

## 12. 규격 표 및 수식 재현 메모

냉방 공기 대 공기 부분부하 조건은 Table 2 기준 A/B/C/D 운전점을 사용한다.

| 운전점 | 외기 건구온도 °C | 명목 부분부하율 |
| --- | ---: | ---: |
| A | 35 | 100% |
| B | 30 | 74% |
| C | 25 | 47% |
| D | 20 | 21% |

Table 36 냉방 bin hour는 다음 값을 기준으로 한다.

| Tj °C | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30 | 31 | 32 | 33 | 34 | 35 | 36 | 37 | 38 | 39 | 40 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| hj h | 205 | 227 | 225 | 225 | 216 | 215 | 218 | 197 | 178 | 158 | 137 | 109 | 88 | 63 | 39 | 31 | 24 | 17 | 13 | 9 | 4 | 3 | 1 | 0 |

냉방 기준 연간 수요와 부하선은 아래 구조다. 근거: EN14825:2012 Clause 6.2, Clause 6.4.

```text
Qc = Pdesignc * Hce
Pc(Tj) = Pdesignc * (Tj - 16) / (35 - 16)
```

SEER와 SEERon의 기준 구조는 아래와 같다. 근거: EN14825:2012 Clause 6.1, Clause 6.3.

```text
SEER = Qc / (Qc / SEERon + Hto*Pto + Hsb*Psb + Hck*Pck + Hoff*Poff)
SEERon = sum(hj * Pc(Tj)) / sum(hj * (Pc(Tj) / EERPL(Tj)))
```

난방 기준 연간 수요와 부하선은 아래 구조다. 근거: EN14825:2012 Clause 7.2.

```text
Qh = Pdesignh * Hhe
Ph(Tj) = Pdesignh * (Tj - 16) / (Tdesignh - 16)
```

SCOP와 SCOPon의 기준 구조는 아래와 같다. 근거: EN14825:2012 Clause 7.1, Clause 7.3, Equation 9.

```text
SCOP = Qh / (Qh / SCOPon + Hto*Pto + Hsb*Psb + Hck*Pck + Hoff*Poff)
SCOPon = sum(hj * Ph(Tj)) / sum(hj * ((Ph(Tj) - elbu(Tj)) / COPPL(Tj) + elbu(Tj)))
elbu(Tj) = max(0, Ph(Tj) - Pdh(Tj))
```

TOL 아래 bin은 히트펌프 용량과 COPPL을 0으로 두고, 전체 난방 부하를 보조 전기 히터 부하로 처리한다.

```text
Pdh(Tj) = 0
COPPL(Tj) = 0
elbu(Tj) = Ph(Tj)
```

난방 기후 정의와 Annex D 운전 시간은 아래 값을 기준으로 검증한다.

| 기후 | Tdesignh °C | Tbiv 최대 °C | 가역식 Hto | 가역식 Hsb | 가역식 Hoff | Hhe | 가역식 Hck |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average | -10 | 2 | 179 | 0 | 0 | 1400 | 179 |
| warmer | 2 | 7 | 755 | 0 | 0 | 1400 | 755 |
| colder | -22 | -7 | 131 | 0 | 0 | 2100 | 131 |

Full standard match를 위해서는 Clause 6.4.2.2와 Clause 7.4.2.2의 raw capacity-control step 선택 로직, colder climate에서 `TOL < -20 °C`일 때의 -15 °C 추가점, Equation 10의 SCOPnet 반환 여부, 인증 리포트 또는 공식 worksheet 기반 golden case가 추가로 필요하다.

## 13. Prompt Snippets for Agent

### 문서 업데이트

```text
AGENTS.md의 Lite 규칙과 docs/DOCS_GUIDELINES.md를 먼저 읽어라. EN14825 문서는 docs/en14825/en14825_notes.md, docs/en14825/en14825_dev_notes.md, docs/en14825/en14825_design_notes.md, docs/en14825/en14825_glossary.md와 core/calculator_en14825.py를 Primary 기준으로 삼고, PDF는 Clause/Table/Equation 확인용으로만 사용하라. 문서 작업이면 docs/en14825 하위 EN14825 Markdown만 수정하라.
```

### SCOP 계산 변경

```text
AGENTS.md를 먼저 읽고, 수정 범위를 core/calculator_en14825.py와 필요한 테스트 파일로 제한하라. 현재 API는 A/B/C/D/TOL/Tbiv를 resolved declared point로 취급한다. raw capacity-control step list가 없으므로 Clause 7.4.2.2 closest-step 완전 구현을 추측하지 말라. 변경 후 py_compile과 tests/test_en14825_golden.py -v --runxfail을 실행하라.
```

### JSON 데이터 변경

```text
AGENTS.md와 docs/en14825/en14825_notes.md를 먼저 읽어라. data/region_configs/en14825_scop.json의 Table 37 또는 Annex D 값을 변경할 때는 출처 메타데이터를 유지하고, temperature/hour 길이와 heating_bin_hours_total이 일치하는지 확인하라.
```
