# Work Plan

## Purpose
- 현재 우선순위와 다음 실행 순서를 관리한다.
- 장기 목표와 Phase 1~5는 `PROJECT_CHARTER.md`를 따른다.
- 실제 작업 기록과 결정 이력은 `project_log.md`를 본다.
- 구조 리팩토링 후보와 트리거는 `docs/REFACTOR_PLAN.md`를 본다.

## Current milestone focus
- Calculator series reset Step 1~5는 실행 완료 상태다.
- 기존 ISO 파일 내부 부분 cleanup 누적은 중단 (037~043 같은 미세 cleanup 사이클은 종료)
- 새 ISO 16358 calculator는 CSPF/HSPF common standard logic만 담당한다.
- KS C 9306 / AS/NZS workbook oracle 책임은 각각 별도 calculator 파일로 분리한다.
- legacy behavior 보존 테스트는 `core/_legacy/`와 `tests/_legacy/` 또는 explicit xfail diagnostic으로 격리한다.
- production ISO common path와 AS/NZS Excel compatibility path 분리 유지
- AS/NZS historical case3 full-dump exact matching은 Z-phase. 현재 repo의 `reference_files/iso16358_test_sheet.xlsx` HSPF/CSPF snapshot exact-match는 AS/NZS compatibility calculator/fixture에서만 관리
- `app_calculator.py` / `ui/calc_window.py`는 PyQt offscreen launch smoke로 확인했고, AHRI SEER2와 EN14825 SCOP selector는 resolver-backed profile selection으로 전환했다.
- EN14825 tab은 `calculate_scop()`를 실제 호출하도록 연결되어 있다 (TOL/Tbiv/p_design_h/climate/standby 입력 포함, W → kW 변환 UI adapter).
- Calculator result envelope / ML adapter boundary는 `docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md`에 설계 완료했다.
- AHRI SEER2 input/result envelope 첫 slice는 `core/calculator_input_adapter.py` / `core/calculator_result_adapter.py`로 구현 완료. 단위 변환은 의도적으로 envelope 밖.
- Calculator core / region config 가드는 banned-key 및 adapter-owned term 가드 (`tests/test_calculator_schema_boundaries.py`)로 강화 완료.
- ISO16358-2 HSPF official exact 16-case golden은 원문 audit + 099 `-7_ext` default factor fix 이후 기준으로 정리되어 16/16 모두 pass한다. `XFAIL_CASE_IDS`는 빈 frozenset이다 (100 참고).
- ISO16358-2 HSPF official exact fixture는 official data (input / description / expected)만 남기도록 정리되어 있고, current-implementation status는 `tests/test_iso16358_hspf_official_exact_golden.py`의 `XFAIL_CASE_IDS` constant로 분리된다 (현재 비어 있음).
- Hong Kong HSPF는 core/config/test + profile/dispatcher smoke까지 완료했다. `core/calculator_profiles.py`에 `hong_kong_hspf` profile이 `hong_kong_cspf`와 같은 `data/region_configs/hong_kong.json`을 공유하면서 `metric=HSPF` / `mode=heating`으로 등록되어 있고, dispatcher는 `calculator_id=iso16358` 기존 경로로 `ISO16358Calculator.calculate_hspf`를 호출할 수 있다 (103 참고). UI surface는 아직 만들지 않았다.
- AHRI / EN14825 horizontal table-input UI와 ML W ↔ calculator-native unit boundary는 `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`에 설계 완료. 첫 구현 slice는 AHRI SEER2 table input 한 곳으로 제한한다.
- ML W ↔ AHRI SEER2 Btu/h capacity 변환은 `core/calculator_unit_adapter.py`로 분리했고, PredictedPointsEnvelope → CalculatorInputEnvelope → CalculatorResultEnvelope → RankingCandidateEnvelope end-to-end smoke (`tests/test_calculator_envelope_chain.py`)가 chain 무결성을 보호한다.
- 전역 UI/UX active SSOT는 `docs/ui_ux/`로 도입 완료. Root는 `docs/ui_ux/00_UI_UX_SYSTEM.md`, table UX contract는 `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`, PyQt 구현 adapter는 `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md`. 기존 `docs/ui/SPREADSHEET_TABLE_CONTRACT.md`는 삭제했고 legacy 전문은 `docs/ui_ux/_source/SPREADSHEET_TABLE_CONTRACT_legacy_pyqt.md`에만 history로 남긴다. 전역 PyQt spreadsheet-like table UI는 이 새 SSOT를 단일 owner로 한다. 공통 component는 `ui/spreadsheet_table.py` (QAbstractTableModel 기반 model, QTableView 기반 `SpreadsheetTableView`, TSV copy/paste, clear, undo, invalid numeric, point-dict 변환)와 `tests/test_spreadsheet_table_model.py` / `tests/test_spreadsheet_table_view.py` smoke harness로 시작했다.
- AHRI SEER2 입력은 horizontal spreadsheet table (`SpreadsheetTableView` + `make_ahri_seer2_table_model()`)로 전환했다. 5 cooling point (A_Full/B_Full/B_Low/E_Int/F_Low) × 2 row (능력 [Btu/h] / 전력 [W]). `calculate_ahri()`와 HSPF2 v3 A2 derivation 모두 동일 table에서 값을 읽는다. Cd_low/Cd_full만 기존 compact form.
- AHRI HSPF2 v3 입력도 horizontal spreadsheet table (`SpreadsheetTableView` + `make_ahri_hspf2_table_model()`)로 전환했다. 7 heating point (H01/H11/H12/H1N/H22/H2Int/H32) × 2 row (능력 [Btu/h] / 전력 [W]). `_build_hspf2_v3_input()`는 A2를 SEER2 table에서, H01~H32을 HSPF2 table에서 읽는다. t_off/t_on/defrost_t_test_minutes/defrost_t_max_minutes만 기존 compact form (`input_widgets_hspf2`)으로 유지.
- EN14825 SEER / SCOP 입력도 horizontal spreadsheet table (`SpreadsheetTableView` + `make_en14825_seer_table_model()` / `make_en14825_scop_table_model()`)로 전환했다. UI 입력 단위는 W로 통일하고, `calculate_en()`이 EN core (`calculate_seer` / `calculate_scop`) 호출 직전 W → kW (1/1000) 변환을 수행한다. `core/calculator_en14825.py`와 `data/region_configs/en14825_scop.json`은 kW/core 기준을 그대로 유지한다. SCOP는 Average / Warmer / Colder checkbox로 다중 선택 가능하고, 선택된 climate별 table/card (각 climate은 자체 A/B/C/D/TOL/Tbiv table + p_design_h_w + Tbiv/TOL temp prefill) 를 가진다. 기본 prefill은 Average=Tbiv -10, TOL -11 / Warmer=Tbiv 2, TOL -11 / Colder=Tbiv -15, TOL -22. 공통 standby form (`p_to_w`/`p_sb_w`/`p_ck_w`/`p_off_w`) 도 W 입력으로 통일하고 기본값 0.0 prefill.

## Near-term execution order
1. Step 1~5 완료 상태를 유지하고, 새 ISO / KS / ASNZS boundary를 깨는 후속 변경을 피한다.
2. ISO16358-2 HSPF official exact 16-case mismatch는 hold 상태이며 repo immediate next action에서 제외한다. 사용자 외부 분석 결과 대기 중이고, repo 계산식 / expected / xfail / fixture 수정은 보류한다. 분석 결과가 들어오면 그때 repo 후속 작업을 다시 정한다.
3. Repo 다음 순서는 다음 sequence로 둔다:
   1. Calculator UI/UX audit against new SSOT (`docs/ui_ux/`) — **완료** (107 참고).
   2. Calculator UI design token foundation — **완료** (108 참고). `ui/theme.py`가 `02_DESIGN_TOKENS_AND_LAYOUT.md` token name을 보수적으로 캡쳐 (PyQt 없이 import 가능), error border 한 곳에 PoC 적용. 색/레이아웃 변경 없음.
   3. EN14825 tab layout polish — **완료** (109 참고). standby form을 EN tab 최상단 compact horizontal row로 이동, single-input row width 제한 (p_design_c / p_design_h / Tbiv / TOL), SCOP climate card 보조 form을 horizontal row로 정렬. 108 token foundation의 `theme_spacing("space.section"/"space.row")`를 사용. calculate_en core / W→kW 변환 / input key / default 0.0은 그대로 유지.
   4. Calculator auto-calculate behavior alignment — micro-design **완료** (110 참고, `docs/designs/2026-05-22-calculator-action-model-alignment.md`). 결정: **Option A — Auto-calc unified**. Slice α (`SpreadsheetTableModel.values_changed` signal) **완료** (111 참고).
   4a. Calculator UI module boundary plan — **완료** (113 참고, `docs/designs/2026-05-22-calculator-ui-module-boundary.md`). `ui/calc_window.py` shell만 유지하고 EN/AHRI tab + 공통 helper (`ui/calculator_errors.py`, `ui/calculator_recompute.py`, `ui/calculator_result_panel.py`)를 별도 module로 분리하는 순서를 확정. 다음 slice는 ε → ζ → η → β → γ → δ. (recommended next action: slice ε — `ui/calculator_errors.py` 추출)
   4b. Slice ε `ui/calculator_errors.py` 추출 — **완료** (115 참고). `InputValidationError`, `parse_number`, `bind_error_reset`, `apply_error_style`, `clear_error_style`, `get_float_val`을 신규 module로 이동. `calc_window.py`는 import alias 유지, `_get_float_val` 인스턴스 메서드는 새 helper를 호출하는 thin wrapper. 동작 변경 없음.
   4y. **Project-wide new code quality gate** (119 참고). UI 전용 규칙이 아니라 `core/`, `ui/`, `ui_tk/`, `scripts/`, `tools/`, ML adapter, packaging probe 등 새 script/module/feature 전반에 적용되는 boundary 원칙을 `AGENTS.md` New Code Quality Gate / `AGENT_TASK_ROUTER.md` Shared Guardrails / `docs/architecture/project_architecture.md` §6에 추가했다. 자동 guard `tools/check_code_structure.py` (layer import 금지, app entrypoint thin, ui_tk multi-책임 anti-pattern, LOC/class soft limit + 기존 large 파일 allowlist) 와 `tests/test_code_structure_guard.py` (20 case + CLI smoke) 추가. 현재 repo 실행 결과 `code structure guard: OK (no findings)`. 코드 구조에 영향을 주는 작업에서 `python3 -B tools/check_code_structure.py` 결과를 최종 보고에 포함한다. CI / pre-commit hook은 이번 작업에서 추가하지 않는다.

   4w. **Legacy / unused script cleanup audit / C2 archive README status header** (121, 127 참고). repo 안의 legacy / unused / spike / debug / one-off script 후보를 read-only로 inventory했다. 즉시 삭제 / 이동 / rename 대상 없음 — 모든 후보는 후속 slice (C1 docs/guides cross-link, C2 `docs/archive/iso16358_initial_reverse_engineering/README.md` status header, C3 `tests/_legacy` 명명 audit, C4 `core/_legacy/calculator_iso16358_legacy.py` decommission 조건 문서화, C5 119 allowlist 재검토) 로 분리했다. C2는 완료: `docs/archive/iso16358_initial_reverse_engineering/`는 historical archive / initial reverse-engineering snapshot이며 runtime/import/test/calculator path 대상이 아님을 README 상단 status header로 명확히 했다. 삭제 / 이동 / rename은 수행하지 않았다.

   4u. **PyQt macOS fatal-abort environment audit / known-bad skip patch** (128~129 참고). macOS 15.7.3 arm64 + Python 3.14.4 + PyQt5 5.15.11 / Qt 5.15.14에서 PyQt import와 offscreen `QApplication` 생성은 통과하지만, pytest 실행 중 일부 `QTableView` subclass 생성 경로가 native SIGABRT로 abort된다. 129에서 `tests/helpers/pyqt_env.py`를 추가하고 4개 PyQt widget test 파일에 known-bad macOS Python 3.14 + PyQt5 skip guard를 적용했다. PyQt test는 삭제하지 않고, Windows / Linux / Python 3.12·3.11 / 향후 검증된 host에서는 계속 실행 가능하게 유지한다. manual PyQt ignore 없는 전체 suite는 **579 passed, 59 skipped, 19 xfailed**로 통과했다.

   4t. **Tkinter ISO section pure helper cleanup / PyQt test support matrix** (130~131 참고). `ui_tk/sections/iso_cspf_section.py`와 `ui_tk/sections/iso_hspf_section.py`에 남아 있던 input dict 구성과 result text formatting을 `ui_tk/sections/iso16358_helpers.py`로 분리했다. Section class는 widget 생성, `NumericEntryRow.get_value()`, `resolve_profile_id`, `create_calculator_for_profile`, calculator call, result callback orchestration만 유지한다. helper는 Tkinter/PyQt를 import하지 않고 pure tests로 보호한다. Hong Kong smoke는 CSPF **4.939**, HSPF **3.643** 유지. 131에서 `docs/guides/pyqt_test_support_matrix.md`를 추가해 macOS Python 3.14 + PyQt5 known-bad skip 정책, PyQt test 보존 이유, Python 3.12/3.11 및 Windows validation pending 상태를 문서화했다. 131 문서는 중간 안정화 문서로 유지하되 PyQt calculator-only UI를 계속 고도화하는 것은 더 이상 목표가 아니다. PyQt Predict/Train 앱은 유지 후보이고, PyQt calculator-only 경로는 retirement audit 후보로 본다. manual PyQt ignore 없는 전체 suite는 **585 passed, 59 skipped, 19 xfailed**로 통과했다. 다음 recommended action은 (1) **PyQt calculator-only retirement audit** (read-only inventory, 본 lifecycle 작업에서는 실행하지 않음), (2) Windows host 확보 시 PyInstaller size measurement, (3) 필요 시 Python 3.12/3.11 venv PyQt support validation, (4) 필요 시 Tkinter next metric/standard extension design, (5) ML / inverse-search 복귀 준비.

   4s. **PyQt calculator-only retirement audit** (154 참고). Runtime import inventory에서 `app_calculator.py` → `ui/calc_window.py` → `ui/calculators_2point.py` / `ui/calculator_errors.py`는 calculator-only retirement 후보로 분리되었고, `app_predict.py` / `app_train.py` 및 `ui/predict_window.py` / `ui/train_window.py` / `ui/base_model.py` / `ui/base_view.py`는 유지 후보로 확인했다. `ui/spreadsheet_table.py`와 `ui/theme.py`는 현재 runtime consumer가 calculator 경로뿐이지만 active UI/UX SSOT와 테스트 자산이 범용 PyQt utility로 다루므로 별도 retention decision 전에는 삭제 후보로 확정하지 않는다. 다음 실제 retirement action은 calculator-only direct tests를 먼저 별도 slice에서 retire하거나 quarantine하고, shared utility tests와 PyQt environment guard는 유지 판단을 분리하는 것이다. source 삭제와 active docs 갱신은 그 뒤의 독립 slice로 둔다. **PyQt calculator-only source retirement는 Tkinter final UX vertical slice (slice 3) 검증 이후로 보류한다.**

   4r. **PyQt calculator-only direct test retirement** (155 참고). `tests/test_app_calculator_ui_smoke.py`, `tests/test_iso16358_result_table_copy_tsv.py`, `tests/test_calculator_errors.py`는 각각 `ui/calc_window.py`, `ui/calculators_2point.py`, `ui/calculator_errors.py`에 직접 묶인 calculator-only 보호면으로 확인되어 retire했다. Mixed/shared 후보인 `tests/test_iso16358_table_excel_like_behavior.py`, `tests/test_spreadsheet_table_model.py`, `tests/test_spreadsheet_table_view.py`, `tests/test_ui_theme_tokens.py`와 PyQt environment guard는 유지한다. 다음 recommended action은 (1) `ui/spreadsheet_table.py` / `ui/theme.py` 및 남은 shared tests retention decision, (2) PyQt calculator-only source retirement, (3) active docs update, (4) PyQt support matrix guide update/retirement 판단 순이다. **PyQt calculator-only source retirement는 Tkinter final UX vertical slice (slice 3) 검증 이후로 보류한다.**

   4q. **Shared PyQt utility retention decision** (156 참고). `ui/spreadsheet_table.py`와 `ui/theme.py`는 현재 Predict/Train·Tkinter runtime consumer가 없고 calculator path만 import하지만, active UI/UX SSOT와 독립 regression tests가 future reusable PyQt utility/token foundation으로 보존한다. 따라서 calculator-only source와 함께 삭제하지 않고 **quarantine/hold**로 유지한다. `tests/test_spreadsheet_table_model.py`, `tests/test_spreadsheet_table_view.py`, `tests/test_ui_theme_tokens.py` 및 `tests/helpers/pyqt_env.py` / `tests/test_pyqt_environment_guard.py`는 유지한다. `tests/test_iso16358_table_excel_like_behavior.py`는 calculator model과 shared helper가 섞인 mixed test이므로 source retirement 전에 split-or-retire 판단 slice를 먼저 수행한다. `docs/guides/pyqt_test_support_matrix.md`는 남은 guarded widget tests 때문에 유지하되, 삭제된 direct tests와 현재 baseline을 반영하는 narrow/update는 별도 docs slice로 둔다. **PyQt calculator-only source retirement는 Tkinter final UX vertical slice (slice 3) 검증 이후로 보류한다.**

   4p. **Project-wide visual design architecture adoption** (158 참고). `docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md`를 `predictor_v3` visual SSOT로 추가했다. Figma-inspired source는 reference로만 사용하고, neutral-first chrome과 table-first philosophy를 PyQt Predict/Train 및 Tkinter Calculator에 공통 적용한다. 기존 header/cell/result/status color는 폐기하지 않고 semantic role inventory/token foundation 대상으로 유지한다. 다음 recommended action 순서:
     1. **Existing PyQt visual/color/token inventory** — Predictor/Trainer/Calculator remnants의 header color, condition-based cell color, status color, inline style을 코드 수정 없이 inventory/report한다.
     2. **Toolkit visual token foundation** — PyQt/Tkinter 공통 semantic token vocabulary를 코드 또는 문서 adoption point와 연결한다.
     3. **Tkinter table/grid input foundation**.
     4. **Tkinter auto-calc debounce/helper foundation**.
     5. **ISO Hong Kong CSPF/HSPF table + auto-calc vertical slice**.
     - **PyQt calculator-only source retirement**는 Tkinter final UX vertical slice 검증 이후까지 보류한다.
     - **Windows PyInstaller size measurement**는 Windows host available 시점까지 pending으로 유지한다.

   4o. **Toolkit visual token foundation** (160 참고). `ui_common/visual_tokens.py`에 PyQt/Tkinter import가 없는 project-wide semantic color/spacing/radius/font registry와 lookup helper를 추가했다. 현재 checkout의 159 report는 source reference tracking이며 별도 Existing PyQt visual/color/token inventory report는 확인되지 않았으므로, 158 visual architecture와 현재 `ui/theme.py`/table/Tkinter source inventory를 baseline evidence로 사용했다. 기존 `ui/theme.py`, widget styling, header/cell/result/status color에는 적용하거나 변경하지 않았다. 다음 recommended action 순서:
     1. **Tkinter table/grid input foundation**.
     2. **Tkinter auto-calc debounce/helper foundation**.
     3. **ISO Hong Kong CSPF/HSPF table + auto-calc vertical slice**.
     4. **macOS manual UX smoke**.
     5. **Windows PyInstaller size measurement** — Windows host available 시.
     - **PyQt calculator-only source retirement**는 Tkinter final UX vertical slice 검증 이후까지 보류한다.

   4n. **Tkinter table/grid input foundation** (161 참고). `ui_tk/table_grid_model.py`에 toolkit-free row/column schema, text storage, numeric parsing, missing/invalid state, snapshot helper를 추가하고 `ui_tk/table_grid.py`에 `Frame` + header/row label/`Entry` grid adapter와 변경 시에만 발생하는 `values_changed` callback hook을 추가했다. 기존 `IsoCspfSection` / `IsoHspfSection`, `NumericEntryRow`, result panel, core 호출, auto-calc, visual token styling은 변경하거나 연결하지 않았다. 다음 recommended action 순서:
     1. **Tkinter auto-calc debounce/helper foundation**.
     2. **ISO Hong Kong CSPF/HSPF table + auto-calc vertical slice**.
     3. **macOS manual UX smoke**.
     4. **Windows PyInstaller size measurement** — Windows host available 시.
     - **PyQt calculator-only source retirement**는 Tkinter final UX vertical slice 검증 이후까지 보류한다.

   4m. **Tkinter ISO Hong Kong CSPF/HSPF table + auto-calc vertical slice** (162 참고). `ui_tk/auto_calc.py`의 `after` 기반 debounce helper를 추가하고, Hong Kong CSPF/HSPF section을 `TableGrid` 입력과 자동 계산으로 연결했다. 계산 버튼은 제거했으며, result panel은 metric별 최신 결과만 합쳐 표시해 자동 계산 이력을 누적하지 않는다. core/profile/dispatcher 및 visual token styling은 변경하지 않았다. 다음 recommended action 순서:
     1. **macOS manual UX smoke**.
     2. **Windows PyInstaller size measurement** — Windows host available 시.
     3. **Visual token/style adapter adoption** — 필요 시.
     4. **Tkinter standard/region expansion** — 필요 시.
     - **PyQt calculator-only source retirement**는 Windows packaging size measurement 또는 vertical slice 사용성 판단 이후까지 계속 보류한다.

   4l. **Tkinter ISO Hong Kong input/output UI correction** (163 참고). CSPF/HSPF 입력을 각 metric별 단일 시험표(`능력 [W]`/`전력 [W]` × rating/full/half)로 정리하고, result 영역을 kWh 단위 summary card로 바꾸어 `None`/raw long-float 표시를 제거했다. CSPF/HSPF auto-calc와 기존 core/profile/dispatcher 경로, 기본 smoke `4.939`/`3.643`, copy/clear는 유지했다. 다음 recommended action 순서:
     1. **macOS manual UX smoke**.
     2. **Tkinter visual spacing/style adapter adoption** — 필요 시.
     3. **Windows PyInstaller size measurement** — Windows host available 시.
     4. **Tkinter standard/region expansion** — 필요 시.
     - **PyQt calculator-only source retirement**는 계속 보류한다.

   4k. **Project-wide input matrix and result surface rules adoption** (164 참고). `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`를 active UI/UX SSOT로 추가해 반복 측정/조건/비교 입력은 행/열 header가 있는 matrix surface로 정규화하고, primary result는 raw text dump 대신 summary surface로 표시하도록 확정했다. 163 ISO Hong Kong correction은 이 rule의 첫 concrete application이며, graph/detail surface는 lightweight follow-up design으로 보류한다. 다음 recommended action 순서:
     1. **Lifecycle summary/archive maintenance**.
     2. **macOS Tkinter manual UX smoke**.
     3. **Tkinter matrix/result visual surface refinement** — 필요 시.
     4. **Lightweight graph/detail surface design** — 필요 시.
     5. **Windows PyInstaller size measurement** — Windows host available 시.
     6. **Tkinter standard/region expansion** — 필요 시.
     - **PyQt calculator-only source retirement**는 계속 보류한다.
     - **Large graph dependency** (`matplotlib` 등)는 Windows packaging size 판단 전까지 도입하지 않는다.

   4j. **PyQt retirement / Tkinter UI matrix-rules lifecycle summary** (165 참고). `result_reports/summaries/165_summary-pyqt-retirement-tkinter-ui-matrix-rules.md`로 154~164 active report를 압축하고 covered reports를 archive로 이동했다. 163 화면은 matrix input/summary surface의 first implementation이지만 사용자 확인 결과 visible refinement가 더 필요하며, 164는 rule adoption-only이므로 실행 화면을 변경하지 않았다. 다음 recommended action 순서:
     1. **Tkinter matrix/result visual surface refinement implementation**.
     2. **macOS Tkinter manual UX smoke** — refinement 이후.
     3. **Lightweight graph/detail surface design** — 필요 시.
     4. **Windows PyInstaller size measurement** — Windows host available 시.
     5. **Tkinter standard/region expansion** — 필요 시.
     6. **PyQt calculator source retirement 재검토** — Tkinter UX/packaging 판단 이후.
     - **PyQt calculator-only source retirement**는 계속 보류한다.
     - **Large graph dependency** (`matplotlib` 등)는 Windows packaging size 판단 전까지 도입하지 않는다.

   4i. **Tkinter matrix/result visual surface refinement implementation** (166 참고). ISO Hong Kong CSPF/HSPF 입력은 header/editable/static cell을 구분하는 bordered matrix surface로, 결과는 header/value/status를 구분하는 compact bordered summary table로 렌더링한다. `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`를 visible widget layer에 적용했으며 auto-calc, copy/clear, core/profile/dispatcher, 기본 smoke `4.939`/`3.643`은 유지한다. 다음 recommended action 순서:
     1. **Tkinter ISO HK layout correction** — 정격 표기치 분리, CSPF 입력→CSPF 결과→HSPF 입력→HSPF 결과 순서, 하단 결과 복사/지우기 제거, 숫자 가운데 정렬, 입력 오류 시 회색 block 문제 수정.
     2. **Tkinter Excel-like table behavior** — selection, TSV copy/paste, Delete/clear, undo, Tab/Enter navigation.
     3. **Tkinter graph/detail surface design** — PyQt reference를 lightweight 방식으로 재설계; 큰 dependency는 packaging 판단 전 보류.
     4. **Tkinter standard/region expansion plan** — ISO/ISEER 2점식, SASO T3, EN 14825, AHRI 210/240 순서를 판단.
     5. **Windows PyInstaller size measurement** — Windows host available 시.
     6. **PyQt calculator source retirement 재검토** — Tkinter UX, 기능 migration, packaging 판단 이후.
     - **Visual token full wiring**과 **large graph dependency** (`matplotlib` 등)는 본 refinement 범위가 아니다.

   4h. **PyQt calculator reference feature migration contract** (167 참고). `result_reports/archive/154_pyqt-calculator-retirement-audit.md`와 `result_reports/summaries/165_summary-pyqt-retirement-tkinter-ui-matrix-rules.md`의 기존 분류를 `docs/designs/2026-05-24-pyqt-calculator-reference-feature-migration-contract.md`에 migration requirement로 재정렬한다. `app_calculator.py`는 thin entrypoint이며 `ui/calc_window.py` / `ui/calculators_2point.py`의 ISO/ISEER·SASO·EN·AHRI, table behavior, summary/detail/graph, validation, batch surface가 reference 기능군임을 기록한다. 새 parity audit나 retirement 승인이 아니며 Predict/Train과 shared PyQt utility는 hold/retention 범위로 분리한다. 다음 recommended action 순서는 4i의 갱신된 1~6 순서를 따른다.

   4g. **Tkinter ISO Hong Kong layout correction** (168 참고). CSPF/HSPF마다 capacity-only `정격 표기치` matrix를 시험 입력표와 분리하고, 시험 입력표는 full/half × 능력/전력 matrix만 유지한다. 각 결과 table은 해당 입력 section 바로 아래 표시되어 `CSPF 입력 → CSPF 결과 → HSPF 입력 → HSPF 결과` 순서를 이루며, 하단 공통 복사/지우기 버튼은 표시하지 않는다. numeric entry 가운데 정렬과 invalid-input status-only surface를 적용했으며 auto-calc, core/profile/dispatcher 경로, 기본 smoke `4.939`/`3.643`은 유지한다. 다음 recommended action 순서:
     1. **Tkinter Excel-like table behavior** — selection, TSV copy/paste, Delete/clear, undo, Tab/Enter navigation.
     2. **Tkinter graph/detail surface design** — PyQt reference를 lightweight 방식으로 재설계; 큰 dependency는 packaging 판단 전 보류.
     3. **Tkinter standard/region expansion plan** — ISO/ISEER 2점식, SASO T3, EN 14825, AHRI 210/240 순서를 판단.
     4. **Windows PyInstaller size measurement** — Windows host available 시.
     5. **PyQt calculator source retirement 재검토** — Tkinter UX, 기능 migration, packaging 판단 이후.
     - **Excel-like behavior**, **graph/detail**, **packaging**, **PyQt retirement**는 task 168 구현 범위가 아니다.

   4g-a. **Tkinter table/card width alignment refinement** (169 참고). ISO Hong Kong CSPF/HSPF section의 `정격 표기치`, 시험 입력, compact 결과 표에 local content-width/padding contract를 적용해 같은 left edge와 visual width, 일관된 block spacing으로 정렬한다. auto-calc, result formatting, invalid status-only surface, core/profile/dispatcher, 기본 smoke `4.939`/`3.643`은 변경하지 않는다. 다음 recommended action 순서:
     1. **Tkinter Excel-like table behavior** — selection, TSV copy/paste, Delete/clear, undo, Tab/Enter navigation.
     2. **Tkinter Canvas graph/detail surface design** — PyQt reference를 lightweight Canvas 방향으로 재설계; `matplotlib`은 packaging size 판단 전 도입하지 않는다.
     3. **Tkinter standard/region expansion plan** — ISO/ISEER 2점식, SASO T3, EN 14825, AHRI 210/240 순서를 판단.
     4. **Windows PyInstaller size measurement** — Windows host available 시.
     5. **PyQt calculator source retirement 재검토** — Tkinter UX, 기능 migration, packaging 판단 이후.
     - **Excel-like behavior**, **Canvas graph/detail 구현**, **packaging**, **PyQt retirement**는 task 169 구현 범위가 아니다.

   4g-b. **Tkinter responsive table architecture alignment** (170 참고). Task 169의 fixed pixel content-width 방식은 문자/글꼴 기반 초기 sizing과 parent-driven `ew` stretch 방식으로 대체한다. `MetricInputTable`은 row/column/cell/editable-entry metadata를 제공해 후속 interaction controller가 register 가능한 기반을 가지며, CSPF/HSPF rated/trial/result surface는 창 폭 변경 시 함께 늘어나면서 정렬을 유지한다. auto-calc, result formatting, invalid status-only surface, core/profile/dispatcher, 기본 smoke `4.939`/`3.643`은 유지한다. 다음 recommended action 순서:
     1. **Tkinter Excel-like table behavior controller** — selection, TSV copy/paste, Delete/clear, undo, Tab/Enter navigation을 metadata registry 위에 연결.
     2. **Tkinter Canvas graph/detail surface design** — lightweight Canvas 방향으로 설계; `matplotlib`은 packaging size 판단 전 도입하지 않는다.
     3. **Tkinter standard/region expansion plan** — ISO/ISEER 2점식, SASO T3, EN 14825, AHRI 210/240 순서를 판단.
     4. **Windows PyInstaller size measurement** — Windows host available 시.
     5. **PyQt calculator source retirement 재검토** — Tkinter UX, 기능 migration, packaging 판단 이후.
     - **Excel-like behavior 구현**, **Canvas graph/detail 구현**, **packaging**, **PyQt retirement**는 task 170 구현 범위가 아니다.

   4g-c. **Portable UI visual value ownership cleanup** (171 참고). Tkinter table/result component의 concrete visual value는 `ui_tk/layout_constants.py`가 소유하고 component는 이를 소비하는 boundary로 정리한다. `docs/ui_ux`의 portable adoption kit는 common docs뿐 아니라 project binding, token owner, component skeleton, adapter와 최소 ownership guard를 함께 요구한다. responsive metadata/auto-calc/result formatting은 변경하지 않는다. 다음 recommended action 순서:
     1. **Tkinter Excel-like table behavior controller** — selection, TSV copy/paste, Delete/clear, undo, Tab/Enter navigation을 metadata registry 위에 연결.
     2. **Tkinter Canvas graph/detail surface design** — lightweight Canvas 방향으로 설계; `matplotlib`은 packaging size 판단 전 도입하지 않는다.
     3. **Tkinter standard/region expansion plan** — ISO/ISEER 2점식, SASO T3, EN 14825, AHRI 210/240 순서를 판단.
     4. **Windows PyInstaller size measurement** — Windows host available 시.
     5. **PyQt calculator source retirement 재검토** — Tkinter UX, 기능 migration, packaging 판단 이후.
     - **Excel-like behavior 구현**, **Canvas graph/detail 구현**, **packaging**, **PyQt retirement**는 task 171 구현 범위가 아니다.

   4g-d. **Tkinter Excel-like table behavior controller** (172 참고). ISO Hong Kong CSPF/HSPF rated/trial `MetricInputTable`에 별도 `ExcelLikeTableController`를 attach하여 rectangular selection, TSV copy/paste, Delete/Backspace clear, grouped undo, Tab/Enter navigation, click-then-type replacement를 제공한다. Table은 metadata와 notify-once batch mutation만 제공하고 interaction logic을 소유하지 않는다. Numeric TSV paste는 partial auto-calc 결과를 피하기 위해 atomic validation 후 적용하며, visual state 값은 `ui_tk/layout_constants.py` owner boundary를 유지한다. 기본 smoke `4.939`/`3.643`과 invalid status-only surface는 유지한다. 다음 recommended action 순서:
      1. **macOS Tkinter manual UX smoke** — controller attach 이후.
      2. **Tkinter Canvas graph/detail surface design** — lightweight Canvas 방향으로 설계; `matplotlib`은 packaging size 판단 전 도입하지 않는다.
      3. **Tkinter standard/region expansion plan** — ISO/ISEER 2점식, SASO T3, EN 14825, AHRI 210/240 순서를 판단.
      4. **Windows PyInstaller size measurement** — Windows host available 시.
      5. **PyQt calculator source retirement 재검토** — Tkinter UX, 기능 migration, packaging 판단 이후.
      - **Canvas graph/detail 구현**, **standard/region 확장**, **packaging**, **PyQt retirement**는 task 172 구현 범위가 아니다.

   4g-e. **Tkinter Excel-like table UX smoke fix** (173 참고). Task 172 controller attach 이후 macOS 수동 smoke에서 click selection 시 typing caret 즉시 노출, arrow key 이동 부재, keypad Enter 미동작, selection 취소 후 active 표시 잔존, macOS Command shortcut 미동작 등 Excel-like 동작 차이가 확인되었다. `ExcelLikeTableController`에 insertontime 기반 caret 제어, arrow key navigation, KP_Enter binding, Esc/blank click/outside focus selection clear, Command/Control 대소문자 방어를 추가했다. 기존 Tab/Enter 이동 후 첫 입력 replace 동작은 유지하고 regression test로 보호한다. 다음 recommended action 순서:
      1. **macOS Tkinter manual UX smoke** — controller patch 이후 다시 실행.
      2. **Tkinter Canvas graph/detail surface design** — lightweight Canvas 방향으로 설계; `matplotlib`은 packaging size 판단 전 도입하지 않는다.
      3. **Tkinter standard/region expansion plan** — ISO/ISEER 2점식, SASO T3, EN 14825, AHRI 210/240 순서를 판단.
      4. **Windows PyInstaller size measurement** — Windows host available 시.
      5. **PyQt calculator source retirement 재검토** — Tkinter UX, 기능 migration, packaging 판단 이후.
      - **Canvas graph/detail 구현**, **standard/region 확장**, **packaging**, **PyQt retirement**는 task 173 구현 범위가 아니다.

    4g-f. **Tkinter Excel-like table selection clear fix** (174 참고). Task 173 이후 macOS 수동 smoke에서 다른 table/card 클릭 시 이전 active highlight가 잔존하고, blank area 클릭 가능 영역이 header/static cell frame 안의 Label까지 포함하지 않아 너무 좁으며, `_internal_focus_move` flag가 외부 focus-out clear를 잘못 억제할 수 있는 경합이 확인되었다. `ExcelLikeTableController`에 class-level active controller 추적(새 select 시 이전 controller 자동 clear), header/row_header/static cell 및 모든 자손 widget에 recursive `<Button-1>` binding, `table_frame` 자체 blank gap 클릭 handler, `_internal_focus_move`를 `after_idle`로 reset하는 안정화를 추가했다. 기존 Tab/Enter/arrow navigation, click caret 숨김, 첫 입력 replace는 유지한다. 다음 recommended action 순서:
      1. **macOS Tkinter manual UX smoke** — controller patch 이후 다시 실행.
      2. **Tkinter Canvas graph/detail surface design** — lightweight Canvas 방향으로 설계; `matplotlib`은 packaging size 판단 전 도입하지 않는다.
      3. **Tkinter standard/region expansion plan** — ISO/ISEER 2점식, SASO T3, EN 14825, AHRI 210/240 순서를 판단.
      4. **Windows PyInstaller size measurement** — Windows host available 시.
      5. **PyQt calculator source retirement 재검토** — Tkinter UX, 기능 migration, packaging 판단 이후.
      - **Canvas graph/detail 구현**, **standard/region 확장**, **packaging**, **PyQt retirement**는 task 174 구현 범위가 아니다.

   4g-g. **Excel-like table selection/edit state machine contract** (175-a 참고). 공통 spreadsheet-like table UX contract에 selection mode와 edit mode를 구분하고, first printable key whole-cell replace, same-cell second click/double click/F2 edit-entry, mode별 Arrow/Delete/Backspace/Esc/commit 동작을 toolkit-agnostic state machine으로 확정했다. Tkinter/PyQt adapter와 Tkinter manual smoke checklist는 이 공통 규칙을 참조하도록 연결하며, predictor_v3 numeric atomic paste는 paste-specific deviation으로 유지한다. 다음 recommended action 순서:
      1. **Tkinter Excel-like edit mode implementation** — same-cell second click/double click/F2 진입, caret-visible partial edit, mode별 key behavior를 controller에 구현하고 검증한다.
      2. **macOS Tkinter manual UX smoke** — edit mode 구현 이후 state machine 확인 항목을 실행한다.
      3. **Tkinter Canvas graph/detail surface design** — lightweight Canvas 방향으로 설계; `matplotlib`은 packaging size 판단 전 도입하지 않는다.
      4. **Tkinter standard/region expansion plan** — ISO/ISEER 2점식, SASO T3, EN 14825, AHRI 210/240 순서를 판단.
      5. **Windows PyInstaller size measurement** — Windows host available 시.
      6. **PyQt calculator source retirement 재검토** — Tkinter UX, 기능 migration, packaging 판단 이후.
      - **실제 Python 구현**, **Canvas graph/detail 구현**, **standard/region 확장**, **packaging**, **PyQt retirement**는 task 175-a 범위가 아니다.

   4g-h. **Tkinter Excel-like edit mode implementation** (176 참고). `ExcelLikeTableController`에 selection/edit mode 상태와 edit snapshot을 추가해 첫 클릭 selection mode, first printable key whole-cell replace, same-cell second click/double click/F2 caret-visible partial edit를 구현했다. Edit mode에서 printable/Arrow/Delete/Backspace는 native text edit로 남기고, Enter/Tab/KP_Enter는 snapshot commit 후 navigation, Esc는 snapshot restore 후 selection mode 유지, external focus-out은 commit 후 selection clear로 정렬했다. Undo는 edit 시작 전 snapshot 기준으로 commit 시 한 번만 기록하며 paste atomic validation과 cross-table selection clear는 유지한다. 다음 recommended action 순서:
      1. **macOS Tkinter manual UX smoke** — 구현된 state machine 확인 항목을 실제 앱에서 실행한다.
      2. **Tkinter Canvas graph/detail surface design** — lightweight Canvas 방향으로 설계; `matplotlib`은 packaging size 판단 전 도입하지 않는다.
      3. **Tkinter standard/region expansion plan** — ISO/ISEER 2점식, SASO T3, EN 14825, AHRI 210/240 순서를 판단.
      4. **Windows PyInstaller size measurement** — Windows host available 시.
      5. **PyQt calculator source retirement 재검토** — Tkinter UX, 기능 migration, packaging 판단 이후.
      - **Canvas graph/detail 구현**, **standard/region 확장**, **packaging**, **PyQt retirement**, **Forest-ttk-theme/visual theme 검토**는 task 176 범위가 아니다.

   4g-i. **Tkinter edit cross-table commit and window centering** (177 참고). macOS manual smoke에서 edit mode 중 다른 table/card cell 클릭 시 이전 값으로 restore되는 문제와 앱 창이 화면 왼쪽 아래로 떠 title/status 일부만 보이는 문제가 확인되었다. `ExcelLikeTableController`에서 Esc cancel과 external/cross-controller clear를 분리해 Esc는 snapshot restore, focus-out 및 다른 controller click은 commit 후 selection clear로 정렬했다. `ui_tk/calculator_app.py`에는 requested size와 screen size를 기준으로 초기 창을 중앙 또는 최소 화면 안쪽에 배치하는 helper를 추가했고 `app_calculator_tk.py` thin entrypoint는 유지했다. 다음 recommended action 순서:
      1. **macOS Tkinter manual UX smoke** — cross-table edit commit, Esc cancel, focus-out commit, initial window placement를 실제 앱에서 재확인한다.
      2. **Tkinter Canvas graph/detail surface design** — lightweight Canvas 방향으로 설계; `matplotlib`은 packaging size 판단 전 도입하지 않는다.
      3. **Tkinter standard/region expansion plan** — ISO/ISEER 2점식, SASO T3, EN 14825, AHRI 210/240 순서를 판단.
      4. **Windows PyInstaller size measurement** — Windows host available 시.
      5. **PyQt calculator source retirement 재검토** — Tkinter UX, 기능 migration, packaging 판단 이후.
      - **Canvas graph/detail 구현**, **standard/region 확장**, **packaging**, **PyQt retirement**, **Forest-ttk-theme/visual theme 검토**는 task 177 범위가 아니다.

   4g-j. **Tkinter initial window size and vertical scroll** (178 참고). macOS manual smoke에서 초기 창 위치는 정상이나 콘텐츠보다 창 높이가 짧아 하단 table이 잘리고 scroll이 없어 접근할 수 없는 문제가 확인되었다. `ui_tk/calculator_app.py`는 requested size를 반영하되 screen width/height를 초과하지 않도록 초기 geometry를 cap하고 minsize를 설정한다. `ui_tk/tabs/iso16358_tab.py`는 region selector와 CSPF/HSPF section stack을 Canvas 기반 vertical scroll container 안에 렌더링해 콘텐츠가 창보다 길 때 하단 table에 접근 가능하게 했다. 다음 recommended action 순서:
      1. **macOS Tkinter manual UX smoke** — 초기 창 크기, vertical scroll/trackpad scroll, table edit/copy/paste/navigation 유지 여부를 실제 앱에서 재확인한다.
      2. **Tkinter Canvas graph/detail surface design** — lightweight Canvas 방향으로 설계; `matplotlib`은 packaging size 판단 전 도입하지 않는다.
      3. **Tkinter standard/region expansion plan** — ISO/ISEER 2점식, SASO T3, EN 14825, AHRI 210/240 순서를 판단.
      4. **Windows PyInstaller size measurement** — Windows host available 시.
      5. **PyQt calculator source retirement 재검토** — Tkinter UX, 기능 migration, packaging 판단 이후.
      - **ExcelLikeTableController 수정**, **MetricInputTable 리팩토링**, **Canvas graph/detail 구현**, **standard/region 확장**, **packaging**, **PyQt retirement**는 task 178 범위가 아니다.

   4g-k. **Workflow/tokenization guard update** (179-a 참고). Tkinter UI smoke 반복 과정에서 작은 UI micro-fix마다 WORK_PLAN/report/full-ish diff 확인이 반복되어 토큰 소모가 과도했고, task 178의 window geometry helper에 raw layout number가 shell module에 직접 들어간 문제가 확인되었다. `AGENT_TASK_ROUTER.md`에 UI smoke-loop mode와 stable checkpoint mode, diff/read budget 규칙을 추가하고, `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`에 window geometry/screen cap/minsize/margin/ratio 값은 toolkit-local layout owner constant/ratio로 둔다는 원칙을 명시했다. 다음 recommended action:
      1. **Tkinter scroll wheel and geometry tokenization implementation** — task 178의 raw geometry 값을 `ui_tk/layout_constants.py` owner constant/ratio로 이동하고 live scroll behavior를 확인한다.
      - **Python source/test 수정**, **theme 변경**, **lifecycle/archive maintenance**는 task 179-a 범위가 아니다.

   4g-l. **Tkinter calculator metric sub-tab design amendment** (179-e 참고). macOS 수동 smoke에서 ISO Hong Kong CSPF/HSPF same-view vertical stack이 창 높이/스크롤/geometry 문제를 반복적으로 일으켰다. `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md`를 amendment하여: (1) top-level standard tabs와 region selector는 유지, (2) per-region tabs와 standard-tab replacement는 여전히 rejected, (3) content density가 높은 경우 standard tab 낸부에 metric sub-tab 또는 equivalent segmented metric navigation을 허용, (4) ISO Hong Kong CSPF/HSPF는 same-view 기본이나 metric sub-tab 분리가 권장되는 amendment로 변경, (5) EN 14825 SEER/SCOP, AHRI 210/240 SEER2/HSPF2도 같은 원칙 확장, (6) graph/detail surface는 여전히 deferred. `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`에 metric navigation은 surface-shaping rule이 아닌 IA/design contract 영역임을 명시. 다음 recommended action:
      1. **ISO Hong Kong CSPF/HSPF metric sub-tab implementation** — `ui_tk/tabs/iso16358_tab.py`에 CSPF/HSPF metric sub-tab 도입 및 수동 smoke 확인.
      2. **Tkinter scroll wheel and geometry tokenization implementation** — task 178/179-b/c/d에서 확인된 geometry 문제 추가 수정.
       - **Python source/test 수정**, **theme 변경**, **lifecycle/archive maintenance**는 task 179-e 범위가 아니다.

    4g-m. **Portable window geometry rule documentation checkpoint** (184 참고). Tkinter calculator UI smoke-loop에서 확인한 window geometry / scroll container / resize 안정성 경험을 portable UI/UX rule로 문서화했다. `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md` §8에 initial geometry order of operations, separation of concerns (initial geometry / resize minsize / screen cap / scrollbar visibility), event-loop safety 원칙을 추가했다. `AGENT_TASK_ROUTER.md` §8에 window geometry / scroll container / resize handling 작업 gate를 추가했다. source/test는 수정하지 않았다. 다음 recommended action: 수동 smoke 결과를 조금 더 확인한 뒤 active report lifecycle 판단 또는 다음 UI implementation task.

    4g-n. **Tkinter shell geometry / scroll cleanup checkpoint** (185 참고). Geometry helper extraction, `ScrollableFrame` extraction, and wheel binding cleanup are complete. `Iso16358Tab` now stays focused on region selector, metric sub-tabs, and metric section rendering while shell/scroll responsibilities are separated. 다음 recommended action: **186 PyQt reference parity audit**.

    4g-o. **PyQt reference parity audit** (186 참고). PyQt/app_calculator ISO16358 reference 기능 대비 Tkinter는 Hong Kong CSPF/HSPF shell, metric sub-tabs, auto-calc, summary panel, Excel-like table behavior, window geometry/scroll foundation은 갖췄지만 ISO/ISEER 2-point, SASO T3, multi/batch, detail/trace/graph는 아직 미이식이다. 다음 recommended action: **ISO/ISEER 2-point single calculation을 별도 slice로 설계/구현**하고, SASO/multi/detail/graph는 후속 slice 후보로 유지한다.

    4g-p. **Tkinter ISO/ISEER 2-point single design** (187-a 참고). `docs/designs/2026-05-29-tkinter-iso-iseer-2point-single-design.md`에서 ISO tab 최상단 profile/mode selector를 두고 Hong Kong 모드와 `ISO / ISEER 2-point` 모드를 분리하는 방향으로 결정했다. 2-point는 새 section에서 `MetricInputTable` + `ResultPanel`을 재사용하고, Hong Kong CSPF/HSPF metric sub-tabs는 기본 모드로 유지한다. 다음 recommended action: **187-b ISO/ISEER 2-point single calculation implementation**.

    4g-q. **Tkinter ISO/ISEER 2-point single implementation** (187-b 참고). ISO tab 최상단 `계산 모드` selector에 `Hong Kong` / `ISO / ISEER 2-point`를 연결하고, 새 `IsoIseer2PointSection`에서 ISO 16358-1과 India ISEER 2-point single calculation summaries를 함께 렌더링한다. Hong Kong CSPF/HSPF metric sub-tabs, auto-calc, Excel-like table behavior, scroll/window geometry foundation은 유지했다. SASO, multi/batch, detail/trace, graph, EN/AHRI는 아직 구현하지 않았다. 다음 recommended action: **manual smoke 후 187-c visual/result refinement 필요 여부 판단**.

    4g-r. **Tkinter ISO profile selector IA correction** (187-c 참고). ISO tab selector를 `ISO 프로파일`로 정리하고 default profile을 `ISO / ISEER 2-point`로 변경했다. `Hong Kong` 선택 시 중복 `지역: Hong Kong` selector는 숨기고 기존 CSPF/HSPF metric sub-tabs와 계산 동작은 유지한다. 수동 smoke에서 default profile 열림, 전환, table/scroll/resize 모두 정상 확인되었다. SASO/multi/detail/graph/EN/AHRI는 아직 구현하지 않았다. 다음 recommended action: **Design First Gate에 따라 후속 high-impact 작업의 design slice 시작**.

    4s. **Design First Gate documentation** (188-a 참고). `AGENT_TASK_ROUTER.md`에 design slice → implementation slice 분리 gate를 추가했다. 영향 범위가 큰 작업은 구현 전에 design slice를 수행하고, 승인된 design doc 기준으로 implementation slice를 진행한다. hotfix/micro cleanup은 예외. 187-c report/manual smoke cleanup 완료. 다음 recommended action: **Design First Gate에 따라 후속 design slice 선택**. 후보: (1) SASO T3 design slice, (2) 2-point result visual refinement design slice, (3) multi/batch design slice, (4) detail/trace/graph design slice.

    4s-a. **ISO/ISEER 2-point result visual refinement design** (189-a 참고). `docs/designs/2026-05-29-tkinter-iso-iseer-2point-result-visual-refinement.md`에서 PyQt/reference의 2-point primary result가 profile rows x metric columns 비교 table이고 detail/trace/graph는 별도 surface임을 확인했다. 현재 Tkinter는 `ResultPanel` stacked summary 방식으로 정상 동작하지만 두 profile 비교 가독성이 약하므로, 189-b에서는 `ResultPanel` 대규모 변경 없이 `IsoIseer2PointSection`에 국소적인 2-point 전용 비교 table surface를 추가하는 방향을 추천한다. SASO/multi/detail/graph/core/golden/PyQt retirement/window geometry는 제외한다. 다음 recommended action: **189-b ISO/ISEER 2-point result visual refinement implementation**.

    4s-b. **ISO/ISEER 2-point result visual refinement implementation** (189-b 참고). `IsoIseer2PointSection`의 success result를 `ResultPanel` stacked summary 2개에서 section-local read-only comparison table로 바꾸어 `ISO 16358-1` / `India ISEER` rows와 `Region/Profile`, `EER Full`, `EER Half`, `CSPF/ISEER`, `CSTL [kWh]`, `CSEC [kWh]` columns를 함께 보여준다. invalid input은 stale success rows를 지우고 safe status만 표시한다. Hong Kong CSPF/HSPF `ResultPanel` result display, profile selector, scroll/window geometry, core/golden/PyQt source는 변경하지 않았다. 다음 recommended action: **manual smoke 후 다음 Design First Gate slice 선택**.

    4s-c. **Profile switch window fit / no-overflow scroll hotfix** (189-c 참고). 189-b 수동 확인에서 ISO/ISEER 2-point content가 viewport에 맞아도 wheel/trackpad로 빈 공간까지 스크롤되는 문제와, 기본 2-point 창 크기에서 Hong Kong profile로 전환하면 아래가 잘리는 문제가 확인되었다. `ScrollableFrame`은 overflow가 없을 때 internal wheel event를 소비하되 scroll하지 않고, `Iso16358Tab`은 profile switch 후 after-idle 1회만 현재 profile preferred content size로 toplevel geometry를 보정한다. root/toplevel `<Configure>` binding, continuous geometry observer, `bind_all`/`unbind_all`, 2-point result table logic 변경은 도입하지 않았다. 다음 recommended action: **manual smoke 후 후속 Design First Gate slice 선택**.

    4s-d. **Profile switch grow-to-fit / scroll reset hotfix** (189-d 참고). 189-c 수동 확인에서 Hong Kong 전환 후 스크롤이 남고, ISO/ISEER 2-point 복귀 시 창이 최초보다 작아지는 exact-fit/shrink 문제가 확인되었다. profile switch 보정은 grow-only로 변경해 현재 창 크기보다 줄이지 않고, preferred content grow 후 measured overflow delta가 남을 때 한 번만 추가 grow하며, 마지막에 scroll position을 top으로 reset한다. root/toplevel `<Configure>` binding, continuous observer, hardcoded pixel tuning, 2-point section/result table logic 변경은 도입하지 않았다. 다음 recommended action: **manual smoke 확인 후 후속 Design First Gate slice 선택**.

    4s-e. **Profile switch default exact-fit hotfix** (189-e 참고). 189-d 수동 확인에서 grow-only 정책 때문에 Hong Kong에서 ISO/ISEER 2-point로 복귀할 때 아래 빈 공간이 남는 문제가 확인되었다. 이 calculator는 profile 전환마다 현재 profile의 rendered preferred size 기준 default exact-fit을 우선하므로, profile switch helper는 current-size floor 없이 grow/shrink를 모두 허용하도록 되돌렸다. exact-fit 후 measured overflow 1회 보정과 scroll top reset, no-overflow wheel guard는 유지한다. 후속 tab/profile도 같은 hook을 재사용하되 hidden tab/dynamic surface의 preferred size owner는 해당 design slice에서 확인한다. 다음 recommended action: **manual smoke 확인 후 후속 Design First Gate slice 선택**.

    4v. **Xfail retirement audit / ISO pure-route obsolete xfail retirement / legacy diagnostic owner cleanup / AS/NZS case3 compatibility decision** (122~126 참고). PyQt fatal-abort 4개 파일 제외 full-ish baseline은 **568 passed, 1 skipped, 23 xfailed**에서 ISO pure-route Formula 45/49/47/50 obsolete experiment xfail 4개 제거 후 **568 passed, 1 skipped, 19 xfailed**로 정리되었다. `tests/test_iso16358_hspf_pure_iso_track_a.py`에는 fixture identity / workbook-reference guard / cycling / Formula 44·48 min-half / saturated auxiliary smoke만 남겼다. `tests/_legacy` 17개 xfail은 marker/count를 유지하면서 legacy workbook-oracle diagnostic/reference owner와 production official-exact path 분리를 reason/README로 명확히 했다. AS/NZS case3 2개 xfail은 marker/count를 유지하며 external workbook reference/full component row data prerequisite로 정책 결정했다. exact reconstruction / full row extraction은 Z-phase AS/NZS Excel compatibility work까지 deferred로 유지한다. 다음 recommended action은 (1) Python 3.12 venv 또는 Windows host에서 PyQt smoke 재검증, (2) Windows host 확보 시 PyInstaller size measurement, (3) Tkinter next metric/standard extension design 필요 시.

   4x. **macOS Tkinter manual smoke checklist** (120 참고). `docs/guides/lightweight_calculator_tk_manual_smoke.md` 신규 작성. 14 항목 manual checklist + OK/NG 기록 형식 + 기대값 (Hong Kong CSPF 4.939 / HSPF 3.643) + PyQt5 미import 확인 + macOS PyQt fatal-abort 분리 + 다음 단계 (Windows host 확보 시 packaging guide로 진행, 아니면 pending 유지). Tkinter MVP는 코드 변경 없이 동일 (118 reset 결과 유지). 다음 recommended action은 (1) Windows host 확보 후 PyInstaller size 실측 (Slice T6) 또는 (2) legacy/unused script cleanup audit 또는 (3) ISO section pure helper 분리. Windows 사용 불가 동안 (1)은 pending이므로 (2) 또는 (3) 중 사용자 우선순위에 따라 선택. 본 작업은 docs only.

   4z. **Calculator deployment UI feasibility pivot** (116 참고, `docs/designs/2026-05-22-lightweight-calculator-ui-feasibility.md`). PyInstaller packaging 시 PyQt5 + Qt runtime + Qt plugins로 calculator-only 배포물이 100~150MB 수준이 될 가능성 때문에, 아래 4c~4g와 5번 (Hong Kong HSPF UI surface)를 **hold**로 이동. 116에서 feasibility prototype을 만들고, 117 audit에서 단일 파일 비대화 위험을 식별한 뒤, 118에서 production-candidate clean module foundation으로 재정리 완료. 130에서 ISO section pure helper 분리까지 완료. 현재 구조: `app_calculator_tk.py` (thin entrypoint) + `ui_tk/calculator_app.py` (shell) + `ui_tk/profile_resolver.py` + `ui_tk/result_panel.py` + `ui_tk/input_widgets.py` + `ui_tk/tabs/iso16358_tab.py` + `ui_tk/sections/iso_cspf_section.py` + `ui_tk/sections/iso_hspf_section.py`. PyQt5 import 없음, Hong Kong CSPF = 4.939 / HSPF = 3.643 smoke 유지, `profile_id`/`calculator_id`/`config_path` UI 비노출. 157에서 Tkinter calculator **final UX contract** (`docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md`)를 정의했다. 현재 MVP는 Entry row + 계산 버튼 방식이며, 최종 UX는 table/grid input + auto-calc이다. PyQt calculator UI 자산은 reference로 유지, 4a 모듈 boundary plan은 폐기하지 않고 Tkinter direction이 fall back되면 resume. Calculator slice 순서는 4p의 project-wide visual adoption 선행 inventory/token foundation 이후 아래 순서로 이어진다:
     1. **Tkinter table/grid input foundation** (slice 1) — Hong Kong CSPF/HSPF `Entry` row를 editable grid/table로 교체.
     2. **Tkinter auto-calc debounce/helper foundation** (slice 2) — 계산 버튼 제거, `after`-based debounce helper 도입.
     3. **ISO Hong Kong CSPF/HSPF table + auto-calc vertical slice** (slice 3) — grid + auto-calc + per-section result panel 통합.
     4. **macOS manual UX smoke** (slice 4) — `docs/guides/lightweight_calculator_tk_manual_smoke.md` 14항목 체크리스트 실행.
     5. **Windows PyInstaller size measurement** (slice 5) — Windows host 확보 시 one-folder/one-file 실측.
     6. **PyQt calculator-only source retirement 재개** (slice 6) — slice 3 검증 + slice 5 continue criteria 충족 후 154~156 retirement sequence 재개.
     7. **Tkinter standard/region expansion** (slice 7) — EN, AHRI, KS tab 추가.
   - 안 쓰는 legacy/script 정리는 별도 future cleanup phase로 둔다.
   4c. **hold** — Slice ζ `ui/calculator_en_tab.py` 추출 (4z 결과에 따라 resume 여부 결정).
   4d. **hold** — Slice η `ui/calculator_ahri_tab.py` 추출.
   4e. **hold** — Slice β AHRI/EN auto-recompute wiring.
   4f. **hold** — Slice γ per-tab result/status surface unification.
   4g. **hold** — Slice δ error feedback alignment.
   5. **hold** — Hong Kong HSPF UI surface (PyQt). Tkinter MVP direction이 결정된 뒤 PyQt resume / Tkinter port / CLI fallback 중 한 경로로 재배치한다. core/config/test + profile/dispatcher 자산은 이미 준비되어 있어 어느 경로에서든 재사용 가능하다.
   6. unit adapter 확장 — ISO / KS / EN profile을 `core/calculator_unit_adapter.py`에 추가한다. UI audit와 완전 분리된 non-UI 작업. **순서는 calculator-only deployment UI feasibility (4z) 결과 이후 재조정**한다 (UI direction과 무관하게 진행 가능하지만 우선순위는 deployment direction 확정 후 재산정).
   7. ML / inverse-search 복귀 준비. **순서는 4z 결과 이후 재조정**한다.
   8. Train/Predict UI 작은 refactor phase — ML / inverse-search 복귀 phase 진입 시점에 함께 다룬다 (112 audit 참고). **순서는 4z 결과 이후 재조정**한다. 후보: app entrypoint thin 유지 / PredictWindow controller 책임 정리 / ODU cascading helper 분리 검토 / TrainWorker boundary 정리 / inline style token 적용 / ML result key SSOT 정렬 / ref_type · exp_type literal 중복 제거 / base_model · base_view contract 재확인. 본 phase는 Calculator action model slice (β/γ/δ), unit adapter 확장, ML 본 구현과 **섞지 않는다**.
   - ISO table Excel-like behavior patch (Ctrl+C copy / Delete·Backspace clear / invalid cell BackgroundRole+ToolTip / Enter·Shift+Enter·Tab·Shift+Tab 방향)는 `ProfileInputGridModel` / `ProfileInputGridView`에서 완료했다 (104 참고). Hong Kong / SASO / ISO T1 / India ISEER 모두 같은 모델/뷰를 공유하므로 한 번에 정렬되었다.
   - ISO result/read-only table copy TSV (`TwoPointTableModel` / `RegionResultTableModel` / `TraceTableModel` / `RegionDetailTab.table`) 완료 (105 참고). 공통 helper `selected_cells_to_tsv` + `ReadOnlyCopyTableView` subclass로 Ctrl+C TSV copy를 연결했고 read-only이므로 paste / clear / undo는 의도적으로 지원하지 않는다.
   - 096: bin detail의 frost flag를 trace에 명시 노출 완료.
   - 097: Formula 44/45/47/48/49/50 boundary COP 보간을 ISO 원문 표현과 정렬 (rewrite-only, numeric 변화 없음). Formula 50 trace에 cop_ful_f_tg / cop_ext_f_tf endpoint COP 명시 노출.
   - 098: 남은 11개 mismatch case를 4개 cluster로 분류하고 원문 audit 항목 5개 식별.
   - 099: `_iso_hspf_extended_minus7_default()` 의 -7_ext default factor 적용 대상 정정 (2°C frost → 2°C non-frost → -7°C 2-step).
   - 100: ISO16358-2 HSPF official exact fixture expected를 원문 audit + 099 기준으로 갱신하고 `XFAIL_CASE_IDS`를 비워서 16/16 case pass 상태로 정리.
4. 전역 table contract는 "Excel-like behavior"를 기본으로 한다는 점이 `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` / `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md` / `AGENTS.md` / `AGENT_TASK_ROUTER.md` / calculator design doc에 명시 완료. 094 audit에서 식별된 ISO16358-1 CSPF 입력표 (Copy/Clear/Invalid 시각/Enter 방향) 가 alignment 1번 대상이다. ISO16358-2 HSPF mismatch는 외부 분석 대기 hold 유지.
5. Historical case3 workbook full-dump가 확보되면 AS/NZS workbook oracle compatibility를 별도 Z-phase로 확장한다.

`ui/spreadsheet_table.py` 공통 model/view component, `core/calculator_unit_adapter.py` (AHRI SEER2 ml_prediction → Btu/h 변환), envelope chain end-to-end smoke (`tests/test_calculator_envelope_chain.py`), AHRI SEER2 / AHRI HSPF2 / EN14825 SEER / EN14825 SCOP (multi-climate) horizontal table-input UI slice는 모두 완료 상태이므로 next action으로 나열하지 않는다. 위 1~5는 그 위에 쌓이는 작업이다.

`work/iso-hspf-refactor-ui-followup` 브랜치는 merge하지 않고 reference/spike로만 둔다.

기존 ISO 파일 내부의 KS-aware 분기 제거 / measured input prep 분리 / point resolution 분리 / standalone body 작성 같은 037~043 사이클의 후속 미세 cleanup은 더 이상 다음 작업으로 제안하지 않는다. 다음 단계는 위 1번부터.

## Medium-term milestones
- CSPF/HSPF profile/schema consolidation
- UI resolver-backed config selection
- Calculator UI v1 follow-up
- Predictor / Calculator adapter boundary
- ML / inverse-search 재개

## Z-phase / deferred work
- AS/NZS historical case3 full-dump exact matching
- Excel helper column exact compatibility
- Windows Excel COM row-level extraction
- original workbook full_dump / chat_packet 기반 compatibility 작업
- large compatibility calculator module

## What does not belong here
- 완료 상세 기록
- 긴 decision history
- 세부 실패/교훈
- 리팩토링 후보의 세부 분리 전략
- 규격 공식/fixture 상세 근거
