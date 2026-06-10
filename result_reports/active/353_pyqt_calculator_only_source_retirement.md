# Active Report 353: PyQt Calculator-Only Source Retirement

## 목표 (Goal)

* Mixed ISO table test blocker가 해제되었으므로, runtime entrypoint에서 분리된 legacy PyQt calculator-only source 3개 파일을 retire한다.
* 삭제 후 full pytest를 실행하여 retirement change로 인한 regression이 없음을 확인한다.
* shared PyQt utility (ui/spreadsheet_table.py, ui/theme.py)와 Train/Predict PyQt path는 유지한다.
* current calculator app path인 apps/calculator/ui/는 수정하지 않는다.

## 기준으로 사용한 Reports (Reference Reports)

* [Report 349](349_calculator_pyqt_reference_retirement_preflight.md): PyQt 계산기 은퇴 preflight — retirement readiness 판단, reference value inventory, blocker 식별
* [Report 350](350_349_report_local_link_correction.md): 349 local link correction 완료 확인
* [Report 351](351_mixed_iso_table_test_split_or_retirement.md): mixed test blocker 해제 — ui.calculators_2point/ProfileInputGrid import 제거 완료
* [Report 352](352_351_report_wording_validation_note_correction.md): 351 wording 보정 및 full pytest 필요 note 추가
* [Report 154](../archive/154_pyqt-calculator-retirement-audit.md): PyQt calculator-only source retirement 대상 분류 (audit)
* [Report 156](../archive/156_shared-pyqt-utility-retention-decision.md): ui/spreadsheet_table.py, ui/theme.py quarantine/hold 결정

## 삭제한 Files (Retired Sources)

* `ui/calc_window.py` — `git rm`으로 영구 삭제
* `ui/calculators_2point.py` — `git rm`으로 영구 삭제
* `ui/calculator_errors.py` — `git rm`으로 영구 삭제

## 유지한 Files (Retained Files)

### Shared utility (quarantine/hold 유지)
* `ui/spreadsheet_table.py`
* `ui/theme.py`

### Train/Predict PyQt path
* `ui/train_window.py`
* `ui/predict_window.py`
* `ui/base_model.py`
* `ui/base_view.py`
* `ui/__init__.py`

### Current calculator entrypoint
* `app_calculator.py`
* `app_calculator_tk.py`
* `apps/calculator/` (전체 유지)

### Test utilities
* `tests/helpers/pyqt_env.py`
* `tests/test_pyqt_environment_guard.py`
* `tests/test_spreadsheet_table_model.py`
* `tests/test_spreadsheet_table_view.py`
* `tests/test_ui_theme_tokens.py`

## Pre-Delete Reference Check 결과

* `app_calculator.py`, `app_calculator_tk.py`, `app_train.py`, `app_predict.py`: 삭제 대상 import 없음
* `apps/calculator/ui/`: 삭제 대상 import 없음
* `tests/`: `test_code_structure_guard.py`에 fixture 문자열 및 inline allowlist 매개변수용 경로만 존재 (runtime import 아님)
* `tools/check_code_structure.py`: `ui/calc_window.py`, `ui/calculators_2point.py`가 LOC/CLASS allowlist에 hardcoded — source 삭제 후 함께 정리
* `docs/architecture/project_architecture.md`, `project_brief.md`, archive docs: reference 존재하지만 이번 수정 금지 대상 (후속 active docs update slice로 기록)

## Stale Reference 정리 결과 (Task 4)

* `tools/check_code_structure.py`의 `LOC_ALLOWLIST`에서 `ui/calc_window.py`, `ui/calculators_2point.py` 제거
* `tools/check_code_structure.py`의 `CLASS_ALLOWLIST`에서 `ui/calculators_2point.py`, `ui/calc_window.py` 제거
* `ui/spreadsheet_table.py`는 quarantine/hold 상태이므로 양 allowlist에 유지
* `tests/test_code_structure_guard.py`의 fixture 문자열 (`"ui/calc_window.py"`)은 `check_soft_limits` 함수의 unit test 동작 검증용으로, runtime import가 아니며 파일 존재 여부와 무관하게 유효하므로 수정 없이 유지

## Post-Delete Reference Check 결과

* `app_calculator.py`, `app_calculator_tk.py`, `apps/`, `ui/`, `tests/`: `ui.calc_window`, `ui.calculators_2point`, `ui.calculator_errors`, `CalculatorWindow`, `ProfileInputGrid` runtime import 없음
* 잔존 참조: `ui/theme.py` docstring (수정 금지 파일) 및 `test_code_structure_guard.py` fixture 문자열 — 모두 non-runtime reference

## Focused Validation 결과 (Task 6)

* `python3 -B -m py_compile app_calculator.py app_calculator_tk.py apps/calculator/app.py`: **OK**
* `import apps.calculator.app, app_calculator, app_calculator_tk`: **OK** ("calculator entrypoint imports ok")
* `pytest tests/test_apps_calculator_entrypoints.py`: **4 passed**
* `pytest tests/test_spreadsheet_table_model.py tests/test_ui_theme_tokens.py tests/test_pyqt_environment_guard.py`: **95 passed**
* `pytest tests/test_spreadsheet_table_view.py`: **8 skipped** (macOS PyQt5 environment guard — expected)

## Full Pytest 결과 (Task 7)

* `python3 -B -m pytest -q -rxXs` (두 pre-existing SyntaxError 파일 포함): **collection 단계에서 exit code 2**
  * `tests/test_code_structure_guard.py`: SyntaxError (function name에 `.` 포함) — **pre-existing** (이번 변경 이전에도 동일)
  * `tests/test_ui_tk_calculator_foundation.py`: SyntaxError (function name에 `.` 포함) — **pre-existing** (이번 변경 이전에도 동일)
* `python3 -B -m pytest -q --ignore=tests/test_code_structure_guard.py --ignore=tests/test_ui_tk_calculator_foundation.py`: **975 passed, 9 skipped, 19 xfailed, 5 failed**
* 5 failures 상세:
  * `tests/test_code_checker_reference_map.py::test_keyword_hit_group_not_ownership` — pre-existing logic test failure (not related to retirement)
  * `tests/test_ui_tk_hong_kong_hspf_detail.py::TestHongKongHspfSectionDefaults::test_section_defaults_calculate_hspf_summary` — pre-existing
  * `tests/test_ui_tk_window_lifecycle_repair.py::TestMetricTabChangeRefitScheduling::test_iso_iseer_section_receives_visibility_callback` — pre-existing
  * `tests/test_ui_tk_window_lifecycle_repair.py::TestMetricTabChangeRefitScheduling::test_saso_section_receives_visibility_callback` — pre-existing
  * `tests/test_ui_tk_window_measurement.py::test_nested_notebook_uses_hidden_tabs_for_width_but_visible_tab_for_height` — pre-existing
* **모든 failure가 retirement change 이전에도 동일하게 실패함을 git stash 검증으로 확인. Retirement change로 인한 regression 없음.**

## CODEBASE_REFERENCE_MAP.md 재생성 결과 (Task 8)

* `python3 -B tools/code_checker/build_reference_map.py`: Reference map written, 228 lines
* `python3 -B tools/code_checker/build_reference_map.py --check`: **FRESH** (working directory uncommitted changes 경고는 정상)
* `grep "ui/calc_window\|ui/calculators_2point\|ui/calculator_errors" docs/code_map/CODEBASE_REFERENCE_MAP.md`: **결과 없음** (삭제된 파일이 code map에 남지 않음 확인)

## WORK_PLAN 업데이트 결과 (Task 9)

* Recent history에 351 (mixed test blocker resolved)과 353 (PyQt calculator-only source retirement) 완료 추가
* Next Actions 1번을 "PyQt calculator active docs/support matrix update after source retirement (Recommended next slice)"로 교체
* Deferred/Hold에서 "PyQt calculator source retirement remains on hold" 항목을 "completed" 상태로 교체

## 후속 active docs update 필요 여부

아래 docs/architecture/README references는 이번 작업에서 수정 금지 대상이므로 후속 slice에서 처리 필요:

* `docs/architecture/project_architecture.md`: `ui/calc_window.py` 라우팅/module-boundary text 포함
* `project_brief.md`: `app_calculator.py` / `ui/calc_window.py` 설명 포함
* `docs/guides/pyqt_test_support_matrix.md`: calculator widget test inventory 포함 — retirement 후 surviving PyQt tests만 반영하도록 갱신 필요
* `README.md`: `ui/`, `app_calculator.py` 설명 포함

## 제외 범위 (Non-Goals)

* apps/calculator/ui/ 수정 없음
* app_train.py / app_predict.py 수정 없음
* EN14825 / AHRI 210/240 / KS profile 구현 없음
* project_log.md 수정 없음
* memory seed 수정 없음
* archive 이동 없음
* apps/train, apps/predict 생성 없음

## next action (Next Action)

* PyQt calculator active docs/support matrix update slice: `docs/architecture/project_architecture.md`, `project_brief.md`, `docs/guides/pyqt_test_support_matrix.md`, `README.md`에 남은 legacy reference를 retirement 완료 상태로 반영한다.
