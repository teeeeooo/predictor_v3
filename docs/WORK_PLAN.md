# Work Plan

## Purpose

- Own only the current slice, exact next action, blockers, constraints, holds,
  and short ordered follow-up.
- Keep phase/owner/milestone direction in `project_brief.md`, durable history in
  `project_log.md`, and point-in-time evidence in Result Records.
- Do not reconstruct completed implementation/audit/merge chronology here.

## Current Slice

**Native Windows source-runtime acceptance** is active again. The source blockers
required before real Train → Candidate publication are closed through PR #62;
Windows Compatibility Stabilization remains only for later surface-specific work
that is not a Candidate-publication prerequisite.

PR #58 and PR #59 closed the Data Definition / Data Mapping onboarding source
prerequisite, PR #60 closed the DRM-sensitive legacy Mapping acquisition repair,
PR #61 closed the shared Train child structured-event UTF-8 transport repair, and
PR #62 closed the shared Model Lifecycle Windows handle compatibility repair.
Native Windows still preserves PASS evidence for affected runtime-generation
recovery, clean-state Train startup, and corrected Result Review alignment unless
later source changes materially invalidate those contracts.

The completed Native Windows Equivalent-Defect Repository Audit resolved the
three observed blockers and materially equivalent sibling gaps into four repair
slices:

1. **Data Mapping DRM-sensitive Legacy Bootstrap Acquisition — Lane B: closed.**
   Windows production now uses the established Excel automation / `xlwings`
   direction for this bootstrap-only acquisition while strict parsing, validation,
   Unsaved-draft, exchange/edit/import, and explicit-Save ownership remain intact.
   Native protected-file smoke remains external acceptance evidence.
2. **Shared Train Child Structured-Event Encoding — Lane C: closed.**
   PR #61 makes the shared child stdin/stdout/stderr UTF-8 before protocol
   activity while preserving both existing consumers, structured event meanings,
   confirmation transport, and process lifecycle.
3. **Model Lifecycle Windows Handle Compatibility — Lane C: closed.**
   PR #62 repairs the shared native Windows handle access-mode primitive used by
   Candidate publication/read, Active lifecycle mutation/read and writer-lock
   paths, closeout persistence, and Deployment Export file durability without
   changing lifecycle/publication identity or persistence contracts.
4. **Headless CLI JSON Output Encoding Compatibility — Lane C:** repair the
   separate versioned public CLI stdout contract. It is related to the encoding
   family but is not required to unblock real Train → Candidate publication; it
   must close before the dependent Experiment/headless acceptance surface closes.

The audit gives no reason to reopen Runtime Generation recovery or broaden this
slice into unrelated Windows cleanup. Native acceptance resumes at real Train
execution → Candidate publication after Slices 1-3 are closed; Slice 4 remains a
later acceptance prerequisite only for its dependent headless/Experiment surface.

## Exact Next Action

**Resume Native Windows source-runtime acceptance — real Train execution → Candidate publication**

Run the real Train workflow on native Windows through successful Candidate
publication. Reuse the already accepted Runtime Generation recovery, clean Train
startup, and Result Review alignment evidence unless new evidence materially
invalidates those contracts; do not repeat them merely because Slice 3 closed.

Do not route to Slice 4 before this Candidate-publication acceptance step.

## Ordered Follow-ups

1. **Resume Native Windows acceptance** at real Train execution → Candidate
   publication, now that Slices 1-3 are closed.
2. **Slice 4 — Headless CLI JSON Output Encoding Compatibility** — Lane C; finish
   before closing the dependent Experiment/headless acceptance surface, but do
   not treat it as a prerequisite for Candidate publication.
3. **Continue Native Windows application acceptance** across Predict / Experiment /
   Calculator / Deployment Export as applicable after each blocking repair is
   closed.
4. **Predict Case → Standard Predicted Points / Standard Request Product/Owner
   Decision** after Native Windows source-runtime acceptance closes.
5. **Multi-point Predict → Calculate** remains behind that product decision.

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
