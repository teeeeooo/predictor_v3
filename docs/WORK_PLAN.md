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

Train/Admin UI/UX Overhaul Phase 2 — Data Mapping UX Overhaul Slices 2B and 2C
are implemented and pushed on `phase/train-admin-data-mapping-ux` after the
approved Slice 2A head. Slice 2B adds bounded spreadsheet interaction owners,
rectangular TSV copy/paste, clear, grouped undo, keyboard navigation, CRUD
selection, and the PFC Pi guard. Slice 2C adds exact baseline-diff dirty state,
structured issue-to-cell navigation, validation feedback, and transactional
Save/Reload state handling. The Batch audit correction now canonicalizes valid
typed cell input before dirty comparison, atomically blocks overflow paste, and
enforces one contiguous rectangular selection. Slice 2D has not started.

## Next Action

Commit and push the focused correction, confirm CI, then prepare the native
synthetic harness for the three bounded scenarios. Use Computer Use only for
display/window inspection and request physical user input for table interaction.
Keep Draft PR #15 open and do not begin Slice 2D without separate approval.

## Active Blockers

- Native macOS rendering succeeds, but Computer Use interaction with the
  populated PySide6 table crashes Python in AppKit's accessibility hierarchy
  (`EXC_BAD_ACCESS` / `SIGSEGV`). Two independent attempts reproduced it, and
  injected keyboard shortcuts did not reach the Qt table. Therefore paste/undo,
  PFC Pi, and issue-navigation/Save/Reload native interaction evidence remains
  incomplete; automated regression is recorded separately and is not treated
  as a substitute.

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
- Do not begin Slice 2D exchange export/import work.

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
