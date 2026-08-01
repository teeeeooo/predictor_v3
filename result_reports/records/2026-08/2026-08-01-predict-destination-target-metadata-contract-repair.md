record:
  date: 2026-08-01
  topic: predict-destination-target-metadata-contract-repair
  tags: predict, typed-result, target-metadata, identity, unit, value-source, correction
  memory_review: no-change
  memory_reason: Architecture and Work Plan own the corrected projection boundary while PR #44 remains an unmerged Draft; this record preserves exact repair evidence.
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

Fresh audit found that a supplied `PredictionTargetDescriptor` could be
internally complete and consistent with sibling descriptor fields while forging
stable Target identity-bound metadata. The prior validator did not compare the
descriptor against the Target registry and canonical runtime owners that
created the normal five-target projection.

# Completed Boundary

`PredictRuntimeSnapshot` now retains the immutable ordered `RuntimeTarget`
projection already produced by the Data Definition Target registry. The
application validator derives the expected descriptor from that Target
identity/ML-name/Result-Feature association, the canonical Feature-bound result
key, the existing five-target unit mapping, and the fixed
`model_prediction` source. Supplied descriptors, active Target names, and
Target/result-key pairs must match the derived contract exactly.

Unknown or rebound identity, ML name, Result Feature, result key, unit, source,
and active-set variants fail before standalone/embedded composition or sealed
zero-result migration artifact issue. Rejection leaves cases, results,
revisions, allowed executions, the active contract, and issued-artifact ledger
unchanged; the genuine five-target contract remains immediately eligible.

# Compatibility And Scope

No writable Target/unit registry or Feature Definition schema field was added.
The public/generated Predict schema and persisted Feature Definition shape are
unchanged. Prior canonical acceptance, case cleanup, artifact lifecycle,
freshness, migration/rollback, progress, cancellation, and five-target W/Hz/kg
contracts remain intact. Partial-target models, EER/COP, Result Review, Layout B,
bulk paste/export, Calculate integration, history, controller refactor, and
generation lifecycle redesign remain excluded. PR #44 remains Draft and Slice 2
is not closed.
