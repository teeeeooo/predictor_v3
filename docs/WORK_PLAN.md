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
- Narrow Viewport Result Review Pinning is merged and closed. Result Review alone
  keeps `Case + 상태` visible when its canonical columns overflow, while the
  remaining columns retain internal horizontal scrolling over the same model,
  selection, vertical position, copy path, and generation rebind. Input Authoring
  and shell geometry remain unchanged.
- Result Review CSV v1 is merged and closed. Selected Result Review rows now
  publish through the existing full-row application document in canonical Case
  order, retaining raw numeric evidence, provenance, issues, and stale/unavailable
  semantics without a second mutable export schema or new dependency.
- The Result Review XLSX Product/Owner Decision is complete. XLSX source
  implementation is `DEFER`; this changes neither CSV behavior nor the
  existing Result Review contract and authorizes no writer/runtime/dependency
  slice.
- The Agent Work-Contract Audit and its bounded Active Documentation Contract
  Restoration follow-up are independently audited, merged, and closed. Generic
  Engineering Workflow authority and predictor_v3 project-specific authority are
  separated without weakening domain/UI/mechanical owners.

## Next Action

**Predict Case → Standard Predicted Points / Standard Request Product-Owner
Decision** is the exact next product gate. Define the authoritative product
semantics for assembling canonical Predict Case/execution evidence into one
standard operating-point request while preserving Calculator envelope/application
ownership. Multi-point Predict → Calculate source implementation remains held
until this decision closes.

## Active Decisions / Blockers

- Partial-target Active models are not supported. An Active artifact must provide
  and prove compatibility with the full runtime Target contract. Missing artifact
  capability is an incompatible Active / fail-closed error, not a compatibility
  option to relax.
- A model-incompatible saved Definition generation continues to block Predict
  with Retraining required until compatibility is proven; the overhaul does not
  auto-replace or auto-promote a model.
- Both cooling and heating capacities blank requests only `Ref Qty`, provided the
  Case satisfies the existing Ref Qty required HW/one-hot/model input contract.
  The blank capacities alone do not invalidate the Case; an empty row or missing
  Ref Qty requirements does not become runnable.

## Active Constraints

- Preserve completed Findings #1–#7 and existing prediction execution, row
  isolation, cancellation, and partial-result behavior.
- Preserve model lifecycle, reload, Active observation, no-hot-swap, schema,
  mapping, preprocessing, runtime snapshot, and inference contracts.
- Keep the Active runtime Target registry at its full compatible capability.
  Case-scoped execution derives only the requested execution subset from canonical
  raw user input before zero-fill/preprocessing; it does not shrink the registry
  or change artifact capability per Case.
- Preserve the distinction between an incompatible artifact and runtime partial
  results: missing Active capability fails compatibility, while actual execution
  failure for only some requested Targets on a valid Active produces `partial`.
- Existing ML mode-specific missing and target leakage policies remain
  authoritative. Predict Case execution consumes those upstream policies without
  redefining feature policy or Target registry ownership.
- Requested Targets are fixed by canonical raw capacity presence: both present
  requests Cooling Power, Heating Power, Ref Qty, Cooling Hz, and Heating Hz;
  cooling-only requests Cooling Power, Ref Qty, and Cooling Hz; heating-only
  requests Heating Power, Ref Qty, and Heating Hz; both blank requests Ref Qty
  only when its existing inputs validate. The Lane C correction now implements
  this matrix from raw Case input before zero-fill/preprocessing.
- For a valid Ref Qty-only Case, Ref Qty success makes the row `complete`; actual
  Ref Qty execution failure follows existing terminal/error semantics. Power/Hz
  Targets are not requested and EER/COP are N/A, without fabricated Target
  outcomes or a new outcome status.
- Preserve Data Definition, Data Mapping, Train, Predict, and Calculator owner
  directions. Predict remains a consumer of saved contracts, mapping values, and
  a compatible loaded model.
- Standalone and embedded Predict must use the same canonical session, shared
  Layout B workspace implementation, and Predict-owned workspace-state policy.
- Keep root-level horizontal scrolling prohibited. Result Review table scrolling
  remains internal; the closed narrow-viewport presentation pins exactly
  `Case + 상태` only when Result Review content exceeds its own viewport.
- Treat closed Slices 1–6 as upstream contracts. Do not fold export, Calculate
  integration, Target-registry changes, or viewport-pinning work into the
  correctness repair without separate approval.
- Use repository fixtures or mock data only. Do not infer production readiness or
  mutate production data or models.

## Deferred / Hold

- Result graph or Advanced surface, Train navigation, lifecycle wording redesign,
  model training workflow, ML feature/schema changes, calculator formula changes,
  and packaging/deployment require separate approval or follow-up workstreams.
- Result Review XLSX source implementation is `DEFER` after the completed
  Product/Owner Decision. Reopen only for demonstrated workbook-specific need:
  CSV Excel import/locale/encoding friction, typed numeric cells, repeated
  filter/freeze/column-sizing workflow, separate Evidence / Issues / Metadata
  sheets, or an official shared-workbook artifact. `openpyxl` availability is a
  resolved technical condition, not implementation priority evidence.
- Multi-point Predict-to-Calculate source integration remains on hold. Calculator
  already has a `PredictedPointsEnvelope`/adapter foundation; the missing product
  decision is how multiple canonical Predict Cases/execution results are assembled
  with authoritative semantics into one standard operating-point set/request for
  the existing Calculator envelope/application boundary.
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

1. **Target applicability documentation reconciliation — complete:** recorded
   the design invariant and Predict integration gap without source mutation.
2. **Case-Scoped Target Applicability Owner Audit — complete:** resolved current
   owners and execution seams read-only.
3. **Ref-Qty-only applicability product decision — complete in this task:** both
   capacities blank requests Ref Qty only when its existing inputs validate.
4. **Case-Scoped Target Applicability Lane C Source Correction — complete:**
   independently audited, merged, and closed without relaxing Active compatibility.
5. **Fresh independent exact-head Lane C audit and Close — complete.**
6. **Narrow Viewport Result Review Pinning — merged and closed:** exact
   `Case + 상태` responsive anchor without reopening the closed correctness repair.
7. **Result Review CSV v1 — merged and closed:** selected-row CSV publication now
   reuses the canonical Result Review application document, preserving canonical
   Case order, raw numeric evidence, provenance, issues, and existing copy/pinning
   ownership without a new mutable export schema or dependency.
8. **Agent Work-Contract Audit + bounded Contract Improvement — complete:**
   responsibility/navigation drift was confirmed, active documentation authority
   was restored, and the exact repaired head was independently audited and merged.
9. **Result Review XLSX Product/Owner Decision — complete:** source
   implementation is `DEFER`; reopen only for demonstrated workbook-specific
   workflow need. CSV behavior and the existing Result Review contract remain
   unchanged.
10. **Predict Case → Standard Predicted Points / Standard Request Product-Owner
    Decision — next approval gate:** define how canonical Predict Cases/execution
    evidence become one standard operating-point set/request while reusing
    Calculator envelope/application ownership.
11. **Multi-point Predict → Calculate implementation — held** until the Standard
    Request decision closes; Predict must not copy Calculator formulas or replace
    the Calculator owner.

## Minimal Anchors

- Authoritative approved product and integration boundary:
  `docs/designs/2026-07-14-future-predict-ui-ux-overhaul-boundary.md`
- Product and owner map: `project_brief.md`
- UI/UX owner root: `docs/ui_ux/00_UI_UX_SYSTEM.md`
- Spreadsheet behavior: `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
- Input/result roles: `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`
- Viewport policy: `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`
