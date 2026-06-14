# EN14825 Notes

## 1. Overview

이 문서는 EN14825 SEER/SCOP 계산 구조를 프로젝트 기준으로 정리한 기준 문서다. Primary 기준은 `core/calculator_en14825.py`, `data/region_configs/en14825.json`, `tests/test_en14825_golden.py`이며, PDF는 Clause/Table/Equation 번호 확인용 Secondary 근거로만 사용한다.

현재 계산기는 `BS EN 14825:2012 / EN 14825:2012 (E)`의 공기 대 공기(Air-to-air), 가변 용량(Variable capacity), 1:1 가역식(Reversible) 장비를 대상으로 한다. 냉방은 SEER, 난방은 SCOP 경로를 제공하며, 난방 SCOP는 A/B/C/D/TOL/Tbiv 선언 운전점이 이미 해석된 입력이라고 본다. 이 구분이 중요한 이유는 EN14825의 원문은 capacity-control step 선택을 포함하지만, 현재 입력 스키마는 raw step 후보 목록을 받지 않기 때문이다. 근거: EN14825:2012 Clause 6.4.2.2, Clause 7.4.2.2.

## 2. Scope

| 항목 | 현재 지원 | 근거 | 설명 |
| --- | --- | --- | --- |
| 냉방 지표 | SEER, SEERon | EN14825:2012 Clause 6.1, Clause 6.3 | Table 36 bin hour와 A/B/C/D 선언점을 사용한다. |
| 난방 지표 | SCOP, SCOPon | EN14825:2012 Clause 7.1, Clause 7.3 | Table 37 bin hour와 Annex D 운전 시간을 사용한다. |
| 제품 유형 | 공기 대 공기, 가변 용량, 가역식 | EN14825:2012 Clause 5.2, Clause 7.4 | 현재 SCOP JSON의 `system_type` 기준이다. |
| 냉방 운전점 | A/B/C/D | EN14825:2012 Table 2 | 35/30/25/20 °C 조건을 사용한다. |
| 난방 운전점 | A/B/C/D/TOL/Tbiv | EN14825:2012 Clause 5.2, Clause 7.4 | 입력은 이미 결정된 declared point로 취급한다. |
| 난방 기후 | average, warmer, colder | EN14825:2012 Table 37 | 각 기후별 `Tdesignh`, bin hour, 운전 시간을 사용한다. |
| 보조전력 | Pto, Psb, Pck, Poff | EN14825:2012 Annex D Table D.1, Table D.2, Table D.3, Table D.4 | 단위는 kW로 입력해야 한다. |

| 제외 또는 제한 항목 | 현재 상태 | 필요한 추가 입력 | 근거 |
| --- | --- | --- | --- |
| raw capacity-control step selection | 미지원 | 각 조건별 용량 제어 step 후보 목록과 step별 효율 | EN14825:2012 Clause 6.4.2.2, Clause 7.4.2.2 |
| SCOPnet 반환 | 미반환 | SCOPnet 출력 요구와 보조열 제외 기준 검토 | EN14825:2012 Equation 10 |
| colder climate에서 TOL < -20 °C일 때 -15 °C 추가점 | 별도 입력점 미지원 | -15 °C 운전점과 해석 규칙 | EN14825:2012 Clause 7.4 관련 난방 운전점 |
| 물 대 공기, 물/브라인 계열 분기 | 미지원 | 해당 장비군 표와 보정식 | EN14825:2012 Clause 6.4.2.2, Clause 7.4.2.2 |

## 3. Glossary

용어 및 수식 기호의 상세 정의는 `en14825_glossary.md`를 참조하라. 이 문서는 규격 개요, 계산 구조, 입력/출력 스키마, 수식과 코드 매핑을 기준으로 유지하고, 용어 정의 본문은 중복 작성하지 않는다.

## 4. Input Schema

### SEER

| Field | Standard symbol | Unit | Required | Validation rule | Reference |
| --- | --- | --- | --- | --- | --- |
| `test_points["A"..."D"]` | declared capacity and power at A/B/C/D | kW, kW | Yes | 각 capacity/power는 0보다 커야 한다. | EN14825:2012 Table 2 |
| `p_design_c` | Pdesignc | kW | Yes | 0보다 커야 한다. | EN14825:2012 Clause 6.2 |
| `t_design_c` | Tdesignc | °C | No | 기본값은 `en14825.json`의 `seer.design.t_design_c`다. 16 °C는 부하선 분모가 0이므로 금지한다. | EN14825:2012 Table 2 |
| `p_to` | Pto | kW | Yes | 보조전력 합산에 직접 사용한다. | EN14825:2012 Annex D Table D.1 |
| `p_sb` | Psb | kW | Yes | 보조전력 합산에 직접 사용한다. | EN14825:2012 Annex D Table D.1 |
| `p_ck` | Pck | kW | Yes | 보조전력 합산에 직접 사용한다. | EN14825:2012 Annex D Table D.3 |
| `p_off` | Poff | kW | Yes | 가역식 냉방 기준 `Hoff = 0`이므로 현재 기본 경로에서는 영향이 없다. | EN14825:2012 Annex D Table D.1 |
| `cd` | Cd | dimensionless | No | 기본값은 `en14825.json`의 `seer.defaults.degradation_coefficient`다. | EN14825:2012 Clause 6.4.2.1 |

### SCOP

| Field | Standard symbol | Unit | Required | Validation rule | Reference |
| --- | --- | --- | --- | --- | --- |
| `test_points["A"..."D"]` | declared capacity and power at A/B/C/D | kW, kW | Yes | dict 또는 tuple 입력 가능, capacity/power는 0보다 커야 한다. | EN14825:2012 Clause 5.2 |
| `test_points["TOL"]` | declared point at TOL | kW, kW | Yes | `TOL <= Tbiv`, 기후별 `tol_max_c` 이하 | EN14825:2012 Clause 7.4 |
| `test_points["Tbiv"]` | declared point at Tbiv | kW, kW | Yes | 기후별 `tbiv_max_c` 이하 | EN14825:2012 Clause 7.4 |
| `p_design_h` | Pdesignh | kW | Yes | 0보다 커야 한다. | EN14825:2012 Clause 7.2 |
| `climate` | climate condition | n/a | Yes | `average`, `warmer`, `colder`; alias `avg`, `a`, `w`, `c` 허용 | EN14825:2012 Table 37 |
| `p_to`, `p_sb`, `p_ck`, `p_off` | Pto, Psb, Pck, Poff | kW | Yes | Annex D 운전 시간과 곱해 연간 에너지로 합산한다. | EN14825:2012 Annex D Table D.2, Table D.4 |
| `tbiv_temp_c` | Tbiv | °C | No | 없으면 기후별 최대값을 사용한다. | EN14825:2012 Clause 5.2 |
| `tol_temp_c` | TOL | °C | No | 없으면 기후별 최대값을 사용한다. | EN14825:2012 Clause 5.2 |
| `cd` | Cd | dimensionless | No | 기본 0.25다. | EN14825:2012 Clause 7.4.2.1 |
| `appliance_type` | appliance type | n/a | No | 기본 `reversible`, `heating_only`도 JSON에 존재한다. | EN14825:2012 Annex D Table D.2, Table D.4 |

## 5. Output Schema

### SEER

| Field | Meaning | Unit | Derived from | Reference |
| --- | --- | --- | --- | --- |
| `seer` | 최종 계절 냉방 효율 | W/W 또는 kW/kW | `Qc / total_kWh` | EN14825:2012 Clause 6.1 |
| `seer_on` | 활성 냉방 효율 | W/W 또는 kW/kW | bin별 `Pc / EERPL` 합산 | EN14825:2012 Clause 6.3 |
| `qc_kwh` | 기준 연간 냉방 수요 | kWh | `Pdesignc * Hce` | EN14825:2012 Clause 6.2 |

### SCOP

| Field | Meaning | Unit | Derived from | Reference |
| --- | --- | --- | --- | --- |
| `scop`, `SCOP` | 최종 계절 난방 효율 | W/W 또는 kW/kW | `Qh / total_kWh` | EN14825:2012 Clause 7.1 |
| `scop_on` | 활성 난방 효율 | W/W 또는 kW/kW | Equation 9 구조의 bin 합산 | EN14825:2012 Clause 7.3, Equation 9 |
| `qh_kwh` | 기준 연간 난방 수요 | kWh | `Pdesignh * Hhe` | EN14825:2012 Clause 7.2 |
| `active_kwh` | 활성 난방 에너지 | kWh | `Qh / SCOPon` | EN14825:2012 Clause 7.1 |
| `standby_kwh` | 보조 운전 모드 에너지 | kWh | `Hto*Pto + Hsb*Psb + Hck*Pck + Hoff*Poff` | EN14825:2012 Annex D Table D.2, Table D.4 |
| `total_kwh` | 총 연간 난방 에너지 | kWh | `active_kwh + standby_kwh` | EN14825:2012 Clause 7.1 |
| `bin_details` | bin별 난방 부하, 용량, COPPL, elbu, 기여 에너지 | mixed | Table 37 bin loop | EN14825:2012 Table 37, Equation 9 |
| `unimplemented_notes` | 현재 구현 제한 설명 | n/a | 프로젝트 해석 | EN14825:2012 Clause 7.4.2.2, Equation 10 |

## 6. Calculation Flow

### SEER Flow

1. A/B/C/D 입력 capacity와 power가 모두 0보다 큰지 확인한다.
2. `en14825.json`의 `seer.operational_hours`에서 appliance type별 `Hce`를 읽고 `Qc = Pdesignc * Hce`를 계산한다. 현재 기본 `Hce = 350 h`다. 근거: EN14825:2012 Clause 6.2, Annex D Table D.1.
3. 각 냉방 declared point의 `EERDC = capacity / power`를 계산한다.
4. A는 degradation을 적용하지 않고, B/C/D는 declared capacity가 required cooling load보다 큰 경우 Cd degradation을 적용한다. 근거: EN14825:2012 Clause 6.4.2.1.
5. `en14825.json`의 `seer.bin_data` Table 36 bin에서 `Pc(Tj) = Pdesignc * (Tj - 16) / (Tdesignc - 16)`을 계산한다. 근거: EN14825:2012 Table 36, Clause 6.4.
6. bin 온도별 `EERPL(Tj)`를 A/B/C/D point에서 선형 보간한다. 범위 밖은 끝점으로 clamp한다.
7. `SEERon = sum(hj * Pc(Tj)) / sum(hj * Pc(Tj) / EERPL(Tj))`를 계산한다. 근거: EN14825:2012 Clause 6.3.
8. `SEER = Qc / (Qc / SEERon + Hto*Pto + Hsb*Psb + Hck*Pck + Hoff*Poff)`를 계산한다. 근거: EN14825:2012 Clause 6.1, Annex D Table D.1, Table D.3.

### SCOP Flow

1. 기후 문자열을 정규화하고, JSON에서 기후별 `Tdesignh`, heating bin temperature/hour, Tbiv/TOL 제한, Annex D 운전 시간을 읽는다. 근거: EN14825:2012 Table 37, Annex D Table D.2, Table D.4.
2. A/B/C/D/TOL/Tbiv declared point를 해석한다. dict 입력은 `capacity`, `power`, 선택적 `temp_c`를 사용하고, tuple 입력은 capacity/power만 사용한다.
3. 온도가 입력되지 않은 A/B/C/D는 JSON schema의 -7/2/7/12 °C를 사용한다. Tbiv/TOL은 사용자 입력 온도 또는 기후별 최대값을 사용한다.
4. `Tbiv <= climate tbiv_max`, `TOL <= climate tol_max`, `TOL <= Tbiv`를 검증한다.
5. 각 declared point에서 `Ph(Tj) = Pdesignh * (Tj - 16) / (Tdesignh - 16)`를 계산한다. 근거: EN14825:2012 Clause 7.2, Table 37.
6. 각 declared point에서 `COPDC = capacity / power`를 계산하고, 현재 declared-point 입력 스키마에 맞춘 Clause 7.4.2.2 해석으로 `COPPL`을 결정한다.
7. capacity curve와 COPPL curve를 온도순으로 구성한다. 같은 온도에 여러 point가 있으면 priority는 `TOL > Tbiv > A > B > C > D`다.
8. Table 37 각 bin에서 `Ph(Tj)`를 계산한다. `Tj < TOL`이면 히트펌프 용량과 COPPL은 0이며 `elbu = Ph(Tj)`다.
9. `Tj >= TOL`이면 capacity와 COPPL을 선형 보간한다. COPPL은 상단 범위에서 마지막 두 점을 사용해 외삽할 수 있다.
10. `Pdh(Tj) >= Ph(Tj)`이면 보조 전기 히터는 0이고, 부족하면 `elbu(Tj) = Ph(Tj) - Pdh(Tj)`다. 근거: EN14825:2012 Equation 9.
11. `SCOPon = sum(hj * Ph(Tj)) / sum(hj * ((Ph(Tj) - elbu(Tj)) / COPPL(Tj) + elbu(Tj)))` 구조로 활성 난방 효율을 계산한다. 근거: EN14825:2012 Clause 7.3, Equation 9.
12. `Qh = Pdesignh * Hhe`를 계산하고, Annex D 운전 모드 에너지를 더해 최종 SCOP를 계산한다. 근거: EN14825:2012 Clause 7.1, Clause 7.2, Annex D Table D.2, Table D.4.

## 7. Formula Mapping

| Formula | Standard reference | Inputs | Outputs | Project interpretation |
| --- | --- | --- | --- | --- |
| `Qc = Pdesignc * Hce` | EN14825:2012 Clause 6.2 | Pdesignc, Hce | qc_kwh | Hce는 가역식 기준 350 h를 사용한다. |
| `Pc(Tj) = Pdesignc * (Tj - 16) / (Tdesignc - 16)` | EN14825:2012 Clause 6.4, Table 36 | Tj, Pdesignc, Tdesignc | cooling load | 음수 부하는 0으로 clamp한다. |
| `EERPL = EERDC * (1 - Cd * (1 - CR))` | EN14825:2012 Clause 6.4.2.1 | EERDC, Cd, CR | EERPL | A는 degradation 제외, B/C/D는 조건에 따라 적용한다. |
| `SEERon = sum(hj * Pc) / sum(hj * Pc / EERPL)` | EN14825:2012 Clause 6.3 | Table 36, Pc, EERPL | seer_on | A/B/C/D point에서 EERPL을 선형 보간한다. |
| `SEER = Qc / (Qc / SEERon + mode energy)` | EN14825:2012 Clause 6.1 | Qc, SEERon, Pto/Psb/Pck/Poff | seer | 보조전력 단위는 kW여야 한다. |
| `Qh = Pdesignh * Hhe` | EN14825:2012 Clause 7.2 | Pdesignh, Hhe | qh_kwh | Hhe는 기후별 Annex D 값을 사용한다. |
| `Ph(Tj) = Pdesignh * (Tj - 16) / (Tdesignh - 16)` | EN14825:2012 Clause 7.2, Table 37 | Tj, Pdesignh, Tdesignh | bin heating load | 음수 부하는 0으로 clamp한다. |
| `COPPL` with Cd | EN14825:2012 Clause 7.4.2.1, Clause 7.4.2.2 | capacity, power, load, Cd | cop_pl | raw step list가 없으므로 declared point 기준의 10% 조건을 적용한다. |
| `elbu(Tj) = max(0, Ph(Tj) - Pdh(Tj))` | EN14825:2012 Equation 9 | Ph, Pdh | elbu | Tj < TOL이면 Pdh=0, elbu=Ph다. |
| `SCOPon = sum(hj * Ph) / sum(hj * ((Ph - elbu) / COPPL + elbu))` | EN14825:2012 Clause 7.3, Equation 9 | Table 37, Ph, COPPL, elbu | scop_on | bin별 상세 결과를 `bin_details`에 남긴다. |
| `SCOP = Qh / (Qh / SCOPon + mode energy)` | EN14825:2012 Clause 7.1 | Qh, SCOPon, Pto/Psb/Pck/Poff | scop | operational hours는 JSON의 appliance_type/climate 조합을 사용한다. |

## 8. Code Mapping

| Standard item | File | Function | Output key | Notes |
| --- | --- | --- | --- | --- |
| Table 36 cooling bin hours | `data/region_configs/en14825.json` `seer` section | `_get_seer_bin_data` | n/a | module constants remain legacy fallback |
| Cooling load line | `core/calculator_en14825.py` | `_cooling_load_at_temp` | internal | Tdesignc=16이면 fail-fast |
| EERPL declared point | `core/calculator_en14825.py` | `_eer_pl_at_declared_point` | internal | `_part_load_performance` 공통 사용 |
| SEERon | `core/calculator_en14825.py` | `_calculate_seer_on` | `seer_on` | `seer.bin_data` 기반 bin loop |
| SEER | `core/calculator_en14825.py` | `calculate_seer` | `seer`, `seer_on`, `qc_kwh` | `seer.design`, `seer.defaults`, `seer.operational_hours` 기본값을 사용한다. |
| Table 37 and Annex D data | `data/region_configs/en14825.json` `scop` section | n/a | source data | climate와 appliance_type별 값 |
| SCOP point validation | `core/calculator_en14825.py` | `_validate_scop_points` | internal | TOL/Tbiv 제한 검증 |
| Heating load line | `core/calculator_en14825.py` | `_heating_part_load` | internal | Tdesignh=16이면 fail-fast |
| SCOP Cd handling | `core/calculator_en14825.py` | `_scop_pl_at_declared_point` | internal | Clause 7.4.2.2를 declared-point schema에 맞춰 해석 |
| SCOP capacity/COPPL curve | `core/calculator_en14825.py` | `_scop_capacity_curve_points`, `_scop_coppl_curve_points` | internal | 같은 온도 priority 존재 |
| SCOPon | `core/calculator_en14825.py` | `_calculate_scop_on` | `scop_on`, `bin_details` | Equation 9 구조 |
| SCOP | `core/calculator_en14825.py` | `calculate_scop` | `scop`, `SCOP`, `qh_kwh`, `active_kwh`, `standby_kwh`, `total_kwh` | SCOPnet은 반환하지 않는다. |

## 9. Critical Implementation Notes

| 주의사항 | 왜 중요한가 | 근거 |
| --- | --- | --- |
| 보조전력 입력은 W가 아니라 kW로 넣어야 한다. | Annex D 시간이 h 단위이므로 W를 그대로 넣으면 연간 에너지가 1000배 커진다. | EN14825:2012 Annex D |
| SCOP A/B/C/D/TOL/Tbiv는 raw step 후보가 아니라 이미 해석된 declared point다. | 현재 API로는 완전한 closest-step selection을 재현할 수 없다. | EN14825:2012 Clause 7.4.2.2 |
| declared capacity가 required load보다 크고 load gap이 10% 초과인 경우에만 SCOP Cd degradation을 적용한다. | 현재 입력 스키마에서 ±10% closest step 개념을 보수적으로 반영한 조건이다. | EN14825:2012 Clause 7.4.2.2 |
| Tj < TOL 구간은 히트펌프 off, 전기 백업 only로 처리한다. | 저온 bin의 denominator가 급격히 증가하므로 SCOP에 큰 영향을 준다. | EN14825:2012 Equation 9 |
| Table 37 bin hour 총합을 JSON의 expected total과 비교한다. | bin hour 누락은 계절 합산 전체를 왜곡한다. | EN14825:2012 Table 37 |
| `SCOPon`의 active demand 합과 `Qh = Pdesignh * Hhe`는 서로 다른 위치에서 사용된다. | Equation 9의 bin 기반 활성 효율과 Clause 7.2의 기준 연간 수요를 혼동하면 SCOP가 달라진다. | EN14825:2012 Clause 7.2, Equation 9 |

## 10. Unsupported / Not Yet Implemented

| Item | Reason | Required data to support | Reference |
| --- | --- | --- | --- |
| Full variable-capacity closest step selection | raw capacity-control step list가 입력되지 않는다. | 각 조건별 step capacity, power, efficiency 후보 | EN14825:2012 Clause 6.4.2.2, Clause 7.4.2.2 |
| SCOPnet output | 현재 요구 출력은 SCOP이며 반환 dict에 SCOPnet이 없다. | SCOPnet 정의와 출력 schema 확장 | EN14825:2012 Equation 10 |
| Optional -15 °C point for colder special case | 현재 입력 schema는 A/B/C/D/TOL/Tbiv 고정이다. | -15 °C declared point | EN14825:2012 Clause 7.4 |
| Water/brine formula branches | 현재 대상은 air-to-air다. | 장비군별 입력 schema와 별도 수식 | EN14825:2012 Clause 6.4.2.2, Clause 7.4.2.2 |
| Certified reference workbook parity | 현재 golden 값은 프로젝트 테스트 기준이다. | 인증 리포트 또는 공식 예제의 전체 입력/출력 | Project golden tests |

## 11. Golden Sample Verification

| Case | Source | Expected | Actual | Tolerance | Result |
| --- | --- | ---: | ---: | ---: | --- |
| SEER golden | `tests/test_en14825_golden.py` | 9.104 | test expected 기준 | 0.005 | 현재 테스트 기준 |
| SCOP average | `tests/test_en14825_golden.py` | 5.108 | test expected 기준 | 0.005 | 현재 테스트 기준 |
| SCOP warmer | `tests/test_en14825_golden.py` | 6.008 | test expected 기준 | 0.005 | 현재 테스트 기준 |
| SCOP colder | `tests/test_en14825_golden.py` | 4.190 | test expected 기준 | 0.005 | 현재 테스트 기준 |

검증 시 권장 명령:

```bash
python3 -B -m py_compile core/calculator_en14825.py
python3 -B -m pytest tests/test_en14825_golden.py -v --runxfail
```

## 12. References

| Reference | Usage |
| --- | --- |
| `core/calculator_en14825.py` | Primary: 현재 계산 동작 기준 |
| `data/region_configs/en14825.json` | Primary: unified EN14825 config owner; `seer` contains cooling constants and `scop` contains heating climate/Annex D data |
| `tests/test_en14825_golden.py` | Primary: 현재 golden 기대값 기준 |
| `docs/archive/standards_legacy/en14825_scop_notes.md` | Historical archive: PDF 확인 페이지와 원본 SEER/SCOP 요약 보존 |
| `docs/en14825/en14825_dev_notes.md` | Secondary: PDF 확인 페이지, Clause 6.1~6.4, Clause 7.1~7.4, Table 36, Table 37, Annex D Table D.1~D.4 근거 확인 |

## 13. Prompt for Future Agent

```text
AGENTS.md의 Lite 규칙과 docs/DOCS_GUIDELINES.md를 먼저 읽어라. EN14825 작업에서는 docs/en14825/en14825_notes.md, docs/en14825/en14825_dev_notes.md, docs/en14825/en14825_design_notes.md, docs/en14825/en14825_glossary.md, core/calculator_en14825.py를 기준으로 삼고, PDF는 Clause/Table/Equation 확인용으로만 사용하라. 과거 PDF 검토 범위 확인이 필요할 때만 docs/archive/standards_legacy/en14825_scop_notes.md를 historical source로 참조하라. 코드 변경이 필요한 경우 수정 대상 파일과 금지 파일을 명시하고, py_compile 및 tests/test_en14825_golden.py 검증을 수행하라.
```
