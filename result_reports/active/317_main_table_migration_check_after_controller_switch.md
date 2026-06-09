# 317 Main Table Migration Check After Controller Switch Arc Closeout

## Goal

- 기존 `262_main-table-migration-candidate-check.md` 분석 결과를 바탕으로, 최신 controller switch 아크 종결(313) 상태를 대조하여 메인 테이블 마이그레이션 타당성을 최종 재검토하고 후속 ui_tk cleanup 방향을 확정한다.

## Scope

- `MetricInputTable`, `ExcelLikeTableController`, `TkTableSurface`, `TkTableController`, `interaction_core` 의 최신 책임 소재 감사.
- MVC/SoC(관심사 분리) 관점의 view, controller, model/validation boundary 확인.
- `262` preflight 대비 마이그레이션 가능성 재평가 및 결론 도출.
- 후속 `ui_tk folder cleanup` 및 legacy controller 퇴출을 위한 next implementation slice 제안.
- docs/WORK_PLAN.md 및 Report 315의 wording mismatch compact 보정.

## Non-Goals

- Python source (.py) 수정 금지.
- ui_tk, calculator/core, ML/predictor 로직 변경 금지.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md` 재생성 금지.
- result report archive 폴더 이동 금지.

## Task Results

### 1. 최신 controller switch 상태 대조 (Task 1)
- `262` preflight 작성 당시에는 4개 main section에서 `ExcelLikeTableController`를 사용하고 있었으나, 이후 순차적 마이그레이션을 통해 `HongKongCspfSection`, `HongKongHspfSection`, `IsoIseer2PointSection`, `IsoSasoT3Section`의 모든 메인 테이블 컨트롤러가 `TkTableController`로 스위치 완료(313에서 closeout)되었음.
- 따라서 `262`에서 우려했던 마이그레이션의 regression 리스크(paste, selection, navigation 등)는 실제 final closeout GUI smoke를 통해 안정적으로 종결 및 극복된 상태임.

### 2. 현재 main table 관련 owner 및 MVC/SoC (Task 2)
- **MetricInputTable**: UI grid 빌드 및 Entry 바인딩 등의 View presentation 책임을 가지며, 동시에 `TkTableSurface` 프로토콜을 구현하기 위한 position-based adapter 메서드들(`row_count`, `column_count`, `cell_role`, `text_at_position`, `set_positions_batch`, `snapshot`, `restore_snapshot`, `cell_frame`, `cell_widget` 등)을 동일 파일에 내장하여 어댑터 책임을 겸함.
- **ExcelLikeTableController**: 4개 main section에서 모두 `TkTableController`로 전환됨에 따라 프로덕션 main table path에서는 완전히 retired되어 더 이상 사용되지 않는 상태임. 다만 `tests/test_ui_tk_iso_table_autocalc.py`와 같은 legacy 테스트 코드의 단언문에 잔재가 존재함.
- **TkTableController**: 현재 모든 4개 main section 테이블의 copy/paste, clear, undo, navigation, selection painting 상태를 표준 `TkTableSurface` 계약 하에 공통 제어함.
- **Validation / Invalid Marking Boundary**:
  - `parse_numeric_cell` (in `ui_tk/table_grid_model.py`)이 numeric parsing의 단일 원천임.
  - `MetricInputTable`이 `_invalid_fields`를 통해 셀/필드 단위의 invalid visual state를 격리 소유하고 있음.
  - `recalculate_now` 연산 도중 `get_numeric_values()`가 예외를 유발하면, `MetricInputTable`이 invalid visual marking을 업데이트하고 calculator section이 에러 상태 표시 및 연산 실행을 block함.
  - `TkTableController`는 값의 타당성을 직접 알지 못하며, 오직 `EDITABLE` 셀에 대해서만 clipboard 데이터를 바인딩하여 surface로 흘려보내므로 관심사 분리가 유지됨.

### 3. 마이그레이션 가능성 최종 판단 (Task 3)
- **결론: C. migration 보류, ui_tk cleanup 먼저 수행**
- **근거**: 4개 main section의 `TkTableController` 전환(migration)은 이미 종결되어 정상 작동하고 있음. 따라서 추가적인 마이그레이션 작업은 불필요(보류)하며, 최우선 후속 과제는 프로덕션에서 retired된 legacy `ExcelLikeTableController`와 이에 결합된 legacy unit test gaps를 제거하는 `ui_tk folder cleanup`을 수행하는 것임.

### 4. 다음 implementation slice 제안 (Task 4)
- **작업명**: ui_tk folder cleanup (Retiring ExcelLikeTableController and correcting test gaps)
- **목적**: 프로덕션 코드에서 완전히 retired된 `ExcelLikeTableController`를 삭제하고, `tests/test_ui_tk_iso_table_autocalc.py` 등의 legacy 단언문을 `TkTableController` 검증으로 수정하여 테스트 갭을 해소함.
- **수정 허용 후보**:
  - `ui_tk/excel_like_table_controller.py` (완전 삭제)
  - `tests/test_ui_tk_excel_like_table_controller.py` (완전 삭제)
  - `tests/test_ui_tk_iso_table_autocalc.py` (단언문 교정)
- **수정 금지 후보**: `ui_tk/metric_input_table.py`, `ui_tk/table/controller.py`, calculator/core 및 ML predictor 코드 전체.
- **검증 후보**: `python3 -B tools/check_code_structure.py`, `pytest tests/test_ui_tk_iso_table_autocalc.py`.
- **User GUI smoke 필요 여부**: 불필요 (비주얼 변경 없는 dead code/test cleanup이므로).

## Verification

- `docs/WORK_PLAN.md` 315 설명이 cleanup 활동으로 정확히 정정되었음을 확인.
- `result_reports/active/315_active_report_lifecycle_cleanup_after_controller_switch.md` 의 16개/16개 파일 표기가 archive 개수 19개에 대응하여 neutral wording으로 보정되었음을 확인.
- `python3 -B tools/check_code_structure.py` 를 통한 structure guardrail 위배 여부 없음 확인.
- `git diff --check` 상의 whitespace 오류 없음 확인.
- exact active report count 대신 threshold wording 정책 준수 확인.

## Changed Files

- `docs/WORK_PLAN.md`: 315 summary/lifecycle cleanup 설명 수정 및 task 317/Next Actions 업데이트.
- `project_log.md`: task 317 엔트리 추가.
- `result_reports/active/315_active_report_lifecycle_cleanup_after_controller_switch.md`: count mismatch 보정.
- `result_reports/active/317_main_table_migration_check_after_controller_switch.md`: 본 리포트 생성.

## Known Failures / Risks

- `test_ui_tk_iso_table_autocalc.py`에 남아 있는 legacy 단언문은 local pytest 실행 시 assert fail을 유발할 수 있는 잠재 리스크(test gap)이므로, 차후 ui_tk folder cleanup slice에서 즉시 보정되어야 함.

## Next Suggested Action

1. **ui_tk folder cleanup** (ExcelLikeTableController 삭제 및 test gap correction)

## Scope Compliance

- Python source 및 ui_tk 코드 비즈니스 로직에 전혀 손대지 않고, docs wording correction 및 preflight audit 리포트 작업만 수행하였으므로 contract boundary를 완벽히 준수함.

## Commit / Push

- **Commit Message**: `docs: Check main table migration readiness`
- **Push Result**: Pushed successfully.

## Project Memory Delta

- `type`: decision
  `topic`: Main table migration check and ExcelLikeTableController retiring
  `content`: 4개 main section에 대한 TkTableController 마이그레이션이 최종 완료 및 검증되었으므로 메인 테이블 마이그레이션은 완료 종결로 보류함. 후속 Next Action으로 legacy ExcelLikeTableController 및 관련 unit test gaps를 정리하는 ui_tk folder cleanup을 최우선 수행함.
  `keywords`:
    - main table migration
    - ExcelLikeTableController
    - ui_tk cleanup
  `assertionStatus`: verified
  `source`: result_reports/active/317_main_table_migration_check_after_controller_switch.md
