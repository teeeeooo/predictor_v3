# Train/Admin Phase 5C Training Result And Analysis

```yaml
record:
  date: 2026-07-25
  topic: train-admin-phase5c-training-result-analysis
  tags: train-admin, phase-5c, training-result, metrics, rfecv, optuna, xlsx, model-lifecycle
  memory_review: updated
  memory_reason: Phase 5C establishes the durable result/artifact contract and advances the workstream to independent L4 audit.
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

Phase 5B Candidate publication retained only a limited terminal summary and
could not support target-level quality review, fair baseline comparison, Feature
analysis, tuning review, preprocessing inspection, or artifact-completeness
decisions. Phase 5C needed one shared Qt-free result source without advancing
the Phase 5D UI, CLI, Campaign, or agent loop.

## Contract / Behavior Changed

- Core ML now returns versioned evaluation evidence for each canonical Target:
  R², MAE, RMSE, fold stability, RFECV state/rank, target-local XGBoost gain
  importance, Optuna trials/best parameters, preprocessing, and Feature data
  quality.
- The application layer builds `training_result.v1`, permits deltas only for
  identical training-data and evaluation contexts, and records Bootstrap or
  unavailable baseline reasons instead of manufacturing comparisons.
- New `model_candidate_manifest.v2` Candidates own hash-verified JSON, CSV, and
  consolidated XLSX analysis artifacts. Legacy v1 Candidates remain read-only
  and report analysis as unavailable; unknown future versions fail closed.
- Complete artifacts are verified before immutable Candidate publication.
  Partial, failed, cancelled, and artifact-generation-failed executions remain
  non-promotable and preserve structured immutable `run_evidence` without
  entering the Candidate namespace.
- Promotion eligibility is a snapshot only. It does not grant promotion,
  replace promotion-time compatibility checks, activate a Candidate, or define
  a new performance threshold. SHAP remains explicitly optional/not used.

## Evidence And Verification

Focused tests independently recompute known prediction metrics; verify
production Target identity association, fair/unfair baseline handling, partial
evidence, Optuna/RFECV/importance/preprocessing projections, JSON/CSV/XLSX
parity, artifact hashes, legacy/future-version behavior, and Active preservation
for success, cancellation, partial, and artifact failure. Phase 5B lifecycle,
promotion, migration, dependency-boundary, QProcess, and repository regression
tests remain included. Structure guard reports no new warning from this slice.

Final branch-wide and staged validation evidence is recorded in the PR and Git
history rather than copied into this record.

## Changed Files

- `core/ml/training.py` and `core/ml/training_results/`
- `apps/train/application/training_results/`
- `apps/train/adapters/training_results/`
- Train job, terminal contract, lifecycle, and Candidate publication owners
- common model-lifecycle Candidate contracts, validation, and repository
- focused Phase 5C and Phase 5B regression tests
- current work-plan, phase, log, index, and memory owners

## Known Risks

- Full production Optuna/RFECV training is intentionally not converted into a
  large validation matrix; focused numerical and lifecycle cases protect the
  contract while the independent L4 audit reviews the exact worker head.
- SHAP is unavailable/not used in this slice and is not an eligibility blocker.
- Phase 5D Train/Model UI, CLI, Campaign, leaderboard, agent loop, retention,
  deployment export, and packaging remain unstarted.
