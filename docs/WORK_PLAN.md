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

Phase 5H lifecycle closeout source is under final bounded repair on its Lane C
Draft branch after the first independent audit failed at exact head
`009e4d3d668df2fc3df13a06aa22a8991ec67299`. Historical run `30280886312`
succeeded but did not make that audit a pass. The second independent audit also
failed at repaired exact head
`97914c0285c7155ecfbd6da1fb9fa1d7c60f24a7`; historical run `30286229720`
succeeded but is likewise validation-only evidence. The same PR now adds immutable
content-addressed confirmation snapshots, all-production-Target fixed
confirmation, content-addressed single-use locked final-test seals with actual
evaluation, trusted opaque interactive user capabilities and single-use
decisions routed through the existing guarded promotion owner, strict
historical dispositions, byte-invariant migration/retention previews, Predict
loaded-model leases, and a complete fail-closed lifecycle reference inventory.
The third independent audit failed at exact head
`ae20c626a12c15906c5ffb9e4f159875418caed4`; historical exact-head run
`30323789487` succeeded but remains validation-only evidence. Its two blockers
are repaired by a versioned, hashed execution claim that can reconstruct the
exact pending confirmation before one durable start, and one locked-test
finalization integrity fence that revalidates snapshot, seal, dataset,
membership, Target/split/evaluation policy, immutable result, and staged
Candidate linkage inside the shared writer lock before atomic public
finalization. The repair remains pending independent exact-head re-audit. No
production confirmation/promotion, migration apply, deletion, or deployment
mutation has been performed.

Phase 5G Agent-assisted Campaign Loop is complete and merged. The final
independent re-audit accepted exact head
`3344be1237f56752f8fcb607074152c53ea75c52`; required exact-head run
`30203030680` succeeded, and PR #34 was guarded squash-merged to `main` as
`cb9183353dd6492dff07012c4276e4beb2b582b8`. Preserve the two earlier audit
`FAIL` heads `029fefdd783c21f380f6d43c6bd6efe403a52b28` and
`a58f4584344fce921341bddc25091aef79403485`, plus successful runs
`30199916760` and `30201667033`, as historical validation evidence only.
The merged Phase 5G contract accepts only explicit external one-step proposals,
keeps stable retry scope and total attempt allowance across pre-start resume,
uses Core-start-only iteration accounting, rejects proposal-side budget
escalation, fails closed on unavailable or non-finite selection evidence, and
rebuilds deterministic campaign incumbent, leaderboard, and immutable
approval-required recommendations without changing Active, Definition, or
deployment. Phase 5H reuses those immutable recommendation and execution owners.

Phase 5F Headless Experiment Interface is complete and merged. The final
independent re-audit accepted exact head
`fa13ddd75c5cf8a423d3ffc1fc046f552086e01a`; required validation run
`30197335156` succeeded, and PR #33 was squash-merged to `main` as
`1f441c6d82545943aa160919c7d97d3a4b969580`. Preserve the earlier independent
audit `FAIL` heads `b5ce141711c3660e2ce38b738f58f478a333d251` and
`e5558e82d7ca736bb45ca71eb94ab83b71a19950`, plus successful validation runs
`30193572243` and `30195511666`, as historical evidence only.
The merged Phase 5F contract provides one strict GUI/headless Experiment
Specification and training application owner, versioned machine output,
single-run and explicit bounded campaign execution, pause/cancel/resume, total
per-iteration retry allowance, Core-owned training-start accounting,
repository-owned build identity, detached fail-closed compatibility outcomes,
read-only validate/resolve, and one workspace-wide training writer lock. Phase
5G reuses these owners without changing their accounting meaning. It
preserves explicit user promotion, immutable deployment export, and Predict
reload boundaries.

Phase 5D Train/Model UI/UX is complete and merged. The user accepted repaired
head `a2ea64464e595d28d58db77a28d31eac60c6a72d` and authorized PR #31 closeout;
GitHub squash-merged it to `main` as
`78e9d097693c3e3b8c23d2ed18dd7e68dc1f44b0`. The first and second independent
audit `FAIL` results remain historical evidence, and no independent `PASS` is
retroactively declared. Phase 5D now owns the Candidate/Active Train surface,
dynamic Phase 5C result projection, explicit guarded promotion, rollback by
re-promotion, Bootstrap, current compatibility, fail-closed corruption, and
complete Korean rejection guidance. Exact-head validation run `30165774817`
succeeded. Phase 5B and Phase 5C remain complete and merged foundations.
The authoritative Phase 5 design is
`docs/designs/2026-07-22-train-model-lifecycle-agent-assisted-experiment-design.md`.
The earlier Phase 5 Train UI document remains supporting UI/UX guidance only;
the new design governs lifecycle, CLI, campaigns, the agent loop, migration, and
implementation order.

Phase 5E Deployment Export and Predict Reload Boundary is complete and merged.
PR #32 was squash-merged to `main` as
`f372f5d2d5f01c96eb9b547bb5758c9c561e0836` from accepted exact head
`cf0b71d86a3e490799c98e8f32a0f2652d6d660b`. The final independent L4 audit
returned `PASS`, and required validation run `30188757140` succeeded. The
first independent L4 audit
returned `FAIL` at exact head
`5364ff7a106f27975e649d44a3b0059509dc797e`: an older reload failure could
overwrite a newer successful reload state, and reload/export failures were not
structured or safely separated from raw diagnostics. The bounded repair adds a
monotonic application-owned reload operation guard and structured Korean
failure guidance while retaining raw diagnostics/traceback outside the default
message. The second independent L4 audit also returned `FAIL` at repaired exact
head `f22d6e9526bc3c31d0775123a9614b860fadbf5b`: ordinary refresh could bypass
ordering, stale UI completion could start another unguarded refresh,
prediction-running UI bypassed structured application guidance, and unexpected
export exceptions could escape the UI event boundary. The second bounded repair
uses one monotonic status-observation sequence for refresh and reload, renders
stale callbacks from the read-only authoritative status, routes running reload
through the application outcome, and normalizes unexpected export failures
while preserving raw diagnostics.
Predict now keeps a process-loaded Candidate/revision, observes current Active
without hot-swap, exposes explicit idle reload, and preserves the prior bundle
on corruption, incompatibility, recovery, running-state, or Active-race failure.
Train/Model can create a checksum-verified immutable export only from the
guarded current Active without changing Candidate, Active, or history. Phase 5D
promotion and rollback remain unchanged. No-hot-swap, explicit idle reload,
reload-failure preservation, and immutable current-Active-only export remain
the Phase 5E contracts. Leaderboard, the Agent-assisted Experiment Loop,
retention, and executable packaging remain later slices.

## Next Action

Complete Worker validation and provide the new exact head for one independent
exact-head re-audit of the Phase 5H Draft PR. Do not merge
or claim Phase 5 completion until that audit and required CI evidence accept the
same head. Keep real-user confirmation/promotion and migration/delete apply as
separately authorized controlled operations.

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

- Phase 5G agent-assisted selection/ranking/recommendation is complete and
  merged. Phase 5H source is pending independent audit and must not grant
  autonomous production/delete authority or bypass explicit final confirmation.
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
- Phase 5G closeout record: `result_reports/records/2026-07/2026-07-26-phase5g-post-merge-closeout.md`
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
