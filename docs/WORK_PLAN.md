# Work Plan

## Purpose

- Own only the current slice, exact next action, blockers, constraints, holds,
  and short ordered follow-up.
- Keep phase/owner/milestone direction in `project_brief.md`, durable history in
  `project_log.md`, and point-in-time evidence in Result Records.
- Do not reconstruct completed implementation/audit/merge chronology here.

## Current Slice

**Windows Compatibility Stabilization** remains active, with native acceptance
paused on the remaining user-data onboarding prerequisite rather than a Windows
runtime defect.

Native Windows already confirms runtime-generation recovery, clean-state Train
startup, and corrected Result Review alignment. PR #58 now closes the Data
Definition side of onboarding by exposing the exact saved-generation Train header
contract and a spreadsheet-safe Definition reference export.

Full Train acceptance still cannot proceed through real training/Candidate
publication until the local Data Mapping bootstrap path is available.

## Exact Next Action

**Data Mapping Legacy Bootstrap Onboarding**

Complete the remaining Mapping onboarding needed to prepare real local training
inputs:

1. when `data/mapping.json` is absent, allow the existing strict legacy-wide
   mapping parser to create only a validated **unsaved** Data Mapping draft;
2. keep the bootstrap explicitly user-initiated and distinguish it from the
   normal Mapping exchange/import contract;
3. preserve the existing review/exchange/import/Save flow so the user can replace
   bootstrap values with real local values before explicitly creating
   `data/mapping.json`;
4. fail closed on invalid/conflicting legacy data without partially mutating the
   current Data Mapping draft or runtime mapping state; and
5. do not auto-install repository fixture data or make the legacy-wide CSV a new
   permanent writable SSOT.

The PR #58 Training Header Template remains the saved-generation `ml_name` truth
for preparing the training CSV. Its inspection found the remaining static
`config/ml/features.csv` fingerprint seam but no demonstrated blocker to current
generation training/Candidate publication, so no catalog mutation is authorized
by this workstream.

## Ordered Follow-ups

1. **Data Mapping Legacy Bootstrap Onboarding** — exact next source gate.
2. **Resume Native Windows 11 Enterprise source-runtime acceptance**:
   - use the Training Header Template and locally prepared Mapping to run real
     Train execution through Candidate publication;
   - continue Predict, Experiment, Calculator, and Deployment Export acceptance;
   - reuse the already confirmed native runtime-generation recovery, clean startup,
     and Result Review alignment evidence unless later source changes invalidate it.
3. **Predict Case → Standard Predicted Points / Standard Request Product/Owner
   Decision** after native Windows source-runtime acceptance closes.
4. **Multi-point Predict → Calculate** remains behind that product decision.

## Active Constraints

- Data Definition / canonical runtime generation remains the Feature/Target and
  Train contract owner. PR #58 exports saved-generation truth only; generated or
  static projections do not become independent writable SSOTs.
- Train-required raw headers are the current generation's active `ml_name`
  contract and are now user-exportable without changing Train validation.
- Data Mapping owns concrete `mapping.json` values. Legacy-wide conversion remains
  bootstrap-only and must not become a permanent general import contract or
  silently auto-write runtime Mapping state.
- Preserve Data Mapping draft/review/exchange/import/Save ownership and existing
  runtime-generation/persistence behavior.
- Keep `config/ml/features.csv` as a compatibility projection. The remaining
  static fingerprint seam is observed but is not a demonstrated onboarding
  blocker and is not authorized for mutation in the Mapping slice.
- Native Windows evidence remains external/manual evidence. Already confirmed
  native checks may be reused only while their relevant source/runtime contracts
  remain uninvalidated.
- Use repository fixtures/mock data for repository validation; do not commit or
  infer company-local mapping values, training data, or model quality evidence.

## Holds

- Native Windows acceptance is **paused, not failed or cancelled**, pending the
  remaining Mapping onboarding source prerequisite.
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
- Data Mapping bootstrap boundary:
  `docs/designs/2026-07-14-train-admin-phase-1-mapping-data-foundation.md`
- ML training-header compatibility:
  `docs/workflows/ml_feature_catalog_workflow.md`
- Native acceptance evidence discovery: `result_reports/REPORT_INDEX.md`
