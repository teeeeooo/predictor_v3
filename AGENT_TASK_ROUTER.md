## Task Routing Rules

작업자는 먼저 작업 유형을 분류한 뒤, 해당 유형에 필요한 문서만 읽는다.
불필요한 긴 문서를 습관적으로 읽지 않는다.

### 1. Commit / Git 정리

읽을 문서:
- `AGENTS.md`

읽지 말 것:
- `PROJECT_CHARTER.md`
- `project_brief.md`
- `project_log.md`
- `AGENTS_FULL.md`
- 규격별 notes 문서

절차:
1. `git status`
2. `git diff --stat`
3. 변경 파일 성격 확인
4. 테스트 결과가 사용자가 보고한 내용과 일치하는지 확인
5. 명확한 commit message 작성
6. commit/push 수행

주의:
- `temporary.txt`는 로컬 scratch 파일이며 `.gitignore` 대상이므로 커밋하지 않는다.

### 2. Logic 수정 / 계산 엔진 수정

읽을 문서:
- `AGENTS.md`
- 관련 규격의 notes/dev_notes/design_notes 중 필요한 문서
- 필요한 경우 `docs/REFACTOR_PLAN.md`의 해당 섹션

조건부로 읽을 문서:
- 새 대화 시작 직후 방향이 불명확하면 `project_brief.md`
- 과거 실패가 의심되면 `project_log.md`에서 관련 키워드만 검색

읽지 말 것:
- `AGENTS_FULL.md` unless explicitly requested
- 관련 없는 규격 문서 전체
- 대형 파일 전체

절차:
1. 먼저 공통 엔진으로 풀 수 있는 문제인지 확인한다.
2. 지역별 하드코딩으로 바로 구현하지 않는다.
3. `rg`/`grep`으로 대상 함수와 테스트 위치를 찾는다.
4. 필요한 범위만 `sed -n`으로 읽는다.
5. 최소 수정한다.
6. 관련 smoke/golden/validation test를 먼저 실행한다.
7. 필요 시 전체 테스트를 실행한다.

금지:
- golden 값 임의 변경
- public API 무단 변경
- region-specific hardcoding 우선 구현

### 3. Smoke / Golden / Validation test 추가

읽을 문서:
- `AGENTS.md`
- 관련 테스트 파일
- 관련 region config
- 관련 규격 notes의 필요한 섹션
- 필요 시 `docs/REFACTOR_PLAN.md`의 validation/smoke/golden 섹션

절차:
1. 기존 테스트 구조를 먼저 확인한다.
2. golden test는 계산 결과 회귀 방어용으로 둔다.
3. smoke test는 입력 누락, 잘못된 값, optional branch, region config 동작을 방어한다.
4. validation test는 사용자 입력/필수 키/양수 조건을 방어한다.
5. 계산 로직을 테스트에 맞추기 위해 왜곡하지 않는다.

주의:
- golden 값 변경은 공식 계산기, 수기 계산, 기존 확정 문서 중 하나의 근거가 있을 때만 허용한다.

#### 4. 단순 docs 문구 수정

대상:
- 오타 수정
- 문장 1~2개 치환
- 특정 문서의 짧은 표현 완화/수정
- 링크/파일명 1~2개 수정

읽을 문서:
- `AGENTS.md`
- 수정 대상 문서의 해당 섹션만

읽지 말 것:
- 관련 없는 문서 전체
- `project_log.md`
- `PROJECT_CHARTER.md`
- `AGENTS_FULL.md`
- 코드 파일
- 테스트 파일

절차:
1. 지정된 파일의 지정된 섹션 또는 문장만 확인한다.
2. 지정된 문구만 수정한다.
3. 검색, 테스트 실행, 주변 문서 검토를 하지 않는다.
4. 링크/파일명 변경이 있을 때만 참조 검색을 수행한다.
5. 수정 후 해당 파일의 diff만 확인한다.

금지:
- 코드/테스트 수정 금지
- 다른 문서 “겸사겸사” 수정 금지
- 문서 전체 재구성 금지
- 관련 작업을 새로 제안하며 범위 확장 금지

운영 팁:
- 문장 1~2개 치환 수준이면 agent보다 사용자가 직접 수정하는 것이 더 빠를 수 있다.

### 5. Notes 내용 정리 / 문서 리팩토링

읽을 문서:
- `AGENTS.md`
- `PROJECT_CHARTER.md`
- `project_brief.md`
- `docs/REFACTOR_PLAN.md`
- 정리 대상 notes/guideline 문서

조건부로 읽을 문서:
- 과거 결정/실패 이력이 필요하면 `project_log.md`

절차:
1. 먼저 문서 역할을 분류한다.
2. 삭제하지 말고 이동/축약/보존 후보로 나눈다.
3. 같은 내용을 여러 문서에 중복 기록하지 않는다.
4. 작업 결과는 `project_log.md`에 기록한다.
5. 앞으로 할 일이 바뀐 경우에만 `docs/REFACTOR_PLAN.md`를 수정한다.
6. 프로젝트 대표 상태가 바뀐 경우에만 `project_brief.md`를 수정한다.