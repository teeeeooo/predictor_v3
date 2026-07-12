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

Implement the approved AHRI 210/240-2026 multi-capacity workstream from
`docs/designs/2026-07-12-ahri-multicapacity-core-calculator-gui-design.md`.
The active branch adds product-discriminated Dual-stage SEER2, Dual-stage HSPF2,
and Triple-capacity Northern HSPF2 while preserving the current variable-capacity
engines and stable capability IDs.

## Next Action

Complete product-aware Calculator Single/Batch surfaces, focused export/state
guards, and CI validation; then close the implementation record and request
review without merging to main.

## Active Blockers

- GitHub connector cannot perform local Tkinter platform visual smoke; CI and
  automated UI guards are required before closeout.

## Active Constraints

- Preserve existing variable-capacity numeric results, fixtures, and goldens.
- Keep stable capability IDs and facade method names.
- Keep raw official AHRI Analytics evidence immutable; use the separate 2026
  expected overlay for corrected or derived values.
- Multi-capacity published ratings use nearest 0.05 without changing the current
  variable-capacity 0.025 HSPF2 behavior.
- Use focused verification and staged-gate checks for affected owners.

## Deferred / Hold

- Production ML Readiness resumes after the standard-calculation sequence.
- ML validation gap: `model/model.pkl` is absent and training CSV is external;
  mock smoke cannot validate accuracy, trends, importance, or model quality.

## Minimal Anchors

- Phase and milestone direction: `project_brief.md`
- Durable milestone history: `project_log.md`
- Active memory: `result_reports/memory/project_memory_seed.md`
- Structural candidates: `docs/REFACTOR_PLAN.md`
