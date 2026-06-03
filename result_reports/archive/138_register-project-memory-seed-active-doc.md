# 138 Register Project Memory Seed Active Document

## Goal

`result_reports/memory/project_memory_seed.md`를 backend-neutral active memory staging 문서로 inventory에 등록한다.

## Scope

- `ACTIVE_DOCUMENTS.md`의 scope boundary와 active document inventory 갱신
- 이 Compact report 작성
- seed 본문, 기존 report/summary/archive, `project_log.md`, code/test/config는 변경하지 않음

## Task Results

- `result_reports/memory/*.md`를 active owner inventory에 포함되는 lifecycle-artifact 예외로 명시했다.
- `result_reports/active/**`, `result_reports/summaries/**`, `result_reports/archive/**`는 계속 lifecycle artifact exclusion으로 유지했다.
- `Memory Staging Docs` 섹션에 `result_reports/memory/project_memory_seed.md`의 role, primary inbound, primary outbound를 등록했다.
- seed/staging 문서는 원본 report를 대체하지 않고 source summary/report 추적성을 유지한다는 역할을 row에 기록했다.

## Changed Files

- `ACTIVE_DOCUMENTS.md` - memory staging 예외 및 `project_memory_seed.md` active document row 추가
- `result_reports/active/138_register-project-memory-seed-active-doc.md` - 작업 결과 Compact report

## Verification

- `git diff --check` - source/docs 커밋 전 통과; report 커밋 전 재실행 예정.
- `rg -n "result_reports/memory|project_memory_seed|Project Memory|lifecycle artifact|Excluded|Included" ACTIVE_DOCUMENTS.md` - scope 예외, lifecycle exclusion, inventory row 확인.
- `git diff --name-only` - source/docs 커밋 전 변경 파일이 `ACTIVE_DOCUMENTS.md`뿐임을 확인.
- Scope compliance - `result_reports/memory/project_memory_seed.md`, 기존 reports/summaries/archive, `project_log.md`, code/test/config를 수정하지 않음.

## Checklist

- `result_reports/memory/*.md`가 active memory staging 예외로 명시되었는가? Yes.
- `result_reports/active`, `summaries`, `archive`가 lifecycle artifact로 excluded 상태를 유지하는가? Yes.
- `project_memory_seed.md`의 역할/inbound/outbound가 등록되었는가? Yes.
- seed 본문, 기존 report, summary, `project_log.md`를 수정하지 않았는가? Yes.
- 새 report의 `Project Memory Delta.keywords`가 YAML list 형식인가? Yes.

## Known Risks

- memory staging 문서의 향후 추가 파일이나 supersession 정책은 아직 inventory에 존재하지 않으며 별도 승인 작업이 필요하다.
- active tail backfill, backend 연결, summary/archive lifecycle maintenance는 수행하지 않았다.

## Commit / Push

- Source/docs commit: `eded636c70258ea234abc983f32cef1f1dddd4bc` (`docs: register project memory seed active document`)
- Report commit: 이 파일을 포함하는 별도 `report: ...` 커밋으로 생성
- Push: report commit 생성 후 `origin/work/ui-ux-ssot-adoption`으로 push하고 최종 출력에서 확인

## Project Memory Delta

- type: `procedure`
  topic: `predictor_v3 active document inventory for memory staging`
  content: `predictor_v3 manages result_reports/memory/project_memory_seed.md as an active backend-neutral memory staging document while result_reports active, summaries, and archive paths remain excluded lifecycle artifacts.`
  keywords:
    - predictor_v3
    - active documents
    - project memory seed
    - memory staging
  assertionStatus: `verified`
  source: `ACTIVE_DOCUMENTS.md Scope and Memory Staging Docs; source commit eded636c70258ea234abc983f32cef1f1dddd4bc`
