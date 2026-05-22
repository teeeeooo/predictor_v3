# 109 — EN14825 Tab Layout Polish

## Goal

EN14825 tab을 새 UI/UX SSOT (`docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`
§5 / §7) 와 108 token foundation 기준에 맞춰 작게 정리한다. standby
위치, single-input row width, SCOP climate card spacing만 손댄다.
auto-calculate, calculate path, W→kW 변환, key, default는 변경하지
않는다.

## Scope

- task 1: EN tab standby form을 최상단 compact horizontal row로 이동.
- task 2: `p_design_c_w`, climate별 `p_design_h_w` / `tbiv_w` / `tol_w`
  의 single-input full-width 회피 (max width 제한 + horizontal row).
- task 3: SCOP climate card 내부 spacing을 `ui.theme.spacing` token
  으로 정렬.
- task 4: layout smoke test 추가 (standby 위치 + key/default 유지).
- task 5: 본 report + WORK_PLAN sequence 갱신.

## Non-goals

- AHRI / ISO tab layout 변경
- auto-calculate behavior 변경
- `계산 실행` 버튼 정책 변경
- EN14825 core / W→kW 변환 / golden 변경
- input key 변경, climate dict 구조 변경
- result rendering 구조 변경
- SCOP climate checkbox 동작 변경
- 색 재디자인 / theme 추가 token
- Hong Kong HSPF UI / unit adapter / ML 작업
- result report lifecycle maintenance

## Verification

- `python3 -B -m py_compile ui/calc_window.py ui/theme.py tests/test_app_calculator_ui_smoke.py` → OK
- `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q` → 1 skipped (이 환경 PyQt5 미설치). 새 layout smoke 포함.
- `python3 -B -m pytest tests/test_ui_theme_tokens.py -q` → 32 passed
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q` → 3 passed
- `python3 -B -m pytest -q` → 462 passed, 6 skipped, 23 xfailed

PyQt5 가 설치된 CI / 회사 PC 환경에서는 EN smoke 9개 (기존 8 + 신규 1)
모두 실행되며, 본 변경은 layout 만 손대므로 SEER / SCOP / W→kW
계산 검증 smoke가 그대로 통과해야 한다 (코드 path 미변경).

## Task Results

### task 1 — Standby section을 상단 compact row로 이동

- 변경 대상: `ui/calc_window.py::init_en_tab`.
- 이전: standby form (`QFormLayout` × 4 row) 이 layout 맨 아래.
- 변경 후: profile combo 바로 아래에 `self.en_standby_group`
  (`QGroupBox`, objectName `en_standby_group`) 을 두고, 내부는
  `QHBoxLayout` 으로 `p_to (W): [QLineEdit]  p_sb (W): [QLineEdit]
  p_ck (W): [QLineEdit]  p_off (W): [QLineEdit]` + `addStretch()`.
- 입력 key 유지: `p_to_w`, `p_sb_w`, `p_ck_w`, `p_off_w`.
- default 0.0 prefill 유지.
- W 단위 유지. `calculate_en()` 의 `_get_float_val` + W→kW 변환 path
  미변경 (호출 위치/로직 그대로).
- `bind_error_reset()` 호출 유지 → error styling 토큰 (108) 그대로
  적용됨.

### task 2 — Single-input row width / compact layout

- `combo_region_en.setMaximumWidth(320)` — region combo 가 전체 폭을
  먹지 않도록 제한.
- SEER `p_design_c_w` 은 `QFormLayout` → `QHBoxLayout` 으로 교체
  (`QLabel("p_design_c (W, SEER):") + QLineEdit(MaxW 120) + stretch`).
- SCOP climate card 내부 `p_design_h_w` / `tbiv_widget` / `tol_widget`
  은 세 `QFormLayout row` (수직 누적) → 한 `QHBoxLayout` (3 label +
  3 input + stretch). 각 input `setMaximumWidth(110)`.
- standby input 4개도 `setMaximumWidth(90)` 으로 통일 (compact grid).
- p_design_c / p_design_h / Tbiv / TOL `QLineEdit` 객체 자체는 동일
  하게 `self.input_widgets_en` / climate dict 에 등록 — read path
  (`_read_en_table_points_kw`, `calculate_en`) 미변경.
- climate dict key 이름 `p_design_h_w` / `tbiv_w` / `tol_w` 모두 그대로
  유지 (smoke test 호환).

### task 3 — SCOP climate card spacing

- 사용 token (모두 기존 `ui/theme.py` token):
  - `space.section` → EN tab outer `QVBoxLayout.setSpacing()`,
    seer_layout, scop_layout.
  - `space.row` → standby row, seer aux row, climate card layout,
    climate aux row.
- climate card 내부 layout 는 그대로 `QVBoxLayout` (table 위, aux row
  아래). card 의 `setCheckable(True)` / `setChecked()` / Average 기본
  동작 미변경.
- 색 / stylesheet / table model / factory / `make_en14825_*` 모두 미수정.
- SCOP climate 선택 방식 (`average` default check) 변경 없음. unchecked
  climate 는 그대로 표시 (숨김 동작 도입 없음).

### task 4 — UI smoke 보호

- `tests/test_app_calculator_ui_smoke.py` 에 1개 smoke 추가:
  `test_en_standby_group_is_positioned_above_seer_and_scop_sections`.
  - `self.tab_en` 의 `QVBoxLayout` 안에서 `en_standby_group`,
    `en_seer_group`, `en_scop_group` 의 index 를 비교해 standby <
    seer 와 standby < scop 을 단순 검증.
  - standby 4개 key 가 모두 존재하고 text 가 "0.0" 인지 확인.
- 기존 EN smoke (SEER table layout / SCOP multi-climate / climate
  default temp prefill / SEER profile show-hide / SEER 계산 / SCOP
  단일 climate 계산 / SCOP multi-climate 계산 / W→kW 변환 / HSPF2
  required validation) 그대로 유지. layout 만 손대고 read/write path
  미변경 이라 회귀 없음 (PyQt5 환경에서 검증 필요).
- 새 smoke 는 PyQt5 가 없는 환경에서는 기존 `pytest.importorskip("PyQt5")`
  로 자동 skip → optional 정책 준수.
- screenshot / pixel-perfect / 수동 조작 기반 test 없음.

### task 5 — WORK_PLAN

- `docs/WORK_PLAN.md` Near-term execution order 의 항목 3.3 (EN14825
  layout polish) 을 완료 표시로 갱신. 108 token foundation 의
  `theme_spacing("space.section"/"space.row")` 가 실제 사용처에서 처음
  적용되었음을 명시. recommended next action 을 Slice C (Calculator
  auto-calculate behavior alignment) 로 이동.
- 그 외 항목 (HK HSPF UI, unit adapter, ML restart) 순서 유지.
- result report lifecycle maintenance 는 본 작업 범위가 아니므로
  수행하지 않음. Known Risks 에 pending 으로만 기록.

## Test Results

- `python3 -B -m py_compile ui/calc_window.py ui/theme.py tests/test_app_calculator_ui_smoke.py` → 통과
- `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q` → 1 skipped (PyQt5 미설치 환경)
- `python3 -B -m pytest tests/test_ui_theme_tokens.py -q` → 32 passed
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q` → 3 passed
- `python3 -B -m pytest -q` → 462 passed, 6 skipped, 23 xfailed

## Changed Files

- M `ui/calc_window.py` (`init_en_tab` 재배치 + token spacing 사용)
- M `tests/test_app_calculator_ui_smoke.py` (new layout smoke)
- M `docs/WORK_PLAN.md` (sequence 갱신)
- A `result_reports/active/109_en14825-layout-polish.md`

## Known Failures / Risks

- result report lifecycle maintenance pending — `result_reports/
  active/` 누적이 trigger 부근. 별도 작업.
- 현재 environment 에서는 PyQt5 미설치라 UI smoke 가 skip. CI / 회사
  PC 환경에서 EN smoke 9개 모두 실행하여 확인 필요. layout 만 손대고
  read/write/calculate path 미변경이므로 regression 위험은 낮다.
- 108 token foundation 의 `space.card` token 은 본 slice 에서 직접
  사용처가 없음 (사용한 token 은 `space.section`, `space.row`). 다음
  polish slice 에서 카드 padding 적용 시 자연스럽게 검증됨.

## Next Suggested Action

**Slice C — Calculator action model alignment.** ISO tab 의 auto-calc
와 AHRI/EN 의 explicit `계산 실행` 사이 mixed pattern 정리. 옵션 결정
(전 tab auto-calc 통일 vs explicit 통일) 을 위한 짧은 micro-design
1 page 가 먼저 필요. layout polish / token / unit adapter 와 섞지
않음.

## Scope Compliance

- AHRI / ISO tab layout 미변경.
- auto-calculate / `계산 실행` 버튼 정책 미변경.
- EN14825 core / `_read_en_table_points_kw` / W→kW 변환 미변경.
- input key (`p_to_w`, `p_sb_w`, `p_ck_w`, `p_off_w`, `p_design_c_w`,
  climate dict keys) / default 0.0 / climate dict 구조 미변경.
- calculator logic / profile / dispatcher / expected / fixture / xfail
  미수정.
- Hong Kong HSPF UI / unit adapter / ML 미수정.
- 색 재디자인 / dark mode / screenshot test 없음.
- result report lifecycle / archive / summaries 미이동.
- `ACTIVE_DOCUMENTS.md`, `project_log.md` 미수정.
- AGENTS_FULL.md 미열람.

## Commit / Push

- 단일 commit (`ui/calc_window.py` + smoke + WORK_PLAN), report 별도
  commit.
- commit message: `ui: polish EN14825 calculator layout`
- report commit message: `report: 109 EN14825 layout polish`
- push to `work/ui-ux-ssot-adoption`.
