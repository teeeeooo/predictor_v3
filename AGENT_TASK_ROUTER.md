## Task Routing Rules

작업자는 먼저 작업 유형을 분류한 뒤, 해당 유형에 필요한 문서만 읽는다.
불필요한 긴 문서를 습관적으로 읽지 않는다.

### 1. Commit / Git 정리

읽을 문서:
- `AGENTS.md`

조건부로 읽을 문서:
- 문서 리팩토링, TODO 변경, 계획 변경, 완료 기록이 포함된 diff인 경우:
  - `project_log.md`의 최근 섹션 또는 관련 키워드
  - `project_brief.md`
  - `docs/REFACTOR_PLAN.md`의 관련 섹션

읽지 말 것:
- `PROJECT_CHARTER.md`
- `AGENTS_FULL.md`
- 규격별 notes 문서 전체

절차:
1. `git status`
2. `git diff --stat`
3. 변경 파일 성격 확인
4. Documentation Sync & Lifecycle Gate 수행 → [문서 동기화 판단] 출력
5. 갱신 필요로 판단된 문서가 있으면 먼저 수정하고, 수정 완료 후에만 다음 단계로 진행한다.
   갱신 불필요면 바로 테스트 확인 단계로 진행한다.
6. 테스트 결과가 사용자가 보고한 내용과 일치하는지 확인
7. 명확한 commit message 작성
8. commit/push 수행

#### Documentation Sync & Lifecycle Gate

commit 전에 diff를 보고 문서 갱신 필요 여부뿐 아니라, 기존 문서의 수명주기를 함께 판단한다.

1. `project_log.md`
   - 새 작업 결과, 실패, 결정, 교훈은 append한다.
   - 이미 끝난 작업의 상세 기록은 `project_log.md`에 보존한다.
   - `project_log.md`는 append 중심 문서이므로 과거 로그를 임의 삭제하지 않는다.
   - 갱신 여부를 diff 크기만으로 판단하지 않는다.
   - 작은 코드 변경이라도 architecture direction, phase boundary, resolver/adapter/registry/manifest contract, schema boundary, routing decision, compatibility layer, 중요한 guard-test decision을 고정하면 로그 대상이다.
   - 단순 오타, 포맷팅, 주석 문구 조정, 기계적 테스트 유지보수처럼 의사결정이 없는 변경은 로그를 생략할 수 있다.
   - 갱신이 필요하면 새 로그를 바로 append하기 전에 최근 로그 2~3개만 확인한다.
   - 같은 phase, 같은 architecture decision, 같은 작업 묶음이면 새 섹션을 만들지 말고 해당 최근 로그에 짧게 merge/update한다.
   - 오래된 로그 전체를 훑거나 대규모 재작성하지 않는다.
   - 기존 failure, decision, lesson 기록은 삭제하지 않는다.
   - 독립 phase 또는 의미가 분리되는 후속 작업이면 새 로그를 append한다.

2. `docs/REFACTOR_PLAN.md`
   - 살아있는 TODO / 보류 항목 / 다음 실행 순서만 유지한다.
   - 완료된 TODO는 다음 중 하나로 처리한다.
     - 단순 완료: 체크/완료 문구 없이 제거하거나 짧게 축약
     - 후속 영향 있음: “완료됨. 후속 TODO는 ...” 형태로 1~2줄만 유지
     - 상세 보존 필요: project_log.md 또는 관련 dev_notes에 기록하고 REFACTOR_PLAN에서는 제거/참조만 남김
   - 새 TODO를 추가할 때는 기존 완료 항목을 함께 줄인다.
   - 같은 섹션에 새 항목만 계속 append하지 않는다.

3. `project_brief.md`
   - 새 대화 시작에 필요한 현재 상태만 유지한다.
   - 완료 이력의 상세 나열을 금지한다.
   - 대표 상태가 바뀌면 기존 문장을 교체/축약하고, 새 문장을 덧붙이기만 하지 않는다.
   - 오래된 “다음 작업”은 최신 우선순위로 교체한다.

4. 규격별 `notes/dev_notes/design_notes`
   - 규격 해석, 계산 근거, schema 의미처럼 나중에 재사용될 지식만 보존한다.
   - 단순 완료 기록은 dev_notes에 중복 추가하지 않고 project_log.md로 보낸다.
   - 이미 REFACTOR_PLAN이나 project_log에 있는 내용을 그대로 복사하지 않는다.

5. `docs/archive/`
   - 원본 분석, 폐기된 계획, 더 이상 active TODO가 아닌 긴 기록만 이동 후보로 분류한다.
   - agent가 임의로 archive 이동/삭제하지 않는다.
   - 이동이 필요하면 “archive 후보”로 보고하고 사용자 승인 후 수행한다.

출력:
- [문서 동기화 판단]
  - project_log.md: 필요/불필요 + 이유
  - REFACTOR_PLAN.md: 필요/불필요 + 이유
  - project_brief.md: 필요/불필요 + 이유
  - 규격별 notes/dev_notes: 필요/불필요 + 이유

주의:
- `temporary.txt`는 로컬 scratch 파일이며 `.gitignore` 대상이므로 커밋하지 않는다.

### 2. Logic 수정 / 계산 엔진 수정

읽을 문서:
- `AGENTS.md`
- 관련 규격의 notes/dev_notes/design_notes 중 필요한 문서
- 필요한 경우 `docs/REFACTOR_PLAN.md`의 해당 섹션
- routing/schema boundary가 관련되면 `docs/architecture/project_architecture.md`의 calculator profile resolver 관련 섹션

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
8. 계산 로직 수정 시 region config와 HW candidate input을 혼동하지 않는다.
9. 계산 엔진이 ML feature schema 또는 UI table schema에 직접 의존하지 않게 한다.
10. ML predicted values는 calculator input adapter를 통해 들어와야 하며 region config에 섞지 않는다.
11. standard-specific dev notes와 architecture 문서의 calculator boundary를 필요한 범위만 확인한다.

금지:
- golden 값 임의 변경
- public API 무단 변경
- region-specific hardcoding 우선 구현

### 3. Coding work / architecture-sensitive changes

대상:
- calculator profile resolver 추가/수정
- region config resolver 추가/수정
- `calc_window.py` routing 변경
- calculator registry / profile manifest / selector behavior 변경
- nested config 후보 또는 schema boundary 변경
- ML output → calculator input adapter 설계
- calculator result schema normalization
- UI, core calculator, config loader, ML module 사이의 연결 변경

읽을 문서:
- `AGENTS.md`
- `docs/architecture/project_architecture.md`의 calculator profile resolver 관련 섹션
- 관련 규격의 dev_notes/notes 중 필요한 섹션
- 필요 시 `docs/REFACTOR_PLAN.md`의 관련 섹션

절차:
1. selector 입력과 output contract를 먼저 정의한다.
2. filename scanning보다 explicit selector/manifest/registry contract를 우선한다.
3. compatibility layer는 얇게 유지하고, 초기에는 기존 flat `config_path` 또는 기존 calculator input을 반환한다.
4. ambiguous selector combination은 fail-fast 한다.
5. local one-off conditional로 구조 문제를 덮지 않는다.

금지:
- region config, HW candidate input, ML feature schema, calculator result schema 혼합
- nested region config를 production calculator에 직접 전달
- calculator engine이 UI table schema 또는 ML registry에 직접 의존
- public API 또는 diagnostics schema를 별도 phase 없이 변경

### 4. Smoke / Golden / Validation test 추가

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

### 5. 단순 docs 문구 수정

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

### 6. Notes 내용 정리 / 문서 리팩토링

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
