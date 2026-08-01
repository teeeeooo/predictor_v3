record:
  date: 2026-08-01
  topic: predict-canonical-result-state-boundary-recovery
  tags: predict, typed-result, canonical-state, projection, rollback, atomicity, correction
  memory_review: no-change
  memory_reason: Architecture and Work Plan carry the durable invariant while PR #44 remains an unmerged Draft; this record preserves correction evidence.
change_gate:
  new_source: small
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

PR #44 had repaired malformed fresh-result acceptance and direct/bulk terminal
setter bypasses, but runtime projection restore could still install the same
context-free `complete` row and make the canonical summary count it. Validity
therefore depended on the entry API instead of the state held by
`PredictSession`.

# Canonical State Recovery

`PredictSession` now exposes its result mapping read-only and permits six
explicit mutation families: non-executed state creation, fresh executed-result
acceptance, validated migration, sealed rollback, freshness transformation, and
deletion. Stored non-executed state is limited to payload-free
`pending`/`running`/`invalid`; every terminal state retains typed execution
provenance and satisfies its aggregate/target contract.

Fresh acceptance still validates the pinned request. Generation preparation now
asks the session to validate current source state, result migration lineage, and
the destination Target/semantic/model contract before issuing a sealed artifact.
Apply accepts only the unchanged artifact from the issuing session. Rollback is
a separate one-use snapshot artifact containing the previously valid results,
case revisions, runtime contract, allowed executions, and session revision.
Caller-created or altered projection objects fail before canonical mutation.

Presentation-only Feature-key migration keeps valid results current. Runtime
semantic or Target-registry changes preserve typed outcomes and provenance as
stale; shared result Features receive their destination keys while removed
historical outcomes retain their evidence. Projection rejection leaves case
values, revisions, results, run authority, and session revision unchanged.

# Fixture And Compatibility Recovery

UI, participant, migration, and rollback fixtures now create terminal rows
through `allow_result()` and `accept_result()`. No test uses projection restore
as an arbitrary installer, and no unsafe production fixture API exists.

The five-target W/Hz/kg catalog, raw precision, accepted-progress
reconciliation, cancellation/infrastructure context, model freshness,
generation rollback, standalone/embedded composition, public/generated Predict
schema, and persisted Feature Definition shape remain unchanged. EER/COP,
Result Review, Layout B, partial-target models, unit authoring, Calculate, and
cross-launch history remain excluded. PR #44 remains Draft; Slice 2 is not
recorded as merged or closed.

# Verification

Verification commands and exact pass counts are recorded in the final Worker
handoff for the repaired PR head. The repository boundary suite includes direct,
bulk, acceptance, freshness, deletion, sealed migration/apply, tamper rejection,
and exact rollback characterization, plus the prior three adversarial repairs.
