# Project Brief

이 문서는 새 세션 또는 작업 재개 시 읽는 compact current-state handoff다.
현재 실행 순서나 task-specific pointer 목록은 소유하지 않는다.

## 1. Current State

- 프로젝트는 계산 엔진과 주요 규격 regression 보호망을 기반으로 Tkinter
  calculator profile/UI를 확장하는 단계다. KS C 9306, ISO T1, SASO T3,
  Hong Kong, India ISEER, AHRI, EN14825의 focused smoke/golden 보호망이 있다.
- current calculator entrypoint는 `app_calculator.py` →
  `apps.calculator.app:main` → `apps/calculator/ui/`다. Train/Predict 경로는
  calculator shell과 분리된 상태로 유지한다.
- calculator core, profile/config, UI, result envelope/ML adapter의 책임
  경계가 분리되어 있다. ML / inverse-search 재개 시
  `docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md`를 경계
  기준으로 사용한다.
- EN14825 SEER/SCOP config와 point contract, batch headless handlers, SEER
  dialog, SCOP rebuild/snapshot policy가 구현되어 있다. 현재 실행 우선순위는
  SCOP batch parent-section wiring이며 상세 순서는 `docs/WORK_PLAN.md`가
  소유한다.
- 최근 닫힌 calculator/workflow arc의 compact anchor는
  `result_reports/summaries/416_summary-en14825-batch-agent-change-gate-closeout.md`다.

## 2. Session Start

1. `project_brief.md`에서 stable current state를 확인한다.
2. `docs/WORK_PLAN.md`에서 현재 focus와 정확히 하나의 next action을 확인한다.
3. `docs/WORK_PLAN.md`에 명시 요청으로 작성된 `Session Handoff`가 있을
   때만 그 pointer를 우선 따른다.

## 3. Document Guide

- `AGENTS.md`: 매 작업 시작 시 확인하는 lite rule entrypoint.
- `AGENT_TASK_ROUTER.md`: task route와 compact gate map.
- `PROJECT_CHARTER.md`: 프로젝트 목적과 장기 Phase 1~5 방향.
- `project_brief.md`: 새 세션을 위한 stable current-state handoff.
- `docs/WORK_PLAN.md`: 현재 focus, next action, blockers, constraints, hold를
  관리하는 execution board.
- `project_log.md`: milestone decision, failure, lesson 기록.
- `ACTIVE_DOCUMENTS.md`: active 문서 owner/inbound/outbound map.
- `result_reports/`: task detail, lifecycle summary, completed report archive.

## 4. Next Session Entry

Status: ready for a new implementation session. Updated: 2026-06-20.

Read first:

1. `AGENTS.md` - apply the lite work contract, routing, report, and validation
   rules before reading task-specific files.
2. `docs/WORK_PLAN.md` - use `Session Handoff` for the current pointers and its
   single Next Action; do not reconstruct priority from report history.
3. `result_reports/summaries/416_summary-en14825-batch-agent-change-gate-closeout.md`
   - recover the accepted SCOP rebuild/snapshot boundary without reading the
   archived source reports.

Active blocker / open decision: none. The parent-section slice has no open
schema, calculator, region-config, result-contract, or ownership decision.

Next Action: wire the EN14825 SCOP batch dialog into its parent section as a
thin lifecycle and snapshot-handoff slice.
