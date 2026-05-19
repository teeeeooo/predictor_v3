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
- ISO16358-2 HSPF official exact 16-case verification은 active diagnostic으로 추가했다. 현재 계산기 actual은 5개 case match, 11개 case mismatch이며 mismatch case는 strict xfail로 보존한다. 083 report는 historical diagnostic snapshot이며 "official exact" expected의 성격은 추가 검토 중이다 (자세한 hold 사유는 091 참고).
- ISO16358-2 HSPF official exact fixture는 official data (input / description / expected)만 남기도록 정리했고, current-implementation status (match/mismatch xfail list)는 `tests/test_iso16358_hspf_official_exact_golden.py`의 `XFAIL_CASE_IDS` constant로 분리했다.
- ISO16358-2 HSPF mismatch는 hold 상태로 두며 repo immediate next action에 포함하지 않는다. 사용자 외부 분석 결과 대기 중이고, repo 계산식/expected/xfail 수정은 보류한다. xfail case 목록은 그대로 유지한다. 부분 점검 결과 bin_hours (2866 h)와 HSTL expected 4885.4 kWh, fixture ↔ external reference script 입력 동일성, repo의 `2_full` / `2_half` → `2_full_f` / `2_half_f` measured 보존 동작은 모두 정상으로 확인됐다. case 12/15/16의 큰 mismatch는 external reference script가 2_full/2_half measured를 frost/non-frost 양쪽에 동일하게 주입한 해석 오류 가능성이 높다 (091 참고).
- AHRI / EN14825 horizontal table-input UI와 ML W ↔ calculator-native unit boundary는 `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`에 설계 완료. 첫 구현 slice는 AHRI SEER2 table input 한 곳으로 제한한다.
- ML W ↔ AHRI SEER2 Btu/h capacity 변환은 `core/calculator_unit_adapter.py`로 분리했고, PredictedPointsEnvelope → CalculatorInputEnvelope → CalculatorResultEnvelope → RankingCandidateEnvelope end-to-end smoke (`tests/test_calculator_envelope_chain.py`)가 chain 무결성을 보호한다.
- 전역 PyQt spreadsheet-like table UI는 `docs/ui/SPREADSHEET_TABLE_CONTRACT.md`를 단일 owner로 한다. 공통 component는 `ui/spreadsheet_table.py` (QAbstractTableModel 기반 model, QTableView 기반 `SpreadsheetTableView`, TSV copy/paste, clear, undo, invalid numeric, point-dict 변환)와 `tests/test_spreadsheet_table_model.py` / `tests/test_spreadsheet_table_view.py` smoke harness로 시작했다.
- AHRI SEER2 입력은 horizontal spreadsheet table (`SpreadsheetTableView` + `make_ahri_seer2_table_model()`)로 전환했다. 5 cooling point (A_Full/B_Full/B_Low/E_Int/F_Low) × 2 row (능력 [Btu/h] / 전력 [W]). `calculate_ahri()`와 HSPF2 v3 A2 derivation 모두 동일 table에서 값을 읽는다. Cd_low/Cd_full만 기존 compact form.
- AHRI HSPF2 v3 입력도 horizontal spreadsheet table (`SpreadsheetTableView` + `make_ahri_hspf2_table_model()`)로 전환했다. 7 heating point (H01/H11/H12/H1N/H22/H2Int/H32) × 2 row (능력 [Btu/h] / 전력 [W]). `_build_hspf2_v3_input()`는 A2를 SEER2 table에서, H01~H32을 HSPF2 table에서 읽는다. t_off/t_on/defrost_t_test_minutes/defrost_t_max_minutes만 기존 compact form (`input_widgets_hspf2`)으로 유지.
- EN14825 SEER / SCOP 입력도 horizontal spreadsheet table (`SpreadsheetTableView` + `make_en14825_seer_table_model()` / `make_en14825_scop_table_model()`)로 전환했다. UI 입력 단위는 W로 통일하고, `calculate_en()`이 EN core (`calculate_seer` / `calculate_scop`) 호출 직전 W → kW (1/1000) 변환을 수행한다. `core/calculator_en14825.py`와 `data/region_configs/en14825_scop.json`은 kW/core 기준을 그대로 유지한다. SCOP는 Average / Warmer / Colder checkbox로 다중 선택 가능하고, 선택된 climate별 table/card (각 climate은 자체 A/B/C/D/TOL/Tbiv table + p_design_h_w + Tbiv/TOL temp prefill) 를 가진다. 기본 prefill은 Average=Tbiv -10, TOL -11 / Warmer=Tbiv 2, TOL -11 / Colder=Tbiv -15, TOL -22. 공통 standby form (`p_to_w`/`p_sb_w`/`p_ck_w`/`p_off_w`) 도 W 입력으로 통일하고 기본값 0.0 prefill.

## Near-term execution order
1. Step 1~5 완료 상태를 유지하고, 새 ISO / KS / ASNZS boundary를 깨는 후속 변경을 피한다.
2. ISO16358-2 HSPF official exact 16-case mismatch는 hold 상태이며 repo immediate next action에서 제외한다. 사용자 외부 분석 결과 대기 중이고, repo 계산식 / expected / xfail / fixture 수정은 보류한다. 분석 결과가 들어오면 그때 repo 후속 작업을 다시 정한다.
3. Repo 다음 순서는 다음 sequence로 둔다:
   1. ISO16358-2 HSPF Formula 44/45/47/48/49/50 boundary COP alignment (외부 분석 결과 도착 시점에 진행).
   2. ISO table Excel-like behavior patch — Ctrl+C copy, Delete/Backspace clear, invalid cell 시각화, Enter/Shift+Enter/Tab/Shift+Tab 방향 정렬 (`ProfileInputGridModel` / `ProfileInputGridView`).
   3. ISO result/read-only table copy TSV — `TwoPointTableModel` / `RegionResultTableModel` / `TraceTableModel` / `RegionDetailTab.table` 에 TSV copy 추가.
   4. unit adapter 확장 — ISO / KS / EN profile을 `core/calculator_unit_adapter.py`에 추가한다.
   5. ML / inverse-search 복귀 준비.
   - 096에서 ISO16358-2 HSPF common bin detail의 frost flag를 trace에 명시적으로 노출하도록 수정 완료. ISO16358-2 HSPF 전체 mismatch는 여전히 외부 분석 대기 hold 상태.
4. 전역 table contract는 "Excel-like behavior"를 기본으로 한다는 점이 `docs/ui/SPREADSHEET_TABLE_CONTRACT.md` / `AGENTS.md` / `AGENT_TASK_ROUTER.md` / calculator design doc에 명시 완료. 094 audit에서 식별된 ISO16358-1 CSPF 입력표 (Copy/Clear/Invalid 시각/Enter 방향) 가 alignment 1번 대상이다. ISO16358-2 HSPF mismatch는 외부 분석 대기 hold 유지.
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
