# Project Log
이 문서는 작업 과정의 시도, 실패, 성공, 중요 결정사항 및 반복 방지를 위한 기록용입니다.

## 2026-05-04 — Validation smoke/golden 안정화

### Result
- Validation smoke 및 golden 테스트 안정화 완료.
- Hong Kong HSPF smoke/golden validation 완료.
- 전체 테스트 기준: `109 passed`.

### Decision
- 문서 리팩토링 전 필수 코드/테스트 수정 항목은 없음.

---

## 2026-05-04 — ISO16358 초기 리버스 엔지니어링 파일 archive 이동

### Result
- 루트 디렉토리의 초기 ISO16358 reverse engineering 파일을 `docs/archive/iso16358_initial_reverse_engineering/`로 이동.
- `temporary.txt`는 로컬 scratch 파일이므로 제외.

### Verification
- `pytest tests/` → `109 passed`.

---

## 2026-05-04 — 문서 리팩토링 시작 결정

### Tried
- `project_context.md`의 역할 비대화를 검토.

### Decision
- 장기 방향은 `PROJECT_CHARTER.md`.
- 현재 상태 요약은 `project_brief.md`.
- 작업 기록은 `project_log.md`.
- 살아있는 계획은 `docs/REFACTOR_PLAN.md`.

### Lesson
- ISO16358 계열 작업에서 공통 엔진 구조보다 지역별 하드코딩을 먼저 시도해 재작업이 발생했다.
- 앞으로 Logic 수정 시 공통 엔진 / profile / config / handler 구조로 표현 가능한지 먼저 검토한다.