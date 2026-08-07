# Work Plan

## Purpose

- Own only the current slice, exact next action, blockers, constraints, holds,
  and short ordered follow-up.
- Keep phase/owner/milestone direction in `project_brief.md`, durable history in
  `project_log.md`, and point-in-time evidence in Result Records.
- Do not reconstruct completed implementation/audit/merge chronology here.

## Current Slice

**Windows Compatibility Stabilization** remains active. Native Windows acceptance
is paused, not failed or cancelled, while the confirmed repair sequence is
completed.

PR #58 and PR #59 closed the Data Definition / Data Mapping onboarding source
prerequisite. Native Windows still preserves PASS evidence for affected runtime-
generation recovery, clean-state Train startup, and corrected Result Review
alignment unless later source changes materially invalidate those contracts.

The completed Native Windows Equivalent-Defect Repository Audit resolved the
three observed blockers and materially equivalent sibling gaps into four repair
slices:

1. **Data Mapping DRM-sensitive Legacy Bootstrap Acquisition — Lane B:** repair
   only user-selected legacy Mapping CSV acquisition by reusing the established
   Windows Excel automation / `xlwings` dependency direction. Existing parser,
   validation, Unsaved-draft, exchange/edit/import, and explicit-Save ownership
   remains unchanged. No additional DRM-sensitive production acquisition defect
   was found, and ordinary Train CSV reads are not part of this repair.
2. **Shared Train Child Structured-Event Encoding — Lane C:** repair the shared
   `train_job` producer contract used by both GUI `QProcessTrainingRunner` and
   headless/Experiment `SubprocessTrainingRunner`. The defect is a producer/
   consumer encoding-contract mismatch, not an emoji-content defect; preserve
   the structured event protocol and process lifecycle.
3. **Model Lifecycle Windows Handle Compatibility — Lane C:** repair the shared
   Windows handle/filesystem primitive used by Candidate publication/read,
   Active lifecycle mutation/read and writer-lock paths, closeout persistence,
   and Deployment Export file durability. Runtime Generation and Experiment
   persistence do not share this failure mechanism.
4. **Headless CLI JSON Output Encoding Compatibility — Lane C:** repair the
   separate versioned public CLI stdout contract. It is related to the encoding
   family but is not required to unblock real Train → Candidate publication; it
   must close before the dependent Experiment/headless acceptance surface closes.

The audit gives no reason to reopen Runtime Generation recovery or broaden this
slice into unrelated Windows cleanup. Native acceptance resumes at real Train
execution → Candidate publication after Slices 1-3 are closed; Slice 4 remains a
later acceptance prerequisite only for its dependent headless/Experiment surface.

## Exact Next Action

**Data Mapping DRM-sensitive Legacy Bootstrap Acquisition Repair — Lane B**

Repair only DRM-sensitive user-selected legacy Mapping CSV acquisition by reusing
the existing Windows Excel automation / `xlwings` dependency direction. Feed the
acquired legacy-wide data into the existing parser/validation flow as a validated
Unsaved Data Mapping draft, preserving review/exchange/edit/import and explicit
Save as the only publication owner for local `mapping.json`.

Do not broaden this repair to ordinary Train CSV or general CSV acquisition, do
not change parser/validation semantics, and do not implement any later Windows
repair slice in the same branch.

## Ordered Follow-ups

1. **Slice 1 — Data Mapping DRM-sensitive Legacy Bootstrap Acquisition** — Lane B,
   exact next repair gate.
2. **Slice 2 — Shared Train Child Structured-Event Encoding** — Lane C, after
   Slice 1 closes.
3. **Slice 3 — Model Lifecycle Windows Handle Compatibility** — Lane C, after
   Slice 2 closes.
4. **Resume Native Windows acceptance** at real Train execution → Candidate
   publication after Slices 1-3 close.
5. **Slice 4 — Headless CLI JSON Output Encoding Compatibility** — Lane C; finish
   before closing the dependent Experiment/headless acceptance surface, but do
   not treat it as a prerequisite for Candidate publication.
6. **Continue Native Windows application acceptance** across Predict / Experiment /
   Calculator / Deployment Export as applicable after each blocking repair is
   closed.
7. **Predict Case → Standard Predicted Points / Standard Request Product/Owner
   Decision** after Native Windows source-runtime acceptance closes.
8. **Multi-point Predict → Calculate** remains behind that product decision.

This is a sequential repair/acceptance plan, not authorization to create all four
repair branches concurrently.

## Active Constraints

- Data Definition / canonical runtime generation remains the Feature/Target and
  Train contract owner. The Training Header Template is saved-generation truth,
  not a second editable schema.
- Train-required raw headers are the current generation's active `ml_name`
  contract.
- Data Mapping owns concrete `mapping.json` values. Legacy-wide conversion remains
  bootstrap-only; normal round-trip editing remains `mapping_bundle_v1`, and only
  explicit Save publishes runtime Mapping state.
- Preserve Data Mapping draft/review/exchange/import/Save ownership and existing
  runtime-generation/persistence behavior.
- Keep `config/ml/features.csv` as a compatibility projection. The remaining
  static fingerprint seam is observed but is not a demonstrated blocker to
  generation-bound Train/Candidate publication and is not authorized for mutation
  by native acceptance.
- Native Windows evidence remains external/manual evidence. Reuse prior PASS only
  while the relevant source/runtime contracts remain uninvalidated.
- Do not commit or infer company-local mapping values, training data, or model
  quality evidence.

## Holds

- **Standard Request Product/Owner Decision** remains held until Native Windows
  source-runtime acceptance closes.
- **Multi-point Predict → Calculate** remains held behind that product decision;
  Predict does not copy Calculator formulas or replace Calculator ownership.
- **Result Review XLSX** source implementation remains `DEFER` until a concrete
  workbook-specific requirement justifies reopening it.
- Frozen/PyInstaller Train child execution, Windows reserved-name/long-path
  packaging concerns, DLL/runtime packaging, production promotion, migration
  apply, and retention/delete apply remain separately authorized work.

## Minimal Anchors

- Product/phase map: `project_brief.md`
- Train/Predict architecture: `docs/architecture/pyside6_train_predict_architecture.md`
- Train/Admin canonical owner direction:
  `docs/designs/2026-07-17-train-admin-phase-4-unified-feature-manager.md`
- Data Mapping onboarding boundary:
  `docs/designs/2026-07-14-train-admin-phase-2-data-mapping-ux-overhaul.md`
- ML training-header compatibility:
  `docs/workflows/ml_feature_catalog_workflow.md`
- Native acceptance evidence discovery: `result_reports/REPORT_INDEX.md`
