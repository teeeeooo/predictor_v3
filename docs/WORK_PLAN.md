# Work Plan

## Purpose

- Own only the current slice, exact next action, blockers, constraints, holds,
  and short ordered follow-up.
- Keep phase/owner/milestone direction in `project_brief.md`, durable history in
  `project_log.md`, and point-in-time evidence in Result Records.
- Do not reconstruct completed implementation/audit/merge chronology here.

## Current Slice

**Windows Compatibility Stabilization** remains active, but native acceptance is
currently paused on a user-data onboarding prerequisite rather than a Windows
runtime defect.

Native Windows 11 Enterprise evidence now confirms the previously affected
runtime-generation state recovers successfully, clean-state Train startup succeeds,
and the PR #57 Result Review pinned-table alignment renders correctly. Full Train
acceptance cannot continue through real training/Candidate publication until the
user can prepare training headers and local Mapping through supported product flows.

## Exact Next Action

**Data Definition / Data Mapping onboarding workstream**

Close the user-data preparation gap needed to resume native Train acceptance:

1. expose the current generation's exact Train-required `ml_name` headers as a
   user-facing Training Header Template/reference export;
2. provide enough Definition reference information to map those headers back to
   current Feature meaning without making generated compatibility projections
   writable SSOTs;
3. when `data/mapping.json` is absent, allow the legacy wide mapping source to
   bootstrap only a validated **unsaved** Data Mapping draft;
4. preserve the existing review/exchange/import/Save path so the user can enter
   real local Mapping values and explicitly create the local runtime mapping; and
5. audit the remaining `config/ml/features.csv` static compatibility dependencies
   before any source mutation that retires or redirects that projection.

## Ordered Follow-ups

1. **Data Definition / Data Mapping onboarding** — exact next source gate.
2. **Resume Native Windows 11 Enterprise source-runtime acceptance**:
   - perform real Train execution through Candidate publication using prepared
     user data;
   - continue Predict, Experiment, Calculator, and Deployment Export acceptance;
   - reuse the already confirmed native runtime-generation recovery, clean startup,
     and Result Review alignment evidence unless later source changes invalidate it.
3. **Predict Case → Standard Predicted Points / Standard Request Product/Owner
   Decision** after native Windows source-runtime acceptance closes.
4. **Multi-point Predict → Calculate** remains behind that product decision.

## Active Constraints

- Data Definition / canonical runtime generation remains the Feature/Target and
  Train contract owner. Generated/static projections do not become independent
  writable SSOTs.
- Train-required raw headers are the current generation's active `ml_name`
  contract; onboarding must expose that contract rather than invent a second
  training-header schema.
- Data Mapping owns concrete `mapping.json` values. Legacy-wide conversion remains
  bootstrap-only and must not become a permanent general import contract or
  silently auto-write runtime Mapping state.
- Preserve Data Mapping draft/review/exchange/import/Save ownership and existing
  runtime-generation/persistence behavior.
- Keep `config/ml/features.csv` as a compatibility projection unless a bounded
  owner audit proves its remaining static dependency can be safely retired or
  redirected.
- Native Windows evidence remains external/manual evidence. Already confirmed
  native checks may be reused only while their relevant source/runtime contracts
  remain uninvalidated.
- Use repository fixtures/mock data for repository validation; do not commit or
  infer company-local mapping values, training data, or model quality evidence.

## Holds

- Native Windows acceptance is **paused, not failed or cancelled**, pending the
  onboarding source prerequisite above.
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
