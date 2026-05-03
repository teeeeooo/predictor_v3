# ISO16358 Notes

## 1. Overview

ISO 16358은 air-cooled air conditioner와 heat pump의 seasonal performance factor를 산정하기 위한 공통 계산 체계이다. 이 프로젝트의 `iso16358` 문서는 국가별 세부 규정을 본문에 길게 포함하지 않고, CSPF/HSPF 공통 계산 구조와 region configuration 경계를 정의한다.

근거: ISO 16358-1:2013 Chapter 5, Chapter 6, Clause 6.4, Clause 6.5, Clause 6.6, Clause 6.7. ISO 16358-2는 heating seasonal performance factor의 계절 난방 부하, 계절 소비전력, HSPF 비율 구조를 제공한다.

프로젝트 해석: 현재 구현은 region configuration으로 시험점, 파생점, bin-hour, building load 기준을 주입하고 하나의 ISO16358 계산 엔진에서 CSPF common path와 HSPF common/variable/profile path를 처리한다. KS C 9306 상세 수식과 region-specific 판단은 [ks_c_9306_notes.md](./regions/ks_c_9306/ks_c_9306_notes.md)에 둔다.

## 2. Scope

| 항목 | 지원 범위 | 제외 범위 | Reference |
| --- | --- | --- | --- |
| 평가 지표 | CSPF, HSPF | APF, standby/off-mode 별도 합산 | ISO 16358-1:2013 Chapter 5, Chapter 6; ISO 16358-2 |
| 제품 모드 | Cooling, Heating | 통합 APF 계산 | ISO 16358-1; ISO 16358-2 |
| 용량 제어 | fixed, two-stage, multi-stage, variable capacity를 포인트 구성으로 표현 | 규격 원문 방식별 독립 public API | ISO 16358-1:2013 Clause 6.4~6.7 |
| 기후 데이터 | region configuration의 outdoor temperature bin hours | 특정 국가 bin의 원문 재서술 | UN AC proposal Annex 4; region notes |
| 지역 특이 규칙 | region 문서와 JSON profile에서 확장 | ISO 공통 문서에 국가별 특례 포함 | docs/DOCS_GUIDELINES.md |

## 3. CSPF Current Status

ISO 16358-1 CSPF common 엔진은 구현되어 있다. Korea KS C 9306 CSPF golden은 `6.504`를 유지한다.

| Item | Current behavior |
| --- | --- |
| 시험점 | region config의 `points`로 measured/default point를 선언한다. |
| 파생점 | `derived_rules`로 default point를 생성한다. |
| bin-hour | `bin_hours`를 사용해 cooling output과 electric power를 누적한다. |
| building load | `building_load_source`, `reference_point`, `declared_capacity`, load temperatures로 결정한다. |
| region-specific branch | 공통 CSPF 흐름 안에서 config key로만 분기한다. |

### 3.1 CSPF `cspf_test_profile` opt-in path status

ISO16358-1 CSPF는 기존 flat region config path를 유지하면서, variable-capacity / inverter-only 장비를 위한 `cspf_test_profile` opt-in path를 병렬로 도입하고 있다.

현재 구현 상태:

| Item | Status |
| --- | --- |
| Target unit type | Variable-capacity / inverter-only |
| Out of scope | Fixed, two-stage, multi-stage |
| T1 required_only resolver | Implemented |
| T1 required_only calculation path | Implemented |
| T1 with_optional_test | Planned |
| T3 required_only | Planned |
| T3 with_optional_test | Planned |
| Legacy flat config path | Preserved |

T1 `required_only`에서는 35°C full/half measured point만 필수로 받고, 29°C full/half point는 default factor로 생성한다. Minimum point는 생성하지 않으며, half point를 lowest continuous operating point로 사용한다.

T3는 아직 계산 path에 연결하지 않았지만, 공식 xlsm 역추적 결과에 따라 `tj > 35`에서는 46↔35 segment, `tj <= 35`에서는 35↔29 segment를 사용할 예정이다.

## 4. HSPF Current Status

ISO 16358-2 HSPF의 현재 구현은 계절 난방 부하와 계절 소비전력의 Wh 누적 구조를 따른다.

| Formula item | Project behavior |
| --- | --- |
| `HSTL` | `Σ building load × hours` |
| `HSEC` | `Σ heat pump energy + auxiliary energy` |
| `HSPF` | `HSTL / HSEC` |
| auxiliary / make-up heat | 난방 능력 부족분을 denominator인 `HSEC`에 포함한다. |

현재 경로:

| Path | Role |
| --- | --- |
| HSPF common fallback | heating point를 온도 기준으로 보간/외삽하고 부족분을 auxiliary로 누적한다. |
| variable HSPF path | stage별 heating point를 사용해 load 위치별 운전점을 선택한다. |
| KS C 9306 HSPF profile path | `hspf.profile = ks_c_9306_hspf`일 때 KS profile-specific helper를 사용한다. |

## 5. CSPF vs HSPF Structure Difference

| Item | CSPF | HSPF |
| --- | --- | --- |
| Load direction | outdoor temperature 상승에 따라 cooling load가 증가한다. | outdoor temperature 하락에 따라 heating load가 증가한다. |
| Main limiting case | capacity excess, cyclic operation, part-load correction | capacity shortage, auxiliary heat, defrost correction |
| Seasonal numerator | delivered cooling output | building heating load |
| Seasonal denominator | cooling electric energy | heat pump electric energy plus auxiliary energy |
| Region sensitivity | cooling bin, cooling load line, part-load rules | heating bin, heating load line, frost/defrost rules |

## 6. Region Configuration Principles

ISO common 엔진에 국가별 rule을 하드코딩하지 않는다. region별 `bin_hours`, `hspf_bin_hours`, `load_line`, `required_points`, `derived_rules`는 JSON/profile로 관리한다.

production region config에는 규격값과 공식 계수만 둔다. golden/sample/test fixture 전용 값은 test fixture에 분리한다. 특정 국가의 해석, 수식 번호, 예외 동작은 `docs/iso16358/regions/<region>/` 아래에 기록한다.

## 7. Input Schema

| Field | Standard meaning | Unit | Required | Validation rule | Data location |
| --- | --- | --- | --- | --- | --- |
| `measured_inputs` | 시험점별 measured capacity와 power | W | Yes | configuration/profile에서 요구하는 point가 모두 있어야 한다. | caller input |
| `capacity` | 시험점 능력 | W | Yes | 양수 값이어야 한다. 지역 규칙에 따라 반올림될 수 있다. | `measured_inputs[point].capacity` |
| `power` | 시험점 소비전력 | W | Yes | 양수 값이어야 한다. 지역 규칙에 따라 반올림될 수 있다. | `measured_inputs[point].power` |
| `declared_capacity` | 제조사 선언 정격 냉방 능력 | W | Conditional | `building_load_source = declared`이면 CSPF에서 필수이다. | caller input |
| `rated_heating_capacity` | 정격 난방 능력 | W | Conditional | HSPF load line 또는 common fallback에서 필요할 수 있다. | caller input |
| `aux_cop` | 보조열 COP | dimensionless | Optional | 0보다 커야 한다. | caller input |
| `bin_hours` | cooling outdoor temperature bin hours | h | CSPF Yes | `nj`가 0 이하인 bin은 누적에서 제외된다. | region configuration |
| `hspf_bin_hours` | heating outdoor temperature bin hours | h | HSPF Yes | `nj`가 0 이하인 bin은 누적에서 제외된다. | region configuration |
| `cspf_test_profile` | ISO16358 CSPF variable-capacity profile selector | object | Optional | 있으면 profile path로 진입하고, 없으면 legacy flat config path를 사용한다. | region configuration |
| `climate_profile` | CSPF climate profile | enum | Profile path Yes | `T1` 또는 `T3` | `cspf_test_profile.climate_profile` |
| `test_selection` | required/optional test selection | enum | Profile path Yes | `required_only` 또는 `with_optional_test` | `cspf_test_profile.test_selection` |

## 8. Output Schema

| Field | Meaning | Unit | Derived from | Notes |
| --- | --- | --- | --- | --- |
| `cspf` | cooling seasonal performance factor | Wh/Wh | total seasonal cooling output / total seasonal electric power | 소수 셋째 자리로 반올림한다. |
| `annual_cooling_kwh` | 연간 냉방량 | kWh | accumulated cooling output / 1000 | 내부 누적 단위는 Wh이다. |
| `annual_power_kwh` | 연간 냉방 소비전력량 | kWh | accumulated power / 1000 | 내부 누적 단위는 Wh이다. |
| `hspf` | heating seasonal performance factor | Wh/Wh | `hstl / hsec` | HSPF path별 raw precision을 유지할 수 있다. |
| `hstl` | heating seasonal total load | Wh | `Σ BL(tj) × nj` | building load 기준 누적값이다. |
| `hsec` | heating seasonal electric consumption | Wh | heat pump energy plus auxiliary energy | auxiliary energy를 포함한다. |
| `heat_pump_energy` | heat pump electric energy | Wh | bin별 heat pump power × hours | HSPF denominator 구성요소이다. |
| `auxiliary_energy` | auxiliary electric energy | Wh | auxiliary heat × hours / aux_cop | HSPF denominator 구성요소이다. |

## 9. Formula Mapping

| Formula | Standard reference | Inputs | Outputs | Project interpretation |
| --- | --- | --- | --- | --- |
| Cooling building load line | ISO 16358-1:2013 Chapter 6 | L_c_ref, t_100_load, t_0_load, tj | Lc | `Lc = L_c_ref * (tj - t_0_load) / (t_100_load - t_0_load)`로 계산한다. |
| Temperature interpolation | ISO 16358-1:2013 Clause 6.4~6.7 | two temperature points, tj | capacity, power | 동일 load type 안에서 온도 기준 선형 보간/외삽을 수행한다. |
| Cooling PLF correction | ISO 16358-1:2013 Chapter 6 | Lc, lowest capacity, Cd | P_tj | 최저 용량보다 부하가 낮을 때 `PLF = 1 - Cd * (1 - X)`를 적용한다. |
| Capacity-range power | ISO 16358-1:2013 Chapter 6 | adjacent capacity/power points, Lc | P_tj | 공통 기본값은 capacity-linear interpolation이다. |
| CSPF seasonal accumulation | ISO 16358-1:2013 Chapter 5 | cooling output, P_tj, nj | cstl, csec | 각 bin의 시간 가중치를 곱해 Wh 단위로 합산한다. |
| HSPF seasonal accumulation | ISO 16358-2 | building load, heat pump power, auxiliary energy, nj | hstl, hsec | numerator는 building load, denominator는 heat pump energy와 auxiliary energy의 합이다. |
| Auxiliary energy | ISO 16358-2 auxiliary / make-up heat structure | shortage, hours, aux_cop | auxiliary energy | `auxiliary_heat × hours / aux_cop`로 계산한다. |

## 10. Code Mapping

| Standard item | File | Function | Output key | Notes |
| --- | --- | --- | --- | --- |
| region configuration loading | `core/calculator_iso16358.py` | `ISO16358Calculator.__init__` | internal configuration | JSON key를 공통 엔진 속성으로 읽는다. |
| measured/default point resolution | `core/calculator_iso16358.py` | `resolve_points` | resolved point dict | `points`와 `derived_rules`를 해석한다. |
| cooling temperature interpolation | `core/calculator_iso16358.py` | `interpolate` | interpolated point dict | load type별 temperature-capacity-power line을 만든다. |
| heating temperature interpolation | `core/calculator_iso16358.py` | `interpolate_heating` | interpolated point dict | HSPF common fallback에서 사용한다. |
| CSPF calculation | `core/calculator_iso16358.py` | `calculate_cspf` | `cspf`, `annual_cooling_kwh`, `annual_power_kwh` | bin loop와 seasonal accumulation을 수행한다. |
| HSPF calculation | `core/calculator_iso16358.py` | `calculate_hspf` | `hspf`, `hstl`, `hsec` | generic, variable, profile branch의 entry point이다. |
| variable HSPF bin | `core/calculator_iso16358.py` | `_variable_heating_bin` | bin detail | aux_cop를 auxiliary energy에 적용한다. |
| KS C 9306 HSPF profile | `core/calculator_iso16358.py` | `_calculate_ks_c9306_hspf` | `hspf`, `details` | KS region 문서의 profile-specific helper이다. |
| region data | `data/region_configs/*.json` | configuration file | configuration keys | 국가별 차이는 JSON과 region 문서로 분리한다. |

## 11. Golden Sample Verification

공통 ISO 문서는 국가별 golden sample을 본문에 복사하지 않는다. 공통 엔진의 golden 검증은 region 문서와 test fixture를 통해 동일 계산 흐름이 재현되는지 확인한다.

| Case | Source | Expected | Actual | Tolerance | Result |
| --- | --- | --- | --- | --- | --- |
| Korea KS C 9306 CSPF region sample | `regions/ks_c_9306/ks_c_9306_notes.md` | CSPF 6.504 | CSPF 6.504 | 0.001 | Pass |

## 12. Unsupported / Not Yet Implemented

| Item | Reason | Required data to support | Reference |
| --- | --- | --- | --- |
| APF | 현재 반환 스키마에 통합 annual performance factor가 없다. | cooling/heating/standby 통합 weighting | ISO 16358 series |
| standby/off-mode seasonal energy | 현재 반환 스키마에 별도 보조전력 항목이 없다. | standby hours, thermostat-off hours, crankcase heater power | ISO 16358-3:2013 Chapter 5 |
| unverified country-specific exceptions | 공통 문서의 범위 밖이다. | region-specific notes and configuration | docs/DOCS_GUIDELINES.md |

## 13. References

| Source | Usage |
| --- | --- |
| ISO 16358-1:2013 Chapter 5, Chapter 6, Clause 6.4~6.7 | CSPF 계산 구조와 용량 제어 방식별 계산 흐름의 기준 |
| ISO 16358-2 | HSPF 계절 난방 부하, 계절 소비전력, auxiliary/make-up heat 구조 |
| UN AC proposal regarding ISO16358, Table 4 | ISO 16358-1:2013 참조 chapter와 clause 확인 |
| UN AC proposal regarding ISO16358, Annex 4 | outdoor temperature bin hours가 seasonal calculation에 쓰인다는 근거 |
| [ks_c_9306_notes.md](./regions/ks_c_9306/ks_c_9306_notes.md) | KS C 9306 region-specific CSPF/HSPF 계산 기준 |
| `core/calculator_iso16358.py` | 프로젝트 구현 매핑 |
| `data/region_configs/*.json` | 지역별 configuration schema |
