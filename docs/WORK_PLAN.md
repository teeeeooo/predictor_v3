# Work Plan

## Purpose

- Own only the current slice, exact next action, blockers, constraints, holds,
  and short ordered follow-up.
- Keep phase/owner/milestone direction in `project_brief.md`, durable history in
  `project_log.md`, and point-in-time evidence in Result Records.
- Do not reconstruct completed implementation/audit/merge chronology here.

## Current Slice

**Windows Compatibility Stabilization** remains active. Native Windows acceptance
is paused, not failed or cancelled, until newly confirmed source-runtime blockers
and the repository-wide equivalent-pattern audit are closed.

PR #58 and PR #59 closed the Data Definition / Data Mapping onboarding source
prerequisite. Native Windows still preserves PASS evidence for affected runtime-
generation recovery, clean-state Train startup, and corrected Result Review
alignment unless later source changes materially invalidate those contracts.

Acceptance resumed far enough into the real user workflow to confirm three new
Windows blockers:

1. **Data Mapping Legacy Bootstrap — DRM-sensitive CSV acquisition:** the user
   legacy Mapping CSV is not accessible through the ordinary direct file-read
   path in the DRM environment, while native evidence shows access through
   Windows Excel automation / `xlwings`. Existing dependency policy already
   directs DRM-sensitive user Excel reads through that Windows automation path;
   this plan does not preselect the concrete adapter repair.
2. **Train child-process status/log encoding:** real Train execution exposed a
   `cp949` encoding failure in training status/event output. The child-job text/
   event transport and Windows console/stdout encoding boundary are materially
   involved; this plan does not choose emoji removal, encoding coercion, or a
   transport repair.
3. **Model Lifecycle Windows handle compatibility:** native Windows fails on an
   `os.O_ACCMODE` availability assumption in the lifecycle file-handle path.
   Candidate/Active and materially adjacent persistence/publication safety paths
   must be inspected before fixing an isolated call site.

Real Train execution through Candidate publication, followed by Predict,
Experiment, Calculator, and Deployment Export acceptance, resumes only after the
confirmed repairs are selected from audit evidence and completed.

## Exact Next Action

**Native Windows Equivalent-Defect Repository Audit — read-only**

Audit the repository for materially equivalent Windows patterns before any
source repair:

- DRM-sensitive user-file acquisition that still bypasses the established
  Windows Excel-automation dependency direction through direct filesystem/parser
  reads;
- locale-dependent encoding assumptions at child process, subprocess, QProcess,
  CLI, protocol, stdout/stderr, or other text/event transport boundaries; and
- POSIX-only or platform-dependent `os` flags/constants/file-descriptor semantics
  used by Windows persistence/publication paths.

The audit must distinguish confirmed defects from merely similar patterns,
identify the affected owners and dependency direction, determine which findings
can safely share a repair slice versus require independent owners, and produce
evidence for the appropriate lane and validation purpose of each follow-up.
It must not mutate source, tests, dependencies, or runtime state.

## Ordered Follow-ups

1. **Native Windows Equivalent-Defect Repository Audit** — exact next gate,
   read-only.
2. **Confirmed Windows repair slice(s)** — owner/lane/order selected only after
   Orchestrator review of the audit evidence.
3. **Resume Native Windows acceptance** at real Train execution → Candidate
   publication → Predict / Experiment / Calculator / Deployment Export.
4. **Predict Case → Standard Predicted Points / Standard Request Product/Owner
   Decision** after native Windows source-runtime acceptance closes.
5. **Multi-point Predict → Calculate** remains behind that product decision.

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
