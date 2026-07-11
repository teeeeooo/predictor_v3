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

Calculator table architecture Slice 1 is the active workstream under
`docs/designs/2026-07-12-calculator-table-architecture-design.md`. It adds the
shared Tk visual policy and grid primitives, establishes Compact Result Grid,
and migrates only the representative ISO/ISEER single input and result surfaces.

## Next Action

Review Slice 1 focused validation and visual behavior, then approve Slice 2
(generic result surfaces and Brazil adoption) separately.

## Active Blockers

None.

## Active Constraints

- Preserve calculator numeric results, config meaning, fixtures, and goldens.
- Public/schema changes require a concrete boundary or UX reason and the
  smallest compatible change.
- Keep legacy report and summary bodies byte-preserved historical evidence.
- Do not combine documentation cleanup with unrelated source refactoring.
- Delete tracked files only within the user-approved scope of each slice.
- Use focused verification and staged-gate checks for the affected surface.

## Deferred / Hold

- AHRI multi-capacity remains deferred after Calculator UI/UX unification.
- Production ML Readiness resumes after the standard-calculation sequence.
- ML validation gap: `model/model.pkl` is absent and training CSV is external;
  mock smoke cannot validate accuracy, trends, importance, or model quality.

## Minimal Anchors

- Phase and milestone direction: `project_brief.md`
- Durable milestone history: `project_log.md`
- Active memory: `result_reports/memory/project_memory_seed.md`
- Structural candidates: `docs/REFACTOR_PLAN.md`
