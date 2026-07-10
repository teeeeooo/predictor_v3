# KS C 9306 Glossary

이 문서는 KS C 9306 region 문서에서 사용하는 한국 고유 도메인 용어, 수식 기호, 코드 변수명, 데이터 위치의 단일 용어 사전이다. 설계 엔지니어가 보는 물리적 의미와 Coding Agent 및 SW 엔지니어가 확인해야 하는 변수/스키마 정보를 분리하여 관리한다.

ISO 16358 공통 용어는 [`../../iso16358_glossary.md`](../../iso16358_glossary.md)를 참조하고 이 문서에 중복 정의하지 않는다.

---

## 1. HVAC 설계 엔지니어용

| 용어 및 기호 | 한글명 | 근거 | 정의 및 설계상 의미 |
| --- | --- | --- | --- |
| KS C 9306 | 한국 에어컨 성능 규격 | KS C 9306:2017 Annex E | 한국 에어컨의 냉방 CSPF와 난방 HSPF 산정에 사용하는 region-specific 기준이다. ISO 16358 계열 계산 구조를 한국 기후, 시험 조건, 보정계수에 맞게 적용한다. |
| CSPF | 냉방 계절 성능계수 | KS C 9306:2017 Equation E.1.1~E.1.3 | 한국 냉방 계절에서 처리한 냉방량을 냉방 소비전력량으로 나눈 지표다. 35°C full, 35°C half, 29°C minimum 시험점이 성능선의 anchor로 작용한다. |
| HSPF | 난방 계절 성능계수 | KS C 9306:2017 Equation E.2.1~E.2.3 | 한국 난방 계절에서 필요한 난방 부하량을 heat pump 전력과 보조 전열 장치 전력의 합으로 나눈 지표다. 7°C 운전점, 2°C 제상점, -7°C 최대 운전점이 중요하다. |
| 표기 정격 냉방 능력 | declared cooling capacity | KS C 9306:2017 Equation E.1.4 | 한국 CSPF building load 계산의 기준이 되는 제조사 표기 냉방 능력이다. 냉방 load line의 절대 크기를 결정한다. |
| 냉방 부하선 | cooling building load line | KS C 9306:2017 Equation E.1.4 | 냉방 외기온도별 요구 부하를 나타내는 선이다. 장비의 minimum, half, full capacity curve와 만나는 위치가 cooling operating case를 결정한다. |
| 난방 부하선 | heating building load line | KS C 9306:2017 Equation E.2.4 | 난방 외기온도별 요구 부하를 나타내는 선이다. KS C 9306 문구에는 cooling reference가 등장하지만, 현재 프로젝트는 공식 계산 시트 동작 기준으로 난방 정격 입력을 사용한다. 이 해석은 재검증 전 임의 변경하지 않는다. |
| 한국 냉방 bin-hour | Korean cooling bin-hour | KS C 9306:2017 Table E.2 | 한국 냉방 계절에서 각 외기온도가 발생하는 시간 분포다. CSPF에서 어느 온도대의 power가 크게 누적되는지 결정한다. |
| 한국 난방 bin-hour | Korean heating bin-hour | KS C 9306:2017 Table E.4 | 한국 난방 계절에서 각 외기온도가 발생하는 시간 분포다. HSPF에서 중온 효율, 제상 영역, 저온 부족 운전의 중요도를 결정한다. |
| 35°C full 시험점 | 35°C full cooling point | KS C 9306:2017 Annex E | 고온 full 운전의 냉방 능력과 소비전력 기준점이다. 고온 냉방 output cap과 high-load 영역에 영향을 준다. |
| 35°C half 시험점 | 35°C half cooling point | KS C 9306:2017 Annex E | 고온 중간 운전의 냉방 능력과 소비전력 기준점이다. bin-hour가 많은 중간부하 냉방 영역의 power 산정에 영향을 준다. |
| 29°C minimum 시험점 | 29°C minimum cooling point | KS C 9306:2017 Annex E | 낮은 외기온 minimum 운전의 냉방 능력과 소비전력 기준점이다. 저부하 냉방 bin의 cycling loss와 minimum power에 영향을 준다. |
| 7°C full / half / minimum 시험점 | 7°C 난방 정격 / 중간 / 최소 운전점 | KS C 9306:2017 Annex E, Equation E.2.20~E.2.32 | 일반 난방 조건에서 minimum, intermediate, rated heating curve를 만드는 기준점이다. 중온 난방 bin에서 HSPF에 큰 영향을 줄 수 있다. |
| 2°C defrost 시험점 | 2°C 제상 시험점 | KS C 9306:2017 Annex E, Equation E.2.21, E.2.23, E.2.25, E.2.28, E.2.30, E.2.32 | 착상 영역의 capacity/power curve에 들어가는 제상 anchor다. capacity 저하와 power 증가를 동시에 반영하므로 HSPF에 중요하다. |
| -7°C maximum 시험점 | -7°C 최대 난방 운전점 | KS C 9306:2017 Annex E, Equation E.2.26, E.2.33 | 저온 maximum operation의 capacity/power anchor다. heating building load가 maximum capacity를 넘으면 보조 전열 장치가 발생한다. |
| 35°C minimum 파생점 | 35°C minimum calculated point | KS C 9306:2017 Annex E, Table E.3 | 29°C minimum 시험점에서 보정계수로 산정하는 고온 minimum 냉방점이다. 저부하 냉방 성능선의 상단 anchor로 사용된다. |
| 29°C full 파생점 | 29°C full calculated point | KS C 9306:2017 Annex E, Table E.3 | 35°C full 시험점에서 보정계수로 산정하는 29°C full 냉방점이다. 낮은 외기온 full curve 계산에 쓰인다. |
| 29°C half 파생점 | 29°C half calculated point | KS C 9306:2017 Annex E, Table E.3 | 35°C half 시험점에서 보정계수로 산정하는 29°C half 냉방점이다. 낮은 외기온 half curve 계산에 쓰인다. |
| low-temperature derived point | 저온 파생점 | KS C 9306:2017 Table E.5 | HSPF에서 min, intermediate, rated stage의 -7°C 값을 직접 측정하지 않을 때 기본 계수로 산정하는 point다. 2°C stage point를 계산하는 중간 anchor로도 사용될 수 있다. |
| defrost / no-frost correction | 제상 / 무착상 보정 | KS C 9306:2017 Table E.5 | 제상 조건과 무착상 조건의 capacity/power 관계를 나타내는 보정이다. 착상 영역의 성능선에 적용되며 중복 적용하면 HSPF가 크게 틀어진다. |
| 착상 영역 | frost region | KS C 9306:2017 Equation E.2.21, E.2.23, E.2.25, E.2.28, E.2.30, E.2.32 | 제상 영향이 반영되는 난방 외기온 영역이다. 한국 HSPF에서 2°C defrost anchor의 영향이 성능선 전체에 반영된다. |
| 무착상 영역 | non-frost region | KS C 9306:2017 Equation E.2.20, E.2.22, E.2.24, E.2.27, E.2.29, E.2.31 | 제상 보정 없이 low-temperature point와 7°C point를 연결해 성능선을 구성하는 영역이다. |
| 보조 전열 장치 | auxiliary electric heater | KS C 9306:2017 Equation E.2.7 | heat pump capacity가 난방 부하보다 부족할 때 부족분을 보충하는 전기열이다. HSPF denominator에 포함되어 지표를 낮춘다. |
| 효율 저하 계수, `C_D` | degradation coefficient | KS C 9306:2017 Table E.5 | 단속 운전 손실을 PLF에 반영하는 계수다. 냉방과 난방의 minimum capacity가 building load보다 큰 구간에서 중요하다. |
| 교점 기반 전력 보간 | intersection-based power interpolation | KS C 9306:2017 Equation E.1.18~E.1.26, E.2.36~E.2.40 | building load line과 운전 성능선의 교점 온도를 기준으로 소비전력을 산정하는 방식이다. 단순 capacity 비율 보간과 결과가 달라질 수 있다. |
| minimum operation | 최소 운전 | KS C 9306:2017 Annex E | 장비가 안정적으로 낮출 수 있는 낮은 capacity 운전이다. 낮을수록 cycling이 줄 수 있지만 해당 운전점의 COP가 나쁘면 이득이 제한된다. |
| intermediate operation | 중간 운전 | KS C 9306:2017 Annex E | minimum과 rated 사이의 대표 part-load 운전이다. 계절 bin-hour가 많은 영역에서 power를 결정하는 중요한 anchor다. |
| rated operation | 정격 운전 | KS C 9306:2017 Annex E | 표준 조건에서의 대표 운전점이다. 냉방과 난방 성능선의 기본 anchor로 쓰인다. |
| maximum operation | 최대 운전 | KS C 9306:2017 Annex E | 난방 저온 영역에서 capacity shortage를 막기 위한 high-stage 운전이다. capacity 증가와 power 증가의 trade-off를 함께 봐야 한다. |
| ta | minimum 교점 온도 | minimum 운전선과 building load line의 낮은 부하 쪽 교점으로 설계 판단에 쓰인다. | design concept | design notes |
| tb | 중간 기준 온도 | minimum 교점과 고온 기준점 사이에서 half capacity target을 판단하는 설계 기준 온도이다. | design concept | design notes |
| tc | half target 교점 온도 | half 운전선과 building load line의 관계를 판단하는 설계 기준 온도이다. | design concept | design notes |

---

## 2. Coding Agent & SW 엔지니어용

| 코드 변수명 또는 키 | 데이터 타입 | 위치 | 정의 및 구현상 주의 |
| --- | --- | --- | --- |
| `standard = "KS C 9306"` | string | `data/region_configs/korea.json` | 한국 region 식별자다. KS 전용 보정, 반올림, bin table을 적용하는 기준이 된다. |
| `declared_capacity` | number | caller input | 한국 CSPF building load 기준 capacity다. ROUND_HALF_UP 적용 대상이며 누락 시 CSPF 계산을 중단해야 한다. |
| `building_load_source = "declared"` | string | `data/region_configs/korea.json` | 한국 CSPF가 measured reference가 아니라 declared capacity를 기준으로 building load를 만든다는 설정이다. |
| `round_test_values` | bool | `data/region_configs/korea.json` | KS 시험값 정수 반올림 적용 여부다. true일 때 measured와 derived capacity/power 모두 HALF_UP 처리한다. |
| `rounding_method = "nearest_integer_half_up"` | string | `data/region_configs/korea.json` | Python bankers rounding을 피하기 위한 반올림 방식이다. golden sample과 맞추기 위해 유지해야 한다. |
| `points.35_full` | string | `data/region_configs/korea.json` | 35°C full 냉방 point가 measured input임을 나타낸다. |
| `points.35_half` | string | `data/region_configs/korea.json` | 35°C half 냉방 point가 measured input임을 나타낸다. |
| `points.29_min` | string | `data/region_configs/korea.json` | 29°C minimum 냉방 point가 measured input임을 나타낸다. |
| `derived_rules.35_min` | dict | `data/region_configs/korea.json` | 29°C minimum point에서 35°C minimum point를 파생하는 capacity/power factor다. |
| `derived_rules.29_full` | dict | `data/region_configs/korea.json` | 35°C full point에서 29°C full point를 파생하는 capacity/power factor다. |
| `derived_rules.29_half` | dict | `data/region_configs/korea.json` | 35°C half point에서 29°C half point를 파생하는 capacity/power factor다. |
| `bin_hours` | list | `data/region_configs/korea.json` | KS C 9306 냉방 Table E.2 bin-hour다. CSPF용이므로 HSPF bin과 섞지 않는다. |
| `hspf_bin_hours` | list | `data/region_configs/korea.json` | KS C 9306 난방 Table E.4 bin-hour다. 각 row는 `j`, `tj`, `nj`를 포함하며 load/heating_load를 넣지 않는다. |
| `power_interpolation_method = "ks_intersection"` | string | `data/region_configs/korea.json` | KS CSPF 중간 부하 전력 산정에 쓰는 교점 기반 방식이다. 타 region에 누출되면 안 된다. |
| `half_capacity_recommendation` | dict | `data/region_configs/korea.json` | 35°C half capacity 목표를 검토하기 위한 보조 계산 설정이다. CSPF 본계산 입력을 자동 대체하지 않는다. |
| `hspf.profile = "ks_c_9306_hspf"` | string | `data/region_configs/korea.json` | KS C 9306 HSPF profile 경로를 선택한다. 이 profile이면 `ks_c_9306_hspf` 입력 누락 시 common fallback하지 않고 ValueError를 내야 한다. |
| `ks_c_9306_hspf` | dict | HSPF caller input | KS HSPF production-style 입력 root다. `capacity`, `power`, `correction`을 포함해야 한다. |
| `ks_c_9306_hspf.capacity.min.7` | number | HSPF caller input | 7°C minimum heating capacity다. min stage 성능선의 7°C anchor다. |
| `ks_c_9306_hspf.capacity.rated.7` | number | HSPF caller input | 7°C rated heating capacity다. rated stage 성능선의 7°C anchor다. |
| `ks_c_9306_hspf.capacity.intermediate.7` | number | HSPF caller input | 7°C intermediate heating capacity다. intermediate stage 성능선의 7°C anchor다. |
| `ks_c_9306_hspf.capacity.max.-7` | number | HSPF caller input | -7°C maximum heating capacity다. maximum operation curve의 low-temperature anchor이며 필수다. |
| `ks_c_9306_hspf.capacity.max.def` | number | HSPF caller input | 2°C defrost maximum heating capacity anchor다. maximum operation curve와 shortage branch에 사용된다. |
| `ks_c_9306_hspf.power.min.7` | number | HSPF caller input | 7°C minimum heating power다. min stage power curve의 7°C anchor다. |
| `ks_c_9306_hspf.power.rated.7` | number | HSPF caller input | 7°C rated heating power다. rated stage power curve의 7°C anchor다. |
| `ks_c_9306_hspf.power.intermediate.7` | number | HSPF caller input | 7°C intermediate heating power다. intermediate stage power curve의 7°C anchor다. |
| `ks_c_9306_hspf.power.max.-7` | number | HSPF caller input | -7°C maximum heating power다. maximum power curve의 low-temperature anchor이며 필수다. |
| `ks_c_9306_hspf.power.max.def` | number | HSPF caller input | 2°C defrost maximum heating power anchor다. maximum power curve와 shortage branch에 사용된다. |
| `ks_c_9306_hspf.correction.capacity_def_over_nof` | number | HSPF caller input / config default | defrost capacity와 no-frost capacity의 비율이다. Table E.5 기본값은 `1 / 1.12` 방향으로 관리한다. |
| `ks_c_9306_hspf.correction.power_def_over_nof` | number | HSPF caller input / config default | defrost power와 no-frost power의 비율이다. Table E.5 기본값은 `1 / 1.06` 방향으로 관리한다. |
| `ks_c_9306_hspf.correction.cd` | number | HSPF caller input / config default | HSPF PLF 계산에 사용하는 degradation coefficient다. 0 이상 1 미만으로 검증한다. |
| `hspf.required_points` | dict | `data/region_configs/korea.json` | KS HSPF 필수 시험점 선언이다. 현재 7°C full/half/min, 2°C defrost, -7°C max를 요구한다. |
| `hspf.optional_points` | dict | `data/region_configs/korea.json` | KS HSPF 선택 입력 선언이다. min/full/half stage의 2°C와 -7°C는 optional이며 fallback 또는 derived 가능하다. |
| `hspf.derived_rules.min_-7` | dict | `data/region_configs/korea.json` | 7°C min stage에서 -7°C min stage를 Table E.5 factor로 생성하는 규칙이다. |
| `hspf.derived_rules.half_-7` | dict | `data/region_configs/korea.json` | 7°C intermediate/half stage에서 -7°C intermediate stage를 Table E.5 factor로 생성하는 규칙이다. |
| `hspf.derived_rules.full_-7` | dict | `data/region_configs/korea.json` | 7°C rated/full stage에서 -7°C rated stage를 Table E.5 factor로 생성하는 규칙이다. |
| `hspf.correction.capacity_def_over_nof` | number | `data/region_configs/korea.json` | KS HSPF capacity defrost/no-frost correction 기본값이다. 중복 적용하지 않는다. |
| `hspf.correction.power_def_over_nof` | number | `data/region_configs/korea.json` | KS HSPF power defrost/no-frost correction 기본값이다. 중복 적용하지 않는다. |
| `hspf.load_line.source` | string | `data/region_configs/korea.json` | KS HSPF heating load line 기준 capacity source다. 현재 한국은 공식 계산 시트 동작 기준 `rated_heating_capacity`를 사용한다. |
| `hspf.load_line.zero_load_temp` | number | `data/region_configs/korea.json` | KS HSPF heating load가 0이 되는 외기온도다. |
| `hspf.load_line.full_load_temp` | number | `data/region_configs/korea.json` | KS HSPF heating load가 기준 부하가 되는 외기온도다. |
| `hspf.load_line.rated_capacity_factor` | number | `data/region_configs/korea.json` | KS HSPF heating load line 기준 capacity에 곱하는 factor다. 현재 값은 0.82다. |
| `source = "rated_heating_capacity"` | string | HSPF load line config | 공식 계산 시트 동작을 따른 현재 한국 profile 해석이다. spec text의 cooling reference와 차이가 있으므로 임의 변경 금지다. |
| `35_full`, `35_half`, `29_min` | dict | CSPF measured input | KS CSPF의 필수 measured cooling point다. 각 dict에는 `capacity`, `power`가 필요하다. |
| `full`, `half`, `min` | stage alias | HSPF required/optional points | HSPF region config에서 `full`은 rated, `half`는 intermediate, `min`은 minimum stage와 매핑된다. |
| `max` | stage alias | HSPF required points | maximum operation stage다. -7°C와 2°C defrost anchor가 필수다. |
| `def` | point key | HSPF maximum stage input | 2°C defrost anchor를 나타내는 key다. stage별 2°C no-frost 또는 calculated point와 혼동하지 않는다. |
| `operating_case = "maximum_shortage"` | string | HSPF bin detail | heating building load가 maximum capacity를 초과해 auxiliary heat가 발생한 branch다. |
| `operating_case = "cyclic_minimum"` | string | HSPF bin detail | building load가 minimum capacity 이하라 PLF가 적용되는 branch다. |
| `operating_case = "minimum_intermediate"` | string | HSPF bin detail | building load가 minimum과 intermediate capacity 사이에 있는 branch다. |
| `operating_case = "intermediate_rated"` | string | HSPF bin detail | building load가 intermediate와 rated capacity 사이에 있는 branch다. |
| `operating_case = "rated_maximum"` | string | HSPF bin detail | building load가 rated와 maximum capacity 사이에 있는 branch다. |

---

## 3. Data Location Summary

| Data | Location | Owner document |
| --- | --- | --- |
| 한국 region configuration | `data/region_configs/korea.json` | [`ks_c_9306_notes.md`](./ks_c_9306_notes.md) |
| 한국 CSPF golden sample | `docs/iso16358/regions/ks_c_9306/ks_c_9306_notes.md` | [`ks_c_9306_notes.md`](./ks_c_9306_notes.md) |
| 한국 HSPF golden / validation tests | `tests/test_iso16358_hspf_ks_oracle.py`, `tests/test_iso16358_hspf_validation.py` | [`ks_c_9306_dev_notes.md`](./ks_c_9306_dev_notes.md) |
| 한국 구현 주의사항 | `docs/iso16358/regions/ks_c_9306/ks_c_9306_dev_notes.md` | [`ks_c_9306_dev_notes.md`](./ks_c_9306_dev_notes.md) |
| 한국 설계 heuristic | `docs/iso16358/regions/ks_c_9306/ks_c_9306_design_notes.md` | [`ks_c_9306_design_notes.md`](./ks_c_9306_design_notes.md) |
| ISO 공통 용어 | `docs/iso16358/iso16358_glossary.md` | [`../../iso16358_glossary.md`](../../iso16358_glossary.md) |
