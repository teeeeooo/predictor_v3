# Project Brief

This document owns the compact Phase / Arc / Milestone map for `predictor_v3`.
It is the first project-state document to read when starting a new session or
resuming work.

It does not own task-specific read pointers, code file pointers, or the exact
next implementation action. Current slice, next action, blockers, constraints,
and explicit handoff pointers belong to `docs/WORK_PLAN.md`.

## 1. Current Phase

Current phase: Calculator UI / workflow completion before ML / predictor
continuation.

Project direction remains aligned with `PROJECT_CHARTER.md`:

1. stabilize calculator formulas and regression protection;
2. complete calculator UI/workflow surfaces for the active standards;
3. stabilize calculator result boundaries;
4. return to ML / predictor integration after calculator outputs are reliable.

## 2. Current Architecture State

- Calculator entrypoints are rooted at `app_calculator.py` and
  `apps.calculator.app:main`, with UI code under `apps/calculator/ui/`.
- Train/Predict paths remain separate from the calculator shell.
- Calculator core, profile/config, UI, result envelope, and ML adapter concerns
  should stay separated.
- Region config, HW candidate input, ML feature schema, calculator result schema,
  and UI table schema must not be mixed.
- For later calculator-to-ML boundary work, use
  `docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md` as the
  starting design reference.

## 3. Arc / Milestone Map

### Arc 1 — EN14825 Calculator Completion

Goal:

- Complete EN14825 calculator usability across main UI and batch mode without
  reopening stable core, schema, region-config, fixture, or golden contracts.

Status: complete.

Milestones:

- Main SEER/SCOP calculation UI: complete.
- EN14825 config ownership and SEER/SCOP point contract: complete.
- SEER batch mode and dialog wiring: complete.
- SCOP batch profile-local rebuild/snapshot policy: complete.
- SCOP batch parent-section access: complete.
- EN14825 calculator smoke / lifecycle closeout: complete.

Current near-term slice:

- Owned by `docs/WORK_PLAN.md`.

Reference anchors:

- `result_reports/summaries/404_summary-en14825-config-point-contract-ui-workflow-closeout.md`
- `result_reports/summaries/416_summary-en14825-batch-agent-change-gate-closeout.md`

### Arc 2 — AHRI 210/240 Calculator Completion

Goal:

- Complete AHRI 210/240 calculator usability across the required main and batch
  workflows after EN14825 closeout.

Status:

- Design and SEER2 main UI foundation complete; SEER2 batch is the next
  separately approved implementation slice.

Milestones:

- AHRI UI/Batch design specification: complete.
- SEER2 main UI foundation: complete.
- SEER2 batch: next.
- HSPF2 main UI foundation: pending.
- HSPF2 batch: pending.
- Focused regression and lifecycle closeout: pending.

### Arc 3 — Calculator Workflow / Result Boundary Stabilization

Goal:

- Stabilize calculator outputs, result envelopes, and adapter boundaries needed
  before returning to ML / predictor work.

Status:

- Later arc; do not start while active standard-calculator completion work is in
  progress unless explicitly approved.

Candidate reference:

- `docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md`

### Arc 4 — ML / Predictor Continuation

Goal:

- Resume ML / predictor integration after calculator workflows and result
  boundaries are stable enough to serve as reliable downstream inputs.

Status:

- Later phase; not the current implementation focus.

## 4. Deferred / Hold Areas

- AS/NZS Excel compatibility Z-phase remains deferred.
- Internal formula trace remains on hold unless a separate core/data contract is
  approved.
- Broad code-quality refactors belong in `docs/REFACTOR_PLAN.md`, not in this
  brief.
- Packaging and hook-integration work should remain separate workflow arcs unless
  explicitly promoted.

## 5. Session Start Rule

1. Read `project_brief.md` to understand the current Phase, active Arc, and
   Milestone position.
2. Read `docs/WORK_PLAN.md` to identify the current slice, next action,
   blockers/open decisions, and constraints.
3. If `docs/WORK_PLAN.md` contains a user-requested `Session Handoff`, follow its
   `Read First` and `Task-Specific Pointers` before broader reads.
4. Use `AGENT_TASK_ROUTER.md` only for the sections required by the current task
   type.
5. Do not reconstruct current priority from archived reports or long report
   histories.

## 6. Document Guide

- `AGENTS.md`: lite rule entrypoint for each agent task.
- `AGENT_TASK_ROUTER.md`: task route and compact gate map.
- `PROJECT_CHARTER.md`: long-term purpose, Phase 1~5, and project principles.
- `project_brief.md`: Phase / Arc / Milestone map.
- `docs/WORK_PLAN.md`: current slice, next action, blocker/open decision,
  constraints, deferred/hold items, and explicit Session Handoff.
- `project_log.md`: milestone decision, failure, and lesson history.
- `ACTIVE_DOCUMENTS.md`: active document owner/inbound/outbound map.
- `result_reports/`: task detail, lifecycle summaries, completed report archive,
  and memory staging.
