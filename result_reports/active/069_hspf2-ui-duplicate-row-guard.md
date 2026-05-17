# 069 HSPF2 UI duplicate row guard

## Goal

audit_4 task 1: HSPF2 입력 form에 중복 row가 생기지 않도록 regression 방지 smoke
보강. audit_4가 지적한 `form_hspf2.addRow(...전력...)` 중복은 현재 코드에서 실제로
관찰되지 않았으므로 코드 삭제 작업은 없고 가드 테스트만 추가한다.

## Scope

- `tests/test_app_calculator_ui_smoke.py`
- HSPF2 input widget key/instance 구조 검증
- HP 모드 HSPF2 필수 입력 누락 시 validation 동작 확인

## Non-goals

- AHRI HSPF2 계산식 수정
- HSPF2 expected/golden 수정
- UI redesign 또는 layout 재구성
- `ui/calc_window.py` 코드 수정 (실제 중복이 없으므로 변경하지 않음)

## Verification

- `python3 -B -m py_compile tests/test_app_calculator_ui_smoke.py`
  - passed
- `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q`
  - `6 passed`
- `ui/calc_window.py` 211~232 line 직접 확인: HSPF2 loop 내 addRow는
  `능력 (Btu/h)` 1회 + `전력 (W)` 1회로 정상. 중복 없음.

## Task Results

- task 1: OK
  - audit_4가 지적한 `form_hspf2.addRow(...전력...)` 중복은 현재 main branch 코드에서
    재현되지 않음을 직접 확인. 따라서 코드 수정은 수행하지 않음.
  - 향후 regression 방지를 위해 두 smoke 테스트 추가:
    - `test_hspf2_input_widgets_have_no_duplicate_rows`: 7개 point × 2 + 4 extras
      = 18개 widget key가 정확히 등록되고 cap/pow widget 인스턴스가 분리되어 있음을
      확인.
    - `test_hspf2_required_input_raises_validation_error_when_missing`: HP 모드에서
      HSPF2 필수 입력이 비어 있으면 `InputValidationError`가 발생하는지
      `calculate_hspf2_v3()` 호출로 확인. (on_calculate를 직접 부르면
      `QMessageBox.warning`이 호출되므로 validation 경로만 격리해서 점검.)

## Test Results

- new tests:
  - `test_hspf2_input_widgets_have_no_duplicate_rows` → PASS
  - `test_hspf2_required_input_raises_validation_error_when_missing` → PASS
- existing tests in same file:
  - `test_calculator_window_instantiates_offscreen` → PASS
  - `test_ahri_combo_uses_profile_ids_for_dispatcher_selection` → PASS
  - `test_en_combo_uses_profile_ids_for_dispatcher_selection` → PASS
  - `test_ahri_calculate_button_displays_result_text` → PASS
- 총 6 passed (PyQt5 사용 가능 환경).

## Changed Files

- `tests/test_app_calculator_ui_smoke.py`

## Known Failures / Risks

- audit_4의 중복 row 관찰은 현재 코드와 일치하지 않음. 만약 audit_4가 별도 작업
  브랜치를 보고 작성된 것이라면, 그 브랜치를 머지할 때 본 guard 테스트가 실패하면서
  중복 발생을 탐지해줄 것이다.
- HSPF2 입력 UI는 여전히 단일 form 구조이므로 layout 자체의 가독성은 별도 UX 작업
  대상으로 남는다. 본 작업의 scope 밖.

## Next Suggested Action

- audit_4 task 2 (EN14825 calculate_en()를 실제 SCOP 계산 경로로 연결)

## Scope Compliance

- AHRI HSPF2 계산식 변경 없음.
- HSPF2 golden expected 변경 없음.
- `ui/calc_window.py` 수정 없음.
- 테스트 파일 1개에만 변경, 다른 모듈/문서/계산기/region config 미수정.

## Commit / Push

- 본 보고서 작성 시점에는 아직 source/report 커밋이 분리되지 않음.
- 다음 단계: source 커밋 → report 커밋 → push 순으로 진행.
