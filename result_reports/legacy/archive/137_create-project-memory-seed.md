# 137 Create Project Memory Seed

## Goal

summary-compressed project knowledge를 기반으로 backend-neutral `Project Memory Delta` seed 문서를 만들고, repo-local staging 경로 규칙을 등록한다.

## Scope

- `AGENT_TASK_ROUTER.md`에 `result_reports/memory/` 경로와 seed/index 운영 규칙 추가
- `result_reports/memory/project_memory_seed.md` 신규 생성
- 이 Compact report 작성
- 기존 individual report, summary, archive, `project_log.md`, 코드, 테스트, config는 변경하지 않음

## Task Results

### Task 1: Memory Staging Path Rule

- `result_reports/memory/`를 `Project Memory Delta` 기반 seed/index/staging 문서의 repo-local 경로로 등록했다.
- 이 경로가 Memento, Mem0, PostgreSQL, Redis, local index 등 특정 backend 구현에 종속되지 않음을 명시했다.
- memory 문서는 기존 report 원문의 대체물이 아니며 source report 또는 summary 추적성을 유지하도록 규정했다.
- seed/index 작성은 retroactive report 수정이나 summary/archive lifecycle maintenance와 분리된 별도 문서 작업임을 명시했다.

### Task 2: Project Memory Seed

- 지정된 summary 10개를 source 목록으로 포함하는 `project_memory_seed.md`를 작성했다.
- summary의 decision, risk, remaining-work, action, project-log judgment에 해당하는 제한된 section만 읽고 seed를 구성했다.
- Seed entries: `31`개 (`decision` 18, `procedure` 3, `fact` 2, `error` 2, `open_question` 6).
- 모든 seed entry에 필수 필드와 YAML list 형식 `keywords`를 작성했고, `source`에는 summary 파일명과 covered report 범위를 포함했다.
- 검증 전 또는 미완료 follow-up은 `decision`이 아니라 `open_question` + `assertionStatus: observed`로 기록했다.

## Changed Files

- `AGENT_TASK_ROUTER.md` - backend-neutral memory staging 경로와 source/retroactive/lifecycle 분리 규칙 추가
- `result_reports/memory/project_memory_seed.md` - summary 기반 backend-neutral memory seed 신규 문서
- `result_reports/active/137_create-project-memory-seed.md` - 작업 결과 Compact report

## Verification

- `git diff --check` - source/docs 변경 stage 전 및 commit 시 통과; report 커밋 전 재실행 예정.
- `git diff --name-only` / staged path 확인 - source/docs 커밋은 `AGENT_TASK_ROUTER.md`, `result_reports/memory/project_memory_seed.md`만 포함.
- `rg -n "result_reports/memory|Project Memory Seed|Project Memory Delta|keywords:|assertionStatus|source:" AGENT_TASK_ROUTER.md result_reports/memory/project_memory_seed.md` - staging 규칙 및 seed 필드 존재 확인.
- Entry field count - seed 내 `type`, `keywords`, `assertionStatus`, `source`가 각각 `31`개임을 확인.
- Scope compliance - 기존 report/summary/archive/`project_log.md` 원문, code/test/config, active tail은 수정하지 않음.

## Checklist

### Task 1

- `result_reports/memory/` 용도가 backend-neutral로 정의되었는가? Yes.
- 기존 report 원문 대체물이 아님을 명시했는가? Yes.
- seed/index 생성이 retroactive report 수정이 아님을 명시했는가? Yes.

### Task 2

- summary 기반으로만 seed를 만들었는가? Yes; individual archived report 본문은 읽지 않음.
- seed 항목이 `25-40`개 이내로 유지되었는가? Yes; `31`개.
- `keywords`가 모두 YAML list인가? Yes.
- `source`가 summary와 covered report 범위를 추적 가능하게 적혀 있는가? Yes.
- 가설과 확정 decision을 구분했는가? Yes; unresolved follow-up은 `open_question`으로 작성.

## Known Risks

- Seed는 summary가 압축한 정보에 기반하므로 개별 report 수준의 evidence 전체를 재현하지 않는다.
- active reports `133-136`의 delta는 seed 입력 대상 summaries에 포함되지 않았으며 active tail backfill은 수행하지 않았다.
- backend import 또는 seed supersession 정책은 별도 authorized task가 필요하다.

## Commit / Push

- Source/docs commit: `bf216654c6600c7cf84ccc2b8a1e1b36ec1d80da` (`docs: add backend-neutral project memory seed`)
- Report commit: 이 파일을 포함하는 별도 `report: ...` 커밋으로 생성
- Push: report commit 생성 후 `origin/work/ui-ux-ssot-adoption`으로 push하고 최종 출력에서 확인

## Project Memory Delta

- type: `fact`
  topic: `predictor_v3 backend-neutral project memory seed creation`
  content: `predictor_v3 now contains a backend-neutral project memory seed staged at result_reports/memory/project_memory_seed.md with 31 entries derived from ten existing summary reports covering archived work through report 131.`
  keywords:
    - predictor_v3
    - project memory delta
    - memory seed
    - summary provenance
  assertionStatus: `verified`
  source: `result_reports/memory/project_memory_seed.md; source commit bf216654c6600c7cf84ccc2b8a1e1b36ec1d80da`
