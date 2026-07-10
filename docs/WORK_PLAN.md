# Work Plan

## Purpose

- Own the current slice, one next action, blockers, constraints, and deferred work.
- Keep phase, milestone, and Standard Calculation direction in `project_brief.md`.
- Keep milestone decisions and durable lessons in the log; keep conditional
  evidence in records and structural triggers in `docs/REFACTOR_PLAN.md`.

## Update Rule

- This file is a near-term execution board, not a roadmap or task log.
- Update it only when the current slice, next action, blocker, constraint, or
  hold state changes.
- Do not append report lists, terminal output, or completed-action history.
- Add a Session Handoff only when the user explicitly requests one.

## Current Slice

Agent harness/report lifecycle redesign, legacy migrations, audit corrections,
and the main merge are complete and verified.

## Next Action

Start Standard Calculation Capability Extension design using the capability
boundary and execution order in `project_brief.md`.

## Active Blockers

None.

## Active Constraints

- Preserve formulas, config, fixtures/goldens, public results, schemas, and owners.
- Keep legacy report and summary bodies byte-preserved historical evidence.
- Do not combine documentation cleanup with unrelated source refactoring.
- Delete tracked files only within the user-approved scope of each slice.
- Use focused verification and staged-gate checks for the affected surface.
- Commit and push only with explicit user approval.

## Deferred / Hold

- Production ML Readiness resumes after the standard-calculation sequence.
- ML validation gap: `model/model.pkl` is absent and training CSV is external;
  mock smoke cannot validate accuracy, trends, importance, or model quality.

## Minimal Anchors

- Phase and milestone direction: `project_brief.md`
- Durable milestone history: `project_log.md`
- Active memory: `result_reports/memory/project_memory_seed.md`
- Structural candidates: `docs/REFACTOR_PLAN.md`
