# 141 Add Project Memory Recall Gate

## Goal

과거 decision, procedure, error, open question에 의존하는 작업이 backend-neutral memory seed의 관련 entry를 제한 확인하도록 기본 recall gate를 추가한다.

## Scope

- `AGENTS.md`에 짧은 seed recall hook 추가
- `AGENT_TASK_ROUTER.md`에 상세 recall gate 추가
- 이 Compact report 작성
- seed, 기존 report/summary/archive, `project_log.md`, code/test/config는 변경하지 않음

## Task Results

- `AGENTS.md` Routing에 과거 기억 의존 작업의 topic/keyword 단위 seed 확인 hook과 source 범위 제한 원칙을 추가했다.
- `AGENT_TASK_ROUTER.md`에 `Project Memory Recall Gate`를 추가해 trigger, `rg -n`/`sed -n` 기반 확인 방법, 문서 우선순위, 충돌 검증과 대량 archive/report 읽기 금지를 정의했다.
- Recall gate는 seed를 지시 owner가 아닌 evidence/staging source로 취급하며, current prompt와 active owner rules/docs를 우선한다.

## Changed Files

- `AGENTS.md` - Project Memory Seed recall hook 추가
- `AGENT_TASK_ROUTER.md` - 상세 Project Memory Recall Gate 규칙 추가
- `result_reports/active/141_add-project-memory-recall-gate.md` - 작업 결과 Compact report

## Verification

- `git diff --check` - source/docs 커밋 전 통과; report 커밋 전 재실행 예정.
- `rg -n "project_memory_seed|memory seed|recall|topic|keyword|archive|source summary|owner doc" AGENTS.md AGENT_TASK_ROUTER.md` - hook, triggers, 제한 확인 방법, 우선순위와 금지 규칙 확인.
- `git diff --name-only` - source/docs 커밋 전 변경 파일이 `AGENTS.md`, `AGENT_TASK_ROUTER.md`뿐임을 확인.
- Scope compliance - `result_reports/memory/project_memory_seed.md`, 기존 reports/summaries/archive, `project_log.md`, code/test/config를 수정하지 않음.

## Checklist

- `AGENTS.md`에 짧은 recall hook이 추가되었는가? Yes.
- `AGENT_TASK_ROUTER.md`에 상세 recall gate가 추가되었는가? Yes.
- seed를 전체 읽지 않고 topic/keyword 제한 확인하도록 명시했는가? Yes.
- source summary/report로 내려가는 조건이 명시되었는가? Yes.
- memory seed가 current prompt/rules/owner docs보다 우선하지 않는다고 명시했는가? Yes.
- 기존 seed, reports, summaries, `project_log.md`를 수정하지 않았는가? Yes.

## Known Risks

- Topic/keyword 검색어 선택이 너무 좁으면 relevant seed entry를 놓칠 수 있으므로, 충돌이나 불확실성이 남는 경우 owner doc 또는 source summary/report로 제한 검증해야 한다.
- 이 작업은 recall 규칙만 추가하며 seed entry나 backend retrieval 구현은 변경하지 않는다.

## Commit / Push

- Source/docs commit: `0f2e8c169add980fe680607d0981f6bcf2406d16` (`docs: add project memory recall gate`)
- Report commit: 이 파일을 포함하는 별도 `report: ...` 커밋으로 생성
- Push: report commit 생성 후 `origin/work/ui-ux-ssot-adoption`으로 push하고 최종 출력에서 확인

## Project Memory Delta

- type: `procedure`
  topic: `predictor_v3 project memory recall gate`
  content: `predictor_v3 agents use a recall gate for work that depends on prior decisions, procedures, errors, or open questions: search relevant project memory seed topics or keywords first, inspect only matched entry context, and consult source summaries or reports only when owner docs and the seed are insufficient or conflicting.`
  keywords:
    - predictor_v3
    - project memory seed
    - recall gate
    - topic search
  assertionStatus: `verified`
  source: `AGENTS.md Routing; AGENT_TASK_ROUTER.md Project Memory Recall Gate; source commit 0f2e8c169add980fe680607d0981f6bcf2406d16`
