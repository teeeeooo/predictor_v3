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

AHRI 210/240-2026 multi-capacity implementation is complete. Dual-stage SEER2,
Dual-stage HSPF2, and Triple-capacity Northern HSPF2 are integrated through the
existing stable capability IDs and product-specific sibling engines. All audit
corrections, including conditional H3Low requiredness, seasonal-total contracts,
Case 4–7 equation evidence, field validation, and overlay integrity, are complete.
Automated validation passed and the user completed GUI verification and accepted
the implementation for main integration.

## Next Action

Await the next user-selected workstream and establish its active slice from the
owner documents. No further action remains for PR #11.

## Active Blockers

None.

## Active Constraints

- Preserve existing variable-capacity numeric results, fixtures, and goldens.
- Keep stable capability IDs and facade method names.
- Keep raw official AHRI Analytics evidence immutable; use the separate 2026
  expected overlay for corrected or derived values.
- Multi-capacity published ratings use nearest 0.05 without changing the current
  variable-capacity 0.025 HSPF2 behavior.
- Keep normalized fractional-bin aggregates separate from actual seasonal totals.
- Use the inclusive 37°F boundary for conditional H3Low requiredness in core,
  application, Single, and Batch contracts.

## Deferred / Hold

- Production ML Readiness resumes when selected as the next active workstream.
- ML validation gap: `model/model.pkl` is absent and training CSV is external;
  mock smoke cannot validate accuracy, trends, importance, or model quality.

## Minimal Anchors

- Phase and milestone direction: `project_brief.md`
- Durable milestone history: `project_log.md`
- Active memory: `result_reports/memory/project_memory_seed.md`
- Structural candidates: `docs/REFACTOR_PLAN.md`
