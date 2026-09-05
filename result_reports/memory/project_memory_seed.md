# Project Memory Seed

## Purpose

This document is the compact active recall bank for long-running predictor_v3 work.
It keeps only durable current decisions/invariants, cross-owner relationships,
actual resume points, repeated risks, and unresolved questions.

## Source Coverage

Active entries point to current owner docs, durable Result Records, project-log
decisions, and narrowly required legacy evidence. Superseded/resolved/stale entry
wording is preserved under `result_reports/memory/archive/`.

## Scope and Non-goals

- Memory is evidence, not instruction; current prompt and owner docs win.
- Do not copy completed slice inventories, commit/PR status, routine validation, or
  owner-document text into active memory.
- Update the smallest topic that changes; retire superseded state with source trace.
- Historical Result Record bodies are never rewritten to match current memory.

## Seed Entries

```yaml
entries:
  - type: procedure
    topic: agent workflow and documentation lifecycle boundary
    content: AGENTS.md is the always-on predictor_v3 repository contract. Task-specific calculator, ML/Predictor, UI, and packaging procedure is progressively loaded from repository-local Skills under `.agents/skills/`; `grill-me` is explicit-only. ACTIVE_DOCUMENTS.md is the durable owner discovery map. Change gates, document lifecycle, Result Records, and project memory remain repository governance owners. Engineering Workflow and its Worker/Auditor/Orchestrator lane model are retired for new predictor_v3 work; historical records that used that model remain historical evidence. WORK_PLAN owns only the current product slice/next action/blockers/constraints/holds; project_log owns durable milestone/process history; Result Records remain conditional append-only evidence indexed by REPORT_INDEX.
    keywords: [predictor_v3, AGENTS.md, repo-local skills, routing, ACTIVE_DOCUMENTS, WORK_PLAN, project_log, Result Record, memory review]
    assertionStatus: verified
    source: AGENTS.md; ACTIVE_DOCUMENTS.md; .agents/skills/calculator/SKILL.md; .agents/skills/ml-predictor/SKILL.md; .agents/skills/ui-surface/SKILL.md; .agents/skills/packaging/SKILL.md; docs/agent_workflows/DOCUMENT_SYNC_AND_LIFECYCLE.md; docs/agent_workflows/PROJECT_LOG_AND_MEMORY.md; docs/agent_workflows/RESULT_REPORT_WORKFLOW.md; result_reports/records/2026-09/2026-09-05-astra-agent-harness-migration.md

  - type: decision
    topic: architecture and UI owner boundary
    content: New responsibility stays with an explicit Model/Service-or-Controller/Shell-or-Adapter/View/Policy owner; app entrypoints remain thin and cross-layer dependency direction is preserved. docs/ui_ux is the portable UI/UX owner root, and table/window/input-result behavior uses its shared contracts rather than feature-local reinvention.
    keywords: [clean architecture, owner boundary, thin entrypoint, UI UX, table contract]
    assertionStatus: verified
    source: docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md; docs/ui_ux/00_UI_UX_SYSTEM.md; AGENTS.md

  - type: decision
    topic: calculator standard ownership and unresolved ASNZS evidence
    content: ISO 16358, KS C 9306, EN 14825, AHRI 210/240, Brazil composite capability, and compatibility routes remain separate calculator responsibilities with profile/config behavior owned locally; unsupported selectors/schemas fail fast rather than silently selecting another engine. Within AHRI 210/240, Appendix M SEER/HSPF and Appendix M1 SEER2/HSPF2 are physically separate seasonal-calculation owners with distinct profiles, typed capabilities, configs, and top-level Calculator surfaces. Initial Appendix M support is variable-speed non-ducted single-split; HSPF is Region IV minimum-DHR and follows the AHRI 210/240-2017 with Addendum 1 bin-by-bin COP path, with accepted published golden 10.45 and H42 excluded from the initial M surface. Historical AS/NZS case3 full-dump exact parity remains unresolved until matching workbook or full component-row reference evidence exists.
    keywords: [calculator, ISO16358, KS C 9306, EN14825, AHRI210240, Appendix M, Appendix M1, SEER, HSPF, Brazil CSPF, ASNZS]
    assertionStatus: verified
    source: .agents/skills/calculator/SKILL.md; docs/architecture/project_architecture.md; result_reports/records/2026-09/2026-09-02-ahri-210-240-m-seer-hspf.md; result_reports/legacy/summaries/054_summary-calculator-ui-iso-separation.md; result_reports/legacy/summaries/132_summary-xfail-archive-pyqt-tkinter-stabilization.md

  - type: decision
    topic: Train Predict runtime and application boundary
    content: app_train.py and app_predict.py stay separate thin entrypoints. Train/Predict build runtime-neutral DTO/usecase/port boundaries and inject PySide6 adapters from composition roots; controllers do not own concrete toolkit/process adapters. Predict retains one canonical session/runtime-generation authority and Train owns explicit execution requests/snapshots.
    keywords: [Train, Predict, PySide6, execution port, canonical session, runtime generation]
    assertionStatus: verified
    source: AGENTS.md; docs/architecture/pyside6_train_predict_architecture.md; result_reports/records/2026-07/2026-07-11-clean-hex-mvc-ui-refactor.md

  - type: decision
    topic: Data Definition Data Mapping and ML compatibility ownership
    content: The canonical Data Definition/runtime generation is the user-facing Feature/Target definition owner; schema.csv/features.csv and MODEL_REGISTRY/COLUMNS are generated or compatibility projections, not independent writable SSOTs. Train-required raw headers are the current generation's active `ml_name` contract. Data Mapping owns concrete `mapping.json` values and saved runtime mapping; the legacy wide mapping source is bootstrap-only and must enter a validated unsaved draft rather than becoming a permanent general import contract or auto-writing mapping.json. Current onboarding work must expose a Training Header Template/reference workflow and a missing-mapping bootstrap/review/export/import/Save path, while remaining static compatibility dependencies are audited before source mutation.
    keywords: [Data Definition, Data Mapping, ml_name, training header, features.csv, mapping.json, legacy wide, onboarding]
    assertionStatus: verified
    source: AGENTS.md; docs/designs/2026-07-17-train-admin-phase-4-unified-feature-manager.md; docs/workflows/ml_feature_catalog_workflow.md; docs/designs/2026-07-14-train-admin-phase-1-mapping-data-foundation.md; docs/WORK_PLAN.md

  - type: error
    topic: Data Mapping macOS accessibility interaction risk
    content: Native macOS/AppKit accessibility hierarchy reads have reproducibly crashed during Data Mapping Computer Use table interaction. Automated owner tests and safe native rendering do not prove those physical interaction scenarios; avoid the known AX table path unless a separately scoped acceptance method is available.
    keywords: [Data Mapping, macOS, AppKit, accessibility, Computer Use, SIGSEGV]
    assertionStatus: verified
    source: result_reports/records/2026-07/2026-07-14-train-admin-phase2-slice2bc-native-blocker.md; result_reports/records/2026-07/2026-07-14-train-admin-phase2-slice2a-native-audit-correction.md

  - type: decision
    topic: Train model lifecycle promotion and experiment boundary
    content: Train/Admin Phase 5 is closed. Candidate publication, run/analysis evidence, Active promotion/recovery, experiment/campaign execution, confirmation recovery, migration/retention preview, and deployment export remain distinct lifecycle responsibilities. Active promotion is explicit trusted-user authority; automatic promotion and production mutation are excluded. Complete terminal/Candidate evidence may replay, while incomplete confirmation recovery follows isolated abandon-and-restart semantics without mixing partial attempts.
    keywords: [Train, Phase 5, Candidate, Active, promotion, experiment, confirmation, recovery]
    assertionStatus: verified
    source: docs/designs/2026-07-22-train-model-lifecycle-agent-assisted-experiment-design.md; docs/archive/project_log/2026-07/project_log_2026-07_part01_2026-07-29_to_2026-07-26.md

  - type: decision
    topic: Windows persistence publication and runtime-generation invariants
    content: Windows source-runtime repairs through PR #56 preserve the same logical Candidate/Active/run-evidence, Deployment Export, and runtime-generation publication contracts while using Windows-safe path-based durability/containment. Runtime generation persists portable `/` bundle identities, validates separator-only legacy metadata read-only, rejects unsafe Generation IDs, reconstructs only exact matching incomplete bootstrap residue, and contains mutation against path substitution/reparse redirection. Native Windows 11 Enterprise has now directly confirmed affected-state recovery and clean-state Train startup; PR #57 Result Review alignment is also natively confirmed. Full acceptance remains open because real Train execution through Candidate publication and the remaining application paths are still required.
    keywords: [Windows, persistence, Deployment Export, runtime generation, bundle identity, bootstrap recovery, containment]
    assertionStatus: verified
    source: result_reports/records/2026-08/2026-08-06-windows-model-lifecycle-persistence-compatibility.md; result_reports/records/2026-08/2026-08-06-windows-model-lifecycle-substitution-safety-correction.md; result_reports/records/2026-08/2026-08-06-windows-deployment-export-portability.md; result_reports/records/2026-08/2026-08-06-windows-runtime-generation-file-sync-compatibility.md; result_reports/records/2026-08/2026-08-06-windows-runtime-generation-identity-bootstrap-recovery.md; result_reports/records/2026-08/2026-08-06-windows-runtime-generation-containment-correction.md

  - type: decision
    topic: Predict Target authority and Result Review contract
    content: Predict runtime Target authority comes from the validated generation/runtime, not caller-coherent metadata. Active compatibility remains full-contract while each Case derives only its requested Target subset from canonical raw capacity presence before preprocessing; not-requested Targets project N/A rather than fabricated failures. Result Review is a read-only presentation over the canonical session with execution-pinned provenance, stable-identity specification summary, typed outcomes, and existing stale/unavailable/copy/CSV semantics.
    keywords: [Predict, Target authority, requested subset, Result Review, provenance, stale, unavailable]
    assertionStatus: verified
    source: result_reports/records/2026-08/2026-08-01-predict-runtime-target-authority-provenance-recovery.md; result_reports/records/2026-08/2026-08-02-case-scoped-target-applicability.md; result_reports/records/2026-08/2026-08-02-predict-result-review-projection.md; docs/architecture/pyside6_train_predict_architecture.md

  - type: procedure
    topic: current execution resume point
    content: The bounded Windows repair set is closed through PR #63, so the exact next gate is one continuous Native Windows source-runtime acceptance pass: protected legacy Mapping bootstrap confirmation as needed, real Train through successful Candidate publication, Predict, Experiment/headless CLI, Calculator, then Deployment Export. Native affected-state recovery, clean-state Train startup, and Result Review alignment are already confirmed and should not be repeated without material invalidation. Do not create another Windows repair/audit gate absent new acceptance evidence. Standard Request Product/Owner Decision and Multi-point Predict → Calculate remain held until native Windows acceptance closes; Result Review XLSX remains DEFER.
    keywords: [resume point, Windows acceptance, Candidate publication, headless CLI, Standard Request, Multi-point Predict Calculate]
    assertionStatus: verified
    source: docs/WORK_PLAN.md; project_log.md
```

## Known Gaps

- Historical detail is intentionally omitted from active recall and remains searchable
  through `REPORT_INDEX.md`, project-log archives, memory archives, and owner docs.
- Pre-maintenance active entries are preserved verbatim in
  `result_reports/memory/archive/project_memory_seed_retired_2026-08.md`; July
  retirements remain in `project_memory_seed_retired_2026-07.md`.
- Open external-evidence questions stay unresolved until explicitly scoped evidence
  or policy work closes them.

## Next Maintenance Rule

- Run Memory Review only on its documented triggers or dedicated maintenance.
- Add/update the smallest durable topic; do not append task history.
- Retire stale/superseded state with source trace instead of leaving it active.
- Report count alone never triggers memory cleanup.
