
## ISO16358 CSPF xlsm 구조 확인 메모

### 확인일
2026-05-03

### T1 구조
- T1 result는 Y15에서 시작해 내부 CSPF 계산 셀을 참조한다.
- T1 CSTL/CSEC는 각각 CK49 및 CZ49로 계산된다 (SUM(CK18:CK48), SUM(CZ18:CZ48)).
- T1 actual calculation rows는 18~48 범위이다.
- T1은 35↔29 단일 boundary_eer segment를 사용한다.
- T1 boundary temperature / boundary EER table은 CK5~CK7 및 CN5~CN8 계열이다.

### T3 구조
- T3 result는 Y40 → CF112 → CK163/CZ163 경로로 계산된다.
- T3 CSTL/CSEC는 각각 CK132:CK162 및 CZ132:CZ162를 합산한다.
- T3 actual calculation rows는 132~162 범위이다.
- T3는 T1과 동일한 bin-row 계산 템플릿을 사용한다.
- 단, anchor는 piecewise 구조이다:
  - tj <= 35: 35↔29 segment
  - tj > 35: 46↔35 segment
- T3 anchor/boundary 관련 table은 CC115:CN126 및 CK115:CN124 근처에 있다.

### 설계 결론
- SASO/T3는 flat region config와 hard-coded 35/29 iso_boundary_eer만으로는 표현하기 어렵다.
- 하지만 공식 xlsm 구조상 T3는 별도 계산 엔진이 아니라 T1과 같은 bin-row template에 piecewise anchor를 적용한 구조다.
- 따라서 SASO 전용 one-off method보다 generic cspf_profile schema가 적합하다.
- 새 schema는 다음 개념을 표현해야 한다:
  - climate_profile: T1 / T3
  - temperature_segments:
    - T1: [35, 29]
    - T3: tj > 35 → [46, 35], tj <= 35 → [35, 29]
  - test_selection: required_only / with_optional_test
  - point_source_matrix: measured / default / derived / not_used
  - power_model: boundary_eer / piecewise_boundary_eer

## 0. 문서 목적

이 문서는 `predictor_v3` 프로젝트의 리팩토링 후보를 한 곳에서 관리하기 위한 백로그다.

리팩토링은 기능 구현보다 앞서서 진행하지 않는다. 이미 검증된 계산 엔진을 성급하게 분리하거나 구조를 크게 바꾸지 않고, 실제로 반복되는 문제와 확장 병목이 확인된 항목부터 단계적으로 처리한다.

---

## 1. 현재 프로젝트 상태 요약

| 영역 | 현재 상태 | 리팩토링 판단 |
|---|---|---|
| ISO 16358 CSPF | KS C 9306 CSPF, ISO T1 default 2-point, India ISEER xlsx-compatible, Hong Kong custom bin source golden regression 완료. ISO16358 `cspf_test_profile` T1/T3 smoke 및 SASO T3 official xlsm golden regression 완료. | Phase 1에서는 검증 완료 profile만 UI에 노출하고, cspf_profile 대형 리팩토링은 보류. Legacy flat path와 기존 regression은 보호 대상이다. |
| ISO 16358 HSPF | KS C 9306 HSPF profile, validation, golden, smoke test 구축 완료. | 공통/지역 분리는 보류. |
| AHRI 210/240 SEER2/HSPF2 | SEER2 및 HSPF2 full variable-capacity path 구현 완료. | Phase 1 UI 연결 대상으로 유지. |
| EN 14825 SEER/SCOP | 계산 엔진 구현 및 주요 검증 완료. | 당장 대규모 리팩토링 불필요. |
| Region config | Phase 1 production config와 Phase 2 planned config를 구분하는 단계. | golden/sample/test 전용 값은 production config에 넣지 않는다. |
| Docs | notes / dev_notes / design_notes / glossary 구조로 정리 중. | 기존 임시 구조 정리 완료 방향. |
| UI calculator | Phase 1 검증 profile 중심으로 Calculator UI v1 연결 예정. | fixed/two-stage/multi-stage profile matrix는 scope 밖이다. SASO T3 UI 노출 여부는 Calculator UI v1 연결 단계에서 별도 결정한다. |
| ML pipeline | app_trainer.py / app_predictor.py pipeline 재개 예정. | 출근 후 실제 학습 데이터 환경에서 진행. |

---

## 2. 전체 우선순위

| 우선순위 | 항목 | 상태 | 판단 |
|---|---|---|---|
| P0 | 계산 결과 회귀 방어 | 진행 중 | golden / smoke / validation test 유지 |
| P1 | 계산기 Phase 1 scope 문서화 | 진행 중 | 검증 완료 profile만 UI/배포 대상으로 확정 |
| P1 | calc_window.py 계산기 연결 | 예정 | 학습 데이터 없는 환경에서 진행 가능 |
| P1 | app_trainer / app_predictor pipeline 연결 | 예정 | 학습 데이터 있는 환경에서 진행 |
| P2 | ISO 16358 CSPF cspf_profile schema | 보류 | Phase R1에서 official sheet adapter 기반으로 진행 |
| P2 | docs 구조 최신화 | 진행 중 | notes/dev_notes/design_notes/glossary 정리 |
| P2 | region config 수정 규칙 정리 | 진행 중 | golden 끼워맞춤 방지 |
| P3 | ISO16358Calculator 구조 분리 | 보류 | region 예외가 더 쌓인 뒤 판단 |
| P3 | ML feature schema 통합 | 보류 | pipeline 개통 후 판단 |
| P4 | plugin / inheritance 구조 도입 | 금지에 가까운 보류 | 지금은 과설계 위험 |

---

## 3. 실행 원칙

### 3.1 지금 지켜야 할 원칙

- 한 번에 대규모 구조 변경을 하지 않는다.
- 계산 결과가 검증된 엔진은 region config 확장 전까지 보존한다.
- golden expected를 임의로 수정하지 않는다.
- golden sample 하나에 맞추기 위해 hidden factor, 보정 계수, 임의 scaling을 넣지 않는다.
- region config는 규격 근거 또는 명시된 실험/공식 계산시트 근거가 있을 때만 수정한다.
- 코드 리팩토링보다 validation test 추가를 우선한다.
- UI와 ML pipeline은 계산 엔진 안정화 이후 연결한다.

### 3.2 Codex / coding agent 작업 원칙

- `AGENTS.md`의 Lite 규칙만 기본으로 읽는다.
- `AGENTS_FULL.md`는 사용자가 명시적으로 요청할 때만 읽는다.
- 코드 수정 전 변경 범위를 먼저 제한한다.
- 계산식 변경 시 반드시 regression/golden 결과를 함께 보고한다.
- region config 변경 시 기존 region 결과가 변하지 않는지 확인한다.
- 문서만 수정하는 작업에서는 코드, test, JSON을 수정하지 않는다.

---

## 4. ISO 16358 리팩토링 계획

### 4.1 현재 상태

`ISO16358Calculator`는 현재 다음 역할을 함께 가진다.

- ISO 16358-1 CSPF common path
- ISO 16358-2 HSPF generic fallback
- ISO 16358-2 HSPF variable path
- KS C 9306 CSPF profile-specific logic
- KS C 9306 HSPF profile-specific logic
- KS C 9306 intersection power helper
- HSPF load line / defrost / auxiliary heat helper
- CSPF half-capacity recommendation helper

클래스가 커지고 있지만, 현재는 테스트가 통과하고 있으며 계산 결과가 안정화되는 단계다. 따라서 지금은 분리하지 않는다.

### 4.2 지금 하지 않을 작업

아래 작업은 당분간 하지 않는다.

- `ISO16358Calculator` 클래스 분리
- `calculator_iso16358_ks.py` 신규 분리
- region별 subclass 구조 도입
- plugin architecture 도입
- KS C 9306 helper 대량 이동
- inheritance 기반 common/region 구조 재설계
- generic ISO HSPF를 완전한 인증급 엔진으로 확대

### 4.3 나중에 검토할 분리 후보

region-specific 예외가 더 쌓이면 아래 구조를 검토한다.

| 후보 모듈 | 역할 |
|---|---|
| `calculator_iso16358.py` | ISO16358 common entry point, CSPF common path, generic HSPF fallback |
| `calculator_iso16358_ks.py` 또는 `regions/ks_c9306.py` | KS C 9306 CSPF/HSPF profile-specific helper |
| `calculator_iso16358_profiles.py` | region profile dispatch / validation |
| `region_config_schema.py` | region config validation 전담 |
| `tests/iso16358/` | CSPF/HSPF golden, validation, smoke test 분리 |

### 4.4 분리 검토 트리거

다음 조건 중 2개 이상 만족할 때 구조 분리를 재검토한다.

- ISO16358Calculator가 1800줄 이상으로 증가
- KS 외 region-specific 계산 예외가 2개 이상 추가
- CSPF/HSPF 공통 path 수정 시 KS test가 반복적으로 깨짐
- region config schema validation이 계산기 본문을 복잡하게 만듦
- UI 연결 시 입출력 schema가 계산기 내부 구조에 강하게 묶임
- 새 규격 추가 시 기존 ISO16358Calculator 수정이 반복됨

---

## 5. ISO 16358 CSPF Region Config 확장 계획

### 5.1 목표

ISO 16358-1 CSPF 기반 국가들을 region config 중심으로 확장한다. 엔진 수정 없이 config와 test로 처리하는 것을 원칙으로 한다.

### 5.2 우선 확장 후보

| 그룹 | 국가/지역 | 작업 방향 |
|---|---|---|
| ISO 기본 bin 계열 | Southeast Asia T1 default | `iso_t1_default_2point.json` production config 사용 |
| custom bin 계열 | India | ISEER xlsx-compatible boundary temperature rounding opt-in 유지 |
| custom bin 계열 | Hong Kong | custom bin 2-point source golden regression 유지. Measured CSPF는 measured performance point와 declared/rated full capacity load anchor를 분리 사용한다. |
| custom bin 계열 | Brazil | 기존 Brazil adaptation 자료 확인 후 적용 |
| 4-point 가능성 | SASO / Saudi Arabia | T3 및 official sheet optional matrix를 cspf_profile Phase R2 이후 구현 |

### 5.3 방어 규칙

- Cd를 golden에 맞추기 위해 바꾸지 않는다.
- derived_rules를 golden에 맞추기 위해 바꾸지 않는다.
- 온도 bin만 다른 국가라면 계산식은 건드리지 않는다.
- golden sample은 가능하면 국가별 2개 이상 확보한다.
- golden이 1개뿐이면 “1-sample smoke/golden”으로 표시하고 인증급 검증으로 보지 않는다.
- 공식 계산시트와 다른 결과가 나오면 먼저 input schema와 bin_hours를 확인한다.

### 5.4 ISO16358 CSPF 엔진 재설계

#### 등록일

2026-05-01, (5/3 수정)

#### 트리거 조건 (이미 충족됨)

- SASO T3 추가 시 `iso_boundary_eer`가 35/29 hard-code로 인해 `ValueError`를 발생시킨다.
- Hong Kong / India / SASO 추가 과정에서 지역별 patch method(`ks_intersection`, `iso_boundary_eer`, `iso_boundary_temperature_rounding`)가 누적되었다.
- 공식 ISO16358 xlsm 시트의 T1/T3 x required/optional x measured/default matrix를 현재 config schema로 표현할 수 없다.

#### 현재 구조의 문제

- `_iso_boundary_eer()`가 `35_{type}` / `29_{type}`을 하드코딩한다.
- T1/T3 climate profile 구분이 없다.
- temperature anchor matrix가 없다. 예를 들어 46/35/29 anchor를 구조적으로 선언할 수 없다.
- `required_only` / `with_optional_test` 선택 표현이 없다.
- min-half 구간 공식 분기 없이 capacity-linear fallback에 의존한다.
- 지역 추가마다 calculator 수정이 필요해질 위험이 커졌다.

#### 목표 구조

- `cspf_profile` schema를 도입한다.
  - `climate_profile`: T1 / T3
  - `test_selection`: `required_only` / `with_optional_test`
  - `temperature_anchors`: `[46, 35, 29]` 등
  - `load_levels`: `full` / `half` / `minimum`
  - point source matrix: `measured` / `default` / `derived` / `not_used`
  - `power_model.branches`: 구간별 계산 방식 선언
- 기존 flat config는 legacy path로 유지한다.
- 새 schema는 병렬 opt-in으로만 동작한다.
- 지역 추가 시 calculator 수정 없이 config만으로 처리할 수 있게 한다.

#### 단계별 계획

#### Scope clarification

현재 프로젝트의 ISO16358 CSPF profile path는 variable-capacity / inverter-only를 대상으로 한다. Fixed, two-stage, multi-stage unit 지원은 명시적으로 scope 밖이며, 이를 위한 schema abstraction이나 branch는 추가하지 않는다.

Phase R1 — `cspf_test_profile` opt-in layer 추가 (calculator 계산 결과 변경 없음)

- [완료] `cspf_test_profile` 감지 helper 추가
- [완료] point resolver 추가
- [완료] Cd default resolver 추가
- [완료] temperature segment metadata 추가
- [완료] active load levels metadata 추가
- [완료] T1 `required_only` calculation path 추가
- [완료] legacy ISO T1 default parity 확인

- [완료] T1 `required_only` profile path를 legacy ISO T1 default path와 parity 검증한다.
  - `tests/test_iso16358_cspf_profile_calculation.py`
  - legacy ISO T1 default production regression `4.665` 유지 확인
- [계속 유지] 기존 regression은 전부 유지해야 한다.
  - 현재 기준: 전체 pytest `99 passed`
- [완료] T1 `with_optional_test` minimum branch smoke/sanity 확인
- [완료] T3 `required_only` / `with_optional_test` resolver/smoke 확인

Phase R2 — SASO T3 official xlsm alignment (Complete)

- [완료] T1 required_only / with_optional_test smoke/sanity 검증 완료
- [완료] T3 required_only / with_optional_test resolver/smoke 검증 완료
- [완료] SASO T3 t100=46 / ref46 load line 확인 및 config 정렬
- [완료] T3 29_full default point 동작 확인 및 테스트 커버 유지
  - 29_full capacity = `1.077 × 35_full capacity`
  - 29_full power = `0.914 × 35_full power`
  - git diff 기준 Phase R2-2 신규 추가가 아니라 현재 구현 동작으로 확인/유지됨
- [완료] T3 piecewise boundary EER helper 추가
  - 기존 T1/legacy `_iso_boundary_eer()` 시그니처와 동작은 유지
  - T3 profile에서는 `_iso_boundary_eer_t3_piecewise()`가 `tj <= 35`에서 29↔35, `tj > 35`에서 35↔46 anchor를 사용
  - `_iso_boundary_eer_power()`는 `cspf_test_profile.climate_profile == "T3"` guard 안에서만 T3 helper를 사용
- [완료] T3 `with_optional_test`의 `{min, half}` 및 `{half, full}` bracket support
  - 기존 `_iso_boundary_eer_power()`의 half-full 제한 때문에 T3 min-half가 capacity_linear fallback을 타던 문제를 해소
  - 기존 `_iso_boundary_eer()`의 29/35 고정 구조는 T1/legacy 보호를 위해 유지
- [완료] SASO T3 golden regression
  - config: `climate_profile=T3`, `test_selection=with_optional_test`, `t_100_load=46.0`, `t_0_load=20.0`, `reference_point="46_full"`, `Cd=0.27`, `power_interpolation_method="iso_boundary_eer"`
  - golden sample: 46_full 5418/1971, 35_full 6058/1611, 35_half 3036/566, 35_min 1780/284
  - result: CSTL ≈ `21,547.386 kWh`, CSEC ≈ `4,349.020 kWh`, CSPF ≈ `4.955 W/W`
  - official target: CSTL ≈ `21,546 kWh`, CSEC ≈ `4,349 kWh`, CSPF ≈ `4.954 W/W`
- [완료] Boundary diagnostic
  - Tb ≈ `45.2479°C`, Tc ≈ `34.6371°C`, Tp ≈ `29.1799°C`
  - `tj > 35` full segment는 `46_full`이 BL reference이므로 intersection이 `46.0°C`
- [완료] 전체 pytest `99 passed`

#### 보호 조건 (어떤 단계에서도 위반 금지)

Phase R3 — 기존 config 마이그레이션 (선택적)

- `iso_t1_default_2point` / `hong_kong` / `india_iseer`를 새 schema로 순차 전환한다.
- legacy flat config path에는 deprecation 경고만 추가한다.

#### 보호 조건 (어떤 단계에서도 위반 금지)

- Korea CSPF 6.504 regression을 유지한다.
- ISO T1 default CSPF 4.665 regression을 유지한다.
- India ISEER xlsx-compatible 4.993을 유지한다.
- Hong Kong CSPF source golden regression을 유지한다.
- Cd / derived factor / hidden 보정을 금지한다.
- 기존 public function signature는 가능하면 유지한다.

#### 현재 상태

- Phase R1/R2의 `cspf_test_profile` variable/inverter profile path 검증이 완료되었다.
- 완료:
  - `cspf_test_profile` opt-in 감지
  - variable/inverter-only profile resolver
  - T1 `required_only` / `with_optional_test` smoke/sanity
  - T3 `required_only` / `with_optional_test` resolver/smoke
  - T3 piecewise boundary EER path
  - SASO T3 official xlsm golden regression
  - legacy ISO T1 default path parity 확인
  - debug/audit/trace 임시 파일 제거
  - 전체 pytest `99 passed`
- 보호:
  - `iso_boundary_eer` 전역 동작 변경 금지
  - T3 helper는 T3 `cspf_test_profile` guard 안에서만 동작
  - Korea CSPF 6.504, ISO T1 default 4.665, India, Hong Kong source golden regression 유지
  - hidden factor / golden fitting 계수 추가 금지
- 남음:
  - Calculator UI v1 연결 범위 검토
  - Hong Kong HSPF는 ISO 16358-2 완전 구현 Phase로 별도 추적한다. 구현 전 pitfalls/calculation order 문서 작성과 golden 후보값 재확인이 필요하다.

### 5.5 계산기 Phase 1 배포 범위

Phase 1에서는 한 번에 모든 지역을 완전 구현해서 배포하지 않는다. 이미 regression/golden 검증이 끝난 주요 지역과 규격만 UI와 배포 대상에 포함하고, 계산기에 포함되지 않은 지역은 기존 공식 엑셀 시트를 계속 사용하게 한다.

#### Phase 1 포함

- Korea KS C 9306 CSPF/HSPF
- ISO16358-1 T1 default 2-point CSPF
- India ISEER xlsx-compatible
- Hong Kong custom bin source golden regression
- EN14825 SEER/SCOP
- AHRI SEER2/HSPF2

#### Phase 1 제외

- ISO16358 official sheet full optional matrix
- 모든 required/optional/default 조합 완전 구현
- fixed/two-stage/multi-stage `cspf_test_profile` abstraction

#### UI v1 원칙

- 검증된 profile만 노출한다.
- optional 선택 UI는 비활성화하거나 노출하지 않는다.
- SASO T3는 official golden regression 완료 상태이나 UI 노출 여부는 Calculator UI v1 연결 단계에서 별도 검토한다.

---

## 6. KS C 9306 유지보수 계획

### 6.1 현재 확정된 방향

KS C 9306은 ISO 16358 계열 구조를 따르지만 한국 고유의 시험점, 보정계수, bin-hour, 공식 계산시트 관행이 있다. 따라서 common ISO 계산과 무리하게 합치지 않는다.

현재 유지할 정책:

- KS C 9306 CSPF는 region config profile로 관리한다.
- KS C 9306 HSPF는 `ks_c_9306_hspf` 입력 profile을 명시적으로 사용한다.
- KS profile인데 전용 입력이 없으면 silent fallback하지 않고 오류를 낸다.
- HSPF load line의 capacity source는 region config에서 명시한다.
- 공식 계산시트 관행과 규격 문구가 다를 수 있는 항목은 TODO/주석/문서에 남긴다.

### 6.2 주의 항목

| 항목 | 현재 판단 | 후속 조치 |
|---|---|---|
| HSPF load line 기준 | 한국 공식 계산시트 기준 `rated_heating_capacity × 0.82` 사용 | 규격 원문과 공식 시트 차이를 문서에 유지 |
| ISO16358-2 common HSPF | KS 경로와 분리 | 한국 외 HSPF 확장 전까지 보류 |
| Australia / New Zealand HSPF | 확인 필요 | AS/NZS 3823.4.2 원문 확인 전 구현 금지 |
| 31-bin KS HSPF golden | raw output 확보됨 | production korea.json 기반 golden 확정 여부 별도 판단 |
| 2°C stage fallback | -7 ↔ 7 선형보간 방식으로 수정됨 | validation 유지 |

---

## 7. AHRI 210/240 리팩토링 계획

### 7.1 현재 상태

AHRI 210/240 HSPF2 v3는 다음 범위에서 구현 및 검증을 진행했다.

- simplified canonical path
- H12/H32/H42 canonical schema
- H42 제공/미제공 경로
- full variable-capacity path
- H22 tested
- H12 tested
- h1n_same_speed_as_h3=True 경로
- defrost / auxiliary / delta_j 관련 주요 case 검증

### 7.2 지금 할 일

- 구조 분리보다 문서와 테스트 유지가 우선이다.
- AHRI 계산기는 현재 다음 작업이 생기기 전까지 대규모 리팩토링하지 않는다.
- 신규 case가 발견될 때마다 golden case를 추가한다.

### 7.3 나중에 검토할 항목

- v2 legacy path와 v3 canonical path의 파일 분리
- HSPF2 constants/config schema 정리
- bin-level debug output 표준화
- 공식 AHRI calculator 비교 case 누적

---

## 8. EN 14825 리팩토링 계획

### 8.1 현재 상태

EN 14825 SEER/SCOP 엔진은 구현 완료 상태로 본다. SCOP/SEER 계산 경로에서 일부 규격 해석 주석이 필요한 항목은 문서로 관리한다.

### 8.2 보류 항목

- EN 14825 엔진 대규모 구조 변경
- ISO 16358과 공통 seasonal engine으로 통합
- AHRI/ISO/EN 공통 bin engine 추상화

### 8.3 나중에 검토할 항목

- SCOP bin-level debug output 정리
- degradation/cycling 보정 로직 주석 보강
- design_notes에 설계 관점 요약 보강

---

## 9. Docs 리팩토링 계획

### 9.1 현재 목표 구조

규격별 문서는 아래 구조를 기준으로 한다.

```text
docs/
├── ahri210240/
│   ├── ahri210240_glossary.md
│   ├── ahri210240_notes.md
│   ├── ahri210240_design_notes.md
│   └── ahri210240_dev_notes.md
├── en14825/
│   ├── en14825_glossary.md
│   ├── en14825_notes.md
│   ├── en14825_design_notes.md
│   └── en14825_dev_notes.md
└── iso16358/
    ├── iso16358_glossary.md
    ├── iso16358_notes.md
    ├── iso16358_design_notes.md
    ├── iso16358_dev_notes.md
    └── regions/
        └── ks_c_9306/
            ├── ks_c_9306_glossary.md
            ├── ks_c_9306_notes.md
            ├── ks_c_9306_design_notes.md
            └── ks_c_9306_dev_notes.md
```

### 9.2 문서 역할 구분

| 문서 | 역할 |
|---|---|
| glossary | 공식 용어, 약어, symbol, 설계/SW 공통 이해 |
| notes | 규격 구조, 계산 구조, 입출력, 검증 결과 |
| design_notes | 열유체/제품 설계 관점의 해석과 개선 전략 |
| dev_notes | 구현 실수 방지, 테스트 전략, agent 작업 주의사항 |
| REGION_CONFIG_RULES | region config 수정 규칙과 금지사항 |

### 9.3 완료/진행 중 항목

- AHRI glossary 구조 참고 완료
- ISO16358 glossary 개정 초안 작성
- KS C 9306 glossary 개정 초안 작성
- ISO16358 design_notes 초안 작성
- KS C 9306 design_notes 초안 작성
- REGION_CONFIG_RULES 작성/정리 진행

### 9.4 문서 작성 금지사항

- design_notes에 코드 파일명/함수명/JSON key를 남발하지 않는다.
- 공식 용어가 아닌 AI 임의 용어를 glossary에 넣지 않는다.
- 규격 근거 없는 단정 표현을 피한다.
- TODO만 있는 빈 문서를 만들지 않는다.
- code mapping은 notes/dev_notes로 보내고 design_notes에는 넣지 않는다.

---

## 10. ML Pipeline 리팩토링 계획

### 10.1 현재 상태

ML pipeline은 계산기 작업 이후 재개한다. 실제 학습 데이터가 있는 환경에서 app_trainer.py, app_predictor.py, preprocessing, feature schema를 연결하고 검증한다.

### 10.2 우선 작업

| 항목 | 설명 |
|---|---|
| app_trainer.py 실행 검증 | 실제 데이터 기준 학습 가능 여부 확인 |
| app_predictor.py 실행 검증 | 기존 모델/새 모델 예측 경로 확인 |
| feature schema 확인 | trainer와 predictor의 feature 순서/이름 불일치 방지 |
| preprocessing version 관리 | 향후 모델 호환성 문제 방지 |
| model artifact 구조 확인 | 저장/로드 경로와 metadata 통일 |

### 10.3 보류 중인 리팩토링

- trainer/predictor 공통 adapter 도입
- preprocess pipeline 객체화
- OptimalModel dataclass 구조 확장
- model registry 구조 도입
- feature schema migration system 도입

이 항목들은 pipeline이 먼저 개통된 뒤 진행한다.

---

## 11. UI / Calculator Window 계획

### 11.1 목표

학습 데이터가 없는 환경에서도 진행 가능한 작업이다. 계산기 엔진과 UI를 연결하고, 사용자가 region과 표준을 선택해 CSPF/HSPF를 계산할 수 있게 한다.

### 11.2 우선 작업

| 항목 | 설명 |
|---|---|
| region dropdown | region config 선택 |
| standard/profile 표시 | 선택한 region의 계산 방식 명시 |
| CSPF input form | 필요한 시험값만 입력 |
| HSPF input form | 한국 profile 우선 |
| result panel | SPF, seasonal load, seasonal energy, auxiliary 등 표시 |
| intermediate output | T_min, T_mid, Lc(T_mid), recommended phi_half_35 등 향후 표시 |

### 11.3 주의사항

- UI 편의를 위해 계산기 엔진의 validation을 약화하지 않는다.
- QDoubleValidator가 기존 comma 입력 처리와 충돌할 수 있으므로 무리하게 적용하지 않는다.
- UI에서 입력을 예쁘게 보여주더라도 core calculator는 독립적으로 검증 가능해야 한다.

---

## 12. Region Config 관리 규칙

### 12.1 기본 원칙

- region config는 규격/공식 계산시트/검증된 sample을 근거로 수정한다.
- golden에 맞추기 위한 임의 보정값을 넣지 않는다.
- country-specific bin_hours만 다른 경우 계산 엔진은 수정하지 않는다.
- 한국처럼 시험점과 derived rule이 다른 경우 profile로 명시한다.
- config key 이름은 코드와 문서에서 반드시 일치시킨다.

### 12.2 변경 시 필수 확인

region config를 수정할 때는 최소한 아래를 확인한다.

- JSON parse 통과
- 해당 region CSPF/HSPF smoke 통과
- 기존 Korea CSPF regression 유지
- 기존 KS HSPF validation 유지
- golden expected를 수정했다면 수정 이유와 근거 명시
- bin_hours 합계 확인
- test value rounding 적용 범위 확인

---

## 13. Test / Golden 관리 계획

### 13.1 테스트 계층

| 테스트 | 목적 |
|---|---|
| smoke | 계산이 실행되고 양수/기본 구조가 맞는지 확인 |
| validation | 누락/음수/잘못된 schema 입력 방어 |
| golden | 공식 계산시트 또는 신뢰 가능한 reference와 수치 비교 |
| regression | 기존 region 결과가 깨지지 않았는지 확인 |
| bin-level debug | 특정 bin에서 case, load, capacity, power, auxiliary 확인 |

### 13.2 golden 관리 규칙

- golden expected는 임의로 바꾸지 않는다.
- 공식 계산시트 값이 바뀐 경우에만 expected 변경을 검토한다.
- golden sample 하나만으로 인증급 구현 완료라고 보지 않는다.
- 가능하면 region별 최소 2개 golden sample을 확보한다.
- golden sample과 production region config를 분리해 쓰는 경우 이름에 명확히 표시한다.

---

## 14. 보류 중인 대형 리팩토링 후보

| 후보 | 현재 판단 | 재검토 시점 |
|---|---|---|
| ISO16358Calculator 분리 | 보류 | CSPF region 확장 후 |
| KS C 9306 전용 calculator 분리 | 보류 | KS 외 HSPF profile 등장 후 |
| region plugin architecture | 보류 | region 예외 3개 이상 누적 후 |
| common seasonal bin engine | 보류 | AHRI/EN/ISO 간 중복이 실제 유지보수 문제를 만들 때 |
| ML adapter/preprocess version system | 보류 | trainer/predictor 개통 후 |
| UI form schema 자동 생성 | 보류 | region config가 충분히 안정화된 후 |

---

## 15. 가까운 실행 순서

### Step 1 — 계산기 Phase 1 scope 문서화

- Phase 1 production profile과 Phase 2 planned profile을 구분한다.
- UI v1에 노출할 region/standard 목록을 확정한다.
- 공식 엑셀 시트 유지 대상 지역을 문서에 남긴다.

### Step 2 — Calculator UI v1 연결

- `app_calculator.py` / `calc_window.py`에서 검증된 profile만 선택 가능하게 한다.
- optional 선택 UI는 비활성화하거나 미노출한다.
- SASO T3는 official golden regression 완료 상태로 표시할 수 있으나, UI 노출 여부는 2점식 ISO/ISEER 탭 안정화 이후 별도 검토한다.

### Step 3 — predictor → calculator pipeline 연결

- predictor 출력값을 calculator 입력 schema로 변환한다.
- ML 예측값 기반 CSPF/SEER/HSPF 자동 산출 경로를 연결한다.
- app_predict.py 결과 컬럼 확장 범위를 확인한다.

### Step 4 — 역방향 예측 MVP

- 목표 성능/효율 입력에서 HW 조합을 추천하는 최소 기능을 설계한다.
- 물리 제약과 단조 제약을 먼저 적용하고 통계 최적화는 후순위로 둔다.

### Step 5 — ISO16358 cspf_profile schema Phase R1

- cspf_profile schema validator를 추가한다.
- 기존 계산 결과가 바뀌지 않는 mirror/diagnostic test부터 추가한다.

### Step 6 — SASO T3 Phase R2

- 완료: T3 climate profile과 `46_full` high-anchor branch를 구현했다.
- 완료: SASO CSPF 4.954 official xlsm golden regression을 추가했다.

### Step 7 — Hong Kong ISO 16358-2 HSPF Review

- Hong Kong HSPF는 이번 Hong Kong CSPF golden 전환 범위 밖이다.
- ISO 16358-2 완전 구현 Phase에서 별도 추적한다.
- 구현 전 선행 조건:
  - ISO 16358-2 pitfalls / calculation order 문서 작성
  - Hong Kong HSPF golden 후보값 재확인: Measure #1 `3.643`, Measure #2 `4.572`
  - 기존 KS C 9306 HSPF regression 보호 확인
- Preliminary observations, not implementation decisions:
  - `Lh(tj) = cap_0 × (12.75 - tj) / 12.75`
  - `cap_0 = 7°C full heating capacity × 0.82` 후보이며 ISO 16358-2 계수로 재검증 필요
  - `t_limit = 12.75°C`, `t_0_heat = 17°C`, `t_100_heat = 0°C` 후보
  - Rated 변경이 Measured HSPF에 영향 없음. `building_load_source = "measured"` 후보
  - 2°C 외삽 계수 후보: full non-frost cap `0.8714`, pwr `0.9357`; full frost cap `0.7781`, pwr `0.8829`; half frost only cap `0.7781`, pwr `0.9286`
  - `Cd_heating = 0.25`, frost/non-frost 분기, boundary temperature(`ta`, `td`, `te`, `tg`) 계산 필요
  - AHRI HSPF2 구현은 reference design으로 참조 가능하지만 계수와 calculation order는 ISO 16358-2 기준으로 별도 검증한다.

---

## 16. 삭제/폐기된 구식 계획

아래 항목은 현재 계획에서 폐기하거나 후순위로 내렸다.

- “Docs 구조 리팩토링은 ISO16358 구현 완료 이후 처음부터 대이동” 계획
  - 이미 notes/dev_notes/design_notes/glossary 구조로 점진 정리 중이므로 대이동 방식은 폐기한다.
- “ISO16358 완료 직후 calculator class 분리” 계획
  - 현재는 region config 확장과 UI 연결이 우선이다.
- “predictor/trainer 안정화 이후에만 docs 정리” 계획
  - 계산기 문서는 지금 정리한다. ML 문서는 pipeline 재개 후 정리한다.
- “공통 seasonal engine 추상화” 아이디어
  - AHRI/EN/ISO 차이가 크므로 현재는 과설계다.
- “region-specific 예외를 미리 plugin화” 아이디어
  - 실제 예외가 더 쌓이기 전까지 도입하지 않는다.

---

## 17. 한 줄 결론

현재 리팩토링의 핵심은 구조를 크게 바꾸는 것이 아니라, 검증된 계산 결과를 유지하면서 region config, docs, UI, ML pipeline을 순서대로 안정화하는 것이다.
