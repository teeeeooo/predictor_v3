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

Train/Admin Phase 2 — Data Mapping UX Overhaul is complete for code and
repository-automated acceptance. PR #15 is ready for user review and merge.
Native Slice 2B+2C interaction and Slice 2D+2E visual acceptance remain
deferred under their existing blockers and do not reopen Phase 2 code scope.

## Next Action

The user merges PR #15 to `main`. After confirming the merged-main SHA, start
Phase 3 — Data Definition UX Overhaul from a new branch and Draft PR. Its first
work is a current-state audit and confirmation of the Slice 3A boundary.

## Active Blockers

- Deferred acceptance: native macOS rendering succeeds, but Computer Use interaction with the
  populated PySide6 table crashes Python in AppKit's accessibility hierarchy
  (`EXC_BAD_ACCESS` / `SIGSEGV`). Two independent attempts reproduced it, and
  injected keyboard shortcuts did not reach the Qt table. Therefore paste/undo,
  PFC Pi, and issue-navigation/Save/Reload native interaction evidence remains
  incomplete; automated regression is recorded separately and is not treated
  as a substitute. This remains deferred and non-blocking for Slice 2D/2E. The
  audit-correction follow-up confirmed native rendering without accessibility
  clicks, but no physical interaction completion was reported, so no new
  interaction PNG was added.
- Deferred acceptance: the Slice 2D+2E native visual capture could not start because the Mac
  desktop was locked and Computer Use could not unlock it automatically. No
  native screenshot is claimed; the automated Batch result remains valid and
  the visual states are pending a later unlocked-desktop audit.
- Sequencing hold: Phase 3 does not start until the user merges PR #15 to
  `main`. This is a phase-ordering constraint, not a production defect.

## Active Constraints

- Preserve the Data Definition/Data Mapping owner boundary and runtime
  `mapping.json` contract.
- Use repository fixtures and mock training data whose structure matches the real
  local contract; do not add company production data.
- Do not infer model quality or production readiness from mock pipeline success.
- Keep Cooling and Heating models independent, including monotone constraints.
- Preserve the accepted Slice 2A–2E contracts while PR #15 awaits user merge.
- Do not create a Phase 3 branch, Draft PR, or implementation before merged
  `main` is confirmed.

## Deferred / Hold

- Predict internal UI/UX overhaul begins only after Train/Admin Phase 4 and a fresh
  populated-state audit.
- Real mapping values, training data, model quality, and production-readiness
  validation remain company-local.

## Minimal Anchors

- Governing design: `docs/designs/2026-07-14-train-admin-ui-ux-overhaul-governing-design.md`
- Accepted Phase 2 design: `docs/designs/2026-07-14-train-admin-phase-2-data-mapping-ux-overhaul.md`
- Phase and milestone direction: `project_brief.md`
- Durable milestone history: `project_log.md`
- Active memory: `result_reports/memory/project_memory_seed.md`
- Structural candidates: `docs/REFACTOR_PLAN.md`
