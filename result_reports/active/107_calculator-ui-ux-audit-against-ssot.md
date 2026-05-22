# 107 — Calculator UI/UX Audit Against New SSOT

## Goal

새 UI/UX SSOT (`docs/ui_ux/`) 기준으로 현재 calculator UI 구현을 audit
하고, 다음 구현 slice를 위험도/영향 범위에 따라 안전하게 나누는 audit-
only 작업. UI 코드, 계산 로직, unit adapter, ML 코드 변경 없음.

## Scope

- task 1: SSOT 문서에서 calculator UI 에 적용되는 기준 추출
- task 2: 현재 calculator UI surface inventory (코드 inspection only)
- task 3: SSOT 대비 gap classification
- task 4: 다음 작업 slice 4~6 개 제안 + 추천 next action
- task 5: 본 report 작성, WORK_PLAN 갱신 여부 판단

## Non-goals

- UI/code 수정
- calculator logic / profile / dispatcher 수정
- unit adapter 수정
- ML / inverse-search 작업
- 구현 prompt 작성
- result report lifecycle maintenance

## Verification

- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q` → 3 passed
- `python3 -B -m pytest -q` → 430 passed, 6 skipped, 23 xfailed
- 코드 변경 없음 → diff 는 본 report + (필요 시) WORK_PLAN 한 줄 갱신.

## Task Results

### task 1 — SSOT 기준 요약

확인한 문서:

- `docs/ui_ux/00_UI_UX_SYSTEM.md`
- `docs/ui_ux/01_TOOLKIT_SELECTION_POLICY.md`
- `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
- `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md`
- `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`
- `docs/WORK_PLAN.md`

Calculator UI 에 적용되는 기준만 추리면 다음과 같음:

- **Toolkit**: 새 desktop UI 중 editable / spreadsheet-heavy 화면이면
  PyQt5 default (01 §1, §2). predictor_v3 calculator 는 이미 PyQt5
  단일 toolkit 이므로 toolkit-change design gate 없음. Toolkit mix
  금지.
- **Core UX**: 1초 이상 작업은 progress + completion 명시, internal
  identifier (e.g. `case_id`, `delta`)는 UI 에 노출 금지, smallest
  sufficient layout, 단일 input 을 full-width 로 늘리지 말 것
  (00 §2, §7, §10).
- **Buttons / actions**: 버튼은 클릭 가능하게 보이고, 클릭 불가능한
  것은 버튼처럼 보이게 만들지 말 것. primary / secondary / destructive
  visual 차이, 비활성 상태 시각화 (00 §4, 02 §4). 라벨은 결과를
  서술하는 동사 ("Run analysis").
- **Dialogs / feedback**: progress dialog 는 작업 전에 paint, 실패 시
  닫히고 에러 사용자 언어로 (00 §5, §6). raw stack trace 노출 금지.
- **Forms**: numeric 입력은 사용자가 실제로 타이핑하는 포맷 (콤마,
  소수점) 수용 후 commit 시 정규화. 단일 fixed input 을 행 전체로
  늘리지 말 것 (00 §7, 02 §7).
- **Numeric display**: compact / consistent formatter, integer 는
  소수점 없음, trailing zeros strip, units 는 header / label 에 (00 §8).
- **Design tokens (02)**: `color.bg.app|card|header|cell.readonly|
  cell.invalid`, `color.text.primary|secondary|disabled`, `color.
  accent|success|warning|danger`. typography token (`font.window_
  title|card_title|section_label|body|table.header|table.cell|caption`).
  spacing token (`space.outer|card|section|row|button|cell`).
  각 프로젝트는 token name 을 자기 theme module 에서 hex 로 bind
  하면 됨 — token 이름이 contract.
- **Card layout (02 §5)**: 카드 한 개는 한 가지 concern, padding =
  `space.card`, section gap = `space.section`, 카드 중첩 1 단계까지.
- **Dynamic sizing (02 §7)**: 단일 input 을 full-width 로 늘리지
  않는다. 다중 fixed input 은 compact grid 또는 wrap. initial-value
  table 은 2~7 point 가 한 화면에 보이도록 우선. root window 에
  horizontal scroll 금지 (스크롤은 table 내부에서만).
- **Spreadsheet table UX (03)**: selection / typing replace / Esc
  cancel / Enter commit / Ctrl+C TSV copy / Ctrl+V TSV paste / Delete
  · Backspace clear / Ctrl+Z undo / Tab · Shift+Tab · Enter ·
  Shift+Enter navigation / 다섯 cell state (editable / read-only /
  disabled / invalid / empty) 모두 시각 구분 / keyboard-only workflow
  필수.
- **PyQt adapter (adapters/PYQT_TABLE_IMPLEMENTATION.md)**: `QTableView`
  + `QAbstractTableModel` + `QStyledItemDelegate`. `QTableWidget` /
  `setCellWidget` 금지. 1-click editor open = `QTimer.singleShot(0,
  editor.showPopup)`. edit / paste / cascade path 분리. DisplayRole /
  EditRole / UserRole 분리. validation 은 model/delegate 에서, painter
  는 표시만. `blockSignals` 는 `try/finally`. test 는 `QT_QPA_PLATFORM=
  offscreen`.
- **Calculator-specific design doc**: AHRI / EN / 미래 ISO migration
  table 은 글로벌 contract 를 상속받고 calculator-specific table shape
  (column / row / unit label / profile-bound column set) + unit boundary
  (ML W ↔ calculator-native) 만 정의.

문서 우선순위 / 충돌:

- 정면 충돌 없음. 계층은 다음과 같이 명확함:
  1. `00_UI_UX_SYSTEM.md` (toolkit-agnostic principles, 최상위)
  2. `01_TOOLKIT_SELECTION_POLICY.md` (toolkit 선택)
  3. `02_DESIGN_TOKENS_AND_LAYOUT.md` (visual token / layout)
  4. `03_SPREADSHEET_TABLE_UX_CONTRACT.md` (table UX)
  5. `adapters/PYQT_TABLE_IMPLEMENTATION.md` (PyQt 구현 rule)
  6. `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`
     (calculator-specific table shape / unit boundary)
- `00` 는 명시적으로 "wins when it conflicts with any single project's
  local UI notes" 라고 선언.
- adapter 와 design doc 은 상위 contract 의 implementation / scope-
  restricted 형태이며, 다시 정의하지 않고 참조함 → 충돌 없음.
- `auto-calculate` vs `explicit action` 은 어느 문서에서도 명시 강제
  하지 않음. 00 §4 에서 "button labels are verbs that describe the
  result" / 00 §3 "reduce required clicks for the primary task" 정도가
  관련 기준이며, mixed UX 자체를 명시 금지하지는 않지만 "smallest
  sufficient layout / consistent across screens" 원칙상 calculator
  내부의 두 패턴 혼재는 alignment 대상으로 간주해야 함.

### task 2 — Calculator UI surface inventory

대상 파일 (rg 로 필요한 범위만 확인, 전체는 읽지 않음):

- `app_calculator.py` (12 lines, entrypoint)
- `ui/calc_window.py` (`CalculatorWindow`)
- `ui/calculators_2point.py` (ISO/India/HK/SASO single widget + 공용
  table / read-only helper)
- `ui/spreadsheet_table.py` (`SpreadsheetTableView`,
  `SpreadsheetTableModel`, factory 함수 4개)
- `tests/test_app_calculator_ui_smoke.py`,
  `tests/test_iso16358_table_excel_like_behavior.py`,
  `tests/test_iso16358_result_table_copy_tsv.py`,
  `tests/test_spreadsheet_table_model.py`,
  `tests/test_spreadsheet_table_view.py`

#### CalculatorWindow shell

- `QTabWidget` 3 tabs: ISO 16358 / EN 14825 / AHRI 210/240.
- Window 하단에 단일 `계산 실행` `QPushButton` + `result_label`
  (`QLabel`, word-wrap, text-selectable). raw 한 영역에 결과 텍스트만
  표시.
- error 표시는 inline border + background 직접 stylesheet
  (`#E74C3C` / `#FDEDEC`) + `QMessageBox.warning` / `critical`.
- internal "result_label" 라벨이 internal id 가 아니라 "결과 대기" 한
  국어 라벨이므로 00 §9 위반 없음.

#### ISO 16358 tab

- `IsoCspfSingleWidget` (`ui/calculators_2point.py` line 1263+).
- top panel: profile combo (`ISO / ISEER 2점식` / `Hong Kong CSPF` /
  `SASO T3`) + `Multi 입력` button.
- input panel: `ProfileInputGridModel` + `ProfileInputGridView` (line
  680 / 907 / 941). 2 point 또는 SASO 의 3/4 point.
  - SASO 는 추가 checkbox (`35°C Minimum 사용`).
  - Hong Kong 은 추가 `declared_capacity` (W) `QLineEdit`.
- result panel: `RegionResultTableModel` + `ReadOnlyCopyTableView`
  (line 1112 / 72). 상태 label (`계산 대기` / 실시간 갱신).
- detail panel: toggle, `QTabWidget` 안에 `RegionDetailTab` 각 region.
  - region 별 trace / two-point table (read-only) + bin-graph
    (`BinGraphWidget`), `TraceDetailPanel`.
- **interaction**: **auto-calc**. `_recalculate` 가 `input_model.
  values_changed` 와 `declared_capacity.textChanged` / `chk_saso_min.
  toggled` 에 직접 연결. profile switch 도 `_apply_profile` 가
  `_recalculate` 를 호출. 사용자에게 명시적 `계산 실행` 버튼 없음 —
  window 의 상단 `계산 실행` 버튼이 이 tab 에서는 no-op (line 692
  `calculate_iso()` 가 "2점식 ISO/ISEER 탭은 실시간 계산이므로 수동
  계산 버튼 동작 안 함" 주석으로 명시).
- 사용된 widget set: `QFrame` panel + inline stylesheet (cards 흉내).
- inline stylesheet 의 hex 값이 token-bound 아님: `#F6F7F9`,
  `#FFFFFF`, `#DCE1E7`, `#C8D0DA`, `#EEF1F4`, `#8A94A3`, `#2F6F9F`,
  `#285F88`, `#F8FAFC`, `#E1E6EE`, `#526071`, `#2F455C` 등.

#### EN 14825 tab

- top: `규격 프로파일` `QComboBox`.
- `en_seer_group` (`QGroupBox`): single SEER table
  (`make_en14825_seer_table_model`) + `SpreadsheetTableView`. 그 아래
  `QFormLayout` 에 `p_design_c_w` `QLineEdit`. SEER profile 일 때만
  visible.
- `en_scop_group` (`QGroupBox`): for each climate in
  `{average, warmer, colder}` →  `QGroupBox`(`setCheckable(True)`)
  카드 안에 SCOP table (`make_en14825_scop_table_model`) + 4 개
  보조 `QLineEdit` (`p_design_h_w`, `tbiv_w`, `tol_w`, 그리고 prefill
  된 Tbiv/TOL 기본값). SCOP profile 일 때 visible. climate checkbox
  로 선택 (`average` default).
- 공통 standby `QGroupBox`: `p_to_w`, `p_sb_w`, `p_ck_w`, `p_off_w`
  4 개 `QLineEdit` (W, default 0.0). **하단** 배치.
- 단위 통합: UI 입력 모두 W → `calculate_en()` 호출 직전 W → kW
  변환.
- **interaction**: **explicit calculate**. window 의 `계산 실행`
  버튼 → `on_calculate` → `calculate_en()`. table 변경 자체로 결과
  갱신 없음.

#### AHRI 210/240 tab

- top: `시스템 타입` (HP/AC `QRadioButton`), `규격 프로파일`
  `QComboBox`.
- `QScrollArea` 안에:
  - SEER2 cooling group: `make_ahri_seer2_table_model` +
    `SpreadsheetTableView` (5 col × 2 row).
  - SEER2 extra params (`Cd_low`, `Cd_full`) `QFormLayout`.
  - HSPF2 v3 heating group: `make_ahri_hspf2_table_model` +
    `SpreadsheetTableView` (7 col × 2 row) + 보조 form (`t_off`,
    `t_on`, `defrost_t_test_minutes`, `defrost_t_max_minutes`).
- **interaction**: **explicit calculate**. `계산 실행` → `calculate_
  ahri()` → SEER2 결과 + HP 일 때 HSPF2 v3 결과를 `result_label` 에
  단일 string 으로 표시.
- HSPF2 input 의 A2 는 SEER2 table 의 `A_Full` 열에서 읽음 (즉,
  SEER2 와 HSPF2 table 간 cross-read 가 명시).

#### Result / error / status surface 공통

- `CalculatorWindow.result_label`: 단일 `QLabel`. 줄바꿈 word-wrap,
  text-selectable. EN/AHRI 결과 string 전부 이 한 줄 label 에. 카드
  / banner / progress 없음.
- error: `QMessageBox.warning` (input validation) / `QMessageBox.
  critical` (기타 exception). `InputValidationError.widget` 이 있으면
  해당 widget 에 red border + selectAll + focus. stack trace 는 노출
  되지 않음 (`str(e)` 만).
- progress: 없음. 계산은 즉시 실행되므로 progress dialog 미사용.
  ISO tab 의 debounce 가 _recalculate_pending 으로 자동 갱신.
- ISO tab 의 result panel 은 별도 `status` `QLabel` ("계산 대기" /
  결과 텍스트). 즉 ISO tab 은 result panel 자체 보유, AHRI/EN 은
  window-level result label 만 사용.

#### Hong Kong HSPF UI surface

- **없음.** WORK_PLAN 에 명시된 대로 core/config/test + profile/
  dispatcher smoke 만 완료 (`core/calculator_profiles.py` 에
  `hong_kong_hspf` 등록, `hong_kong_cspf` 와 동일 region config 공유,
  `metric=HSPF` / `mode=heating`). `CalculatorWindow` / `IsoCspfSingle
  Widget` 어느 곳에도 HSPF 진입점 없음.
- 현재 ISO tab 의 profile combo 에는 `ISO / ISEER 2점식` /
  `Hong Kong CSPF` / `SASO T3` 만 있음 — HSPF 항목 없음.

#### Test coverage 현황

- `tests/test_spreadsheet_table_model.py`,
  `tests/test_spreadsheet_table_view.py` — 공통 `SpreadsheetTable
  Model` / View 의 TSV copy / paste / clear / undo / navigation /
  invalid-mark.
- `tests/test_iso16358_table_excel_like_behavior.py` — ISO 입력
  grid (`ProfileInputGridModel` / View) Excel-like behavior.
- `tests/test_iso16358_result_table_copy_tsv.py` — ISO result /
  read-only table TSV copy.
- `tests/test_app_calculator_ui_smoke.py` — calc_window offscreen
  smoke. AHRI SEER2 / HSPF2 horizontal table 존재 / point dict mapping /
  EN SEER & SCOP multi-climate / EN W→kW 변환 / HP 모드 SEER2 +
  HSPF2 동시 표시 / SCOP 결과 / standby smoke / HSPF2 required input
  validation.
- 보호되지 않는 범위:
  - ISO tab 자동 계산 트리거 / debounce — `IsoCspfSingleWidget._
    recalculate` 자체에 smoke 없음 (정확한 결과는 calculator core 측
    golden 으로 보호).
  - result/status label rendering, error styling 분기, message box
    경로.
  - Hong Kong HSPF UI (surface 부재).
  - design token / theme — theme module 자체가 없음.
  - stylesheet 의 inline hex 값 일관성.

### task 3 — Gap classification

각 gap = (affected / 현재 / SSOT / user impact / 위험도 / 즉시 vs 별도
설계).

1. **Table contract gap** — 거의 충족.
   - affected: `ui/spreadsheet_table.py` (`SpreadsheetTableModel` /
     View), `ui/calculators_2point.py` (`ProfileInputGridModel` /
     View, `ReadOnlyCopyTableView`, `TwoPointTableModel`,
     `RegionResultTableModel`, `TraceTableModel`).
   - 현재: 03 + adapter 의 핵심 항목 (Ctrl+C TSV / Ctrl+V TSV /
     Delete clear / Ctrl+Z undo / Tab · Enter navigation / invalid
     mark / read-only copy) 모두 두 model family 에 구현 + smoke
     test 로 보호.
   - SSOT: 03 §2~§10, adapter §1~§11.
   - user impact: keyboard-only workflow 가능, Excel paste 호환.
   - 위험도: 낮음 (이미 정렬됨). 미세한 항목: 03 §3 "double click /
     F2 / explicit edit affordance" 의 F2 는 명시 구현 여부 미확인
     (Qt 의 기본 동작 의존). 03 §10 "keyboard-only workflow" 모두
     이미 가능.
   - 즉시 vs 별도 설계: alignment 추가 작업은 거의 없음. 별도
     micro-audit 만 필요.

2. **Layout / card structure gap** — 부분 충족.
   - affected: `ui/calc_window.py` (AHRI / EN tab 전체 layout),
     `ui/calculators_2point.py` (`IsoCspfSingleWidget._init_ui`).
   - 현재:
     - ISO tab 은 이미 card-like panel (`QFrame#panel` inline QSS) +
       result panel + detail panel 구조.
     - EN tab 은 vertical `QVBoxLayout` 에 GroupBox 카드 3개 (SEER,
       SCOP, standby) + climate 별 카드 중첩 (GroupBox in GroupBox).
       카드 중첩 1단계까지 (`scop_group → climate card`) 로 02 §5
       위반은 아님. standby 카드는 가장 아래.
     - AHRI tab 은 `QScrollArea` 내부 GroupBox (SEER2 cooling,
       SEER2 extra params, HSPF2 heating + auxiliary).
   - SSOT: 00 §10 "single fixed input must not stretch full width",
     02 §5 card, 02 §7 dynamic sizing, 02 §3 spacing token.
   - user impact: EN standby 가 화면 가장 아래라 매번 스크롤 (특히
     SCOP 3 climate 모두 켜면 카드 길이 증가). single-input row 가
     full-width (예: `p_design_c (W, SEER)` 한 줄에 한 입력만).
   - 위험도: 중간. layout 만 손대도 calculate path 영향 없음, 다만
     spacing/token 도입 전에 layout 만 옮기면 inline hex 가 그대로
     남음.
   - 즉시 vs 별도: token 도입 (gap 3) 와 분리 가능. polish-only
     slice 로 가능. **layout polish ≠ core/unit adapter** — 절대
     섞지 않음.

3. **Design token / theme gap** — 부재.
   - affected: 전 calculator UI. 명시적 theme module 없음.
   - 현재: `IsoCspfSingleWidget._init_ui` 한 곳에 큰 inline QSS,
     `calc_window` 의 error border 도 inline hex, `BinGraphWidget`,
     `TraceDetailPanel`, `RegionResultTableModel` 등 곳곳 inline
     hex.
   - SSOT: 02 §1~§4 color / typography / spacing token, 02 §5 card,
     02 §9 "Token names are the contract until a project commits a
     palette".
   - user impact: 색 일관성 떨어짐 (error 한 곳 `#E74C3C`, ISO panel
     border `#DCE1E7`, table grid `#E1E6EE` 등 비슷한 회색 여러 톤),
     향후 dark mode / accessibility 어려움.
   - 위험도: 중간. theme module 자체 도입은 코드 변경이지만 calc
     path 영향 없음. 다만 token 이름만 도입하고 hex bind 는 보수적
     으로 유지하면 risk 낮음.
   - 즉시 vs 별도: **theme token foundation** 은 독립 slice.
     layout polish 보다 먼저 깔리면 자연스럽지만 필수 선행은 아님
     (mock token 으로 polish 후 token 도입도 가능). 별도 작업 권장.

4. **Interaction / action model gap** — mixed pattern.
   - affected: `ui/calc_window.py` (AHRI/EN explicit `계산 실행`),
     `ui/calculators_2point.py` (ISO auto-calc).
   - 현재: ISO tab = auto-calc on input change (debounce + values_
     changed). AHRI/EN tab = window 하단 `계산 실행` 버튼만 인식.
     `계산 실행` 버튼은 ISO tab 에선 no-op (주석 명시).
   - SSOT: 00 §3 "reduce required clicks for primary task" + 00 §4
     "button labels are verbs that describe the result". 어느 쪽
     모델도 명시 금지 아님. 단, "smallest sufficient layout / no
     button that does nothing" (10 §1) 와의 정렬 필요 — ISO tab
     에서 `계산 실행` 이 disabled 가 아니라 클릭 가능하지만 ISO
     tab 에서 실제로 아무것도 안 함.
   - user impact: 사용자가 ISO tab 에서 "계산 실행" 눌러도 변화 없음
     (실시간 갱신이라 사용자가 의식 못 할 수 있지만, 00 §10
     "Buttons that look like buttons but do nothing" 위반 가능).
     AHRI/EN 에서 입력만 바꾸고 계산을 잊을 가능성. 결과 위치도
     ISO 는 panel 내부, AHRI/EN 은 window 하단 label — 일관성 부족.
   - 위험도: 중간. 결정은 두 가지 — (A) 모든 tab 을 auto-calc 로
     통일하고 `계산 실행` 버튼 제거, (B) 모든 tab 을 explicit 으로
     통일하고 ISO 자동 갱신 제거 + tab 별 result panel 일관화. ISO
     tab 의 auto-calc 는 이미 user-facing 가치가 큼 (2점식 입력
     실시간 비교). (A) 추천. 결정 자체는 설계 판단 필요.
   - 즉시 vs 별도: **auto-calculate behavior alignment** 는 layout
     polish 와 섞지 않음. 별도 slice.

5. **Result / error / progress feedback gap** — 부분 충족.
   - affected: `CalculatorWindow.result_label`, error path,
     `InputValidationError` styling.
   - 현재: AHRI / EN 결과는 단일 string 한 줄, ISO 는 result panel
     + status label. progress dialog 없음 (계산 즉시 끝남).
     error 는 `QMessageBox` + inline red border (raw hex). stack
     trace 비노출 OK.
   - SSOT: 00 §5/§6 progress + completion, 02 §8 empty state + error
     색은 `color.danger`. inline hex 는 token 부재로 비정렬.
   - user impact: AHRI 결과를 한 줄로 표시 → "AHRI SEER2 (HP) 결과:
     X / HSPF2 v3 결과: Y" 같이 두 metric 을 한 string 으로 합쳐
     UX 가 약함. EN SCOP multi-climate 결과도 한 줄에 합쳐짐 (smoke
     test `test_en_calculate_button_displays_multi_climate_scop_
     result_text` 참고).
   - 위험도: 중간. result 영역 카드화 + 라벨 분리 = layout polish 의
     일부로 처리 가능. 또는 별도 result feedback slice.
   - 즉시 vs 별도: layout polish slice 의 하위 task 로 묶거나, EN
     polish slice 안에서 함께 처리. core 영향 없음.

6. **Missing surface gap** — Hong Kong HSPF UI 부재.
   - affected: ISO tab `IsoCspfSingleWidget` profile combo, profile
     dispatcher.
   - 현재: profile / config / test + dispatcher smoke 모두 완료
     상태 (WORK_PLAN 24 line). UI 진입점 없음.
   - SSOT: surface 없음 자체가 SSOT 위반은 아님. 단 추가 시 03 +
     adapter + 02 (card / token) + design doc (HSPF heating point
     shape) 모두 따라야 함.
   - user impact: UI 에서 Hong Kong HSPF 계산 불가 (core 만 가능).
   - 위험도: 중간. HSPF heating point shape 은 새 column set 이라
     설계 필요 — design doc 의 HSPF section 또는 추가 design slice.
     layout polish 와 절대 섞지 않음.
   - 즉시 vs 별도: **independent slice**. 별도 design + 구현.

7. **Test coverage gap** — 부분 충족.
   - affected: `IsoCspfSingleWidget._recalculate` 직접 smoke 부재,
     auto-calc trigger smoke 부재, error message box 경로 smoke
     부재, HK HSPF UI 부재 (테스트도 없음).
   - 위험도: 낮음 (core / calculator 측 golden 으로 결과는 보호됨).
     UI 폴리시 slice 와 함께 보강 권장.

### task 4 — Next implementation slice candidates

각 slice 는 위험도 / 영향 범위 기준으로 분리. 절대 섞지 않을 항목 명시.

#### Slice A — Calculator UI design token / theme foundation
- 작업명: Calculator UI design token foundation
- 목적: 02 의 color / typography / spacing token 을 calculator UI 가
  실제로 참조 가능한 `ui/theme.py` (또는 동등) module 로 도입. 현재
  scatter 된 inline hex 를 token 으로 점진적으로 옮길 수 있게 함.
- 수정 대상 후보:
  - 신규 `ui/theme.py` (token name → 현재 hex 매핑, palette commit).
  - calc_window error border, IsoCspfSingleWidget QSS 의 일부 색을
    token 참조로 교체 (선택적, 최소 PoC level).
- 포함 범위:
  - token name 정의 (02 의 token 그대로 차용).
  - token 별 현재 hex commit (기존 inline 값을 그대로 캡쳐, 색 변경
    하지 않음).
  - 1~2 개 inline 색 (error border, panel background) 만 token 참조
    PoC.
- 제외 범위:
  - 모든 inline QSS 의 일괄 token 교체 (다음 polish slice).
  - 색 자체 변경, dark mode, accessibility tuning.
  - layout 변경.
- 선행 조건: 없음.
- 검증 방법: full pytest smoke + offscreen launch smoke (이미 보호
  됨). token module 자체 unit test (`test_ui_theme_tokens.py` 신규)
  로 token 이름 / hex 형식 정렬 확인.

#### Slice B — EN14825 layout polish
- 작업명: EN14825 tab layout polish
- 목적: EN tab 의 standby 와 single-input 행을 02 layout 규칙에
  맞게 정리. SCOP climate 카드의 시각 단계를 명확히 함.
- 수정 대상 후보: `ui/calc_window.py::init_en_tab`.
- 포함 범위:
  - standby form 을 SEER/SCOP 카드 위쪽 또는 옆 compact grid 로
    재배치 (단일 input full-width 회피).
  - `p_design_c_w` 같은 single-input row 의 width 제한 (02 §7).
  - climate 카드의 checkable header 가 button-like 로 보이는지 점검,
    필요한 경우 03 §8 "cell states" 식 시각 구분.
  - SCOP card 들 spacing token 정렬 (현재 inline 0).
- 제외 범위:
  - core EN calculator 수정, W/kW 변환 변경, calc 결과 텍스트 포맷
    변경, auto-calc 전환, theme token 도입 자체 (Slice A 와 분리),
    standby 값 의미 변경.
- 선행 조건: Slice A 가 끝나면 token 참조로 작성 가능. 안 끝나도
  가능하지만 다음 token slice 에서 일괄 교체가 필요해짐.
- 검증 방법: `tests/test_app_calculator_ui_smoke.py` 의 EN 관련 smoke
  통과 유지. 필요 시 standby form 위치 smoke 추가.

#### Slice C — Calculator auto-calculate behavior alignment
- 작업명: Calculator action model alignment (auto-calc vs explicit)
- 목적: ISO tab 의 auto-calc 와 AHRI/EN 의 explicit `계산 실행`
  사이 mixed pattern 을 일관화. 00 §10 의 "버튼이 클릭 가능하지만
  아무것도 안 함" 위반 해소.
- 수정 대상 후보: `ui/calc_window.py` (action layout + on_calculate),
  `ui/calculators_2point.py` (auto-calc trigger 정리).
- 포함 범위 (옵션 A — 전체 auto-calc 통일, 추천):
  - AHRI/EN tab 도 입력 변경 시 (debounce) 자동 결과 갱신.
  - `계산 실행` 버튼 제거 또는 "Recalculate now" 정도의 명시 secondary
    action 으로 축소. result 영역을 각 tab 내부 panel 로 이동
    (window-level result_label 제거 또는 status banner 로 변경).
  - input validation error 는 inline (per-field) + status banner 로
    노출. `QMessageBox` 는 destructive / unexpected error 만 사용.
- 포함 범위 (옵션 B — explicit 통일):
  - ISO tab 의 auto-calc 제거. `_recalculate` 호출을 button click 으
    로 한정.
  - 모든 tab 에 동일 result panel 배치.
- 제외 범위:
  - layout polish (Slice B), token (Slice A), HK HSPF UI (Slice D),
    core calc / unit adapter / ML 작업.
- 선행 조건: 옵션 결정 (A vs B). 본 audit 의 추천은 A (사용자 입력
  비용 ↓, ISO tab UX 유지). 결정 자체는 별도 micro-design 1 page 로
  마무리 가능.
- 검증 방법: `tests/test_app_calculator_ui_smoke.py` 의 explicit
  button 의존 test 가 옵션 A 일 때 갱신 필요 (단, 본 audit 에서
  test 수정은 다음 slice 의 일부로 둔다). 옵션 B 일 때 ISO debounce
  smoke 가 새로 필요.

#### Slice D — Hong Kong HSPF UI surface (design + first slice)
- 작업명: Hong Kong HSPF UI surface
- 목적: 이미 core / dispatcher 가 준비된 Hong Kong HSPF 를 UI 에서
  실행 가능하게 함.
- 수정 대상 후보:
  - 신규 design doc (`docs/designs/YYYY-MM-DD-hong-kong-hspf-ui.md`)
    또는 기존 `docs/designs/2026-05-17-calculator-horizontal-table-
    input-ui.md` 에 HSPF section 추가.
  - `ui/calculators_2point.py::IsoCspfSingleWidget` profile combo
    에 `Hong Kong HSPF` 항목 추가, HSPF 입력 grid + heating point
    column set, result/detail panel 의 HSPF 처리.
  - 또는 별도 위젯/tab 으로 분리할지는 design 단계에서 결정.
- 포함 범위:
  - design 단계: heating point column set, two-row 능력/전력 형태,
    auxiliary form (defrost / standby 등 HK 규격에 맞춰), unit 단위.
  - 1차 구현 slice: input grid + 결과 display (single result panel).
- 제외 범위:
  - layout polish (Slice B), token foundation (Slice A) 의 일괄 교체,
    auto-calc 통일 (Slice C), unit adapter 확장 (별도).
- 선행 조건: Slice C 의 결정 (auto-calc vs explicit) 이 먼저 끝나면
  HK HSPF 도 그 모델을 따라 일관성 유지. 결정 전이라도 기존 ISO tab
  의 auto-calc 모델 (현행) 을 그대로 답습 가능.
- 검증 방법: 신규 smoke `tests/test_calculator_hong_kong_hspf_ui.py`
  (offscreen) — profile 선택 시 grid 출현, point dict 매핑, profile
  dispatcher 와 결과 reachable.

#### Slice E — Unit adapter 확장: ISO / KS / EN profile (non-UI)
- 작업명: Unit adapter expansion — ISO / KS / EN
- 목적: 기존 AHRI SEER2 전용인 `core/calculator_unit_adapter.py` 를
  ISO / KS / EN profile 로 확장. ML W ↔ calculator-native 단위 경계
  확립.
- 수정 대상 후보: `core/calculator_unit_adapter.py`, 관련 envelope
  smoke / unit test.
- 포함 범위:
  - profile 별 ml_prediction → calculator-native dict 변환.
  - profile 별 result envelope → ranking candidate 단위 보존.
- 제외 범위:
  - UI 작업 일체, calculator core 공식식 수정, ML 모델 자체 수정,
    profile/dispatcher 신규 등록.
- 선행 조건: 없음. **UI audit 작업과 완전 분리**. 본 audit 가
  blocker 아님.
- 검증 방법: `tests/test_calculator_envelope_chain.py` 확장 + 새
  profile 단위 conversion smoke.

#### Slice F — ML / inverse-search 복귀 준비 (non-UI)
- 작업명: ML / inverse-search restart
- 목적: WORK_PLAN 의 long-term next step. unit adapter 확장 (Slice
  E) 후 ML 입력 envelope 통합과 inverse-search 진입점 정비.
- 수정 대상 후보: `core/predictor.py`, ML/inverse 모듈, 관련 smoke.
- 포함 범위 / 제외 범위 / 선행 조건 / 검증: 별도 design slice 에서
  정의. 본 audit scope 외.
- 본 audit 에서는 단지 sequence 상의 위치만 확인 (가장 뒤).

#### 추천 next action

**Slice A — Calculator UI design token foundation 1개.**

근거:
- gap 3 (design token) 이 layout polish (B) 와 result feedback / EN
  polish 양쪽의 선행 inflection 점.
- A 는 inline hex 를 그대로 commit 만 하면 되므로 시각 변화 없음 →
  사용자 영향 0, 회귀 위험 최소.
- C (auto-calc alignment) 는 옵션 결정 (A vs B) 이 필요해 별도
  micro-design 이 필요. A → B → C 순서가 안전.
- D 와 E 는 서로 독립이라 A 이후 어느 쪽 먼저 가도 됨.

### task 5 — report + WORK_PLAN

- 본 report 를 `result_reports/active/107_calculator-ui-ux-audit-
  against-ssot.md` 로 작성.
- WORK_PLAN 갱신: audit 결과가 다음 sequence 후보를 4~6 개로 확장
  하므로, 항목 3 의 sequence 를 audit 의 slice 후보와 일치시키기 위해
  짧게 갱신.
- result report lifecycle maintenance 는 본 작업 범위가 아님. active
  report 가 lifecycle gate trigger 부근까지 누적 — Known Risks 에
  pending 으로만 남김.

## Test Results

- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q`
  → 3 passed in 0.16s
- `python3 -B -m pytest -q`
  → 430 passed, 6 skipped, 23 xfailed in 2.72s

## Changed Files

- A `result_reports/active/107_calculator-ui-ux-audit-against-ssot.md`
- M `docs/WORK_PLAN.md` (sequence 짧게 갱신)

## Known Failures / Risks

- result report lifecycle maintenance pending — `result_reports/
  active/` 누적이 trigger 부근. 본 audit scope 외라 별도 lifecycle
  maintenance 작업에서 처리.
- `ui/calc_window.py` line 338 의 주석에 legacy 경로 `docs/ui/
  SPREADSHEET_TABLE_CONTRACT.md` 가 남아 있음 (code comment). active
  doc 참조는 아니지만, slice A 또는 B 에서 함께 정리 가능. 본 audit
  에서는 UI 코드 미수정.
- Slice C 의 옵션 A vs B 결정은 본 report 의 추천 (옵션 A) 이지만,
  최종 결정은 사용자 승인 필요.

## Next Suggested Action

**Slice A — Calculator UI design token foundation.**
시작 전 추천 micro-design 1 페이지 (token name list + 현재 hex
mapping) 와 함께 user approval. 그 다음 Slice B (EN layout polish),
Slice C (action model alignment, 옵션 결정 후), Slice D (HK HSPF UI),
Slice E (unit adapter 확장, non-UI 평행 가능), Slice F (ML / inverse
restart) 순서.

## Scope Compliance

- UI 코드 / calculator logic / profile / dispatcher / expected /
  fixture / xfail / unit adapter / ML 코드 미수정.
- 새 UI/UX 문서 본문 미수정.
- result report lifecycle maintenance 미실행.
- archive / summaries 미이동.
- `project_log.md` 미수정.
- AGENTS_FULL.md 미열람.
- 구현 prompt 작성 안 함.

## Commit / Push

- audit-only 작업이므로 본 report + WORK_PLAN 짧은 갱신만 commit.
- commit message: `audit: assess calculator UI UX against SSOT`
- push to `work/ui-ux-ssot-adoption`.
