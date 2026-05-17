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
- ISO16358-2 HSPF official exact 16-case verification은 active diagnostic으로 추가했다. 현재 계산기 actual은 5개 case match, 11개 case mismatch이며 mismatch case는 strict xfail로 보존한다.
- ISO16358-2 HSPF official exact fixture는 official data (input / description / expected)만 남기도록 정리했고, current-implementation status (match/mismatch xfail list)는 `tests/test_iso16358_hspf_official_exact_golden.py`의 `XFAIL_CASE_IDS` constant로 분리했다.
- AHRI / EN14825 horizontal table-input UI와 ML W ↔ calculator-native unit boundary는 `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`에 설계 완료. 첫 구현 slice는 AHRI SEER2 table input 한 곳으로 제한한다.

## Near-term execution order
1. Step 1~5 완료 상태를 유지하고, 새 ISO / KS / ASNZS boundary를 깨는 후속 변경을 피한다.
2. ISO16358-2 HSPF official exact 16-case mismatch를 먼저 분석한다. UI redesign, calculator table-input UI 구현, 또는 추가 table UI slice는 이 mismatch 분석 뒤로 둔다.
3. 그 뒤 Calculator UI v1 follow-up을 별도 UI 작업으로 다룬다. 현재 `ui/calc_window.py`에는 launch smoke, AHRI/EN profile selector guard, AHRI AC calculate button/result-display smoke, EN SCOP result smoke, HSPF2 form layout guard, HSPF2 validation guard가 있다. AHRI / EN14825 horizontal table-input UI 설계는 `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md` 기준으로 AHRI SEER2 → AHRI HSPF2 → EN14825 SCOP → EN14825 SEER 순서로 slice를 분리한다. 그 뒤 unit adapter slice (W ↔ profile-native)를 별도로 둔다.
4. ML / inverse-search 복귀는 envelope adapter chain의 첫 AHRI SEER2 slice 상태를 유지한 뒤 별도 작업으로 다룬다.
5. Historical case3 workbook full-dump가 확보되면 AS/NZS workbook oracle compatibility를 별도 Z-phase로 확장한다.

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
