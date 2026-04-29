# ISO16358 Notes

## 1. Overview

ISO 16358은 air-cooled air conditioner와 heat pump의 seasonal performance factor를 산정하기 위한 공통 계산 체계이다. 이 프로젝트의 `iso16358` 문서는 국가별 세부 규정을 포함하지 않고, cooling seasonal performance factor(CSPF)를 계산하는 공통 엔진의 입력, 중간 계산, 출력, 검증 기준을 정의한다.

근거: ISO 16358-1:2013 Chapter 5, Chapter 6, Clause 6.4, Clause 6.5, Clause 6.6, Clause 6.7. UN AC proposal Table 4는 ISO 16358-1:2013의 Chapter 5, Chapter 6 및 용량 제어 방식별 Clause 6.4~6.7을 CSPF 계산 기준으로 참조한다.

프로젝트 해석: 현재 구현 범위는 region configuration으로 시험점, 파생점, bin-hour, building load 기준을 주입하고 하나의 CSPF 계산 흐름으로 처리하는 공통 계산 엔진이다.

## 2. Scope

| 항목 | 지원 범위 | 제외 범위 | Reference |
| --- | --- | --- | --- |
| 평가 지표 | CSPF | APF, HSPF, standby/off-mode 별도 합산 | ISO 16358-1:2013 Chapter 5, Chapter 6 |
| 제품 모드 | Cooling | Heating 전용 계산 | ISO 16358-1:2013 |
| 용량 제어 | fixed, two-stage, multi-stage, variable capacity를 포인트 구성으로 표현 | 규격 원문 방식별 독립 함수 분기 | ISO 16358-1:2013 Clause 6.4~6.7 |
| 기후 데이터 | region configuration의 outdoor temperature bin hours | 특정 국가 bin의 원문 재서술 | UN AC proposal Annex 4 |
| 지역 특이 규칙 | region 문서에서 확장 | ISO 공통 문서에 국가별 특례 포함 | docs/DOCS_GUIDELINES.md |

## 3. Calculation Structure

| 단계 | 계산 내용 | 입력 | 출력 | Reference |
| --- | --- | --- | --- | --- |
| 1 | region configuration을 읽어 기준 온도, 부하 기준, 시험점, 파생 규칙, bin-hour를 준비한다. | JSON configuration | calculator state | ISO 16358-1:2013 Chapter 6 |
| 2 | 측정 시험점을 검증하고 필요한 파생 시험점을 생성한다. | measured points, derived rules | resolved points | ISO 16358-1:2013 Clause 6.4~6.7 |
| 3 | 기준 냉방 부하를 결정한다. | reference point 또는 declared capacity | L_c_ref | ISO 16358-1:2013 Chapter 6 |
| 4 | 각 outdoor temperature bin에서 building load BL(tj)를 계산한다. | L_c_ref, t_100_load, t_0_load, tj | Lc | ISO 16358-1:2013 Chapter 6 |
| 5 | 각 bin 온도에서 용량과 소비전력을 보간 또는 외삽한다. | resolved points, tj | interpolated capacity/power | ISO 16358-1:2013 Clause 6.4~6.7 |
| 6 | 부하가 최저 용량 이하이면 PLF와 Cd를 적용한다. | Lc, lowest capacity, Cd | P_tj | ISO 16358-1:2013 Chapter 6 |
| 7 | 부하가 용량 범위 안이면 부하를 만족하는 소비전력을 산정한다. | Lc, interpolated load points | P_tj | ISO 16358-1:2013 Chapter 6 |
| 8 | 부하가 최고 용량을 초과하면 최고 용량으로 cooling output을 제한한다. | Lc, highest capacity | capped cooling output | ISO 16358-1:2013 Chapter 6 |
| 9 | bin-hour로 cooling output과 power를 누적하고 CSPF를 계산한다. | cooling output, P_tj, nj | annual cooling, annual power, CSPF | ISO 16358-1:2013 Chapter 5 |

## 4. Input Schema

| Field | Standard meaning | Unit | Required | Validation rule | Data location |
| --- | --- | --- | --- | --- | --- |
| `measured_inputs` | 시험점별 measured cooling capacity와 power | W | Yes | configuration에서 `measure`로 지정된 point가 모두 있어야 한다. | caller input |
| `capacity` | 시험점 냉방 능력 | W | Yes | 양수 값이어야 한다. 지역 규칙에 따라 반올림될 수 있다. | `measured_inputs[point].capacity` |
| `power` | 시험점 소비전력 | W | Yes | 양수 값이어야 한다. 지역 규칙에 따라 반올림될 수 있다. | `measured_inputs[point].power` |
| `declared_capacity` | 제조사 선언 정격 냉방 능력 | W | Conditional | `building_load_source`가 `declared`이면 필수이다. | caller input |
| `t_100_load` | 100% cooling load reference temperature | °C | Yes | `t_0_load`와 같으면 안 된다. | region configuration |
| `t_0_load` | zero cooling load reference temperature | °C | Yes | `t_100_load`와 같으면 안 된다. | region configuration |
| `Cd` | degradation coefficient | dimensionless | Yes | PLF 계산에 사용된다. | region configuration |
| `bin_hours` | outdoor temperature bin hours | h | Yes | `nj`가 0 이하인 bin은 누적에서 제외된다. | region configuration |

## 5. Output Schema

| Field | Meaning | Unit | Derived from | Notes |
| --- | --- | --- | --- | --- |
| `cspf` | cooling seasonal performance factor | Wh/Wh | total seasonal cooling output / total seasonal electric power | 소수 셋째 자리로 반올림한다. |
| `annual_cooling_kwh` | 연간 냉방량 | kWh | accumulated cooling output / 1000 | 내부 누적 단위는 Wh이다. |
| `annual_power_kwh` | 연간 소비전력량 | kWh | accumulated power / 1000 | 내부 누적 단위는 Wh이다. |

## 6. Formula Mapping

| Formula | Standard reference | Inputs | Outputs | Project interpretation |
| --- | --- | --- | --- | --- |
| Building load line | ISO 16358-1:2013 Chapter 6 | L_c_ref, t_100_load, t_0_load, tj | Lc | `Lc = L_c_ref * (tj - t_0_load) / (t_100_load - t_0_load)`로 계산한다. |
| Temperature interpolation | ISO 16358-1:2013 Clause 6.4~6.7 | two temperature points, tj | capacity, power | 동일 load type 안에서 온도 기준 선형 보간/외삽을 수행한다. |
| PLF correction | ISO 16358-1:2013 Chapter 6 | Lc, lowest capacity, Cd | P_tj | 최저 용량보다 부하가 낮을 때 `PLF = 1 - Cd * (1 - X)`를 적용한다. |
| Capacity-range power | ISO 16358-1:2013 Chapter 6 | adjacent capacity/power points, Lc | P_tj | 공통 기본값은 capacity-linear interpolation이다. |
| Seasonal accumulation | ISO 16358-1:2013 Chapter 5 | cooling output, P_tj, nj | cstl, csec | 각 bin의 시간 가중치를 곱해 Wh 단위로 합산한다. |
| CSPF | ISO 16358-1:2013 Chapter 5 | cstl, csec | CSPF | cstl / csec 값을 seasonal factor로 사용한다. |

## 7. Code Mapping

| Standard item | File | Function | Output key | Notes |
| --- | --- | --- | --- | --- |
| region configuration loading | `core/calculator_iso16358.py` | `ISO16358Calculator.__init__` | internal configuration | JSON key를 공통 엔진 속성으로 읽는다. |
| measured/default point resolution | `core/calculator_iso16358.py` | `resolve_points` | resolved point dict | `points`와 `derived_rules`를 해석한다. |
| temperature interpolation | `core/calculator_iso16358.py` | `interpolate` | interpolated point dict | load type별로 temperature-capacity-power line을 만든다. |
| CSPF calculation | `core/calculator_iso16358.py` | `calculate_cspf` | `cspf`, `annual_cooling_kwh`, `annual_power_kwh` | bin loop와 seasonal accumulation을 수행한다. |
| region data | `data/region_configs/*.json` | configuration file | configuration keys | 국가별 차이는 JSON과 region 문서로 분리한다. |

## 8. Golden Sample Verification

공통 ISO 문서는 국가별 golden sample을 본문에 복사하지 않는다. 공통 엔진의 golden 검증은 region 문서의 샘플을 통해 동일 계산 흐름이 재현되는지 확인한다.

| Case | Source | Expected | Actual | Tolerance | Result |
| --- | --- | --- | --- | --- | --- |
| Korea KS C 9306 region sample | `regions/ks_c_9306/ks_c_9306_notes.md` | CSPF 6.504 | CSPF 6.504 | 0.001 | Pass |

## 9. Unsupported / Not Yet Implemented

| Item | Reason | Required data to support | Reference |
| --- | --- | --- | --- |
| APF/HSPF | 현재 계산기는 cooling CSPF 흐름만 문서화한다. | heating test points, heating bin-hours, defrost/backup heat rules | ISO 16358-2:2013 |
| standby/off-mode seasonal energy | 현재 반환 스키마에 별도 보조전력 항목이 없다. | standby hours, thermostat-off hours, crankcase heater power | ISO 16358-3:2013 Chapter 5 |
| country-specific exceptions | 공통 문서의 범위 밖이다. | region-specific notes and configuration | docs/DOCS_GUIDELINES.md |

## 10. References

| Source | Usage |
| --- | --- |
| ISO 16358-1:2013 Chapter 5, Chapter 6, Clause 6.4~6.7 | CSPF 계산 구조와 용량 제어 방식별 계산 흐름의 기준 |
| UN AC proposal regarding ISO16358, Table 4 | ISO 16358-1:2013 참조 chapter와 clause 확인 |
| UN AC proposal regarding ISO16358, Annex 4 | outdoor temperature bin hours가 seasonal calculation에 쓰인다는 근거 |
| `core/calculator_iso16358.py` | 프로젝트 구현 매핑 |
| `data/region_configs/*.json` | 지역별 configuration schema |
