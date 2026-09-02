# AHRI 210/240 Dev Notes

## 1. Purpose

이 문서는 AHRI 210/240 Appendix M SEER/HSPF와 Appendix M1 SEER2/HSPF2 계산 자산을 수정하거나 검증하는 개발자와 AI Agent를 위한 작업 지침이다. 현재 프로젝트에서는 HSPF2 v3가 가장 중요한 M1 생산 경로이며, Appendix M은 별도의 2017/Addendum 1 variable-speed 경로로 다룬다.

Primary 기준은 `docs/ahri210240/ahri210240_notes.md`, 이 문서, Appendix M/M1 standard engine과 application adapter, `data/region_configs/usa_m_seer.json`, `data/region_configs/usa_m_hspf.json`, `data/region_configs/usa_hspf2.json`, 관련 AHRI 테스트다. 현재 테스트의 variable-capacity HSPF2/SEER2 입력과 expected 결과 및 Appendix M project golden은 각 standard path의 계약을 보호하며, refactor를 맞추기 위해 변경하지 않는다. AHRI PDF는 Section/Table/Equation 번호 확인용 Secondary 근거로만 사용한다. 과거 HSPF2 구현 상세 원본은 `docs/archive/standards_legacy/ahri_hspf2.md`에 historical source로 보존한다. 근거: AHRI 210/240-2017 Appendix M Tables 19/20, Addendum 1, AHRI 210/240-2026 Section 11, Table 16, Equation 11.104, Equation 11.107.

도메인 용어 및 코드 변수명 정의는 `ahri210240_glossary.md`를 참조하라.

### M/M1 boundary

M과 M1은 이름이 비슷해도 standard edition, 시험점, bin/config, fallback, 결과 지표가 다르다. M 문서나 코드 작업에서 M1 `H2Int`/`H42` schema, M1 Region IV table, M1 SEER2/HSPF2 rounding 또는 product policy를 재사용하지 않는다. 공통 UI table interaction은 공용 table contract를 따르되, M/M1 계산 의미와 result schema는 각 owner가 유지한다.

## 2. Top Implementation Pitfalls

| Pitfall | Symptom | Cause | Prevention | Reference |
| --- | --- | --- | --- | --- |
| fractional bin hours를 그대로 absolute hour로 사용 | total load와 total energy가 작아진다. | Table 16 fractional 값을 HLH와 곱하지 않음 | `fractional_bin_hours * heating_load_hours`를 seasonal sum에 사용한다. | AHRI 210/240-2026 Table 16 |
| `BL(tj)` 부하선에 임의 상수 사용 | Case I/II/III bin 분포가 바뀐다. | `t_zl`, `t_od`, `C_vs`를 table 기준으로 쓰지 않음 | Region IV table의 `zero_load_temp_f`, `outdoor_design_temp_f`, `variable_capacity_slope_factor`를 사용한다. | AHRI 210/240-2026 Equation 11.104 |
| H12/H22 optional fallback을 추적하지 않음 | official calculator와 차이가 났을 때 원인 추적이 어렵다. | tested/fallback source metadata 누락 | `h12_source`, `h22_source`를 유지한다. | AHRI 210/240-2026 Equation 11.44, 11.50, 11.181~11.186 |
| H2Int envelope 검증을 완화 | Case II COP interpolation이 비물리적으로 된다. | H2Int가 Low(35°F)와 H2Full 사이가 아님 | `N_Hq`, `N_HE`가 0~1인지 fail-fast 한다. | AHRI 210/240-2026 Equation 11.199~11.204 |
| Case I PLF를 Case II/III에도 적용 | energy denominator가 과대 또는 과소 계산된다. | cycling correction 적용 위치 혼동 | Case I에만 `PLF = 1 - Cd * (1 - HLF)` 적용한다. | AHRI 210/240-2026 Case I path |
| ISO16358 HSPF Formula 30/50 branch를 AHRI HSPF2에 이식 | Case I/II/III energy trace가 표준과 맞지 않는다. | ISO Table 1의 2°C/-7°C extended frost matrix와 AHRI HSPF2 Hxx test point 체계를 혼동함 | AHRI HSPF2는 Section 11의 Case I/II/III, H01/H11/H12/H22/H2Int/H32/H42 경로만 사용한다. ISO `P_fe`, `P_ext`, `P_RH` 구조는 AHRI path에 넣지 않는다. | AHRI 210/240-2026 Section 11; ISO16358-2 Table 1, Formula 30 |
| defrost trace와 multiplier 적용을 혼동 | raw HSPF2가 예상과 다르게 변한다. | Eq.11.107 계산값과 `fdef_override` 적용 정책 혼동 | `summary.metadata.defrost`의 `f_def_seasonal`, `fdef_used`, `seasonal_defrost_multiplier_applied`를 함께 확인한다. | AHRI 210/240-2026 Equation 11.107 |
| official golden과 characterization을 혼동 | refactor 실패와 구조 snapshot 차이를 구분하지 못한다. | 새로 생성한 deep-result fingerprint를 공식 golden으로 오인 | 기존 사용자 확인 expected만 official-calculator golden으로 두고, 신규 fingerprint는 structural characterization으로 표기한다. | Project decision 2026-07-12 |

## 3. Correct Calculation Order

### HSPF2 v3

1. 입력 key를 canonical schema로 변환한다.
2. `defrost_t_test_minutes`, `defrost_t_max_minutes`, `t_off`, `t_on`을 검증한다.
3. 필수 canonical point `H01`, `H11`, `H1N`, `H2Int`, `H32`, `A2`가 있는지 확인한다.
4. Region IV canonical table에서 bin temperature, fractional hours, HLH, `t_zl`, `t_od`, `C_vs`를 읽고 검증한다. 근거: AHRI 210/240-2026 Table 16.
5. H12 source를 결정한다. H12 tested, Eq.11.183 fallback, Eq.11.185 fallback 중 하나다.
6. H22 source를 결정한다. H22 tested 또는 Eq.11.44/11.50 fallback 중 하나다.
7. H42가 있으면 저온 full-speed anchor로 사용한다.
8. 각 bin에서 `BL(tj)`를 계산한다. 근거: AHRI 210/240-2026 Equation 11.104.
9. 각 bin에서 full, low, intermediate capacity/power를 계산한다.
10. `BL <= q_low`, `q_low < BL < q_full`, `BL >= q_full` 순서로 Case I/II/III를 결정한다.
11. Case별 compressor heat/energy와 auxiliary heat/energy를 계산한다.
12. bin별 `q_j`, `E_j`를 합산하고 `raw_hspf2_base`를 만든다.
13. `fdef_override`를 곱해 `raw_hspf2`를 만들고, 0.025 단위로 반올림한다.

### SEER2 Current

1. config에서 cooling bin table, point temperature, scale factor, v-factor를 읽는다.
2. `A_Full`, `B_Full`, `B_Low`, `E_Int`, `F_Low`를 입력받는다.
3. E intermediate point의 envelope 위치로 cooling intermediate slope를 계산한다.
4. 각 bin에서 low/full/intermediate capacity와 power를 계산한다.
5. building load를 계산하고 Case 1, 2.1, 2.2, 3으로 분기한다.
6. bin별 cooling amount와 energy를 합산해 SEER2를 산출한다.

### Appendix M SEER/HSPF

1. M SEER는 Appendix M Table 19의 `A2`, `B2`, `EV`, `B1`, `F1` 다섯 point pair를 사용한다. `EV`는 canonical key이고 UI display label만 `Ev`다.
2. M SEER는 F1→B1 low curve, B2→A2 full curve, EV에서 계산한 intermediate slope와 three-anchor quadratic EER path를 사용한다. M1 SEER2의 A/B/E/F schema로 변환하지 않는다.
3. M HSPF는 Appendix M Table 20 Region IV bin data와 필수 `H01`, `H11`, `H1N`, `H2V`, `H32`를 사용한다. `H12`, `H22`는 독립 optional pair이며 `H42`는 현재 M schema에 없다.
4. M HSPF는 H2V의 low/full envelope 위치를 기준으로 intermediate COP를 계산하고, Case I/II/III seasonal accumulation과 resistance auxiliary를 적용한다.
5. M HSPF demand defrost가 꺼져 있으면 timing input은 `N/A` presentation이고 credit은 `1.0`; 켜져 있으면 Defrost Test/Max 입력을 사용해 M 2017 defrost factor를 계산한다.

## 4. Data Model Notes

| Data | Location | Meaning | Validation |
| --- | --- | --- | --- |
| canonical HSPF2 bin table | `data/region_configs/usa_hspf2.json` | Region IV Table 16 fractional bin hours | length, non-negative, sum 0.757 |
| HSPF2 test point schema | `data/region_configs/usa_hspf2.json` | H01/H11/H12/H1N/H22/H2Int/H32/H42/A2 alias and temperatures | canonical key lookup |
| HSPF2 public aliases | `data/region_configs/usa_hspf2.json` | accepted public names to canonical names | conflicting value fail-fast |
| HSPF2 bin details | HSPF2 return dict | bin별 case, BL, q/p low/int/full, COP, auxiliary | smoke and case tests inspect |
| SEER2 config | `core/calculators/standards/ahri_seer2.py` current config block and external config path | cooling bin and point temperatures | limited validation |
| Appendix M SEER config | `data/region_configs/usa_m_seer.json` | Appendix M Table 19 cooling bins, sizing factor, CDc default | point order and fractional-hour sum |
| Appendix M HSPF config | `data/region_configs/usa_m_hspf.json` | Appendix M Table 20 Region IV bins, design/load constants, CDh default | point order, bin lengths, standardized DHR |
| Appendix M SEER point schema | `apps/calculator/application/ahri_m/seer_adapter.py` | A2/B2/EV/B1/F1 capacity/power pairs | all pairs > 0; EV UI alias is display-only |
| Appendix M HSPF point schema | `apps/calculator/application/ahri_m/hspf_adapter.py` | required H01/H11/H1N/H2V/H32 and optional H12/H22 pairs | optional pairs are both blank or both populated |

`data/region_configs/usa_hspf2.json`은 canonical Region IV table, active point schema,
`A_Full -> A2` public alias, production defaults만 HSPF2 runtime contract로
유지한다. retired v2 `bin_data`, point temperatures, constants는 제거됐다.

현재 `data/region_configs/usa.json`은 SEER2/cooling flat config이고, `data/region_configs/usa_hspf2.json`은 HSPF2/heating flat config이다. 두 계산기 모두 top-level key를 직접 읽으므로 단순 병합은 금지한다. 완전 통합은 `cooling` / `heating` namespace schema migration 이후 별도 검토한다.

Appendix M의 `usa_m_seer.json`과 `usa_m_hspf.json`도 각각 독립적인 flat/config shape와 standard scope를 가진다. M config를 `usa.json` 또는 `usa_hspf2.json`에 병합하거나 M point를 M1 alias로 승격하지 않는다.

## 5. Interpolation / Extrapolation Rules

| Path | Rule | Boundary behavior | Reference |
| --- | --- | --- | --- |
| H1Full missing | H12 없으면 H1N 또는 H32 기반 fallback | source metadata 기록 | AHRI 210/240-2026 Equation 11.183~11.186 |
| H22 missing | H32와 H1Full_calc로 H2Full 계산 | source metadata 기록 | AHRI 210/240-2026 Equation 11.44, Equation 11.50 |
| Full speed `tj >= 45°F` | H32~H1Full line에 H1N/H1Full ratio 적용 | high bin path | AHRI 210/240-2026 Equation 11.209~11.210 |
| Full speed `17°F < tj < 45°F` | H32~H22 line | mid bin path | AHRI 210/240-2026 Equation 11.213~11.214 |
| Full speed with H42 | H42~H32 또는 H42 anchored low line | low bin path | AHRI 210/240-2026 Equation 11.215~11.218 |
| Low speed non-limiting | H01~H11 line | all low bins | AHRI 210/240-2026 Equation 11.187~11.188 |
| Low speed minimum-limiting | H01/H11/H2Int/int path piecewise | 47°F, 35°F 기준 분기 | AHRI 210/240-2026 Equation 11.189~11.194 |
| Intermediate speed | Eq.11.199~11.204 slope | envelope 밖이면 ValueError | AHRI 210/240-2026 Equation 11.199~11.204 |
| SEER2 low/full/int | F/B/A/E points로 온도 선형 계산 | 현재 구현 범위 | Project current implementation |
| M SEER low/full | F1→B1 및 B2→A2 선형 curve | Appendix M cooling bins | Appendix M Table 19 |
| M SEER intermediate | EV의 87°F envelope 위치에서 capacity/power slope를 계산하고 three-anchor quadratic EER를 사용 | `NQ`, `NE`는 0~1 | Appendix M Table 19 |
| M HSPF H1Full | H12 measured, H1N same-speed, 또는 H32 slope fallback | source를 `h12_source`에 기록 | Appendix M Addendum 1 |
| M HSPF H2Full | H22 measured 또는 H32/H1Full 기반 fallback | source를 `h22_source`에 기록 | Appendix M Addendum 1 |
| M HSPF intermediate | H2V와 35°F low/full 값으로 capacity/power slope를 만들고 delivered load 기준 COP를 보간 | `NQ`, `NE`는 0~1 | Appendix M Addendum 1 |

## 6. Degradation / Correction Factor Rules

| Rule | Current handling | Why | Reference |
| --- | --- | --- | --- |
| Heating Case I PLF | `PLF = max(0.01, 1 - Cd * (1 - HLF))` | low-speed cycling 손실 반영 | AHRI 210/240-2026 Case I path |
| Heating Case II | PLF 1.0, COP_bin interpolation | 용량이 low와 full 사이이므로 intermediate COP를 사용 | AHRI 210/240-2026 Case II path |
| Heating Case III | PLF 1.0, full-speed plus auxiliary | full capacity 부족분은 보조열 | AHRI 210/240-2026 Case III path |
| Cross-standard branch boundary | ISO16358-2 Formula 30의 `P_fe`, `P_ext`, `P_RH` 항은 AHRI HSPF2 v3 denominator 구조로 가져오지 않는다. | AHRI HSPF2는 Section 11 Case I/II/III와 Hxx point resolver가 기준이며, ISO 2°C extended frost branch와 test matrix는 별도 표준의 해석이다. | AHRI 210/240-2026 Section 11; ISO16358-2 Formula 30 |
| `delta_j` | `temp <= t_off` 또는 COP < 1이면 0, `temp <= t_on`이면 0.5, 그 외 1.0 | heat pump availability 반영 | AHRI 210/240-2026 Section 11 |
| Defrost | Eq.11.107 값을 trace하고 raw에는 `fdef_override` 적용 | 현재 정책을 명확히 추적 | AHRI 210/240-2026 Equation 11.107 |
| SEER2 low cycling | Case 1에서 `PLF = 1 - cd_low * (1 - CLF)` | low cooling cycling 손실 | Project current implementation |

### HSPF2 v3 diagnostics contract

HSPF2 v3 diagnostics는 계산 경로 회귀를 추적하기 위한 project trace다. 테스트가 아래 key/value를 guard로 사용하므로, rename 또는 위치 이동은 별도 phase에서만 수행한다.

`summary.metadata` contract:

| Key | Current values / type | Meaning |
| --- | --- | --- |
| `h12_source` | `tested`, `eq_11_183`, `eq_11_185` | H12/H1Full source 또는 fallback equation trace |
| `h22_source` | `tested`, `eq_11_44_11_50` | H22/H2Full source 또는 fallback equation trace |
| `minimum_speed_limited` | boolean | minimum-speed limiting branch 활성 여부 |
| `case_i_low_source` | `eq_11_187_188`, `eq_11_189_194` | Case I low-speed capacity/power path trace |
| `t_OBO` | number | AHRI v3 path에서 사용하는 OBO boundary trace |

Top-level diagnostics:

| Key | Current values / type | Meaning |
| --- | --- | --- |
| `h42_source` | `provided`, `not_provided` | H42 low-temperature full-speed anchor 제공 여부. 현재 `summary.metadata`가 아니라 result top-level key이며, 이번 phase에서는 위치를 변경하지 않는다. |

`bin_details[].debug_info` contract:

| Key | Current values / type | Meaning |
| --- | --- | --- |
| `full_capacity_method` | `eq_11_209_11_210`, `eq_11_213_11_214`, `h4full_low_temp_line`, `no_h4full_h1full_h3full_line` | bin별 full-speed capacity/power path trace |
| `low_capacity_method` | `eq_11_187_188`, `eq_11_189_194` | bin별 low-speed path trace |
| `intermediate_capacity_method` | `ahri_210_240_2026_eq_11_199_to_11_204` | H2Int intermediate interpolation path trace |
| `intermediate_metadata` | dict | H2Int envelope와 slope trace. 주요 key는 `N_Hq`, `N_HE`, `M_Hq`, `M_HE`, `q_low_35`, `p_low_35`이다. |

Naming policy note:
- 현재 source/method 값은 equation 기반 이름(`eq_11_183`, `eq_11_44_11_50`)과 descriptive 이름(`h4full_low_temp_line`, `not_provided`)이 섞여 있다.
- 이번 phase에서는 기존 key/value를 rename하지 않는다.
- `h42_source`를 `summary.metadata`로 이동하거나 mirror하는 작업은 code/API 변경 가능성이 있으므로 보류한다.
- diagnostics key/value를 변경해야 할 경우 먼저 테스트와 문서 contract를 함께 갱신한다.

## 7. Debugging Checklist

| Check | What to inspect | Expected |
| --- | --- | --- |
| canonical key | `normalize_public_test_points()` result | HSPF2 production 필수 key가 모두 존재 |
| Region IV table | `bin_table.fractional_bin_hours_sum` | 0.757 |
| absolute hours | `bin_details.hours` | fractional * 1701 |
| H12 fallback | `summary.metadata.h12_source` | tested / eq_11_183 / eq_11_185 |
| H22 fallback | `summary.metadata.h22_source` | tested / eq_11_44_11_50 |
| H2Int envelope | `intermediate_metadata.N_Hq`, `N_HE` | 0~1 |
| Case distribution | `operating_case` set | smoke fixture에서 Case I/II/III 존재 |
| Case I PLF | `PLF_j` | `1 - Cd * (1 - HLF)`와 일치 |
| fractional availability | `delta_j` | smoke fixture에서 -8°F row가 0.5 |
| heat conservation | `q_j == q_comp + q_aux` | tolerance 내 일치 |
| energy conservation | `E_j == e_comp + e_aux` | tolerance 내 일치 |
| defrost trace | `summary.metadata.defrost` | 입력 clamp와 override 상태 확인 |

## 8. Test Strategy

| Change type | Required checks |
| --- | --- |
| 문서만 변경 | docs 파일만 변경되었는지 확인 |
| HSPF2 equation path 변경 | `test_hspf2_v3_smoke.py`, `test_hspf2_v3_low_cases.py`, `test_hspf2_v3_h2int.py`, `test_hspf2_v3_bincheck.py` |
| HSPF2 bin table 변경 | fractional sum, active bin count, total load/energy 재검증 |
| H12/H22 fallback 변경 | official comparison case와 metadata source 확인 |
| H2Int 경로 변경 | H2Int power sensitivity test 필수 |
| Case I/II/III 변경 | conservation test와 case activation test 필수 |
| SEER2 변경 | 기존 official-calculator golden과 deep characterization을 먼저 실행한 뒤 변경 |
| Appendix M 문서/label/batch 변경 | `tests/test_apps_calculator_ui_ahri_m.py`의 adapter, UI, batch golden과 display contract를 확인 |
| Appendix M calculation path 변경 | M SEER 18.05 / M HSPF 10.45 project golden, optional H12/H22 pair semantics, defrost and Region IV boundary를 확인 |

권장 명령:

```bash
python3 -B test_hspf2_v3_smoke.py
python3 -B test_hspf2_v3_low_cases.py
python3 -B test_hspf2_v3_h2int.py
python3 -B test_hspf2_v3_bincheck.py
```

## 9. Golden Case Strategy

| Case | Purpose | Current source |
| --- | --- | --- |
| Official Case #1 | AHRI 공식 계산기와 raw HSPF2 근접성 확인 | `docs/archive/standards_legacy/ahri_hspf2.md` |
| Official Case #2 | 다른 A2 anchor에서 공식 계산기 근접성 확인 | `docs/archive/standards_legacy/ahri_hspf2.md` |
| H22 tested | optional tested point 우선 사용 확인 | `docs/archive/standards_legacy/ahri_hspf2.md` |
| H12 tested | tested H1Full path 확인 | `docs/archive/standards_legacy/ahri_hspf2.md` |
| Eq.11.183 | H1N same speed fallback 확인 | `docs/archive/standards_legacy/ahri_hspf2.md` |
| H2Int sensitivity | intermediate power가 Case II COP에 영향을 주는지 확인 | `test_hspf2_v3_h2int.py` |
| Case activation | Case I/II/III, fractional availability 확인 | `test_hspf2_v3_low_cases.py` |

Appendix M project golden은 `tests/test_apps_calculator_ui_ahri_m.py`와 active design spec에 고정한다. 기준 fixture에서 M SEER는 published 18.05, M HSPF는 raw 10.46286 및 published 10.45이며, 이 값은 M1 official-calculator golden과 섞지 않는다. M HSPF 결과 표시는 DHRmin 15000, Heating Load 4605.6, Compressor Input 359.5, Auxiliary Input 80.7을 사용한다.

SEER2의 현재 variable-capacity 테스트 입력과 expected는 사용자가 AHRI 공식 계산기로 검증한 golden이다. 다만 이 결정은 현재 지표와 결과를 보호하며, off-mode나 추가 standard parity를 검증했다는 의미는 아니다.

## 10. Future Refactor Notes

| Topic | Keep current behavior until | Refactor direction | Reference |
| --- | --- | --- | --- |
| HSPF2 v2 legacy path | v3 migration 안정성 확인 완료까지 | legacy reference로만 유지 | Project compatibility |
| Defrost multiplier | 정책과 golden이 확정될 때까지 | Eq.11.107 seasonal multiplier 적용 여부 명확화 | AHRI 210/240-2026 Equation 11.107 |
| Region expansion | Region IV 외 table 검증 전까지 | region parameterized table 구조 | AHRI 210/240-2026 Table 16 |
| SEER2 config | config/schema migration 승인 전까지 | external JSON schema와 tests 정비 | AHRI 210/240 cooling sections |
| SEER2 off-mode | 공식 요구와 입력 단위 확인 전까지 | `p_w_off` 실제 seasonal denominator 반영 검토 | AHRI 210/240 cooling sections |
| Appendix M/M1 boundary | 두 standard edition의 schema와 golden이 분리되어 있는 동안 | 공통 adapter가 필요해도 metric/point/config owner는 분리 유지 | Project design spec |
| Appendix M region expansion | M HSPF Region IV Table 20 외 검증 전까지 | region parameterized table과 별도 golden을 Design Gate로 추가 | Appendix M Table 20 |

계산기 파일은 Lite 규칙상 명시 지시 없이 수정하지 않는다. Production `calculate_hspf2()`는 보호 대상이며 retired v2 public method는 제공하지 않는다.

### Final internal ownership

Public import path와 method/result contract는 `ahri_hspf2.py`, `ahri_seer2.py` facade가 소유한다. 구현은 `core/calculators/standards/_ahri/`의 private owner로 분리되며 application, UI, capability, ML envelope에 노출하지 않는다.

| Owner | Responsibility |
| --- | --- |
| `hspf2_context.py` | config 로드, Region IV validation, seasonal runtime context |
| `hspf2_points.py` | alias/case normalization, validation, H12/H22/H42 fallback metadata |
| `hspf2_performance.py` | variable-capacity low/intermediate/full performance와 building load |
| `hspf2_variable.py` | Case I/II/III bin loop와 seasonal accumulation |
| `hspf2_result.py` | 기존 raw result, duplicate totals, summary, diagnostics mapping assembly |
| `seer2_variable.py` | A/B/E/F curves, Case 1/2.1/2.2/3, fractional seasonal result |
| `numeric.py` | 두 engine에서 의미가 동일함이 확인된 safe division과 linear interpolation만 공유 |

Two-stage/triple-capacity는 현재 variable formula body에 조건문으로 누적하지 않고, 후속 design에서 facade 뒤의 sibling engine으로 추가한다.

## 11. HSPF2 v3 구현 현황 및 검증 기준

### 구현 현황
- **대상 규격**: AHRI 210/240-2026 (Region IV 기준)
- **핵심 엔진**: `core/calculators/standards/_ahri/hspf2_variable.py` (stable `ahri_hspf2.py` facade를 통해 호출)
- **입력 체계**: `normalize_public_test_points()`를 통해 active public alias를 canonical 키(H01, H11, H12, H1N, H22, H2Int, H32, H42, A2)로 통합 관리함.
- **Variable exact allowlist**: required `H01`, `H11`, `H1N`, `H2Int`,
  `H32`, `A2`; optional `H12`, `H22`, `H42`만 계산 입력으로
  허용한다. 전체 schema의 `H2V`, `B2`, `C2`, `D2`, `E2`는
  variable engine이 소비하지 않으므로 fail-fast한다.
- **Unit type**: derived H12는 split(`split`, `split_system`,
  `split-system`) 또는 packaged(`single_package`, `single-package`,
  `package`, `packaged`)만 허용한다. 명시 selector 오타/null과
  `unit_type`/`system_type` 충돌은 fail-fast한다.
- **상태**: Full variable-capacity path 구현 및 `tests/test_ahri_hspf2*.py` 기반 smoke/golden/edge regression 보호망 확보.

### 검증 및 디버깅 기준
- **Metadata Trace**: `h12_source`, `h22_source` 등을 통해 H12/H22 fallback 발생 여부를 반드시 확인해야 함.
- **Bin-level 검증**: 결과 딕셔너리의 `bin_details`를 통해 각 Bin별 `operating_case` (I, II, III), `delta_j` (availability), 보조열(`auxiliary_energy`) 투입 시점을 전수 조사할 수 있음.
- **Intermediate Path**: `intermediate_metadata`의 `N_Hq`, `N_HE`가 0~1 범위 내에 있는지 확인하여 비물리적 보간 여부를 감시함.

### 주요 테스트 세트
로직 수정 시 아래 테스트를 최우선으로 실행하여 회귀(Regression)를 방어함:
- `tests/test_ahri_hspf2_v3_smoke.py`: 기본 연산 및 v2/v3 비교
- `tests/test_ahri_hspf2_low_cases.py`: 저온 영역 Case activation 및 에너지 보존 검증
- `tests/test_ahri_hspf2_h2int.py`: Intermediate speed 민감도 테스트
- `tests/test_ahri_hspf2_bincheck.py`: Bin 단위의 물리적 타당성(음수 방지 등) 검증

### 주의사항
- `fdef_override` 정책: Eq. 11.107에 따른 seasonal defrost multiplier 적용 여부를 `summary.metadata.defrost`에서 확인 가능함.
- **유지보수**: AHRI 공식 계산기(Official Calculator)와의 Parity를 유지하는 것이 최우선이며, 임의의 scaling factor 도입을 금지함.

## 12. Prompt Snippets for Agent

### AHRI 문서 작업

```text
AGENTS.md의 Lite 규칙만 따르고 docs/DOCS_GUIDELINES.md, docs/STANDARD_DOC_TEMPLATE.md, docs/FORMULA_REFERENCE_GUIDE.md를 먼저 읽어라. AHRI 문서는 docs/ahri210240/ahri210240_notes.md, docs/ahri210240/ahri210240_dev_notes.md, AHRI HSPF2/SEER2 계산 코드, 관련 tests를 Primary로 삼고, AHRI PDF는 Section/Table/Equation 확인용 Secondary로만 사용하라. 과거 HSPF2 구현 상세 원본은 필요할 때만 docs/archive/standards_legacy/ahri_hspf2.md를 historical source로 참조하라. 문서 작업이면 docs/ahri210240/ 하위만 수정하라.
```

이 snippet의 기존 `docs/ahri210240/` 한정 문구는 표준 owner 문서에 대한 기본값이다. M UI adapter 또는 조건부 Result Record의 직접 정합성 보정이 필요한 경우에는 active design spec과 Result Record Workflow가 허용하는 직접 참조 문서까지 명시적으로 포함한다.

### HSPF2 계산 작업

```text
AGENTS.md Lite 규칙을 먼저 읽어라. HSPF2는 variable-capacity, dual-stage, triple-capacity-northern production 경로를 보호한다. calculate_hspf2()는 명시 지시 없이 수정하지 말고, 변경 후 active product golden과 product dispatch 테스트를 실행하라.
```

### SEER2 정비 작업

```text
AGENTS.md Lite 규칙을 먼저 읽어라. SEER2는 현재 variable-capacity official-calculator golden expected를 변경하지 말고, 현재 구현 확인 범위 밖의 off-mode나 추가 parity를 주장하지 말라. 계산 해석 변경은 별도 golden evidence와 승인 후 진행하라.
```
