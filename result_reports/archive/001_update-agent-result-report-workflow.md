# 001_update-agent-result-report-workflow

## Goal
- predictor_v3의 agent 결과 보고 방식을 Markdown report 기반 workflow로 전환하는 규칙을 추가한다.
- 모든 CLI/Codex/agent 작업 결과를 `result_reports/active/` 아래 Markdown 파일로 저장하고, 터미널 출력은 task별 OK/NG 한 줄 요약과 report 파일 경로만 남기도록 한다.

## Scope
- `AGENTS.md`: `## 출력` 섹션에 공통 출력 원칙(report 저장, 터미널 한 줄 요약, commit/push) 추가.
- `AGENT_TASK_ROUTER.md`: Section 0과 Section 1 사이에 `### Result Report Workflow` subsection 신설. `### 1. Commit / Git 정리` 절차에 source/docs 커밋과 report 커밋 분리 단계 추가.
- `result_reports/active/` 디렉토리 신설.
- `result_reports/active/001_update-agent-result-report-workflow.md` (본 파일) 생성.
- 두 개의 분리된 커밋(source/docs commit, report commit) 후 push.

## Non-goals
- 코드/테스트/fixture 수정 없음.
- workbook/reference_files 수정 없음.
- ISO 계산 로직 문서 수정 없음.
- 기존 task routing 구조 대규모 재작성 없음.
- 기존 문서 읽기 최소화 정책, Documentation Sync & Lifecycle Gate, 기존 금지 규칙 약화 없음.
- `result_reports/summaries/`와 `result_reports/archive/` 디렉토리는 이번에 생성하지 않는다 (필요 시 추후 생성).

## Verification
- `AGENTS.md` `## 출력` 섹션에 7개 bullet이 추가되어 있다.
- `AGENT_TASK_ROUTER.md`에 `### Result Report Workflow` subsection이 Section 0 직후/Section 1 직전에 존재한다.
- `### 1. Commit / Git 정리` 절차 step 8–9가 source/docs commit과 report commit 분리를 명시한다.
- 본 report 파일이 `result_reports/active/001_update-agent-result-report-workflow.md`에 존재한다.
- 두 개의 commit hash (source/docs commit, report commit)가 `Commit / Push` 섹션에 기록된다.
- 최종 `git status`가 clean이거나 무관한 변경만 남는다 (pre-existing `.devcontainer/devcontainer.json` 삭제 제외).

## Task Results

### task 1 결과
- 수정 파일: `AGENTS.md`
- 수정 내용: `## 출력` 섹션에 다음 원칙을 추가했다.
  - 모든 agent 작업 상세 결과는 `result_reports/active/` 아래 Markdown report로 저장.
  - 파일명 `NNN_verb-target-scope.md` 형식.
  - 터미널은 task별 `OK/NG` 한 줄 요약과 report path만 출력.
  - 문제가 있거나 blocked이면 원인을 짧게 덧붙임.
  - report 파일은 항상 stage/commit/push.
  - 코드/문서 변경 커밋과 report 커밋 분리.
  - 세부 규칙은 `AGENT_TASK_ROUTER.md`의 Result Report Workflow를 따른다고 명시.
- OK/NG: OK

### task 2 결과
- 수정 파일: `AGENT_TASK_ROUTER.md`
- 수정 내용:
  - Section 0 직후, Section 1 직전에 `### Result Report Workflow` subsection 신설.
  - 포함 항목: 경로(`active`/`summaries`/`archive`), 파일명 규칙, 다음 번호 산정 규칙, 터미널 출력 형식, report 기본 섹션 11종, Commit / Push 규칙, 운영(summary/archive/`project_log.md`) 규칙, 주의사항.
  - `### 1. Commit / Git 정리`의 절차 step 8을 "source/docs 커밋 후 report 커밋을 별도로 만들고 push"로 확장, step 9에 "최종 터미널 보고에 source commit hash, report commit hash, pushed branch 포함" 추가.
- OK/NG: OK

### task 3 결과
- 생성 파일: `result_reports/active/001_update-agent-result-report-workflow.md`
- 작성 내용: 본 작업의 Goal / Scope / Non-goals / Verification / Task Results / Changed Files / Known Failures / Next Suggested Action / Scope Compliance / Commit / Push 섹션을 모두 포함.
- OK/NG: OK

### task 4 결과
- source/docs commit: `071b41d` — `docs: add agent result report workflow`
- report commit: 이 commit 자체. hash는 terminal summary에 출력된다 (self-reference 불가).
- push 결과: terminal summary 참조.
- 최종 git status: pre-existing `.devcontainer/devcontainer.json` 삭제만 staged (이번 작업과 무관, 그대로 보존).
- OK/NG: OK

## Test Results
- 본 작업은 docs/rule 수정 작업이므로 별도 테스트 실행 없음.
- 기존 테스트 영향도: 없음 (코드/테스트/fixture 미수정).

## Changed Files
- `AGENTS.md` (변경)
- `AGENT_TASK_ROUTER.md` (변경)
- `result_reports/active/001_update-agent-result-report-workflow.md` (신규)

## Known Failures / Risks
- pre-existing staged change: `.devcontainer/devcontainer.json` deletion이 이번 세션 시작 시점에 이미 staged 상태였음. 이번 작업과 무관하여 커밋에 포함하지 않고 그대로 보존했다. 사용자가 별도로 처리할 항목.
- `result_reports/summaries/`와 `result_reports/archive/` 디렉토리는 이번에 생성하지 않았다. 필요한 시점에 후속 작업에서 생성한다.

## Next Suggested Action
- 다음 agent/Codex 작업부터는 `result_reports/active/002_...md` 형식으로 report를 작성하도록 유지한다.
- `result_reports/active/`에 report가 약 10개 누적되거나 큰 작업 묶음이 끝나는 시점에 첫 summary report 생성을 검토한다.
- 사용자가 원할 경우 `.devcontainer/devcontainer.json` 삭제건의 처리 방향(되돌릴지, 별도 커밋으로 정리할지)을 결정한다.

## Scope Compliance
- code: 수정 없음
- tests: 수정 없음
- fixtures: 수정 없음
- workbook/reference_files: 수정 없음
- unrelated files: 수정/stage 없음 (pre-existing staged 삭제는 그대로 보존)

## Commit / Push
- source/docs commit: `071b41d` — `docs: add agent result report workflow`
- report commit: 이 commit 자체. hash는 terminal summary에 출력된다 (self-reference 불가).
- pushed branch: `main` → `origin/main`
