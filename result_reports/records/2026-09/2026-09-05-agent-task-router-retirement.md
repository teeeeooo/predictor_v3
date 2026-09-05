# Agent Task Router Retirement

```yaml
record:
  date: 2026-09-05
  topic: agent-task-router-retirement
  tags: agent-harness, routing, skills, router-retirement
  memory_review: no-change
  memory_reason: Active memory already describes the final AGENTS plus repo-local Skills plus ACTIVE_DOCUMENTS topology without relying on the router.
```

## Change Reason

The Astra harness migration left `AGENT_TASK_ROUTER.md` as a temporary compatibility pointer. A fresh repository search after Slice 1 found no current active owner that depends on it, so retaining the extra routing layer would only preserve redundant instruction surface.

## Contract / Behavior Changed

- Delete `AGENT_TASK_ROUTER.md` as an active repository instruction file.
- Remove temporary compatibility-pointer wording from current owners.
- Keep historical references in project history, records, archived memory, and legacy designs as evidence.
- Final routing is `AGENTS.md` → matching repository-local Skill → durable owner, with `ACTIVE_DOCUMENTS.md` used only when owner discovery is needed.
## Evidence And Verification

- Fresh active-reference search found only migration/status/history references and one legacy PyQt source note; no current owner required the router.
- The legacy PyQt source note was redirected to the current `ui-surface` Skill and shared table contract.
- `python3 -m pytest -q tests/test_tools_check_agent_change_gate.py tests/test_githooks.py` passed: 16 tests.
- Direct `pytest` first resolved one test module through an unrelated stale checkout path and failed collection; repo-local `python3 -m pytest` resolved the current checkout and passed, so this is recorded as an invocation/path anomaly rather than source failure.
- `python3 -B tools/check_agent_change_gate.py --cached` and `git diff --cached --check` passed on the complete router-retirement change.

## Changed Files

- `AGENT_TASK_ROUTER.md` deleted.
- Current `AGENTS.md`, `ACTIVE_DOCUMENTS.md`, migration design/index, and legacy PyQt relationship note synchronized.
- Project log and Result Record index updated for the completed retirement.

## Known Risks

Historical documents still contain the retired filename by design. They are evidence of the prior harness and must not be treated as current routing instructions.