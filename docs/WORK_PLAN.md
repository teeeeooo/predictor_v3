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

Train/Admin UI/UX Overhaul Phase 1 — Mapping/Data Foundation is the active
workstream. Slices 1A–1D and Phase 1 automated validation are complete on Draft
PR #14; the dynamic option-payload/type audit correction is complete locally
and the final hidden-payload persistence correction is complete locally. The
phase remains held unmerged for final re-audit.

## Next Action

Await final re-audit of Draft PR #14. Do not start Phase 2 or merge without a
separate instruction.

## Active Blockers

None.

## Active Constraints

- Preserve the Data Definition/Data Mapping owner boundary and runtime
  `mapping.json` contract.
- Use repository fixtures and mock training data whose structure matches the real
  local contract; do not add company production data.
- Do not infer model quality or production readiness from mock pipeline success.
- Keep Cooling and Heating models independent, including monotone constraints.
- Commit and push each verified slice to the phase branch; merge only after phase
  acceptance is complete.

## Deferred / Hold

- Predict internal UI/UX overhaul begins only after Train/Admin Phase 4 and a fresh
  populated-state audit.
- Real mapping values, training data, model quality, and production-readiness
  validation remain company-local.

## Minimal Anchors

- Governing design: `docs/designs/2026-07-14-train-admin-ui-ux-overhaul-governing-design.md`
- Active phase design: `docs/designs/2026-07-14-train-admin-phase-1-mapping-data-foundation.md`
- Phase and milestone direction: `project_brief.md`
- Durable milestone history: `project_log.md`
- Active memory: `result_reports/memory/project_memory_seed.md`
- Structural candidates: `docs/REFACTOR_PLAN.md`
