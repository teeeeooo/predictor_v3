# Active Owner Map

## Role

Route a task to the smallest durable owner, root, index, or repository-local Skill needed after `AGENTS.md`. This is not an exhaustive document inventory.

Use it only when ownership is not already clear from the task or matching Skill. Stop once the task owner and focused evidence are known.

## Maintenance

- Update this map only when a top-level owner/root/index/Skill is added, retired, moved, or changes responsibility.
- Do not list individual standards, designs, historical records, snapshots, archives, or legacy files here.
- Use filesystem search when completeness matters.

## Owner Routes

| Need | Start here | Continue only when needed |
| --- | --- | --- |
| Agent rules | `AGENTS.md` | matching repo-local or global Skill |
| Long-term/current direction | `PROJECT_CHARTER.md`, `project_brief.md`, `docs/WORK_PLAN.md` | `docs/REFACTOR_PLAN.md` for structural candidates |
| Document sync/lifecycle | `docs/agent_workflows/DOCUMENT_SYNC_AND_LIFECYCLE.md` | this map and changed owner |
| Recall / durable memory | `result_reports/memory/project_memory_seed.md` | one matching `docs/decisions/` or `docs/failures/` record, then current owner |
| Durable chronology | `project_log.md` | latest relevant entries only |
| Mechanical change gates | `docs/agent_workflows/AGENT_CHANGE_GATES.md` | affected checker/hook and focused tests |
| Architecture | `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md` | nearest architecture owner and design evidence |
| UI | `docs/ui_ux/README.md` | matching UI/UX owner; global table/window Skill when applicable |
| Calculator/standards | `.agents/skills/calculator/SKILL.md`, `docs/README.md` | matching standard/region owner and focused evidence |
| ML/Predictor | `.agents/skills/ml-predictor/SKILL.md` | architecture, knowledge, or DEV-smoke owner named there |
| Packaging/dependencies | `.agents/skills/packaging/SKILL.md`, `docs/development/dependencies.md` | `docs/PACKAGING.md` and app-scoped requirements |
| Design evidence | `docs/designs/README.md` | one matching active design record |

## Historical Evidence

- Historical Result Records under `result_reports/` remain searchable evidence but are not an active workflow or required change artifact.
- `result_reports/REPORT_INDEX.md` remains a historical discovery index.
- `docs/archive/`, result-report legacy material, and memory archives are not default reads.
- Current behavior remains owned by active source and owner documents even when historical evidence explains why it exists.
