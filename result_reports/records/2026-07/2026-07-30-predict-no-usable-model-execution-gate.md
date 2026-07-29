record:
  date: 2026-07-30
  topic: predict-no-usable-model-execution-gate
  tags: predict, ui-ux, execution-gate, model-lifecycle, standalone, embedded
  memory_review: no-change
  memory_reason: Existing memory already records the controller execution boundary and preserved loaded-model lifecycle ownership.

# Change Reason

Predict enabled prediction execution while the current process had no usable
loaded model service. The worker then converted a known global capability
failure into repeated row-level runtime errors.

# Contract / Behavior Changed

`PredictionController` now owns execution eligibility from its current service
status, preserved lifecycle loaded identity, and running state. The workspace
projects that capability for standalone and embedded Predict without inspecting
the filesystem, Active reference, model path, or Train UI. Reload-required,
reload-failed, and Active-unavailable states remain executable when the prior
loaded model is preserved. A missing or failed startup capability blocks before
request preparation or worker creation, preserving row results.

# Evidence And Verification

- Independent-process focused Qt/controller suites: 68 passed.
- Adjacent lifecycle, generation, startup, and Train integration suites:
  41 passed with only existing joblib/NumPy deprecation warnings.
- Python compilation and `git diff --check`: passed.
- Structure guard: passed with warnings only. The changed
  `apps/predict/ui/workspace.py` remains above the existing 400 LOC soft limit;
  command-state projection is an existing workspace responsibility and the
  bounded helper does not justify a mechanical split in this slice.

# Changed Files

- Predict controller execution gate and workspace command-state projection.
- Lifecycle/reload and runtime-generation refresh hooks.
- Focused controller, lifecycle UI, workspace, standalone, and embedded tests.
- Active architecture and workstream status documents.

# Known Risks

- No production model, Active reference, user data, or deployment state was
  mutated.
- Native manual UI smoke was not required because enabled state, non-start, row
  preservation, lifecycle transitions, and both shell compositions are covered
  programmatically.
