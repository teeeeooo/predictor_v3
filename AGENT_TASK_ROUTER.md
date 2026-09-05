# Task Routing Compatibility Pointer

`AGENTS.md` is the repository entrypoint and current authority for agent work. This file is retained temporarily so existing active links do not break during the repository-local Skill migration.

## Task Skills

- Calculator / standards / region / golden: `.agents/skills/calculator/SKILL.md`
- ML / Train / Predict: `.agents/skills/ml-predictor/SKILL.md`
- UI surfaces / tables / windows / input-result-export: `.agents/skills/ui-surface/SKILL.md`
- Packaging / deployment build: `.agents/skills/packaging/SKILL.md`
- Design interrogation: `.agents/skills/grill-me/SKILL.md` only when explicitly invoked

## Governance References

- Mechanical change gates: `docs/agent_workflows/AGENT_CHANGE_GATES.md`
- Document sync/lifecycle: `docs/agent_workflows/DOCUMENT_SYNC_AND_LIFECYCLE.md`
- Result Records: `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`
- Project log/memory: `docs/agent_workflows/PROJECT_LOG_AND_MEMORY.md`

Use `ACTIVE_DOCUMENTS.md` when the durable owner/root/index is unclear. Do not treat this compatibility pointer as a second instruction layer or repeat rules from `AGENTS.md` or the matching Skill.

This file is scheduled for retirement after active inbound references are migrated and a repository search confirms that no current owner depends on it.