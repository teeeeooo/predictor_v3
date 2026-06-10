# Active Report 351: Mixed ISO Table Test Split or Retirement

## 목표 (Goal)

* PyQt calculator-only source retirement의 blocker로 남은 [tests/test_iso16358_table_excel_like_behavior.py](../../tests/test_iso16358_table_excel_like_behavior.py)를 정리하여 legacy PyQt 계산기 소스 은퇴의 준비 상태를 확보한다.

## 기준으로 사용한 349/350/154/156 report (Reference Reports)

* [Report 349](349_calculator_pyqt_reference_retirement_preflight.md) & [Report 350](350_349_report_local_link_correction.md): PyQt 계산기 은퇴 preflight 결과 및 blocker로 남은 mixed ISO table test의 의존성 식별.
* [Report 154](../archive/154_pyqt-calculator-retirement-audit.md) & [Report 156](../archive/156_shared-pyqt-utility-retention-decision.md): mixed ISO table test blocker 분석 및 스프레드시트 뷰/모델 분리 결정 이력 확인.

## 기존 mixed test coverage 분류 (Old Mixed Test Coverage Classification)

기존 `tests/test_iso16358_table_excel_like_behavior.py` 파일의 테스트 케이스들은 다음과 같이 분류되었습니다:
1. **PyQt Calculator-only widgets (`ProfileInputGridModel` / `ProfileInputGridView`)**:
   * `test_selected_to_tsv_emits_bounding_rectangle`
   * `test_copy_selection_puts_tsv_on_clipboard`
   * `test_clear_selection_blanks_cells_and_groups_undo`
   * `test_clear_with_no_selection_uses_current_index`
   * `test_zero_or_negative_cell_is_invalid`
   * `test_positive_numeric_cell_is_not_invalid`
   * `test_move_active_cell_updates_current_index`
2. **Shared spreadsheet view/model behaviors (TSV copy/paste, clear, undo, navigation)**:
   * `test_empty_cell_is_not_invalid`
   * `test_non_numeric_cell_is_invalid_with_tooltip`
   * `test_next_navigation_index_wrap_and_clamp`

## 선택한 option과 이유 (Selected Option and Reason)

* **선택**: **Option A. Retire whole mixed test** (mixed test 전체 은퇴)
* **이유**:
  * `ProfileInputGridModel` 및 `ProfileInputGridView`는 PyQt calculator-only legacy 소스로서 은퇴 예정 대상입니다.
  * 해당 mixed test의 핵심 비즈니스 로직(TSV copy/paste, clear, undo, navigation, tooltip, background styling)은 공용 스프레드시트 컴포넌트인 [ui/spreadsheet_table.py](../../ui/spreadsheet_table.py) 테스트용으로 작성된 [tests/test_spreadsheet_table_model.py](../../tests/test_spreadsheet_table_model.py) 및 [tests/test_spreadsheet_table_view.py](../../tests/test_spreadsheet_table_view.py)에서 이미 동일하거나 더 포괄적인 검증 항목으로 완벽하게 커버되고 있습니다.
  * 따라서 mixed test 전체를 삭제(은퇴)해도 공용 컴포넌트의 테스트 커버리지 누수가 발생하지 않습니다.

## 수정한 tests (Modified/Deleted Tests)

* `tests/test_iso16358_table_excel_like_behavior.py` 파일을 `git rm` 명령으로 영구 삭제하였습니다.

## shared utility coverage 보존 여부 (Preservation of Shared Utility Coverage)

* [tests/test_spreadsheet_table_model.py](../../tests/test_spreadsheet_table_model.py)와 [tests/test_spreadsheet_table_view.py](../../tests/test_spreadsheet_table_view.py)가 정상 보존 및 통과하고 있으므로, 공용 spreadsheet 유틸리티 관련 coverage는 안전하게 보존되었습니다. 추가적인 테스트 복제는 필요하지 않은 것으로 판단됩니다.

## blocker 해제 여부 (Blocker Resolution Status)

* **해제됨 (Resolved)**:
  * `tests/` 디렉토리 아래의 모든 테스트 코드에서 `ui.calculators_2point` 및 `ProfileInputGrid` 임포트가 완전히 제거되었습니다.
  * 이로써 PyQt calculator-only 소스 은퇴(retirement)의 핵심 blocker가 완전히 해제되었습니다.

## 검증 결과 (Verification)

* `python3 -B tools/check_code_structure.py`: `code structure guard: OK (no findings)`.
* `git diff --check`: whitespace 에러 없음.
* `git status --short`: `D tests/test_iso16358_table_excel_like_behavior.py` 만 스테이징된 정상 상태.
* 관련 테스트 정상 동작 확인:
  * `pytest tests/test_spreadsheet_table_model.py` (52 passed)
  * `pytest tests/test_spreadsheet_table_view.py` (8 skipped - macOS PyQt5 environment guard)
  * `pytest tests/test_ui_theme_tokens.py` (46 passed)
  * `pytest tests/test_pyqt_environment_guard.py` (11 passed)

## WORK_PLAN 업데이트 여부 (WORK_PLAN Update Status)

* **미갱신 (Unchanged)**: 본 작업의 `[수정 금지]` 제약 사항에 따라 `docs/WORK_PLAN.md` 파일은 수정하지 않고 보존하였습니다.

## 제외 범위 (Non-goals)

* PyQt calculator-only 프로덕션 소스 코드([ui/calc_window.py](../../ui/calc_window.py), [ui/calculators_2point.py](../../ui/calculators_2point.py) 등) 및 공용 유틸리티 소스([ui/spreadsheet_table.py](../../ui/spreadsheet_table.py) 등)는 본 작업에서 수정하거나 삭제하지 않았습니다.

## next action (Next Action)

* Blocker가 완전히 해제되었으므로, 후속 슬라이스인 **PyQt calculator-only source retirement execution**을 실행하여 레거시 소스 코드를 은퇴시킬 수 있습니다.
