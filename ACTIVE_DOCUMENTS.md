# Active Owner Map

## Role

This map routes a task to the smallest durable owner, root, index, or repository-local Skill needed after `AGENTS.md`. It is intentionally not an exhaustive active-document inventory.

Use it only when ownership is not already clear from the task or matching Skill. Discover child documents from the nearest owner README, index, or Skill when required.

## Use And Maintenance

- Start with the matching row and expand only when behavior, ownership, or evidence remains unclear.
- Treat rows as route choices, not a mandatory read bundle.
- Stop once the task's owner and focused evidence are clear.
- Update this map only when a top-level owner/root/index/Skill is added, retired, moved, or changes responsibility.
- Do not list individual standards, designs, records, guides, snapshots, archive, or legacy files here.
- Use filesystem search when completeness matters.

## Owner Routes

| Need | Start here | Continue only when needed |
| --- | --- | --- |
| Agent rules | `AGENTS.md` | matching repo-local Skill or governance owner |
| Long-term/current direction | `PROJECT_CHARTER.md`, `project_brief.md`, `docs/WORK_PLAN.md` | `docs/REFACTOR_PLAN.md` for structural candidates |
| Document sync/lifecycle | `docs/agent_workflows/DOCUMENT_SYNC_AND_LIFECYCLE.md` | this map and changed owner |
| Durable history/memory | `project_log.md`, `result_reports/memory/project_memory_seed.md` | focused keyword/source-trace reads only |
| Result records | `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md` | `result_reports/REPORT_INDEX.md` |
| Mechanical change gates | `docs/agent_workflows/AGENT_CHANGE_GATES.md` | affected checker/hook and focused tests || Architecture | `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md` | nearest architecture owner and design evidence |
| UI | `.agents/skills/ui-surface/SKILL.md`, `docs/ui_ux/00_UI_UX_SYSTEM.md` | matching UI/UX owner and adapter |
| Calculator/standards | `.agents/skills/calculator/SKILL.md`, `docs/README.md` | matching standard/region owner and focused evidence |
| ML/Predictor | `.agents/skills/ml-predictor/SKILL.md` | architecture, knowledge, or DEV-smoke owner named there |
| Packaging/dependencies | `.agents/skills/packaging/SKILL.md`, `docs/development/dependencies.md` | `docs/PACKAGING.md` and app-scoped requirements |
| Design evidence | `docs/designs/README.md` | one matching active design record |

## Indexed And Historical Evidence

- Design discovery starts at `docs/designs/README.md`.
- Result-record discovery starts at `result_reports/REPORT_INDEX.md`.
- Cross-workstream recall starts at `result_reports/memory/project_memory_seed.md`.
- `docs/archive/` and `result_reports/legacy/` preserve historical evidence and are not default reads.
- Individual records and design evidence explain one point in time; current behavior remains owned by active source and owner documents.
