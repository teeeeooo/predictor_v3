# 493 PySide6 Train/Predict Doc Alignment

## Goal

Align project documentation with the approved PySide6 Train/Predict rewrite
decision and make the new design gate/spec discoverable without starting
implementation.

## Scope

- Docs-only alignment.
- No production code, tests, fixtures, golden data, model artifacts, dependency
  files, or legacy PyQt5 file moves/deletions.
- New design documents were treated as the local owner for this decision and
  only minimally linked from existing active docs.

## Changed Files

- `PROJECT_CHARTER.md`
- `project_brief.md`
- `docs/WORK_PLAN.md`
- `docs/architecture/project_architecture.md`
- `docs/agent_workflows/ML_PREDICTOR_WORKFLOW.md`
- `docs/ui_ux/01_TOOLKIT_SELECTION_POLICY.md`
- `docs/designs/README.md`
- `docs/designs/2026-06-27-pyside6-train-predict-rewrite-design-gate.md`
- `docs/designs/2026-06-27-pyside6-train-predict-ui-implementation-spec.md`
- `result_reports/active/493_pyside6-train-predict-doc-alignment.md`

## Changes

- Registered the PySide6 Train/Predict design gate and implementation spec in
  `docs/designs/README.md`.
- Updated charter, brief, architecture, ML workflow, and toolkit policy wording
  so Train/Predict is a PySide6 rewrite, not a PyQt5 migration or deferred
  placeholder path.
- Kept legacy `ui/` PyQt5 Train/Predict files as reference-only until a later
  retirement slice, rather than implying immediate deletion.
- Updated `docs/WORK_PLAN.md` so the next action can proceed to PySide6
  Train/Predict rewrite implementation preflight and then the skeleton slice.
- Linked `predict_ref_img.png` and `train_ref_img.png` as non-binding visual
  references; they are layout references, not pixel-perfect requirements.

## Verification

- `git diff --check` - passed.
- `git status --short` - checked modified tracked docs plus untracked new
  design docs/assets/report.
- Targeted stale-wording search - checked PyQt5/PySide6/app boundary terms.
  Remaining PyQt5 hits are archive/history, current source-map evidence,
  legacy/reference-only wording, or active PyQt5 adapter docs with an explicit
  project-specific PySide6 exception.
- Visual reference asset existence - checked `predict_ref_img.png` and
  `train_ref_img.png`.

Skipped:

- pytest: docs-only alignment.
- GUI smoke: no implementation or launch work.
- packaging check: no dependency or packaging changes.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: not_required
  ui_literal_exemption: none
  reuse_commonization: not_required
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `ACTIVE_DOCUMENTS.md`: active document inventory and design-record indexing
  rule.
- `docs/agent_workflows/DOCUMENT_SYNC_AND_LIFECYCLE.md`: docs sync and design
  record index update rule.
- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`: compact report rules.
- `docs/designs/README.md`: design record index owner.
- new PySide6 design gate/spec: decision, implementation slices, and visual
  reference placement.
- targeted `rg` search across active docs for PyQt5/PySide6/app boundary stale
  wording.

## Memory Seed

Not updated. This is ordinary docs alignment; summary-level memory sync can be
considered later after a PySide6 preflight or skeleton summary closes a durable
implementation decision.

## Known Risks

- The new design docs and visual assets were present as untracked files at task
  start; this alignment links them but does not implement or validate PySide6
  runtime behavior.
- PySide6 dependency installation and import smoke belong to the implementation
  preflight/skeleton slice, not this docs-only task.

## Next Action

Run PySide6 Train/Predict rewrite implementation preflight, then start the
PySide6 package skeleton slice if the boundary and verification plan are still
accepted.
