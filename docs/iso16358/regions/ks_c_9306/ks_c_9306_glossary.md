# KS C 9306 Glossary

## 1. Purpose

이 문서는 KS C 9306 region에서만 사용하는 용어, 물리적 의미, 소프트웨어 변수 매핑, 데이터 위치를 관리하는 단일 용어 사전이다. ISO 공통 용어는 [../../iso16358_glossary.md](../../iso16358_glossary.md)를 참조하고 이 문서에 중복 정의하지 않는다.

## 2. KS-specific Glossary

| Term | Korean name | Physical meaning | SW mapping | Data location | Reference |
| --- | --- | --- | --- | --- | --- |
| KS C 9306 | 한국 에어컨 성능 규격 | 한국 냉방 CSPF 계산의 region-specific 기준이다. | `standard = "KS C 9306"` | `data/region_configs/korea.json` | KS C 9306:2017 |
| declared capacity | 표기 정격 냉방 능력 | 한국 BL(tj) 계산의 기준이 되는 제조사 표기 능력이다. | `declared_capacity` | caller input | KS C 9306:2017 Equation E.1.4 |
| declared capacity load line | 표기 능력 기반 부하선 | `t_0_load = 23°C`와 `t_100_load = 35°C`를 잇는 한국 냉방 부하선이다. | `L_c_ref`, `Lc` | internal calculation | KS C 9306:2017 Equation E.1.4 |
| round test values | 시험값 반올림 | capacity와 power 시험값을 정수로 HALF_UP 반올림하는 규칙이다. | `round_test_values = true` | `data/region_configs/korea.json` |
| nearest integer half up | 0.5 올림 정수 반올림 | bankers rounding을 피하고 시험값 반올림을 일관되게 만든다. | `rounding_method = "nearest_integer_half_up"` | `data/region_configs/korea.json` |
| 35_full | 35°C full 시험점 | 고온 full 운전의 capacity/power 기준점이다. | `35_full` | measured input |
| 35_half | 35°C half 시험점 | 고온 중간 운전의 capacity/power 기준점이다. | `35_half` | measured input |
| 29_min | 29°C minimum 시험점 | 낮은 온도 minimum 운전의 capacity/power 기준점이다. | `29_min` | measured input |
| 35_min | 35°C minimum 파생점 | 29°C minimum 시험점에서 factor로 산정하는 고온 minimum 운전점이다. | `35_min` | `derived_rules` |
| 29_full | 29°C full 파생점 | 35°C full 시험점에서 factor로 산정하는 저온 full 운전점이다. | `29_full` | `derived_rules` |
| 29_half | 29°C half 파생점 | 35°C half 시험점에서 factor로 산정하는 저온 half 운전점이다. | `29_half` | `derived_rules` |
| ks_intersection | KS 교점 기반 전력 보간 | building load line과 운전 성능선의 교점 전력을 이용하는 한국 전용 중간 부하 전력 산정 방식이다. | `power_interpolation_method = "ks_intersection"` | `data/region_configs/korea.json` |
| ta | minimum 교점 온도 | minimum 운전선과 building load line의 낮은 부하 쪽 교점으로 설계 판단에 쓰인다. | design concept | design notes |
| tb | 중간 기준 온도 | minimum 교점과 고온 기준점 사이에서 half capacity target을 판단하는 설계 기준 온도이다. | design concept | design notes |
| tc | half target 교점 온도 | half 운전선과 building load line의 관계를 판단하는 설계 기준 온도이다. | design concept | design notes |
| Korean cooling bin hours | 한국 냉방 bin-hour | 한국 냉방 계절에서 각 외기온도가 발생하는 시간 분포이다. | `bin_hours` | `data/region_configs/korea.json` | KS C 9306:2017 Table E.2 |
| half capacity recommendation | 35°C half capacity 추천 | 35°C half 시험 목표를 검토하기 위한 보조 계산이다. CSPF 본계산 입력을 자동 대체하지 않는다. | `half_capacity_recommendation` | `data/region_configs/korea.json` |

## 3. Data Location Summary

| Data | Location | Owner document |
| --- | --- | --- |
| 한국 region configuration | `data/region_configs/korea.json` | [ks_c_9306_notes.md](./ks_c_9306_notes.md) |
| 한국 golden sample | [ks_c_9306_notes.md](./ks_c_9306_notes.md) | KS notes |
| 한국 구현 주의사항 | [ks_c_9306_dev_notes.md](./ks_c_9306_dev_notes.md) | KS dev notes |
| 한국 설계 heuristic | [ks_c_9306_design_notes.md](./ks_c_9306_design_notes.md) | KS design notes |
| ISO 공통 용어 | [../../iso16358_glossary.md](../../iso16358_glossary.md) | ISO glossary |
