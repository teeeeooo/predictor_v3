# Audit 4 Next Actions — Completion Report

## 요약

`reference_files/audit_4.md`가 제시한 "지금 당장 할 수 있는 다음 작업 4개"를
모두 완료했다. 각 task는 source 커밋과 report 커밋을 분리하고,
`result_reports/active/`에 단계별 결과 리포트를 추가했다.

| Task | 제목 | 상태 | Source commit | Report (`result_reports/active/`) |
| ---- | ---- | ---- | ------------- | --------------------------------- |
| 1 | HSPF2 UI 중복 row 제거 + smoke 보강 | OK | `e35ea2f` | `069_hspf2-ui-duplicate-row-guard.md` |
| 2 | EN14825 `calculate_en()` 실제 SCOP 계산 연결 | OK | `b673293` | `070_wire-en14825-ui-to-scop.md` |
| 3 | CalculatorInputEnvelope 첫 slice 구현 | OK | `f7c7527` | `071_calculator-input-envelope-adapter-slice.md` |
| 4 | Adapter schema boundary guard 강화 | OK | `2a3b680` | `072_strengthen-calculator-schema-boundary-guards.md` |

작업 순서는 audit_4와 동일하며, 각 task가 끝날 때마다 (a) source 커밋,
(b) report 커밋을 분리해서 작성했다.

## 환경 / 도구

- 작업 브랜치: `work/iso-separation-plan`
- Python 3 + PyQt5 사용 가능 (smoke 테스트가 skip되지 않고 모두 실행됨)
- 검증 명령: `python3 -B -m py_compile`, `python3 -B -m pytest -q`,
  필요한 경우 region config JSON 정적 검사 (in-process)

## Task 1 — HSPF2 UI 중복 row 제거 + smoke 보강

### Goal

`ui/calc_window.py` HSPF2 입력 loop에 중복 `form_hspf2.addRow(...전력...)`이
있다는 audit 지적을 반영해 layout bug를 제거하고, regression 방지 smoke를
추가한다.

### Changed Files

- `tests/test_app_calculator_ui_smoke.py`

### 결과

- audit_4가 지적한 중복 row는 현재 main branch 코드(`ui/calc_window.py`
  213~220)에서 실제로 재현되지 않았다. HSPF2 loop의 form rows는 이미
  `능력 (Btu/h)` 1회 + `전력 (W)` 1회로 정상 상태였다.
- 향후 회귀를 막기 위해 PyQt5-gated smoke 2건을 추가했다.
  - `test_hspf2_input_widgets_have_no_duplicate_rows`: 7 point × 2 + 4 extras
    = 18개 widget key가 정확히 등록되고 cap/pow가 별도 instance인지 확인.
  - `test_hspf2_required_input_raises_validation_error_when_missing`: HP 모드
    HSPF2 입력 누락 시 `calculate_hspf2_v3()`가 `InputValidationError`를
    발생시키는지 확인 (QMessageBox를 건드리지 않는 격리된 검증 경로).

### Verification

- `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q` → `6 passed`.

## Task 2 — EN14825 `calculate_en()` 실제 SCOP 계산 연결

### Goal

EN tab의 placeholder `return "EN 계산 결과 (kW 기준)"`을 실제 SCOP 계산
경로로 연결한다.

### Changed Files

- `ui/calc_window.py`
- `tests/test_app_calculator_ui_smoke.py`

### 결과

- `init_en_tab`을 A/B/C/D → A/B/C/D/TOL/Tbiv 6 포인트로 확장.
- 새 group "SCOP 계산 파라미터"에 `p_design_h (kW)`, climate combo
  (Average/Warmer/Colder), `TOL/Tbiv 온도(°C)`, `p_to/p_sb/p_ck/p_off (W)`
  입력을 추가.
- `calculate_en()`을 `self.en_calc.calculate_scop(...)` 호출 경로로 교체.
  - 6 test point의 (cap, pow)을 dict로 변환.
  - climate combo `currentData()`로 calculator API 문자열 직접 매핑.
  - standby power는 UI에서 W로 받고 `/ 1000.0`로 kW 변환 후 전달.
  - 결과는 `EN14825 SCOP (<climate>) 결과: <scop>` 형식으로 result label에 표시.
- offscreen smoke `test_en_calculate_button_displays_scop_result_text` 추가
  (EN14825 golden average sample 사용, label에 "EN14825 SCOP" / "결과:" 포함
  여부 검증).

### Verification

- `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py tests/test_en14825_golden.py -q`
  → `11 passed`.
- EN14825 공식, golden expected, region config 미변경.

## Task 3 — CalculatorInputEnvelope 첫 slice 구현

### Goal

061 envelope design의 다음 slice로, ML/manual candidate input을 calculator
input으로 변환하는 최소 adapter를 추가한다. 우선 `ahri_usa_seer2`만 지원.

### Changed Files

- `core/calculator_input_adapter.py` (new)
- `tests/test_calculator_input_adapter.py` (new)
- `tests/test_calculator_schema_boundaries.py`
  (`ADAPTER_MODULE` → `ADAPTER_MODULES` set, 새 input adapter 모듈 포함)

### 결과

- 새 함수 `build_calculator_input_envelope(profile_id, points, units=None,
  source="manual")` 추가.
  - 지원 profile: `ahri_usa_seer2`. 다른 profile은 `ValueError`.
  - 필수 point: `A_Full, B_Full, B_Low, E_Int, F_Low`.
  - 포인트 입력 형태는 `(capacity, power)` tuple 또는
    `{"capacity": ..., "power": ...}` dict 모두 허용.
  - 단위는 `Btu/h` capacity / `W` power만 허용. 단위 변환은 의도적으로
    제외하고, 다른 단위는 `ValueError`.
  - 음수/0 값, 누락된 point, 잘못된 형식에 fail-fast.
  - 반환 envelope: `{calculator_profile_id, calculator_id, test_points,
    units, source}`. `test_points`는 곧바로 `AHRICalculator.calculate_seer2`
    에 전달 가능 (테스트로 보장).
- `tests/test_calculator_input_adapter.py`에 8건 테스트 추가
  (tuple/dict 정상 경로, predicted-source 태깅, calculator-ready 호환성,
  unsupported profile / missing point / non-positive value /
  unsupported unit / malformed value 각각 fail-fast).
- adapter 모듈 두 개를 동등하게 처리하기 위해
  `tests/test_calculator_schema_boundaries.py`의 ADAPTER 예외 set을 확장.

### Verification

- `python3 -B -m pytest tests/test_calculator_input_adapter.py tests/test_calculator_result_adapter.py tests/test_calculator_schema_boundaries.py tests/test_ahri_seer2_smoke.py -q`
  → `17 passed`.
- 계산기 public API (`calculate_seer2` signature/return) 미변경. region config
  미변경.

## Task 4 — Adapter schema boundary guard 강화

### Goal

ML 복귀 전에 region config / calculator core 오염 방지 범위를 넓힌다.

### Changed Files

- `tests/test_calculator_schema_boundaries.py`

### 결과

- `BANNED_REGION_RUNTIME_KEYS`에 6개 추가:
  `candidate_id, predicted_points, calculator_input, calculator_result,
  ranking, ranking_features`. 기존 `candidate / prediction / model_version /
  raw_result`는 유지.
- `ADAPTER_ONLY_TERMS`에 4개 추가:
  `predicted_points, calculator_input, calculator_result, ranking_features`.
  기존 envelope 타입 4개와 `raw_result / model_version / prediction`은 유지.
- production region config 9개 (en14825_scop, eu, hong_kong, india_iseer,
  iso_t1_default_2point, korea, saso, usa, usa_hspf2)가 새 guard에서 모두
  통과함을 사전 정적 검사로 확인 (`python3` walk_keys 비교).

### Verification

- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py
  tests/test_calculator_input_adapter.py
  tests/test_calculator_result_adapter.py -q` → `15 passed`.
- 전체 suite: `python3 -B -m pytest -q` → `312 passed, 23 xfailed`
  (회귀 없음).

## 종합 검증

- 단계별 부분 검증은 각 task 절에 기재.
- 최종 종합 검증:
  - `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py
    tests/test_calculator_result_adapter.py
    tests/test_calculator_input_adapter.py
    tests/test_calculator_schema_boundaries.py
    tests/test_calculator_profiles.py tests/test_calculator_dispatcher.py
    tests/test_en14825_golden.py tests/test_ahri_seer2_smoke.py -q`
    → `60 passed`.
  - `python3 -B -m pytest -q` → `312 passed, 23 xfailed`.

## 커밋 / push 기록

작업이 끝날 때마다 source 커밋과 report 커밋을 분리했다 (audit_4의 지시에
따라 단계별 commit + report). 본 reference report는 별도 final-report 커밋으로
추가한다.

| # | Commit | 내용 |
| - | ------ | ---- |
| 1 | `e35ea2f` | test: guard HSPF2 input form against duplicate rows |
| 2 | `afa9e13` | report: record HSPF2 duplicate row guard |
| 3 | `b673293` | feat: wire EN14825 calculate_en() to calculate_scop |
| 4 | `798be75` | report: record EN14825 calculate_en SCOP wiring |
| 5 | `f7c7527` | feat: add CalculatorInputEnvelope adapter slice for AHRI SEER2 |
| 6 | `30c0d9c` | report: record CalculatorInputEnvelope adapter slice |
| 7 | `2a3b680` | test: strengthen calculator schema boundary guards |
| 8 | `7819a50` | report: record schema boundary guard strengthening |

push는 사용자가 검토 후 직접 진행하는 것이 본 프로젝트 규약이므로 본 작업
범위에서는 push를 수행하지 않았다.

## 남은 위험 / 후속 작업 후보

- EN tab은 입력 항목이 늘어났으나 layout 조정(스크롤/그룹 정돈)은 그대로다.
  매우 작은 화면에서는 후속 UI 튜닝이 필요할 수 있다 (scope 밖).
- CalculatorInputEnvelope는 현재 `ahri_usa_seer2` 단일 profile만 지원한다.
  EN14825/KS C 9306/ISO 16358 profile 확장은 후속 slice로 분리해야 한다.
- 단위 변환은 envelope에 포함하지 않았으므로 ML caller가 다른 단위를 쓰는
  경우 caller 측에서 미리 변환해야 한다 (의도된 boundary).
- `reference_files/`는 `.gitignore` 대상이므로 본 보고서는 `git add -f`로
  강제 추적한다 (audit_3 완료 보고서와 동일 패턴).

## Scope Compliance

- 각 task가 명시한 "수정 대상" 외의 파일은 수정하지 않았다.
- 계산기 공식, golden expected, region config, ML 본체 코드는 모두
  미변경.
- adapter-owned 용어가 calculator core로 새어 들어오지 않음을 정적 guard로
  보장.
- audit_4의 각 task 금지 항목 준수:
  - task 1: AHRI HSPF2 계산식 / HSPF2 golden / UI redesign 미수행.
  - task 2: EN14825 공식 / EN golden / calculator_en14825 리팩토링 /
    ML adapter 혼합 미수행.
  - task 3: ML/inverse-search caller 구현 / calculator return schema 변경 /
    region config schema 변경 / 다중 profile 확장 미수행.
  - task 4: region config 값 수정 / calculator logic 수정 / adapter 기능
    구현 혼합 미수행.
