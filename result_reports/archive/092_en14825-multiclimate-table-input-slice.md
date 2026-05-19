# 092 EN14825 Multi-Climate Horizontal Table Input Slice

## Goal
- EN14825 SEER / SCOP point 입력을 vertical `QFormLayout`에서 horizontal
  `SpreadsheetTableView` + `QAbstractTableModel` 입력으로 전환한다.
- UI 입력 단위를 W로 통일하고, EN core (`calculate_seer` /
  `calculate_scop`)와 region config (`en14825_scop.json`)는 기존 kW
  기준을 그대로 유지한다.
- SCOP는 Average / Warmer / Colder 다중 climate 선택과 climate별
  table/card 입력을 지원한다.

## Scope
- 수정 대상: `ui/spreadsheet_table.py`, `tests/test_spreadsheet_table_model.py`,
  `ui/calc_window.py`, `tests/test_app_calculator_ui_smoke.py`,
  `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`,
  `docs/WORK_PLAN.md`, 본 report.
- 수정 금지: `core/calculator_en14825.py`,
  `data/region_configs/en14825_scop.json`, AHRI SEER2/HSPF2 table 구조,
  ISO16358 UI, EN expected/golden, calculator/unit/adapter core 구현.

## Non-goals
- EN14825 계산식 / region config / expected 변경 (수행 안 함).
- Adapter `core/calculator_unit_adapter.py` 확장 (이번 slice에서 손대지 않음).
- Invalid-cell visual delegate, Tab/Enter navigation 보강.
- ISO16358 UI 작업, ISO16358-2 HSPF mismatch 후속 작업 (외부 audit 대기 hold 유지).

## Verification
| command | result |
| --- | --- |
| `python3 -B -m py_compile ui/spreadsheet_table.py ui/calc_window.py tests/test_app_calculator_ui_smoke.py` | passed |
| `python3 -B -m pytest tests/test_spreadsheet_table_model.py -q` | `39 passed in 0.53s` |
| `python3 -B -m pytest tests/test_spreadsheet_table_view.py -q` | `(included in next row)` |
| `python3 -B -m pytest tests/test_spreadsheet_table_view.py tests/test_en14825_golden.py tests/test_calculator_schema_boundaries.py -q` | `12 passed in 0.20s` |
| `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q` | `19 passed in 1.39s` |
| `python3 -B -m pytest -q` | `460 passed, 34 xfailed in 2.31s` |

## Task 1 Result — EN14825 SEER / SCOP table factories

### Modified Files
- `ui/spreadsheet_table.py`
- `tests/test_spreadsheet_table_model.py`

### Added Factories
- `make_en14825_seer_table_model(parent=None)` — columns
  `("A", "B", "C", "D")`, rows `("능력 [W]", "전력 [W]")`.
- `make_en14825_scop_table_model(parent=None)` — columns
  `("A", "B", "C", "D", "TOL", "Tbiv")`, rows
  `("능력 [W]", "전력 [W]")`.
- 모듈 상수: `EN14825_SEER_COLUMNS`, `EN14825_SEER_ROW_LABELS`,
  `EN14825_SCOP_COLUMNS`, `EN14825_SCOP_ROW_LABELS`.

### Table Shape
- SEER: 4 column × 2 row (능력 [W] / 전력 [W])
- SCOP: 6 column × 2 row (능력 [W] / 전력 [W])

### `as_point_dict()` Output
- UI 입력값을 그대로 W/W 단위 tuple로 돌려준다.
  - SEER: `{"A": (capacity_w, power_w), "B": (...), "C": (...), "D": (...)}`
  - SCOP: `{"A": (capacity_w, power_w), ..., "TOL": (...), "Tbiv": (...)}`
- 빈 cell / 비숫자 입력은 `ValueError("non-numeric capacity or power")`
  로 기존 helper와 동일하게 처리.

### Added Tests
- `test_en14825_seer_columns_and_rows_match_design_doc`
- `test_en14825_seer_factory_uses_locked_column_and_row_labels`
- `test_en14825_seer_as_point_dict_returns_w_values`
- `test_en14825_scop_columns_and_rows_match_design_doc`
- `test_en14825_scop_factory_uses_locked_column_and_row_labels`
- `test_en14825_scop_as_point_dict_returns_w_values`
- `test_en14825_scop_as_point_dict_rejects_missing_tbiv`

## Task 2 Result — EN tab wiring

### Modified File
- `ui/calc_window.py`

### 기존 → 신규 입력 범위
- 세로 `QFormLayout` 으로 받던 6 point × 2 row (`A/B/C/D/TOL/Tbiv`,
  `_capacity` / `_power` per cell) 전체를 horizontal table input으로
  교체했다. `input_widgets_en[f"{pt}_capacity"]` / `*_power` 키는
  더 이상 EN tab에서 사용되지 않는다.
- SEER profile은 단일 `make_en14825_seer_table_model()` table을 사용한다.
- SCOP profile은 Average / Warmer / Colder climate별로 독립
  `make_en14825_scop_table_model()` table + compact form (card)을 가진다.
- profile metric switch 시 `on_region_changed_en()`이 SEER section과
  SCOP section의 visibility를 토글한다 (`setVisible(metric == "SEER")`
  / `setVisible(metric == "SCOP")`).

### SCOP climate checkbox / multi-climate 구조
- 각 climate은 `QGroupBox(checkable=True)` card로 구현한다.
- 기본값: Average만 checked, Warmer / Colder는 unchecked.
- 최소 1개 climate은 선택되어야 하고, 모두 해제하면
  `InputValidationError("SCOP 계산을 위해 최소 1개 climate
  (Average / Warmer / Colder)를 선택해주세요.")`로 fail-fast.
- climate card 내부 구성:
  - SCOP horizontal table (`SpreadsheetTableView`)
  - compact form: `p_design_h [W]` (required, blank prefill),
    `Tbiv 온도 [°C]` (default prefill), `TOL 온도 [°C]` (default prefill)
- climate별 default temp prefill (UI-only; region config는 수정하지 않음):
  - Average: Tbiv=-10, TOL=-11
  - Warmer: Tbiv=2, TOL=-11
  - Colder: Tbiv=-15, TOL=-22
- 공통 standby form: `p_to [W]`, `p_sb [W]`, `p_ck [W]`, `p_off [W]`,
  모두 `0.0` prefill, 사용자가 수정하면 그 값을 사용.

### W → kW 변환
- `_read_en_table_points_kw()` helper가 model의 W 셀 값을 읽어
  `{point: (capacity_kw, power_kw)}` 로 변환 (`/1000.0`).
- `calculate_en()` 내부에서 호출 직전 변환:
  - `p_to_kw = p_to_w / 1000.0` (그리고 sb/ck/off 동일)
  - SEER: `p_design_c_kw = p_design_c_w / 1000.0`
  - SCOP: `p_design_h_kw = p_design_h_w / 1000.0` (climate별)
- 변환은 UI 책임이고 `core/calculator_en14825.py` 호출 인자는 기존
  kW 그대로 유지된다.

### 유지된 auxiliary / core / config 범위
- `core/calculator_en14825.py`는 수정하지 않았다 (kW 입력 그대로).
- `data/region_configs/en14825_scop.json`도 수정하지 않았다 (`t_design_h_c`,
  `tbiv_max_c`, `tol_max_c`, `heating_bin_*`, `operational_hours`,
  `defaults` 모두 그대로).
- AHRI SEER2/HSPF2 table 구조와 `input_widgets_ahri`/`input_widgets_hspf2`
  는 변경하지 않았다.
- ISO16358 UI (`tab_iso`)는 변경하지 않았다.
- `combo_climate_en` (단일 climate combo)은 SCOP multi-climate 구조로
  대체되어 제거했다.

### Validation / Error 처리
- 셀 누락 / 비숫자 / 0 이하 입력 시 `InputValidationError`를 던지며,
  메시지에 "EN14825 SEER" 또는 "EN14825 <Climate label> climate" 와
  point id, row 종류 (능력/전력 [W])를 명시한다.
- climate 선택이 0개일 때 fail-fast.
- 기존 `_get_float_val()` 경로는 standby (p_to/sb/ck/off),
  `p_design_c_w`, climate별 `p_design_h_w` / Tbiv / TOL 입력에 그대로
  사용한다.

## Task 3 Result — Smoke tests

### Modified File
- `tests/test_app_calculator_ui_smoke.py`

### Added / Updated Tests
- `_fill_en_seer_table()` / `_fill_en_scop_table()` helper 추가.
  실제 OS clipboard / GUI manual interaction에 의존하지 않고
  model.set_cell()로 채운다.
- `test_en_seer_input_uses_horizontal_table_layout` — column/row 라벨이
  `["A","B","C","D"]` 와 `["능력 [W]","전력 [W]"]` 인지 확인.
- `test_en_scop_input_uses_multi_climate_table_layout_with_average_default`
  — Average / Warmer / Colder card가 모두 존재하고 column/row 라벨이
  설계 doc과 일치, Average만 기본 checked.
- `test_en_scop_climate_default_temperatures_are_prefilled` — Tbiv/TOL
  prefill 값이 Average=-10/-11, Warmer=2/-11, Colder=-15/-22 인지 확인.
- `test_en_seer_profile_shows_seer_table_and_hides_scop_section` — SEER
  profile 선택 시 SEER group은 `isHidden() is False`, SCOP group은
  `isHidden() is True`.
- `test_en_calculate_button_displays_seer_result_text_for_seer_profile`
  — SEER table 채우고 계산 버튼 클릭 시 result label에 "EN14825 SEER"
  표시. golden 수치는 검증하지 않음.
- `test_en_calculate_button_displays_scop_result_text` — Average climate
  table 입력 후 result label에 "Average SCOP" 표시.
- `test_en_calculate_button_displays_multi_climate_scop_result_text` —
  Average + Warmer 선택 시 result label에 두 climate 모두 표시.
- `test_en_seer_w_input_is_converted_to_kw_before_core_call` —
  `_read_en_table_points_kw()` 가 W 입력을 kW로 변환하는지 helper
  수준에서 직접 확인.

### W → kW 변환 확인 방식
- `_read_en_table_points_kw()`를 직접 호출해 `(capacity_kw, power_kw)`
  결과가 입력 W의 1/1000인지 `pytest.approx`로 확인한다.

### PyQt optional skip
- 기존과 동일하게 `pytest.importorskip("PyQt5")` 와
  `QT_QPA_PLATFORM=offscreen` 기반.

## Task 4 Result — Documentation

### Modified Files
- `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/092_en14825-multiclimate-table-input-slice.md`

### Document Updates
- design doc EN14825 SEER / SCOP 섹션을 W 단위 + UI W → kW 변환
  + climate별 card + climate별 default temp prefill로 정정. core /
  region config 는 kW/core 기준을 유지한다고 명시. Unit boundary table의
  Manual UI input 행에 EN14825 예외 (UI W, core kW)를 추가.
- `docs/WORK_PLAN.md` Current milestone focus 에 EN14825 horizontal
  table-input slice 완료 상태와 W → kW 변환 책임 분리를 추가했다.
  Near-term execution order에서 EN14825 horizontal table-input slice
  항목을 제거하고, 다음 순서를 invalid-cell visual delegate →
  Tab/Enter navigation → 필요 시 ISO16358 table contract alignment
  audit 으로 재정렬. ISO16358-2 HSPF mismatch는 사용자 외부 audit
  대기 hold 유지.

### 다음 작업 순서
1. Invalid-cell visual delegate slice — numeric invalid 상태를 table
   delegate에서 시각 표시.
2. Tab/Enter navigation 보강 — spreadsheet contract §10 이동 규칙.
3. 필요 시 ISO16358 table contract alignment audit.
4. 이후 unit adapter를 ISO / KS / EN profile로 확장, 그 다음 ML /
   inverse-search 복귀.

## Changed Files
- `ui/spreadsheet_table.py`
- `tests/test_spreadsheet_table_model.py`
- `ui/calc_window.py`
- `tests/test_app_calculator_ui_smoke.py`
- `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/092_en14825-multiclimate-table-input-slice.md`

## Known Failures / Risks
- 본 slice는 unit adapter 확장을 수행하지 않는다. EN14825 UI W →
  core kW 변환은 `ui/calc_window.py` 안에 한정된 conversion이고,
  ML/adapter 경로 (`core/calculator_unit_adapter.py`)의 EN 지원은
  future slice 대상이다.
- climate별 card 구조에서 사용자가 `setChecked(False)` 후 다시 활성화하면
  UI 입력값은 보존되지만 validation은 그 시점 값으로만 동작한다.
- ISO16358-2 HSPF 16-case mismatch (091)는 hold 상태 그대로 유지된다.

## Next Suggested Action
- Invalid-cell visual delegate slice 시작 (numeric invalid 색상 표시).
- 이후 Tab/Enter navigation 보강과 ISO16358 table contract alignment
  audit으로 진행.

## Scope Compliance
- `core/calculator_en14825.py`, `data/region_configs/en14825_scop.json`,
  AHRI SEER2/HSPF2 table 구조, ISO16358 UI, EN expected/golden, adapter
  unit conversion 코드는 모두 수정하지 않았다.
- `QTableWidget` / `setCellWidget` 신규 도입 없음.
- AGENTS_FULL.md는 읽지 않았다.

## Commit / Push
- source change commit: 코드 + 테스트 + 디자인 doc + WORK_PLAN을
  한 commit (`feat: wire EN14825 multi-climate table input`)으로 묶는다.
- report commit (`report: ...`)을 별도로 만들고 함께 push한다.
- push 결과는 최종 터미널 보고에 남긴다.
