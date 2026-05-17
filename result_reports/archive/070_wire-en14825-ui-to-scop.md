# 070 Wire EN14825 UI to calculate_scop

## Goal

audit_4 task 2: EN tab의 placeholder `calculate_en()`을 실제 SCOP 계산 경로로
연결한다. EN A/B/C/D 외에 TOL, Tbiv, p_design_h, climate, standby power 입력을
UI에 추가해 `EN14825Calculator.calculate_scop(...)`를 호출하고 결과를
`result_label`에 표시한다.

## Scope

- `ui/calc_window.py` (`init_en_tab`, `calculate_en`)
- `tests/test_app_calculator_ui_smoke.py` (EN SCOP smoke 추가)

## Non-goals

- EN14825 공식 수정
- EN golden expected 수정 (`tests/test_en14825_golden.py` 미변경)
- `core/calculator_en14825.py` 대규모 리팩토링
- ML adapter 연결
- region config 수정

## Verification

- `python3 -B -m py_compile ui/calc_window.py tests/test_app_calculator_ui_smoke.py`
  - passed
- `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py tests/test_en14825_golden.py -q`
  - `11 passed`
- 새 smoke `test_en_calculate_button_displays_scop_result_text`는
  `tests/test_en14825_golden.py::test_en14825_golden_scop_average`와 동일한
  sample 값을 사용해 UI 경로에서도 SCOP 결과가 표시되는지 확인.

## Task Results

- task 2: OK
  - `init_en_tab`:
    - 기존 A/B/C/D test point 입력을 A/B/C/D/TOL/Tbiv 6 포인트로 확장.
    - SCOP 추가 파라미터 group 신설 (p_design_h, climate combo,
      TOL/Tbiv °C, p_to/p_sb/p_ck/p_off W).
    - climate combo `currentData()`는 calculator API가 받는 문자열
      `"average" / "warmer" / "colder"` 그대로 반환.
    - 입력 widget 에러 리셋 binding 유지.
  - `calculate_en`:
    - `_get_float_val`로 6 test point의 (cap, pow) 추출 → dict 형태로
      `calculate_scop(test_points=...)`에 전달.
    - TOL/Tbiv 온도와 standby power는 음수 또는 0이 유효하므로 `allow_zero=True`.
    - UI는 standby를 W로 받고 `/ 1000.0`로 kW 변환 후 calculator에 전달.
    - 결과는 `EN14825 SCOP (<climate>) 결과: <scop>` 형식으로 result label에 표시.
  - 새 smoke 테스트는 `average` 골든 케이스 입력을 그대로 사용해
    "EN14825 SCOP" 및 "결과:" substring 노출만 검증 (수치 비교는 골든 테스트가
    이미 보호).

## Test Results

- `tests/test_app_calculator_ui_smoke.py` → 7 passed
  - 신규: `test_en_calculate_button_displays_scop_result_text` → PASS
- `tests/test_en14825_golden.py` → 4 passed
  - SEER, SCOP average/warmer/colder 모두 unchanged.

## Changed Files

- `ui/calc_window.py`
- `tests/test_app_calculator_ui_smoke.py`

## Known Failures / Risks

- TOL/Tbiv 온도와 p_design_h를 사용자가 항상 입력해야 함 (optional 처리 X).
  이는 calculator API 입장에서는 안전하지만 UX적으로는 향후 default fill /
  하단 hint를 검토할 수 있다. 본 작업의 scope 밖.
- climate 선택 외 appliance_type은 현재 calculator의 default(`reversible`)를
  사용한다. heating_only 케이스가 필요하면 별도 UI 작업이 필요하다.
- EN tab의 입력 항목이 늘어났지만 layout 정돈(스크롤, 그룹 분리)은 추가 작업
  없이 form layout 그대로 사용. 매우 작은 화면에서는 후속 UI 조정 필요할 수
  있음.

## Next Suggested Action

- audit_4 task 3 (CalculatorInputEnvelope 첫 slice)

## Scope Compliance

- 계산기 공식, EN14825 golden expected, region config 모두 미수정.
- 계산기 public API (`calculate_scop` signature) 미변경.
- UI tab/계산 경로만 확장.
- 테스트는 PyQt5 import skip guard 유지 (`importorskip`).

## Commit / Push

- 본 보고서 작성 시점 source 커밋: `b673293` (feat: wire EN14825
  calculate_en() to calculate_scop).
- 다음: report 커밋 후 push.
