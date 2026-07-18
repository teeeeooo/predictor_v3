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

Train/Admin Phase 4E — Restricted Derived Feature Authoring and Shared Evaluator
is implemented over the Phase 4B–4D baseline. Canonical v2 Derived operands use
Feature/Derived stable identities; historical v1 name-based generations remain
readable and rollback-safe through explicit compatibility decoding. Restricted
`safe_ratio` Add/Edit/Rename/Duplicate/Remove/Enable/Disable commands, deterministic
DAG ordering, prepared Preview/Apply, inactive-safe generation Save, and table-first
authoring are connected. One pure evaluator now owns the existing eight production
formula semantics for both Train and Predict. Derived semantics and active model
compatibility fingerprints are separate, while active semantic/activation changes
remain blocked by the retraining/migration Save guard. The Phase 4E audit correction
also centralizes pre-evaluator operand eligibility and transitive base dependency
projection in the same immutable core snapshot, blocks Result/Target leakage in
commands and whole-contract validation, and removes View/Predict policy duplication.

## Next Action

Reaudit and integrate the corrected Phase 4E change in Draft PR #22. After its
audit/merge boundary, start
Phase 4F One-hot group/category CRUD. Keep Target/registry authoring, runtime
cutover, model candidate generation, training, and promotion outside Phase 4F.

## Active Blockers

- Active Derived activation or semantic changes remain Save-blocked until an
  approved retraining/migration boundary; inactive definitions are publishable.
- Actual protected ML/import-time/fixed-string consumers still block ordinary
  ML-name/order/One-hot/Target changes until their explicit migration.
- Existing fixed-index Predict keys remain protected migration targets; saved
  user-created Features without those dependencies remain renameable/removable.
- Windows native Feature Manager smoke remains a pre-release verification item;
  automated macOS/offscreen coverage is not a substitute for that evidence.
- Phase 5 Train/Model and Shell UX remains on hold until Phase 4 is stable.

## Active Constraints

- Preserve Data Definition as the canonical user-edit owner through one versioned
  structured JSON manifest. Exact path, package layout, DTO names, and field
  spelling are selected by Phase 4B after owner audit.
- Keep `config/predict/schema.csv`, `config/ml/features.csv`, Derived/One-hot,
  Target/registry, and Mapping requirements as generated compatibility or
  consumer projections rather than independent editors.
- Preserve the Data Definition/Data Mapping owner boundary and runtime
  `mapping.json` value contract.
- Preserve the accepted Qt-free draft, command, edit policy, projection,
  validation, save-plan, schema-writer, readiness, handoff, coverage, keyboard,
  focus, accessibility, and exact-navigation owners until their approved
  replacement or adapter is accepted.
- Use immutable stable identities independent of user-facing keys and ML names.
  Duplicate creates a new identity; Rename preserves identity and validates
  dependencies.
- Keep Predict display order, ordered ML contract, One-hot emitted order, Derived
  DAG order, and Target presentation order isolated.
- Publish immutable Definition generations through one all-or-nothing bundle and
  atomic active-generation pointer. Disk publication, consumer preflight, and
  runtime cutover remain distinct states.
- Require one active contract generation across required TrainShell consumers;
  preserve prior active generation and expose stale/restart-required after a
  failed preflight rather than allowing mixed normal state.
- Preserve active training-run snapshots and Data Mapping unsaved drafts across
  Definition changes. Do not classify stale artifacts as current-compatible.
- Separate training candidate publication from validated explicit active-model
  promotion, and distinguish TrainShell process-wide cutover from standalone
  Predict cross-process generation detection.
- Separate static/mapping-backed/external One-hot category mutation owners and
  Target CRUD from new model-group/model-level policy creation.
- Data Mapping remains the concrete `mapping.json` value owner; Train remains the
  explicit training-execution owner; Predict remains a saved-contract and
  compatible-model consumer.
- Phase 4 excludes automatic retraining, automatic promotion/activation, training
  execution from Data Definition, and Predict internal redesign.
- Use repository fixtures and mock data; do not add company production data or
  infer model quality or production readiness.
- Keep Cooling and Heating models independent, including monotone constraints.

## Deferred / Hold

- Slices 4F–4I remain deferred; Slice 4F begins only after Phase 4E integration.
- Phase 5 Train/Model and Shell implementation begins only after Unified Feature
  Manager stabilization and a fresh dynamic-contract audit.
- Deferred Phase 2 native interaction acceptance remains a separate acceptance
  item and does not block Phase 4.
- Predict internal UI/UX overhaul begins only after Train/Admin Phase 5 and a fresh
  populated-state audit.
- Real mapping values, training data, model quality, and production-readiness
  validation remain company-local.

## Minimal Anchors

- Governing design: `docs/designs/2026-07-14-train-admin-ui-ux-overhaul-governing-design.md`
- Phase 4 design: `docs/designs/2026-07-17-train-admin-phase-4-unified-feature-manager.md`
- Approved Phase 4A closeout: `docs/designs/2026-07-17-train-admin-phase-4a-current-state-contract-audit-closeout.md`
- Deferred Phase 5 design: `docs/designs/2026-07-14-train-admin-phase-5-train-model-shell-ux-overhaul.md`
- Phase 3 foundation design: `docs/designs/2026-07-14-train-admin-phase-3-data-definition-ux-overhaul.md`
- Arc 15 owner foundation: `docs/designs/2026-07-06-arc15-unified-data-definition-manager-foundation.md`
- Phase 4A result record: `result_reports/records/2026-07/2026-07-17-train-admin-phase4a-contract-audit-closeout.md`
- Phase 4B result record: `result_reports/records/2026-07/2026-07-17-train-admin-phase4b-unified-contract-persistence.md`
- Phase 4B final audit correction: `result_reports/records/2026-07/2026-07-17-train-admin-phase4b-final-audit-correction.md`
- Phase 4C+4D closeout: `result_reports/records/2026-07/2026-07-17-train-admin-phase4c-4d-feature-manager.md`
- Phase 4E contract: `docs/designs/2026-07-18-derived-feature-authoring-shared-evaluator.md`
- Phase 4E result: `result_reports/records/2026-07/2026-07-18-train-admin-phase4e-derived-authoring.md`
- Phase 4E audit correction: `result_reports/records/2026-07/2026-07-18-train-admin-phase4e-derived-eligibility-correction.md`
- Phase and milestone direction: `project_brief.md`
- Durable milestone history: `project_log.md`
- Active memory: `result_reports/memory/project_memory_seed.md`
- Structural candidates: `docs/REFACTOR_PLAN.md`
