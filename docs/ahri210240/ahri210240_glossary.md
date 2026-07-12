# AHRI 210/240 Glossary

이 문서는 AHRI 210/240 HSPF2/SEER2 문서에서 사용하는 도메인 용어, 수식 기호, 코드 변수명 정의의 단일 용어 사전이다. 설계 엔지니어가 보는 물리적 의미와 Coding Agent 및 SW 엔지니어가 확인해야 하는 변수/스키마 정보를 분리하여 관리한다.

## 1. HVAC 설계 엔지니어용

| 용어 및 기호 | 한글명 | 근거 | 정의 및 설계상 의미 |
| --- | --- | --- | --- |
| HSPF2 | 난방 계절 성능 계수 2 | AHRI 210/240-2026 Section 11 | 계절 난방 부하를 압축기 에너지와 보조열 에너지 합으로 나눈 지표다. 저온 용량, 부분부하 효율, 보조열 사용량이 함께 반영된다. |
| SEER2 | 냉방 계절 에너지 효율 2 | AHRI 210/240 cooling rating sections | 냉방 seasonal bin에서 전달 냉방량을 소비전력 합으로 나눈 지표다. 저속 및 중간속 냉방 효율이 계절값에 영향을 준다. |
| BL(tj) | bin별 건물 부하 | AHRI 210/240-2026 Equation 11.104 | 외기온 bin `tj`에서 요구되는 난방 부하다. 장비 용량선과 만나는 위치가 Case I/II/III 분기를 결정한다. |
| tj | bin 외기온 | AHRI 210/240-2026 Table 16 | 계절 계산에서 사용하는 외기온 대표값이다. 온도별 시간 가중치와 함께 계절 부하 및 에너지 합산에 사용된다. |
| fractional bin hours | 분수 빈 시간 | AHRI 210/240-2026 Table 16 | Table 16의 시간 가중치다. HLH와 곱해 absolute bin hours로 변환해야 계절 합산에 사용할 수 있다. |
| absolute bin hours | 절대 빈 시간 | AHRI 210/240-2026 Table 16 | `fractional bin hours × HLH`로 계산되는 실제 계절 시간이다. 계절 부하와 에너지 합산에는 이 값을 사용한다. |
| HLH | 난방 부하 시간 | AHRI 210/240-2026 Table 16 | Heating Load Hours의 약어다. fractional bin hours를 계절 시간으로 변환하는 난방 부하 시간이며, 현재 Region IV 값은 1701이다. |
| HLF | 난방 부하율 | AHRI 210/240-2026 Case I path | 저속 용량 대비 건물 부하 비율이다. Case I에서 cycling 손실을 계산하는 기준이 된다. |
| PLF | 부분부하 보정계수 | AHRI 210/240-2026 Case I path | Part Load Factor의 약어다. 저부하에서 압축기 정지/재기동으로 생기는 cycling 손실을 반영한다. |
| Fdef | 제상 보정계수 | AHRI 210/240-2026 Equation 11.107 | demand defrost 시험 시간으로 계산되는 제상 보정 계수다. 현재 프로젝트는 계산 trace와 실제 적용 multiplier 정책을 구분한다. |
| Ttest | 제상 시험 시간 | AHRI 210/240-2026 Equation 11.107 | 제상 보정계수 계산에 사용하는 시험 시간이다. 프로젝트 내부에서는 최소 90분으로 clamp한다. |
| Tmax | 최대 제상 시간 | AHRI 210/240-2026 Equation 11.107 | 제상 보정계수 계산에 사용하는 최대 시간이다. 프로젝트 내부에서는 최대 720분으로 clamp한다. |
| t_off | 저온 차단 온도 | AHRI 210/240-2026 Section 11 | heat pump가 동작하지 않는 저온 차단 기준이다. bin별 heat pump availability를 결정한다. |
| t_on | 저온 재가동 온도 | AHRI 210/240-2026 Section 11 | 저온 차단 이후 재가동 기준 온도다. `t_on >= t_off` 조건을 만족해야 한다. |
| delta_j | bin별 heat pump availability | AHRI 210/240-2026 Section 11 | 특정 bin에서 heat pump가 담당하는 가용 비율이다. 현재 경로에서는 0, 0.5, 1.0 값이 사용될 수 있다. |
| COP | 성능계수 | AHRI 210/240-2026 Section 11 | 난방 또는 냉방 출력 대비 소비전력의 비율이다. COP가 낮아지면 동일 부하를 처리하는 에너지가 증가한다. |
| Case I | 저속 cycling 구간 | AHRI 210/240-2026 Case I path | 건물 부하가 저속 용량 이하인 구간이다. 이 구간에만 PLF가 적용된다. |
| Case II | 중간속 보간 구간 | AHRI 210/240-2026 Case II path | 건물 부하가 저속 용량과 full-speed 용량 사이에 있는 구간이다. 중간속 COP 보간 경로가 중요하다. |
| Case III | full-speed 및 보조열 구간 | AHRI 210/240-2026 Case III path | 건물 부하가 full-speed 용량 이상인 구간이다. 부족분은 보조열로 처리되어 HSPF2를 낮춘다. |
| H01/H11 | 난방 저속 시험점 | AHRI 210/240-2026 Table 8 aliases, Section 11 | 저속 난방 용량과 전력선을 구성하는 시험점이다. 온화한 bin에서 cycling 손실 판단에 영향을 준다. |
| H12 | 47°F full-load 난방 시험점 | AHRI 210/240-2026 Equation 11.181~11.186 | 존재하면 H1Full 실측값으로 우선 사용된다. 없으면 H1N 또는 H32 기반 fallback이 적용된다. |
| H1N | nominal 난방 시험점 | AHRI 210/240-2026 Equation 11.183~11.186 | H12가 없을 때 H1Full fallback 계산에 사용될 수 있는 난방 시험점이다. |
| H22 | frost accumulation full-load 난방 시험점 | AHRI 210/240-2026 Equation 11.44, Equation 11.50 | 존재하면 H2Full 실측값으로 우선 사용된다. 없으면 H32와 H1Full 기반 fallback이 적용된다. |
| H2Int | 중간속 난방 시험점 | AHRI 210/240-2026 Equation 11.199~11.204 | Case II 보간의 중심이 되는 시험점이다. Low(35°F)와 H2Full 사이에 있어야 한다. |
| H32 | 17°F full-load 난방 시험점 | AHRI 210/240-2026 Equation 11.213~11.218 | 저온 full-speed 용량선의 핵심 기준점이다. 보조열 발생 여부에 큰 영향을 준다. |
| H42 | 5°F optional full-load 난방 시험점 | AHRI 210/240-2026 Equation 11.215~11.218 | 저온 지역 제품에서 5°F 근처 extrapolation 신뢰도를 높이는 optional anchor다. |
| A2 | 냉방 full-load 시험점 | AHRI 210/240-2026 Table 8 aliases, Equation 11.104 프로젝트 anchor | HSPF2 v3에서 variable-capacity heating load line anchor로 사용된다. |
| A/B/E/F cooling points | 냉방 시험점 | AHRI 210/240 cooling rating sections | SEER2 현재 경로에서 full, low, intermediate 냉방 용량과 전력선을 구성하는 시험점이다. |
| Cd | degradation coefficient | AHRI 210/240-2026 Case I path | 부분부하 cycling 손실 크기를 결정하는 계수다. 난방 기본값은 0.25로 사용된다. |
| CLF | 냉방 부하율 | Project current implementation | SEER2 low cycling에서 저속 냉방 용량 대비 냉방 부하 비율로 사용된다. |
| 보조열 | 전기 저항 보조열 | AHRI 210/240-2026 Case III path | heat pump 용량 부족분을 보충하는 열원이다. COP 1.0 기준으로 처리되며 계절 에너지 denominator를 크게 늘린다. |
| demand defrost | 수요 제상 | AHRI 210/240-2026 Equation 11.107 | frost 조건에서 필요한 시점에 제상을 수행하는 제어 방식이다. 제상 시간과 회복 손실은 난방 계절 성능에 영향을 준다. |

## 2. Coding Agent & SW 엔지니어용

| 코드 변수명 또는 키 | 데이터 타입 | 위치 | 정의 및 구현상 주의 |
| --- | --- | --- | --- |
| `calculate_hspf2()` | function | `core/calculators/standards/ahri_hspf2.py` | HSPF2 생산 entry point다. 현재 v3 AHRI path로 연결되며 명시 지시 없이 수정하지 않는다. |
| `_calculate_hspf2_v3_ahri()` | function | `core/calculators/standards/ahri_hspf2.py` | AHRI 210/240-2026 variable-capacity heating 계산의 핵심 내부 경로다. |
| `calculate_seer2()` | function | `core/calculators/standards/ahri_seer2.py` | 현재 구현 확인 가능한 SEER2 냉방 bin 계산 entry point다. |
| `data/region_configs/usa_hspf2.json` | JSON | `data/region_configs/usa_hspf2.json` | HSPF2 Region IV canonical table, active point schema/alias/default를 담는다. |
| `canonical_hspf2_bin_tables.heating.region_iv` | JSON object | `data/region_configs/usa_hspf2.json` | variable/dual/triple 경로가 공통으로 사용하는 Region IV Table 16 canonical table이다. |
| `fractional_bin_hours` | list 또는 number | `data/region_configs/usa_hspf2.json`, return dict | Table 16의 분수 빈 시간이다. 계절 합산 전 `heating_load_hours`와 곱한다. |
| `heating_load_hours` | number | `data/region_configs/usa_hspf2.json` | HLH 값이다. 현재 Region IV는 1701이며 absolute hours 계산에 사용된다. |
| `zero_load_temp_f` | number | `data/region_configs/usa_hspf2.json` | `t_zl`에 해당한다. `BL(tj)` 계산에 사용한다. |
| `outdoor_design_temp_f` | number | `data/region_configs/usa_hspf2.json` | `t_od`에 해당한다. `BL(tj)` 계산에 사용한다. |
| `variable_capacity_slope_factor` | number | `data/region_configs/usa_hspf2.json` | `C_vs`에 해당한다. `BL(tj)` 계산에 사용한다. |
| `H01`, `H11`, `H12`, `H1N`, `H22`, `H2Int`, `H32`, `H42`, `A2` | dict | HSPF2 input schema | canonical HSPF2 test point key다. 각 dict에는 capacity와 power가 필요하다. |
| `A_Full` | alias key | variable-capacity public input schema | active alias로 `A2`로 매핑되며 canonical key와 충돌하면 fail-fast한다. |
| `defrost_t_test_minutes` | number | HSPF2 input schema | Ttest 입력이다. > 0이어야 하며 내부 사용값은 최소 90으로 clamp한다. |
| `defrost_t_max_minutes` | number | HSPF2 input schema | Tmax 입력이다. > 90이어야 하며 내부 사용값은 최대 720으로 clamp한다. |
| `h1n_same_speed_as_h3` | bool | HSPF2 optional input | H12가 없을 때 Eq.11.183 fallback을 선택하는 speed relation flag다. 기본값은 False다. |
| `does_comp_limit_min_spd` | bool | HSPF2 optional input | minimum-speed limiting 여부를 나타낸다. low-speed 경로 선택에 사용된다. 기본값은 False다. |
| `unit_type` | string | HSPF2 optional input | split 또는 single_package slope factor 선택에 사용된다. |
| `t_off`, `t_on` | number | HSPF2 optional input | 저온 차단/재가동 온도다. `t_on >= t_off` 검증이 필요하다. |
| `c_d_heating` | number | HSPF2 optional input | 난방 Case I PLF 계산에 사용하는 Cd 값이다. 기본값은 0.25다. |
| `aux_cop` | number | HSPF2 optional input | 보조열 COP다. 기본값은 1.0이며 Case III 보조열 에너지 계산에 사용된다. |
| `fdef_override` | number | HSPF2 optional input | raw HSPF2에 실제 곱하는 defrost override multiplier다. 기본값은 1.0이다. |
| `raw_hspf2_base` | number | HSPF2 return dict | defrost override 적용 전 원값이다. `total_heating_btu / total_energy_wh`로 계산된다. |
| `raw_hspf2` | number | HSPF2 return dict | `raw_hspf2_base * fdef_override` 적용 후 원값이다. |
| `HSPF2` | number | HSPF2 return dict | 0.025 단위 half-up rounding이 적용된 최종 HSPF2다. |
| `total_heating_btu`, `total_load` | number | HSPF2 return dict | bin별 `q_j` 합으로 계산되는 계절 난방 부하 합이다. |
| `total_energy_wh`, `total_energy` | number | HSPF2 return dict | bin별 `E_j` 합으로 계산되는 계절 에너지 합이다. |
| `bin_table` | dict | HSPF2 return dict | Region IV bin metadata와 canonical table 정보를 담는다. |
| `bin_details` | list | HSPF2/SEER2 return dict | bin별 부하, 용량, 전력, COP, case, compressor/auxiliary heat와 energy trace를 담는다. |
| `summary.metadata.h12_source` | string | HSPF2 return dict | H12 source를 기록한다. 값은 tested, eq_11_183, eq_11_185 계열이다. |
| `summary.metadata.h22_source` | string | HSPF2 return dict | H22 source를 기록한다. 값은 tested 또는 eq_11_44_11_50 계열이다. |
| `summary.metadata.defrost` | dict | HSPF2 return dict | Eq.11.107 계산 trace, clamp 상태, override 적용 상태를 확인하는 metadata다. |
| `q_low`, `p_low` | number | internal/bin detail | 저속 난방 또는 냉방 용량과 전력이다. |
| `q_int`, `p_int` | number | internal/bin detail | 중간속 용량과 전력이다. H2Int envelope 검증과 Case II 보간에 사용된다. |
| `q_full`, `p_full` | number | internal/bin detail | full-speed 용량과 전력이다. 저온에서 보조열 발생 여부를 결정한다. |
| `q_j`, `E_j` | number | bin detail | bin별 총 처리 열량과 총 에너지다. `q_j = q_comp + q_aux`, `E_j = e_comp + e_aux` 보존 관계를 검증한다. |
| `q_comp`, `e_comp` | number | bin detail | bin별 압축식 heat pump가 담당한 열량과 에너지다. |
| `q_aux`, `e_aux` | number | bin detail | bin별 보조열이 담당한 열량과 에너지다. |
| `operating_case` | string | bin detail | Case I/II/III 등 bin별 운전 분기 결과다. smoke 및 case activation test에서 확인한다. |
| `PLF_j` | number | bin detail | bin별 PLF trace다. Case I에서 `1 - Cd * (1 - HLF)`와 일치해야 한다. |
| `debug_info.intermediate_metadata` | dict | HSPF2 debug trace | H2Int envelope의 `N_Hq`, `N_HE` 등을 담는다. 0~1 범위를 벗어나면 fail-fast 대상이다. |
| `A_Full`, `B_Full`, `B_Low`, `E_Int`, `F_Low` | dict | SEER2 input schema | 현재 SEER2 경로가 사용하는 냉방 시험점이다. capacity와 power가 필요하다. |
| `system_type` | string | SEER2 optional input | HP 또는 AC 값으로 v-factor 선택에 사용된다. |
| `cd_low` | number | SEER2 optional input | 냉방 low cycling PLF 계산에 사용하는 Cd 값이다. 기본값은 0.25다. |
| `SEER2` | number | SEER2 return dict | 현재 냉방 seasonal efficiency다. `sum_q_j / sum_E_j`로 계산된다. |
| `EER2_A_Full`, `EER2_B_Low` | number | SEER2 return dict | A full-load 및 B low-speed 효율 trace다. |
| `total_cooling_Btu`, `total_energy_Wh` | number | SEER2 return dict | SEER2 bin별 냉방량 합과 에너지 합이다. |
