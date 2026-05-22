# 093 Spreadsheet Table UX Polish

## Goal
- `SpreadsheetTableModel`에 invalid numeric cell visual indicator (Qt
  `BackgroundRole` + `ToolTipRole`)를 추가한다.
- `SpreadsheetTableView`에 Tab / Shift+Tab / Enter / Shift+Enter
  navigation을 추가한다 (`docs/ui/SPREADSHEET_TABLE_CONTRACT.md` §10
  기준).
- 기존 copy / paste / clear / undo / AHRI·EN UI smoke를 깨지 않는다.

## Scope
- 수정 대상: `ui/spreadsheet_table.py`,
  `tests/test_spreadsheet_table_model.py`,
  `tests/test_spreadsheet_table_view.py`, `docs/WORK_PLAN.md`, 본 report.
- 수정 금지: `core/calculator_en14825.py`, `core/calculator_iso16358.py`,
  AHRI/EN/ISO expected, calculator/unit adapter, `app_calculator.py`,
  ISO16358 UI.

## Non-goals
- 별도 `QStyledItemDelegate` 페인트 구현 (data-role 기반 최소 표시만).
- ISO16358 UI 마이그레이션 / contract alignment audit.
- Unit adapter 확장, ML / inverse-search 복귀.
- ISO16358-2 HSPF mismatch 후속 (외부 분석 대기 hold 유지).

## Verification
| command | result |
| --- | --- |
| `python3 -B -m py_compile ui/spreadsheet_table.py tests/test_spreadsheet_table_model.py tests/test_spreadsheet_table_view.py tests/test_app_calculator_ui_smoke.py` | passed |
| `python3 -B -m pytest tests/test_spreadsheet_table_model.py -q` | passed (model 테스트 일괄) |
| `python3 -B -m pytest tests/test_spreadsheet_table_view.py -q` | passed (view 테스트 일괄) |
| `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q` | passed |
| `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q` | passed |
| `python3 -B -m pytest -q` | 464 passed, 34 xfailed (ISO16358-2 HSPF mismatch는 hold 유지) |

## Task 1 — invalid numeric cell visual indicator
- 수정 파일: `ui/spreadsheet_table.py`,
  `tests/test_spreadsheet_table_model.py`.
- 구현 방식: `SpreadsheetTableModel.data()`에서
  `Qt.BackgroundRole`과 `Qt.ToolTipRole`을 지원한다.
  `is_cell_invalid(row, col) is True`인 셀에 한해
  `QBrush(QColor(*INVALID_CELL_BACKGROUND_RGB))` (pale red,
  `(255, 224, 224)`) 와 `INVALID_CELL_TOOLTIP` ("Invalid numeric value")
  을 반환한다. delegate 신설 없이 model data-role만으로 처리하므로
  `QTableWidget` / `setCellWidget` 도입 없이 `QTableView` 기본 paint
  경로가 그대로 색을 입힌다.
- 빈 셀 vs non-numeric 셀 구분: `is_cell_invalid()`는 `value == ""`이면
  `False`를 반환하고 (required validation은 계산 시점 책임), 그 외에
  `coerce_numeric(value) is None`인 경우만 `True`를 반환한다. 따라서
  빈 셀은 background/tooltip override 대상이 아니다.
- 미지원 UX: 셀 테두리 색상, 단위/range 분기 별 메시지 분리, 풍부한
  delegate paint 효과는 이 slice 범위 밖. invalid 표시는 `BackgroundRole
  + ToolTipRole` 최소 표면으로 한정한다.

## Task 2 — Tab / Enter navigation
- 수정 파일: `ui/spreadsheet_table.py`,
  `tests/test_spreadsheet_table_view.py`.
- 이동 규칙:
  - `Tab` → 오른쪽 셀. 같은 행 끝이면 다음 행 0열로 wrap.
  - `Shift+Tab` (Qt에서는 `Key_Backtab`) → 왼쪽 셀. 같은 행 0열이면
    이전 행의 마지막 열로 wrap.
  - `Enter` / `Return` → 아래 셀. 같은 열 끝이면 다음 열의 0행으로
    wrap.
  - `Shift+Enter` / `Shift+Return` → 위 셀. 같은 열 0행이면 이전 열의
    마지막 행으로 wrap.
- Boundary 처리: 더 이상 이동할 곳이 없으면 (Tab from bottom-right,
  Shift+Tab from top-left 등) 현재 셀을 그대로 유지한다 (helper에서
  `(row, col)` 그대로 반환).
- 분리된 helper: 순수 함수 `SpreadsheetTableView.next_navigation_index(
  row, col, direction)`을 노출해 key path 없이도 navigation 규칙을
  단위 테스트 가능하게 했다. `keyPressEvent`는 helper를 호출한 뒤
  `selectionModel().setCurrentIndex(..., ClearAndSelect)`로 view state를
  갱신한다.
- 기존 동작 보존: `Ctrl+C` / `Ctrl+V` / `Ctrl+Z` / `Delete` /
  `Backspace`는 그대로이며, view 테스트의
  `test_copy_selection_tsv_returns_selected_rectangle` /
  `test_paste_tsv_at_selection_writes_from_top_left_anchor` /
  `test_clear_selection_and_undo_last_restore_previous_grid` /
  `test_undo_last_reverts_paste_group` /
  `test_delete_key_clears_selection_without_clipboard_dependency`가 모두
  통과한다.

## Task 3 — 테스트 보호
- 추가 테스트:
  - `test_spreadsheet_table_model.py`:
    `test_invalid_cell_exposes_background_and_tooltip_roles` — invalid
    cell (`abc`), valid cell (`12.5`), 빈 cell (`""`) 세 가지에 대해
    `BackgroundRole`이 expected RGB의 `QBrush`를 반환하는지,
    `ToolTipRole`이 `INVALID_CELL_TOOLTIP`을 반환하는지, valid/empty
    셀은 둘 다 `None`을 반환하는지 확인.
  - `test_spreadsheet_table_view.py`:
    - `test_navigation_helper_moves_right_down_with_wrap` — 2×3 grid의
      right/left/down/up 이동과 행/열 끝 wrap 동작을 helper로 검증.
    - `test_navigation_helper_clamps_at_table_corners` — bottom-right
      corner에서 `right`/`down`이 셀을 유지하고, top-left corner에서
      `left`/`up`이 셀을 유지함을 확인.
    - `test_tab_and_enter_keys_update_current_index` — 실제 `QTest`
      keyClick (`Tab`, `Return`, `Backtab+Shift`, `Return+Shift`)으로
      `currentIndex`가 helper와 일치하게 갱신되는지 확인.
- PyQt5 optional skip: 두 테스트 모듈 모두 기존 `pytest.importorskip
  ("PyQt5")`와 `QT_QPA_PLATFORM=offscreen` 패턴을 유지한다.
- AHRI/EN smoke: `tests/test_app_calculator_ui_smoke.py` 22개 케이스
  전부 그대로 통과. 전체 suite는 464 passed / 34 xfailed
  (ISO16358-2 HSPF mismatch hold).

## Task 4 — 문서 / report
- `docs/WORK_PLAN.md` 의 "Near-term execution order" 3항을
  업데이트해 invalid-cell visual indicator / navigation slice가 완료
  되었음을 명시하고, 다음 sequence를
  1. ISO16358 table contract alignment audit
  2. unit adapter 확장 (ISO / KS / EN profile)
  3. ML / inverse-search 복귀 준비
  로 정렬했다. ISO16358-2 HSPF mismatch는 외부 분석 대기 hold 유지.
- 본 report (093) 작성.

## 남은 위험 / 후속 작업
- Invalid-cell 표시는 `BackgroundRole + ToolTipRole`만 사용한다.
  delegate 기반 border / focus highlight가 필요해지면 별도 slice.
- ISO16358 UI (CSPF/HSPF) 는 아직 `QFormLayout` 기반이며 contract
  alignment audit이 다음 작업으로 남아 있다.
- Navigation은 spreadsheet 컨트랙트 §10의 wrap-around를 따른다.
  계산 화면 다른 위젯과의 focus 이동이 필요해지면 (예: Esc로 form
  영역으로 빠지기) 후속 slice에서 정의한다.
