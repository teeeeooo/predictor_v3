# KS C 9306 Notes

## 1. Overview

KS C 9306 문서는 ISO 16358 공통 CSPF 엔진을 한국 냉방 효율 규격에 맞게 확장하는 region-specific 기준 문서이다. 공통 계산 구조는 [../../iso16358_notes.md](../../iso16358_notes.md)를 참조하며, 이 문서는 한국 규칙, 입력/출력 차이, 파생 규칙, 검증 샘플만 기록한다.

근거: KS C 9306:2017 Annex E, Table E.2, Equation E.1.4. 프로젝트 해석: `data/region_configs/korea.json`은 Table E.2 bin-hour와 Equation E.1.4의 `t_0_load = 23°C` 기준을 한국 region 설정으로 반영한다.

## 2. Scope

| 항목 | KS C 9306 region rule | ISO common reference |
| --- | --- | --- |
| 기준 부하 | declared capacity 기반 BL(tj) | [ISO calculation structure](../../iso16358_notes.md#3-calculation-structure) |
| 시험값 처리 | capacity, power, declared capacity에 ROUND_HALF_UP 정수 반올림 적용 | [ISO input schema](../../iso16358_notes.md#4-input-schema) |
| 시험점 구성 | 35_full, 35_half, 29_min은 measured point | [ISO measured/default point resolution](../../iso16358_notes.md#3-calculation-structure) |
| 파생 규칙 | 35_min, 29_full, 29_half를 factor로 생성 | [ISO formula mapping](../../iso16358_notes.md#6-formula-mapping) |
| 중간 부하 전력 | `power_interpolation_method = ks_intersection` | [ISO code mapping](../../iso16358_notes.md#7-code-mapping) |
| bin-hour | KS C 9306 한국 냉방 bin-hour | ISO 공통 bin accumulation |

## 3. KS Input Schema

| Field | Meaning | Unit | Required | Validation rule | Data location |
| --- | --- | --- | --- | --- | --- |
| `declared_capacity` | 표기 정격 냉방 능력 | W | Yes | 양수이며 ROUND_HALF_UP으로 정수화된다. | caller input |
| `35_full.capacity` | 35°C full capacity 시험값 | W | Yes | ROUND_HALF_UP 적용 후 계산에 사용한다. | measured input |
| `35_full.power` | 35°C full power 시험값 | W | Yes | ROUND_HALF_UP 적용 후 계산에 사용한다. | measured input |
| `35_half.capacity` | 35°C half capacity 시험값 | W | Yes | ROUND_HALF_UP 적용 후 계산에 사용한다. | measured input |
| `35_half.power` | 35°C half power 시험값 | W | Yes | ROUND_HALF_UP 적용 후 계산에 사용한다. | measured input |
| `29_min.capacity` | 29°C minimum capacity 시험값 | W | Yes | ROUND_HALF_UP 적용 후 계산에 사용한다. | measured input |
| `29_min.power` | 29°C minimum power 시험값 | W | Yes | ROUND_HALF_UP 적용 후 계산에 사용한다. | measured input |

## 4. Region Configuration

| Key | Value | Meaning | Reference |
| --- | --- | --- | --- |
| `standard` | `KS C 9306` | 한국 region 식별자 | KS C 9306:2017 |
| `t_100_load` | 35.0 | 100% cooling load 기준 온도 | KS C 9306:2017 Annex E |
| `t_0_load` | 23.0 | BL(tj) zero-load 기준 온도 | KS C 9306:2017 Equation E.1.4 |
| `Cd` | 0.25 | PLF 계산의 degradation coefficient | KS C 9306:2017 Annex E |
| `building_load_source` | `declared` | BL(tj)의 L_c_ref는 declared capacity이다. | KS C 9306:2017 Equation E.1.4 |
| `round_test_values` | true | 시험값 정수 반올림을 적용한다. | KS C 9306:2017 Annex E |
| `rounding_method` | `nearest_integer_half_up` | Python bankers rounding을 사용하지 않는다. | Project implementation |
| `power_interpolation_method` | `ks_intersection` | 한국 중간 부하 전력 산정 방식이다. | KS C 9306:2017 Annex E |

## 5. Derived Point Rules

| Derived point | Source | Capacity factor | Power factor | Meaning |
| --- | --- | --- | --- | --- |
| `35_min` | `29_min` | 0.9285 | 1.1574 | 29°C minimum 시험값에서 35°C minimum point를 파생한다. |
| `29_full` | `35_full` | 1.077 | 0.864 | 35°C full 시험값에서 29°C full point를 파생한다. |
| `29_half` | `35_half` | 1.077 | 0.864 | 35°C half 시험값에서 29°C half point를 파생한다. |

프로젝트 해석: 파생된 capacity와 power도 `round_test_values = true`이면 ROUND_HALF_UP 정수 반올림을 거친다.

## 6. Calculation Mapping

| KS item | Standard reference | Project behavior | Code mapping |
| --- | --- | --- | --- |
| declared capacity 기반 BL(tj) | KS C 9306:2017 Equation E.1.4 | `declared_capacity`를 L_c_ref로 사용한다. | `calculate_cspf` |
| 시험값 ROUND_HALF_UP | KS C 9306:2017 Annex E | measured capacity/power와 declared capacity를 정수화한다. | `_prepare_measured_inputs`, `_round_test_value` |
| 29/35°C 파생 규칙 | KS C 9306:2017 Annex E, Table E.2 context | configuration factor로 default point를 생성한다. | `resolve_points` |
| `ks_intersection` power interpolation | KS C 9306:2017 Annex E | load line과 performance line의 교점 기반 전력선을 사용한다. | `_ks_intersection_power` |
| BL > max_cap 처리 | ISO common branch reused by KS | output을 highest capacity로 제한하고 power는 highest power를 사용한다. | `calculate_cspf` |

## 7. Golden Sample Verification

| Input | Value |
| --- | --- |
| declared_capacity | 6000 W |
| 35_full | 6035.8 W / 1641.4 W |
| 35_half | 3420.4 W / 679.4 W |
| 29_min | 1759.6 W / 201.7 W |

| Output | Expected | Actual | Tolerance | Result |
| --- | --- | --- | --- | --- |
| CSPF | 6.504 | 6.504 | 0.001 | Pass |
| cooling_output | 1,943,798 Wh | 1,943,798 Wh | 1 Wh | Pass |
| cooling_power | approximately 298,852 Wh | 298,852 Wh | 1 Wh | Pass |

검증 명령 결과: `{'cspf': 6.504, 'annual_cooling_kwh': 1943.798, 'annual_power_kwh': 298.852}`.

## 8. References

| Source | Usage |
| --- | --- |
| KS C 9306:2017 Annex E | 한국 CSPF 계산 조건 |
| KS C 9306:2017 Table E.2 | 한국 냉방 bin-hour와 시험 조건 맥락 |
| KS C 9306:2017 Equation E.1.4 | declared capacity 기반 BL(tj), `t_0_load = 23°C` |
| `data/region_configs/korea.json` | 한국 region configuration SSOT |
| `core/calculator_iso16358.py` | 계산 구현 mapping |
