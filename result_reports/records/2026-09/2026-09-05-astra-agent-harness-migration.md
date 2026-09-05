# Astra Agent Harness Migration

```yaml
record:
  date: 2026-09-05
  topic: astra-agent-harness-migration
  tags: agent-harness, astra, skills, routing, engineering-workflow-retirement
  memory_review: updated
  memory_reason: active agent authority and task-routing topology changed to repo-local Skills
```

## Change Reason

GPT-6 Astra follows long Skill/instruction context strongly, so predictor_v3 needs a smaller always-on contract and progressive task procedure. The previously external Engineering Workflow role/lane framework is retired for new predictor_v3 work.

## Contract / Behavior Changed

- `AGENTS.md` is the single always-on repository execution contract.
- Calculator, ML/Predictor, UI, and packaging procedure moves to repository-local Skills under `.agents/skills/`.
- `grill-me` is explicit-only and asks only decision-bearing questions.
- `ACTIVE_DOCUMENTS.md` remains the durable owner discovery map.
- `AGENT_TASK_ROUTER.md` becomes a temporary compatibility pointer pending a separate retirement slice.
- Engineering Workflow / Worker / Auditor / Orchestrator / Lane authority is removed from current instructions; historical evidence is preserved.

## Evidence And Verification

- OpenAI Codex documentation confirms `$REPO_ROOT/.agents/skills` as REPO-scope Skill discovery and `policy.allow_implicit_invocation: false` for explicit-only invocation.
- OpenAI Astra guidance supports auditing conflicting instruction/Skill context and making user-instruction priority explicit.
- Local Skill/frontmatter validation passed for all five repo Skills; `grill-me` is explicit-only and the four moved workflow paths are absent.
- Focused harness tests passed: `tests/test_tools_check_agent_change_gate.py` and `tests/test_githooks.py` — 16 passed.
- Active stale-path/authority searches found no moved workflow path or current role/lane authority dependency outside intentional migration/history evidence.
- `python3 -B tools/check_agent_change_gate.py --cached` passed on the complete staged change, including Result Record/index/memory coupling.
- `git diff --check` and staged `git diff --cached --check` passed.

## Changed Files

- Agent entrypoint/router/owner map and repository documentation references.
- Four task workflows moved from `docs/agent_workflows/` to `.agents/skills/` and compacted.
- `grill-me` redesigned with explicit-only invocation policy.
- Active architecture/design references and current memory synchronized.
- Governing migration design, this Result Record, index, and project-log process decision added/updated.

## Known Risks

- `AGENT_TASK_ROUTER.md` intentionally remains during Slice 1; deleting it before active inbound references are fully retired would create broken current links.
- Historical documents still contain Engineering Workflow/Lane terminology by design and must not be interpreted as current authority.
- Skill trigger quality depends on concise frontmatter descriptions and should be observed in actual Codex/Astra use before Router retirement.