# ISO16358 Glossary

이 문서는 ISO 16358 공통 문서에서 사용하는 도메인 용어, 수식 기호, 코드 변수명, 데이터 위치의 단일 용어 사전이다. 설계 엔지니어가 보는 물리적 의미와 Coding Agent 및 SW 엔지니어가 확인해야 하는 변수/스키마 정보를 분리하여 관리한다.

국가별 특이 용어, 보정계수, region profile 용어는 각 region glossary에서 관리한다. 한국 KS C 9306 고유 용어는 [`regions/ks_c_9306/ks_c_9306_glossary.md`](./regions/ks_c_9306/ks_c_9306_glossary.md)를 참조한다.

---

## 1. HVAC 설계 엔지니어용

| 용어 및 기호 | 한글명 | 근거 | 정의 및 설계상 의미 |
| --- | --- | --- | --- |
| ISO 16358 | 계절 성능계수 산정 규격 | ISO 16358-1, ISO 16358-2, ISO 16358-3 | 에어컨 및 heat pump의 계절 효율을 온도 bin, building load, capacity/power curve를 이용해 계산하는 규격군이다. 단일 정격점이 아니라 계절 운전 영역 전체를 평가한다. |
| Cooling Seasonal Performance Factor (CSPF) | 냉방 계절 성능계수 | ISO 16358-1 | 계절 전체 냉방량을 계절 전체 소비전력량으로 나눈 냉방 효율 지표다. 중간 외기온 part-load 운전과 cycling 손실이 결과에 크게 반영될 수 있다. |
| Heating Seasonal Performance Factor (HSPF) | 난방 계절 성능계수 | ISO 16358-2 | 계절 전체 난방 부하량을 heat pump 소비전력량과 보조열 소비전력량의 합으로 나눈 난방 효율 지표다. 저온 능력, 제상 영향, 보조열 발생 여부가 중요하다. |
| Annual Performance Factor (APF) | 연간 성능계수 | ISO 16358-3 | 냉방과 난방 계절 성능을 연간 기준으로 통합해 보는 지표다. 냉방과 난방 중 어느 쪽이 더 중요한지는 지역 기후와 사용 패턴에 따라 달라진다. |
| seasonal cooling output | 계절 냉방량 | ISO 16358-1 | 각 냉방 bin에서 처리한 냉방량을 계절 시간으로 누적한 값이다. 냉방 output이 장비 capacity로 제한되는 구간이 있으면 단순 building load 합과 달라질 수 있다. |
| seasonal heat load | 계절 난방 부하량 | ISO 16358-2 | 각 난방 bin의 building load에 발생 시간을 곱해 누적한 값이다. HSPF의 numerator이며, heat pump와 보조열 중 어느 쪽이 처리했는지와 관계없이 전체 난방 요구량을 나타낸다. |
| seasonal electric power consumption | 계절 소비전력량 | ISO 16358-1, ISO 16358-2 | 각 bin의 운전 소비전력에 시간을 곱해 누적한 값이다. HSPF에서는 heat pump energy와 auxiliary energy가 모두 포함된다. |
| outdoor temperature bin, `t_j` | 외기온도 bin | ISO 16358-1, ISO 16358-2 | 계절 계산에서 사용하는 대표 외기온도다. 같은 장비라도 어떤 온도대에 시간이 많이 분포하는지에 따라 계절 효율이 달라진다. |
| bin hours, `n_j` | bin 발생 시간 | ISO 16358-1, ISO 16358-2 | 특정 외기온도가 계절 중 몇 시간 발생하는지를 나타내는 시간 가중치다. 시간이 많은 bin에서의 작은 power 차이가 최종 지표에 크게 누적된다. |
| building load | 건물 부하 | ISO 16358-1, ISO 16358-2 | 외기온도별로 장비가 처리해야 하는 냉방 또는 난방 부하다. capacity curve와 building load의 상대 위치가 cycling, part-load, shortage 여부를 결정한다. |
| cooling building load | 건물 냉방 부하 | ISO 16358-1 | 외기온도가 높아질수록 증가하는 냉방 요구량이다. 저부하 bin에서는 minimum capacity가 너무 높으면 cycling 손실이 발생할 수 있다. |
| heating building load | 건물 난방 부하 | ISO 16358-2 | 외기온도가 낮아질수록 증가하는 난방 요구량이다. heat pump capacity가 이 값을 따라가지 못하면 auxiliary heat가 발생한다. |
| 100 % load temperature | 100 % 부하 기준 온도 | ISO 16358-1, ISO 16358-2 | 기준 부하가 100 %가 되는 외기온도다. region별 load line을 정의하는 anchor로 쓰인다. |
| zero load temperature | 0 % 부하 기준 온도 | ISO 16358-1, ISO 16358-2 | 냉방 또는 난방 부하가 0으로 정의되는 외기온도다. load line의 기울기와 bin별 부하를 결정한다. |
| capacity | 냉난방 능력 | ISO 16358-1, ISO 16358-2 | 특정 시험 조건에서 장비가 처리할 수 있는 열량률이다. capacity가 building load보다 너무 크면 cycling 또는 part-load 손실이, 너무 작으면 output cap 또는 auxiliary heat가 발생한다. |
| electric power input | 소비전력 | ISO 16358-1, ISO 16358-2 | 특정 시험 조건에서 장비가 소비하는 전력이다. 계절 효율의 denominator를 직접 결정하므로 capacity만큼 중요하다. |
| measured point | 실측 시험점 | ISO 16358-1, ISO 16358-2 | 시험에서 직접 얻은 capacity와 power 쌍이다. 성능선의 anchor가 되므로 하나의 시험점이 넓은 온도 구간의 결과에 영향을 줄 수 있다. |
| default point / calculated point | 기본값 또는 계산 시험점 | ISO 16358-1, ISO 16358-2 | 직접 시험하지 않은 조건을 규격의 기본 계수 또는 보간식으로 산정한 point다. 실제 제품 성능을 대표하는 값이 아니라 규격 계산을 닫기 위한 값일 수 있다. |
| degradation coefficient, `C_D` | 성능 저하 계수 | ISO 16358-1, ISO 16358-2 | cycling 손실을 part-load factor에 반영하는 계수다. minimum capacity가 building load보다 큰 구간에서 계절 효율에 영향을 준다. |
| part-load factor, `PLF` | 부분부하 계수 | ISO 16358-1, ISO 16358-2 | 단속 운전 시 연속 운전 대비 효율 저하를 반영하는 계수다. 낮은 부하에서 compressor가 안정적으로 내려가지 못하면 불리해진다. |
| auxiliary heat / make-up heat | 보조열 / 보충열 | ISO 16358-2 | heat pump capacity가 heating building load보다 부족할 때 부족분을 보충하는 열이다. 보조열 energy는 HSPF denominator에 포함되어 지표를 낮춘다. |
| defrost | 제상 | ISO 16358-2 | 난방 중 실외 열교환기 착상으로 인한 성능 저하와 제상 운전 영향을 의미한다. capacity 감소와 power 증가가 동시에 나타날 수 있다. |
| frost region | 착상 영역 | ISO 16358-2 | 제상 또는 착상 보정이 적용되는 외기온 구간이다. 난방 효율 저하와 capacity shortage가 동시에 발생하기 쉬운 영역이다. |
| non-frost region | 무착상 영역 | ISO 16358-2 | 착상 보정이 적용되지 않는 외기온 구간이다. 난방 성능선은 주로 저온 및 표준 난방 anchor 사이의 보간으로 결정된다. |
| operating case | 운전 case | ISO 16358-1, ISO 16358-2 | bin별 building load가 minimum, intermediate, rated, maximum capacity curve 중 어디에 위치하는지에 따른 운전 분기다. 최종 power 산정 방식이 이 case에 따라 달라진다. |

---

## 2. Coding Agent & SW 엔지니어용

| 코드 변수명 또는 키 | 데이터 타입 | 위치 | 정의 및 구현상 주의 |
| --- | --- | --- | --- |
| `ISO16358Calculator` | class | `core/calculators/standards/iso16358.py` | ISO 16358 CSPF/HSPF 계산 entry class다. 공통 경로와 ISO profile 경로를 함께 포함하므로 수정 시 CSPF/HSPF regression을 모두 확인한다. |
| `calculate_cspf()` | method | `core/calculators/standards/iso16358.py` | CSPF 계산 entry point다. region config의 `points`, `derived_rules`, `bin_hours`, `Cd`, load line 설정을 사용한다. |
| `calculate_hspf()` | method | `core/calculators/standards/iso16358.py` | HSPF 계산 entry point다. ISO common profile, variable HSPF path, simple fallback path가 공존한다. KS C 9306 profile-specific HSPF는 `core/calculators/standards/ks_c9306.py`가 소유한다. |
| `cspf` | number | CSPF return dict | 최종 Cooling Seasonal Performance Factor다. `annual_cooling_kwh / annual_power_kwh` 구조로 계산된다. |
| `hspf` | number | HSPF return dict | 최종 Heating Seasonal Performance Factor다. `HSTL / HSEC` 구조로 계산된다. |
| `annual_cooling_kwh` | number | CSPF return dict | 계절 냉방량을 kWh 단위로 표시한 값이다. 내부 누적 Wh를 1000으로 나눈 값이다. |
| `annual_power_kwh` | number | CSPF return dict | 계절 냉방 소비전력량을 kWh 단위로 표시한 값이다. 내부 누적 Wh를 1000으로 나눈 값이다. |
| `HSTL` | number | HSPF return dict | Heating Seasonal Total Load. bin별 heating building load와 hours를 곱해 Wh 단위로 누적한 값이다. |
| `HSEC` | number | HSPF return dict | Heating Seasonal Energy Consumption. heat pump energy와 auxiliary energy를 Wh 단위로 합산한 값이다. |
| `heat_pump_energy` | number | HSPF return dict | heat pump가 소비한 계절 전력량이다. auxiliary energy와 분리해 추적한다. |
| `auxiliary_energy` | number | HSPF return dict | 보조열이 소비한 계절 전력량이다. `auxiliary_heat × hours / aux_cop` 구조를 유지해야 한다. |
| `aux_cop` | number | HSPF input | 보조열 COP다. 기본값은 1.0이며 0 이하 값은 ValueError 대상이다. |
| `bin_details` | list | return dict | bin별 온도, 시간, 부하, capacity, power, auxiliary, operating case를 추적하는 디버그/검증용 구조다. |
| `tj` | number | region config / bin detail | bin 대표 외기온도다. 냉방과 난방 모두 계절 loop의 기본 입력이다. |
| `nj` | number | region config / bin detail | bin 발생 시간이다. ISO16358 계열에서는 계절 합산에 absolute hours를 사용한다. |
| `bin_hours` | list | `data/region_configs/*.json` | CSPF 냉방 bin table이다. 각 row는 일반적으로 `tj`, `nj`를 포함한다. |
| `hspf_bin_hours` | list | `data/region_configs/*.json` | HSPF 난방 bin table이다. region-specific profile에서 사용한다. |
| `points` | dict | `data/region_configs/*.json` | 각 CSPF point가 measured인지 default인지 정의한다. |
| `derived_rules` | dict | `data/region_configs/*.json` | default point 생성에 사용하는 source point와 capacity/power factor를 정의한다. |
| `capacity` | number 또는 dict | measured input / resolved point | 시험점 또는 stage의 능력 값이다. 반드시 숫자 변환 가능하고 양수여야 한다. |
| `power` | number 또는 dict | measured input / resolved point | 시험점 또는 stage의 소비전력 값이다. 반드시 숫자 변환 가능하고 양수여야 한다. |
| `Cd` | number | region config / HSPF correction input | PLF 계산에 사용하는 degradation coefficient다. 보통 0 이상 1 미만으로 검증한다. |
| `PLF` | number | internal / bin detail | part-load factor다. cyclic 구간에서 power 보정에 사용한다. |
| `building_load_source` | string | region config | CSPF 기준 부하를 measured reference에서 가져올지 declared capacity에서 가져올지 결정한다. |
| `reference_point` | string | region config | measured 기준 부하를 사용할 때 reference capacity로 사용할 point key다. |
| `t_100_load` | number | region config | CSPF load line의 100 % load 기준 온도다. |
| `t_0_load` | number | region config | CSPF load line의 zero-load 기준 온도다. |
| `round_test_values` | bool | region config | region-specific 시험값 반올림 적용 여부다. 한국 KS C 9306에서는 true다. |
| `rounding_method` | string | region config | 시험값 반올림 방식이다. Python 기본 `round()`와 HALF_UP의 차이에 주의한다. |
| `power_interpolation_method` | string | region config | 중간 용량 범위에서 power를 산정하는 방식이다. region-specific method가 common region으로 누출되지 않게 한다. |
| `hspf.profile` | string | region config | HSPF region/profile 경로를 선택한다. KS C 9306 profile이면 입력 누락 시 common fallback을 허용하지 않는다. |
| `hspf.required_points` | dict | region config | HSPF profile에서 필수로 요구하는 시험점 stage와 온도를 정의한다. |
| `hspf.optional_points` | dict | region config | HSPF profile에서 선택적으로 입력될 수 있는 stage와 온도를 정의한다. |
| `hspf.derived_rules` | dict | region config | HSPF stage별 low-temperature point를 계산하기 위한 factor를 정의한다. |
| `hspf.correction` | dict | region config | HSPF defrost/no-frost correction factor와 Cd 기본값을 정의한다. |
| `hspf.load_line.source` | string | region config | HSPF heating load line의 기준 capacity source다. 지원 값은 `rated_heating_capacity`, `rated_cooling_capacity`, `declared_capacity`다. |
| `hspf.load_line.zero_load_temp` | number | region config | HSPF heating load가 0이 되는 외기온도다. |
| `hspf.load_line.full_load_temp` | number | region config | HSPF heating load가 기준값이 되는 외기온도다. |
| `hspf.load_line.rated_capacity_factor` | number | region config | 기준 capacity에 곱하는 load line factor다. 한국 KS C 9306은 공식 계산 시트 동작 기준 0.82를 사용한다. |
| `operating_case` | string | bin detail | cyclic, intermediate, rated, maximum_shortage 등 bin별 운전 분기 결과다. case 이름은 테스트와 디버깅에서 사용되므로 임의 변경하지 않는다. |
| `load` / `heating_load` | number | HSPF bin input | HSPF bin에 직접 지정된 부하 값이다. 없으면 profile load line이 사용될 수 있다. |
| `declared_capacity` | number | caller input | 일부 region의 CSPF building load 기준 capacity다. 한국 CSPF에서는 ROUND_HALF_UP 적용 대상이다. |
| `rated_heating_capacity` | number | HSPF input | 일부 HSPF region profile에서 heating load line 기준으로 사용할 수 있는 capacity input이다. |
| `rated_cooling_capacity` | number | HSPF input | 일부 HSPF region profile에서 heating load line 기준으로 사용할 수 있는 cooling capacity input이다. 현재 region별 근거 확인 없이는 공통 fallback으로 쓰지 않는다. |

---

## 3. Data Location Summary

| Data | Location | Owner document |
| --- | --- | --- |
| ISO 16358 공통 계산 흐름 | `core/calculators/standards/iso16358.py` | [`iso16358_notes.md`](./iso16358_notes.md) |
| ISO 16358 공통 구현 주의사항 | `docs/iso16358/iso16358_dev_notes.md` | [`iso16358_dev_notes.md`](./iso16358_dev_notes.md) |
| ISO 16358 공통 설계 인사이트 | `docs/iso16358/iso16358_design_notes.md` | [`iso16358_design_notes.md`](./iso16358_design_notes.md) |
| ISO 16358 공통 용어 | `docs/iso16358/iso16358_glossary.md` | this document |
| 지역별 설정 | `data/region_configs/*.json` | each region notes |
| 한국 KS 확장 용어 | `docs/iso16358/regions/ks_c_9306/ks_c_9306_glossary.md` | [`ks_c_9306_glossary.md`](./regions/ks_c_9306/ks_c_9306_glossary.md) |
