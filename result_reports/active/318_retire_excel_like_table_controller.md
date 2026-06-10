# 318 Retire ExcelLikeTableController and Correct Test Gaps

## Goal

- production main table path에서 더 이상 사용되지 않는 legacy `ExcelLikeTableController`를 안전하게 retired/제거한다.
- legacy controller 전용 테스트가 검증하던 paste / undo / clear / type-replace 등의 behavior가 `TkTableController`에서 충분히 방어되고 있는지 inventory를 확인하고 부족한 검증을 보강하여 test gap을 corrected/해소한다.
- `tests/test_ui_tk_iso_table_autocalc.py` 및 `tests/test_ui_tk_table_controller.py`에 남아있던 legacy import와 assertions를 `TkTableController` 기준으로 교정한다.

## Legacy Controller Usage Audit Results

- **Production Source**: `ui_tk/excel_like_table_controller.py` 외의 어떠한 프로덕션 소스 코드(`.py`)에서도 `ExcelLikeTableController` 및 관련 모듈의 import/usage가 전혀 남아있지 않음을 확인하였습니다. (완전한 dead code)
- **Historical Mentions**: `result_reports/archive/` 및 기존 design docs 내의 historical mention을 제외하고는 런타임 소스에서 제거 준비가 끝났습니다.

## Legacy Test Coverage Inventory

`tests/test_ui_tk_excel_like_table_controller.py`가 검증하던 핵심 behavior와 `TkTableController` 관련 테스트 매핑 상태는 다음과 같습니다:

1. **parse / encode / clip / validate matrix**:
   - `test_ui_tk_table_interaction_core.py`에서 `parse_clipboard_matrix`, `encode_selection_to_clipboard` 등을 이미 직접 완벽히 테스트 중.
2. **paste (tiling, repeat-fill, single-cell copy)**:
   - `test_ui_tk_table_interaction_core.py` 및 `test_ui_tk_metric_input_table_controller_parity.py`에서 editable cell paste, mxn paste, single-cell paste, readonly cell ignore 등 다각도로 검증 완료.
3. **clear / delete / undo**:
   - `test_ui_tk_metric_input_table_controller_parity.py`에서 `TestClearAndUndo`를 통해 clear 후 복원 및 paste 후 복원을 검증 완료.
4. **invalid paste and visual validation (invalid fields, paint)**:
   - `test_ui_tk_metric_input_table_controller_parity.py`에서 `TestInvalidVisualState`를 통해 validation error 시 `TABLE_INVALID_BG`가 칠해지는 visual state와 clear behavior 검증 완료.
5. **replace on type**:
   - `test_ui_tk_metric_input_table_controller_parity.py`에서 `TestReplaceOnType`를 통해 keystroke Replace 후 edit mode 진입 및 selection clear 검증 완료.
6. **interactive behaviors (F2, Escape, Arrow Navigation, Shift Click)**:
   - `TkTableController` focused test인 `test_ui_tk_metric_input_table_controller_parity.py`에 신규 테스트 클래스 `TestInteractiveBehaviors`를 추가하여 F2 edit mode 진입, Escape key revert, arrow keys navigation, shift click extend selection을 완벽하게 검증 보강함.

## TkTableController Test Gap Resolution

- `test_ui_tk_metric_input_table_controller_parity.py`에 `TestInteractiveBehaviors` 클래스를 추가하여 `TkTableController`가 user interaction 흐름(F2, Escape, Arrow navigation, Shift-click selection)을 안전하게 방어하도록 보강하였습니다.
- `tests/test_ui_tk_table_controller.py`에 존재하던 `_FakeWidget`에 `select_clear` alias 메소드를 추가하여 mock environment에서 발생하던 `AttributeError`를 해소하고 모든 focused test가 100% green 패스하도록 조치하였습니다.

## Retired Files

- `ui_tk/excel_like_table_controller.py`
- `tests/test_ui_tk_excel_like_table_controller.py`

## Autocalc Test Assertion Corrections

- `tests/test_ui_tk_iso_table_autocalc.py`의 `ExcelLikeTableController` import를 제거하고 `TkTableController`로 교정하였습니다.
- `section.input_controller` 및 `cspf.rated_controller`에 대한 type assertion을 `TkTableController`로 정정하였습니다.
- 어댑터 상에서 `interaction_controller` 프로퍼티 우회 대신 `controller.table is table` 관계 단언문을 통해 더 적합한 behavior/relationship assertion으로 교정 완료하였습니다.

## MVC/SoC Design Decision

- **View & Adapter Layer**: `MetricInputTable`은 순수 UI grid 빌드 및 `TkTableSurface` 계약 충족에만 집중합니다.
- **Controller Layer**: `TkTableController`는 오직 `TkTableSurface` 계약 하에 UI 이벤트(copy, paste, undo, selection, navigation)를 제어하고, visual state를 페인팅하는 역할만 수행합니다.
- **Validation Boundary**: 에러 값 타당성 검사 및 invalid flag visual marking 판단은 `MetricInputTable` 및 calculator layer에 완벽히 위임하고, 컨트롤러는 raw text를 그대로 전달하기만 함으로써 완벽한 관심사 분리(SoC)를 달성하였습니다.

## Verification Result

- `python3 -B -m pytest tests/test_ui_tk_metric_input_table_controller_parity.py -vv`: 20개 테스트 전체 통과 (OK)
- `python3 -B -m pytest tests/test_ui_tk_table_controller.py -vv`: 7개 테스트 전체 통과 (OK)
- `python3 -B -m pytest tests/test_ui_tk_iso_table_autocalc.py -k test_iso_hong_kong_sections_use_corrected_layout_without_action_buttons -vv`: 수정된 단언문 테스트 통과 (OK)
- `python3 -B tools/check_code_structure.py`: 코드 구조 자동 검사 통과 (OK)

## Scope Compliance & Excluded Areas

- Calculator core logic, ML/predictor 로직, profile/region config, golden/fixture는 전혀 수정되지 않았습니다.
- `ui_tk/metric_input_table.py` 및 `ui_tk/table/controller.py` 등 핵심 프로덕션 코드 또한 어떠한 비즈니스 로직 변경 없이 dead code 삭제 및 테스트 수정으로만 진행되었습니다.

## Project Memory Delta

- `type`: decision
  `topic`: Retire ExcelLikeTableController and corrected test gaps
  `content`: Legacy ExcelLikeTableController를 완전히 제거하고, 그에 따라 발생한 테스트 갭(assert isinstance 및 import 잔재)을 TkTableController 기준으로 교정하였으며, 부족했던 user interaction(F2, Escape, arrow, shift-click) 테스트 검증을 TkTableController focused test에 추가 보강하여 folder cleanup 완료함.
  `keywords`:
    - ExcelLikeTableController retirement
    - TkTableController test gap
    - ui_tk folder cleanup
  `assertionStatus`: verified
  `source`: result_reports/active/318_retire_excel_like_table_controller.md

## Next Action Suggested

1. **EN14825 / AHRI 210/240 / KS profile expansion**
