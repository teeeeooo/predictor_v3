# 133 Add Project Memory Delta Workflow

## Goal

`AGENT_TASK_ROUTER.md`의 Result Report Workflow에 장기 기억 후보를 backend-neutral 형식으로 기록하는 `Project Memory Delta` 규칙을 추가한다.

## Scope

- `AGENT_TASK_ROUTER.md`의 Result Report Workflow 문구 추가
- 이 Compact report 작성
- 기존 report, summary, archive, `project_log.md`, 코드, 테스트, config는 변경하지 않음

## Changed Files

- `AGENT_TASK_ROUTER.md` - report mode별 `Project Memory Delta` 적용 기준, 필드/enum/품질/lifecycle 규칙 추가
- `result_reports/active/133_add-project-memory-delta-workflow.md` - 작업 결과 Compact report

## Verification

- `git diff --check` - 통과
- `rg -n "Project Memory Delta|retroactive|project_log|Full report|Compact report|No-report" AGENT_TASK_ROUTER.md AGENTS.md` - mode별 기준, retroactive 수정 금지, `project_log.md` 복사 제한 문구 확인
- `git diff --name-only` - report 작성 전 source/docs 변경 파일이 `AGENT_TASK_ROUTER.md`뿐임을 확인
- `git diff --name-only origin/work/ui-ux-ssot-adoption -- AGENT_TASK_ROUTER.md result_reports` - 변경 경로가 `AGENT_TASK_ROUTER.md`와 이 report뿐임을 확인
- Scope compliance - 기존 `result_reports/active/`, `result_reports/archive/`, `result_reports/summaries/` 원문 및 `project_log.md`를 수정하지 않음

## Known Risks

- 기존 report의 backfill은 수행하지 않았으며, 필요 시 새 규칙에 따라 별도 migration/backfill report 작업이 필요하다.

## Commit / Push

- Source/docs commit: `e74605580ab52314e96f930b7b6d199ec0ad414b` (`docs: add project memory delta report workflow`)
- Report commit: 이 파일을 포함하는 별도 `report: ...` 커밋으로 생성
- Push: report commit 생성 후 `origin/work/ui-ux-ssot-adoption`으로 push하고 최종 결과에서 확인

## Project Memory Delta

- type: `procedure`
  topic: `predictor_v3 result report long-term memory candidate workflow`
  content: `predictor_v3 Result Report Workflow records long-term memory candidates in a backend-neutral Project Memory Delta section; Full reports include it by default, Compact reports include it only for qualifying durable items, and No-report/terminal-only mode omits it.`
  keywords: `result report`, `project memory delta`, `backend-neutral`, `workflow`
  assertionStatus: `verified`
  source: `AGENT_TASK_ROUTER.md Result Report Workflow; source commit e74605580ab52314e96f930b7b6d199ec0ad414b`
