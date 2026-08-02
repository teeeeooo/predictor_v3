# Work Plan

## Purpose

- Own the current slice, one next action, blockers, constraints, and deferred work.
- Keep phase, owner, and milestone direction in `project_brief.md`.
- Keep durable history in `project_log.md` and its archives; keep conditional
  evidence in records.

## Update Rule

- This file is a near-term execution board, not a roadmap or task log.
- Update it only when the current slice, next action, blocker, constraint, or
  hold state changes.
- Do not repeat completed audit, validation, repair, or merge history.

## Current Baseline

- Train/Admin Phase 5 is complete and merged.
- Predict Findings #1–#7 are complete and merged.
- The **Predict input workflow broad overhaul** is complete and closed.
- The disposable Layout A–D comparison and existing-app owner audit are complete.
- The approved direction is a shared Layout B full-surface Input/Result switch,
  one `사양 요약` review column, and a Predict-owned identity/result/state seam
  over the existing Feature, Mapping, lifecycle, execution, and Calculate owners.
- Slice 1 — Stable Identity Seam is independently audited, merged, and closed.
  Predict now carries canonical Feature identity through one immutable,
  generation-bound runtime descriptor into standalone and embedded presentation
  adapters without changing the public/generated projection or persisted Feature
  Definition shape.
- Slice 2 — Typed Result and Execution Context is independently audited, merged,
  and closed. Predict now owns raw typed target outcomes, immutable execution
  provenance, one fail-closed canonical session boundary, and repository-issued
  runtime authority across execution, reload, migration, rollback, and generation
  transitions while preserving the public/generated and persisted schema shapes.
- Slice 3 — EER/COP Enrichment is independently audited, merged, and closed.
  Predict now derives raw EER/COP from execution-pinned stable-identity capacity
  evidence and accepted typed power outcomes while preserving canonical result
  provenance, lifecycle semantics, and the public/persisted schema boundaries.
- Slice 4 — Result Review Projection is independently audited, merged, and
  closed. It projects the canonical session read-only, formats EER/COP only at
  presentation, composes the stable-identity full specification summary, and
  exposes full-row TSV copy with hidden raw source/provenance evidence.
- Slice 5 — Shared Layout B Composition is independently audited, merged, and
  closed. Standalone and embedded Predict now share one cached full-surface
  Input/Result workspace, Qt-free surface/selected-case state, bounded terminal
  reveal policy, and generation-preserving presentation rebinding.
- Slice 6 — Bulk Paste Transaction is independently audited, merged, and closed.
  Headerless TSV now lands through one generation-ordered canonical transaction
  with final-combination Mapping/autofill, precise issue reconciliation, atomic
  rollback, affected-only result invalidation, and fail-closed compound undo.

## Next Action

The next gate is the read-only **Case-Scoped Target Applicability Owner Audit**.
It must locate the current owners for canonical raw-input applicability,
requested-Target propagation, execution provenance and result acceptance,
Complete/Partial/N/A, EER/COP interaction, and the both-capacities-blank product
decision before any source correction is authorized.

## Active Decisions / Blockers

- Partial-target Active models are not supported. An Active artifact must provide
  and prove compatibility with the full runtime Target contract. Missing artifact
  capability is an incompatible Active / fail-closed error, not a compatibility
  option to relax.
- A model-incompatible saved Definition generation continues to block Predict
  with Retraining required until compatibility is proven; the overhaul does not
  auto-replace or auto-promote a model.
- The execution/validation UX for a Case whose cooling and heating capacities are
  both blank is unresolved and requires a small product decision before source
  implementation.

## Active Constraints

- Preserve completed Findings #1–#7 and existing prediction execution, row
  isolation, cancellation, and partial-result behavior.
- Preserve model lifecycle, reload, Active observation, no-hot-swap, schema,
  mapping, preprocessing, runtime snapshot, and inference contracts.
- Keep the Active runtime Target registry at its full compatible capability.
  Future correction may derive a Case-scoped requested execution subset from
  canonical raw user input before zero-fill/preprocessing; it must not shrink the
  registry or change artifact capability per Case.
- Preserve the distinction between an incompatible artifact and runtime partial
  results: missing Active capability fails compatibility, while actual execution
  failure for only some requested Targets on a valid Active produces `partial`.
- Existing ML mode-specific missing and target leakage policies remain
  authoritative. Their application to Predict Case execution is an integration
  gap, not a new feature-policy design.
- Preserve Data Definition, Data Mapping, Train, Predict, and Calculator owner
  directions. Predict remains a consumer of saved contracts, mapping values, and
  a compatible loaded model.
- Standalone and embedded Predict must use the same canonical session, shared
  Layout B workspace implementation, and Predict-owned workspace-state policy.
- Keep root-level horizontal scrolling prohibited. Result Review table scrolling
  remains internal; the narrow embedded pinned-column range is an open gate.
- Treat closed Slices 1–6 as upstream contracts. Do not fold export, Calculate
  integration, Target-registry changes, or viewport-pinning work into the
  correctness repair without separate approval.
- Use repository fixtures or mock data only. Do not infer production readiness or
  mutate production data or models.

## Deferred / Hold

- Result graph or Advanced surface, CSV/XLSX file export and export dialogs,
  Train navigation, lifecycle
  wording redesign, model training workflow, ML feature/schema changes,
  calculator formula changes, and packaging/deployment require separate approval
  or follow-up workstreams.
- CSPF/HSPF2 requires a future multi-point Predict-to-Calculate contract and is
  not a current Result Review capability.
- Process-restart view-state persistence, a persistent selected-case detail
  panel, a separate Full Context screen, and legacy split-table restoration are
  outside the first implementation.
- Production confirmation/promotion, migration apply, and retention/delete apply
  remain separately authorized controlled operations.
- Real mapping values, training data, model quality, and production-readiness
  validation remain company-local.
- Windows native Feature Manager smoke and deferred Phase 2 native interaction
  acceptance remain separate verification items and do not define this overhaul.

## Authoritative Near-Term Order

1. **Documentation reconciliation — complete in this task:** record the design
   invariant and the existing Predict integration gap without source mutation.
2. **Case-Scoped Target Applicability Owner Audit:** read-only owner and current
   source audit, including requested Target flow, outcomes, EER/COP, and the
   both-capacities-blank decision.
3. **Case-Scoped Target Applicability source correction:** separate Lane C slice
   that connects existing ML policy to Predict execution without relaxing Active
   compatibility.
4. **Fresh independent exact-head audit and Close.**
5. **Narrow Viewport Result Review Pinning:** separate presentation slice using
   Case + 상태 as the anchor direction; do not combine it with correctness repair.
6. **Separately approved deferred work:** CSV/XLSX export, multi-point
   Predict-to-Calculate, and other deferred product work.

## Minimal Anchors

- Authoritative approved product and integration boundary:
  `docs/designs/2026-07-14-future-predict-ui-ux-overhaul-boundary.md`
- Product and owner map: `project_brief.md`
- UI/UX owner root: `docs/ui_ux/00_UI_UX_SYSTEM.md`
- Spreadsheet behavior: `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
- Input/result roles: `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`
- Viewport policy: `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`
