# Task Routing Rules

`AGENTS.md`가 mandatory entrypoint이고 이 문서는 route map이다. 작업 유형을
분류한 뒤 matching section과 직접 owner 문서만 읽는다. 규칙 충돌 시
`AGENTS.md` → 이 router → workflow owner → reference evidence 순으로 해석한다.

## Quick Route Index

| Task | Owner |
| --- | --- |
| Commit / Git | Result workflow, document sync |
| Calculator logic / golden / region | `CALCULATOR_WORKFLOW.md` |
| Architecture-sensitive coding | architecture owner + change gates |
| Smoke / validation | matching behavior owner |
| Docs / agent rules | document lifecycle + changed owner |
| UI | `UI_SURFACE_WORKFLOW.md` |
| ML / Predictor | `ML_PREDICTOR_WORKFLOW.md` |
| Packaging | `PACKAGING_WORKFLOW.md` |

## Common Gates

### Work Boundary

- Goal / Scope / Non-goals / Verification은 `AGENTS.md` Work Contract를
  따른다.
- every changed line은 Goal과 직접 연결되어야 한다.
- ambiguous standard/profile/region/schema combination은 fail-fast한다.
- commit/push와 tracked file 삭제는 사용자 승인이 필요하다.
- 기존 변경 검토는 changed paths/stat, exact-symbol 검색, narrow
  hunk/owner range순으로 시작하고 behavior/ownership가 불명확할 때만
  범위를 넓힌다.
- validation은 matching owner에서 가져오며 unrelated guard나 최종
  focused suite가 이미 커버한 unchanged subset을 반복하지 않는다.

### Architecture Triage

다음 중 하나가 Yes이면 owner boundary를 먼저 정한다.

- 새 Model / Service / Controller / Shell / Adapter / View / Policy 책임
- 한 파일에 state, UI, calculation, formatting, I/O가 새로 혼합됨
- 새 public/helper/schema/registry/resolver boundary
- 반복 가능한 local hotfix 또는 sibling surface 공통화 후보
- 새 source file 또는 기존 hotspot에 큰 책임 추가

prompt가 owner/tests를 충분히 고정하면
`prompt-supplied boundary is sufficient`로 진행할 수 있다. 그렇지 않으면
Design Gate 또는 별도 audit/design slice를 사용한다.

### Staged Change Gate

- objective whitespace, syntax, hard LOC, UI literal 정책은 hard check다.
- reuse/commonization과 hotspot 책임 판단은 기본 warning-first다.
- ordinary source/test/tool/config 변경은 report 부재만으로 실패하지 않는다.
- 예외 UI literal 또는 구조 판단을 durable하게 남길 필요가 있으면 optional
  `change_gate` block을 compact record에 둔다.
- 상세 owner: `docs/agent_workflows/AGENT_CHANGE_GATES.md`.

### Conditional Result Record

다음 변경만 compact record trigger다.

- architecture/owner boundary
- schema, public API, JSON key, diagnostics contract
- calculator formula, golden, fixture, region-config behavior
- agent harness/gate/workflow enforcement
- migration, release, decisive external/manual acceptance evidence
- non-obvious/repeated/cross-owner/platform/manual-only/unguarded UI or bugfix
- explicit user request

그 외는 기본 `report: not created`다. record path, index, same-commit,
Memory Review, terminal 형식은
`docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`가 소유한다.

### Memory Review

다음 trigger에서 `updated` 또는 `no-change + reason`을 판단한다.

- 새 compact record
- milestone/branch closeout
- explicit session handoff
- 장기 중단 workstream 복귀

상세 owner는 `docs/agent_workflows/PROJECT_LOG_AND_MEMORY.md`다.

### Documentation Sync

- owner 역할/inbound/outbound 또는 active doc 집합이 바뀌면
  `ACTIVE_DOCUMENTS.md`를 확인한다.
- current slice/next action이 바뀔 때만 `docs/WORK_PLAN.md`를 갱신한다.
- milestone decision/process rule이면 `project_log.md` 갱신을 판단한다.
- 상세 owner는 `DOCUMENT_SYNC_AND_LIFECYCLE.md`다.

## 1. Commit / Git

읽기:

- `AGENTS.md`
- 필요 시 Result Report / Document Sync owner

절차:

1. `git status --short`, diff stat, focused validation 상태를 확인한다.
2. 사용자가 승인한 scope만 stage/commit/push한다.
3. compact record가 있으면 source 변경과 같은 commit에 포함한다.
4. final output에 commit hash와 push remote/branch 결과를 남긴다.

## 2. Calculator Logic / Golden / Region

읽기:

- `docs/agent_workflows/CALCULATOR_WORKFLOW.md`
- 관련 standard/region owner의 필요한 heading
- region config 수정 시 `data/region_configs/REGION_CONFIG_RULES.md`

owner가 common engine, standard/profile handler, region config, UI adapter 중
어디인지 먼저 정한다. Formula/golden/fixture/config behavior 변경은 compact
record trigger다. Accepted evidence 없이 expected 값을 변경하지 않는다.

## 3. Architecture-Sensitive Coding

읽기:

- 관련 `docs/architecture/` owner heading
- `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`
- matching workflow owner

owner/input/output/public contract를 먼저 정하고 compatibility layer는 얇게
유지한다. 새 helper/adapter/surface/split/move는 bounded sibling/owner
검색을 수행한다. ordinary internal 구조 변경은 warning-first이며 report를
자동 요구하지 않지만, owner/public contract 변경은 compact record trigger다.

## 4. Smoke / Golden / Validation

- golden은 confirmed result regression, smoke는 user-facing route, validation은
  input/error boundary를 방어한다.
- expected 변경은 accepted evidence가 있을 때만 한다.
- 자동/focused guard를 먼저 실행하고 GUI/manual smoke는 마지막에 bounded하게
  수행한다.
- manual evidence가 최종 승인 근거이거나 자동 guard를 만들 수 없으면 compact
  record를 남긴다.

## 5. Simple Docs

대상 문장/링크 범위만 읽고 코드·테스트·문서 구조를 함께 바꾸지 않는다.
단순 wording/formatting은 record trigger가 아니다.

## 6. Agent Rules / Harness

읽기:

- `AGENTS.md`
- router의 matching section
- 변경하는 workflow/tool owner

entrypoint에는 hard boundary와 trigger만, router에는 routing만, workflow에는
세부 계약만 둔다. 자동 enforcement 변경은 compact record와 focused test가
필요하다.

## 7. Notes / Document Refactor

`DOCUMENT_SYNC_AND_LIFECYCLE.md`를 따르고 문서 owner와 lifecycle 상태를 먼저
분류한다. 신규 standard 구조만 `docs/README.md`,
`docs/DOCS_GUIDELINES.md`, template을 조건부로 읽는다.

## 8. UI

읽기:

- 관련 UI class/function
- `docs/agent_workflows/UI_SURFACE_WORKFLOW.md` matching gate
- table/window/input-result surface의 matching `docs/ui_ux/` owner

UI와 calculator/ML/schema 변경을 분리하고 focused behavior test를 우선한다.
일반 UI 변경은 record trigger가 아니다. 비자명·반복·platform/manual-only,
cross-owner, regression guard 불가 bug는 symptom/cause/fix/guard를 compact
record에 남긴다.

## 9. ML / Predictor

`docs/agent_workflows/ML_PREDICTOR_WORKFLOW.md`와 관련 owner 범위만 읽는다.
feature/schema, leakage, Cooling/Heating separation, monotonicity를 보존한다.
UI surface도 바뀌면 UI route를 함께 적용한다.

## 10. Packaging / Deployment

`docs/agent_workflows/PACKAGING_WORKFLOW.md`와 `docs/PACKAGING.md`를 따른다.
target platform/output/verification을 먼저 확인하고 speculative command를
canonical guidance로 기록하지 않는다. release/deployment 결정은 compact
record trigger다.
