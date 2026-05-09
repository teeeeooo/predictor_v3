# Refactor Plan

## Purpose
- 리팩토링 후보와 트리거만 관리한다.
- 장기 목표와 Phase 1~5는 `PROJECT_CHARTER.md`를 따른다.
- 현재 우선순위와 다음 실행 순서는 `docs/WORK_PLAN.md`를 본다.
- 실제 작업 기록과 decision history는 `project_log.md`를 본다.
- 큰 설계 결정은 `docs/designs/*`에 둔다.

## Refactor principles
- 계산 결과 회귀 방어 최우선
- public API 무단 변경 금지
- golden expected 임의 변경 금지
- 한 번에 대규모 구조 변경 금지
- 분리 전 branch trace / tests / fixtures 보호 확인

## Active refactor candidates

### 1. `calculator_iso16358.py` structure audit
- **왜 후보인지**: 클래스 및 파일 크기 비대화로 인한 유지보수성 저하 우려.
- **지금 바로 분리하지 않는 이유**: ISO HSPF 공통화 작업 및 xfail 해소 작업이 진행 중이므로 계산 안정성이 우선임.
- **분리 트리거**: HSPF 공통화 완료 및 completion 기준 도달 시.
- **지켜야 할 guard**: public API, golden result, region config boundary 유지.

### 2. ISO CSPF/HSPF helper separation
- **CSPF/HSPF helper 분리 후보**: bin loop, point resolution, energy accumulation 등 공통 로직 모듈화.
- **common path / region-specific path 경계**: 공통 엔진이 특정 지역의 특수 로직(예: KS C 9306)에 오염되지 않도록 분리.
- **production path와 compatibility path 분리**: 표준 경로와 호환성 경로(Z-phase)의 코드 베이스 격리.

### 3. KS C 9306 helper separation
- **KS C 9306 독립성 유지**: 한국 고유의 부하 라인 계산 및 보간 규칙을 별도 모듈로 관리.
- **common ISO로 무리하게 흡수하지 않음**: 규격 간의 미세한 차이를 강제로 통합하여 공통 엔진을 복잡하게 만들지 않음.
- **분리 트리거**: KS 관련 조건 분기가 공통 엔진 가독성을 해칠 때.

### 4. profile/schema resolver cleanup
- **region config / profile schema / calculator input boundary**: 각 레이어 간의 데이터 계약 명확화.
- **nested config 직접 주입 금지**: 계산기 core가 config 파일 구조에 직접 의존하지 않도록 resolver를 통한 데이터 전달.
- **resolver-backed path 필요성**: 신규 규격 추가 시 유연한 확장을 위한 프로필 리졸버 강화.

### 5. UI resolver-backed config selection
- **UI가 config 파일을 직접 scan하는 경로 정리 후보**: 현재 UI 계층이 리졸버 가드를 우회하여 파일을 직접 스캔하는 문제 해결.
- **calculator profile resolver 우회 방지**: UI에서도 항상 `core/calculator_profiles.py`를 통해 설정을 로드하도록 강제.

## Deferred refactor candidates
- common seasonal bin engine
- full plugin architecture
- AS/NZS HSPF compatibility calculator module
- Excel row-level exact reconstruction support
- large package split

## Not refactor tasks
- HSPF xfail 해소
- golden fixture 보강
- UI 기능 구현
- ML/inverse-search 복귀
- 문서 오타 수정
- 단순 validation/smoke test 추가

## Refactor trigger checklist
- 파일/클래스 비대화
- 같은 branch 조건이 반복적으로 생김
- common path 수정 시 region regression이 반복적으로 깨짐
- UI/config/ML schema가 calculator core에 침투함
- public API 또는 result schema가 흔들릴 위험이 생김

## Guardrails for any refactor
- public API 유지
- golden/smoke/validation test 선확인
- region config 의미 변경 금지
- compatibility calculator와 production calculator 분리
- `docs/designs/*`에 design gate summary 작성 후 구현
