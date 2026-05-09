# Project Brief
이 문서는 새 대화창 시작 시 현재 상태를 빠르게 파악하기 위한 요약 문서입니다.

## 1. 현재 상태 및 마일스톤
- **테스트 및 검증:** Validation smoke/golden 안정화 및 KS oracle cycling consistency(H-2b) 검증이 완료되었습니다. 전체 테스트 통과 기준은 **250 passed** 입니다.
- **보호망 확보:** Phase 1 범위에서 KS C 9306, ISO T1, SASO T3, Hong Kong, India ISEER, AHRI, EN14825 규격에 대한 Regression 보호망을 확보했습니다. ISO HSPF는 Formula micro golden 및 KS shared-formula oracle로 이중 보호 중입니다.
- **다음 큰 작업 후보:**
  1. ISO16358-2 common HSPF 마무리 및 UI 연결 (진행 중)
  2. 문서 리팩토링 마무리
  3. Predictor 연동
- **ISO16358-2 HSPF / AS/NZS 경계:** ISO16358-2 HSPF는 Track A common ISO path와 Track B AS/NZS Excel compatibility path로 분리합니다. AS/NZS Excel `1126.120 kWh` / `4.33824` / `1126120.47 Wh`는 `ASNZS_EXCEL_COMPAT` reference이며 common ISO expected가 아닙니다. AS/NZS row-level exact reconstruction 작업은 Z-phase로 보류되었습니다.

## 2. 문서 가이드
- **`AGENTS.md`**: 매 작업 시작 시 확인하는 얇은(Lite) 규칙 문서입니다.
- **`AGENTS_FULL.md`**: 명시적 요청이 있기 전에는 읽지 않습니다.
- **`PROJECT_CHARTER.md`**: 프로젝트의 최종 목표와 장기 방향을 정의하는 앵커 문서입니다.
- **`project_brief.md`**: 새 대화 시작 시점의 얇은 현재 상태 요약 문서입니다. (현재 문서)
- **`project_log.md`**: Try/Fail/Success 이력 기록, 결정 사항, 반복 실수 방지용 기록 문서입니다.
- **`docs/architecture/project_architecture.md`**: 프로젝트의 주요 기술 구조, 피처 정의, UI 컬럼 매핑 정보를 정리한 문서입니다.
- **`docs/REFACTOR_PLAN.md`**: 살아있는 개발 계획과 남은 작업(TODO)을 관리하는 문서입니다.
