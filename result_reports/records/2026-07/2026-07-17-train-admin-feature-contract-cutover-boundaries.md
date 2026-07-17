record:
  date: 2026-07-17
  topic: train-admin-feature-contract-cutover-boundaries
  tags: train-admin, phase-4, contract-generation, training-snapshot, data-mapping, one-hot, model-registry
  memory_review: updated
  memory_reason: Application-wide cutover, training concurrency, dirty draft, category-source, and Target/model-group boundaries are durable prerequisites for every Phase 4 implementation slice.

# Change Reason

The initial Unified Feature Manager design allowed each consumer to reload after
Save but did not prevent mixed active generations or bind concurrent training
results to their start contract. It also left dirty Mapping drafts, One-hot
vocabulary ownership, and Target versus model-group scope ambiguous.

# Contract / Behavior Changed

The proposed Phase 4 design now fixes these durable invariants:

- all persisted projections derive from one immutable contract generation;
- disk publication and application-wide runtime cutover are separate stages;
- required consumers never silently activate mixed generations;
- each training run, result, and artifact retains its immutable start-generation
  Feature/Target/preprocessing identity;
- Definition Save does not retroactively alter an active run, and stale artifacts
  are not current-compatible by default;
- Definition reload never silently discards a dirty Data Mapping draft;
- static, mapping-backed, and external/provider-backed One-hot vocabularies have
  distinct mutation owners;
- default Target CRUD associates with validated existing model groups and does
  not imply arbitrary model-group or model-level policy creation.

Phase 4 remains proposed. No runtime, public API, schema, config, data, fixture,
or production behavior changed.

# Evidence And Verification

- Current `TrainingRequest` and `TrainingResult` contain run/path/preprocess state
  but no contract generation or projection fingerprints.
- Data Mapping owns draft/baseline/undo state and projects current Definition
  requirements; explicit Reload is the provider-reload/discard boundary.
- Current One-hot validation distinguishes selector and emitted rows but has no
  category source-mode contract.
- Current Python model registry combines model groups, Targets, `use_rfe`, and
  target rules, confirming the need to separate default Target CRUD from
  model-level policy management.
- Focused Markdown, stale-expression, staged-scope, and repository change-gate
  checks are performed before commit.

# Changed Files

- Active Train/Admin Phase 4/5 designs, governing direction, current planning,
  milestone log, result index, and active memory.
- No production source, configuration, schema, data, fixture, or model artifact.

# Known Risks

Phase 4A still must choose the runtime cutover failure fallback, dirty Mapping
rebase/conflict rules, exact training snapshot payload/fingerprints, category
identities and ordering per source mode, and whether a separately validated
model-group creation workflow is approved. Existing guards remain in force until
those decisions are implemented.
