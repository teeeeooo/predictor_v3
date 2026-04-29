# ISO16358 Glossary

## 1. Purpose

이 문서는 ISO 16358 공통 엔진에서 사용하는 용어, 물리적 의미, 소프트웨어 변수 매핑, 데이터 위치를 관리하는 단일 용어 사전이다. 국가별 특이 용어는 region glossary에서 관리하고, 이 문서에는 공통 용어만 둔다.

## 2. Glossary

| Term | Korean name | Physical meaning | SW mapping | Data location | Reference |
| --- | --- | --- | --- | --- | --- |
| Cooling Seasonal Performance Factor (CSPF) | 냉방 계절 성능계수 | 계절 전체 냉방량을 계절 전체 소비전력으로 나눈 효율 지표이다. | `cspf` | `calculate_cspf` return | ISO 16358-1:2013 Chapter 5 |
| seasonal cooling output | 계절 냉방량 | 각 bin에서 처리한 냉방 부하에 발생 시간을 곱해 누적한 값이다. | `cstl`, `annual_cooling_kwh` | internal accumulation, return | ISO 16358-1:2013 Chapter 5 |
| seasonal electric power | 계절 소비전력량 | 각 bin에서 필요한 소비전력에 발생 시간을 곱해 누적한 값이다. | `csec`, `annual_power_kwh` | internal accumulation, return | ISO 16358-1:2013 Chapter 5 |
| outdoor temperature bin | 외기온도 bin | 계절 계산에서 특정 외기온도와 그 발생 시간을 묶은 단위이다. | `tj`, `nj` | `data/region_configs/*.json` |
| bin hours | bin 발생 시간 | 특정 외기온도가 계절 중 몇 시간 발생하는지를 나타낸다. | `bin_hours` | `data/region_configs/*.json` | UN AC proposal Annex 4 |
| building load | 건물 냉방 부하 | 외기온도에 따라 요구되는 냉방 능력이다. | `Lc`, `L_c_ref` | internal calculation | ISO 16358-1:2013 Chapter 6 |
| 100% load temperature | 100% 부하 기준 온도 | 기준 냉방 부하가 100%가 되는 외기온도이다. | `t_100_load` | region configuration |
| zero load temperature | 0% 부하 기준 온도 | 냉방 부하가 0이 되는 외기온도이다. | `t_0_load` | region configuration |
| measured point | 실측 시험점 | 시험에서 직접 얻은 capacity와 power 쌍이다. | `points[point] = "measure"` | region configuration and caller input |
| default point | 파생 시험점 | measured point에 factor를 적용해 만든 계산용 point이다. | `points[point] = "default"` | region configuration |
| derived rule | 파생 규칙 | default point를 만들기 위한 source point와 factor 정의이다. | `derived_rules` | region configuration |
| cooling capacity | 냉방 능력 | 지정 조건에서 장비가 처리할 수 있는 냉방량률이다. | `capacity` | measured input, resolved points |
| electric power | 소비전력 | 지정 조건에서 장비가 소비하는 전력이다. | `power` | measured input, resolved points |
| load type | 부하 타입 | full, half, min 등 시험점의 용량 수준을 나타낸다. | point suffix | point key |
| degradation coefficient | 성능 저하 계수 | cycling 손실을 PLF에 반영하는 계수이다. | `Cd` | region configuration | ISO 16358-1:2013 Chapter 6 |
| part-load factor | 부분부하 계수 | 요구 부하가 최저 용량보다 낮을 때 cycling 손실을 반영하는 계수이다. | `PLF` | internal calculation | ISO 16358-1:2013 Chapter 6 |
| building load source | 부하 기준 출처 | 기준 부하를 measured reference에서 가져올지 declared capacity에서 가져올지 정한다. | `building_load_source` | region configuration |
| reference point | 기준 시험점 | measured 기준 부하를 사용할 때 L_c_ref의 출처가 되는 point이다. | `reference_point` | region configuration |
| power interpolation method | 소비전력 보간 방식 | 중간 용량 범위에서 power를 계산하는 방법이다. | `power_interpolation_method` | region configuration |

## 3. Data Location Summary

| Data | Location | Owner document |
| --- | --- | --- |
| 공통 계산 흐름 | `core/calculator_iso16358.py` | [iso16358_notes.md](./iso16358_notes.md) |
| 공통 용어 | `docs/iso16358/iso16358_glossary.md` | this document |
| 지역별 설정 | `data/region_configs/*.json` | each region notes |
| 한국 KS 확장 용어 | `docs/iso16358/regions/ks_c_9306/ks_c_9306_glossary.md` | KS C 9306 region glossary |
