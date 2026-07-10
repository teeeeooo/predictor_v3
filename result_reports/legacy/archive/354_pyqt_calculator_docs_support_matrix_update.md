# Active Report 354: PyQt Calculator Active Docs and Support Matrix Update

## 목표 (Goal)

* PyQt calculator-only source retirement(Report 353) 완료 후, active docs와 PyQt support matrix의 current-state 표현을 정리한다.
* retired source(`ui/calc_window.py`, `ui/calculators_2point.py`, `ui/calculator_errors.py`)가 current implementation처럼 설명되는 문구를 제거/보정한다.
* shared PyQt utility와 Train/Predict PyQt path는 유지 상태로 문서화한다.
* current calculator path는 `apps/calculator/ui/`임을 명확히 한다.
* source/test/code map/project_log/memory seed는 수정하지 않는다.

## 기준으로 사용한 Reports (Reference Reports)

* [Report 353](353_pyqt_calculator_only_source_retirement.md): PyQt calculator-only source retirement 완료 — retired/retained files, follow-up docs list
* [Report 349](349_calculator_pyqt_reference_retirement_preflight.md): EN/AHRI/KS reference inventory 보존 확인
* [Report 156](../archive/156_shared-pyqt-utility-retention-decision.md): `ui/spreadsheet_table.py`, `ui/theme.py` quarantine/hold 결정

## Stale Reference Inventory 요약 (Task 2)

분류:

| 파일 | Stale 표현 | 분류 |
|------|-----------|------|
| `docs/architecture/project_architecture.md` | `ui/calc_window.py`가 current routing contract, current module boundary subject로 설명됨 | **current-state stale — 수정 대상** |
| `project_brief.md` | `app_calculator.py` / `ui/calc_window.py` PyQt offscreen launch smoke 보호 설명 | **current-state stale — 수정 대상** |
| `docs/guides/pyqt_test_support_matrix.md` | retired test 파일들이 active test target으로 나열됨 | **current-state stale — 수정 대상** |
| `README.md` | `ui/`, `app_calculator.py`가 calculator UI entry로 병렬 나열됨 | **current-state stale — 수정 대상** |
| `docs/WORK_PLAN.md` | 이전 task에서 이미 retirement 반영 완료 | **OK (이미 최신)** |

## docs/architecture/project_architecture.md 보정 내용 (Task 3)

* **File structure 섹션** `ui/` 설명 보정:
  * 이전: `app_calculator.py`, `app_train.py`, `app_predict.py`가 공유하는 레거시 화면 경로
  * 이후: `app_train.py`와 `app_predict.py`가 공유하는 Train/Predict 화면 경로 + PyQt calculator-only source retired + shared utility quarantine/hold 상태 명시

* **"UI / calc_window.py routing contract" 및 "Calculator UI module boundary" 섹션**:
  * 이전: current routing contract와 module boundary 설계 설명
  * 이후: **"PyQt Legacy Calculator Reference (Retired)"** 섹션으로 변환
  * 섹션 NOTE에 retired 상태와 current calculator UI(`apps/calculator/ui/`) 명시
  * 기존 내용을 historical record로 보존
  * Current state 표 추가 (current calculator UI, retained shared PyQt utility, retained Train/Predict PyQt)

## project_brief.md 보정 내용 (Task 4)

* **Calculator UI / ML adapter 경계 항목** 보정:
  * 이전: `app_calculator.py` / `ui/calc_window.py`는 PyQt offscreen launch smoke로 보호
  * 이후: PyQt calculator-only source retired + current entrypoint는 `app_calculator.py` → `apps.calculator.app:main` → `apps/calculator/ui/` + Train/Predict PyQt는 future rewrite 전 유지

## docs/guides/pyqt_test_support_matrix.md 보정 내용 (Task 5)

* **Purpose** 섹션: retirement 후 상태 반영
* **Retired 섹션 신설**: retired source와 removed tests 명시
  * Retired sources: `ui/calc_window.py`, `ui/calculators_2point.py`, `ui/calculator_errors.py`
  * Removed tests: `test_iso16358_result_table_copy_tsv.py`, `test_app_calculator_ui_smoke.py`, `test_iso16358_table_excel_like_behavior.py`
* **Retained PyQt Source 표** 신설: `ui/spreadsheet_table.py`, `ui/theme.py`, `ui/train_window.py`, `ui/predict_window.py`, `ui/base_model.py`, `ui/base_view.py`
* **Retained PyQt Tests 표** 신설: `test_spreadsheet_table_model.py`, `test_spreadsheet_table_view.py`, `test_ui_theme_tokens.py`, `test_pyqt_environment_guard.py`
* **PyQt Test Groups 섹션** 제거: retired test 파일들이 active test로 나열되어 있었음
* **Local Test Commands** 보정: retired test 파일 제거, retained tests만 나열
* **Known-bad environment policy**, **Host Matrix**, **Non-Goals** 유지 (환경 skip policy 내용은 그대로 보존)

## README.md 보정 내용 (Task 6)

* **What This Repository Contains** 섹션:
  * 이전: `Calculator UI and application entry points: ui/, app_calculator.py`
  * 이후: `Calculator UI and application entry points: app_calculator.py → apps/calculator/ui/`

* **Repository Map** 섹션:
  * 이전: `ui/ | Qt UI modules and calculator/predictor UI integration`
  * 이후: `ui/ | Legacy PyQt5 Train/Predict UI modules; PyQt calculator-only source retired`

## Retained PyQt/Shared/Train/Predict Scope

* **Retained shared PyQt utility (quarantine/hold)**:
  * `ui/spreadsheet_table.py`, `ui/theme.py`
* **Retained Train/Predict PyQt path**:
  * `ui/train_window.py`, `ui/predict_window.py`, `ui/base_model.py`, `ui/base_view.py`, `ui/__init__.py`
  * `app_train.py`, `app_predict.py`
  * `tests/test_spreadsheet_table_model.py`, `tests/test_spreadsheet_table_view.py`
  * `tests/test_ui_theme_tokens.py`, `tests/test_pyqt_environment_guard.py`

## Retired Calculator-Only Scope (확인)

* `ui/calc_window.py` — retired (Report 353)
* `ui/calculators_2point.py` — retired (Report 353)
* `ui/calculator_errors.py` — retired (Report 353)
* `tests/test_iso16358_result_table_copy_tsv.py` — retired (prior slice)
* `tests/test_app_calculator_ui_smoke.py` — retired (prior slice)
* `tests/test_iso16358_table_excel_like_behavior.py` — retired (Report 351)

## WORK_PLAN 업데이트 결과 (Task 7)

* Recent history에 354 docs update 완료 추가
* Next Actions 1번을 "Test/package naming cleanup after apps calculator UI relocation (Recommended next slice)"로 교체
* 3번으로 "Active report lifecycle cleanup if threshold reached" 추가

## 제외 범위 (Non-Goals)

* production Python source 수정 없음
* tests 수정 없음
* apps/ 수정 없음
* ui/ 파일 수정 없음
* docs/code_map/CODEBASE_REFERENCE_MAP.md 수정/regeneration 없음
* project_log.md 수정 없음
* result_reports/memory/project_memory_seed.md 수정 없음
* EN14825 / AHRI 210/240 / KS profile 구현 없음
* Train/Predict rewrite 없음

## 검증 결과 (Verification)

* `git status --short`: 허용된 docs 파일과 본 354 report만 diff 확인
* `grep "calc_window\|calculators_2point\|calculator_errors\|CalculatorWindow\|ProfileInputGrid"` on updated docs: retired source를 current implementation처럼 설명하는 active 문구 없음 확인
* `python3 -B tools/check_code_structure.py`: OK (no findings)
* `git diff --check`: whitespace 에러 없음

## next action (Next Action)

* Test/package naming cleanup after apps calculator UI relocation: apps/calculator/ui/ 패키지 이주 후 남은 test/package naming inconsistency를 정리한다.
