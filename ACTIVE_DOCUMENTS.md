# Active Owner Map

## Role

This map routes a task to the smallest top-level owner, root, or index needed
after `AGENTS.md` and `AGENT_TASK_ROUTER.md`. It is intentionally not an
exhaustive active-document inventory.

Use it to find the first durable owner. Discover child documents from that
owner's local README, index, or workflow only when the task requires them.

## Use And Maintenance

- Start with the matching row and expand only when behavior, ownership, or
  evidence remains unclear.
- Treat the rows as route choices, not a mandatory read bundle.
- Stop once the task's owner and focused evidence are clear.
- Update this map only when a top-level owner/root/index is added, retired,
  moved, or changes responsibility.
- Do not update it for each child document or for ordinary multi-document
  wording changes.
- Discover child standards, designs, guides, adapters, and snapshots from the
  nearest owner README, index, or workflow.
- Do not list individual standard, design, result, guide, snapshot, archive, or
  legacy files here.
- Use filesystem search when completeness matters; do not generate a tracked
  full-file inventory.

## Owner Routes

| Need | Start here | Continue only when needed |
| --- | --- | --- |
| Agent rules and routing | `AGENTS.md`, `AGENT_TASK_ROUTER.md` | matching workflow owner |
| Long-term and current direction | `PROJECT_CHARTER.md`, `project_brief.md`, `docs/WORK_PLAN.md` | `docs/REFACTOR_PLAN.md` for structural candidates |
| Document sync and lifecycle | `docs/agent_workflows/DOCUMENT_SYNC_AND_LIFECYCLE.md` | this owner map and the changed owner document |
| Durable history and memory | `project_log.md`, `result_reports/memory/project_memory_seed.md` | focused keyword/source-trace reads only |
| Result records | `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md` | `result_reports/REPORT_INDEX.md` |
| Staged objective gates | `docs/agent_workflows/AGENT_CHANGE_GATES.md` | affected checker/hook and focused tests |
| Architecture | `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md` | nearest architecture owner and design evidence |
| UI | `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`, `docs/ui_ux/00_UI_UX_SYSTEM.md` | `docs/ui_ux/README.md` and matching adapter/policy |
| Calculator and standards | `docs/agent_workflows/CALCULATOR_WORKFLOW.md`, `docs/README.md` | matching standard/region owner and focused evidence |
| ML and Predictor | `docs/agent_workflows/ML_PREDICTOR_WORKFLOW.md` | architecture, knowledge, or DEV-smoke owner named there |
| Packaging and dependencies | `docs/agent_workflows/PACKAGING_WORKFLOW.md`, `docs/development/dependencies.md` | app-scoped requirements and packaging evidence |
| Design evidence | `docs/designs/README.md` | one matching active design record |

## Indexed And Historical Evidence

- Design discovery starts at `docs/designs/README.md`.
- Result-record discovery starts at `result_reports/REPORT_INDEX.md`.
- Cross-workstream recall starts at
  `result_reports/memory/project_memory_seed.md`.
- `docs/archive/` and `result_reports/legacy/` preserve historical evidence;
  they are not default reads.
- Individual records and design evidence explain one point in time; current
  behavior remains owned by active source and owner documents.
