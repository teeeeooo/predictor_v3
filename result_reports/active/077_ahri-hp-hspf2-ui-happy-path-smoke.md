# 077 AHRI HP / HSPF2 UI happy-path smoke

## Goal

audit_5 task 4: AHRI HP 모드에서 SEER2 + HSPF2 v3가 실제로 함께 표시되는지
offscreen smoke 1건을 추가한다. 기존 smoke는 AC 경로와 HSPF2 validation
경로만 보호하고 있었고, HP happy-path는 비어 있었다.

## Scope

- `tests/test_app_calculator_ui_smoke.py` (신규 smoke 1건)

## Non-goals

- HSPF2 계산식 수정
- HSPF2 / AHRI SEER2 golden expected 수정
- UI redesign
- `ui/calc_window.py` 수정 (이미 HP path에서 SEER2 + HSPF2 v3 결과를 합쳐
  result label에 표시하는 로직이 들어가 있음)

## Verification

- `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py::test_ahri_hp_calculate_button_displays_seer2_and_hspf2_results -v`
  → 1 passed
- `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q` → `10 passed`

## Task Results

- task 4: OK
  - 새 smoke `test_ahri_hp_calculate_button_displays_seer2_and_hspf2_results`:
    - HP radio button 선택.
    - AHRI SEER2 필수 5 포인트 (A_Full, B_Full, B_Low, E_Int, F_Low) 입력.
    - HSPF2 v3 필수 7 포인트 (H01, H11, H12, H1N, H22, H2Int, H32) +
      t_off/t_on/defrost minutes 입력.
    - 입력 값은 `tests/test_ahri_hspf2_v3_smoke.py`에서 가져와 HSPF2 계산기가
      안정적으로 수치를 만들 수 있도록 함.
    - `button_calculate.click()` 후 result label에 `"AHRI SEER2 (HP) 결과:"`
      와 `"HSPF2 v3 결과:"`가 모두 포함되는지 substring 검증.
  - PyQt5 없는 환경에서는 모듈 상단의 `pytest.importorskip("PyQt5")` 가드가
    smoke 전체를 skip하므로 회귀 위험은 없다.

## Test Results

- `tests/test_app_calculator_ui_smoke.py` → 10 passed
  - 신규 1건 추가, 기존 9건 회귀 없음.

## Changed Files

- `tests/test_app_calculator_ui_smoke.py`

## Known Failures / Risks

- 본 smoke는 substring 검증만 한다. 수치 비교는 `tests/test_ahri_seer2_smoke.py`
  와 `tests/test_ahri_hspf2_*` 단위 테스트가 보장한다. UI에서 결과가 빈
  문자열로 나오는 등 silent 실패가 발생하면 substring assertion이 잡아낸다.
- AHRI SEER2 입력 값은 HSPF2 계산이 안정적으로 동작하는 set에 맞춰 선택했다.
  AHRI SEER2 단독으로 더 큰 capacity를 쓰는 경우 (예: 36000 Btu/h) HSPF2
  계산이 어떻게 동작하는지는 다른 smoke가 추가로 보호해야 한다.

## Next Suggested Action

- audit_5 task 3 (PredictedPointsEnvelope 첫 slice)

## Scope Compliance

- 계산기 코드, region config, golden expected 모두 미수정.
- UI 코드 미수정.
- 새 테스트 1건만 추가, 기존 테스트 수정 없음.

## Commit / Push

- Source commit: `223192b`.
- Report commit: 별도로 추가 예정.
