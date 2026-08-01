record:
  date: 2026-08-01
  topic: predict-runtime-target-authority-provenance-recovery
  tags: predict, typed-result, target-authority, provenance, generation, correction
  memory_review: updated
  memory_reason: Predict runtime authority now requires exact repository-issued Generation and runtime objects rather than caller-coherent Target projections.
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

Two exact-head audits found that the prior destination metadata validator treated
`target_registry_targets` as authority even though it and the supplied
fingerprint lived inside the same caller-controlled runtime. A coherent
five-to-four Target reduction therefore passed validation and composition while
reusing the genuine fingerprint.

# Contract / Behavior Changed

The validated generation repository now issues the exact immutable
`GenerationSnapshot`. Predict runtime construction accepts only that issued
object, and registers the exact immutable runtime payload outside the runtime's
own asserted fields. Composition, execution-semantics projection,
PredictionService/model lifecycle adoption, and zero-result migration validate
that provenance before consuming Target projections or fingerprints.

After provenance succeeds, the existing Data Definition Target registry,
Feature identity/key, five-target W/Hz/kg unit seam, and fixed
`model_prediction` source still derive the convenience descriptor projection.
No caller-constructed or `replace()`-produced runtime can acquire authority by
preserving or coherently changing fingerprint-like metadata.

# Evidence And Verification

Characterization on the starting head accepted a coherent four-target runtime
and built its result mapper while retaining the genuine fingerprint. Regression
coverage now rejects that case, caller-updated fingerprints, coherent ML-name
changes, Result-Feature swaps, and unit/source forgeries before mapper creation.
Zero-result migration rejection leaves cases, results, revision, active
contract, allowed execution, and issued-artifact count unchanged. A genuine
five-target terminal result is accepted immediately afterward. Repository-backed
standalone and embedded composition share the same issued runtime.

# Changed Files

The recovery changes generation/runtime authority issuance and adoption gates,
updates production-backed test setup and focused forgery/migration regressions,
and corrects the active architecture and Work Plan trust-model descriptions.

# Known Risks

Authority registration is process-local by design because runtime snapshots are
in-process immutable execution objects; a future cross-process serialized
runtime contract would need a separate durable signing/verification design.
Public/generated Predict schema and persisted Feature Definition shape remain
unchanged. Partial-target models, Target authoring, EER/COP, Result Review,
Layout B, bulk workflows, Calculate integration, history, controller refactor,
and generation transaction redesign remain excluded. PR #44 stays Draft and
Slice 2 is not recorded as closed.
