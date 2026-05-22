# 113 — Calculator UI Module Boundary Plan

## Goal

`ui/calc_window.py`가 ~852 LOC까지 자란 상태에서 AHRI/EN auto-
recompute wiring (Slice β)을 그대로 얹기 전에, calculator UI의 module
boundary를 design-gate한다. 본 작업은 design / docs / report 만
수정하고, UI 코드 이동/refactor 구현은 하지 않는다.

## Scope

- task 1: `ui/calc_window.py` 책임 inventory + 분리/잔류 후보 분류.
- task 2: target module structure 제안 + 각 module의 public interface
  초안 + 의존 방향.
- task 3: 실제 refactor slice 분할 (ε / ζ / η / β / γ / δ) + 추천 next
  implementation slice.
- task 4: `docs/architecture/project_architecture.md`에 calculator UI
  module boundary 짧은 subsection 추가.
- task 5: design doc 작성, WORK_PLAN 갱신, 본 report.

## Non-goals

- `ui/calc_window.py`, `ui/calculators_2point.py`,
  `ui/spreadsheet_table.py`, `ui/theme.py` 코드 수정.
- AHRI/EN auto-recompute wiring 구현 (Slice β).
- per-tab result/status panel 구현 (Slice γ).
- error feedback alignment 구현 (Slice δ).
- Hong Kong HSPF UI surface 추가.
- unit adapter / ML / inverse-search.
- calculator logic / profile / dispatcher / region config / expected /
  fixture / xfail 수정.
- tests 수정.
- result report lifecycle maintenance.
- `ACTIVE_DOCUMENTS.md`, `project_log.md` 수정.

## Verification

- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q`
  → 3 passed
- `python3 -B -m pytest -q` → 462 passed, 6 skipped, 23 xfailed
- 코드 변경 없음. diff는 architecture doc + 신규 design doc + WORK_PLAN
  + 본 report.

## Task Results

### task 1 — `ui/calc_window.py` 책임 inventory

전체 파일 강제 readthrough 없이 rg로 class/function 단위만 확인했다
(상세 inventory는 design doc의 "Current responsibilities" 표 참고).
요약:

- shell 책임 (유지):
  - `CalculatorWindow.__init__`, `init_ui` (tab container + 하단
    `계산 실행` button + `result_label`)
  - `on_calculate` dispatch + `_clear_all_errors`
  - `scan_configs` (regions 로딩)
  - `init_iso_tab` (이미 `IsoCspfSingleWidget` 부착만 하는 thin
    delegate)
- EN tab 책임 (분리 대상):
  - `init_en_tab` (149 lines, SEER table + SCOP climate cards +
    standby compact row)
  - `_populate_en_profiles`, `on_region_changed_en`
  - `_read_en_table_points_kw` (W→kW 변환 포함)
  - `_selected_scop_climates`
  - `calculate_en`
- AHRI tab 책임 (분리 대상):
  - `init_ahri_tab` (~130 lines, system type radio + SEER2 table +
    extras + HSPF2 v3 table + auxiliary form)
  - `_populate_ahri_profiles`, `on_region_changed_ahri`,
    `_load_hspf2_calc`
  - `_read_ahri_seer2_table_points`, `_read_ahri_hspf2_table_points`,
    `_read_ahri_seer2_point`
  - `calculate_ahri`, `_build_hspf2_v3_input`, `calculate_hspf2_v3`
- shared helpers (분리 대상):
  - `InputValidationError`
  - `bind_error_reset`
  - `_get_float_val`
  - `parse_number` (top-level)
  - 108 token-bound error border / background styling (이미 token 참조)
- ISO tab 책임 (이미 분리됨):
  - `ui/calculators_2point.py::IsoCspfSingleWidget` (auto-calc + result
    panel + detail tabs)
  - `calculate_iso` (현재 no-op pass — Slice γ 이후 제거 가능)
- 공통 component (이미 분리됨):
  - `ui/spreadsheet_table.py` — `SpreadsheetTableModel` (`values_
    changed` Slice α 포함), `SpreadsheetTableView`, 4개 factory.
  - `ui/theme.py` — token registry + helper 3개 (108).

### task 2 — Target module structure

```
ui/calc_window.py              # shell only
ui/calculators_2point.py       # IsoCspfSingleWidget (unchanged)
ui/spreadsheet_table.py        # SpreadsheetTableModel/View (unchanged)
ui/theme.py                    # tokens (unchanged)
ui/calculator_errors.py        # InputValidationError, get_float_val, styling, parse_number
ui/calculator_en_tab.py        # EN14825Tab(QWidget)
ui/calculator_ahri_tab.py      # AHRITab(QWidget)
ui/calculator_recompute.py     # DebouncedRecompute (Slice β)
ui/calculator_result_panel.py  # CalculatorResultPanel (Slice γ)
```

Public interfaces (design doc "Public interfaces" 섹션 참고):

- `EN14825Tab(QWidget)` / `AHRITab(QWidget)`: 공통 패턴
  - `values_changed: pyqtSignal` (내부 SpreadsheetTableModel forward)
  - `profile_changed: pyqtSignal` (optional)
  - `populate_profiles(profiles)`, `set_calculator(...)`,
    `read_inputs()` (raises `InputValidationError`),
    `calculate() -> str`, `clear_errors()`.
- `CalculatorResultPanel(QWidget)`:
  `set_result_text`, `set_status(text, kind="info"|"error"|"success")`,
  `clear()`.
- `DebouncedRecompute(callback, *, interval_ms=250)`:
  `connect(signal)`, `disconnect(signal)`, `trigger_now()`.
- `ui.calculator_errors`: `InputValidationError`, `bind_error_reset`,
  `clear_error_style`, `apply_error_style`, `parse_number`,
  `get_float_val(widget, field_name, *, allow_empty=False,
  allow_zero=False) -> float`. PyQt 의존은 `QLineEdit` styling에
  국한.
- `CalculatorWindow`:
  `init_ui`, `on_calculate`, `_clear_all_errors`. 길이는 ~150 LOC
  목표.

의존 방향:

- shell → 세 tab module + (slice β부터) recompute + (slice γ부터)
  result panel + (slice ε부터) errors.
- 각 tab module → `ui.spreadsheet_table`, `ui.theme`,
  `ui.calculator_errors`, `core.calculator_*` (one-way).
- tab module끼리는 import하지 않음.
- core → ui 방향 import는 금지 (기존 boundary 유지).

기존 test 호환 전략: smoke가 사용 중인 public window attribute
(`window.en_seer_group`, `window.en_scop_group`,
`window.en_standby_group`, `window.input_widgets_en`,
`window.en_scop_climates`, `window.ahri_seer2_model`,
`window.ahri_hspf2_model`, `window.input_widgets_ahri`,
`window.input_widgets_hspf2`, `window.radio_hp/ac`,
`window.en_seer_model`, `window.en_seer_view`)는 각 tab 인스턴스
property 또는 `CalculatorWindow`의 alias로 forward. smoke 자체는
slice ζ/η에서 수정하지 않음.

### task 3 — Refactor slice 분할

Slice α (`values_changed`)은 111에서 끝났다. 본 design은 이어지는
slice ε → ζ → η → β → γ → δ를 정의한다.

#### Slice ε — `ui/calculator_errors.py` 추출 (추천 next)
- 목적: 공통 validation/styling helper를 single source로 끌어내, 이후
  tab module이 동일 helper만 import하도록 base를 마련.
- 수정 대상 후보: `ui/calc_window.py` (import만), 신규
  `ui/calculator_errors.py`, 신규 `tests/test_calculator_errors.py`.
- 포함: `InputValidationError`, `parse_number`, `bind_error_reset`,
  `clear_error_style`, `apply_error_style`, `get_float_val`. 108
  token 참조 유지.
- 제외: tab UI 이동 (ζ/η), recompute wiring (β), result panel (γ),
  error routing 변경 (δ). 색 재디자인 없음.
- 선행: 없음.
- 검증: `tests/test_calculator_errors.py` 신규 (parse_number /
  get_float_val 경계 단위). `tests/test_app_calculator_ui_smoke.py`
  PyQt5 CI에서 regression 없음.

#### Slice ζ — `ui/calculator_en_tab.py` 추출
- 목적: EN14825 tab을 자기 widget tree와 read/calc/format helper의
  자체 owner로 분리.
- 수정 대상 후보: `ui/calc_window.py` (init_en_tab 호출을 tab 인스턴스
  화로 교체), 신규 `ui/calculator_en_tab.py`.
- 포함: `init_en_tab`, `_populate_en_profiles`, `on_region_changed_en`,
  `_read_en_table_points_kw`, `_selected_scop_climates`,
  `calculate_en`을 `EN14825Tab` class로 이동. `values_changed`
  forward (내부 `SpreadsheetTableModel` 인스턴스 4개의 `values_changed`
  를 단일 `EN14825Tab.values_changed`로 묶음).
- 제외: AHRI tab (η), recompute wiring (β), result panel (γ), error
  routing (δ).
- 선행: Slice ε (errors helper import 위해).
- 검증: 기존 EN smoke 9개 모두 통과 (PyQt5 CI). `window.en_*`
  attribute alias forwarding.

#### Slice η — `ui/calculator_ahri_tab.py` 추출
- 목적: AHRI tab 동일 패턴.
- 수정 대상 후보: `ui/calc_window.py`, 신규 `ui/calculator_ahri_tab.py`.
- 포함: `init_ahri_tab`, `_populate_ahri_profiles`,
  `on_region_changed_ahri`, `_load_hspf2_calc`,
  `_read_ahri_seer2_table_points`, `_read_ahri_hspf2_table_points`,
  `_read_ahri_seer2_point`, `calculate_ahri`, `_build_hspf2_v3_input`,
  `calculate_hspf2_v3`. `values_changed` forward (SEER2 + HSPF2
  model 2개).
- 제외: recompute (β), result panel (γ), error routing (δ).
- 선행: Slice ε.
- 검증: 기존 AHRI smoke 모두 통과 (button click + HSPF2 required
  validation). `window.ahri_*`, `window.input_widgets_ahri`,
  `window.input_widgets_hspf2`, `window.radio_hp/ac` alias.

#### Slice β — AHRI/EN auto-recompute wiring
- 목적: 110 design 결정 (Option A) 의 핵심 wiring. `EN14825Tab.values_
  changed`와 `AHRITab.values_changed`에 `DebouncedRecompute`를
  연결해 입력 변경 시 자동 재계산.
- 수정 대상 후보: 신규 `ui/calculator_recompute.py`,
  `ui/calculator_en_tab.py`, `ui/calculator_ahri_tab.py`,
  `ui/calc_window.py` (window-level `계산 실행` 버튼을 optional
  "Recalculate now"로 격하).
- 포함: debounce helper + wiring + 기존 button click path와 동일
  helper 호출.
- 제외: ISO (이미 auto-calc), result panel 재배치 (γ), error
  routing (δ).
- 선행: Slice ε + ζ + η.
- 검증: 기존 button click smoke 유지 + `values_changed` 직접 트리거
  smoke 추가 (debounce wall-clock 의존 회피).

#### Slice γ — Per-tab result / status surface unification
- 목적: 각 tab이 자기 result/status panel을 가지도록 일관화. 110
  design의 γ 슬라이스.
- 수정 대상 후보: 신규 `ui/calculator_result_panel.py`,
  `ui/calculator_en_tab.py`, `ui/calculator_ahri_tab.py`,
  `ui/calc_window.py` (window-level `result_label` 제거/축소,
  `calculate_iso` no-op 제거).
- 포함: layout 수준 result surface. table contract / validator 미변경.
- 제외: error routing (δ), Hong Kong HSPF UI.
- 선행: Slice β.
- 검증: 각 tab의 `result_panel` objectName + index smoke (109 스타일).

#### Slice δ — Error feedback alignment
- 목적: `InputValidationError`의 popup `QMessageBox.warning`을 per-
  tab `CalculatorResultPanel.set_status(kind="error")`로 대체. 기타
  exception은 `QMessageBox.critical` 유지하되 메시지 truncation +
  trace logging.
- 수정 대상 후보: `ui/calc_window.py`, `ui/calculator_errors.py`,
  per-tab.
- 포함: routing only. validator 규칙 미변경.
- 제외: copy 변경, table coloring contract.
- 선행: Slice γ.
- 검증: monkeypatch `QMessageBox.warning` smoke.

**추천 next implementation slice: Slice ε — `ui/calculator_errors.py`
추출.**

추천 이유 (완성도 / 중복 방지 / interface 명확성):
- ε이 ζ/η/δ의 공통 dependency다. 먼저 빼면 ζ/η에서 tab module이
  shared helper에서 import하는 형태가 자연스럽고, δ에서 routing만
  바꿀 때 helper signature가 안정적이다.
- ε은 pure helper 수준 (PyQt 의존이 styling string 정도)이라 작고
  backward-compatible. parse_number/get_float_val의 boundary는
  단위 test로 보호하기 좋다.
- `calc_window.py`에서 ε 이후 EN/AHRI tab을 빼면 shell이 ~150 LOC
  목표에 자연스럽게 도달.
- Slice β를 ε/ζ/η 위에 올리면 recompute wiring이 좁은 module에 갇혀
  `calc_window.py`가 더 자라지 않는다.

### task 4 — architecture doc 수정

`docs/architecture/project_architecture.md` §5의 기존 `UI / calc_
window.py routing contract` 아래에 새 subsection `Calculator UI
module boundary` 추가. 추가 내용:

- `CalculatorWindow`는 shell / entry 역할만 유지.
- ISO tab은 이미 `IsoCspfSingleWidget`이 owner.
- EN tab은 `ui/calculator_en_tab.py`, AHRI tab은
  `ui/calculator_ahri_tab.py`로 분리한다.
- 공통 result/status panel은 `ui/calculator_result_panel.py`,
  debounce/recompute helper는 `ui/calculator_recompute.py`,
  validation 헬퍼와 error styling은 `ui/calculator_errors.py`로
  분리한다.
- `calc_window.py`에 EN/AHRI 계산 UI 책임을 누적하지 않는다.
- tab module은 자기 widget tree와 read/format helper만 소유하고,
  core calculator construction / profile manifest는 그대로 둔다.
- core calculator 공식, validation, region config schema, profile
  dispatcher는 UI module refactor에 맞춰 바꾸지 않는다.
- tab module의 public interface는 `(parent, theme tokens)` +
  `set_calculator(...)`, `read_inputs()`, `calculate()`,
  `set_result_text()`, `values_changed`로 좁게 유지.

수정하지 않은 boundary:

- §5 calculator profile resolver / region config 경계.
- §5 calculator series reset direction / external calculator
  compatibility / result schema / forbidden coupling.
- §3.2 cascading autofill ownership / column SSOT.
- §3.3 UI Model/View Guardrails (QTableView 패턴, blockSignals
  try/finally, 1-click editor lifecycle 등).
- §1 / §2 ML 영역.

### task 5 — design doc / WORK_PLAN / report

- 신규 design doc: `docs/designs/2026-05-22-calculator-ui-module-
  boundary.md` (Background / Current responsibilities / Target module
  boundary / Public interfaces / Dependency direction / Extraction
  order / Non-goals / Test strategy / Status).
- `docs/WORK_PLAN.md`: 4번 (auto-calculate alignment) 아래에 4a~4g
  세부 항목 추가. 4a (module boundary plan) 완료 표시, 4b (Slice ε)
  recommended next로 명시. ML 복귀 시 Train/Predict refactor 항목
  (기존 8) 유지.
- `ACTIVE_DOCUMENTS.md`, `project_log.md` 미수정. 새 design doc 두
  개 (110, 113)와 architecture subsection의 inventory 반영은 다음
  lifecycle maintenance step에서 한 번에 처리하는 편이 안전. 본
  작업에서 단독 수정하지 않는다.
- result report lifecycle maintenance는 이번 작업 범위가 아니다.
  active 누적이 trigger 부근이지만 design / docs 작업이라 별도
  lifecycle maintenance step으로 분리한다. Known Risks에 pending
  으로만 기록.

## Test Results

- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q`
  → 3 passed
- `python3 -B -m pytest -q` → 462 passed, 6 skipped, 23 xfailed

## Changed Files

- M `docs/architecture/project_architecture.md` (Calculator UI module
  boundary subsection 추가)
- A `docs/designs/2026-05-22-calculator-ui-module-boundary.md`
- M `docs/WORK_PLAN.md` (4a~4g 세부 항목 추가)
- A `result_reports/active/113_calculator-ui-module-boundary-plan.md`

## Known Failures / Risks

- result report lifecycle maintenance pending — `result_reports/
  active/` 누적이 trigger 부근. 별도 작업.
- `ACTIVE_DOCUMENTS.md`에 110 / 113 두 신규 design doc과 향후 추가될
  `ui/calculator_errors.py` 등 module owner 관계가 아직 반영되지
  않음. 본 design-only 작업 scope 외이며, Slice ε/ζ/η가 끝난 뒤
  lifecycle maintenance에서 한 번에 정리 권장.
- Slice ε/ζ/η에서 alias forwarding을 깔끔하게 유지하지 못하면
  smoke가 깨질 수 있다. 각 slice 보고에 alias 매핑을 명시할 것.

## Next Suggested Action

**Slice ε — `ui/calculator_errors.py` 추출.**
범위: `InputValidationError`, `parse_number`, `bind_error_reset`,
`clear_error_style`, `apply_error_style`, `get_float_val`을 신규
module로 이동. `calc_window.py`는 import alias만 유지. 108 token
참조 그대로. 신규 `tests/test_calculator_errors.py`로 helper boundary
보호.

## Scope Compliance

- UI 코드 미수정.
- tests 미수정.
- Calculator action model / auto-recompute / result panel / error
  feedback / Hong Kong HSPF UI / unit adapter / ML 미구현.
- calculator logic / profile / dispatcher / region config / expected /
  fixture / xfail 미수정.
- `ACTIVE_DOCUMENTS.md`, `project_log.md`, archive/summaries 미수정 /
  미이동.
- AGENTS_FULL.md 미열람.
- design doc + architecture subsection + WORK_PLAN + report만 수정.

## Commit / Push

- 단일 commit (architecture + design doc + WORK_PLAN + report).
- commit message: `design: define calculator UI module boundary`
- push to `work/ui-ux-ssot-adoption`.
