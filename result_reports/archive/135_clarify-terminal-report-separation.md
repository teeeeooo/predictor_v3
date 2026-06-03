# 135 Clarify Terminal Report Separation

## Goal

tracked file 변경 작업에서 터미널 최종 출력은 짧은 3줄 형식으로 유지하고 상세 결과는 Markdown report에만 기록하도록 workflow 규칙을 명확히 한다.

## Scope

- `AGENT_TASK_ROUTER.md`의 Result Report Workflow 터미널 출력 규칙 보강
- 이 Compact report 작성
- 기존 report, summary, archive, `project_log.md`, 코드, 테스트, config는 변경하지 않음

## Changed Files

- `AGENT_TASK_ROUTER.md` - Markdown report 전용 상세 기록, 성공 시 3종류 줄 제한, blocked 원인 예외, prompt 섹션 해석 규칙 추가
- `result_reports/active/135_clarify-terminal-report-separation.md` - 작업 결과 Compact report

## Verification

- `git diff --check` - 통과
- `rg -n "터미널 출력|Markdown report|체크리스트|Project Memory Delta|task N: OK/NG|modified:|report:" AGENT_TASK_ROUTER.md result_reports/active` - terminal/report 분리 규칙과 report delta 형식 확인
- `git diff --name-only` - report 작성 전 source/docs 변경 파일이 `AGENT_TASK_ROUTER.md`뿐임을 확인
- Scope compliance - 기존 report, summary, archive, `project_log.md`, 코드, 테스트, config를 수정하지 않음

## Checklist

- 터미널 출력 3줄 원칙이 더 명확해졌는가? Yes.
- 상세 결과/체크리스트는 Markdown report에만 작성한다고 명시했는가? Yes.
- prompt의 `[결과 보고 형식]`과 `[코드/문서 체크리스트]`가 terminal detail 출력 요구가 아님을 명시했는가? Yes.
- 새 report의 `Project Memory Delta.keywords`가 YAML list 형식인가? Yes.

## Known Risks

- No-report / terminal-only mode에 이미 정의된 별도 짧은 출력 사례는 유지되며, 이번 보강은 Markdown report가 생성되는 작업의 성공 최종 출력에 적용된다.
- inventory audit, backfill, memory seed, summary/archive lifecycle maintenance는 수행하지 않았다.

## Commit / Push

- Source/docs commit: `65338c559e922fc98a5b042eb56f97880a09a6b5` (`docs: clarify terminal report separation`)
- Report commit: 이 파일을 포함하는 별도 `report: ...` 커밋으로 생성
- Push: report commit 생성 후 `origin/work/ui-ux-ssot-adoption`으로 push하고 최종 출력에서 확인

## Project Memory Delta

- type: `procedure`
  topic: `predictor_v3 terminal final output for report-producing tasks`
  content: `predictor_v3 report-producing tasks write detailed results and checklists only in the Markdown result report, while successful terminal final output uses only task summary, modified paths, and report path lines.`
  keywords:
    - predictor_v3
    - result report
    - terminal output
    - Markdown report
  assertionStatus: `verified`
  source: `AGENT_TASK_ROUTER.md Result Report Workflow terminal output rules; source commit 65338c559e922fc98a5b042eb56f97880a09a6b5`
