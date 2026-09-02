# AHRI 210/240 Notes

## 1. Overview

이 문서는 AHRI 210/240 계열의 Appendix M SEER/HSPF와 Appendix M1 SEER2/HSPF2 계산 자산을 프로젝트 기준으로 정리한 기준 문서다. Primary 기준은 이 문서와 `docs/ahri210240/ahri210240_dev_notes.md`, 각 Appendix M/M1 계산 경로, `data/region_configs/usa_m_seer.json`, `data/region_configs/usa_m_hspf.json`, `data/region_configs/usa_hspf2.json`, 관련 테스트 파일이다. AHRI PDF는 Section/Table/Equation 번호 확인용 Secondary 근거로만 사용한다. 과거 HSPF2 구현 상세 원본은 `docs/archive/standards_legacy/ahri_hspf2.md`에 historical source로 보존한다.

현재 프로젝트에서 가장 깊게 검증된 경로는 AHRI 210/240-2026 HSPF2 v3 경로다. Appendix M은 AHRI 210/240-2017 Addendum 1의 variable-speed, non-ducted, single-split 경로로 별도 지원하며 M HSPF는 Region IV로 한정한다. M과 M1은 시험점, bin/config, 계산식, 공개 지표가 다르므로 하나의 입력/출력 계약으로 합치지 않는다. 현재 테스트의 variable-capacity HSPF2/SEER2 및 Appendix M 입력과 expected 결과는 사용자가 확인한 golden 또는 프로젝트 golden으로 각 경로에 고정하며, 신규 deep-result fingerprint는 구조 호환성을 위한 characterization으로만 취급한다. 근거: AHRI 210/240-2017 Appendix M Tables 19/20 및 AHRI 210/240-2026 Section 11, Table 16, Equation 11.104, Equation 11.107, Equation 11.181~11.218.

### Standard-family boundary

| Path | Standard/edition | Current project scope | Canonical config |
| --- | --- | --- | --- |
| Appendix M SEER | AHRI 210/240-2017 Appendix M | variable-speed, non-ducted, single-split cooling | `data/region_configs/usa_m_seer.json` (Appendix M Table 19) |
| Appendix M HSPF | AHRI 210/240-2017 Addendum 1 | variable-speed, non-ducted, single-split heating, Region IV | `data/region_configs/usa_m_hspf.json` (Appendix M Table 20) |
| Appendix M1 SEER2 | AHRI 210/240-2026 | current variable-capacity cooling path | `data/region_configs/usa.json` |
| Appendix M1 HSPF2 | AHRI 210/240-2026 | current variable-capacity heating path, Region IV | `data/region_configs/usa_hspf2.json` |

M and M1 labels may look similar in the UI, but their ratings are not directly interchangeable. Keep standard edition, metric suffix, test-point schema, region/bin data, and golden cases attached to the path that owns them.

## 2. Scope

### Current Appendix M1 HSPF2 implementation scope

현재 AHRI HSPF2 구현 우선 지원 범위는 다음과 같다.

- **적용 규격**: AHRI 210/240
- **장비 유형**: non-ducted, single-split, variable-capacity, air-to-air heat pump
- **적용 지역**: Region IV 중심 (`fractional heating bin hours` 사용)
- **생산 경로**: v3 AHRI path (`calculate_hspf2()`)
- **보조열**: 전기 저항 보조열 (`aux_cop` 1.0)
- **Defrost**: demand defrost 기반 (seasonal multiplier는 현재 override 1.0 기본 적용)
- **SEER2 현재 범위**: variable-capacity cooling bin 계산 (확인 가능한 A/B/E/F 중심)

### Current Appendix M SEER/HSPF implementation scope

Appendix M 지원 범위는 다음과 같다.

- **적용 규격**: AHRI 210/240-2017 Appendix M; HSPF는 Addendum 1 보정 기준을 포함한다.
- **장비 유형**: variable-speed, non-ducted, single-split
- **SEER 시험점**: `A2`, `B2`, `EV`, `B1`, `F1`; UI 표시는 `EV`를 `Ev`로만 변환한다.
- **HSPF 시험점**: 필수 `H01`, `H11`, `H1N`, `H2V`, `H32`; 선택 `H12`, `H22`; `H42`는 지원하지 않는다.
- **적용 지역**: HSPF는 Region IV (`usa_m_hspf.json` Table 20 bin data)만 지원한다. SEER는 Appendix M cooling bin data를 사용한다.
- **보정/옵션**: `CDc`/`CDh`, HSPF의 optional H12/H22 pair, automatic cutout, demand defrost 및 Defrost Test/Max timing을 M 경로에서 독립적으로 해석한다.

### Future extension boundary

아래 항목은 영구적인 구현 금지가 아니며, 명시적인 확장 요청 및 별도의 설계(Design Gate) 전까지는 현재 지원 범위를 벗어난 확장 후보로 취급한다.

- **장비 유형 확장**: ducted ESP, multi-split, VRF, dual fuel, furnace, zoning, northern heat pump, two-compressor special cases
- **지역 확장**: Region IV 외 지역 (Table 16 bin data 및 HLH 필요)
- **SEER2/Defrost 고도화**: SEER2 full standard parity (off-mode 등 반영), HSPF2 defrost seasonal multiplier 실제 적용 정책 확정

## 3. Glossary Pointer

용어 및 수식 기호의 상세 정의는 `ahri210240_glossary.md`를 참조하라.

## 4. Input Schema

### HSPF2 v3 Required Inputs

| Field | Standard symbol | Unit | Required | Validation rule | Reference |
| --- | --- | --- | --- | --- | --- |
| `H01` | H01 Test | Btu/h, W | Yes | capacity/power > 0 | AHRI 210/240-2026 Table 8 aliases |
| `H11` | H11 Test | Btu/h, W | Yes | capacity/power > 0 | AHRI 210/240-2026 Table 8 aliases |
| `H1N` | H1N Test | Btu/h, W | Yes | capacity/power > 0 | AHRI 210/240-2026 Table 8 aliases |
| `H2Int` | H2Int Test | Btu/h, W | Yes | Low(35°F)와 H2Full 사이여야 한다. | AHRI 210/240-2026 Equation 11.199~11.204 |
| `H32` | H32 Test | Btu/h, W | Yes | capacity/power > 0 | AHRI 210/240-2026 Table 8 aliases |
| `A2` 또는 `A_Full` | A2 Test | Btu/h, W | Yes | capacity/power > 0 | AHRI 210/240-2026 Equation 11.104 프로젝트 anchor |
| `defrost_t_test_minutes` | Ttest | min | Yes | > 0, 내부 사용값은 최소 90으로 clamp | AHRI 210/240-2026 Equation 11.107 |
| `defrost_t_max_minutes` | Tmax | min | Yes | > 90, 내부 사용값은 최대 720으로 clamp | AHRI 210/240-2026 Equation 11.107 |

### HSPF2 v3 Optional Inputs

| Field | Standard symbol | Unit | Required | Validation rule | Reference |
| --- | --- | --- | --- | --- | --- |
| `H12` | H12 Test | Btu/h, W | No | 없으면 H1Full_calc fallback 사용 | AHRI 210/240-2026 Equation 11.181~11.186 |
| `H22` | H22 Test | Btu/h, W | No | 없으면 Eq.11.44/11.50 fallback 사용 | AHRI 210/240-2026 Equation 11.44, Equation 11.50 |
| `H42` | H42 Test | Btu/h, W | No | 있으면 5°F 이하 full-speed 경로에 사용 | AHRI 210/240-2026 Equation 11.215~11.218 |
| `h1n_same_speed_as_h3` | speed relation | bool | No | 기본 False | AHRI 210/240-2026 Equation 11.183~11.186 |
| `does_comp_limit_min_spd` | minimum-speed limiting | bool | No | 기본 False | AHRI 210/240-2026 Equation 11.187~11.194 |
| `unit_type` | unit type | n/a | No | split/single_package slope factor 선택 | AHRI 210/240-2026 Equation 11.185~11.186 |
| `t_off`, `t_on` | cut-out/on temp | °F | No | `t_on >= t_off`, 기본 -40/-40 | AHRI 210/240-2026 Section 11 |
| `c_d_heating` | Cd | dimensionless | No | 기본 0.25 | AHRI 210/240-2026 Case I path |
| `aux_cop` | auxiliary COP | dimensionless | No | 기본 1.0 | AHRI 210/240-2026 Case III path |
| `fdef_override` | Fdef override | dimensionless | No | 기본 1.0 | AHRI 210/240-2026 Equation 11.107 |

### SEER2 Current Inputs

| Field | Standard symbol | Unit | Required | Validation rule | Reference |
| --- | --- | --- | --- | --- | --- |
| `A_Full` | A full-load cooling | Btu/h, W | Yes | 현재 코드에서 직접 unpack | AHRI 210/240 cooling rating sections |
| `B_Full` | B full-load cooling | Btu/h, W | Yes | 현재 코드에서 직접 unpack | AHRI 210/240 cooling rating sections |
| `B_Low` | B low-speed cooling | Btu/h, W | Yes | 현재 코드에서 직접 unpack | AHRI 210/240 cooling rating sections |
| `E_Int` | E intermediate cooling | Btu/h, W | Yes | P_Int <= 0이면 ValueError | AHRI 210/240 cooling rating sections |
| `F_Low` | F low-speed cooling | Btu/h, W | Yes | 현재 코드에서 직접 unpack | AHRI 210/240 cooling rating sections |
| `system_type` | HP/AC | n/a | No | HP 또는 AC, v-factor 선택 | Project current implementation |
| `cd_low` | Cd low | dimensionless | No | 기본 0.25 | Project current implementation |

### Appendix M Inputs

Appendix M 입력은 M1 입력과 공유하지 않는다. 아래 key는 현재 M application/capability 경로의 canonical point pair와 option 의미를 요약한 것이다.

| Field | Standard symbol | Unit | Required | Validation / semantics | Reference |
| --- | --- | --- | --- | --- | --- |
| `capacity_A2`, `power_A2` | A2 | Btu/h, W | Yes | capacity/power > 0 | Appendix M Table 19 |
| `capacity_B2`, `power_B2` | B2 | Btu/h, W | Yes | capacity/power > 0 | Appendix M Table 19 |
| `capacity_EV`, `power_EV` | EV | Btu/h, W | Yes | capacity/power > 0; UI label is `Ev` | Appendix M Table 19 |
| `capacity_B1`, `power_B1` | B1 | Btu/h, W | Yes | capacity/power > 0 | Appendix M Table 19 |
| `capacity_F1`, `power_F1` | F1 | Btu/h, W | Yes | capacity/power > 0 | Appendix M Table 19 |
| `cd` | CDc / CDh | dimensionless | Yes | `0 <= cd < 1`; cooling/heating uses its own M adapter | Appendix M calculation path |
| `capacity_H01` ... `power_H32` | H01, H11, H1N, H2V, H32 | Btu/h, W | Yes | every capacity/power pair > 0 | Appendix M Table 20 |
| `capacity_H12`, `power_H12` | H12 | Btu/h, W | No | blank pair = fallback; populated pair = measured; half-filled = invalid | Appendix M Addendum 1 path |
| `capacity_H22`, `power_H22` | H22 | Btu/h, W | No | blank pair = fallback; populated pair = measured; half-filled = invalid | Appendix M Addendum 1 path |
| `defrost_test_minutes`, `defrost_max_minutes` | Ttest / Tmax | min | Conditional | required only with demand defrost; test > 0 and max > 90, test <= max | Appendix M Addendum 1, defrost path |
| `cut_out_c`, `cut_in_c` | cut-out / cut-in | °C | Conditional | required only with automatic cutout; cut-in >= cut-out | Appendix M Addendum 1, cutout path |

`H2V` and `H1N` are canonical M keys. The M UI may render them as `H2v` and `H1N(STD)`; this presentation mapping does not rename the domain keys. M1 `H2Int`, `H42`, `A_Full`, and M1-specific flags remain outside this M schema.

## 5. Output Schema

### HSPF2 v3

| Field | Meaning | Unit | Derived from | Reference |
| --- | --- | --- | --- | --- |
| `HSPF2` | 최종 반올림 HSPF2 | Btu/Wh | nearest 0.025 rounding | AHRI 210/240-2026 Section 11 |
| `raw_hspf2` | defrost override 적용 후 원값 | Btu/Wh | `raw_hspf2_base * fdef_override` | AHRI 210/240-2026 Equation 11.107 |
| `raw_hspf2_base` | defrost override 전 원값 | Btu/Wh | `total_heating_btu / total_energy_wh` | AHRI 210/240-2026 Section 11 |
| `total_heating_btu`, `total_load` | 계절 난방 부하 합 | Btu | bin별 `q_j` 합 | AHRI 210/240-2026 Table 16 |
| `total_energy_wh`, `total_energy` | 계절 에너지 합 | Wh | bin별 `E_j` 합 | AHRI 210/240-2026 Case I~III |
| `bin_table` | Region IV bin metadata | mixed | JSON canonical table | AHRI 210/240-2026 Table 16 |
| `summary.metadata` | formula path, fallback source, defrost trace | mixed | 계산 경로 trace | Project trace |
| `bin_details` | bin별 BL, q/p low/int/full, COP, case, q/e comp/aux | mixed | Region IV bin loop | AHRI 210/240-2026 Equation 11 계열 |

### SEER2 Current

| Field | Meaning | Unit | Derived from | Reference |
| --- | --- | --- | --- | --- |
| `SEER2` | 현재 냉방 seasonal efficiency | Btu/Wh | `sum_q_j / sum_E_j` | AHRI 210/240 cooling rating sections |
| `EER2_A_Full` | A full-load 효율 | Btu/Wh | `q_A / P_A` | Project current implementation |
| `EER2_B_Low` | B low-speed 효율 | Btu/Wh | `q_Blow / P_Blow` | Project current implementation |
| `total_cooling_Btu` | bin별 냉방량 합 | Btu | `sum_q_j` | Project current implementation |
| `total_energy_Wh` | bin별 에너지 합 | Wh | `sum_E_j` | Project current implementation |
| `bin_details` | bin별 BL, q low/int/full, EER, case | mixed | cooling bin loop | Project current implementation |

### Appendix M SEER

| Field | Meaning | Unit | Derived from | Reference |
| --- | --- | --- | --- | --- |
| `raw_seer` | 반올림 전 계절 SEER | Btu/Wh | seasonal cooling numerator / energy denominator | Appendix M cooling path |
| `published_seer` | 최종 표시 SEER | Btu/Wh | M rounding rule | Appendix M cooling path |
| `seasonal_cooling_numerator` | 계절 냉방량 합 | Btu/h display basis | weighted `q` contributions | Appendix M Table 19 |
| `seasonal_energy_denominator` | 계절 에너지 합 | W display basis | weighted `e` contributions | Appendix M Table 19 |
| `eer_by_point` | 시험점별 EER | Btu/Wh | capacity / power at A2/B2/EV/B1/F1 | Appendix M Table 19 |
| `bin_details` | bin별 Case I/II/III, load, capacity/power, EER, q/e contribution | mixed | cooling bin loop | Appendix M cooling path |

### Appendix M HSPF

| Field | Meaning | Unit | Derived from | Reference |
| --- | --- | --- | --- | --- |
| `raw_hspf` | 반올림 전 계절 HSPF | Btu/Wh | seasonal heating load / compressor and resistance energy | Appendix M Addendum 1 |
| `published_hspf` | 최종 표시 HSPF | Btu/Wh | M rounding rule | Appendix M Addendum 1 |
| `dhr_min_raw`, `dhr_min_standardized` | 설계 난방 요구량 | Btu/h | Region IV design/load data | Appendix M Table 20 |
| `heating_load_aggregate` | 계절 난방 부하 합 | Btu/h display basis | weighted bin heating load | Appendix M Table 20 |
| `compressor_energy_aggregate`, `resistance_energy_aggregate` | 압축기/저항 보조열 에너지 합 | W display basis | weighted seasonal denominators | Appendix M Addendum 1 |
| `defrost_credit` | demand-defrost credit | dimensionless | Defrost Test/Max timing | Appendix M Addendum 1 |
| `h12_source`, `h22_source` | optional point source trace | text | tested or M fallback | Appendix M Addendum 1 |
| `bin_details` | bin별 case, load, compressor/auxiliary heat와 energy trace | mixed | Region IV bin loop | Appendix M Table 20 |

M HSPF의 `Heating Load [Btu/h]`, `Compressor Input [W]`, `Auxiliary Input [W]`는 UI 표시명이다. batch 결과의 `load`, `comp`, `aux`는 이 표시를 위한 current row projection이며 M1 result schema와 합치지 않는다.

## 6. Calculation Flow

### HSPF2 v3 Flow

1. 입력 test point를 canonical key로 변환한다. Variable-capacity public
   alias allowlist는 `A_Full -> A2`만 유지하며, dual/triple point alias는
   각 product resolver가 소유한다.
2. 필수점 `H01`, `H11`, `H1N`, `H2Int`, `H32`, `A2`와 defrost 입력을 검증한다.
3. Region IV canonical bin table을 읽고 fractional bin hour 합이 0.757인지 검증한다. `absolute bin hours = fractional bin hours * HLH`이며, 현재 HLH는 1701이다. 근거: AHRI 210/240-2026 Table 16.
4. H12가 있으면 실측 full-load high temperature point로 사용한다. 없으면 `h1n_same_speed_as_h3` 여부에 따라 Eq.11.183 또는 Eq.11.185 fallback을 사용한다.
5. H22가 있으면 실측 frost accumulation full-load point로 사용한다. 없으면 Eq.11.44/11.50 fallback을 사용한다.
6. H42가 있으면 5°F full-load anchor로 사용한다. 없으면 5°F 이하 full-speed 경로는 H1Full/H3Full line 기반으로 간다.
7. 각 bin에서 `BL(tj)`를 계산한다. 현재 anchor는 A2 cooling capacity이며, `C_vs`, `t_zl`, `t_od`는 canonical Region IV table에서 온다. 근거: AHRI 210/240-2026 Equation 11.104.
8. 각 bin에서 q/p full, q/p low, q/p intermediate를 계산한다. full/low/intermediate 경로는 Equation 11.187~11.218 계열을 따른다.
9. Case I/II/III를 결정한다. `BL <= q_low`는 low-speed cycling, `q_low < BL < q_full`은 intermediate interpolation, `BL >= q_full`은 full-speed plus auxiliary heat다.
10. `t_off`, `t_on`, COP 조건으로 `delta_j`를 결정한다. `delta_j=0.5` fractional availability가 나올 수 있다.
11. bin별 compressor heat/energy와 auxiliary heat/energy를 합산한다.
12. `raw_hspf2_base = total_heating_btu / total_energy_wh`를 계산하고, `raw_hspf2 = raw_hspf2_base * fdef_override`를 적용한다.
13. 최종 HSPF2는 0.025 단위 half-up rounding으로 산출한다.

### SEER2 Current Flow

1. 설정 파일에서 cooling bin temperature/hour, A/B/E/F point temperature, scaling factor, v-factor를 읽는다.
2. A full, B full, B low, E intermediate, F low capacity/power를 입력받는다.
3. E point에서 low/full envelope 위치를 계산해 intermediate slope `M_Cq`, `M_CE`를 만든다.
4. 각 cooling bin에서 low, full, intermediate capacity/power를 온도에 따라 계산한다.
5. `BL(tj)`는 zero-load 65°F, A point capacity, scale factor, system v-factor로 계산한다.
6. Case 1은 low cycling, Case 2.1은 low~intermediate 보간, Case 2.2는 intermediate~full 보간, Case 3은 full load로 처리한다.
7. `SEER2 = sum_q_j / sum_E_j`를 반환한다.

### Appendix M SEER Flow

1. Appendix M Table 19 cooling bin data와 A2/B2/EV/B1/F1 test points를 검증한다.
2. A2/B2 및 low/full boundary를 이용해 intermediate capacity/power slope를 계산하고 EV에서 intermediate envelope 위치를 검증한다.
3. 각 bin에서 building load와 low/intermediate/full capacity/power를 계산한다.
4. Case I에서는 CDc를 사용한 cycling correction을 적용하고, Case II/III에서는 해당 M seasonal path에 맞는 EER와 delivered load를 합산한다.
5. seasonal cooling numerator와 energy denominator의 비율로 raw SEER를 구한 뒤 M published SEER를 반환한다.

### Appendix M HSPF Flow

1. Region IV Table 20 bin data와 필수 H01/H11/H1N/H2V/H32 point pair를 검증한다.
2. H12/H22는 각각 독립된 optional pair로 해석한다. blank pair는 fallback, populated pair는 measured, half-filled pair는 invalid다.
3. H1N/H32 관계 옵션에 따라 low/intermediate/full heating performance를 만들고 Region IV building load와 비교한다.
4. 각 bin을 Case I/II/III로 분류한다. Case I에는 CDh cycling correction, Case III에는 부족분에 대한 resistance auxiliary energy가 반영된다.
5. demand defrost가 켜진 경우 Defrost Test/Max로 credit을 계산한다. 꺼진 경우 timing input은 `N/A` presentation이고 credit은 1.0이다.
6. seasonal heating load와 compressor/resistance energy를 합산하여 raw/published HSPF와 diagnostics를 반환한다.

## 7. Formula Mapping

| Formula | Standard reference | Inputs | Outputs | Project interpretation |
| --- | --- | --- | --- | --- |
| `BL(tj) = q_H1_calc * C_vs * (t_zl - tj) / (t_zl - t_od)` | AHRI 210/240-2026 Equation 11.104 | A2 capacity, C_vs, t_zl, t_od | building_load | 현재 v3 path는 A2 cooling capacity를 anchor로 사용한다. |
| H1Full tested | AHRI 210/240-2026 Equation 11.181~11.182 | H12 | H1Full_calc | H12가 있으면 실측값 사용 |
| H1Full nominal fallback | AHRI 210/240-2026 Equation 11.183~11.184 | H1N | H1Full_calc | `h1n_same_speed_as_h3=True` |
| H1Full extrapolated fallback | AHRI 210/240-2026 Equation 11.185~11.186 | H32, CSF, PSF | H1Full_calc | H12 없고 same speed가 아니면 사용 |
| H22 fallback | AHRI 210/240-2026 Equation 11.44, Equation 11.50 | H32, H1Full_calc | H2Full | H22 missing optional point 처리 |
| Low speed non-limiting | AHRI 210/240-2026 Equation 11.187~11.188 | H01, H11, tj | q_low, p_low | minimum-speed limiting이 아니면 사용 |
| Low speed limiting | AHRI 210/240-2026 Equation 11.189~11.194 | H01, H11, H2Int, q_int | q_low, p_low | minimum-speed limiting이면 사용 |
| Intermediate slope | AHRI 210/240-2026 Equation 11.199~11.204 | H2Int, Low(35), H22, H32 | q_int, p_int | H2Int가 envelope 내부인지 검증 |
| Full speed high bins | AHRI 210/240-2026 Equation 11.209~11.210 | H32, H1Full_calc, H1N | q_full, p_full | `tj >= 45°F` |
| Full speed mid bins | AHRI 210/240-2026 Equation 11.213~11.214 | H32, H22 | q_full, p_full | `17°F < tj < 45°F` |
| Full speed low bins with H42 | AHRI 210/240-2026 Equation 11.215~11.218 | H42, H32, H1Full_calc | q_full, p_full | 5°F 근처 저온 경로 |
| Defrost factor | AHRI 210/240-2026 Equation 11.107 | Ttest, Tmax | f_def_seasonal | 현재 trace에 계산하되 기본 raw에는 override 1.0 적용 |

### Appendix M Formula Mapping

| Formula area | Current interpretation | Inputs / boundary | Output |
| --- | --- | --- | --- |
| SEER building load | `BL(t) = (t - 65) / 30 * (A2 / sizing_factor)` | Appendix M cooling bin temperature and A2 | bin building load |
| SEER low/full curves | F1→B1 low curve and B2→A2 full curve are linearly evaluated over temperature | F1, B1, B2, A2 | `q_low`, `p_low`, `q_full`, `p_full` |
| SEER intermediate curve | EV position at 87°F determines capacity/power interpolation slopes; bin EER uses the three curve anchors | EV must remain within the low/full envelope | intermediate EER and bin energy |
| HSPF design load | Region IV building load uses design temperature, building-load factor, and standardized minimum DHR | Appendix M Table 20 `region_iv` data | `building_load`, `dhr_min_standardized` |
| HSPF low curve | H11→H01 line | H01, H11 | `q_low`, `p_low` |
| HSPF intermediate curve | H2V position between 35°F low/full values determines capacity/power slopes; COP is interpolated by delivered load | H2V, H01, H11, H32, H12/H22 fallback | `q_int`, `p_int`, Case II COP |
| HSPF full curve | H32↔47°F and H32↔35°F segments are selected by bin temperature | H32 plus H12 or H1N/H32 fallback; H22 optional/fallback | `q_full`, `p_full` |
| HSPF defrost credit | Demand-defrost timing is clamped to the M limits before the credit is calculated; disabled demand defrost returns 1.0 | Defrost Test/Max only when enabled | `defrost_credit` / `f_def` |
| Seasonal accumulation | Weighted load and energy are summed by bin, then raw metric is rounded to the published M metric | M-specific bin table; no M1 bin reuse | `raw_seer`/`published_seer` or `raw_hspf`/`published_hspf` |

## 8. Code Mapping

| Standard item | File | Function | Output key | Notes |
| --- | --- | --- | --- | --- |
| HSPF2 entry point | `core/calculators/standards/ahri_hspf2.py` | `calculate_hspf2` | `HSPF2` | v3 production path로 연결 |
| HSPF2 v3 path | `core/calculators/standards/_ahri/hspf2_variable.py` | `HSPF2VariableCapacityEngine.calculate` | `raw_hspf2`, `bin_details` | facade 뒤의 AHRI 210/240-2026 variable-capacity heating |
| Region IV bin table | `data/region_configs/usa_hspf2.json` | n/a | `bin_table` | Table 16 fractional bin hours |
| H1Full fallback | `core/calculators/standards/_ahri/hspf2_points.py` | `resolve_variable_capacity` | `summary.metadata.h12_source` | tested / eq_11_183 / eq_11_185 |
| H22 fallback | `core/calculators/standards/_ahri/hspf2_points.py` | `resolve_variable_capacity` | `summary.metadata.h22_source` | tested / eq_11_44_11_50 |
| intermediate slope | `core/calculators/standards/_ahri/hspf2_performance.py` | `intermediate_capacity_power_at_temp` | `debug_info.intermediate_metadata` | Eq.11.199~11.204 trace |
| Case details | `core/calculators/standards/_ahri/hspf2_variable.py` | `calculate` | `bin_details` | Case I/II/III |
| SEER2 current path | `core/calculators/standards/_ahri/seer2_variable.py` | `calculate` | `SEER2` | public SEER2 facade 뒤의 variable-capacity 냉방 경로 |
| Appendix M SEER engine | `core/calculators/standards/_ahri_m/seer_variable.py` | `AppendixMSeerEngine.calculate` | `raw_seer`, `published_seer` | Appendix M Table 19 seasonal cooling path |
| Appendix M HSPF engine | `core/calculators/standards/_ahri_m/hspf_variable.py` | `AppendixMHspfEngine.calculate` | `raw_hspf`, `published_hspf` | Appendix M Addendum 1 Region IV heating path |
| Appendix M SEER adapter | `apps/calculator/application/ahri_m/seer_adapter.py` | `AhriSeerAdapter.calculate` | `AhriSeerSummary` | M point validation and capability boundary |
| Appendix M HSPF adapter | `apps/calculator/application/ahri_m/hspf_adapter.py` | `AhriHspfAdapter.calculate` | `AhriHspfSummary` | M required/optional point and option semantics |
| Appendix M SEER config | `data/region_configs/usa_m_seer.json` | n/a | bin data / defaults | Appendix M Table 19 |
| Appendix M HSPF config | `data/region_configs/usa_m_hspf.json` | n/a | Region IV bin data / constants | Appendix M Table 20 |

## 9. Critical Implementation Notes

| 주의사항 | 왜 중요한가 | 근거 |
| --- | --- | --- |
| fractional bin hours와 absolute bin hours를 반드시 구분한다. | Table 16 값은 fractional이며, seasonal sum에는 `fractional * HLH`를 사용한다. | AHRI 210/240-2026 Table 16 |
| `BL(tj)`는 Table 16의 `t_zl`, `t_od`, `C_vs`를 사용한다. | 부하선이 바뀌면 Case I/II/III 분기가 모두 바뀐다. | AHRI 210/240-2026 Equation 11.104 |
| H12/H22 missing fallback source를 metadata에 남긴다. | 실측값과 계산값의 HSPF2 차이를 추적해야 한다. | AHRI 210/240-2026 Equation 11.44, Equation 11.50, Equation 11.181~11.186 |
| H2Int는 Low(35°F)와 H2Full 사이여야 한다. | intermediate slope가 envelope 밖으로 나가면 Case II COP interpolation이 물리적으로 깨진다. | AHRI 210/240-2026 Equation 11.199~11.204 |
| Case I에만 PLF가 적용된다. | Case II/III에 PLF를 적용하면 에너지 합산이 달라진다. | AHRI 210/240-2026 Case I path |
| ISO16358-2 Formula 30/50 branch 구조를 AHRI HSPF2에 이식하지 않는다. | ISO의 2°C extended frost point, `P_fe`, `P_ext`, `P_RH` 항은 AHRI HSPF2 Section 11의 Hxx point resolver와 Case I/II/III 구조와 다르다. | AHRI 210/240-2026 Section 11; ISO16358-2 Table 1, Formula 30 |
| defrost 입력은 필수지만, 현재 seasonal multiplier 적용은 `fdef_override` 정책을 따른다. | Equation 11.107 계산값과 실제 raw multiplier 적용을 혼동하면 결과가 달라진다. | AHRI 210/240-2026 Equation 11.107 |
| SEER2는 현재 구현 확인 가능한 범위만 문서화한다. | HSPF2 수준의 공식 parity가 아직 문서화/검증되지 않았다. | Project current implementation |

## 10. Unsupported / Not Yet Implemented

| Item | Reason | Required data to support | Reference |
| --- | --- | --- | --- |
| Appendix M HSPF Region I/II/III/V/VI | 현재 M HSPF는 Region IV Table 20만 canonical table로 사용 | 각 region bin hours, HLH, design/load constants | AHRI 210/240-2017 Appendix M Table 20 |
| Appendix M H42 | M HSPF current point schema는 H01/H11/H1N/H2V/H32와 optional H12/H22로 고정 | M 표준에서 별도 H42 의미와 golden을 확정한 뒤 별도 Design Gate | Appendix M Addendum 1 |
| Appendix M ducted/VRF/multi-split | current M scope 밖 | 장비별 test point schema와 별도 seasonal path | Appendix M |
| M/M1 schema merge | standard edition, point schema, bin/config, metric semantics가 다름 | 명시적 migration 설계와 호환성 승인 | Project boundary |
| HSPF2 Region I/II/III/V/VI | Region IV table만 canonical table로 존재 | 각 region fractional bin hours, HLH, t_od, t_zl, C_vs | AHRI 210/240-2026 Table 16 |
| HSPF2 ducted/VRF/multi-split/dual fuel | 현재 scope 밖 | 장비별 test point schema와 Section 11 분기 | AHRI 210/240-2026 Section 11 |
| HSPF2 automatic use of Eq.11.107 multiplier | 현재 raw는 `fdef_override`를 곱함 | defrost 적용 정책과 golden 재검증 | AHRI 210/240-2026 Equation 11.107 |
| SEER2 additional parity | 현재 official-calculator golden은 variable-capacity 구현 범위만 고정 | off-mode 등 추가 경로의 AHRI 공식 계산기 또는 인증 worksheet | AHRI 210/240 cooling sections |
| SEER2 data externalization | 현재 파일 내 기본 config write side effect 존재 | 별도 JSON schema와 테스트 | Project current implementation |

## 11. Golden Sample Verification

| Case | Source | Expected | Actual | Tolerance | Result |
| --- | --- | ---: | ---: | ---: | --- |
| HSPF2 official Case #1 | `docs/archive/standards_legacy/ahri_hspf2.md` | 9.448025 raw | 9.447720 raw | 약 -0.0003 | pass 기준 |
| HSPF2 official Case #2 | `docs/archive/standards_legacy/ahri_hspf2.md` | 8.821440 raw | 8.821297 raw | 약 -0.0001 | pass 기준 |
| H22 tested | `docs/archive/standards_legacy/ahri_hspf2.md` | rounded 9.52 | rounded 9.52 | project 기준 | pass |
| H12 tested | `docs/archive/standards_legacy/ahri_hspf2.md` | rounded 9.47 | rounded 9.47 | project 기준 | pass |
| Eq.11.183 fallback | `docs/archive/standards_legacy/ahri_hspf2.md` | rounded 9.438 | rounded 9.438 | project 기준 | pass |
| v3 smoke | `test_hspf2_v3_smoke.py` | Region IV, 13 active bins, H42 source trace | assert 기준 | n/a | pass 조건 |
| Case activation | `test_hspf2_v3_low_cases.py` | Case I/II/III 존재, -8°F fractional row | assert 기준 | n/a | pass 조건 |
| H2Int sensitivity | `test_hspf2_v3_h2int.py` | H2Int power change affects raw HSPF2 | assert 기준 | n/a | pass 조건 |
| Appendix M SEER project golden | `tests/test_apps_calculator_ui_ahri_m.py`, `docs/designs/2026-09-01-ahri-210-240-m-seer-hspf-audit-design-spec.md` | published SEER 18.05; CSTL 5349.7; CSEC 296.4 | assert 기준 | n/a | pass |
| Appendix M HSPF project golden | `tests/test_apps_calculator_ui_ahri_m.py`, `docs/designs/2026-09-01-ahri-210-240-m-seer-hspf-audit-design-spec.md` | raw HSPF 10.46286; published HSPF 10.45; DHRmin 15000; load 4605.6; compressor 359.5; auxiliary 80.7 | assert 기준 | n/a | pass |

권장 확인 명령:

```bash
python3 -B test_hspf2_v3_smoke.py
python3 -B test_hspf2_v3_low_cases.py
python3 -B test_hspf2_v3_h2int.py
python3 -B test_hspf2_v3_bincheck.py
```

## 12. References

| Reference | Usage |
| --- | --- |
| `docs/archive/standards_legacy/ahri_hspf2.md` | Historical archive: HSPF2 구현 상세 원본과 official calculator 비교값 |
| `core/calculators/standards/ahri_hspf2.py` | Primary: HSPF2 v3/v2 계산 동작 |
| `core/calculators/standards/ahri_seer2.py` | Primary: 현재 SEER2 계산 가능 범위 |
| `data/region_configs/usa_hspf2.json` | Primary: HSPF2 Region IV bin table, schema, aliases |
| `test_hspf2_v3_*.py` | Primary: HSPF2 smoke, bin, H2Int, case activation 검증 |
| `core/calculators/standards/_ahri_m/seer_variable.py` | Primary: Appendix M SEER seasonal engine |
| `core/calculators/standards/_ahri_m/hspf_variable.py` | Primary: Appendix M HSPF seasonal engine |
| `data/region_configs/usa_m_seer.json` | Primary: Appendix M Table 19 cooling bins and defaults |
| `data/region_configs/usa_m_hspf.json` | Primary: Appendix M Table 20 Region IV heating bins and constants |
| `tests/test_apps_calculator_ui_ahri_m.py` | Primary: Appendix M adapter/UI/batch project golden and surface contract |
| `docs/designs/2026-09-01-ahri-210-240-m-seer-hspf-audit-design-spec.md` | Active design decision evidence; not a replacement for this owner document |
| AHRI 210/240 PDF | Secondary: Section 11, Table 16, Equation 11.104, 11.107, 11.181~11.218 근거 확인 |

## 13. Prompt for Future Agent

```text
AGENTS.md의 Lite 규칙만 따르고, docs/DOCS_GUIDELINES.md, docs/STANDARD_DOC_TEMPLATE.md, docs/FORMULA_REFERENCE_GUIDE.md를 먼저 읽어라. AHRI 작업은 docs/ahri210240/ahri210240_notes.md, docs/ahri210240/ahri210240_dev_notes.md, Appendix M/M1 계산 경로, 각 `data/region_configs/usa*.json`, 관련 테스트를 Primary로 삼고, AHRI PDF는 Section/Table/Equation 확인용 Secondary로만 사용하라. 과거 HSPF2 구현 상세 원본은 필요할 때만 docs/archive/standards_legacy/ahri_hspf2.md를 historical source로 참조하라. HSPF2 및 Appendix M 계산 로직은 명시 지시 없이 수정하지 말고, 문서 정합성 작업은 해당 owner 문서와 이를 직접 참조하는 active design/UI adapter/result record만 scope에 포함하라.
```
