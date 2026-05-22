# 094 ISO16358 Table Contract Alignment Audit

## Goal
- ISO16358 (CSPF 2-point / Hong Kong / SASO T3) UI 입력 테이블이
  `docs/ui/SPREADSHEET_TABLE_CONTRACT.md`와 어긋난 곳을 점검한다.
- AHRI / EN14825에서 사용 중인 공통 component (`SpreadsheetTableModel`
  / `SpreadsheetTableView`)을 ISO 입력에 재사용할 수 있는지 판정한다.
- 코드 변경은 하지 않는다 (audit only). 후속 slice 후보만 분리한다.

## Scope
- 점검 대상: `ui/calc_window.py` (ISO tab wiring), `ui/calculators_2point.py`
  (`IsoCspfSingleWidget`, `ProfileInputGridModel`, `ProfileInputGridView`,
  `ProfileInputGridDelegate`, 결과 표 `TwoPointTableModel` /
  `TraceTableModel` / `RegionResultTableModel`).
- 비교 대상: `docs/ui/SPREADSHEET_TABLE_CONTRACT.md`, `ui/spreadsheet_table.py`.

## Non-goals
- 실제 코드 수정. AHRI/EN/ISO 계산 로직 / fixture / xfail 수정.
- ISO16358-2 HSPF mismatch 후속 (외부 분석 대기 hold 유지).
- ISO calculator core (`core/calculator_iso16358.py`) 수정.

## Verification
- 코드 변경 없음. 본 audit은 read-only 점검. 후속 slice 제안만 포함.

## Task 1 — ISO16358 UI table 구조 조사
- ISO tab은 `ui/calc_window.py:130-136`에서 `IsoCspfSingleWidget`
  하나만 호스트한다. ISO16358-2 HSPF 전용 UI 위젯은 현재 없다 (HSPF는
  AHRI HSPF2 v3 tab만 존재).
- `IsoCspfSingleWidget` (`ui/calculators_2point.py:1020`) 는
  3개 profile (ISO/ISEER 2-point, Hong Kong CSPF, SASO T3) 을 하나의
  `ProfileInputGridView` 위에서 swap한다.
  - View: `ProfileInputGridView(QTableView)` (1182~1189에서 install).
  - Model: `ProfileInputGridModel(QAbstractTableModel)` (604~760).
  - Delegate: `ProfileInputGridDelegate(QStyledItemDelegate)` (763~781).
  → contract §4 "QTableView + QAbstractTableModel + QStyledItemDelegate"
  패턴은 **준수**. `QTableWidget` / `setCellWidget` 잔존 없음 (전체
  `ui/`에서 `grep` 결과 0건).
- 결과/요약 표는 모두 read-only `QTableView` + `QAbstractTableModel`:
  - `TwoPointTableModel` (64~349), `TwoPointTableView` (351~365).
  - `TraceTableModel` (14~62), `RegionResultTableModel` (869~914).
  - `BatchTwoPointDialog`의 `RegionDetailTab.table` (944) 도 `QTableView`.
  → contract §2의 read-only display 범위에서는 layout/selection만 만족
  하면 OK이며, 추가 요구사항 (Copy TSV) 은 다음 항목에서 별도로 정리.
- 입력 단위는 W (행 헤더 "Capacity [W]" / "Power [W]") 로 EN14825의
  W → kW 변환 패턴과 동질. ISO16358 core는 W를 그대로 받아도 동작
  (factor 무관) 하므로 별도 unit adapter 변환 단계가 들어있지 않음.

## Task 2 — SPREADSHEET_TABLE_CONTRACT 대비 gap
다음은 `ProfileInputGridModel` / `ProfileInputGridView` 와 contract의
차이점을 항목별로 분리한 결과다.

### copy (Ctrl+C)
- 현재: 구현 없음. `keyPressEvent` (829~848) 는 Paste / Undo / Enter만
  처리하고 Copy는 default로 떨어져 아무 일도 일어나지 않는다 (rich-text
  paste 호환이 없는 상태).
- contract §3 / §7: TSV copy가 필수. `SpreadsheetTableView.
  copy_selection_tsv()` 와 `SpreadsheetTableModel.selected_to_tsv()` 는
  이미 공통 component에서 제공.
- gap: **있음**. 표 → Excel TSV 복사가 안 된다.

### paste (Ctrl+V)
- 현재: `ProfileInputGridModel.paste_tsv()` (681~712) 구현. 동작은 거의
  contract §7과 같으나 다음 차이 존재.
  - 셀 값은 `value.strip()`으로 trim. 공통 `SpreadsheetTableModel.
    paste_tsv` 는 원본 문자열을 그대로 저장.
  - 트림 결과 빈 문자열인 경우 그대로 빈 문자열을 쓰지만, `parse_tsv`
    호환의 trailing `\n` 제거는 `strip("\n").split("\n")` 으로 직접
    처리한다 (CRLF 정규화 없음).
  - "non-TSV payload 거부" 룰 (§7) 은 모델 단에서 강제하지 않는다 —
    tab이 없는 입력이면 단일 열에 쓰여진다 (Excel과 비슷한 관용 동작).
- gap: **경미**. CRLF 정규화 / 공통 `parse_tsv` 사용으로 동작 일치
  가능. 기능적으로는 작동.

### clear (Delete / Backspace)
- 현재: **구현 없음**. `keyPressEvent`는 Delete/Backspace를 처리하지
  않는다. 사용자가 Delete를 누르면 Qt default로 셀이 비워지지도 않고
  edit mode에 들어가지도 않는다.
- contract §3 / §8: Delete / Backspace는 selection 전체를 비우고 단일
  undo group 으로 묶어야 한다.
- gap: **있음**. ISO 표는 multi-cell clear가 불가능.

### undo (Ctrl+Z)
- 현재: 자체 stack 운용. `_undo_stack` 에 `(row, col, old_value)`
  튜플 리스트를 push (setData 단건 / paste bulk 모두 같은 entry 형식).
  `undo()` 는 entry를 pop 해서 셀 값을 복원한다 (반대 방향 redo 없음).
- contract §9: "edit / paste / clear 1회당 single undo group" + redo는
  선택. 현재 구현은 edit / paste를 group으로 묶긴 하지만 clear path가
  없으므로 clear undo는 의미 없음. snapshot-기반 공통 component
  (`SpreadsheetTableModel._push_snapshot()` 64-depth) 와는 internal 표현이
  다름.
- gap: **경미**. 기능은 contract 범위를 만족하지만 다른 표(AHRI/EN)와
  내부 표현이 다르므로 공통 component로 옮기면 일관화 가능.

### invalid numeric 표시
- 현재: 모델 `data(..., BackgroundRole)` 는 `QColor("#FFFFFF")` 를
  무조건 반환 (642~643). 입력 검증은 `_parse_cell()`에서 비숫자 /
  ≤0 을 `None`으로 처리해 `parsed_points()`가 dict 자체를 `None`으로
  반환 → 결과 영역에 "입력값 부족"이라 표시될 뿐, **invalid 셀의
  시각적 표시는 없다**.
- contract §3 / §11: invalid 셀은 시각적으로 구분되어야 한다.
- gap: **있음**. 093에서 공통 `SpreadsheetTableModel`에 추가한
  `BackgroundRole` (pale red) + `ToolTipRole` 인디케이터가 여기엔
  없다.
- 추가 차이: ISO 표는 "양수 numeric"이 invalid 기준 (`_parse_cell`
  `number > 0`). 공통 `is_cell_invalid()`는 numeric parsable 여부만
  본다 (0 / 음수는 invalid 표시 대상이 아님). ISO 의미를 그대로
  유지하려면 column-spec 단위 validator를 모델/delegate 위에 얹어야
  한다.

### Tab / Enter navigation
- 현재:
  - Tab: `setTabKeyNavigation(True)` (793) 로 Qt default 동작 — 같은
    행 끝에서 다음 행으로 wrap (Qt 기본). Shift+Tab은 Qt default로
    역방향. 이는 contract §10 ("Tab → 오른쪽 wrap-around") 와 거의
    같지만 명시 보장은 없음.
  - Enter: `keyPressEvent` (845~847) 와 delegate `eventFilter`
    (775~781) 에서 모두 `move_to_next_cell()` 를 호출한다.
  - `move_to_next_cell()` (850~866) 는 **오른쪽** 으로 이동하고, 열
    끝이면 다음 행 0열로 wrap. 마지막 셀이면 그 자리에 머문다.
  - Shift+Enter ↑ 이동은 **없음**.
- contract §10: Enter는 "한 행 아래로 이동, 열 끝 wrap" 이어야 하며
  Shift+Enter 는 위로. 현재 ISO 표의 Enter는 사실상 Tab과 같은
  방향이라 contract와 어긋난다.
- gap: **있음** (Enter 방향, Shift+Enter 부재).

### to_point_dict / validation path
- ISO 표는 `parsed_points(required_keys=None)` 로
  `{point_key: {"capacity": float, "power": float}}` 를 반환한다 —
  ISO calculator (`calculate_cspf(measured)`) 가 기대하는 dict-of-dict
  구조다.
- 공통 `SpreadsheetTableModel.as_point_dict()` 는
  `{point_key: (capacity, power)}` tuple-shape를 반환한다 (AHRI /
  EN core 입력 형식).
- gap: **있음 (모양 차이)**. 공통 component를 ISO에서 재사용하려면
  ISO 어댑터에서 `as_point_dict()` → `{key: {"capacity":..,"power":..}}`
  변환을 한 줄 추가해야 한다 (core 또는 calculator unit adapter 쪽으로
  변환을 옮기는 것이 안전).

### unit label / row-column 구조
- 공통: 2-row × N-col 구조, row label "Capacity [W]" / "Power [W]"
  (AHRI: Btu/h / W, EN: W / W). ISO는 W / W. → `SpreadsheetTableModel(
  row_labels=["Capacity [W]", "Power [W]"], column_labels=[...])` 로
  표현 가능.
- 차이: ISO는 column labels 가 profile에 따라 동적으로 바뀐다 (2-point /
  Hong Kong / SASO 3-point / SASO 4-point). 공통 `SpreadsheetTableModel`
  은 생성자에서 column labels 를 받지만 **runtime swap을 위한
  set_columns API 가 없다** (현재는 새 model을 만들어 view에 다시
  set 해야 한다). 후속 slice에서 helper 추가가 필요.

### blockSignals discipline
- ISO model은 `blockSignals` 자체를 사용하지 않고 `_bulk_updating`
  플래그로 emit 억제만 한다. contract §12는 `blockSignals`를 쓸 때
  `try/finally`로 감싸라는 요구이므로 위배는 없다. 다만 paste path에서
  `try/finally`로 플래그를 복원하는 패턴 (687, 706 try/finally) 은 동질.

### 종합
- ISO 표는 contract §4 (View/Model/Delegate 패턴) 와 §2 (table widget
  금지) 는 만족.
- 결손은 (1) Copy 미구현, (2) Delete/Backspace 미구현, (3) invalid 셀
  시각화 미구현, (4) Enter 방향/Shift+Enter 부재.
- 변경 시 가장 큰 결정 포인트는 "공통 `SpreadsheetTableModel` 로
  마이그레이션할지" 또는 "ISO 모델에 그대로 missing 기능을 옮길지" 이다.
  핵심 ISO 정책 (positive numeric 강제, dict-of-dict point 변환,
  profile별 column swap, custom delegate alignment / Enter→다음 셀
  edit 모드 자동 진입) 이 공통 component에 없는 항목이므로 즉시
  swap은 위험.

## Task 3 — 수정 가능한 low-risk 항목
다음은 한 slice에서 ~수십 줄 이내로 끝나고 ISO 계산 경로를 건드리지
않는 후보만 골랐다. 모두 별도 slice로 분리 권장.

### Low-risk #1 — Delete / Backspace clear
- 위치: `ProfileInputGridModel`에 `clear_cells(selection)` 추가,
  `ProfileInputGridView.keyPressEvent`에서 Delete/Backspace 처리.
- 영향: 입력값을 비우는 동작만. `_recalculate` 가 자동 호출되어
  결과는 "입력값 부족" 으로 떨어진다.
- 위험: 낮음. parsing path에 새 입력값을 강제하지 않는다.

### Low-risk #2 — Copy TSV
- 위치: `ProfileInputGridView.keyPressEvent`에서 Ctrl+C → 모델
  `selected_to_tsv` 호출. 모델에 `selected_to_tsv()` helper 추가
  (공통 `format_tsv` 재사용).
- 영향: 클립보드에만 출력. 입력값 불변.
- 위험: 낮음.

### Low-risk #3 — Invalid numeric 시각 표시
- 위치: `ProfileInputGridModel.data(..., BackgroundRole)` 에서
  invalid (비숫자 또는 ≤0) 인 경우 `INVALID_CELL_BACKGROUND_RGB`
  반환. `ToolTipRole`도 같이 노출.
- 영향: 현재 invalid시 결과만 빈칸이지만 셀 표시로 사용자에게 더
  빠른 피드백.
- 위험: 낮음. 단, ISO 의 invalid 정의 (양수 강제) 와 AHRI/EN 의
  invalid 정의 (numeric parseable) 가 다르므로 ISO 전용 helper로
  먼저 추가하고 공통화는 별도 slice.

### Low-risk #4 — Enter / Shift+Enter 방향 정정
- 위치: `ProfileInputGridView.move_to_next_cell()` 분기를 명시화하고
  `move_to_prev_cell()` 또는 helper `next_navigation_index(row, col,
  direction)` 추가. `eventFilter` / `keyPressEvent` 에서 Shift+Enter
  를 위로, Enter는 contract §10대로 "아래로" 이동.
- 영향: 현재 사용자가 Enter로 오른쪽 방향 input을 기대했을 수 있음
  → UX 변경. 변경 전에 사용자 승인 필요.
- 위험: 중간 (사용자 습관 영향). delegate edit mode 자동 진입 로직과
  같이 봐야 함.

### Medium-risk / 별도 slice 권장 — 공통 component 이주
- `ProfileInputGridModel` → `SpreadsheetTableModel` 기반으로 재구성.
  필요한 신규 helper: (a) runtime column swap (`set_columns(labels)`),
  (b) dict-of-dict point adapter, (c) positive-numeric validator
  훅 (cell-level invalid 기준 inject).
- 영향: ISO/Hong Kong/SASO 3개 profile 모두 한 번에 변경. paste/copy/
  clear/undo/navigation/invalid 표시가 일관 동작.
- 위험: 중간. profile swap 동작과 delegate alignment / edit-on-enter
  동작이 ISO UX 특성이라 단순 swap만으로는 회귀 가능. 별도 design
  gate 필요.

### Read-only result table 보강 — Copy TSV (Optional)
- `TwoPointTableModel` / `TraceTableModel` / `RegionResultTableModel` /
  `RegionDetailTab.table` 에 Copy TSV 동작이 없다. contract §2는
  read-only 표에도 copy를 요구한다. ISO 입력 표와 동시에 슬라이스화
  가능.
- 위험: 낮음. 결과 변경 없음. 다만 `RegionResultTableModel`은
  format된 표시 문자열 (예: `f"CSPF: {...:.2f}"`) 을 그대로 copy
  하므로 사용자가 "raw 값" 을 원할 경우 별도 옵션 필요.

## Task 4 — 다음 구현 slice 제안 (분리)
다음 순서를 권장한다. 각 항목은 별도 commit / report.

1. **095 — ISO input table: Delete/Backspace + Copy TSV**
   - 가장 안전한 두 가지를 한 번에. clear + copy 만 추가.
   - 모델 helper, view keyPressEvent 추가. invalid 정의 변경 없음.
   - 테스트: `tests/test_calculators_2point.py` 가 있으면 거기에,
     없으면 신규 모듈에서 PyQt importorskip + offscreen.

2. **096 — ISO input table: invalid numeric 시각 표시**
   - `ProfileInputGridModel.data(BackgroundRole)`에 invalid (비숫자
     또는 ≤0) 셀 표시 추가. ToolTip 포함.
   - 공통 `INVALID_CELL_BACKGROUND_RGB` 상수를 그대로 재사용.
   - "양수 강제" 의미와 "numeric parseable" 의미 차이를 doc string에
     명시.

3. **097 — ISO input table: Enter/Shift+Enter 정정**
   - contract §10 에 맞춰 Enter는 아래로, Shift+Enter는 위로 이동.
   - 사용자 UX 변경이므로 design gate / 사용자 확인 후 진행.

4. **098 (선택) — Result tables: Copy TSV**
   - 결과 표 (`TwoPointTableModel`, `RegionResultTableModel`,
     `TraceTableModel`, `RegionDetailTab.table`) 에 Copy 추가.
   - 표시 문자열 vs raw 값 정책은 별도 결정.

5. **099 (medium-risk) — 공통 component 이주**
   - `SpreadsheetTableModel`에 `set_columns()` 와 dict-of-dict point
     adapter 를 추가하고, `ProfileInputGridModel`을 `SpreadsheetTableModel`
     기반으로 재작성. ISO 전용 UX (delegate edit-on-enter, profile swap)
     는 view layer 에서 유지.
   - 별도 design gate 필요.

6. **위 1~5 이후** unit adapter (ISO/KS/EN profile) 확장과 ML /
   inverse-search 복귀로 이동.

ISO16358-2 HSPF UI는 현재 별도 위젯이 없으며 (AHRI HSPF2 v3 표만 존재),
ISO16358-2 HSPF mismatch는 외부 분석 대기 hold 상태 그대로 둔다. 본
audit은 ISO16358-1 CSPF 입력 UI 만 다룬다.

## 남은 위험
- ISO 입력 표에는 invalid 셀 시각 표시 / clear / copy 가 없어 사용자
  실수 시 피드백이 약하다 (현재는 "입력값 부족" 상태 라인만 표시).
- Enter 방향이 contract와 다르다 — Enter를 오른쪽 이동으로 익숙해진
  사용자는 변경 시 혼동 가능 (slice 097 전 사용자 확인 권장).
- ISO profile swap (2-point / Hong Kong / SASO 3/4 point) 은 model
  자체를 새로 만들어 swap하는 구조라 공통 component 직접 이주 시
  set_columns API가 선행 필요.
