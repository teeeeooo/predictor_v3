# Work Plan

## Purpose

- Own only the current slice, exact next action, blockers, constraints, holds,
  and short ordered follow-up.
- Keep phase/owner/milestone direction in `project_brief.md`, durable chronology in `project_log.md`, reusable rationale in focused decision/failure records, and older point-in-time evidence in historical Result Records.
- Do not reconstruct completed implementation/audit/merge chronology here.

## Current Slice

**Calculator combination calculation — implemented across all current
standard/profile/product paths.** The [governing specification](designs/2026-10-16-calculator-combination-search.md)
now has a toolkit-free runner and shared modeless Tk dialog, 10,000-case service
limit, pinned detail/CSV provenance, and separate stale/partial states. Automated
macOS Tk integration covers the actual section actions and all 22 baseline
contexts. The candidate-column revision and ISO screenshot review are complete.
Native OS keyboard, Windows/Linux and multi-monitor/DPI acceptance remain unverified; these do not reopen the separate Predict hold.

**Native Windows source-runtime acceptance** is active again. The complete
pre-acceptance Windows repair set is closed: PR #58/#59 closed the Data Definition
/ Data Mapping onboarding prerequisite, PR #60 closed DRM-sensitive legacy Mapping
acquisition, PR #61 closed shared Train child structured-event UTF-8 transport,
PR #62 closed shared Model Lifecycle Windows handle compatibility, and PR #63
closed the separate versioned Experiment/headless JSON stdout encoding gap.

No known Windows source-repair gate remains. Previously accepted native evidence
for affected runtime-generation recovery, clean-state Train startup, and corrected
Result Review alignment remains reusable unless a later source change materially
invalidates the same owner or contract. Native protected Mapping acquisition and
all still-unexecuted application paths remain acceptance evidence, not new source
work by default.

## Exact Next Action

**Calculator follow-up — native platform acceptance only when scheduled.**
Specification §6.1 is implemented: vertically stacked point blocks contain
Capacity/Power rows and independent candidate columns. Main integration review
corrected result/CSV candidate identification by pinning each original column
number before exclusions. Verification passed 65 feature/application-boundary
tests and 4 native Tk integration tests, plus a fresh ISO 3×5 completion screenshot.
The earlier 170 shared UI regression tests remain applicable. Calculation formulas
and public result contracts remain unchanged. See the specification for remaining
platform limits.

**Resume Native Windows source-runtime acceptance — one continuous acceptance pass**

Continue from the first still-required native acceptance point rather than
repeating uninvalidated PASS evidence. Do not create another Windows repair or
audit gate unless new native acceptance evidence demonstrates a concrete defect.

## Ordered Follow-ups

The Calculator combination implementation is complete. The independent
Windows/Predict sequence remains:

1. **Native Windows continuous source-runtime acceptance**, in this order:
   1. protected DRM-sensitive legacy Mapping bootstrap confirmation as needed;
   2. real Train execution through successful Candidate publication;
   3. Predict;
   4. Experiment, including the headless CLI;
   5. Calculator;
   6. Deployment Export.
   Reuse prior PASS evidence for Runtime Generation recovery, clean Train startup,
   and Result Review alignment while those contracts remain uninvalidated.
2. **Predict Case → Standard Predicted Points / Standard Request Product/Owner
   Decision** after Native Windows source-runtime acceptance closes.
3. **Multi-point Predict → Calculate** remains behind that product decision.

The completed repair set does not authorize another repository-wide Windows audit,
generic compatibility cleanup, or speculative repair slice absent new acceptance
evidence.

## Active Constraints

- Calculator combinations reuse existing standard application owners and the
  capability gateway. Preserve formulas, configs, public contracts, and goldens;
  enforce the 10,000 limit in the service as well as the UI. Native UI and Windows
  acceptance remain distinct from exploratory headless calculation evidence.
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

- Calculator combination specification and implementation evidence:
  `docs/designs/2026-10-16-calculator-combination-search.md`
- Product/phase map: `project_brief.md`
- Train/Predict architecture: `docs/architecture/pyside6_train_predict_architecture.md`
- Train/Admin canonical owner direction:
  `docs/designs/2026-07-17-train-admin-phase-4-unified-feature-manager.md`
- Data Mapping onboarding boundary:
  `docs/designs/2026-07-14-train-admin-phase-2-data-mapping-ux-overhaul.md`
- ML training-header compatibility:
  `docs/workflows/ml_feature_catalog_workflow.md`
- Native acceptance evidence discovery: `result_reports/REPORT_INDEX.md`
