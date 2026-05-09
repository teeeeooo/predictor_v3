# Work Plan

## Purpose
- 현재 우선순위와 다음 실행 순서를 관리한다.
- 장기 목표와 Phase 1~5는 `PROJECT_CHARTER.md`를 따른다.
- 실제 작업 기록과 결정 이력은 `project_log.md`를 본다.
- 구조 리팩토링 후보와 트리거는 `docs/REFACTOR_PLAN.md`를 본다.

## Current milestone focus
- ISO16358-2 common HSPF 마무리
- remaining xfail audit / 해소
- production ISO common path와 AS/NZS Excel compatibility path 분리 유지
- AS/NZS Excel exact matching은 Z-phase

## Near-term execution order
1. ISO16358-2 HSPF remaining xfail audit / 해소
2. HSPF completion 기준 정리
3. `calculator_iso16358.py` structure audit
4. CSPF/HSPF schema/profile 정리
5. Calculator UI follow-up
6. ML / inverse-search 복귀
Z. AS/NZS HSPF compatibility / Excel exact matching 별도 phase

## Medium-term milestones
- CSPF/HSPF profile/schema consolidation
- UI resolver-backed config selection
- Calculator UI v1 follow-up
- Predictor / Calculator adapter boundary
- ML / inverse-search 재개

## Z-phase / deferred work
- AS/NZS Excel exact matching
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
