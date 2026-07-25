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

Phase 5D Train/Model UI/UX is implemented on its dedicated Draft PR branch.
The first independent L4 audit returned `FAIL` at
`c163da7027cdfdcc1bc8f831c17f6e1285b0d6db` with five UI state/projection
blockers. Those blockers are repaired on the same branch, and the repaired
head `89e20055cc45a5c7fad59aa24a2b9d34c16e4237` received a second independent
`FAIL`: its sole remaining blocker was incomplete training-running guidance in
the normal disabled-button QWidget state. That bounded blocker is repaired on
the same branch, and the new exact head awaits independent L4 re-audit. Phase
5C Training Result & Analysis
is complete and merged through PR #30 to `main`
at `8f74fc613d1ad6f6a1cc2c9d206543198f6d88f8`; its final independent L4 audit
returned `PASS`, and required validation run `30157872726` succeeded. Phase 5C
completed the Qt-free versioned training-result contract, Candidate-owned
JSON/CSV/XLSX analysis artifacts, production multi-target training integration,
lifecycle artifact/version validation, terminal failure evidence preservation,
and separate Candidate publication versus Active promotion. Earlier failed
audits, repairs, and validation entries remain historical evidence. The
`joblib.load()` exception normalization is intentional fail-closed behavior at
the serialized-model deserialization trust boundary and was not a final
blocker. Phase 5B lifecycle foundation head
`21b98eb38239e0100be3c3700744c69e2fdc11fe` passed independent audit and PR
#28 was squash-merged to `main` as
`eca6addd38745dadca3b0e4f19cc259090d50e23`; no Phase 5B merge blocker remains.
Phase 5B establishes immutable Candidate publication, explicit revision-guarded
Active promotion and rollback, recovery, and Predict startup resolution.
The authoritative Phase 5 design is
`docs/designs/2026-07-22-train-model-lifecycle-agent-assisted-experiment-design.md`.
The earlier Phase 5 Train UI document remains supporting UI/UX guidance only;
the new design governs lifecycle, CLI, campaigns, the agent loop, migration, and
implementation order.

Phase 5 keeps Train/Model UI/UX improvement as the primary product goal. Phase
5D now shows Candidate and Active state through an understandable,
metric-centered UI, provides explicit `이 모델 사용` promotion, supports rollback
by selecting a previous Candidate, and handles Bootstrap/no-active state
normally. The UI displays the Phase 5C contract without recalculating metrics or
eligibility. The audit repair adds safe populated/empty/error table transitions,
current owner-validated compatibility, target-level comparison fidelity,
complete persisted Advanced evidence, and structured Korean promotion failure
guidance. The follow-up repair makes the default training-running state also
state that Active is maintained and that the user should retry after training;
detailed internal information belongs in an Advanced area. CLI, Campaign,
leaderboard, the Agent-assisted Experiment Loop, runtime reload, export, and
retention remain later slices.

## Next Action

Keep PR #31 open, Draft, and unmerged and obtain an independent L4 re-audit
against the repaired exact head. Preserve both audit `FAIL` results as
historical evidence. Do not declare audit PASS or start Phase 5E/later work from this
repair worker. Keep CLI, Campaign,
leaderboard, the Agent-assisted Experiment Loop, runtime reload, export, and
retention deferred.

## Active Blockers

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
- Lifecycle state resolves beneath the user-state root through a stable workspace
  identity. A repository absolute path is not a permanent workspace identity,
  and the current foundation supports one default workspace only.
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
- Phase 5B closeout record: `result_reports/records/2026-07/2026-07-25-train-admin-phase5b-post-merge-closeout.md`
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
