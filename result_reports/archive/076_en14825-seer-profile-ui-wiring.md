# 076 EN14825 SEER profile and UI wiring

## Goal

audit_5 task 6: 이미 구현되어 있던 `EN14825Calculator.calculate_seer()`를
profile / dispatcher / UI 흐름에서 사용할 수 있게 연결한다. SCOP 경로 동작은
보존한다.

## Scope

- `core/calculator_profiles.py` (en14825_seer profile 추가)
- `tests/test_calculator_profiles.py` (resolve / enabled set 갱신)
- `tests/test_calculator_dispatcher.py` (dispatcher 검증 추가)
- `ui/calc_window.py` (combo 정렬, p_design_c 입력 추가, metric-aware
  calculate_en 분기, en_profile tracking)
- `tests/test_app_calculator_ui_smoke.py` (combo guard 갱신, SEER profile
  smoke, SEER 결과 label smoke)

## Non-goals

- `calculate_seer()` 공식 수정
- EN14825 golden expected 수정
- SCOP 경로 동작 변경
- EN UI 전체 redesign
- ML adapter 작업과 혼합

## Verification

- `python3 -B -m pytest tests/test_calculator_profiles.py
  tests/test_calculator_dispatcher.py tests/test_app_calculator_ui_smoke.py
  tests/test_en14825_golden.py -q` → `48 passed`
- `python3 -B -m pytest -q` → `329 passed, 23 xfailed` (회귀 없음)

## Task Results

- task 6: OK
  - Profile: `en14825_seer`
    - `standard="EN_14825"`, `region="europe"`, `metric="SEER"`,
      `mode="cooling"`, `calculator_id="en14825"`.
    - SEER 경로는 SCOP config의 정적 키를 읽지 않으므로 calculator
      constructor 호출을 만족시키기 위해 `data/region_configs/en14825_scop.json`
      을 재사용한다. 별도 SEER JSON config는 생성하지 않음.
  - Dispatcher: 기존에 `calculator_id="en14825"`를 이미 지원하고 있어서 추가
    수정 없이 새 profile로 EN14825Calculator를 반환한다 (테스트로 확인).
  - UI:
    - EN combo는 SCOP/SEER profile을 모두 노출하며, SCOP을 첫 항목으로 정렬해
      기존 사용자 경험을 보존.
    - 새 입력 `p_design_c (kW, SEER)` 추가. `p_design_h`, climate, TOL/Tbiv
      입력은 SCOP 전용으로 label에 명시.
    - `on_region_changed_en`이 `self.en_profile`을 함께 저장.
    - `calculate_en()`은 `self.en_profile.metric == "SEER"`이면
      `calculate_seer()` 경로를 사용. 그 외는 기존 SCOP 경로.
    - SEER 결과 label: `EN14825 SEER 결과: <seer>`.
    - SCOP 결과 label: `EN14825 SCOP (<climate>) 결과: <scop>` (변경 없음).
  - Tests:
    - profile / dispatcher: en14825_seer profile resolve, enabled set 갱신,
      dispatcher가 같은 EN14825Calculator 반환 확인.
    - UI smoke: combo가 두 profile을 모두 노출, profile 전환 시
      `en_profile.metric`이 즉시 갱신되는지 확인, SEER profile + SEER 골든
      sample → label에 `EN14825 SEER / 결과:` 출력 확인.

## Test Results

- `tests/test_calculator_profiles.py` → 14 passed (회귀 없음)
- `tests/test_calculator_dispatcher.py` → 11 passed (회귀 없음)
- `tests/test_app_calculator_ui_smoke.py` → 10 passed
  - 신규 3건 추가, 1건 갱신.
- `tests/test_en14825_golden.py` → 4 passed (수치 보존)
- 전체 suite → 329 passed, 23 xfailed.

## Changed Files

- `core/calculator_profiles.py`
- `tests/test_calculator_profiles.py`
- `tests/test_calculator_dispatcher.py`
- `ui/calc_window.py`
- `tests/test_app_calculator_ui_smoke.py`

## Known Failures / Risks

- EN tab의 입력 항목이 SEER/SCOP을 모두 노출해 화면이 더 길어졌다. 매우 작은
  화면에서는 후속 layout 정리가 필요할 수 있다 (scope 밖).
- SEER profile은 SCOP config 경로를 재사용한다. 향후 SEER 전용 정적
  파라미터가 필요해지면 별도 config JSON을 신설하고 profile config_path를
  바꿔야 한다. 현재 calculator 코드는 SEER 계산에서 scop_config를 직접
  참조하지 않음을 확인했다.
- combo 정렬은 `metric == "SCOP" ? 0 : 1`로만 결정한다. 추가 EN profile이
  생기면 정렬 정책을 재확인해야 한다.

## Next Suggested Action

- audit_5 task 4 (AHRI HP/HSPF2 happy-path smoke)

## Scope Compliance

- `calculate_seer()` 공식, EN14825 golden expected, SCOP 경로 동작 모두
  미변경.
- EN UI 전체 redesign 없음 (기존 form layout 위에 입력 한 줄과 metric-aware
  분기만 추가).
- ML adapter 작업과 혼합 없음 (audit_5 task 3/5는 별도 단계).
- calculator public API 변경 없음.

## Commit / Push

- Source commit: `80ef665`.
- Report commit: 별도로 추가 예정.
