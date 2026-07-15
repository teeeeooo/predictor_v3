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

Train/Admin Phase 3 Slices 3B and 3C are implemented as separate logical commits
on `phase/train-admin-data-definition-ux`. Controlled Add/Edit commands produce
complete draft transitions; the default impact preview explains definition,
schema, mapping, restart, retrain, ML compatibility, blocker, and writer-result
evidence. Allowed drafts use the existing candidate-validation/backup/atomic-
replace schema writer; unsupported ML changes remain complete but blocked. PR #16
remains Draft/Open. The combined audit correction adds role-aware complete-row
validation and full parity, immutable controlled-Add provenance, and no-selection
blocker preservation. The blocker-presentation correction preserves independent
full-parity evidence beside ML compatibility blockers and renders affected
definition identity when selection is unavailable, without starting Slice 3D.

## Next Action

Slice 3B+3C final re-audit before starting Slice 3D.

## Active Blockers

- No code blocker remains in Slices 3B+3C; the explicit final re-audit hold
  prevents starting Slice 3D.
- Deferred Phase 2 native acceptance remains separate and does not reopen Phase 2
  code or block Phase 3 automated work.
- ML projection-changing definition edits remain intentionally blocked until an
  explicit compatibility persistence owner is approved.

## Active Constraints

- Preserve `config/predict/schema.csv` as the canonical Data Definition source.
- Keep `config/ml/features.csv` as a read/parity compatibility surface; do not add
  canonical writes from Phase 3 without a separate design.
- Preserve the Data Definition/Data Mapping owner boundary and runtime
  `mapping.json` contract.
- Reuse the existing Qt-free draft, edit policy, projection, validation, save-plan,
  schema-writer, and readiness owners.
- Keep the accepted Slice 3A presentation owner Qt-free/presentation-only and
  derive visible action enablement from existing controller/save-plan state.
- Use repository fixtures and mock data; do not add company production data or
  infer model quality or production readiness.
- Keep Cooling and Heating models independent, including monotone constraints.

## Deferred / Hold

- Data Mapping handoff/coverage and native polish remain deferred to Slices 3D
  and 3E respectively.
- Predict internal UI/UX overhaul begins only after Train/Admin Phase 4 and a fresh
  populated-state audit.
- Real mapping values, training data, model quality, and production-readiness
  validation remain company-local.

## Minimal Anchors

- Governing design: `docs/designs/2026-07-14-train-admin-ui-ux-overhaul-governing-design.md`
- Active Phase 3 design: `docs/designs/2026-07-14-train-admin-phase-3-data-definition-ux-overhaul.md`
- Accepted Phase 2 design: `docs/designs/2026-07-14-train-admin-phase-2-data-mapping-ux-overhaul.md`
- Phase and milestone direction: `project_brief.md`
- Durable milestone history: `project_log.md`
- Active memory: `result_reports/memory/project_memory_seed.md`
- Structural candidates: `docs/REFACTOR_PLAN.md`
