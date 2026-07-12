# AHRI 210/240 Notes

## 1. Overview

이 문서는 AHRI 210/240 계열의 HSPF2와 SEER2 계산 자산을 프로젝트 기준으로 정리한 기준 문서다. Primary 기준은 이 문서와 `docs/ahri210240/ahri210240_dev_notes.md`, `core/calculators/standards/ahri_hspf2.py`, `core/calculators/standards/ahri_seer2.py`, `data/region_configs/usa_hspf2.json`, 관련 HSPF2 테스트 파일이다. AHRI PDF는 Section/Table/Equation 번호 확인용 Secondary 근거로만 사용한다. 과거 HSPF2 구현 상세 원본은 `docs/archive/standards_legacy/ahri_hspf2.md`에 historical source로 보존한다.

현재 프로젝트에서 가장 깊게 검증된 경로는 AHRI 210/240-2026 HSPF2 v3 경로다. 적용 대상은 non-ducted, single-split, variable-capacity, air-to-air heat pump이며, 우선 지역은 Region IV다. 현재 테스트의 variable-capacity HSPF2/SEER2 입력과 expected 결과는 사용자가 AHRI 공식 계산기로 검증한 official-calculator golden으로 고정한다. 신규 deep-result fingerprint는 구조 호환성을 위한 characterization이며 official golden으로 재분류하지 않는다. SEER2의 지원 범위는 여전히 현재 계산 코드의 variable-capacity cooling bin 경로로 한정한다. 근거: AHRI 210/240-2026 Section 11, Table 16, Equation 11.104, Equation 11.107, Equation 11.181~11.218.

## 2. Scope

### Current HSPF2 implementation scope

현재 AHRI HSPF2 구현 우선 지원 범위는 다음과 같다.

- **적용 규격**: AHRI 210/240
- **장비 유형**: non-ducted, single-split, variable-capacity, air-to-air heat pump
- **적용 지역**: Region IV 중심 (`fractional heating bin hours` 사용)
- **생산 경로**: v3 AHRI path (`calculate_hspf2()`)
- **보조열**: 전기 저항 보조열 (`aux_cop` 1.0)
- **Defrost**: demand defrost 기반 (seasonal multiplier는 현재 override 1.0 기본 적용)
- **SEER2 현재 범위**: variable-capacity cooling bin 계산 (확인 가능한 A/B/E/F 중심)

### Future extension boundary

아래 항목은 영구적인 구현 금지가 아니며, 명시적인 확장 요청 및 별도의 설계(Design Gate) 전까지는 현재 지원 범위를 벗어난 확장 후보로 취급한다.

- **장비 유형 확장**: ducted ESP, multi-split, VRF, dual fuel, furnace, zoning, northern heat pump, two-compressor special cases
- **지역 확장**: Region IV 외 지역 (Table 16 bin data 및 HLH 필요)
- **SEER2/Defrost 고도화**: SEER2 full standard parity (off-mode 등 반영), HSPF2 defrost seasonal multiplier 실제 적용 정책 확정

## 3. Glossary Pointer

용어 및 수식 기호의 상세 정의는 `glossary.md`를 참조하라.

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

## 6. Calculation Flow

### HSPF2 v3 Flow

1. 입력 test point를 canonical key로 변환한다. legacy alias는 `H1_Full -> H12`, `H2_Full -> H32`, `H3_Full -> H42`, `A_Full -> A2`로 매핑된다.
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

## 8. Code Mapping

| Standard item | File | Function | Output key | Notes |
| --- | --- | --- | --- | --- |
| HSPF2 entry point | `core/calculators/standards/ahri_hspf2.py` | `calculate_hspf2` | `HSPF2` | v3 production path로 연결 |
| HSPF2 v3 path | `core/calculators/standards/ahri_hspf2.py` | `_calculate_hspf2_v3_ahri` | `raw_hspf2`, `bin_details` | AHRI 210/240-2026 variable-capacity heating |
| Region IV bin table | `data/region_configs/usa_hspf2.json` | n/a | `bin_table` | Table 16 fractional bin hours |
| H1Full fallback | `core/calculators/standards/ahri_hspf2.py` | `_calculate_hspf2_v3_ahri` | `summary.metadata.h12_source` | tested / eq_11_183 / eq_11_185 |
| H22 fallback | `core/calculators/standards/ahri_hspf2.py` | `_calculate_hspf2_v3_ahri` | `summary.metadata.h22_source` | tested / eq_11_44_11_50 |
| intermediate slope | `core/calculators/standards/ahri_hspf2.py` | `_cert_intermediate_capacity_power_at_temp` | `debug_info.intermediate_metadata` | Eq.11.199~11.204 trace |
| Case details | `core/calculators/standards/ahri_hspf2.py` | `_calculate_hspf2_v3_ahri` | `bin_details` | Case I/II/III |
| HSPF2 legacy | `core/calculators/standards/ahri_hspf2.py` | `calculate_hspf2_v2` | `HSPF2` | legacy reference only |
| SEER2 current path | `core/calculators/standards/ahri_seer2.py` | `calculate_seer2` | `SEER2` | 현재 구현 확인 가능한 냉방 경로 |

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
| AHRI 210/240 PDF | Secondary: Section 11, Table 16, Equation 11.104, 11.107, 11.181~11.218 근거 확인 |

## 13. Prompt for Future Agent

```text
AGENTS.md의 Lite 규칙만 따르고, docs/DOCS_GUIDELINES.md, docs/STANDARD_DOC_TEMPLATE.md, docs/FORMULA_REFERENCE_GUIDE.md를 먼저 읽어라. AHRI 작업은 docs/ahri210240/ahri210240_notes.md, docs/ahri210240/ahri210240_dev_notes.md, core/calculators/standards/ahri_hspf2.py, core/calculators/standards/ahri_seer2.py, data/region_configs/usa_hspf2.json, test_hspf2_v3_*.py를 Primary로 삼고, AHRI PDF는 Section/Table/Equation 확인용 Secondary로만 사용하라. 과거 HSPF2 구현 상세 원본은 필요할 때만 docs/archive/standards_legacy/ahri_hspf2.md를 historical source로 참조하라. HSPF2 계산 로직은 명시 지시 없이 수정하지 말고, 문서 작업이면 docs/ahri210240/ 하위만 수정하라.
```
