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

Train/Admin UI/UX Overhaul Phase 2 — Data Mapping UX Overhaul Slice 2D+2E audit
correction is implemented on `phase/train-admin-data-mapping-ux`. Import now
runs canonical Data Mapping validation before preview and again at Apply,
reports only groups with semantic changes, and canonicalizes exchange row order
so order-only bundles remain no-ops. Publish rollback regression covers both
fully existing and mixed existing/new eight-target packages, including an
instrumented new-target creation followed by rollback deletion.

## Next Action

Re-audit the Slice 2D+2E correction on Draft PR #15. Keep the PR open and Draft;
do not merge the phase, change readiness, or begin follow-up Phase work.

## Active Blockers

- Native macOS rendering succeeds, but Computer Use interaction with the
  populated PySide6 table crashes Python in AppKit's accessibility hierarchy
  (`EXC_BAD_ACCESS` / `SIGSEGV`). Two independent attempts reproduced it, and
  injected keyboard shortcuts did not reach the Qt table. Therefore paste/undo,
  PFC Pi, and issue-navigation/Save/Reload native interaction evidence remains
  incomplete; automated regression is recorded separately and is not treated
  as a substitute. This remains deferred and non-blocking for Slice 2D/2E. The
  audit-correction follow-up confirmed native rendering without accessibility
  clicks, but no physical interaction completion was reported, so no new
  interaction PNG was added.
- This Batch's bounded native visual capture could not start because the Mac
  desktop was locked and Computer Use could not unlock it automatically. No
  native screenshot is claimed; the automated Batch result remains valid and
  the visual states are pending a later unlocked-desktop audit.

## Active Constraints

- Preserve the Data Definition/Data Mapping owner boundary and runtime
  `mapping.json` contract.
- Use repository fixtures and mock training data whose structure matches the real
  local contract; do not add company production data.
- Do not infer model quality or production readiness from mock pipeline success.
- Keep Cooling and Heating models independent, including monotone constraints.
- Commit and push each verified slice to the phase branch; merge only after phase
  acceptance is complete.
- Preserve the Slice 2B and Slice 2C commits as separately auditable logical
  changes and keep PR #15 Draft/Open.
- Keep Slice 2D and Slice 2E as separately auditable logical commits; start Slice
  2E only after the Slice 2D focused export gate and push succeed.

## Deferred / Hold

- Predict internal UI/UX overhaul begins only after Train/Admin Phase 4 and a fresh
  populated-state audit.
- Real mapping values, training data, model quality, and production-readiness
  validation remain company-local.

## Minimal Anchors

- Governing design: `docs/designs/2026-07-14-train-admin-ui-ux-overhaul-governing-design.md`
- Active phase design: `docs/designs/2026-07-14-train-admin-phase-2-data-mapping-ux-overhaul.md`
- Phase and milestone direction: `project_brief.md`
- Durable milestone history: `project_log.md`
- Active memory: `result_reports/memory/project_memory_seed.md`
- Structural candidates: `docs/REFACTOR_PLAN.md`
