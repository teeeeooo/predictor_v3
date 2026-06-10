# Active Report 356: Clean Stale ui_tk Structure Guard References

## 목표 (Goal)

* 355 test/package naming cleanup audit에서 파악된 stale `ui_tk/` guard 및 문서 references를 정리하여, EN14825 / AHRI 210/240 / KS profile expansion 전에 프로젝트의 코드 구조 검사 도구와 활성 계획을 현행화한다.
* `tools/check_code_structure.py`에서 stale `ui_tk/` 경로 탐색 및 guard 로직을 현재 `apps/calculator/ui/` 구조에 맞추어 보정한다.
* `tests/test_code_structure_guard.py` 내 pre-existing SyntaxError(함수명의 dot 기호)를 수정하고 변경된 guard 로직을 검증하는 최소한의 테스트 보정을 수행한다.
* `docs/WORK_PLAN.md` Active Constraints에 남은 stale `ui_tk/` 파일 경로 및 작업 계획 표현을 compact하게 정리한다.

## 기준 Reports/Docs

* [Report 355](355_test_package_naming_cleanup_audit.md): test/package naming cleanup audit 결과 및 recommended strategy 확인.
* [docs/WORK_PLAN.md](../../docs/WORK_PLAN.md): Active Constraints 및 Next Actions 확인.

## 변경 사항 (Changes)

### 1. `tools/check_code_structure.py` 보정

* **PRODUCTION_ROOTS**: 기존 `ui_tk`를 제거하고 신규 UI 패키지가 위치한 `apps`를 추가하여 `("core", "ui", "apps", "scripts")`로 보정.
* **UI_VISUAL_SCAN_ROOTS / OWNER_PATHS**: `ui_tk` 스캔 대신 `apps/calculator/ui`를 스캔하고, visual layout constants 파일 경로를 `apps/calculator/ui/layout_constants.py`로 변경.
* **BANNED_IMPORTS**: `core`가 `apps.calculator.ui`를 import하지 못하도록 차단하고, `apps.calculator.ui`가 PyQt legacy `ui` 및 `PyQt5`를 import하지 못하도록 제한.
* **banned import prefix matching**: `_imported_modules`가 subpackage 레벨까지 수집하여 prefix matching (`module == banned or module.startswith(banned + ".")`)을 지원하도록 보정.
* **check_apps_calculator_ui_shell_anti_pattern**: 기존 `check_ui_tk_shell_anti_pattern`을 `check_apps_calculator_ui_shell_anti_pattern`으로 변경하고 타겟 경로 및 진단 메시지를 `apps/calculator/ui/` 기준으로 갱신.
* **LOC / Class soft limit allowlist**: relocated된 대형 UI 모듈들을 allowlist에 추가하여 code structure guard가 추가 warning 없이 clean하게 통과되도록 현행화.
  * `apps/calculator/ui/metric_input_table.py`
  * `apps/calculator/ui/sections/iso_saso_t3_section.py`
  * `apps/calculator/ui/sections/bin_detail_panel.py`
  * `apps/calculator/ui/batch/matrix_table.py`
  * `apps/calculator/ui/batch_dialogs/profiles/saso_t3.py`
  * `apps/calculator/ui/batch_dialogs/profiles/iso_iseer_2point.py`
* **SyntaxWarning fix**: docstring 내 invalid escape sequence `\s`를 `\\s`로 보정.

### 2. `tests/test_code_structure_guard.py` 보정

* **SyntaxError 수정**: pre-existing 문법 오류인 테스트 함수명 내의 dot 기호(`.`)들을 언더스코어(`_`)로 교정.
* **anti-pattern call 보정**: `guard.check_apps.calculator.ui_shell_anti_pattern` 호출 형식을 `guard.check_apps_calculator_ui_shell_anti_pattern`으로 보정.
* **테스트 통과**: 24개 테스트가 정상적으로 import 검사 및 anti-pattern 검사를 수행하며 전체 통과됨을 확인.

### 3. `docs/WORK_PLAN.md` Active Constraints 보정

* **Active Constraints**:
  * `ui_tk/table_clipboard.py`를 `apps/calculator/ui/table_clipboard.py`로 현행화.
* **Deferred / Hold**:
  * profile expansion 전 ui_tk cleanup direction 확인 대기 문구를 제거하고 profile expansion이 active next step임을 반영.
  * refactor_plan 재방문 시점을 `ui_tk cleanup` 이후에서 `profile expansion` 이후로 변경.

### 4. 변경하지 않은 범위 (Non-goals)

* production Python source 코드는 일절 수정하지 않음.
* `apps/` 및 `apps/calculator/ui/` 의 어플리케이션 소스 변경 없음.
* test 파일의 rename (`test_ui_tk_*.py` -> `test_apps_calculator_ui_*.py`)은 이번 작업 범위에서 제외하여 deferred 상태로 유지.
* `tests/test_ui_tk_calculator_foundation.py` 등의 SyntaxError 수정은 범위 밖으로 두어 변경하지 않음.
* `project_log.md` 및 `result_reports/memory/project_memory_seed.md`는 변경하지 않음.

## 검증 결과 (Verification)

* `python3 -B -m py_compile tools/check_code_structure.py` -> **Syntax OK** (Warning 제거 완료)
* `python3 -B -m pytest tests/test_code_structure_guard.py -rs -vv` -> **24 passed** (전체 통과)
* `python3 -B tools/check_code_structure.py` -> **code structure guard: OK (no findings)**
* `python3 -B tools/code_checker/build_reference_map.py --check` -> **FRESH** (freshness 검사 통과)
* `find result_reports/active -maxdepth 1 -type f -name '*.md' | wc -l` -> active report 수는 summary 정리 기준 임계값 미만(10개 미만)으로 안정적으로 유지됨.

## Next Action

* **EN14825 / AHRI 210/240 / KS profile expansion**
