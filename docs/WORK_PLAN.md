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

Train/Admin Phase 3 — Data Definition UX Overhaul is complete and merged to
`main` through PR #16. The current workstream is the Phase 4 current-state audit
and design finalization for the Train/Model and common shell UX. This is a
documentation and planning slice only; the existing Data Definition, Data
Mapping, Train, Predict, ML, persistence, and public-contract owners remain
unchanged.

## Next Action

Audit the merged-main Train/Model and shell surfaces against the existing owner
contracts, then finalize the Phase 4 design and ordered implementation slices
before any UI implementation begins.

## Active Blockers

- Phase 4 implementation remains on hold until the current-state audit and design
  finalization are complete and the phase is explicitly started.
- ML projection-changing definition edits remain intentionally blocked until an
  explicit compatibility persistence owner is approved.

## Active Constraints

- Preserve `config/predict/schema.csv` as the canonical Data Definition source.
- Keep `config/ml/features.csv` as a read/parity compatibility surface; do not add
  canonical writes without a separate design.
- Preserve the Data Definition/Data Mapping owner boundary and runtime
  `mapping.json` contract.
- Preserve the accepted Qt-free draft, command, edit policy, projection,
  validation, save-plan, schema-writer, readiness, handoff, coverage, keyboard,
  focus, accessibility, and exact-navigation owners.
- In Phase 4, schema, feature, mapping, and compatibility checks run internally
  and automatically; the default Train view leads with the user's next action
  rather than raw readiness metadata.
- Use repository fixtures and mock data; do not add company production data or
  infer model quality or production readiness.
- Keep Cooling and Heating models independent, including monotone constraints.

## Deferred / Hold

- Phase 4 implementation and merge remain deferred until the current-state audit
  and design finalization are approved.
- Deferred Phase 2 native interaction acceptance remains a separate acceptance
  item and does not block Phase 4.
- Predict internal UI/UX overhaul begins only after Train/Admin Phase 4 and a fresh
  populated-state audit.
- Real mapping values, training data, model quality, and production-readiness
  validation remain company-local.

## Minimal Anchors

- Governing design: `docs/designs/2026-07-14-train-admin-ui-ux-overhaul-governing-design.md`
- Phase 4 design: `docs/designs/2026-07-14-train-admin-phase-4-train-model-shell-ux-overhaul.md`
- Phase 3 foundation design: `docs/designs/2026-07-14-train-admin-phase-3-data-definition-ux-overhaul.md`
- Accepted Slice 3F amendment: `docs/designs/2026-07-16-train-admin-phase-3-slice-3f-task-oriented-definition-workspace.md`
- Final audit closeout: `result_reports/records/2026-07/2026-07-16-train-admin-phase3-final-audit-closeout.md`
- Accepted Phase 2 design: `docs/designs/2026-07-14-train-admin-phase-2-data-mapping-ux-overhaul.md`
- Phase and milestone direction: `project_brief.md`
- Durable milestone history: `project_log.md`
- Active memory: `result_reports/memory/project_memory_seed.md`
- Structural candidates: `docs/REFACTOR_PLAN.md`
