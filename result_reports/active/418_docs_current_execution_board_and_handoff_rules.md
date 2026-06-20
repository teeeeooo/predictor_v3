# 418 Docs Current Execution Board and Handoff Rules

## Goal

Restore `docs/WORK_PLAN.md` as a current execution board and define an explicit,
non-automatic Session Handoff workflow.

## Scope

- Audited the owner roles of the charter, brief, log, work plan, router,
  documentation workflow, and active-document map.
- Updated five required documents and left `ACTIVE_DOCUMENTS.md` unchanged
  because its role mapping already matched the intended ownership split.
- Did not change code, tests, schemas, calculators, UI, fixtures, golden data,
  report lifecycle state, branches, commits, or remote state.

## Changed Files

- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md`
- `AGENT_TASK_ROUTER.md`
- `docs/agent_workflows/DOCUMENT_SYNC_AND_LIFECYCLE.md`
- `result_reports/active/418_docs_current_execution_board_and_handoff_rules.md`

## Change Summary

- Removed completed-report enumeration and historical-note accumulation from
  the work plan, leaving current focus, one next action, blockers/decisions,
  active constraints, holds, and compact anchors.
- Reduced the project brief to stable current state, session-start discovery
  order, and document roles.
- Added a compact router gate and detailed workflow rules distinguishing
  explicit handoff triggers from ordinary work plan/report maintenance.
- Recorded the owner split as a milestone decision in `project_log.md`.
- Did not create a live `Session Handoff` section because the user requested
  the rules and document cleanup, not an actual session handoff.

## Verification

- `git diff --check`: passed.
- `git status --short`: only the five intended document modifications and this
  new active report were present.
- Targeted `rg` checks confirmed Session Handoff trigger/non-trigger wording.
- Manual structure checks confirmed one Next Action, compact reference anchors,
  no long completed-report list, and no router-level handoff template.

## Known Risks

- Current focus was compacted from existing project state and Summary 416; a
  future priority change still requires an ordinary work plan update.
- No manual GUI check is needed because this task changes documentation only.

## Next Action

Wire the EN14825 SCOP batch dialog into its parent section as a thin lifecycle
slice.

## Commit / Push

- Documentation commit: `664adbb` (`Clarify execution board and handoff ownership`).
- The report commit hash and final push result are reported in terminal output
  to avoid a self-referential report update loop.
