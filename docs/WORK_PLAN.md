# Work Plan

## Purpose

- Own only the current slice, exact next action, blockers, constraints, holds,
  and short ordered follow-up.
- Keep phase/owner/milestone direction in `project_brief.md`, durable history in
  `project_log.md`, and point-in-time evidence in Result Records.
- Do not reconstruct completed implementation/audit/merge chronology here.

## Current Slice

**Windows Compatibility Stabilization** remains active and native acceptance may
now resume.

Native Windows already confirms runtime-generation recovery, clean-state Train
startup, and corrected Result Review alignment. PR #58 added saved-generation
Training Header Template / Definition Reference export, and PR #59 completed the
remaining Data Mapping onboarding path from strict legacy-wide CSV to a validated
Unsaved draft with explicit Save ownership.

The user-data onboarding prerequisite is therefore closed at source level. The
remaining gate is native Windows end-to-end source-runtime acceptance using the
supported onboarding workflow and real local training data.

## Exact Next Action

**Resume Native Windows 11 Enterprise source-runtime acceptance**

Use the newly completed onboarding workflow to prepare local inputs, then verify
Train through its existing lifecycle boundary:

1. export the saved-generation Training Header Template / Definition Reference;
2. bootstrap the user-selected legacy-wide Mapping CSV into a validated Unsaved
   Data Mapping draft, review/edit as needed, then explicitly Save local
   `mapping.json`;
3. prepare the real training CSV against the exported `ml_name` header contract;
4. run real Train execution through successful Candidate publication; and
5. continue Predict, Experiment, Calculator, and Deployment Export acceptance.

Previously confirmed native runtime-generation recovery, clean startup, and Result
Review alignment remain reusable unless later source changes invalidate those
specific contracts.

## Ordered Follow-ups

1. **Native Windows 11 Enterprise source-runtime acceptance** — exact next gate.
2. **Predict Case → Standard Predicted Points / Standard Request Product/Owner
   Decision** after native Windows source-runtime acceptance closes.
3. **Multi-point Predict → Calculate** remains behind that product decision.

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
