# Project Brief

This document owns the compact Phase / Arc / Milestone map for `predictor_v3`.
Execution belongs to `docs/WORK_PLAN.md`; history belongs to the log and records.

## Current Phase

Train/Admin Phase 4 Unified Feature Manager is complete for repository-automated
scope. Phase 5A architecture audit is complete, and the independent audit of
Phase 5B head `21b98eb38239e0100be3c3700744c69e2fdc11fe` returned `PASS`.
PR #28 was squash-merged as
`eca6addd38745dadca3b0e4f19cc259090d50e23`; the lifecycle foundation is
complete with no remaining merge blocker. Phase 5C Training Result & Analysis
is complete and merged through PR #30 to `main` at
`8f74fc613d1ad6f6a1cc2c9d206543198f6d88f8`; its final independent L4 audit
returned `PASS`, and required validation run `30157872726` succeeded. Phase 5D
Train/Model UI/UX is complete. The user accepted repaired head
`a2ea64464e595d28d58db77a28d31eac60c6a72d`, and PR #31 was squash-merged to
`main` as `78e9d097693c3e3b8c23d2ed18dd7e68dc1f44b0`. Both independent audit
`FAIL` results remain historical evidence; no independent `PASS` is
retroactively declared. Phase 5E is complete and merged. Phase 5F Headless
Experiment Interface is also complete and merged: final accepted head
`fa13ddd75c5cf8a423d3ffc1fc046f552086e01a`, required validation run
`30197335156`, and PR #33 squash merge
`1f441c6d82545943aa160919c7d97d3a4b969580`. Its two independent audit `FAIL`
heads `b5ce141711c3660e2ce38b738f58f478a333d251` and
`e5558e82d7ca736bb45ca71eb94ab83b71a19950` remain historical evidence.
Phase 5G is complete and merged: final accepted head
`3344be1237f56752f8fcb607074152c53ea75c52`, required run `30203030680`, and
PR #34 squash merge `cb9183353dd6492dff07012c4276e4beb2b582b8`. Its earlier audit `FAIL`
heads `029fefdd783c21f380f6d43c6bd6efe403a52b28` and
`a58f4584344fce921341bddc25091aef79403485`, with runs `30199916760` and
`30201667033`, remain historical evidence. Phase 5H is complete and merged:
fresh independent audit accepted exact head
`45dd7544afc9546abf4ab450bf634f4c37fb1340`, required run `30433284479`
succeeded, and PR #35 was guarded squash-merged as
`b20661ee6b400559fbac61a9f2669d50256247bc`. Train/Admin Phase 5 is therefore
closed. Predict internal UI/UX is now the active product workstream. Findings
#1–#6 are complete and merged. Finding #6's runtime group-header synchronization
repair was guarded squash-merged through PR #41 as
`1c8c786750c78f538ea7c8ba1395592939dab550`. It rebinds the shared
standalone/embedded header to the current runtime model and columns while
preserving scroll alignment and signal ownership. Finding #7's bounded shared
model/Target presentation is implemented on a feature branch and awaits fresh
Lane B exact-head review; it remains unmerged, and no later finding is active.
Guidance, navigation, and lifecycle wording redesign remain separate.

The authoritative Phase 5 contract is
`docs/designs/2026-07-22-train-model-lifecycle-agent-assisted-experiment-design.md`.
The earlier Phase 5 Train/Model document remains supporting UI/UX guidance only.

Phase 3 — Data Definition UX Foundation is complete, final-audit approved, and
merged through PR #16. The earlier ML/Predictor foundation through Arc 15-FU1 and
the merged Phase 1–2 Train/Admin work remain the active owner baseline.

## Current Owner State

- Data Definition is the canonical user-edit owner for Feature definition. The
  approved Phase 4A direction extends it across Predict/ML Feature structure,
  Derived/One-hot, Target/registry, ordering, validation, impact, and safe
  related-contract Save through one versioned structured manifest.
- Data Mapping Manager owns concrete `mapping.json` values and runtime mapping
  cascade; Phase 4 does not move value editing into Data Definition.
- `config/predict/schema.csv`, `config/ml/features.csv`, Derived/One-hot runtime
  policy, Target/registry, and Mapping requirements become generated compatibility
  or consumer projections under Phase 4 rather than independent user-edit owners.
- Canonical generation publication now replaces the legacy full-parity blocker
  for validated presentation-only Save. Protected ML/fixed-string changes remain
  blocked until their consumer migration is accepted.
- Train owns explicit training-data selection and training execution. It consumes
  validated dynamic Feature/Target snapshots and never starts automatically from
  Data Definition Save.
- Predict consumes saved contract snapshots, mapping values, and a promoted
  compatible active model. Findings #1–#6 repaired bounded presentation,
  execution, and runtime group-header synchronization defects. Finding #6 keeps
  the shared standalone/embedded header bound to the current model and columns
  without changing root viewport or column-width policy. Finding #7 model/Target
  display improvement is the next bounded slice; Train navigation, standalone
  routing, guidance, and Bootstrap / Retraining-required integration remain
  separate.
- Train owns run/generation-scoped candidate artifact creation and Phase 5 owns
  explicit validated promotion workflow. Training success does not itself replace
  the active model.
- Phase 5C completed one Qt-free versioned training-result contract, Candidate-
  owned JSON/CSV/XLSX analysis artifacts, production multi-target training
  integration, lifecycle artifact/version validation, terminal failure evidence
  preservation, and separate Candidate publication versus Active promotion.
- Phase 5 lifecycle state lives below the user-state root under a stable workspace
  identity. A repository absolute path is not permanent identity, and Phase 5B
  supports one default workspace only.
- A pre-Phase-5 `model.pkl` becomes the initial Active model only when complete
  compatibility is proven. Otherwise the original is preserved and the workspace
  begins in Bootstrap / Retraining required state.
- Phase 5F uses one strict versioned Experiment Specification across Train GUI
  and headless execution. Explicit campaigns persist current-version contracts,
  bounded attempts, pause/cancel/resume state, and safe run/Candidate/evidence
  references below that same lifecycle workspace. Iteration accounting begins
  only on acknowledgement from the Core optimization owner; configured attempts
  remain total across start and resume; revision identity is repository-owned
  and every incompatible resume outcome is read-only; validate/resolve never
  publish Bootstrap or lifecycle state.
- GUI, headless single-run, campaign, and resume share one non-stealable
  workspace training-writer lock. Read-only run/campaign/model inspection
  remains available during training, and no headless promotion authority exists.
- Phase 5G accepts only explicit external proposals, persists before/delta/after
  evidence before training, preserves stable retry scope, consumes iteration only
  at Core training start, fails closed on unavailable or non-finite gate evidence,
  and keeps deterministic campaign incumbent/recommendation separate from Active.
  Budget extension remains operator-only and every recommendation remains
  approval- and Phase 5H-confirmation-required.
- Phase 5H freezes the selected resolved specification, runs all required
  Targets without search mutation, binds every Confirmation attempt to exact
  child liveness and durable permit/grant evidence, isolates abandoned attempts,
  replays only complete terminal/Candidate pairs, and keeps locked-seal failure,
  final trusted-user decision, migration, retention, Active, export, and Predict
  authority fail-closed and separately owned.
- Train and Predict remain separate PySide6 applications under `apps/train/` and
  `apps/predict/`; the calculator shell and Tkinter path stay separate.
- Canonical calculator launch remains `app_calculator.py` →
  `apps.calculator.app:main`.
- Calculator implementation ownership is under `core/calculators`; calculator
  formulas, profile/config semantics, fixtures/goldens, and public result
  contracts remain protected.
- `core.ml`, `core.predictor_schema`, `core.mapping`, `core.common`, and
  `core.calculators` remain UI-toolkit independent.
- Standard calculation core and standard/region config are calculator-neutral.
  Calculator and ML/Predict reuse their contracts without copying formulas.
- Region config, HW candidate input, ML feature schema, calculator result schema,
  and UI table schema remain separate contracts.

## Milestone Map

### Closed Foundation

- Arc 13 — ML Pipeline Stabilization: complete for automated scope.
- Arc 13.5/13.5A — Feature Catalog Editor/Manager: historical foundation,
  superseded by the Arc 15 Data Definition owner and now retired from the UI.
- Arc 13.5R — Predict Schema projection foundation: complete.
- Arc 14 — Mapping entity, manager UI, runtime cascade, and snapshot export:
  complete for automated scope.
- Arc 15 — Data Definition foundation: complete for automated scope.
- Arc 15-FU1 — controller state-builder extraction: complete, validated, and
  merged into `main` without changing controller behavior.
- Train/Admin UI/UX Overhaul Phase 1 — strict bootstrap, populated mapping
  fixture, dynamic mapping attributes, and aligned mock readiness: complete for
  repository-automated scope and merged before Phase 2.
- Train/Admin UI/UX Overhaul Phase 2 — seven-group Data Mapping information
  architecture, spreadsheet CRUD/Undo, validation and safe persistence, plus
  exchange export/import: merged after repository-automated acceptance; deferred
  native interaction evidence remains separately recorded.
- Train/Admin UI/UX Overhaul Phase 3 — table-first Data Definition inventory,
  controlled Add/Edit, guarded schema Save and impact, saved-only Data Mapping
  handoff/coverage, keyboard/accessibility polish, and bounded native evidence:
  final audit approved and merged through PR #16.
- Train/Admin UI/UX Overhaul Phase 4A — merged-main current-state and contract
  audit: approved for design scope, with canonical manifest, stable identity,
  isolated ordering, generation persistence, runtime snapshot, dirty Mapping,
  One-hot, Target, and artifact boundaries fixed before implementation.
- Train/Admin UI/UX Overhaul Phase 4B — canonical manifest/bootstrap, generated
  projections, cross-validation, scoped fingerprints, immutable generation
  publication, rollback, and guarded Save transaction implemented on Draft PR.
- Train/Admin UI/UX Overhaul Phase 4C+4D — stable-ID Basic Feature lifecycle,
  independent Predict/ML ordering, exact prepared Preview/Apply, and generation
  Save validation implemented.
- Train/Admin UI/UX Overhaul Phase 4E — identity-based Derived operands,
  restricted safe-ratio authoring, deterministic DAG ordering, versioned legacy
  generation decode, and one Train/Predict shared evaluator implemented.
- Train/Admin UI/UX Overhaul Phase 4F–4G — stable-identity One-hot and canonical
  Target/registry authoring implemented and merged through PR #24.
- Train/Admin UI/UX Overhaul Phase 4H+4I — process-wide atomic generation
  cutover, standalone Predict drift detection, dirty Mapping reconciliation,
  generation-bound Predict inference, complete participant stale evidence, actual
  Definition controller cutover, exact dirty Mapping evidence, recovery
  diagnostics, stable Result migration, committed-registry Train Target
  presentation parity, and Phase 4 automated closeout complete.
- Train/Admin Phase 5A — architecture audit and contract freeze complete with
  `PASS`; authoritative design, workspace identity, legacy-model migration, and
  UI/UX priority are fixed for Phase 5B.
- Train/Admin Phase 5B — immutable Candidate publication, revisioned Active
  reference/history, explicit promotion and rollback re-promotion, Bootstrap,
  fail-closed idempotent legacy import, shared Qt-free training orchestration, and
  Predict startup resolution complete. Independent audit returned `PASS` for
  exact head `21b98eb38239e0100be3c3700744c69e2fdc11fe`, and PR #28 was
  squash-merged to `main` as
  `eca6addd38745dadca3b0e4f19cc259090d50e23`.

### Closed — Train/Admin Phase 5C Training Result & Analysis

Phase 5C is complete and merged through PR #30. The final independent L4 audit
returned `PASS`, and required validation run `30157872726` succeeded. The
closeout covers:

- one Qt-free versioned training-result contract;
- Candidate-owned JSON, CSV, and XLSX analysis artifacts;
- production multi-target training integration;
- lifecycle artifact/version validation;
- terminal failure evidence preservation; and
- separate Candidate publication and explicit Active promotion.

Earlier failed audits, repairs, and validation entries remain historical
evidence. `joblib.load()` exception normalization is the intended fail-closed
behavior at the serialized-model deserialization trust boundary and was not a
final blocker.

### Closed — Train/Admin Phase 3 Data Definition UX Overhaul

Phase 3 established the table-first Data Definition inventory, controlled Add/Edit,
guarded schema-only Save, impact/blocker workflow, saved-only Data Mapping
handoff, and keyboard/accessibility polish. It is complete and merged through PR
#16. These boundaries remain in force:

- Data Definition owns structure and mapping attribute definitions; Data Mapping
  owns concrete values.
- Existing projection, validation, save, readiness, handoff, and persistence
  owners remain authoritative until approved Phase 4 replacements are accepted.
- Unsupported active ML rename/delete and projection-changing writes, Remove/
  Reorder, Derived authoring, One-hot group CRUD, Target/registry management, and
  live reload were outside Phase 3 and are owned by Phase 4.
- Automatic retraining, automatic activation, Predict internal redesign, and real
  company data remain excluded.

### Closed — Train/Admin Phase 4 Unified Feature Manager

The Phase 4A audit is approved and Phases 4B–4I are implemented. The final
workflow lets a user manage Predict and
ML Feature contracts without directly editing internal CSV, JSON, Python registry,
or projection files:

```text
Unified Data Definition manifest
    → validated Predict/ML/Derived/One-hot/Target projections
    → immutable generation bundle and atomic active pointer
    → Predict, Train, Data Definition, and Data Mapping owner preflight/cutover
```

Phase 4A fixes these implementation boundaries:

- stable opaque identity is independent of `column_key`, `ml_name`, labels, and
  category values;
- Predict, ML, One-hot emitted, Derived DAG, and Target presentation orders are
  separate contracts;
- dirty Mapping drafts retain state and expose pending-generation reconciliation;
- static, mapping-backed, and external One-hot sources retain distinct owners;
- initial Target CRUD associates only with validated existing model groups and
  target-level policy;
- training runs and candidates preserve scoped start-contract fingerprints;
- candidate and active artifacts remain separate, with explicit Phase 5 promotion;
- one TrainShell process uses staged generation cutover, while standalone Predict
  performs persisted-generation checks at startup and execution boundaries.
- embedded and standalone Predict execute one generation-bound snapshot for
  Derived, One-hot, ordered input, zero-fill, Target/result, and preprocessing;
  compatibility-only static/bootstrap facades are not production runtime owners.

Concrete mapping values remain in Data Mapping. Training remains an explicit user
action in Train. Data Definition does not trigger training or automatic model
activation, and Predict internal redesign is not part of Phase 4.

Phase 4 is complete for repository-automated scope. Its owner and compatibility
boundaries remain the baseline for Phase 5.

### Closed — Train/Admin Phase 5H Final Confirmation and Retention

Phase 5H and Train/Admin Phase 5 are complete and merged through PR #35. The
final independent Lane C audit accepted exact head
`45dd7544afc9546abf4ab450bf634f4c37fb1340`; exact-head run `30433284479`
succeeded, and guarded squash merge produced
`b20661ee6b400559fbac61a9f2669d50256247bc` on `main`.

The closeout freezes immutable Confirmation meaning, executes all
production-required Targets without further search mutation, isolates each
private attempt, blocks replacement while child liveness is live or uncertain,
immutably abandons only proven-ended incomplete attempts, fences stale work,
uses single-use locked final-test disposition, replays only complete linked
terminal/Candidate results, and requires explicit trusted-user final decision
before guarded promotion. Migration apply, retention/delete apply, production
confirmation/promotion, Active, deployment export, and Predict runtime mutation
remain outside repository closeout.

### Current Workstream — Predict UI/UX Findings

Predict findings #1–#6 are complete and merged: populated dropdown rendering,
reset idle projection, running-state projection consistency, user-facing
validation/runtime/partial message semantics, the no-usable-model execution
gate, and runtime group-header synchronization. Finding #6 was guarded
squash-merged through PR #41 as
`1c8c786750c78f538ea7c8ba1395592939dab550`. Runtime projection changes now
rebind the shared standalone/embedded header to the current model and columns,
disconnect stale model signals, avoid duplicate persistent table signals, and
preserve valid horizontal scroll/group geometry after column changes. Root
viewport, column-width policy, lifecycle, execution gating, and other Predict
behavior remain unchanged. Finding #7 now presents application-owned model state
with ordered committed-runtime Target labels through the shared Predict
workspace and awaits fresh Lane B exact-head review; it is not complete or
merged. Existing lifecycle, Target registry, result mapping, and Findings #1–#6
remain unchanged. No later finding is active; guidance and Train navigation
remain separate.

### Later — Production ML Readiness / Calculator Integration

- Validate production model/data availability, prediction quality, physical
  trends, and feature importance through an explicitly approved workstream.
- Define a predicted-points/result envelope for calculator handoff.
- Expand calculator input adapters only through approved owner boundaries.
- Keep seasonal calculation, ranking, and recommendation work separate from
  Train/Predict UI foundation and from formula ownership.

## Deferred / Hold

- Train/Admin Phase 5 is complete and merged. Production confirmation,
  promotion, migration apply, and retention/delete apply remain separate
  controlled operations rather than follow-on repository implementation.
- AS/NZS Excel compatibility and historical reconstruction remain deferred.
- Internal formula trace remains on hold unless a separate core/data contract is
  approved.
- Broad refactors remain trigger-based under `docs/REFACTOR_PLAN.md`.
- Packaging, deployment, and hook integration remain separate workstreams unless
  explicitly promoted.

## State Navigation

- Start every task with `AGENTS.md`; use only the matching router/owner route.
- Read `docs/WORK_PLAN.md` for the current slice, one next action, blockers,
  constraints, and explicit handoff pointers.
- Read this brief when phase, owner state, or milestone direction is needed.
- Read `docs/designs/2026-07-22-train-model-lifecycle-agent-assisted-experiment-design.md`
  before Phase 5B or later Phase 5 implementation. Use the older Phase 5 document
  only as supporting Train/Model and shell UI/UX guidance.
- Read `result_reports/memory/project_memory_seed.md` only for relevant prior
  decisions, failures, open questions, or workstream recovery.
- Use the log/records/legacy evidence for history, not to reconstruct priority.
