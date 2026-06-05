# 215 — Harness Workflow Owner Cleanup

## Goal

Reduce agent harness drift by moving long workflow procedures out of
`AGENT_TASK_ROUTER.md` and into dedicated owner documents, while keeping
`AGENTS.md` as the lite entrypoint and `AGENT_TASK_ROUTER.md` as a routing
gate map.

## Scope

- Audited `ACTIVE_DOCUMENTS.md`, `AGENTS.md`, and `AGENT_TASK_ROUTER.md`
  owner relationships.
- Added dedicated workflow owner docs under `docs/agent_workflows/`.
- Updated `ACTIVE_DOCUMENTS.md` with the new workflow owner docs.
- Slimmed `AGENT_TASK_ROUTER.md` by replacing long procedure bodies with
  short gates that route to owner docs.
- Shortened the table rule in `AGENTS.md` to toolkit-neutral contract wording.
- Added a compact `project_log.md` milestone entry.

## Non-goals

- No code changes.
- No tests changed.
- No BatchCaseTable or UI implementation changes.
- No report lifecycle/archive movement.
- No memory seed maintenance.

## Audit Result

`ACTIVE_DOCUMENTS.md` showed only two agent harness entrypoints:

- `AGENTS.md` as the lite entrypoint;
- `AGENT_TASK_ROUTER.md` as both task routing and workflow owner.

That overloaded `AGENT_TASK_ROUTER.md` with report workflow, read-budget,
memory/project-log, smoke-loop, documentation lifecycle, and task routing
content. The overload made "read only necessary sections" harder to follow,
because the router itself had become a long workflow manual.

## Implemented Structure

New workflow owner docs:

- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`
- `docs/agent_workflows/DIFF_READ_BUDGET.md`
- `docs/agent_workflows/PROJECT_LOG_AND_MEMORY.md`
- `docs/agent_workflows/SMOKE_LOOP_MODE.md`
- `docs/agent_workflows/DOCUMENT_SYNC_AND_LIFECYCLE.md`

`AGENT_TASK_ROUTER.md` now keeps short gates for those workflows and links to
the owner docs instead of carrying the detailed procedures inline.

`ACTIVE_DOCUMENTS.md` now has an `Agent Workflow Docs` inventory section and
changes `AGENT_TASK_ROUTER.md` from "workflow owner" to "routing index and gate
map".

## AGENTS.md Cleanup

`AGENTS.md` remains the lite entrypoint. The table rule was shortened from a
PyQt-specific implementation statement to toolkit-neutral contract wording:

- table-shaped UI uses `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`;
- toolkit details live in the relevant adapter;
- Excel-like parity checklist is the completion standard.

## Router Cleanup

`AGENT_TASK_ROUTER.md` was reduced from 800+ lines to under 500 lines. It now
keeps:

- route index;
- shared hard boundaries;
- architecture/design gates;
- short workflow pointers;
- task-specific owner document gates.

Detailed workflow procedure now lives in owner docs.

## Project Log

Added a compact `2026-06-05 — Agent workflow owner split` entry because this
is a process-rule and harness architecture change.

## Verification

- `git diff --check` — passed.
- `python3 -B tools/check_code_structure.py` — passed with the pre-existing
  `ui_tk/sections/bin_detail_panel.py` LOC soft warning.
- `git status --short` — only intended harness docs, workflow docs, project
  log, and this report were modified/created.
- `wc -l AGENT_TASK_ROUTER.md AGENTS.md docs/agent_workflows/*.md` — router
  is now under 500 lines; detailed workflow procedure is split into focused
  owner docs.

Not planned:

- `pytest`, because this is a docs/harness workflow cleanup with no code/test
  changes.
- GUI smoke, because no UI implementation changed.

## Known Risks

- Some workflow details are now in new owner docs. Future tasks must follow
  router pointers instead of expecting all details inline.
- The new docs are intentionally concise. If a future task needs more detail,
  extend the owner doc rather than expanding `AGENT_TASK_ROUTER.md` again.

## Scope Compliance

- Code files were not modified.
- Existing active report/archive lifecycle was not changed.
- `result_reports/memory/project_memory_seed.md` was not modified.

## Commit / Push

- Commit: final task commit hash is reported in the terminal summary.
- Push: completed after final commit.

## Project Memory Delta

```yaml
- type: decision
  topic: agent workflow owner split
  content: >
    predictor_v3 keeps AGENTS.md as the lite entrypoint and AGENT_TASK_ROUTER.md
    as a routing gate map; detailed result report, diff/read budget,
    project log/memory, smoke-loop, and documentation lifecycle procedures live
    under docs/agent_workflows/.
  keywords:
    - predictor_v3
    - agent workflow
    - AGENT_TASK_ROUTER
    - read budget
    - result report
  assertionStatus: verified
  source: result_reports/active/215_harness-workflow-owner-cleanup.md
```
