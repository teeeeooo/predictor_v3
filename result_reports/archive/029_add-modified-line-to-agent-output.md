# 029_add-modified-line-to-agent-output

## Goal
- 모든 agent 작업의 터미널 결과 보고에 `modified: <paths>` 한 줄을 추가하도록 규칙을 명시한다. report 파일을 열기 전에도 실제 수정/생성/삭제된 파일을 한눈에 확인할 수 있게 한다.

## Scope
- `AGENTS.md`
  - `## Output` 섹션 하단에 터미널 결과 보고의 3-line 형식 (task별 OK/NG → `modified:` → `report:`)을 추가했다.
  - `modified:` 작성 규칙(실제 변경 파일만, report-only는 report 파일만, blocked는 `modified: none`, unrelated/pre-existing dirty 파일 제외)을 명시했다.
- `AGENT_TASK_ROUTER.md`
  - `Result Report Workflow` 안의 `터미널 출력:` block을 표준 3-line 형식으로 확장했다.
  - `modified:` 작성 규칙을 항목으로 정리했다 (실제 변경 파일만, source/docs/report 병기 가능, report-only는 report 파일만, blocked는 `modified: none`, unrelated/pre-existing dirty 파일 제외).
  - `modified:`는 사람용 보조 정보이며 report 내부 `Changed Files` 섹션은 그대로 유지함을 명시했다.

## Non-goals
- code / tests / fixture / workbook / reference_files / UI / profile resolver / `core/calculator_profiles.py` 수정하지 않는다.
- 작업 유형 분류 (Task Routing Rules) 자체 변경 금지.
- Documentation Sync & Lifecycle Gate, report mode, lifecycle check 규칙 약화 금지.
- 기존 금지 규칙 완화 금지.

## Verification
- `git branch --show-current` → `main` 확인 후 작업했다.
- `result_reports/{active,archive,summaries}` 전체 report 번호 최대값 028을 확인하고 다음 번호 029를 사용했다.
- commit 전 `git status` / `git diff --stat`로 staged 대상이 `AGENTS.md`, `AGENT_TASK_ROUTER.md`로 한정됨을 확인했다. code/tests/fixture/region config/UI/profile resolver code는 staged 대상에 포함되지 않았다.
- 변경 후 AGENTS.md / AGENT_TASK_ROUTER.md를 다시 살펴 형식이 표준 3-line으로 일관되게 정의되었음을 확인했다.

## Task Results
### task 1 결과
- `AGENTS.md`의 `## Output` 섹션 끝에 다음 4-bullet block을 추가했다.
  - 터미널 결과 보고는 짧게 출력하되 3-line 형식을 유지: task별 `task N: OK/NG - short summary` → `modified: <comma-separated paths>` → `report: <report path>`.
  - `modified:`는 실제 수정/생성/삭제된 파일만 적고, report-only면 report 파일만, blocked면 `modified: none`. unrelated/pre-existing dirty 파일 제외.
  - 상세 내용은 계속 Markdown report에 기록하고 터미널은 짧게 유지.
- 기존 Output 섹션의 commit 분리, 변경 이유/검증/위험 기록 원칙은 그대로 보존했다.
- 계산기/ML/UI 절대 원칙(Non-Negotiable Boundaries)은 수정하지 않았다.

### task 2 결과
- `AGENT_TASK_ROUTER.md`의 `Result Report Workflow` 안의 `터미널 출력:` block을 다음 구조로 확장했다.
  - 표준 출력 형식 3종 줄(`task N: OK/NG - short summary`, `modified: path/to/file1, path/to/file2`, `report: result_reports/active/NNN_name.md`) 명시.
  - 출력 순서: task별 OK/NG 줄 → `modified:` 한 줄 → `report:` 한 줄.
  - `modified:` 작성 규칙을 다섯 가지 sub-bullet으로 정리: 실제 변경 파일만, source/docs/report 병기 가능, report-only는 report 파일만, blocked는 `modified: none`, unrelated/pre-existing dirty 제외.
  - 문제/blocked 발생 시 원인을 짧게 출력한다는 기존 규칙은 유지.
  - `modified:`는 보조 정보이며 report 내부 `Changed Files` 섹션은 그대로 유지함을 명시.
- Documentation Sync & Lifecycle Gate, Report mode, lifecycle check, summary/archive 규칙은 수정하지 않았다.

### task 3 결과
- `result_reports/active/029_add-modified-line-to-agent-output.md`를 생성하고 본 report 양식(Goal / Scope / Non-goals / Verification / Task Results / Changed Files / Known Failures / Risks / Next Suggested Action / Scope Compliance / Commit-Push)을 채웠다.

### task 4 결과
- `git status` / `git diff --stat`으로 변경 범위가 `AGENTS.md`와 `AGENT_TASK_ROUTER.md`로 한정됨을 확인했다.
- 첫 번째 commit: `docs: add modified-file line to agent output` (hash `60f3673`).
- 두 번째 commit: `report: record agent output modified-file rule` (push 직후 hash 확정).
- push: `origin/main`.

## Changed Files
- `AGENTS.md`
- `AGENT_TASK_ROUTER.md`
- `result_reports/active/029_add-modified-line-to-agent-output.md`

## Known Failures / Risks
- 새 출력 규칙은 향후 agent run에 단계적으로 적용되며, 과거 report들은 retro로 갱신하지 않는다.
- agent가 `modified:` 줄에 unrelated/pre-existing dirty 파일을 실수로 포함하지 않도록 조심해야 한다. 작업 직전 `git status` 비교가 필요하면 보조적으로 사용 가능.

## Next Suggested Action
- 다음 agent run부터 `modified:` 한 줄을 표준으로 출력하고, 실제 운영에서 형식이 잘 적용되는지 모니터링한다.

## Scope Compliance
- code: 수정하지 않았음
- tests: 수정하지 않았음
- fixtures: 수정하지 않았음
- workbook/reference_files: 수정하지 않았음
- UI: 수정하지 않았음
- profile resolver code: 수정하지 않았음 (`core/calculator_profiles.py` 그대로)
- git pull/merge/rebase: 수행하지 않았음

## Commit / Push
- source/docs commit: `60f3673 docs: add modified-file line to agent output`
- report commit: `report: record agent output modified-file rule`
- pushed branch: `origin/main`
