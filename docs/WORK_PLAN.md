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

Train/Admin Phase 3 — Data Definition UX Overhaul is complete and its final audit
is approved on PR #16. Slices 3A–3F, all audit corrections, the table-first Slice
3F correction, and the saved-handoff follow-up preserve the accepted Data
Definition, Data Mapping, Predict, and ML compatibility boundaries. PR #16 is the
Phase 3 merge target and is ready for user review after closeout CI succeeds.

## Next Action

The user merges PR #16 to `main`. After confirming the merged-main SHA, Phase 4 —
Train/Model and Shell UX Overhaul may begin only from a separate branch and Draft
PR after separate instruction.

## Active Blockers

- Phase 4 remains blocked until PR #16 is merged and merged `main` is confirmed.
- Deferred Phase 2 native interaction acceptance remains separate and does not
  reopen accepted Phase 2 or Phase 3 code.
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
- Use repository fixtures and mock data; do not add company production data or
  infer model quality or production readiness.
- Keep Cooling and Heating models independent, including monotone constraints.

## Deferred / Hold

- Phase 4 implementation, merge, and activation remain deferred until the Phase 3
  merge is confirmed and the user starts the next phase explicitly.
- Predict internal UI/UX overhaul begins only after Train/Admin Phase 4 and a fresh
  populated-state audit.
- Real mapping values, training data, model quality, and production-readiness
  validation remain company-local.

## Minimal Anchors

- Governing design: `docs/designs/2026-07-14-train-admin-ui-ux-overhaul-governing-design.md`
- Phase 3 foundation design: `docs/designs/2026-07-14-train-admin-phase-3-data-definition-ux-overhaul.md`
- Accepted Slice 3F amendment: `docs/designs/2026-07-16-train-admin-phase-3-slice-3f-task-oriented-definition-workspace.md`
- Final audit closeout: `result_reports/records/2026-07/2026-07-16-train-admin-phase3-final-audit-closeout.md`
- Accepted Phase 2 design: `docs/designs/2026-07-14-train-admin-phase-2-data-mapping-ux-overhaul.md`
- Phase and milestone direction: `project_brief.md`
- Durable milestone history: `project_log.md`
- Active memory: `result_reports/memory/project_memory_seed.md`
- Structural candidates: `docs/REFACTOR_PLAN.md`
