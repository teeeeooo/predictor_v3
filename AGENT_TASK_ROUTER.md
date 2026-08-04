# Task Routing Rules

`AGENTS.md`가 mandatory repository entrypoint이고 이 문서는 route map이다.
작업 유형을 분류한 뒤 matching section과 직접 owner 문서만 읽는다. 설치된
Engineering Workflow role contract가 적용되면 generic role/lane,
Build → Gate → Close, evidence/re-proof, merge/synchronization/hygiene,
role-specific reporting은 그 contract가 소유한다. Repository 내부 authority는
`AGENTS.md` → 이 router → matching workflow/domain owner → reference evidence
순으로 해석하며, 이 router는 generic Engineering Workflow 절차를 재정의하지 않는다.

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

## Common Route Gates

이 section은 절차를 복제하지 않고 repository-specific owner를 찾는 gate만 둔다.

- Project hard boundary와 standalone baseline: `AGENTS.md`.
- 새/moved owner, public/schema/registry/resolver, cross-layer responsibility:
  matching architecture owner와
  `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`.
- Repository-specific staged enforcement와 warning-first structure checks:
  `docs/agent_workflows/AGENT_CHANGE_GATES.md`.
- Conditional Result Record trigger, path/index, same-change atomicity:
  `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`.
- Result Record/closeout/handoff의 Memory Review:
  `docs/agent_workflows/PROJECT_LOG_AND_MEMORY.md`.
- Active owner map, work-plan/log/document lifecycle synchronization:
  `docs/agent_workflows/DOCUMENT_SYNC_AND_LIFECYCLE.md`.
- Matching behavior validation은 해당 workflow/domain owner가 소유한다.
  Engineering Workflow role이 적용되면 generic evidence reuse/re-proof,
  Git/merge/synchronization, role reporting은 그 role contract를 따른다.

### Architecture Triage

다음 중 하나가 Yes이면 Architecture route와 matching owner를 함께 연다.

- 새 Model / Service / Controller / Shell / Adapter / View / Policy 책임
- 한 파일에 state, UI, calculation, formatting, I/O가 새로 혼합됨
- 새 public/helper/schema/registry/resolver boundary
- 반복 가능한 local hotfix 또는 sibling surface 공통화 후보
- 새 source file 또는 기존 hotspot에 큰 책임 추가

prompt가 owner/tests를 충분히 고정하면
`prompt-supplied boundary is sufficient`로 진행할 수 있다. 그렇지 않으면
Design Gate 또는 별도 audit/design slice를 사용한다.

## 1. Commit / Git

읽기:

- `AGENTS.md`
- Result Record trigger/commit atomicity가 관련되면
  `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`
- owner/document synchronization이 관련되면
  `docs/agent_workflows/DOCUMENT_SYNC_AND_LIFECYCLE.md`

이 route는 repository-specific record/document owner를 찾기 위한 것이다.
Generic stage/commit/push/merge 순서와 role-specific completion reporting은
적용 중인 Engineering Workflow role contract가 있으면 그 authority를 따른다.

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
