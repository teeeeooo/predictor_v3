record:
  date: 2026-07-17
  topic: train-admin-model-promotion-predict-generation-boundaries
  tags: train-admin, phase-4, phase-5, model-artifact, promotion, predict, process-generation, one-hot
  memory_review: updated
  memory_reason: Candidate promotion and standalone Predict generation detection are durable cross-phase safety boundaries not covered by the prior in-process cutover decision.

# Change Reason

The proposed design separated training snapshots from current compatibility but
did not prevent training completion from replacing the active model before
validation. It also used generation-cutover language that could imply atomic
coordination across standalone application processes, and its One-hot acceptance
overstated Data Definition category ownership.

# Contract / Behavior Changed

- Training output is a run/generation-scoped candidate artifact separate from the
  active model.
- Training success, candidate persistence, validation, compatibility, explicit
  promotion, active-model replacement, and Predict availability are distinct.
- Only the established artifact/model owner may explicitly promote a validated
  compatible candidate; stale candidates cannot be promoted and failure
  preserves the prior compatible model.
- Phase 4 owns artifact compatibility metadata and classification. Phase 5 owns
  candidate-result presentation and explicit promotion workflow.
- Atomic generation cutover is process-wide within one TrainShell composition.
  Standalone Predict independently detects persisted-generation mismatch at
  startup, prediction, explicit reload, and model-reload/promotion boundaries.
- A stale standalone process preserves existing rows/results for recovery but
  blocks new prediction when safe reload cannot succeed.
- One-hot final acceptance now follows static, mapping-backed, and external/
  provider source-mode mutation owners.

Phase 4 remains proposed. Automatic promotion/activation remains excluded. No
runtime, public API, schema, config, data, fixture, or model artifact changed.

# Evidence And Verification

- Current production training writes a run-scoped temporary artifact and then
  uses `os.replace` to overwrite the requested fixed model output path on
  completion; `TrainingResult` exposes that final model path rather than a
  candidate/promotion lifecycle.
- TrainShell embeds Predict in its process composition, while standalone
  `app_predict` constructs an independent Predict composition.
- Focused Markdown, ownership, stale-process, promotion, source-mode acceptance,
  staged-scope, and repository change-gate checks are performed before commit.

# Changed Files

- Active Phase 4/5 designs, governing direction, current planning, milestone log,
  result index, and active memory.
- No production source, configuration, schema, data, fixture, or model artifact.

# Known Risks

Phase 4A still must select the candidate store/promotion owner, metadata shape,
atomic replacement primitive, exact pre-promotion checks, standalone detection
mechanism, and stale-process recovery UX. Existing fixed-path behavior remains
unchanged until a later approved implementation.
