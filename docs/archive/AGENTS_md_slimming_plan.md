# AGENTS.md Slimming Route Simulation

## Goal

`AGENTS.md`를 매 세션 시작용 lite entrypoint로 줄이되, 작업자가 `AGENT_TASK_ROUTER.md`의 올바른 섹션으로 이동할 수 있는 routing clue를 유지한다.

## Route Simulation Results

| Case | Scenario | Expected Route | Report Mode | Result |
| --- | --- | --- | --- | --- |
| 1 | 파일 수정 없는 push 확인 | Result Report Workflow의 No-report / terminal-only mode | No-report / terminal-only | OK |
| 2 | 단순 docs 문구 수정 | `### 5. 단순 docs 문구 수정` | Compact report, 파일 수정 시 report required | OK |
| 3 | ISO16358 계산 로직 수정 | `### 2. Logic 수정 / 계산 엔진 수정` + Shared Guardrails의 calculator boundary | Full report | OK |
| 4 | Commit / Git 정리 | `### 1. Commit / Git 정리` + Documentation Sync & Lifecycle Gate | Report required if tracked files changed | OK |
| 5 | ML feature 수정 | `### 9. ML/Predictor 수정` + Shared Guardrails의 ML boundary | Full report if model/schema behavior changes | OK |
| 6 | Agent/router 문구 수정 | `### 6. Agent rule / router 수정` | Compact report | OK |

## Judgment

- `AGENTS.md`가 너무 얇아져 routing clue가 사라졌는가?
  아니오. 작업 유형 목록, document trigger, non-negotiable boundary가 남아 있어 router 진입 단서는 유지된다.
- 중복 상세 규칙이 아직 과하게 남았는가?
  아니오. 세부 절차와 조건부 문서 읽기 규칙은 `AGENT_TASK_ROUTER.md`로 이동했고, `AGENTS.md`는 시작 단서와 절대 경계만 유지한다.
- 추가 보정 필요 여부:
  현재 보정 불필요. 향후 route case가 늘어나면 이 파일의 simulation table에 case만 추가한다.
