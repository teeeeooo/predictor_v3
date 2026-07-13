# KS C 9306 Notes

## 1. Overview

KS C 9306 문서는 ISO 16358 공통 CSPF/HSPF 엔진을 한국 냉난방 효율 규격에 맞게 확장하는 region-specific 기준 문서이다. 공통 계산 구조는 [../../iso16358_notes.md](../../iso16358_notes.md)를 참조하며, 이 문서는 한국 규칙, 입력/출력 차이, 파생 규칙, 검증 샘플만 기록한다.

근거: KS C 9306:2017 Annex E, Table E.2, Equation E.1.4. 프로젝트 해석: `data/region_configs/korea.json`은 Table E.2 bin-hour와 Equation E.1.4의 `t_0_load = 23°C` 기준을 한국 region 설정으로 반영한다.

## 2. Scope

| 항목 | KS C 9306 region rule | ISO common reference |
| --- | --- | --- |
| 기준 부하 | declared capacity 기반 BL(tj) | [ISO CSPF current status](../../iso16358_notes.md#3-cspf-current-status) |
| 시험값 처리 | capacity, power, declared capacity에 ROUND_HALF_UP 정수 반올림 적용 | [ISO input schema](../../iso16358_notes.md#7-input-schema) |
| 시험점 구성 | 35_full, 35_half, 29_min은 measured point | [ISO CSPF current status](../../iso16358_notes.md#3-cspf-current-status) |
| 파생 규칙 | 35_min, 29_full, 29_half를 factor로 생성 | [ISO formula mapping](../../iso16358_notes.md#9-formula-mapping) |
| 중간 부하 전력 | `power_interpolation_method = ks_intersection` | [ISO code mapping](../../iso16358_notes.md#10-code-mapping) |
| bin-hour | KS C 9306 한국 냉방 bin-hour | ISO 공통 bin accumulation |
| HSPF profile | `hspf.profile = ks_c_9306_hspf` | [ISO HSPF current status](../../iso16358_notes.md#4-hspf-current-status) |
| HSPF bin-hour | KS C 9306 한국 난방 31-bin, `nj` 합계 2849 h | ISO HSPF seasonal accumulation |
| HSPF load line | `hspf.load_line.source = rated_cooling_capacity`, factor `0.82` | KS HSPF profile path |

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
| 시험값 ROUND_HALF_UP | KS C 9306:2017 Annex E | measured capacity/power와 declared capacity를 정수화한다. | `_ks_c9306/input.py`의 `_prepare_measured_inputs`, `_round_test_value` |
| 29/35°C 파생 규칙 | KS C 9306:2017 Annex E, Table E.2 context | configuration factor로 default point를 생성한다. | `_ks_c9306/cspf_points.py`의 `_resolve_ks_cspf_points` |
| `ks_intersection` power interpolation | KS C 9306:2017 Annex E | load line과 performance line의 교점 기반 전력선을 사용한다. | `_ks_c9306/cspf_performance.py`의 `_ks_cspf_intersection_power` |
| BL > max_cap 처리 | ISO common branch reused by KS | output을 highest capacity로 제한하고 power는 highest power를 사용한다. | `calculate_cspf` |

## 6.1 KS C 9306 CSPF Status

| Item | Current status |
| --- | --- |
| Golden result | Korea KS C 9306 CSPF `6.504` pass |
| Rounding | measured capacity, measured power, declared capacity, derived point에 ROUND_HALF_UP 적용 |
| Building load | declared capacity 기반 CSPF BL 사용 |
| Intermediate power | `ks_intersection` power interpolation 사용 |

## 6.2 KS C 9306 HSPF Status

KS C 9306 HSPF profile은 구현되어 있다. required/optional point 정책은 아래와 같다.

| Temperature | Required points | Optional points |
| --- | --- | --- |
| 7°C | `full`, `half`, `min` | 없음 |
| 2°C | `defrost` | `full`, `half`, `min` |
| -7°C | `max` | `full`, `half`, `min` |

`full`, `half`, `min` stage의 2°C 및 -7°C 값은 profile helper에서 파생 가능하다. `max.-7`과 `max.def`는 maximum curve anchor이므로 required point이다.

## 6.3 HSPF 31-Bin Table

`data/region_configs/korea.json`의 `hspf_bin_hours`는 KS C 9306 HSPF 실제 31-bin을 사용한다.

| Rule | Current value |
| --- | --- |
| temperature range | -15°C to 15°C |
| bin count | 31 |
| `nj` total | 2849 h |
| bin load fields | `load` 또는 `heating_load`를 넣지 않음 |
| load source | `hspf.load_line`에서 bin별 BL(tj)를 계산 |

production `hspf_bin_hours`에는 golden/sample/test fixture 전용 2-bin 값을 넣지 않는다.

## 6.4 HSPF Load Line

현재 `korea.json`의 KS C 9306 HSPF load line:

| Field | Value |
| --- | --- |
| `source` | `rated_cooling_capacity` |
| `rated_capacity_factor` | `0.82` |
| `full_load_temp` | `0.0` |
| `zero_load_temp` | `16.0` |

규격 문구의 `BLc(35) × 0.82` cooling reference를 따른다. 현재 구현은 `rated_cooling_capacity`를 필수 입력으로 요구하며, 0°C 난방 부하는 `rated_cooling_capacity × 0.82`로 계산한다.

## 6.5 HSPF 31-Bin Sanity Output

아래 값은 현재 31-bin production configuration과 KS HSPF profile implementation의 sanity 참고값이다. official production golden으로 고정하지 않는다. 공식 31-bin golden으로 확정하려면 bin별 공식 계산표가 추가로 필요하다.

| Output | Current sanity value |
| --- | --- |
| HSPF | 3.9589527754156744 |
| HSTL | 5526621.7391304355 |
| HSEC | 1395980.7182974447 |
| heat_pump_energy | 1395888.4042877827 |
| auxiliary_energy | 92.31400966183719 |
| bins | 31 |

## 7. CSPF Source Clause Archive

이 섹션은 루트의 `KS_C_9306.pdf` 스캔본을 OCR로 확인한 CSPF 관련 조항 색인이다. OCR은 표와 수식 기호를 오인식할 수 있으므로, 수식의 최종 구현 전에는 반드시 PDF 원문 이미지를 함께 대조해야 한다.

| Standard item | Reference | OCR-confirmed role | Project interpretation |
| --- | --- | --- | --- |
| 냉방/난방 기간 효율 시험 항목 | KS C 9306:2017 Table E.1 | 냉방 표준 최소, 중간, 정격, 저온 능력 및 전력 시험 항목을 제시한다. | CSPF measured point와 derived point 구성을 확인하는 상위 시험 조건 표로 사용한다. |
| CSPF definition | KS C 9306:2017 Clause E.3.1, Equation E.1.1, Equation E.1.2, Equation E.1.3 | 냉방 기간 총 냉방량 합계, 냉방 기간 총 냉방 소비 전력량 합계, CSPF 비율 구조를 정의한다. | 계절 냉방량과 계절 전력량을 Wh 단위로 합산한 뒤 CSPF를 산정한다. |
| 냉방 building load | KS C 9306:2017 Equation E.1.4 | 외기온도별 건물 냉방 부하선을 정의한다. OCR에서 35°C 기준 부하가 정격 표시 냉방 능력과 같은 값이라는 설명이 확인된다. | 한국 region은 measured reference가 아니라 declared capacity를 `BL(t_j)` 기준으로 사용한다. |
| 냉방 load ratio | KS C 9306:2017 Equation E.1.5 | 온도별 건물 부하와 냉방 능력의 비 `X(t_j)`를 정의하고, 능력이 부하보다 작을 때 `X = 1`로 제한하는 조건이 확인된다. | cycling 보정에 들어가는 load ratio는 0~1 범위로 제한한다. |
| 냉방 PLF | KS C 9306:2017 Equation E.1.6 | 단속 운전시 효율과 연속 운전시 효율의 비 `PLF(t_j)`를 효율 저하 계수 `C_D`로 계산한다. | 최소 운전 능력이 building load보다 클 때만 PLF를 적용한다. |
| 냉방 bin-hour | KS C 9306:2017 Table E.2 | 냉방 기간 중 냉방을 필요로 하는 각 온도의 발생 시간을 제공한다. | `data/region_configs/korea.json`의 `bin_hours`와 대조해야 하는 canonical source다. |
| 냉방 보정/저하 계수 | KS C 9306:2017 Table E.3 | 냉방 능력, 소비 전력 보정 계수 및 효율 저하 계수를 제공한다. | 29°C/35°C 파생 규칙과 `Cd` 값의 근거 표로 관리한다. |
| 냉방 3점식 운전점 선택 | KS C 9306:2017 Clause E.3.1.5, Equation E.1.18~E.1.26 | 최소, 중간, 정격 운전 능력 사이에서 building load 위치에 따라 소비전력을 산정하는 분기 구조가 확인된다. | 한국 CSPF의 `ks_intersection` 중간 부하 전력 산정은 이 구간을 원문 이미지와 대조해 유지한다. |
| 냉방 정격 초과 처리 | KS C 9306:2017 Clause E.3.1.5, Equation E.1.19, Equation E.1.22 | building load가 정격 운전 능력보다 큰 경우 정격 운전 능력과 정격 운전 소비 전력으로 처리하는 설명이 확인된다. | 최고 capacity 초과 시 cooling output을 장비 capacity로 제한하고 power는 해당 운전점 power를 사용한다. |

## 8. HSPF Source Clause Archive

이 섹션은 ISO 16358-2 기반 HSPF 구현을 위한 KS C 9306 Annex E 조항 색인이다. 현재 OCR 텍스트는 `HSPF`를 `15마`처럼 오인식하고, 수식 기호도 일부 깨진다. 따라서 아래 표는 구현 근거 위치와 계산 역할을 보존하는 archive이며, 수식 계수와 기호는 PDF 원문 이미지로 최종 확인해야 한다.

| Standard item | Reference | OCR-confirmed role | Project interpretation |
| --- | --- | --- | --- |
| HSPF definition | KS C 9306:2017 Clause E.3.2, Equation E.2.1, Equation E.2.2, Equation E.2.3 | 난방 기간 총 난방량 합계, 난방 기간 총 난방 소비 전력량 합계, HSPF 비율 구조를 정의한다. | `HSTL / HSEC` 구조는 CSPF와 동일한 계절 합산 구조이며, 단위는 Wh로 관리한다. |
| 난방 building load | KS C 9306:2017 Equation E.2.4 | 난방 부하는 냉방 기간 효율 산정 시 적용한 방면적과 동일한 방에서 평가하기 위해 냉방 부하에 대한 고정비를 적용한다고 설명한다. OCR에서 정격 냉방 표준 능력과 `0.82` 계수가 확인된다. | golden HSTL이 이미 맞는 경우 building load helper는 임의 변경하지 않는다. |
| 난방 load ratio | KS C 9306:2017 Equation E.2.5 | 온도별 건물 난방 부하와 난방 능력의 비를 정의하고, 능력이 부하보다 작을 때 `X = 1`로 제한하는 조건이 확인된다. | cyclic 또는 part-load 보정에 들어가는 ratio는 0~1 범위 제한이 필요하다. |
| 난방 PLF | KS C 9306:2017 Equation E.2.6 | 단속 운전시 효율과 연속 운전시 효율의 비를 효율 저하 계수로 계산한다. | building load가 최소 운전 능력 이하인 cyclic minimum 구간에만 적용한다. |
| 보조 전열 장치 | KS C 9306:2017 Equation E.2.7 | 건물 부하에 대해 에어컨 난방 능력 부족을 보충하기 위한 전열 장치 소비 전력량을 정의한다. OCR에서 `BL(t_j) - capacity(t_j)` 형태와 보조히터 관련 설명이 확인된다. | heat pump capacity가 building load보다 작으면 부족분을 auxiliary energy로 합산한다. |
| 난방 bin-hour | KS C 9306:2017 Table E.4 | 난방 기간 중 난방을 필요로 하는 각 온도의 발생 시간을 제공한다. | ISO16358-2/KS HSPF region data를 만들 때 absolute bin hours의 근거 표로 사용한다. |
| 난방 보정/저하 계수 | KS C 9306:2017 Table E.5 | 난방 능력, 소비 전력 보정 계수 및 효율 저하 계수를 제공한다. | 온도별 고단/중간/최소 운전점 보정과 `C_D` 확인의 근거 표로 사용한다. |
| 착상/무착상 구간 | KS C 9306:2017 Clause E.3.2.3, Equation E.2.20, Equation E.2.21 | 가변 용량형 에어컨에서 최소 운전 난방 능력을 무착상 영역과 착상 영역으로 나누는 구조가 확인된다. 원문 이미지에서 착상 영역은 `-7.0°C < t_j < 5.5°C`, 무착상 영역은 `t_j <= -7.0°C` 또는 `5.5°C <= t_j`로 확인된다. | defrost 영향이 포함된 구간과 low-temperature 구간은 별도 성능선으로 분리해야 한다. |
| 정격/중간/최대 운전 능력선 | KS C 9306:2017 Clause E.3.2.3, Equation E.2.22~E.2.26 | 정격, 중간, 최대 운전 난방 능력식을 온도 구간별로 정의하는 식 번호가 확인된다. | high-stage, half-stage, min-stage curve를 온도별로 만든 뒤 building load 위치에 따라 운전점을 선택한다. |
| 최소/정격/중간/최대 소비전력선 | KS C 9306:2017 Clause E.3.2.3, Equation E.2.27~E.2.33 | 최소, 정격, 중간, 최대 운전 난방 소비전력식을 정의하는 식 번호가 확인된다. | capacity curve와 power curve는 같은 온도 구간 기준으로 보간/외삽한다. |
| 3점식 운전점 선택 | KS C 9306:2017 Clause E.3.2.5, Equation E.2.36~E.2.40 | building load가 최소-중간, 중간-정격, 정격-최대 능력 사이에 위치할 때 소비전력을 보간하는 분기 구조가 확인된다. Equation E.2.36은 `P_h(t_j) = P_h23(t_j) = P_h3(t_g) + (P_h2(t_b) - P_h3(t_g)) * (t_j - t_g) / (t_b - t_g)`로 확인했다. | variable-capacity HSPF는 load 위치에 따라 cyclic minimum, min-half, half-rated, rated-max, max shortage 분기를 가져야 한다. |
| 최대 능력 부족 처리 | KS C 9306:2017 Clause E.3.2.5, Equation E.2.26, Equation E.2.33 | building load가 최대 운전 능력보다 큰 경우 최대 운전 능력과 최대 운전 소비전력으로 처리하는 설명이 확인된다. | 부족분은 auxiliary heat/energy로 별도 합산한다. |

## 9. OCR Verification Notes

| Item | Status | Notes |
| --- | --- | --- |
| OCR engine | Verified | `tesseract 5.5.2`와 `kor+eng` 언어 데이터로 `KS_C_9306.pdf` 17페이지 스캔본을 확인했다. |
| Text reliability | Partial | 한글 문장은 대체로 읽히지만 `CSPF`, `HSPF`, 수식 기호, 첨자, 표 구조는 오인식이 발생한다. |
| Formula reliability | Requires image check | Equation E.1.x와 E.2.x의 번호와 역할은 확인 가능하지만, 실제 수식 계수와 기호는 PDF 이미지 원문을 기준으로 재확인해야 한다. |
| Implementation usage | Archive first | 이 문서는 구현 전 근거 위치를 빠르게 찾기 위한 archive다. 계산 로직 변경 시에는 해당 Equation/Table의 원문 이미지를 확인한 뒤 dev notes와 테스트에 반영한다. |

## 10. Golden Sample Verification

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

## 11. References

| Source | Usage |
| --- | --- |
| KS C 9306:2017 Annex E | 한국 CSPF/HSPF 계산 조건 |
| KS C 9306:2017 Table E.1 | 냉방 및 난방 기간 효율 산출 시험 항목 |
| KS C 9306:2017 Table E.2 | 한국 냉방 bin-hour와 시험 조건 맥락 |
| KS C 9306:2017 Table E.3 | 냉방 보정 계수 및 효율 저하 계수 |
| KS C 9306:2017 Table E.4 | 난방 bin-hour와 시험 조건 맥락 |
| KS C 9306:2017 Table E.5 | 난방 보정 계수 및 효율 저하 계수 |
| KS C 9306:2017 Equation E.1.4 | declared capacity 기반 BL(tj), `t_0_load = 23°C` |
| KS C 9306:2017 Equation E.2.1~E.2.7 | HSPF 계절 합산, building load, PLF, auxiliary energy 구조 |
| KS C 9306:2017 Equation E.2.20~E.2.40 | 가변 용량형 HSPF 성능선과 운전점 선택 구조 |
| `KS_C_9306.pdf` | 로컬 스캔본 OCR 확인 source |
| `data/region_configs/korea.json` | 한국 region configuration SSOT |
| `core/calculators/standards/ks_c9306.py` | KS C 9306 계산 구현 mapping |
