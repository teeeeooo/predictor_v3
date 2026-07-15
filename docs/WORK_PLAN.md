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

Train/Admin Phase 3 Slice 3E editing/accessibility/responsive polish is
implemented on `phase/train-admin-data-definition-ux`. The approved Slice 3A-3D
domain, validation, save, handoff, mapping draft/undo, exchange, and persistence
contracts remain unchanged. Data Definition now has deterministic keyboard and
focus recovery, controlled dialog accessibility, explicit clean/dirty/blocked/
saved/write-error/empty states, and a compact content viewport. Saved Mapping
Requirement handoff focuses exact unresolved cells, ready coverage context, or a
non-mutating stale recovery surface. Synthetic cocoa evidence covers the seven
required native visual states. PR #16 remains Draft/Open.

## Next Action

Phase 3 final audit before merge or Phase 4.

## Active Blockers

- No Slice 3E code blocker remains; the explicit Phase 3 final-audit hold
  prevents merge or Phase 4 work.
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

- Merge and Phase 4 remain deferred until the Phase 3 final audit.
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
