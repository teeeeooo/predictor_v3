# Report 340: Batch Foundation Foldering Implementation - Slice 2

## Goal (목표)

- 337 batch foundation foldering audit 결과와 338 Slice 1 작업의 흐름에 따라, root에 남아 있던 batch 관련 6개 파일(case_table, matrix_table, viewport, controller, table_controller, compat_table)을 `ui_tk/batch/` 패키지로 안전하게 이동하고 관련된 import 경로들을 일괄 갱신하여 패키지 구조화를 완료한다.

## 기준으로 사용한 Reports (References)

- [337_batch_foundation_foldering_audit.md](337_batch_foundation_foldering_audit.md)
  - Candidate A 구조에 기반한 Slice 2 계획을 준수하여 진행함.
- [338_batch_foundation_foldering_slice_1_models.md](338_batch_foundation_foldering_slice_1_models.md)
  - toolkit-neutral model 및 spec 파일 이동 결과와 import matching 패턴을 참조함.
- [339_338_report_reference_link_typo_correction.md](339_338_report_reference_link_typo_correction.md)
  - link correction 및 validation typo 수정 여부를 확인하고 반영함.

## 이동한 파일 (Moved Files)

- git mv를 사용하여 root에 남아 있던 batch foundation 6개 파일을 신규 `ui_tk/batch/` 패키지로 이동 완료:
  - `ui_tk/batch_case_table.py` -> `ui_tk/batch/case_table.py`
  - `ui_tk/batch_matrix_table.py` -> `ui_tk/batch/matrix_table.py`
  - `ui_tk/batch_table_viewport.py` -> `ui_tk/batch/viewport.py`
  - `ui_tk/batch_controller.py` -> `ui_tk/batch/controller.py`
  - `ui_tk/batch_table_controller.py` -> `ui_tk/batch/table_controller.py`
  - `ui_tk/batch_table.py` -> `ui_tk/batch/compat_table.py`

## Import-only 보정 대상 (Import Correction Targets)

- 다음 9개 파일(및 관련 테스트 파일들)의 old imports를 신규 패키지 경로(`ui_tk.batch.*`)로 direct 일괄 보정함:
  - `ui_tk/batch/case_table.py`
  - `ui_tk/batch/matrix_table.py`
  - `ui_tk/batch/viewport.py`
  - `ui_tk/batch/controller.py`
  - `ui_tk/batch/table_controller.py`
  - `ui_tk/batch/compat_table.py`
  - `ui_tk/batch_dialogs/profiles/hong_kong_cspf.py`
  - `ui_tk/batch_dialogs/profiles/iso_iseer_2point.py`
  - `ui_tk/batch_dialogs/profiles/saso_t3.py`
  - `tests/test_ui_tk_batch_matrix_table.py`
  - `tests/test_ui_tk_batch_table_controller.py`
  - `tests/test_ui_tk_batch_table_viewport.py`

## Compatibility Shim을 만들지 않은 이유

- 본 codebase의 규모가 비교적 작고 old imports를 참조하는 파일의 범위가 명확히 한정되어 있었으므로, 불필요한 레거시 잔재와 복잡도를 방지하기 위해 compatibility shim을 별도로 만들지 않고 direct import 갱신을 원스텝으로 완료함.

## Behavior 변경 없음 확인

- 파일들의 위치 이동과 import path 보정 외에 레이아웃, 검증(validation), 재계산(calculation) 및 컨트롤러 바인딩 등의 어떠한 비즈니스 로직 및 동작상의 변경도 가해지지 않았음.

## CODEBASE_REFERENCE_MAP.md Regeneration 결과

- Slice 2 완료에 따라 최종 구조 변경을 명문화하기 위해 `docs/code_map/CODEBASE_REFERENCE_MAP.md`를 재생성하였으며, `freshness` 검증(FRESH)을 통과 완료함.

## WORK_PLAN 업데이트 여부

- `docs/WORK_PLAN.md`에 Slice 2 완료 사실을 명시하고, Next Actions의 최상단 항목을 `Calculator entrypoint handover from PyQt to Tkinter`로 최신화함.

## 제외 범위 (Excluded Scope)

- **UI core 수정 제외**: `ui_tk/table/` 하위 generic table core 파일들의 수정 및 변경 없음.
- **Batch dialog shell 수정 제외**: `ui_tk/batch_dialogs/shell.py` 파일의 변경 없음.
- **기타 core 및 config 수정 제외**: `calculator/core` 및 profile/region config, tests/fixtures 등의 변경 없음.
- **Project log 및 memory seed 유지**: `project_log.md` 및 `result_reports/memory/project_memory_seed.md` 파일은 전혀 수정하지 않음 (unchanged).

## 검증 결과 (Verification Results)

- `python3 -B -m py_compile` 통과 (OK)
- `python3 -B tools/check_code_structure.py` 통과 (OK)
- `python3 -B tools/code_checker/build_reference_map.py --check` 통과 (FRESH, OK)
- `git diff --check` 상의 whitespace 문제 없음 (OK)
- **Focused pytests** (총 104개 테스트 모두 성공 통과):
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

## Project Memory Delta

- none

## Lifecycle Note

- active report count is below lifecycle threshold

## Next Action suggested (차기 과제)

1. **Calculator entrypoint handover from PyQt to Tkinter**
