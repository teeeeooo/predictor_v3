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

Phase 5B lifecycle foundation remains the current slice. The final bounded audit
rejected second-repair head `f944cbc6d40a36db94a599462bb2cdcc21ce2265`
because committed Active cleanup recovery could restore or permanently block the
wrong revision, the global Qt fixture broke non-Qt CI, and the Active resolver hid
unexpected programmer errors. The three blockers now have a bounded repair and
new local exact-source validation. The Draft PR requires a new exact-head
independent audit before Phase 5B can close. Phase 5C has not started. The
authoritative Phase 5 design is
`docs/designs/2026-07-22-train-model-lifecycle-agent-assisted-experiment-design.md`.
The earlier Phase 5 Train UI document remains supporting UI/UX guidance only;
the new design governs lifecycle, CLI, campaigns, the agent loop, migration, and
implementation order.

Phase 5 keeps Train/Model UI/UX improvement as the primary product goal. The
Candidate repository, explicit Active reference, promotion/rollback service,
Bootstrap state, fail-closed legacy import, shared training application boundary,
and Predict startup resolver remain the foundation for that UI. The two repairs
add symlink/path-escape rejection, descriptor-relative root locking,
rollback/recovery-marked durability outcomes, non-optional revision guards,
controlled corrupt legacy state, exactly-once QProcess terminal arbitration,
and deterministic Qt application/process cleanup without expanding the Phase
5B product scope.

## Next Action

Commit and push the final bounded Phase 5B audit repair to Draft PR #28, confirm
the official check, then hand the new exact head to an independent auditor. Do
not start Phase 5C or call Phase 5B merge-ready before that re-audit.

## Active Blockers

- Phase 5B closure is held for independent exact-head re-audit of Draft PR #28.
  Local focused, canonical, structure, and change-gate evidence is repair
  evidence, not independent approval.
- Model-incompatible Definition generations may publish and cut over, but Predict
  remains blocked with Retraining required until compatibility is proven. No model
  artifact is automatically replaced or promoted.
- Existing fixed-index Predict keys remain protected migration targets; saved
  user-created Features without those dependencies remain renameable/removable.
- Windows native Feature Manager smoke remains a pre-release verification item;
  automated macOS/offscreen coverage is not a substitute for that evidence.

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
- Phase 5B must resolve lifecycle state beneath the user-state root through a
  stable workspace identity. A repository absolute path is not a permanent
  workspace identity, and Phase 5B supports one default workspace only.
- Import an existing `model.pkl` as the initial Active model only when complete
  compatibility is proven. Otherwise preserve the original artifact and begin in
  Bootstrap / Retraining required state.
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

- Phase 5F–5G CLI/campaign and agent-assisted loop work remains later than the
  lifecycle and Train/Model UI slices; it must not displace the UI/UX priority.
- Deferred Phase 2 native interaction acceptance remains a separate acceptance
  item and does not block Phase 5B.
- Predict internal UI/UX overhaul begins only after Train/Admin Phase 5 and a fresh
  populated-state audit.
- Real mapping values, training data, model quality, and production-readiness
  validation remain company-local.

## Minimal Anchors

- Governing design: `docs/designs/2026-07-14-train-admin-ui-ux-overhaul-governing-design.md`
- Phase 4 design: `docs/designs/2026-07-17-train-admin-phase-4-unified-feature-manager.md`
- Approved Phase 4A closeout: `docs/designs/2026-07-17-train-admin-phase-4a-current-state-contract-audit-closeout.md`
- Authoritative Phase 5 design: `docs/designs/2026-07-22-train-model-lifecycle-agent-assisted-experiment-design.md`
- Supporting Phase 5 UI/UX design: `docs/designs/2026-07-14-train-admin-phase-5-train-model-shell-ux-overhaul.md`
- Phase 5A decision record: `result_reports/records/2026-07/2026-07-23-train-admin-phase5a-architecture-audit-closeout.md`
- Phase 3 foundation design: `docs/designs/2026-07-14-train-admin-phase-3-data-definition-ux-overhaul.md`
- Arc 15 owner foundation: `docs/designs/2026-07-06-arc15-unified-data-definition-manager-foundation.md`
- Phase 4A result record: `result_reports/records/2026-07/2026-07-17-train-admin-phase4a-contract-audit-closeout.md`
- Phase 4B result record: `result_reports/records/2026-07/2026-07-17-train-admin-phase4b-unified-contract-persistence.md`
- Phase 4B final audit correction: `result_reports/records/2026-07/2026-07-17-train-admin-phase4b-final-audit-correction.md`
- Phase 4C+4D closeout: `result_reports/records/2026-07/2026-07-17-train-admin-phase4c-4d-feature-manager.md`
- Phase 4E contract: `docs/designs/2026-07-18-derived-feature-authoring-shared-evaluator.md`
- Phase 4E result: `result_reports/records/2026-07/2026-07-18-train-admin-phase4e-derived-authoring.md`
- Phase 4E audit correction: `result_reports/records/2026-07/2026-07-18-train-admin-phase4e-derived-eligibility-correction.md`
- Phase 4E final runtime-shape correction: `result_reports/records/2026-07/2026-07-18-train-admin-phase4e-runtime-shape-correction.md`
- Phase 4F result: `result_reports/records/2026-07/2026-07-18-train-admin-phase4f-one-hot-authoring.md`
- Phase 4F audit correction: `result_reports/records/2026-07/2026-07-22-train-admin-phase4f-audit-correction.md`
- Phase 4F merge closeout: `result_reports/records/2026-07/2026-07-22-train-admin-phase4f-merge-closeout.md`
- Phase 4G result: `result_reports/records/2026-07/2026-07-22-train-admin-phase4g-target-registry-authoring.md`
- Phase 4H+4I closeout: `result_reports/records/2026-07/2026-07-22-train-admin-phase4h-4i-runtime-closeout.md`
- Phase 4H+4I audit correction: `result_reports/records/2026-07/2026-07-22-train-admin-phase4h-4i-audit-correction.md`
- Phase 4H+4I final audit correction: `result_reports/records/2026-07/2026-07-22-train-admin-phase4h-4i-final-audit-correction.md`
- Phase and milestone direction: `project_brief.md`
- Durable milestone history: `project_log.md`
- Active memory: `result_reports/memory/project_memory_seed.md`
- Structural candidates: `docs/REFACTOR_PLAN.md`
