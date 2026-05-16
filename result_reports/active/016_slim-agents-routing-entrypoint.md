# Slim AGENTS Routing Entrypoint

## Goal

Read ` AGENTS_md_slimming_plan.md` and update `AGENTS.md` plus necessary documents so `AGENTS.md` becomes a lite working-rules entrypoint while preserving routing clues. Record the result in Markdown.

## Scope

- Slim `AGENTS.md`.
- Move/preserve detailed guardrails in `AGENT_TASK_ROUTER.md`.
- Fill ` AGENTS_md_slimming_plan.md` as a Markdown route simulation result.
- Record the process-rule decision in `project_log.md`.

## Changed Files

- `AGENTS.md`: reduced from 138 lines to 64 lines and kept only work contract, routing clues, non-negotiable boundaries, document triggers, design gate, and output rules.
- `AGENT_TASK_ROUTER.md`: added Shared Guardrails and a dedicated UI route; ML route is now section 9.
- ` AGENTS_md_slimming_plan.md`: converted the blank route simulation template into a Markdown result table and judgment.
- `project_log.md`: merged a follow-up entry into the 2026-05-16 agent workflow log.

## Verification

- `git diff --check`: OK.
- Route heading check: `AGENTS.md` route list matches `AGENT_TASK_ROUTER.md` sections 1 through 9.
- Guardrail preservation spot check: calculator, ML, UI, region config, archived AGENTS, and report mode triggers are present in `AGENTS.md` and/or `AGENT_TASK_ROUTER.md`.
- Source/docs commit: `f2ec714 docs: slim agent routing entrypoint`.
- Runtime tests were not run because this was documentation-only.

## Known Risks

- ` AGENTS_md_slimming_plan.md` keeps the existing leading-space filename because the user referenced that exact file.
- `AGENTS.md` is intentionally shorter, so future detailed behavior changes should be made in `AGENT_TASK_ROUTER.md` rather than expanding `AGENTS.md` again.

## Commit / Push

- Source/docs commit: `f2ec714`.
- Report creation commit: `5f6490b`.
- Push: confirmed. `git push` reported `eae6ca1..5f6490b  main -> main`.

## Lifecycle Check

- Existing active reports before this report: 4 (`012` through `015`).
- This report becomes active report `016`.
- `result_reports/summaries/` and `result_reports/archive/` already exist.
- Active report count after this report is below the 8-12 routine maintenance trigger, so no summary/archive maintenance is required.
