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

Train/Admin Phase 4A — Current-state and Contract Audit is approved and closed by
`docs/designs/2026-07-17-train-admin-phase-4a-current-state-contract-audit-closeout.md`.
No production implementation was included. The next implementation slice is
Phase 4B — Unified Contract and Multi-artifact Persistence.

Phase 4B must establish the canonical structured manifest, stable identities,
bootstrap migration, generated projection providers, immutable generation
bundle, atomic active-generation pointer, cross-contract validation, rollback,
and scoped fingerprints before broader Feature mutation or UI work begins.

## Next Action

After this closeout is merged to `main`, start Phase 4B on a separate branch and
Draft PR from the merged closeout baseline. Audit the existing Data Definition,
Predict schema, ML Feature Catalog, Derived policy, registry, mapping-requirement,
and runtime consumers only as needed to choose the minimum consistent package and
migration shape required by the approved Phase 4A contract.

Do not start Slice 4C mutation commands, Feature Manager UI, Derived/One-hot/
Target authoring, live cutover, or model promotion runtime work inside the 4B
foundation slice.

## Active Blockers

- Phase 4B production implementation must not begin from an unmerged Phase 4A
  closeout branch.
- Current production paths continue blocking ML-projection-changing Definition
  saves until Phase 4B implements and validates the canonical persistence owner,
  migration, all-or-nothing publication, and rollback boundary.
- Existing import-time/fixed-string consumers remain protected migration targets;
  ordinary Rename/Delete is not enabled before their approved provider or atomic
  migration boundary exists.
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

- Slices 4C–4I remain deferred until Phase 4B establishes the approved canonical
  contract and persistence foundation.
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
- Phase and milestone direction: `project_brief.md`
- Durable milestone history: `project_log.md`
- Active memory: `result_reports/memory/project_memory_seed.md`
- Structural candidates: `docs/REFACTOR_PLAN.md`
