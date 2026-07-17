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

Train/Admin Phase 3 — Data Definition UX Foundation is complete and merged to
`main` through PR #16. The current workstream is Train/Admin Phase 4 — Unified
Feature Manager current-state audit and design finalization. Production
implementation has not started. The audit must approve the future unified
contract, persistence, compatibility, ordering, and reload boundaries while
preserving current production guards.

## Next Action

Audit merged `main` Data Definition, Predict schema, ML Feature Catalog, Derived
policy, One-hot contracts, model registry, Train Target consumption, and live
reload boundaries. Finalize the Phase 4 contract and ordered implementation
slices, including application-wide generation cutover, training-run snapshots,
dirty Mapping draft reconciliation, category source modes, and Target/model-group
scope. Do not start Phase 4 production implementation before audit/design
approval.

## Active Blockers

- Phase 4 production implementation remains on hold until current-state audit and
  design finalization are approved.
- Current production paths continue blocking ML-projection-changing Definition
  saves. Phase 4 must approve the persistence owner and compatibility migration/
  rollback boundary; existing guards are not bypassed before that owner exists.
- Phase 5 Train/Model and Shell UX remains on hold until Phase 4 is stable.

## Active Constraints

- Preserve Data Definition as the canonical user-edit owner. Phase 4A determines
  the exact canonical storage/projection shape without prematurely fixing a new
  file format or package layout.
- Keep `config/ml/features.csv` as an ML compatibility/projection surface rather
  than an independent editor; do not add writes before the Phase 4 persistence
  contract is approved.
- Preserve the Data Definition/Data Mapping owner boundary and runtime
  `mapping.json` contract.
- Preserve the accepted Qt-free draft, command, edit policy, projection,
  validation, save-plan, schema-writer, readiness, handoff, coverage, keyboard,
  focus, accessibility, and exact-navigation owners.
- Require one active contract generation across required consumers; keep disk
  publication, consumer preflight, and runtime cutover as distinct states.
- Preserve active training-run snapshots and Data Mapping unsaved drafts across
  Definition changes. Do not classify stale artifacts as current-compatible.
- Separate static/mapping-backed/external One-hot category mutation owners and
  Target CRUD from new model-group/model-level policy creation.
- Data Mapping remains the concrete `mapping.json` value owner; Train remains the
  explicit training-execution owner; Predict remains a saved-contract and
  compatible-model consumer.
- Phase 4 excludes automatic retraining, automatic model activation, training
  execution from Data Definition, and Predict internal redesign.
- Use repository fixtures and mock data; do not add company production data or
  infer model quality or production readiness.
- Keep Cooling and Heating models independent, including monotone constraints.

## Deferred / Hold

- Phase 4 production implementation and merge remain deferred until the audit
  and design finalization are approved.
- Phase 5 Train/Model and Shell implementation begins only after Unified Feature
  Manager stabilization and a fresh dynamic-contract audit.
- Deferred Phase 2 native interaction acceptance remains a separate acceptance
  item and does not block Phase 4.
- Predict internal UI/UX overhaul begins only after Train/Admin Phase 5 and a fresh
  populated-state audit.
- Real mapping values, training data, model quality, and production-readiness
  validation remain company-local.

## Minimal Anchors

- Governing design: `docs/designs/2026-07-14-train-admin-ui-ux-overhaul-governing-design.md`
- Phase 4 design: `docs/designs/2026-07-17-train-admin-phase-4-unified-feature-manager.md`
- Deferred Phase 5 design: `docs/designs/2026-07-14-train-admin-phase-5-train-model-shell-ux-overhaul.md`
- Phase 3 foundation design: `docs/designs/2026-07-14-train-admin-phase-3-data-definition-ux-overhaul.md`
- Arc 15 owner foundation: `docs/designs/2026-07-06-arc15-unified-data-definition-manager-foundation.md`
- Accepted Slice 3F amendment: `docs/designs/2026-07-16-train-admin-phase-3-slice-3f-task-oriented-definition-workspace.md`
- Final audit closeout: `result_reports/records/2026-07/2026-07-16-train-admin-phase3-final-audit-closeout.md`
- Accepted Phase 2 design: `docs/designs/2026-07-14-train-admin-phase-2-data-mapping-ux-overhaul.md`
- Phase and milestone direction: `project_brief.md`
- Durable milestone history: `project_log.md`
- Active memory: `result_reports/memory/project_memory_seed.md`
- Structural candidates: `docs/REFACTOR_PLAN.md`
