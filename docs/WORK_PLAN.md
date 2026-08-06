# Work Plan

## Purpose

- Own only the current slice, exact next action, blockers, constraints, holds,
  and short ordered follow-up.
- Keep phase/owner/milestone direction in `project_brief.md`, durable history in
  `project_log.md`, and point-in-time evidence in Result Records.
- Do not reconstruct completed implementation/audit/merge chronology here.

## Current Slice

**Windows Compatibility Stabilization** remains active. The independently audited
source repairs through PR #56 are closed, and Native Windows 11 Enterprise
source-runtime acceptance has resumed.

That acceptance exposed two Predict Result Review defects and two Train/Admin
onboarding gaps. The defects are handled before acceptance continues; onboarding
follows acceptance as a separate bounded workstream.

## Exact Next Action

**Predict Result Review bounded repair**

Repair only the current Result Review presentation/error paths needed for:

1. narrow/pinned Result Review alignment: the `Case + 상태` anchor and the
   right-side result table must keep horizontal headers and the first data row
   vertically aligned; and
2. unavailable cooling/heating `ReviewSourceValue` tooltip handling: do not assume
   a generic outcome owns `reason_code/message` when that source value shape does
   not, and eliminate the resulting `AttributeError`.

Preserve the canonical Result Review session/projection, pinned-column ownership,
raw source/provenance evidence, copy/CSV behavior, typed Target outcomes, and
existing stale/unavailable semantics.

## Ordered Follow-ups

1. **Predict Result Review bounded repair** — exact next source gate.
2. **Exact-head Gate / merge / Close** for that repair.
3. **Resume Native Windows 11 Enterprise source-runtime acceptance**:
   - inspect/recover the previously affected runtime-generation state first when
     it is still available;
   - then exercise clean-state Train, Predict, Experiment, Calculator, and
     Deployment Export;
   - Train must complete real training through Candidate publication, not merely
     launch or reach pre-training state.
4. **Data Definition / Data Mapping onboarding workstream**:
   - expose the current generation's actual Train-required `ml_name` headers as a
     user-facing Training Header Template/reference workflow;
   - when `data/mapping.json` is missing, bootstrap the legacy wide mapping source
     only into a validated **unsaved** Data Mapping draft, then use explicit
     review/export/import/Save workflow to create the local runtime mapping;
   - keep `config/ml/features.csv` as a compatibility projection rather than the
     canonical user-owned definition surface;
   - audit remaining static compatibility dependencies before authorizing source
     mutation that would retire or redirect them.

## Active Constraints

- Data Definition / canonical runtime generation remains the Feature/Target and
  Train contract owner. Generated/static projections do not become independent
  writable SSOTs.
- Data Mapping owns concrete `mapping.json` values. Legacy-wide conversion remains
  bootstrap-only; normal Data Mapping exchange/import behavior is not replaced by
  a second permanent wide-CSV contract.
- Predict remains a consumer of saved Data Definition, Mapping, compatible model,
  and canonical session contracts; Result Review repair must not move domain or
  persistence ownership into UI code.
- Preserve full Active Target compatibility, Case-scoped requested Target
  applicability, execution provenance, row isolation, cancellation, partial
  results, EER/COP applicability, generation migration, and no-hot-swap behavior.
- Windows automated repair evidence remains macOS-owned. Native Windows 11
  Enterprise execution is external/manual acceptance evidence and must remain
  `NOT RUN`/`NOT AVAILABLE` when not actually executed.
- Use repository fixtures/mock data only for repository validation. Do not mutate
  production mapping, training data, models, Active state, promotion state, or
  retention/migration state as part of these planning/source slices.

## Holds

- **Predict Case → Standard Predicted Points / Standard Request Product/Owner
  Decision** remains held until Native Windows source-runtime acceptance closes.
- **Multi-point Predict → Calculate** remains held behind that product decision;
  Predict does not copy Calculator formulas or replace Calculator ownership.
- **Result Review XLSX** source implementation remains `DEFER` until a concrete
  workbook-specific requirement justifies reopening it.
- Frozen/PyInstaller Train child execution, Windows reserved-name/long-path
  packaging concerns, DLL/runtime packaging, production promotion, migration
  apply, and retention/delete apply remain separately authorized work.

## Minimal Anchors

- Product/phase map: `project_brief.md`
- Predict architecture: `docs/architecture/pyside6_train_predict_architecture.md`
- Train/Admin canonical owner direction:
  `docs/designs/2026-07-17-train-admin-phase-4-unified-feature-manager.md`
- Data Mapping bootstrap boundary:
  `docs/designs/2026-07-14-train-admin-phase-1-mapping-data-foundation.md`
- ML training-header compatibility:
  `docs/workflows/ml_feature_catalog_workflow.md`
- Result Review evidence discovery: `result_reports/REPORT_INDEX.md`
