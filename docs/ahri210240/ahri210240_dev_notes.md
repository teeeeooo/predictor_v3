# AHRI 210/240 Dev Notes

## 1. Purpose

이 문서는 AHRI 210/240 HSPF2/SEER2 계산 자산을 수정하거나 검증하는 개발자와 AI Agent를 위한 작업 지침이다. 현재 프로젝트에서는 HSPF2 v3가 가장 중요한 생산 경로이며, SEER2는 현재 계산 코드에서 확인 가능한 범위만 다룬다.

Primary 기준은 `docs/skills/ahri_hspf2.md`, `core/calculator_ahri_hspf2.py`, `core/calculator_ahri_seer2.py`, `data/usa_hspf2.json`, `test_hspf2_v3_*.py`다. AHRI PDF는 Section/Table/Equation 번호 확인용 Secondary 근거로만 사용한다. 근거: AHRI 210/240-2026 Section 11, Table 16, Equation 11.104, Equation 11.107.

도메인 용어 및 코드 변수명 정의는 `glossary.md`를 참조하라.

## 2. Top Implementation Pitfalls

| Pitfall | Symptom | Cause | Prevention | Reference |
| --- | --- | --- | --- | --- |
| fractional bin hours를 그대로 absolute hour로 사용 | total load와 total energy가 작아진다. | Table 16 fractional 값을 HLH와 곱하지 않음 | `fractional_bin_hours * heating_load_hours`를 seasonal sum에 사용한다. | AHRI 210/240-2026 Table 16 |
| `BL(tj)` 부하선에 임의 상수 사용 | Case I/II/III bin 분포가 바뀐다. | `t_zl`, `t_od`, `C_vs`를 table 기준으로 쓰지 않음 | Region IV table의 `zero_load_temp_f`, `outdoor_design_temp_f`, `variable_capacity_slope_factor`를 사용한다. | AHRI 210/240-2026 Equation 11.104 |
| H12/H22 optional fallback을 추적하지 않음 | official calculator와 차이가 났을 때 원인 추적이 어렵다. | tested/fallback source metadata 누락 | `h12_source`, `h22_source`를 유지한다. | AHRI 210/240-2026 Equation 11.44, 11.50, 11.181~11.186 |
| H2Int envelope 검증을 완화 | Case II COP interpolation이 비물리적으로 된다. | H2Int가 Low(35°F)와 H2Full 사이가 아님 | `N_Hq`, `N_HE`가 0~1인지 fail-fast 한다. | AHRI 210/240-2026 Equation 11.199~11.204 |
| Case I PLF를 Case II/III에도 적용 | energy denominator가 과대 또는 과소 계산된다. | cycling correction 적용 위치 혼동 | Case I에만 `PLF = 1 - Cd * (1 - HLF)` 적용한다. | AHRI 210/240-2026 Case I path |
| defrost trace와 multiplier 적용을 혼동 | raw HSPF2가 예상과 다르게 변한다. | Eq.11.107 계산값과 `fdef_override` 적용 정책 혼동 | `summary.metadata.defrost`의 `f_def_seasonal`, `fdef_used`, `seasonal_defrost_multiplier_applied`를 함께 확인한다. | AHRI 210/240-2026 Equation 11.107 |
| SEER2를 HSPF2와 같은 검증 수준으로 가정 | 문서와 실제 신뢰 수준이 불일치한다. | SEER2 official parity 테스트가 부족함 | SEER2는 현재 구현 확인 범위로만 설명한다. | Project current implementation |

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

## 4. Data Model Notes

| Data | Location | Meaning | Validation |
| --- | --- | --- | --- |
| canonical HSPF2 bin table | `data/usa_hspf2.json` | Region IV Table 16 fractional bin hours | length, non-negative, sum 0.757 |
| HSPF2 test point schema | `data/usa_hspf2.json` | H01/H11/H12/H1N/H22/H2Int/H32/H42/A2 alias and temperatures | canonical key lookup |
| HSPF2 legacy aliases | `data/usa_hspf2.json` | old names to canonical names | conflicting value fail-fast |
| HSPF2 bin details | HSPF2 return dict | bin별 case, BL, q/p low/int/full, COP, auxiliary | smoke and case tests inspect |
| SEER2 config | `core/calculator_ahri_seer2.py` current config block and external config path | cooling bin and point temperatures | limited validation |

`data/usa_hspf2.json`의 `_comment`에는 초기 scaffold 잔여 문구가 있으나, v3 경로는 `canonical_hspf2_bin_tables.heating.region_iv`를 사용한다. 문서 작성 시 legacy `bin_data`와 canonical Region IV table을 혼동하면 안 된다.

현재 `data/region_configs/usa.json`은 SEER2/cooling flat config이고, `data/usa_hspf2.json`은 HSPF2/heating flat config이다. 두 계산기 모두 top-level key를 직접 읽으므로 단순 병합은 금지한다. 단기 방향은 HSPF2 config를 `data/region_configs/usa_hspf2.json`으로 위치 이동하는 것이며, 완전 통합은 `cooling` / `heating` namespace schema migration 이후 별도 검토한다.

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

## 6. Degradation / Correction Factor Rules

| Rule | Current handling | Why | Reference |
| --- | --- | --- | --- |
| Heating Case I PLF | `PLF = max(0.01, 1 - Cd * (1 - HLF))` | low-speed cycling 손실 반영 | AHRI 210/240-2026 Case I path |
| Heating Case II | PLF 1.0, COP_bin interpolation | 용량이 low와 full 사이이므로 intermediate COP를 사용 | AHRI 210/240-2026 Case II path |
| Heating Case III | PLF 1.0, full-speed plus auxiliary | full capacity 부족분은 보조열 | AHRI 210/240-2026 Case III path |
| `delta_j` | `temp <= t_off` 또는 COP < 1이면 0, `temp <= t_on`이면 0.5, 그 외 1.0 | heat pump availability 반영 | AHRI 210/240-2026 Section 11 |
| Defrost | Eq.11.107 값을 trace하고 raw에는 `fdef_override` 적용 | 현재 정책을 명확히 추적 | AHRI 210/240-2026 Equation 11.107 |
| SEER2 low cycling | Case 1에서 `PLF = 1 - cd_low * (1 - CLF)` | low cooling cycling 손실 | Project current implementation |

## 7. Debugging Checklist

| Check | What to inspect | Expected |
| --- | --- | --- |
| canonical key | `legacy_to_canonical()` result | HSPF2 v3 필수 key가 모두 존재 |
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
| SEER2 변경 | 별도 SEER2 golden test를 먼저 작성한 뒤 변경 |

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
| Official Case #1 | AHRI 공식 계산기와 raw HSPF2 근접성 확인 | `docs/skills/ahri_hspf2.md` |
| Official Case #2 | 다른 A2 anchor에서 공식 계산기 근접성 확인 | `docs/skills/ahri_hspf2.md` |
| H22 tested | optional tested point 우선 사용 확인 | `docs/skills/ahri_hspf2.md` |
| H12 tested | tested H1Full path 확인 | `docs/skills/ahri_hspf2.md` |
| Eq.11.183 | H1N same speed fallback 확인 | `docs/skills/ahri_hspf2.md` |
| H2Int sensitivity | intermediate power가 Case II COP에 영향을 주는지 확인 | `test_hspf2_v3_h2int.py` |
| Case activation | Case I/II/III, fractional availability 확인 | `test_hspf2_v3_low_cases.py` |

SEER2는 현재 HSPF2처럼 official calculator parity가 정리되어 있지 않다. 향후 SEER2를 확장할 때는 먼저 AHRI 공식 계산기 또는 인증 worksheet 기반 golden case를 확보해야 한다.

## 10. Future Refactor Notes

| Topic | Keep current behavior until | Refactor direction | Reference |
| --- | --- | --- | --- |
| HSPF2 v2 legacy path | v3 migration 안정성 확인 완료까지 | legacy reference로만 유지 | Project compatibility |
| Defrost multiplier | 정책과 golden이 확정될 때까지 | Eq.11.107 seasonal multiplier 적용 여부 명확화 | AHRI 210/240-2026 Equation 11.107 |
| Region expansion | Region IV 외 table 검증 전까지 | region parameterized table 구조 | AHRI 210/240-2026 Table 16 |
| SEER2 config | SEER2 golden 확보 전까지 | external JSON schema와 tests 정비 | AHRI 210/240 cooling sections |
| SEER2 off-mode | 공식 요구와 입력 단위 확인 전까지 | `p_w_off` 실제 seasonal denominator 반영 검토 | AHRI 210/240 cooling sections |

계산기 파일은 Lite 규칙상 명시 지시 없이 수정하지 않는다. 특히 `calculate_hspf2_v2()`와 `calculate_hspf2()`는 보호 대상이다.

## 11. HSPF2 v3 구현 현황 및 검증 기준

### 구현 현황
- **대상 규격**: AHRI 210/240-2026 (Region IV 기준)
- **핵심 엔진**: `core/calculator_ahri_hspf2.py`의 `calculate_hspf2_v3` (v2 legacy 대비 정교한 canonical path)
- **입력 체계**: `legacy_to_canonical()`을 통해 다양한 입력 변수명을 표준 키(H01, H11, H12, H1N, H22, H2Int, H32, H42, A2)로 통합 관리함.
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
AGENTS.md의 Lite 규칙만 따르고 docs/DOCS_GUIDELINES.md, docs/STANDARD_DOC_TEMPLATE.md, docs/FORMULA_REFERENCE_GUIDE.md를 먼저 읽어라. AHRI 문서는 docs/skills/ahri_hspf2.md, AHRI HSPF2/SEER2 계산 코드, 관련 tests를 Primary로 삼고, AHRI PDF는 Section/Table/Equation 확인용 Secondary로만 사용하라. 문서 작업이면 docs/ahri210240/ 하위만 수정하라.
```

### HSPF2 계산 작업

```text
AGENTS.md Lite 규칙을 먼저 읽어라. HSPF2는 Region IV, non-ducted single-split variable-capacity air-to-air heat pump 경로를 우선 보호한다. calculate_hspf2_v2()와 calculate_hspf2()는 명시 지시 없이 수정하지 말고, 변경 후 test_hspf2_v3_smoke.py, test_hspf2_v3_low_cases.py, test_hspf2_v3_h2int.py, test_hspf2_v3_bincheck.py를 실행하라.
```

### SEER2 정비 작업

```text
AGENTS.md Lite 규칙을 먼저 읽어라. SEER2는 현재 구현 확인 가능한 범위만 신뢰하고, 공식 parity를 주장하지 말라. 먼저 AHRI 공식 계산기 또는 인증 worksheet 기반 golden case를 추가한 뒤 계산 경로를 수정하라.
```
