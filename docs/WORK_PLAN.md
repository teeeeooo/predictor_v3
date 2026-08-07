# Work Plan

## Purpose

- Own only the current slice, exact next action, blockers, constraints, holds,
  and short ordered follow-up.
- Keep phase/owner/milestone direction in `project_brief.md`, durable history in
  `project_log.md`, and point-in-time evidence in Result Records.
- Do not reconstruct completed implementation/audit/merge chronology here.

## Current Slice

**Windows Compatibility Stabilization** remains active for one final already-audited
source repair before Native Windows source-runtime acceptance resumes. Slices 1–3
are closed; Native Windows acceptance is paused, not failed or cancelled, until
Slice 4 closes so the known repair set can be completed before one continuous
acceptance pass.

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
4. **Headless CLI JSON Output Encoding Compatibility — Lane C: open.** Repair the
   separate versioned machine-readable Experiment/headless CLI stdout contract.
   It remains distinct from the internal Train child-process protocol repaired by
   Slice 2.

The audit gives no reason to reopen Runtime Generation recovery, Slices 1–3, or
unrelated Windows cleanup. Because Slice 4 is already a confirmed compatibility
gap on a later acceptance surface, close it before resuming Native Windows
acceptance rather than intentionally interrupting that acceptance for a known
source repair.

## Exact Next Action

**Slice 4 — Headless CLI JSON Output Encoding Compatibility Repair — Lane C**

Repair the separate versioned machine-readable Experiment/headless CLI stdout
contract without reopening the internal Train child protocol or broadening into
generic console/encoding cleanup. After Slice 4 merge/Close, resume Native Windows
source-runtime acceptance as one continuous pass.

## Ordered Follow-ups

1. **Slice 4 — Headless CLI JSON Output Encoding Compatibility Repair** — Lane C,
   the sole exact next source repair.
2. **Resume Native Windows source-runtime acceptance** after Slice 4 closes and
   progress continuously through:
   1. real protected DRM-sensitive legacy Mapping bootstrap confirmation as needed;
   2. real Train execution through successful Candidate publication;
   3. Predict;
   4. Experiment, including the dependent headless CLI surface;
   5. Calculator;
   6. Deployment Export.
   Reuse prior PASS evidence for Runtime Generation recovery, clean Train startup,
   and Result Review alignment unless a later source change materially invalidates
   the relevant owner or contract.
3. **Predict Case → Standard Predicted Points / Standard Request Product/Owner
   Decision** after Native Windows source-runtime acceptance closes.
4. **Multi-point Predict → Calculate** remains behind that product decision.

This sequencing change completes the already-audited repair set before acceptance;
it does not authorize another repository-wide audit, generic Windows cleanup, or
new repair slices.

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
