# 108 — Calculator UI Design Token Foundation

## Goal

새 UI/UX SSOT (`docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`)의 design
token을 predictor_v3 calculator UI가 참조할 수 있는 최소 foundation
module로 도입한다. inline hex 일괄 치환, layout 변경, 색 재디자인은
하지 않는다.

## Scope

- `ui/theme.py` 신규 — color / font / spacing token registry + 3개
  helper (`color`, `spacing`, `font_token`).
- `tests/test_ui_theme_tokens.py` 신규 — token key/format/import
  contract test.
- `ui/calc_window.py` 1곳 PoC — input validation error border /
  background을 token 참조로 교체. 동시에 audit (107)에서 발견된
  legacy 경로 주석 (`docs/ui/SPREADSHEET_TABLE_CONTRACT.md`)을 새
  SSOT 경로로 교체.
- `docs/WORK_PLAN.md` sequence 짧게 갱신.
- 본 report 작성.

## Non-goals

- inline hex 전체 치환
- EN/AHRI/ISO layout polish
- auto-calculate alignment
- Hong Kong HSPF UI surface
- unit adapter / ML 작업
- calculator logic / profile / dispatcher / expected / fixture
- 색상 재디자인 / dark mode / accessibility tuning
- result report lifecycle maintenance

## Verification

- `python3 -B -m py_compile ui/theme.py ui/calc_window.py ui/calculators_2point.py` → OK
- `python3 -B -m pytest tests/test_ui_theme_tokens.py tests/test_app_calculator_ui_smoke.py tests/test_calculator_schema_boundaries.py -q` → 35 passed, 1 skipped (smoke skip은 기존 환경 조건)
- `python3 -B -m pytest -q` → 462 passed, 6 skipped, 23 xfailed (token suite 32개 추가)

## Task Results

### task 1 — `ui/theme.py` token foundation

- **추가 파일**: `ui/theme.py`.
- **PyQt 의존성**: 없음. 순수 Python module. `import re`, `typing`만
  사용. `PyQt5` 미설치 환경에서도 import 가능 (test로 보호).
- **반환 형식**: helper는 `QColor` / `QFont`가 아니라 plain string /
  int / tuple만 반환. 호출 사이트가 stylesheet 문자열 또는 PyQt 객체
  로 변환한다.
- **token group / 값 매핑 기준**: 현재 calculator UI inline hex에서
  실제로 쓰이는 값을 그대로 캡쳐. 색 자체는 변경하지 않음.

color tokens (13개):
- `color.bg.app` = `#F6F7F9` (IsoCspfSingleWidget 전체 배경)
- `color.bg.card` = `#FFFFFF` (panel 배경)
- `color.bg.header` = `#F5F5F5` (summary / table header 영역)
- `color.bg.cell.readonly` = `#EEF1F4` (QLineEdit:disabled)
- `color.bg.cell.invalid` = `#FDEDEC` (error background)
- `color.text.primary` = `#102A43` (selection-color)
- `color.text.secondary` = `#526071` (status label)
- `color.text.disabled` = `#8A94A3` (disabled foreground)
- `color.accent` = `#2F6F9F` (primary button)
- `color.success` = `#2E7D32` (Qt 표준 success)
- `color.warning` = `#B26A00` (Qt 표준 warning)
- `color.danger` = `#E74C3C` (error border)
- `color.border` = `#DCE1E7` (panel border)

font tokens (7개) — `(family, size_pt, weight)` tuple:
- `font.window_title` = `(None, 16, "bold")`
- `font.card_title` = `(None, 14, "bold")` (summary / region 제목)
- `font.section_label` = `(None, 12, "bold")`
- `font.body` = `(None, 11, "normal")`
- `font.table.header` = `(None, 11, "bold")`
- `font.table.cell` = `(None, 11, "normal")`
- `font.caption` = `(None, 10, "normal")`

spacing tokens (6개):
- `space.outer` = 15 (CalculatorWindow main layout spacing)
- `space.card` = 12 (IsoCspfSingleWidget layout spacing)
- `space.section` = 8 (input_layout spacing)
- `space.row` = 6 (form gap default)
- `space.button` = 8 (button row gap)
- `space.cell` = 6 (QLineEdit padding)

- **helper API**: `color(name) -> str`, `spacing(name) -> int`,
  `font_token(name) -> tuple`. unknown token은 `KeyError`.

### task 2 — PoC 적용

- **적용 지점 1**: `ui/calc_window.py::CalculatorWindow.on_calculate`
  내부 `InputValidationError` widget styling.
  - before: `e.widget.setStyleSheet("border: 2px solid #E74C3C; background-color: #FDEDEC;")`
  - after: `theme_color('color.danger')` + `theme_color('color.bg.cell.invalid')` 참조.
- **legacy SSOT 경로 주석 수정**: `ui/calc_window.py` line 338의
  주석에서 `docs/ui/SPREADSHEET_TABLE_CONTRACT.md`를 새 SSOT 경로
  (`docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` +
  `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md`)로 교체.
- **변경 안 한 부분**:
  - `IsoCspfSingleWidget._init_ui`의 inline QSS block — token 일괄
    교체 보류 (다음 layout polish slice 영역).
  - `BinGraphWidget`, `TraceDetailPanel`, `RegionResultTableModel`
    등의 inline 색.
  - calc_window의 다른 inline hex 없음 (해당 위치가 유일).
- **layout / behavior 변경 없음**: layout, widget 구조, validation
  분기, calculate path, result_label, QMessageBox 정책 모두 그대로.
  변환된 색은 token에 그대로 캡쳐된 동일 hex이므로 UI 시각 변화 없음
  (`#E74C3C` / `#FDEDEC` 동일).

### task 3 — 테스트

- **신규 파일**: `tests/test_ui_theme_tokens.py`.
- **테스트 내용**:
  - `test_theme_module_imports_without_pyqt`: `sys.modules['PyQt5']`
    를 None으로 가린 뒤 `ui.theme` 재import. helper 3개 노출 확인.
  - `test_required_*_tokens_present`: color 12개, font 7개, spacing
    6개 필수 키 존재 확인.
  - `test_color_value_is_hex_string`: 12개 color에 대해 `#RRGGBB`
    6자리 hex regex match (`_HEX_RE`).
  - `test_spacing_value_is_positive_int`: 6개 spacing 양수 int 확인.
  - `test_font_token_structure`: 7개 font에 대해 `(family, size_pt,
    weight)` tuple. `family`는 None 또는 str. `size_pt` 양수 int.
    `weight in {"normal", "bold"}`.
  - `test_unknown_*_token_raises_keyerror`: unknown name 입력 시
    `KeyError`.
- **결과**: 32 token tests + 3 schema boundary tests passed. UI smoke
  (`tests/test_app_calculator_ui_smoke.py`)는 회귀 없이 모두 통과.
- **brittle 회피**: 색상 값 자체를 lock-in하지 않음. format / 존재 /
  타입만 검증.

### task 4 — WORK_PLAN

- `docs/WORK_PLAN.md` Near-term execution order 3.1 / 3.2 항목을 audit
  완료 + token foundation 완료로 표시. recommended next action을
  Slice B (EN14825 layout polish)로 갱신.
- 그 외 항목 (HK HSPF UI, auto-calc alignment, unit adapter, ML)
  순서는 유지.
- result report lifecycle maintenance는 이번 작업 범위가 아니므로
  수행하지 않음. active report가 lifecycle gate trigger 부근까지 가
  있지만 별도 작업에서 처리.

## Test Results

- `python3 -B -m py_compile ui/theme.py ui/calc_window.py ui/calculators_2point.py` → 통과
- `python3 -B -m pytest tests/test_ui_theme_tokens.py -q` → 32 passed
- `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q` → 모두 통과 (1 skip은 기존)
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q` → 3 passed
- `python3 -B -m pytest -q` → 462 passed, 6 skipped, 23 xfailed

## Changed Files

- A `ui/theme.py`
- A `tests/test_ui_theme_tokens.py`
- M `ui/calc_window.py` (error styling PoC + legacy SSOT 경로 주석
  수정)
- M `docs/WORK_PLAN.md` (sequence 갱신)
- A `result_reports/active/108_calculator-ui-design-token-foundation.md`

## Known Failures / Risks

- result report lifecycle maintenance pending — `result_reports/
  active/` 누적이 trigger 부근. 별도 작업.
- token 값은 inline hex의 보수적 캡쳐이며, 일부 token (success /
  warning)은 현재 inline 사용처가 없어 Qt 표준 green / amber로
  설정함. 다음 layout polish slice에서 사용처가 생기면 자연스럽게
  검증됨. 본 작업에서는 시각 출현 없음.
- inline QSS sweep (특히 `IsoCspfSingleWidget._init_ui`의 큰 block)은
  의도적으로 보류. 다음 layout polish slice에서 token 참조로 점진적
  교체.

## Next Suggested Action

**Slice B — EN14825 tab layout polish.** standby form 위치 (02 §7
single-input full-width 회피), SCOP climate 카드 spacing token 정렬,
single-input row width 제한. `ui/theme.py`가 이미 token을 제공하므로
inline hex 대신 token 참조로 작성 가능. core / unit adapter / auto-
calc / token 자체 추가는 본 slice에 섞지 않음.

## Scope Compliance

- inline hex 일괄 치환 없음 (1곳 PoC만).
- EN / AHRI / ISO layout 변경 없음.
- auto-calculate 동작 변경 없음.
- Hong Kong HSPF UI surface 추가 없음.
- calculator logic / profile / dispatcher / expected / fixture / xfail
  미수정.
- unit adapter / ML 미수정.
- `ACTIVE_DOCUMENTS.md`, `project_log.md`, archive/summaries 미이동 /
  미수정.
- AGENTS_FULL.md 미열람.
- color palette 재디자인, dark mode, screenshot test, brittle 색
  lock-in 없음.

## Commit / Push

- 단일 commit으로 묶음 (`ui/theme.py`, token test, PoC + 주석 수정,
  WORK_PLAN 갱신). 본 report는 별도 commit.
- commit message: `feat: add calculator UI theme tokens`
- report commit message: `report: 108 calculator UI design token foundation`
- push to `work/ui-ux-ssot-adoption`.
