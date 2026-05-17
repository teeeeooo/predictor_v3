# Work Plan

## Purpose
- 현재 우선순위와 다음 실행 순서를 관리한다.
- 장기 목표와 Phase 1~5는 `PROJECT_CHARTER.md`를 따른다.
- 실제 작업 기록과 결정 이력은 `project_log.md`를 본다.
- 구조 리팩토링 후보와 트리거는 `docs/REFACTOR_PLAN.md`를 본다.

## Current milestone focus
- Calculator series reset 실행: 기존 `core/calculator_iso16358.py`를 legacy/reference로 격하하고 새 ISO / KS / ASNZS calculator 3개 축으로 재작성
- 기존 ISO 파일 내부 부분 cleanup 누적은 중단 (037~043 같은 미세 cleanup 사이클은 종료)
- 새 ISO 16358 calculator는 CSPF/HSPF common standard logic만 담당
- KS C 9306 / AS/NZS workbook oracle 책임은 각각 별도 calculator 파일로 분리
- legacy behavior 보존 테스트는 새 calculator contract 기준으로 삭제 / 이전 / 격리
- production ISO common path와 AS/NZS Excel compatibility path 분리 유지
- AS/NZS historical case3 full-dump exact matching은 Z-phase. 현재 repo의 `reference_files/iso16358_test_sheet.xlsx` snapshot exact-match는 AS/NZS compatibility calculator/fixture에서만 관리

## Near-term execution order
1. 기존 `core/calculator_iso16358.py`를 legacy/reference 파일(예: `core/legacy/calculator_iso16358_legacy.py` 또는 `core/_legacy/` 위치)로 rename/archive 준비 (이름/위치/import 영향 audit이 선행)
2. 새 `core/calculator_iso16358.py` skeleton 작성 (ISO16358 CSPF/HSPF 전용 책임만 표시한 빈 스켈레톤 + public API 시그니처)
3. 새 ISO 16358 CSPF/HSPF 최소 공식 구현 (Hong Kong / India / SASO / ISO T1 default 등 ISO regional profile JSON을 새 ISO calculator가 직접 해석)
4. `core/calculator_ks_c9306.py`의 KS CSPF/HSPF standalone 정리 (이미 standalone이 된 부분 외 잔여 의존이 있다면 제거)
5. legacy tests 정리: (a) 삭제 (b) 새 calculator 기준 이전 (c) legacy/archive 격리 — 분류 기준은 `docs/REFACTOR_PLAN.md`에서 관리
6. profile resolver / dispatcher / Calculator UI 연결은 calculator series가 안정된 뒤 재개
7. ML / inverse-search 복귀는 calculator series 안정 + UI 재연결 이후
Z. historical case3 workbook full-dump 확보 후 AS/NZS workbook oracle compatibility 확장 (별도 phase)

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
