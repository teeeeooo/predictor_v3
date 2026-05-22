# 115 — Calculator Errors Helper Extraction (Slice ε)

## Goal

113 Calculator UI module boundary plan의 Slice ε 구현. `ui/calc_
window.py`에 박혀 있던 shared error / validation helper를 `ui/
calculator_errors.py`로 분리한다. EN/AHRI tab extraction (ζ/η), auto-
recompute wiring (β), per-tab result panel (γ), error feedback 정책
변경 (δ)은 이번 작업에서 하지 않는다.

## Scope

- task 1: `ui/calc_window.py`에서 helper 후보 식별.
- task 2: 신규 `ui/calculator_errors.py`에 6개 public helper 노출.
  108 token (`color.danger`, `color.bg.cell.invalid`) 사용.
- task 3: `ui/calc_window.py`가 새 module을 사용하도록 최소 변경.
  `_get_float_val` 인스턴스 메서드는 thin wrapper로 유지.
- task 4: 신규 `tests/test_calculator_errors.py` (PyQt5 없이 import 가능).
- task 5: WORK_PLAN sequence 갱신.

## Non-goals

- EN tab extraction (Slice ζ).
- AHRI tab extraction (Slice η).
- AHRI/EN auto-recompute wiring (Slice β).
- per-tab result/status panel (Slice γ).
- error feedback UX 정책 변경 (Slice δ).
- Hong Kong HSPF UI surface 추가.
- Train/Predict 리팩토링.
- unit adapter / ML / inverse-search.
- calculator logic / profile / dispatcher / expected / fixture / xfail.
- theme token 새로 추가.
- core calculator validation 수정.
- result report lifecycle maintenance.
- `ACTIVE_DOCUMENTS.md`, `project_log.md`, architecture doc 수정.

## Verification

- `python3 -B -m py_compile ui/calculator_errors.py ui/calc_window.py tests/test_calculator_errors.py` → OK
- `python3 -B -m pytest tests/test_calculator_errors.py -q` → 18 passed, 1 skipped (PyQt5 미설치 환경의 `bind_error_reset` smoke만 skip)
- `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q` → 1 skipped (PyQt5 미설치 환경)
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q` → 3 passed
- `python3 -B -m pytest tests/test_ui_theme_tokens.py -q` → 32 passed
- `python3 -B -m pytest -q` → 480 passed, 7 skipped, 23 xfailed (이전 462 + 신규 18 calculator_errors tests)

## Task Results

### task 1 — helper inventory

`ui/calc_window.py`에서 식별한 shared helper / class (이전 line
번호 기준):

| helper | 이전 위치 | 사용처 |
| --- | --- | --- |
| `parse_number(text)` | top-level function (line 38–44) | `_get_float_val` 내부에서만 호출 |
| `InputValidationError` | top-level class (47–51) | EN/AHRI/HSPF2 read helper 다수 + `on_calculate` except 절 |
| `bind_error_reset(widget)` | `CalculatorWindow` 메서드 (127–129) | `init_en_tab` (5곳), `init_ahri_tab` (1곳) |
| `_get_float_val(widget, field_name, ...)` | `CalculatorWindow` 메서드 (510–525) | AHRI/EN/HSPF2 read 다수 (`Cd_low`, `t_off`, `t_on`, defrost, `p_to_w`, `p_sb_w`, `p_ck_w`, `p_off_w`, `p_design_c_w`, `p_design_h_w`, `Tbiv`, `TOL`) |
| error style 적용 (red border + soft red bg) | `on_calculate` except 절 inline | only `on_calculate` |
| error style clear | `_clear_all_errors` inline `setStyleSheet("")` | only `_clear_all_errors` (+ `bind_error_reset` 연결) |

이동 대상: 위 6개 모두. 잔류 대상: tab UI construction, calculate path,
read helper, profile resolver, `_get_float_val` 인스턴스 메서드의
**호출 시그니처** (호출자가 많아 thin wrapper로 유지).

### task 2 — `ui/calculator_errors.py`

신규 module `ui/calculator_errors.py` (110 LOC) 제공:

- `InputValidationError(Exception)`: 동일 `__init__(message, widget=
  None)`, 동일 `self.widget` 속성.
- `parse_number(text) -> float`: 동일 동작 (콤마 제거, 양끝 공백 제거,
  빈 문자열은 `ValueError("빈 값입니다.")`).
- `bind_error_reset(widget) -> None`: `widget.textChanged.connect(
  lambda: widget.setStyleSheet(""))` 그대로.
- `apply_error_style(widget) -> None`: `ui.theme.color('color.danger')`
  + `ui.theme.color('color.bg.cell.invalid')` 사용한 동일 stylesheet.
- `clear_error_style(widget) -> None`: `widget.setStyleSheet("")`.
- `get_float_val(widgets, key, field_name, *, allow_empty=False,
  allow_zero=False) -> float | None`: dict + key + label 형태로 호출.
  내부 메시지는 한국어 그대로:
  - 빈 값: `'{field}' 항목을 입력해주세요.`
  - 비숫자: `'{field}' 필드에 올바른 숫자를 입력해주세요.`
  - non-positive (`allow_zero=False`): `'{field}' 필드는 0보다 큰 값
    이어야 합니다.`
  raise 시 `InputValidationError.widget`에 widget 첨부 그대로.
- PyQt 의존: bind/apply/clear는 widget의 duck-type 메서드만 호출.
  PyQt5 import 없음. 108 `ui.theme.color`만 import.
- core 모듈 의존 없음. UI helper 전용.

### task 3 — `ui/calc_window.py` 변경

- top-level의 `parse_number` 함수 정의와 `InputValidationError`
  class 정의를 삭제. 대신 `from ui.calculator_errors import (
  InputValidationError, apply_error_style, bind_error_reset as
  _bind_error_reset_widget, clear_error_style, get_float_val,
  parse_number)`로 교체.
- `CalculatorWindow.bind_error_reset` 인스턴스 메서드는 thin wrapper
  로 유지 (`_bind_error_reset_widget(widget)` 호출). 호출부 6곳 그대로.
- `CalculatorWindow._get_float_val(widget, field_name, allow_empty,
  allow_zero)`는 thin wrapper로 유지. 내부에서 `get_float_val({"_":
  widget}, "_", field_name, allow_empty=..., allow_zero=...)`로 위임.
  AHRI/EN/HSPF2 read 호출부 12곳 그대로.
- `on_calculate` except 절의 inline stylesheet 빌드를
  `apply_error_style(e.widget)` 호출로 교체. focus / selectAll
  복원은 그대로 유지.
- `_clear_all_errors` 내부 `w.setStyleSheet("")`를 `clear_error_style(w)`
  로 교체.
- `QMessageBox.warning` / `QMessageBox.critical` 흐름, error 메시지
  문구, validation 분기, EN/AHRI calculate path, `result_label` 동작
  모두 변경 없음.
- import cycle 없음 (`calculator_errors` → `theme`만 의존, 반대 방향
  없음).

### task 4 — 신규 테스트

`tests/test_calculator_errors.py` (19 test case):

`parse_number` (6):
- 콤마 strip + float (`"1,234.5" → 1234.5`)
- whitespace trim (`" 10 "`)
- 음수 / scientific (`-3.5`, `1e3`)
- 빈 문자열 / whitespace-only → `ValueError("빈 값")`
- non-numeric → `ValueError`

`InputValidationError` (2):
- widget reference 보존
- widget 기본값 None

`get_float_val` (with `_FakeLineEdit`, PyQt 없이) (9):
- positive float / comma 처리
- 빈 문자열 → `InputValidationError`, widget 포함
- `allow_empty=True`로 빈 입력 → `None`
- non-numeric → 한국어 메시지 + widget 포함
- `0` → `allow_zero=False` 일 때 raise, `allow_zero=True`일 때 0.0
- 음수 → `allow_zero=False` 일 때 raise

`apply_error_style` / `clear_error_style` (2):
- `apply` 후 stylesheet에 `color.danger` / `color.bg.cell.invalid`
  token 값 포함 + "border" 단어 포함
- `clear` 후 stylesheet 빈 문자열

`bind_error_reset` (1, PyQt 필요):
- `pytest.importorskip("PyQt5")`로 skip-safe.
- `QLineEdit` → `setStyleSheet("border: ...")` 후 `bind_error_reset` →
  `setText("...")` → `styleSheet() == ""`.

PyQt5가 없는 본 environment에서는 18 passed + 1 skip. screenshot /
pixel-perfect test 없음. `QMessageBox` monkeypatch 없음. EN/AHRI
golden 추가 없음.

기존 `tests/test_app_calculator_ui_smoke.py`는 수정하지 않았고,
PyQt5 없는 환경에서 그대로 skip. CI / 회사 PC에서 EN/AHRI smoke가
계속 button click 경로로 통과해야 함 (read helper signature와 error
flow 그대로 유지).

### task 5 — WORK_PLAN

- `docs/WORK_PLAN.md` 항목 4b (Slice ε `ui/calculator_errors.py`
  추출) **완료** 표시. recommended next는 Slice ζ — EN tab
  extraction.
- 다음 sequence (4c~4g, 4h ML 복귀 + Train/Predict refactor) 유지.
- `ACTIVE_DOCUMENTS.md` 수정 없음 (`ui/calculator_errors.py`는
  module owner inventory가 아니라 helper). 추후 lifecycle maintenance
  에서 source layout 변화가 누적되면 반영.
- result report lifecycle maintenance 미실행. 114 cycle 직후라 active
  누적이 다시 시작하는 시점이므로 trigger 부근 아님.

## Test Results

- `python3 -B -m py_compile ui/calculator_errors.py ui/calc_window.py tests/test_calculator_errors.py` → OK
- `python3 -B -m pytest tests/test_calculator_errors.py -q` → 18 passed, 1 skipped
- `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q` → 1 skipped (PyQt5 미설치)
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q` → 3 passed
- `python3 -B -m pytest tests/test_ui_theme_tokens.py -q` → 32 passed
- `python3 -B -m pytest -q` → 480 passed, 7 skipped, 23 xfailed

## Changed Files

- A `ui/calculator_errors.py`
- M `ui/calc_window.py` (top-level helper 삭제 + import + 2 thin
  wrapper + `apply/clear_error_style` 호출)
- A `tests/test_calculator_errors.py`
- M `docs/WORK_PLAN.md` (Slice ε 완료 표시)
- A `result_reports/active/115_calculator-errors-helper-extraction.md`

## Known Failures / Risks

- 본 environment 는 PyQt5 미설치라 `bind_error_reset` smoke와 기존
  app calculator UI smoke가 skip. CI / 회사 PC 환경에서 동일 path
  (`bind_error_reset` 호출부 6곳 + `_get_float_val` 호출부 12곳 +
  `apply/clear_error_style` 1곳씩) 가 정상 작동하는지 확인 필요.
  thin wrapper signature 그대로라 regression 가능성 낮음.
- `theme_color` 직접 import가 calc_window에 남아 있지만 현재 미사용
  상태가 됨. 다음 slice ζ에서 EN tab을 분리할 때 자연스럽게 정리될
  예정 (calc_window가 shell-only가 되면 theme color 직접 사용 자체가
  거의 없음).

## Next Suggested Action

**Slice ζ — `ui/calculator_en_tab.py` extraction.** EN14825 tab의
UI construction (`init_en_tab`), profile populate, region change
handler, table read (`_read_en_table_points_kw`, `_selected_scop_
climates`), `calculate_en` 을 `EN14825Tab(QWidget)` class로 이동.
`CalculatorWindow`는 instance 부착 + alias forwarding (`window.en_*`
smoke attribute) 만 담당.

## Scope Compliance

- EN/AHRI tab 미이동.
- auto-recompute wiring 미구현.
- `계산 실행` 버튼 정책 / `result_label` / `QMessageBox` 정책 미변경.
- 에러 메시지 문구 / validation 기준 미변경.
- theme token 신규 추가 없음.
- core calculator validation 미수정.
- Hong Kong HSPF UI / unit adapter / ML 미수정.
- calculator logic / profile / dispatcher / expected / fixture / xfail
  미수정.
- result report lifecycle maintenance 미실행.
- `ACTIVE_DOCUMENTS.md`, `project_log.md`, architecture doc 미수정.
- AGENTS_FULL.md 미열람.

## Commit / Push

- 단일 commit (`ui/calculator_errors.py` + `ui/calc_window.py` +
  `tests/test_calculator_errors.py` + `docs/WORK_PLAN.md`),
  본 report 별도 commit.
- commit message: `refactor: extract calculator error helpers`
- report commit message: `report: 115 calculator errors helper extraction`
- push to `work/ui-ux-ssot-adoption`.
