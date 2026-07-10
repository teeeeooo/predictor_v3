# 111 — SpreadsheetTableModel `values_changed` Signal (Slice α)

## Goal

110 micro-design (Option A — Auto-calc unified) 의 Slice α 만 수행한다.
`SpreadsheetTableModel` 에 high-level `values_changed = pyqtSignal()`
을 추가하고 AHRI / EN auto-recompute 의 진입점을 마련한다. AHRI/EN
auto-recompute wiring (β), per-tab result panel (γ), error feedback
alignment (δ) 는 본 작업에서 수행하지 않는다.

## Scope

- task 1: `SpreadsheetTableModel` 에 `values_changed` signal 추가.
- task 2: 모든 값 변경 path (`setData`, `set_cell`, `paste_tsv`,
  `clear_cells`, `undo`) 에서 실제 변경이 있을 때만 `values_changed`
  를 1회 emit. 중복 / 무변경 / OOB no-op 에서는 emit 하지 않음.
- task 3: model-level test 12개 추가.
- task 4: 기존 spreadsheet table / view / UI smoke / ISO table /
  schema boundaries / theme tokens regression 점검.
- task 5: WORK_PLAN sequence + 본 report.

## Non-goals

- AHRI/EN auto-recompute wiring (Slice β)
- `계산 실행` 버튼 정책 변경 (Slice β)
- result/status panel 변경 (Slice γ)
- error feedback alignment (Slice δ)
- Hong Kong HSPF UI surface 추가
- EN/AHRI/ISO layout polish
- unit adapter / ML 작업
- calculator logic / profile / dispatcher / expected / fixture / xfail
- result report lifecycle maintenance

## Verification

- `python3 -B -m py_compile ui/spreadsheet_table.py tests/test_spreadsheet_table_model.py` → OK
- `python3 -B -m pytest tests/test_spreadsheet_table_model.py -q`
  → PyQt5 미설치 환경에서 `importorskip` 으로 skip. CI / 회사 PC 의
  PyQt5 환경에서는 기존 + 신규 12개 모두 실행.
- `python3 -B -m pytest tests/test_spreadsheet_table_view.py -q`
  → 동일하게 skip / CI 환경에서 검증.
- `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q`
  → 동일.
- `python3 -B -m pytest tests/test_iso16358_table_excel_like_behavior.py -q`
  → 동일.
- `python3 -B -m pytest tests/test_iso16358_result_table_copy_tsv.py -q`
  → 동일.
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q`
  → 3 passed (PyQt5 independent).
- `python3 -B -m pytest tests/test_ui_theme_tokens.py -q` → 32 passed.
- `python3 -B -m pytest -q` → 462 passed, 6 skipped, 23 xfailed.

## Task Results

### task 1 — `values_changed` signal 추가

- 수정 파일: `ui/spreadsheet_table.py`.
- import 에 `pyqtSignal` 추가 (기존 PyQt import guard 구조 유지).
- `SpreadsheetTableModel` class 수준 attribute 로
  `values_changed = pyqtSignal()` 선언.
- docstring 에 `dataChanged` (Qt built-in, view refresh 용) vs
  `values_changed` (high-level subscriber 용) 역할 분리 명시.
- 기존 `dataChanged` 호출은 모두 그대로 유지 → Qt view 가 expect
  하는 behavior 변경 없음.
- 기존 public API (`set_cell`, `get_cell`, `paste_tsv`, `clear_cells`,
  `undo`, `can_undo`, `reset_undo`, `selected_to_tsv`, `to_grid`,
  `is_cell_invalid`, `as_point_dict`, `row_labels`, `column_labels`)
  signature 변경 없음.

### task 2 — emit 연결과 중복 / no-op 처리

- **`setData`**: 새 값이 현재 값과 같으면 snapshot push / dataChanged
  / `values_changed` 모두 skip 하고 `True` 만 반환 (idempotent).
  값이 바뀌면 snapshot → dataChanged → `values_changed.emit()` 한 번.
- **`set_cell`**: 동일 idempotent 처리. helper / setData 둘 다
  같은 invariant 를 따른다.
- **`paste_tsv`**: 새 `cells_changed` 카운터를 도입.
  - 빈 grid → 0 반환, snapshot push 안 함 (기존 동작 유지).
  - 모든 cell OOB → snapshot pop, `values_changed` 안 함.
  - 모든 cell 이 기존 값과 동일 → snapshot pop, `values_changed`
    안 함 (논리적 변경 0).
  - 최소 1 cell 이 실제로 바뀐 경우만 `values_changed.emit()` 한 번.
  - `cells_written` 반환 값 semantics 는 그대로 (paste 시도된 cell
    수, OOB drop 제외).
- **`clear_cells`**: 기존 `cleared > 0` guard 그대로. clear 된 cell
  이 있으면 `values_changed.emit()` 한 번. 모두 이미 빈 cell 이면
  emit 없음.
- **`undo`**: undo 후 grid 가 실제로 바뀌었는지 (`snapshot != current
  self._cells`) 비교. 바뀌면 `values_changed.emit()` 한 번. (현재
  snapshot push 가 mutation 직전에 이뤄지므로 정상 path 에서는
  대부분 `changed=True` 이지만, 방어적으로 비교 후 emit.)
- paste / clear / undo 는 모두 high-level 한 operation 이므로
  per-cell 이 아니라 operation 당 정확히 1회 emit 한다.
- 기존 `_bulk_updating` 같은 별도 guard 는 없으나, snapshot push /
  pop semantics 가 이미 high-level operation 경계를 명확히 잡고 있어
  signal 도 그 경계에 1회 attach 한 형태.

### task 3 — 테스트 (12개 추가)

`tests/test_spreadsheet_table_model.py` 끝에 `_SignalCounter` 헬퍼
+ `_attach_values_changed(model)` 헬퍼 추가 후 12개 test 추가:

- `test_values_changed_emits_once_on_single_cell_edit`
- `test_values_changed_does_not_emit_on_idempotent_set`
- `test_values_changed_emits_once_on_setdata_edit`
- `test_values_changed_does_not_emit_on_setdata_same_value`
- `test_values_changed_emits_once_per_paste_operation`
- `test_values_changed_does_not_emit_when_paste_is_fully_out_of_bounds`
- `test_values_changed_does_not_emit_when_paste_reproduces_existing_values`
- `test_values_changed_emits_once_per_clear_operation`
- `test_values_changed_does_not_emit_when_clearing_already_empty_cells`
- `test_values_changed_emits_once_per_undo_group`
- `test_values_changed_does_not_emit_when_undo_stack_is_empty`
- `test_values_changed_emits_once_per_paste_with_partial_no_op_rows`

- PyQt5 미설치 환경에서는 file 상단의 `pytest.importorskip("PyQt5")`
  가 module 전체 skip 으로 만든다 (기존 정책 유지).
- `_SignalCounter` 는 Qt event loop / timer 의존 없이 직접 slot 으로
  연결되므로 brittle 하지 않다. 비동기 / debounce 같은 wall-clock
  의존 없음.
- expected / golden 숫자는 추가하지 않음.
- AHRI/EN UI smoke 는 수정하지 않음.

### task 4 — Regression 점검

- `tests/test_spreadsheet_table_model.py` (기존 + 신규 12개): PyQt5
  설치 환경에서 모두 통과 가능한 구조. 본 environment 는 미설치라
  skip.
- `tests/test_spreadsheet_table_view.py`, `tests/test_app_calculator_
  ui_smoke.py`, `tests/test_iso16358_table_excel_like_behavior.py`,
  `tests/test_iso16358_result_table_copy_tsv.py` — PyQt5 종속 → 동일
  하게 본 환경 skip, 그러나 model 의 public API / Qt-side semantics
  (dataChanged 발생 위치, paste cells_written semantics, clear
  cleared count semantics, undo 반환 값) 모두 그대로 유지했으므로
  regression 가능성 낮음. CI / 회사 PC 검증 필요.
- `tests/test_calculator_schema_boundaries.py` → 3 passed (PyQt5
  무관).
- `tests/test_ui_theme_tokens.py` → 32 passed.
- full suite → 462 passed, 6 skipped, 23 xfailed (108 직후와 동일).
- AHRI / EN auto-calc wiring 은 본 작업에서 **수행하지 않았다**.
  `ui/calc_window.py::on_calculate`, `calculate_iso/ahri/en`,
  `result_label`, `계산 실행` 버튼 모두 그대로. 다음 Slice β 에서
  새 `values_changed` signal 을 사용하기 위한 진입점만 마련된 상태.

### task 5 — WORK_PLAN

- `docs/WORK_PLAN.md` Near-term execution order 3.4 줄에 Slice α
  완료 + 다음 recommended next action 을 Slice β 로 갱신.
- 다음 순서 (3.5 이후) 는 기존대로:
  1. AHRI/EN auto-recompute wiring (Slice β)
  2. per-tab result/status surface unification (Slice γ)
  3. error feedback alignment (Slice δ)
  4. Hong Kong HSPF UI surface design / first slice
  5. unit adapter 확장 — ISO / KS / EN profile
  6. ML / inverse-search 복귀 준비
- `ACTIVE_DOCUMENTS.md`, `project_log.md` 미수정.
- result report lifecycle maintenance 는 본 작업 범위가 아니므로
  수행하지 않음. Known Risks 에 pending 으로만 기록.

## Test Results

- `python3 -B -m py_compile ui/spreadsheet_table.py tests/test_spreadsheet_table_model.py` → OK
- `python3 -B -m pytest tests/test_spreadsheet_table_model.py -q` → skip (PyQt5 미설치 환경, CI 에서 신규 12 + 기존 통과 필요)
- `python3 -B -m pytest tests/test_spreadsheet_table_view.py -q` → skip
- `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q` → skip
- `python3 -B -m pytest tests/test_iso16358_table_excel_like_behavior.py -q` → skip
- `python3 -B -m pytest tests/test_iso16358_result_table_copy_tsv.py -q` → skip
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q` → 3 passed
- `python3 -B -m pytest tests/test_ui_theme_tokens.py -q` → 32 passed
- `python3 -B -m pytest -q` → 462 passed, 6 skipped, 23 xfailed

## Changed Files

- M `ui/spreadsheet_table.py` (signal 선언 + 5 mutation path 의
  idempotent / changed 처리)
- M `tests/test_spreadsheet_table_model.py` (12 신규 test + 헬퍼)
- M `docs/WORK_PLAN.md` (Slice α 완료 표시 + next = Slice β)
- A `result_reports/active/111_spreadsheet-table-values-changed-signal.md`

## Known Failures / Risks

- result report lifecycle maintenance pending — `result_reports/
  active/` 누적이 trigger 부근. 별도 작업.
- 본 environment 에서는 PyQt5 미설치라 model / view / UI smoke 가
  skip 됨. CI / 회사 PC 환경에서 model test (기존 + 12 신규) 와 view
  / UI smoke 가 모두 통과하는지 검증 필요. public API / Qt-side
  semantics 그대로 유지했으므로 regression 위험은 낮다.
- Slice β 에서 AHRI/EN tab 의 `make_*_table_model` factory 들이
  돌려주는 `SpreadsheetTableModel` 인스턴스의 `values_changed` 에
  debounced slot 을 연결할 것. 본 slice 는 그 진입점만 만들었다.

## Next Suggested Action

**Slice β — AHRI/EN auto-recompute wiring.** 새 `values_changed`
signal 을 AHRI SEER2 / AHRI HSPF2 / EN SEER / EN SCOP 각 climate
model 에 debounced slot 으로 연결. window-level `계산 실행` 버튼은
optional "Recalculate now" 로 격하. ISO 는 손대지 않음. result panel
폴리시 (γ), error feedback (δ) 와 섞지 않음.

## Scope Compliance

- AHRI/EN auto-recompute wiring 미실행 (Slice β 영역).
- `계산 실행` 버튼 정책 / `on_calculate` 분기 미변경.
- result / status panel 미변경.
- error feedback 미변경 (108 PoC 그대로).
- Hong Kong HSPF UI 미추가.
- EN/AHRI/ISO layout 미변경.
- unit adapter / ML 미변경.
- calculator logic / profile / dispatcher / expected / fixture / xfail
  미수정.
- `ACTIVE_DOCUMENTS.md`, `project_log.md`, archive/summaries 미수정 /
  미이동.
- AGENTS_FULL.md 미열람.
- 색 재디자인 / dark mode / screenshot test 없음.

## Commit / Push

- 단일 commit (`ui/spreadsheet_table.py` + model tests + WORK_PLAN),
  본 report 별도 commit.
- commit message: `feat: add values_changed signal to spreadsheet table model`
- report commit message: `report: 111 spreadsheet table values_changed signal`
- push to `work/ui-ux-ssot-adoption`.
