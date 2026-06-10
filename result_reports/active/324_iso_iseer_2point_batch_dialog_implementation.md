# 324 ISO / India ISEER 2-point Batch Dialog Implementation

## Goal (목표)

- `321` 및 `322` 작업에서 확정된 `BatchDialogShell` + `profiles/` 구조를 재사용하여 ISO/India ISEER 2-point batch dialog를 구현한다.
- `IsoIseer2PointSection`에 "Multi 입력" 버튼을 추가하여 신규 다이얼로그를 연결하고, snapshot 관리와 ISO/India ISEER 비교 결과 표시에 이상이 없도록 검증한다.

## Confirmed ISO 2-point Section/Result Shape (확인한 기존 ISO 2-point section/result shape)

- **Input Keys**:
  - `35_full` 시험점: `full_capacity` / `full_power`
  - `35_half` 시험점: `half_capacity` / `half_power`
- **Result Format**:
  - `ISO 16358-1` 및 `India ISEER` 두 개의 프로파일 계산 결과를 비교 표 형태로 렌더링.
  - 비교 표의 컬럼 구성: `Region/Profile`, `EER Full`, `EER Half`, `CSPF/ISEER`, `CSTL [kWh]`, `CSEC [kWh]`
  - 배치 매트릭스 결과 열도 이에 맞추어 `ISO CSPF`, `ISO CSTL`, `ISO CSEC`, `ISEER`, `ISEER CSTL`, `ISEER CSEC`를 모두 계산하여 다이얼로그 내 그리드에 출력.

## Created Files (생성 파일)

- [ui_tk/batch_dialogs/profiles/iso_iseer_2point.py](ui_tk/batch_dialogs/profiles/iso_iseer_2point.py)
- [tests/test_ui_tk_iso_iseer_2point_batch_dialog.py](tests/test_ui_tk_iso_iseer_2point_batch_dialog.py)

## Modified Files (수정 파일)

- [ui_tk/batch_dialogs/profiles/__init__.py](ui_tk/batch_dialogs/profiles/__init__.py)
- [ui_tk/sections/iso_iseer_2point_section.py](ui_tk/sections/iso_iseer_2point_section.py)
- [result_reports/active/323_remove_private_shell_access_from_batch_dialog_test.md](result_reports/active/323_remove_private_shell_access_from_batch_dialog_test.md) (Closeout Note 보정)
- [docs/WORK_PLAN.md](docs/WORK_PLAN.md)
- [project_log.md](project_log.md)
- [docs/code_map/CODEBASE_REFERENCE_MAP.md](docs/code_map/CODEBASE_REFERENCE_MAP.md)

## ISO 2-point Batch Profile Adapter Responsibility (ISO 2-point batch profile 어댑터 책임)

- `ui_tk/batch_dialogs/profiles/iso_iseer_2point.py`는 오직 아래의 프로필별 데이터 매핑/제어 책임만 가집니다:
  - `ISO_ISEER_2POINT_MATRIX_SPEC` 배치 매트릭스 스펙 구성
  - `IsoIseer2PointBatchHandler`를 통한 두 개의 코어 계산기 (`iso_t1_default_2point_cspf` 및 `india_iseer_cspf`) 호출 및 결과 위임
  - `IsoIseer2PointMatrixController` 및 `IsoIseer2PointBatchSection` 뷰 빌드
  - 다이얼로그 타이틀 및 min_size 제공
  - `snapshot()` 호출을 통한 입력 상태 추출 및 `restore_snapshot` 제어
- `BatchDialogShell`이 가지고 있는 Toplevel 윈도우 라이프사이클 관리, 좌표(geometry) 안착, 닫기 프로토콜 등 공통 책임을 침범하지 않고 복사/붙여넣기 없이 Composition 구조를 준수합니다.

## Section Integration Details (섹션 통합 내용)

- `IsoIseer2PointSection` 하단에 `action_row` 프레임을 구성하여, `Multi 입력` 버튼(`batch_button`)과 기존의 `상세 보기 ↓` 버튼(`detail_toggle`)을 나란히 배치.
- 버튼 클릭 시 `IsoIseer2PointBatchDialog`를 열고, 이미 열려 있는 상태인 경우 `focus()`를 실행해 포커스를 앞당김.
- 다이얼로그 닫기 시 `on_close` 콜백을 통해 다이얼로그의 snapshot 데이터를 `_batch_snapshot`에 임시 보존하며, 재오픈 시 어댑터 초기 생성자에 주입하여 복구하는 상태 보존(persistence) 라이프사이클을 완결.
- section 소스가 batch dialog의 내부 detail(`_shell` or `_adapter`)에 직접 접근하지 않고, public wrapper API인 `snapshot()`, `close()`, `focus()`, `window`만을 사용함.

## Shell/Profile Boundary Compliance (경계 준수 여부)

- `ui_tk/batch_dialogs/shell.py` 및 `ui_tk/batch_dialogs/profiles/hong_kong_cspf.py`를 전혀 수정하지 않았습니다.
- Toplevel 관련 중복 코드가 profile 어댑터 파일에 작성되지 않았습니다.

## Snapshot Behavior Verdict (스냅샷 동작 판단)

- 홍콩 CSPF와 마찬가지로, 다이얼로그를 닫아 위젯이 파괴되어도 사용자 입력 데이터는 섹션의 `self._batch_snapshot` 메모리에 온전히 보존되며 재오픈 시 복구되도록 설계 및 검증 완료.

## Verification & Test Results (검증 결과)

- `python3 -B -m py_compile`을 통해 수정한 모든 파일의 구문 오류 없음 확인.
- `tests/test_ui_tk_iso_iseer_2point_batch_dialog.py` 신설하여 아래 4개 focused test 케이스 검증 및 `PASSED`:
  - `test_iso_iseer_2point_batch_dialog_opens_and_closes` (Multi 입력 호출 및 close 시 snapshot 저장 확인)
  - `test_iso_iseer_2point_batch_dialog_preserves_snapshot_on_reopen` (스냅샷 복원 확인)
  - `test_iso_iseer_2point_batch_handler_calculates_valid_cases` (ISO 및 India ISEER 병렬 계산기 호출과 예외 처리 상태 검증)
  - `test_iso_iseer_2point_batch_spec_properties` (스펙 속성 검증)
- `tests/test_ui_tk_batch_dialog_shell.py`, `tests/test_ui_tk_hong_kong_cspf_matrix_migration.py` 검증 모두 정상 완료.
- `python3 -B tools/check_code_structure.py` structural check 통과 완료.

## CODEBASE_REFERENCE_MAP Regeneration Result (레퍼런스 맵 재생성 결과)

- 신규 생성된 `ui_tk/batch_dialogs/profiles/iso_iseer_2point.py`가 코드 맵에 정상 등록되었으며, `FRESH` 상태를 만족함.

## Excluded Areas (제외 범위)

- SASO T3 batch dialog의 구현은 작업 범위 외로 엄격히 제외되었습니다.
- root의 `ui_tk/batch_*.py` 폴더 이동은 작업 범위 외로 엄격히 제외되었습니다.
- calculator/core 및 ML predictor, golden fixture 등의 변경은 발생하지 않았습니다.

## Manual GUI Smoke Status (수동 GUI 스모크 검증 상태)

- **완료**: 사용자 수동 GUI 확인 결과 이상 없음이 확인되었습니다.
- **운영 원칙**: 앞으로 Codex 프롬프트에는 사용자 수동 GUI 확인 세부 항목을 포함하지 않으며, 사용자가 별도 확인 후 결과만 closeout에 반영하는 운영 방식을 적용합니다.

## Next Actions (향후 작업)

1. **SASO T3 batch dialog implementation** (matrix-based optional 35 Min toggle rendering)
2. **Batch foundation foldering audit**
3. **Batch foundation foldering implementation**
4. **Calculator entrypoint handover from PyQt to Tkinter**
5. **ui_tk root folder inventory audit**
6. **EN14825 / AHRI 210/240 / KS profile expansion**

## Active Report Count Status (액티브 리포트 수 상태)

- active report count meets lifecycle threshold criteria.
