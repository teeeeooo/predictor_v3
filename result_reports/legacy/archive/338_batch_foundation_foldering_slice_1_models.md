# Report 338: Batch Foundation Foldering Implementation - Slice 1

## Goal (목표)

- 337 batch foundation foldering audit 결과에 따라, root의 batch model/spec 파일 2개를 `ui_tk/batch/` 패키지로 안전하게 이동하고 관련된 import 경로들을 갱신하여 패키지 구조를 고도화한다.

## 기준으로 사용한 337 Audit (Reference)

- [337_batch_foundation_foldering_audit.md](337_batch_foundation_foldering_audit.md)
  - Candidate A (ui_tk/batch/ consolidation) 구조에 기반한 Slice 1 계획을 준수하여 진행함.

## 이동한 파일 (Moved Files)

- git mv를 사용하여 root에 분산되어 있던 toolkit-neutral models/specs를 신규 `ui_tk/batch/` 패키지로 이동 완료:
  - `ui_tk/batch_models.py` -> `ui_tk/batch/models.py`
  - `ui_tk/batch_matrix_models.py` -> `ui_tk/batch/matrix_models.py`
  - `ui_tk/batch/__init__.py` (패키지 초기화 파일 생성 완료)

## Import-only 보정 대상 (Import Correction Targets)

- 다음 16개 파일의 old imports를 신규 패키지 경로(`ui_tk.batch.models`, `ui_tk.batch.matrix_models`)로 direct 일괄 보정함:
  - `ui_tk/batch_matrix_table.py`
  - `ui_tk/sections/hong_kong_cspf_batch_spec.py`
  - `ui_tk/batch_table.py`
  - `ui_tk/batch_dialogs/profiles/saso_t3.py`
  - `ui_tk/batch_dialogs/profiles/iso_iseer_2point.py`
  - `ui_tk/batch_dialogs/profiles/hong_kong_cspf.py`
  - `ui_tk/batch_controller.py`
  - `ui_tk/batch_case_table.py`
  - `tests/test_ui_tk_saso_t3_batch_dialog.py`
  - `tests/test_ui_tk_batch_matrix_models.py`
  - `tests/test_ui_tk_table_controller_per_cell_roles.py`
  - `tests/test_ui_tk_iso_iseer_2point_batch_dialog.py`
  - `tests/test_ui_tk_batch_table_controller.py`
  - `tests/test_ui_tk_hong_kong_cspf_matrix_migration.py`
  - `tests/test_ui_tk_batch_models.py`
  - `tests/test_ui_tk_batch_matrix_table.py`

## Compatibility Shim을 만들지 않은 이유

- 본 codebase의 규모가 비교적 작고 old imports를 참조하는 파일의 범위가 16개 파일 수준으로 명확히 한정되어 있었으므로, 불필요한 레거시 잔재와 복잡도를 방지하기 위해 compatibility shim을 별도로 만들지 않고 direct import 갱신을 원스텝으로 완료함.

## 제외 범위 (Excluded Scope)

- **Slice 2 파일 이동 제외**: `batch_case_table.py`, `batch_matrix_table.py`, `batch_table_viewport.py`, `batch_controller.py`, `batch_table_controller.py`, `batch_table.py` 등의 view/viewport/controller root files는 Slice 2의 대상이므로 이동하지 않음.
- **기타 소스 수정 제외**: view/viewport/controller의 레이아웃, 검증(validation), 재계산(calculation) 로직 등의 behavior 변경 없음.
- **문서 수정 제한**: `project_log.md` 및 `result_reports/memory/project_memory_seed.md` 파일은 전혀 수정하지 않음 (unchanged). `docs/code_map/CODEBASE_REFERENCE_MAP.md` regeneration은 이번 Slice 1에서 수행하지 않고 Slice 2 완료 시점에 최종 갱신할 예정임. `docs/WORK_PLAN.md`는 허용된 범위 내에서만 compact하게 업데이트됨.

## 검증 결과 (Verification Results)

- `python3 -B -m py_compile` 통과 (OK)
- `python3 -B tools/check_code_structure.py` 통과 (OK)
- `git diff --check` 상의 whitespace 문제 없음 (OK)
- **Focused pytests** (총 65개 테스트 모두 성공 통과):
  - `tests/test_ui_tk_hong_kong_cspf_matrix_migration.py` (PASSED)
  - `tests/test_ui_tk_iso_iseer_2point_batch_dialog.py` (PASSED)
  - `tests/test_ui_tk_saso_t3_batch_dialog.py` (PASSED)
  - `tests/test_ui_tk_batch_dialog_shell.py` (PASSED)
  - `tests/test_ui_tk_table_controller.py` (PASSED)
  - `tests/test_ui_tk_batch_models.py` (PASSED)
  - `tests/test_ui_tk_batch_matrix_models.py` (PASSED)
  - `tests/test_ui_tk_metric_input_table_controller_parity.py` (PASSED)

## Next Action suggested (차기 과제)
1. **Batch foundation foldering implementation - Slice 2**
