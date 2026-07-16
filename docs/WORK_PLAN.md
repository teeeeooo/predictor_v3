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

Train/Admin Phase 3 Slice 3F table-first correction is active on
`phase/train-admin-data-definition-ux`, based on
`1f3d9d973f7e97a1ed123a88fd757016ccbc34ab`. The correction removes the
always-visible Selected Definition Summary Card and clean lower panel, makes
Inventory the primary vertical stretch owner, projects normal eight-column and
compact six-column user-facing tables, and moves Summary information into an
on-demand read-only Details modal. Unified Add, controlled Edit, conditional
impact/blocker/saved handoff, Advanced Diagnostics, and all accepted Slice 3A–3E
domain, validation, save, mapping, compatibility, persistence, keyboard, focus,
and accessibility contracts remain in scope. PR #16 remains Draft/Open.

## Next Action

Hand off to the Slice 3F final audit before the Phase 3 final audit after the
native evidence is included in the correction commit and its CI/PR state is
confirmed.

## Active Blockers

- Phase 3 final approval and merge are blocked until the implemented Slice 3F
  presentation passes its dedicated audit.
- Slice 3E remains the accepted interaction foundation; the Slice 3F audit does not
  reopen accepted domain or persistence contracts.
- Deferred Phase 2 native acceptance remains separate and does not reopen Phase 2
  code or block Phase 3 automated work.
- ML projection-changing definition edits remain intentionally blocked until an
  explicit compatibility persistence owner is approved.
- Native table-first correction capture is complete through the bounded safe
  Cocoa scenario; the known AppKit table accessibility path was not used.

## Active Constraints

- Preserve `config/predict/schema.csv` as the canonical Data Definition source.
- Keep `config/ml/features.csv` as a read/parity compatibility surface; do not add
  canonical writes from Phase 3 without a separate design.
- Preserve the Data Definition/Data Mapping owner boundary and runtime
  `mapping.json` contract.
- Reuse the existing Qt-free draft, command, edit policy, projection, validation,
  save-plan, schema-writer, readiness, handoff, and coverage owners.
- Limit Slice 3F to workspace composition, UI-facing projections, action hierarchy,
  conditional impact/next-step presentation, responsive table policy, tests, and
  bounded native visual evidence.
- Keep Slice 3E keyboard, focus, shortcut, accessibility, dialog, selection,
  recovery, and exact Data Mapping handoff behavior intact.
- Use repository fixtures and mock data; do not add company production data or
  infer model quality or production readiness.
- Keep Cooling and Heating models independent, including monotone constraints.

## Deferred / Hold

- Merge and Phase 4 remain deferred until Slice 3F and the Phase 3 final audit are
  approved.
- Predict internal UI/UX overhaul begins only after Train/Admin Phase 4 and a fresh
  populated-state audit.
- Real mapping values, training data, model quality, and production-readiness
  validation remain company-local.

## Minimal Anchors

- Governing design: `docs/designs/2026-07-14-train-admin-ui-ux-overhaul-governing-design.md`
- Active Slice 3F design: `docs/designs/2026-07-16-train-admin-phase-3-slice-3f-task-oriented-definition-workspace.md`
- Phase 3 foundation design: `docs/designs/2026-07-14-train-admin-phase-3-data-definition-ux-overhaul.md`
- Accepted Phase 2 design: `docs/designs/2026-07-14-train-admin-phase-2-data-mapping-ux-overhaul.md`
- Phase and milestone direction: `project_brief.md`
- Durable milestone history: `project_log.md`
- Active memory: `result_reports/memory/project_memory_seed.md`
- Structural candidates: `docs/REFACTOR_PLAN.md`
