# Project Brief
이 문서는 새 대화창 시작 시 현재 상태를 빠르게 파악하기 위한 요약 문서입니다.

## 1. 현재 상태 및 마일스톤
- **테스트 및 검증:** Validation smoke/golden 안정화 및 KS oracle cycling consistency(H-2b) 검증이 완료되었습니다. 전체 테스트 통과 기준은 **250 passed** 입니다.
- **보호망 확보:** Phase 1 범위에서 KS C 9306, ISO T1, SASO T3, Hong Kong, India ISEER, AHRI, EN14825 규격에 대한 Regression 보호망을 확보했습니다. ISO HSPF는 Formula micro golden 및 KS shared-formula oracle로 이중 보호 중입니다.
- **실행 로드맵:** 현재 우선순위와 상세 실행 순서는 `docs/WORK_PLAN.md`를 따른다.
- **ISO16358-2 HSPF / AS/NZS 경계:** ISO16358-2 HSPF는 Track A common ISO path와 Track B AS/NZS HSPF calculator(Energy Rating SEER Excel workbook reference)로 분리합니다. AS/NZS current workbook snapshot exact-match는 별도 compatibility calculator/fixture에서만 다루며, historical case3 full-dump 재현은 계속 Z-phase입니다.

## 2. 문서 가이드
- **`AGENTS.md`**: 매 작업 시작 시 확인하는 얇은(Lite) 규칙 문서입니다.
- **`project_brief.md`**: 새 세션 또는 작업 재개 시의 현재 상태 요약입니다. (현재 문서)
- **`docs/WORK_PLAN.md`**: 현재 우선순위와 다음 실행 순서를 관리하는 실행판 문서입니다.
- **`docs/REFACTOR_PLAN.md`**: 리팩토링 후보, 구조 분리 트리거, guardrails를 관리하는 문서입니다.
- **`PROJECT_CHARTER.md`**: 프로젝트의 최종 목표와 장기 방향을 정의하는 헌장입니다.
- **`project_log.md`**: 작업 기록, 결정 사항, 실패, 교훈을 보존하는 로그입니다.
- **`docs/designs/*`**: 아키텍처 및 구현 관련 큰 설계 결정문입니다.
