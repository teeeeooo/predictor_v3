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

   4w. **Legacy / unused script cleanup audit** (121 참고). repo 안의 legacy / unused / spike / debug / one-off script 후보를 read-only로 inventory했다. 즉시 삭제 / 이동 / rename 대상 없음 — 모든 후보는 후속 slice (C1 docs/guides cross-link, C2 `docs/archive/iso16358_initial_reverse_engineering/README.md` status header, C3 `tests/_legacy/` 명명 audit, C4 `core/_legacy/calculator_iso16358_legacy.py` decommission 조건 문서화, C5 119 allowlist 재검토) 로 분리. 추천 first cleanup = **Slice C2** (최저 위험, docs only). `scripts/update_mapping.py`는 `ui/train_window.py:11`에서 import 중인 활성 production helper로 확인되어 cleanup 대상 아님. `core/_legacy/calculator_iso16358_legacy.py` + `tests/_legacy/*` 5개는 강결합이라 별도 design-gated 작업으로 둔다. 119 guard가 직접 막지 못하는 위험 G1~G5 (archive header / tests/_legacy README / scripts owner header / spike lifecycle marker / stale-script audit subcommand) 는 후속 guard improvement 후보로 기록.

   4v. **Xfail retirement audit / ISO pure-route obsolete xfail retirement / legacy diagnostic owner cleanup** (122~125 참고). PyQt fatal-abort 4개 파일 제외 full-ish baseline은 **568 passed, 1 skipped, 23 xfailed**에서 ISO pure-route Formula 45/49/47/50 obsolete experiment xfail 4개 제거 후 **568 passed, 1 skipped, 19 xfailed**로 정리되었다. `tests/test_iso16358_hspf_pure_iso_track_a.py`에는 fixture identity / workbook-reference guard / cycling / Formula 44·48 min-half / saturated auxiliary smoke만 남겼다. `tests/_legacy` 17개 xfail은 marker/count를 유지하면서 legacy workbook-oracle diagnostic/reference owner와 production official-exact path 분리를 reason/README로 명확히 했다. 남은 xfail은 `tests/_legacy` 17개와 AS/NZS case3 external reference/full-row-data prerequisite 2개다. 다음 recommended action은 (1) AS/NZS case3 external reference compatibility decision, (2) Windows host 확보 시 PyInstaller size measurement, (3) PyQt fatal-abort environment handling.

   4x. **macOS Tkinter manual smoke checklist** (120 참고). `docs/guides/lightweight_calculator_tk_manual_smoke.md` 신규 작성. 14 항목 manual checklist + OK/NG 기록 형식 + 기대값 (Hong Kong CSPF 4.939 / HSPF 3.643) + PyQt5 미import 확인 + macOS PyQt fatal-abort 분리 + 다음 단계 (Windows host 확보 시 packaging guide로 진행, 아니면 pending 유지). Tkinter MVP는 코드 변경 없이 동일 (118 reset 결과 유지). 다음 recommended action은 (1) Windows host 확보 후 PyInstaller size 실측 (Slice T6) 또는 (2) legacy/unused script cleanup audit 또는 (3) ISO section pure helper 분리. Windows 사용 불가 동안 (1)은 pending이므로 (2) 또는 (3) 중 사용자 우선순위에 따라 선택. 본 작업은 docs only.

   4z. **Calculator deployment UI feasibility pivot** (116 참고, `docs/designs/2026-05-22-lightweight-calculator-ui-feasibility.md`). PyInstaller packaging 시 PyQt5 + Qt runtime + Qt plugins로 calculator-only 배포물이 100~150MB 수준이 될 가능성 때문에, 아래 4c~4g와 5번 (Hong Kong HSPF UI surface)를 **hold**로 이동. 116에서 feasibility prototype을 만들고, 117 audit에서 단일 파일 비대화 위험을 식별한 뒤, 118에서 production-candidate clean module foundation으로 재정리 완료. 현재 구조: `app_calculator_tk.py` (thin entrypoint) + `ui_tk/calculator_app.py` (shell, ~54 LOC) + `ui_tk/profile_resolver.py` (pure Python, region/metric → profile_id) + `ui_tk/result_panel.py` + `ui_tk/input_widgets.py` + `ui_tk/tabs/iso16358_tab.py` + `ui_tk/sections/iso_cspf_section.py` + `ui_tk/sections/iso_hspf_section.py`. PyQt5 import 없음, Hong Kong CSPF = 4.939 / HSPF = 3.643 smoke 유지, `profile_id`/`calculator_id`/`config_path` UI 비노출. PyQt calculator UI 자산 (app_calculator.py / ui/calc_window.py 외)은 reference로 유지, 4a 모듈 boundary plan은 폐기하지 않고 Tkinter direction이 fall back되면 resume. 다음 작업 후보는 (a) macOS Tkinter manual smoke checklist, (b) ISO section의 input dict 구성 + result text formatting을 pure helper로 추가 분리, (c) **Windows PyInstaller 실측 (Slice T6)** — Windows 호스트 확보 후 진행. 추천 next action은 (a) — Windows 환경 부재 동안 진행 가능하고 packaging baseline 결정 전에 manual smoke 결과를 확보한다. 안 쓰는 legacy/script 정리 (예: spike 잔재, PyQt hold 파일 group review, 미사용 helper script)는 별도 future cleanup phase로 둔다 — 118 작업에서는 삭제/정리 미수행.
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
