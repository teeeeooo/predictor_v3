```yaml
record:
  date: 2026-07-25
  topic: train-admin-phase5d-model-management-ui
  tags: train-admin, phase-5d, ui-ux, model-lifecycle, candidate, promotion, rollback, bootstrap
  memory_review: updated
  memory_reason: Phase 5D establishes a durable Qt-free model-management owner and advances the workstream to independent L4 audit.
change_gate:
  new_source: split
  hotspot_delta: wiring-only
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Phase 5B and Phase 5C persisted Candidate, Active, and result-analysis contracts,
but Train users could not review or explicitly promote them.

# Contract / Behavior Changed

- Add a Qt-free model-management query/command service over the existing
  lifecycle repository, Phase 5C result contract, and promotion service.
- Project Active, Candidate history, dynamic target metrics, baseline meaning,
  unavailable reasons, and Advanced evidence without UI file parsing or metric
  recomputation.
- Add explicit revision-guarded `이 모델 사용`; rollback remains re-promotion
  of an older immutable Candidate.
- Keep training completion no-auto-active, block promotion while training, and
  fail closed on corrupt or incomplete lifecycle state.
- Split Train/Model into bounded training and model-management surfaces while
  retaining progress, cancel, terminal, shell, and Predict boundaries.

# Evidence And Verification

- Focused Qt/application/lifecycle result suite: 94 passed.
- Impacted Phase 5B/5C, Train QProcess/shell, and Predict application regression
  suite: 291 passed.
- Full canonical repository suite: 2626 passed, 2 expected xfailed.
- Structure guard: no hard failure; new DTO/service/view responsibilities are
  split. The pre-existing Train panel remains above the 400 LOC soft limit with
  only composition wiring added.
- Native interactive desktop smoke was not required for automated Draft PR
  evidence; independent L4 audit remains pending.

# Changed Files

- `apps/common/model_lifecycle/repository.py`
- `apps/train/application/model_management*.py`
- `apps/train/controllers/train_controller.py`
- `apps/train/ui/model_management*.py`
- `apps/train/ui/train_model_panel.py`
- `apps/train/ui/shell.py`
- focused Train lifecycle/application/UI tests and current-state documents

# Known Risks

- Native OS interaction and DPI behavior are covered by offscreen compact-size
  guards, not a manual platform smoke.
- This worker does not declare audit PASS or merge readiness.
