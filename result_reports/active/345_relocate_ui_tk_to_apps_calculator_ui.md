# Report 345: Relocate ui_tk to apps/calculator/ui

## Goal (목표)

- 344 apps calculator skeleton and entrypoint handover 완료에 따라, 기존의 calculator-only Tkinter UI 패키지인 `ui_tk/`를 `apps/calculator/ui/` 하위로 완전히 이주(relocate)하여 애플리케이션 관심사 격리를 마친다.

## 기준으로 사용한 Reports (References)

- [342_calculator_first_apps_package_architecture_audit.md](342_calculator_first_apps_package_architecture_audit.md)
  - 후보 구조 및 Slice 3 계획을 참조함.
- [343_charter_architecture_policy_alignment.md](343_charter_architecture_policy_alignment.md)
  - UI toolkit 정책 및 패키지 구조 가이드를 참조함.
- [344_apps_calculator_skeleton_entrypoint_handover.md](344_apps_calculator_skeleton_entrypoint_handover.md)
  - thin entrypoint 및 app skeleton 구현 상태를 확인하고 후속 마이그레이션을 진행함.

## 이동한 Package (Moved Package)

- git mv를 사용하여 `ui_tk/` 패키지 하위의 53개 파일을 `apps/calculator/ui/` 하위로 완전히 이주함:
  - `ui_tk/` -> `apps/calculator/ui/`
  - root level에 레거시 `ui_tk/` 디렉토리나 패키지 잔재는 남기지 않고 모두 삭제 및 정리함.
  - `apps/calculator/ui/__init__.py`가 정상적으로 존재하여 패키지로 기능함.

## Import Path 보정 범위

- **Source Code**:
  - `apps/calculator/app.py` 내부의 UI import 경로를 `apps.calculator.ui.calculator_app`으로 보정함.
  - `apps/calculator/ui/` 하위 전체 파일(53개) 내부의 모든 `ui_tk` 상대/절대 임포트 경로를 `apps.calculator.ui` 패키지 경로로 일괄 교정함.
- **Test Code**:
  - `tests/` 디렉토리 내의 39개 테스트 파일에 분산되어 있던 `ui_tk` 관련 임포트 경로를 모두 `apps.calculator.ui` 패키지 경로로 일괄 교정함.
- 루트 wrapper인 `app_calculator.py` 및 `app_calculator_tk.py`는 이미 `apps.calculator.app`에 대리 위임하는 구조이므로 추가 수정이 불필요함을 확인하고 현행 유지함.

## Stale calculator_app Docstring 보정 내용

- `apps/calculator/ui/calculator_app.py`의 top-level docstring에서 기존 "does not replace PyQt reference" 취지의 오래된 feasibility-spike성 문구를 모두 제거하고 다음 정보를 기술하도록 보정함:
  - `apps.calculator.ui.calculator_app`이 `apps.calculator.app`에서 사용하는 현재 활성 Tkinter calculator UI shell임.
  - `ui/` 하위의 legacy PyQt 계산기는 은퇴 전까지의 read-only reference에 불과함.
  - PyQt 모듈 임포트를 엄격히 금지함.

## project_architecture.md 보정 내용

- `docs/architecture/project_architecture.md`를 보정하여:
  - Section 1. 파일 구조 내 `ui_tk/` 설명을 제거하고 `apps/calculator/ui/`가 현재 마이그레이션 완료된 Tkinter UI 패키지임을 명시함.
  - `ui/`가 legacy PyQt multi-app UI 경로이며, `apps/train` 및 `apps/predict`가 future PySide6 reserved boundary임을 일관되게 표현함.
  - Section 3.3의 PyQt-specific table guardrails 및 Section 5의 calc_window.py routing contract 설명에 legacy PyQt UI에 국한된다는 안내식 Note 및 scope 한정을 명확히 적용하여 혼선을 종식함.

## Compatibility Shim을 만들지 않은 이유

- 레거시 임포트 경로를 유지하기 위한 compatibility shim(`ui_tk/` 패키지 껍데기 등)을 루트에 남길 경우, 향후 패키지 구조가 지저분해지고 cleanup 의미가 무색해짐. 따라서 소스 및 테스트 전역의 모든 임포트 경로를 direct new import로 완벽히 갱신하고 `ui_tk`를 단숨에 소멸시키는 방향을 채택함.

## ui/ Legacy PyQt와 Train/Predict를 수정하지 않은 이유

- `ui/` 레거시 및 `app_train.py` / `app_predict.py` 등은 reserved future boundary로서 장기적인 PySide6 재개발 시점에 이주가 다루어질 영역이므로, current calculator-only 마이그레이션 영역과 철저히 격리하고 변경을 가하지 않음.

## Tests 및 Validation 결과

- `py_compile`을 통해 moved files 및 entrypoints에 구문 오류가 없고 정상 빌드됨을 검증함.
- focused pytests(유닛 테스트 총 108개)가 100% 성공적으로 패스됨을 확인하여 마이그레이션으로 인한 어떠한 기능적 회귀(regression)도 발생하지 않았음을 입증함:
  - `tests/test_apps_calculator_entrypoints.py` (PASSED)
  - `tests/test_ui_tk_batch_models.py` (PASSED)
  - `tests/test_ui_tk_batch_matrix_models.py` (PASSED)
  - `tests/test_ui_tk_batch_matrix_table.py` (PASSED)
  - `tests/test_ui_tk_batch_table_controller.py` (PASSED)
  - `tests/test_ui_tk_batch_table_viewport.py` (PASSED)
  - `tests/test_ui_tk_table_controller_per_cell_roles.py` (PASSED)
  - `tests/test_ui_tk_hong_kong_cspf_matrix_migration.py` (PASSED)
  - `tests/test_ui_tk_iso_iseer_2point_batch_dialog.py` (PASSED)
  - `tests/test_ui_tk_saso_t3_batch_dialog.py` (PASSED)
  - `tests/test_ui_tk_batch_dialog_shell.py` (PASSED)
  - `tests/test_ui_tk_table_controller.py` (PASSED)
  - `tests/test_ui_tk_metric_input_table_controller_parity.py` (PASSED)
- `python3 -B tools/check_code_structure.py` 통과 (OK, 경고 사항 모두 소멸되어 Clean).

## CODEBASE_REFERENCE_MAP.md Regeneration 결과

- relocated package 변경 정보를 영구 문서에 반영하기 위해 `docs/code_map/CODEBASE_REFERENCE_MAP.md`를 재생성하였으며, `freshness` 검증(FRESH)을 통과 완료함.

## WORK_PLAN 업데이트 여부

- `docs/WORK_PLAN.md`에 본 이주 (345) 완료를 기록하고, 차기 우선순위를 `Active report lifecycle cleanup (threshold exceeded)`으로 갱신함.

## 제외 범위 (Excluded Scope)

- **Train/Predict 이주 제외**: `apps/train` 및 `apps/predict` 생성 및 PyQt 이주 진행 없음.
- **물리적 파일명 변경 제외**: 테스트 파일명(`test_ui_tk_*.py`) 등은 이번 이주 단계에서 무리하게 파일명 리네임을 수행하지 않고 import path 보정만 적용함.
- **공통/핵심 모듈 변경 없음**: `calculator/core`, profile/region configs, golden/fixtures의 변경 사항 없음.
- **Project log 및 memory seed 유지**: `project_log.md` 및 `result_reports/memory/project_memory_seed.md` 파일은 전혀 수정하지 않음 (unchanged).

## Project Memory Delta

- none

## Lifecycle Note

- active report count is below lifecycle threshold

## Next Action suggested (차기 과제)

1. **Active report lifecycle cleanup (threshold exceeded)**
