record:
  date: 2026-08-01
  topic: predict-typed-result-execution-context
  tags: predict, typed-result, execution-context, stale-result, model-reload, generation-migration
  memory_review: no-change
  memory_reason: Active Predict owner documents and the indexed record are sufficient for this unmerged slice; durable project memory should change only after independent audit and merge closeout.
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

Predict previously attached formatted string results by `case_id` without
proving that the worker event still belonged to the active session, run, case
input revision, runtime semantics, or loaded model. Late events around edits,
reload, and generation cutover could therefore overwrite current case state.

# Contract / Behavior Changed

Predict application now owns immutable typed target outcomes, execution
semantics/model provenance, and current/stale freshness independently from row
execution status. `PredictSession` owns case-local input revisions, one allowed
context per case, a fail-closed result gate, and bounded rejection diagnostics.
It reuses the runtime snapshot's existing scoped fingerprints and lifecycle
loaded identity; generation ID is retained for traceability but excluded from
freshness equality. Presentation-only migration updates result keys by Feature
identity and remains current, while semantic or successful model changes retain
raw outcomes/provenance and mark them stale. Failed reload and rollback preserve
the prior currentness.

The five validated stable Targets use a closed Predict unit catalog (`W`, `Hz`,
and `kg`). Unknown active Target identities fail composition because this slice
does not add unit fields to the persisted Feature Definition schema.

# Evidence And Verification

- Narrow typed outcome, stale acceptance, migration, reload, and run-event
  suite: 58 passed.
- Targeted Predict application/runner/session/lifecycle/generation/shared-
  composition suite: 133 passed, with one QWidget-only Slice 1 table smoke
  deselected because this slice has no new user-facing GUI behavior.
- Qt-free imports and unchanged generated/persisted shapes are exercised in the
  suites. Changed-source compilation, repository structure, diff hygiene, and
  staged change gates passed at final Worker validation.

# Changed Files

- Predict application target/result/context contracts, runtime snapshot,
  composition, result adapter, usecase, controller, service, and worker payload.
- Canonical Predict case/session/result state and generation migration.
- Focused contract, concurrency, lifecycle, migration, compatibility, and
  standalone/embedded composition tests.
- Clean architecture, PySide Train/Predict architecture, and current work plan.
- This compact record and discovery index row.

# Known Risks

- Unit authoring for a future new Target identity remains unavailable without a
  separately approved semantic schema/unit-owner decision; runtime fails closed.
- Rejection diagnostics are bounded in-memory evidence, not persistent history
  and not a user notification surface.
- Result Review, EER/COP, `사양 요약`, Layout B, bulk paste, export redesign,
  partial-target Active models, and cross-launch result history remain excluded.
- No production generation, model, mapping, lifecycle artifact, or user data is
  mutated by this slice.
