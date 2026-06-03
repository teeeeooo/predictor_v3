# 142 Add Project Log Policy Header

## Goal

`project_log.md`의 향후 운영 범위를 milestone 역사 로그로 명시해 result report와 granular memory 기록의 반복 복사를 방지한다.

## Scope

- `project_log.md` 상단 소개 문장 아래 `Project Log Policy` 섹션 추가
- 이 Compact report 작성
- 기존 날짜별 로그, seed, 기존 reports/summaries/archive, code/test/config는 변경하지 않음

## Task Results

- `project_log.md`는 milestone급 decision, failure, lesson, process-rule change만 기록한다는 policy를 추가했다.
- task 상세 결과, 검증 상세, 체크리스트, 변경 파일 목록은 result report가 소유하고, granular memory candidate는 `Project Memory Delta`와 `result_reports/memory/project_memory_seed.md`가 관리하도록 경계를 명시했다.
- report 본문 또는 seed entry 전문을 log에 반복 복사하지 않는 원칙과, 새 로그 추가 전 최근 2~3개 entry의 merge 가능성을 점검하는 규칙을 명시했다.
- 기존 과거 로그를 보존하며 이 작업에서 기존 날짜별 항목을 재작성, 축약, 삭제하지 않는다고 명시했다.

## Changed Files

- `project_log.md` - 상단 `Project Log Policy` 섹션 추가
- `result_reports/active/142_add-project-log-policy-header.md` - 작업 결과 Compact report

## Verification

- `git diff --check` - source/docs 커밋 전 통과; report 커밋 전 재실행 예정.
- `rg -n "Project Log Policy|milestone|Project Memory Delta|project_memory_seed|result report|기존 과거 로그|최근 2~3개" project_log.md` - 요청된 policy 의미 확인.
- `git diff --name-only` - source/docs 커밋 전 변경 파일이 `project_log.md`뿐임을 확인.
- Scope compliance - `project_log.md` diff는 첫 날짜별 heading 전 policy 삽입뿐이며 기존 dated entry 본문은 수정하지 않음; seed, 기존 reports/summaries/archive, code/test/config를 수정하지 않음.

## Checklist

- `project_log.md` 상단에 policy/header가 추가되었는가? Yes.
- milestone급 decision/failure/lesson/process-rule change만 기록한다는 기준이 명시되었는가? Yes.
- report 본문과 `Project Memory Delta`/seed entry를 반복 복사하지 않는다고 명시했는가? Yes.
- 기존 날짜별 로그 항목을 수정하지 않았는가? Yes.
- seed, reports, summaries, archive를 수정하지 않았는가? Yes.
- 새 report의 `Project Memory Delta.keywords`가 YAML list 형식인가? Yes.

## Known Risks

- Policy는 향후 기록 기준을 명문화하지만, 기존 날짜별 항목을 분류하거나 축약하지 않는다.
- summary/archive lifecycle maintenance와 backend 연동은 수행하지 않았다.

## Commit / Push

- Source/docs commit: `b3ef8f9656d6ea74076a73280803bc76a02c2b12` (`docs: add project log policy header`)
- Report commit: 이 파일을 포함하는 별도 `report: ...` 커밋으로 생성
- Push: report commit 생성 후 `origin/work/ui-ux-ssot-adoption`으로 push하고 최종 출력에서 확인

## Project Memory Delta

- type: `procedure`
  topic: `predictor_v3 project log recording policy`
  content: `predictor_v3 project_log.md records only milestone decisions, failures, lessons, and process-rule changes; task detail belongs in result reports and granular memory candidates belong in Project Memory Delta or the project memory seed without duplicating their full text in the log.`
  keywords:
    - predictor_v3
    - project_log
    - project memory delta
    - logging policy
  assertionStatus: `verified`
  source: `project_log.md Project Log Policy; source commit b3ef8f9656d6ea74076a73280803bc76a02c2b12`
