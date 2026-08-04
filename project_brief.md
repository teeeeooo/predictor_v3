# Project Brief

This document owns the compact Phase / owner / milestone map for `predictor_v3`.
Near-term execution belongs to `docs/WORK_PLAN.md`; history belongs to
`project_log.md`, its archives, and result records.

## Current Phase

Train/Admin Phase 5, Predict Findings #1–#7, and the **Predict input workflow
broad overhaul** are complete and merged. Overhaul Slices 1–6 — Stable Identity
Seam, Typed Result and Execution Context, EER/COP Enrichment, Result Review
Projection, Shared Layout B Composition, and Bulk Paste Transaction — are
independently audited, merged, and closed. The Target applicability Owner Audit,
Ref Qty-only product decision, focused Lane C source correction, independent
exact-head audit, merge, and Close are also complete without relaxing full Active
compatibility. Narrow Viewport Result Review Pinning is also merged and closed.
The successor sequencing decision is now recorded: Result Review CSV v1 is the
next authorized source candidate, followed by an Agent Work-Contract read-only
audit and the remaining separately approved export/integration decision gates.

`docs/designs/2026-07-14-future-predict-ui-ux-overhaul-boundary.md` is the
authoritative product, owner, compatibility, and independent-slice boundary for
this workstream.

## Owner Map

- **Data Definition** is the canonical user-edit owner for Feature structure,
  stable identity, Predict/ML ordering, Derived/One-hot structure,
  Target/registry presentation, validation, impact, and safe publication through
  the versioned structured manifest and immutable generation.
- **Data Mapping** owns concrete `mapping.json` values, mapping attribute CRUD,
  exchange, dirty-draft reconciliation, and the runtime mapping cascade. Concrete
  values do not move into Data Definition.
- **Train** owns explicit training-data selection, training execution,
  run/generation-scoped Candidate creation and analysis, and the validated
  promotion workflow. Definition Save and training success do not automatically
  train or replace Active.
- **Predict** consumes a saved contract generation, Data Mapping values, and a
  compatible loaded model whose Active artifact proves the complete runtime
  Target capability. It preserves generation-bound preprocessing,
  inference, Target/result mapping, execution gating, row isolation,
  cancellation, partial results, reload, Active observation, and no-hot-swap
  behavior. Case-scoped requested execution is distinct from full Active
  compatibility.
- **Calculator** owns calculation implementations under `core/calculators` and
  the protected formula, profile/config, fixture/golden, and public result
  contracts. Standard calculation core and region config stay
  calculator-neutral; ML/Predict and Calculator integrate through approved
  contracts without copying or changing formulas.

Standalone and embedded Predict use the same shared workspace behavior. Findings
#1–#7 completed the bounded Predict presentation, reset/running projection,
message semantics, execution gate, runtime group-header synchronization, and
model/Target status repairs without changing the contracts above.

## Contract Boundaries

- Data Definition, Data Mapping, Train, Predict, and Calculator remain distinct
  owners. Region config, HW candidate input, ML feature schema, calculator result
  schema, and UI table schema remain separate contracts.
- `core.ml`, `core.predictor_schema`, `core.mapping`, `core.common`, and
  `core.calculators` remain UI-toolkit independent.
- Train and Predict remain separate PySide6 applications; the calculator shell
  and Tkinter paths stay separate.
- Immutable Definition publication, consumer preflight, runtime cutover,
  training Candidate publication, explicit Active promotion, deployment export,
  and Predict reload remain distinct state transitions.
- Standalone and embedded Predict share the case-table workspace contract.
  Root-level horizontal scrolling remains prohibited; any width solution belongs
  to the table and responsive viewport design.

## Milestone Map

### Closed Foundation

- Arc 13–15 established the ML pipeline, Predict schema projection, mapping
  entity/runtime cascade, and unified Data Definition owner.
- Train/Admin Phases 1–4 established mapping/data foundations, Data Mapping and
  Data Definition workflows, the Unified Feature Manager, immutable generation
  publication, and shared Train/Predict runtime consumption.
- Train/Admin Phase 5 established model lifecycle, Candidate/Active separation,
  training result and analysis, Train/Model UI, deployment export and explicit
  Predict reload, headless experiments, agent-assisted campaigns, and guarded
  final confirmation/retention boundaries.
- Predict Findings #1–#7 are complete. No numbered finding remains active.

Closed foundation retains its owner and behavior contracts; exact audit heads,
validation runs, repair sequences, and merge history belong to the log, archives,
records, and Git.

### Closed — Predict Input Workflow Broad Overhaul

The delivered direction is one canonical case session with shared standalone and
embedded Layout B Input/Result workspaces. Result Review uses a Predict-owned
projection, one stable-identity `사양 요약`, typed result capability, and the
closed execution-pinned EER/COP enrichment while existing Feature, Mapping,
lifecycle, execution, and Calculator owners remain authoritative.

Slice 1 closed the canonical Feature identity propagation seam without changing
the public/generated projection or persisted Feature Definition shape. Slice 2
closed the typed-result and execution-provenance foundation with one canonical
Predict session, repository-issued runtime authority, fail-closed terminal
acceptance, and preserved reload/generation lifecycle semantics. Slice 3 closed
the Qt-free execution-pinned EER/COP enrichment while preserving raw precision,
canonical result provenance, lifecycle semantics, and Calculator ownership.
Slice 4 closed the read-only canonical-session projection, shared table
presentation seam, and full-row TSV copy boundary while preserving historical
execution provenance and current-generation presentation metadata. Slice 5
closed the shared cached full-surface Input/Result composition, Qt-free
surface/selected-case policy, bounded terminal reveal, and generation-preserving
standalone/embedded rebinding. Slice 6 closed one generation-ordered canonical
bulk transaction with final-combination Mapping/autofill, precise issue truth,
atomic rollback, affected-only result invalidation, and fail-closed compound
undo.

### Closed — Case-Scoped Target Applicability

Existing ML mode-specific missing and Target leakage policy remains authoritative,
and the independently audited correction consumes it as a Case-scoped requested
Target contract. Full runtime Target capability remains mandatory for the Active
artifact; a Case-specific requested subset does not alter the Active registry or
relax compatibility. Both capacities present requests all five Targets;
cooling-only requests Cooling Power, Ref Qty, and Cooling Hz; heating-only
requests Heating Power, Ref Qty, and Heating Hz; both blank requests Ref Qty only
when its existing required inputs validate. A valid Ref Qty-only success is
`complete`; Power/Hz and EER/COP are N/A without fabricated outcomes. The closed
correction implements this matrix without bypassing empty-row or Ref Qty
artifact-selected input validation. Ordered stable Target identities are pinned
per execution while the session retains the full runtime contract; typed mapping,
aggregate status, stale/late rejection, migration, EER/COP, Result Review, and
copy consume the same subset.

### Closed — Narrow Viewport Result Review Pinning

The merged Lane B presentation slice keeps exactly `Case + 상태` visible only
when Result Review content overflows its own viewport. It reuses the existing
shared standalone/embedded workspace, canonical projection, model, selection,
copy, and generation rebind owners without reopening Target applicability or
Active compatibility. Future export, Predict-to-Calculate, training, or schema
work remains separately authorized.

### Next — Predict Successor Sequencing

- Result Review CSV v1 is first. It reuses the canonical Result Review application
  document for selected rows only and preserves canonical Case order, raw numeric
  evidence, provenance, and issues without creating a mutable export schema.
- After CSV v1 Close, perform a read-only Agent Work-Contract audit. Rewrite only
  if that audit finds meaningful responsibility/navigation drift.
- Keep XLSX behind its own product/dependency approval rather than bundling it
  into CSV v1.
- Before multi-point source integration, make a separate Predict Case → Standard
  Predicted Points / Standard Request product-owner decision.

### Later — Production ML Readiness / Calculator Integration

- Validate production model/data availability, prediction quality, physical
  trends, and feature importance only through an explicitly approved workstream.
- Reuse the existing `PredictedPointsEnvelope` and Calculator adapter foundation;
  the remaining Predict-side gap is authoritative assembly of multiple canonical
  Case/execution results into one standard operating-point set/request.
- Expand Calculator input adapters only through approved owner boundaries.
- Keep seasonal calculation, ranking, and recommendation work separate from the
  Predict input foundation and protected formula ownership.

## Controlled Operations / Deferred

- Production confirmation/promotion, migration apply, retention/delete apply,
  production data/model mutation, and deployment remain separately authorized
  controlled operations.
- Result graph or Advanced surface, export redesign, Train navigation, lifecycle
  wording redesign, model training workflow, ML feature/schema changes,
  Calculator formula changes, and packaging/deployment are not automatically part
  of the first Predict input overhaul scope.
- Narrow Viewport Result Review Pinning is closed. Result Review CSV v1 is the
  authorized successor source candidate; XLSX and multi-point Predict-to-Calculate
  remain separately gated follow-up work and are not implied by that authorization.
- AS/NZS Excel compatibility and historical reconstruction remain deferred.
- Internal formula trace remains on hold unless a separate core/data contract is
  approved.
- Broad refactors remain trigger-based under `docs/REFACTOR_PLAN.md`.

## State Navigation

- Start with `AGENTS.md` and the matching router/owner route.
- Read `docs/WORK_PLAN.md` for the active slice, next action, blockers,
  constraints, and holds.
- Read this brief for phase, owner, and milestone direction.
- Read the closed Predict overhaul boundary before authorizing successor work;
  expand it only after a new product/owner decision exists.
- Search `project_log.md` and its monthly archives by heading for durable history;
  use result records only for pointed evidence.
