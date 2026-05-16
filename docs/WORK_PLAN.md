# Work Plan

## Purpose
- 현재 우선순위와 다음 실행 순서를 관리한다.
- 장기 목표와 Phase 1~5는 `PROJECT_CHARTER.md`를 따른다.
- 실제 작업 기록과 결정 이력은 `project_log.md`를 본다.
- 구조 리팩토링 후보와 트리거는 `docs/REFACTOR_PLAN.md`를 본다.

## Current milestone focus
- Calculator architecture reset 실행 (ISO / KS / ASNZS 3-module boundary)
- KS C 9306 CSPF/HSPF를 `core/calculator_ks_c9306.py`로 분리
- `core/calculator_iso16358.py`를 ISO16358 CSPF/HSPF 전용으로 정리/재작성하기 위한 선행 작업
- production ISO common path와 AS/NZS Excel compatibility path 분리 유지
- AS/NZS Excel exact matching은 Z-phase

## Near-term execution order
1. `core/calculator_ks_c9306.py` 생성 및 KS CSPF/HSPF 분리
2. `core/calculator_iso16358.py`를 ISO16358 CSPF/HSPF 전용으로 정리/재작성 (ISO 기반 regional profile JSON 해석을 ISO calculator에 한정)
3. profile resolver / Calculator UI 연결 (calculator boundary 안정화 후 별도 작업)
4. ML / inverse-search 복귀
Z. `core/calculator_asnzs_hspf_excel.py` AS/NZS workbook oracle compatibility calculator 별도 phase

`work/iso-hspf-refactor-ui-followup` 브랜치는 merge하지 않고 reference/spike로만 둔다.

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
