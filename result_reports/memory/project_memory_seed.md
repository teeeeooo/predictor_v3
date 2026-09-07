# Project Memory Seed

## Purpose

This document is the compact active recall bank for long-running predictor_v3 work.
It routes durable lessons, cross-owner relationships, and past-dependent work.
Current acceptance, holds, and next actions belong to `docs/WORK_PLAN.md`.

## Source Coverage

Active entries point to current owner docs, focused decision/failure records,
project-log decisions, and narrowly required historical evidence. Superseded,
resolved, or stale wording is preserved under `result_reports/memory/archive/`.

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
    topic: agent harness v2 recall and routing boundary
    content: "Global harness owns generic execution and reusable Skills; repository owners retain domain contracts. Mandatory Result Records and memory-write gates were retired; historical records remain evidence."
    keywords: [predictor_v3, operating-envelope, AGENTS.md, global skills, grill-me, desktop-table-ui, desktop-window-lifecycle, recall gate, decision record, failure record, historical Result Record]
    assertionStatus: verified
    source: AGENTS.md; ACTIVE_DOCUMENTS.md; docs/agent_workflows/PROJECT_LOG_AND_MEMORY.md; docs/agent_workflows/AGENT_CHANGE_GATES.md; docs/decisions/2026-09-07-agent-harness-v2.md; docs/designs/2026-09-07-astra-agent-harness-v2-migration.md

  - type: decision
    topic: architecture and UI owner boundary
    content: "Locate responsibility at the existing Model/Service-or-Controller/Shell-or-Adapter/View/Policy owner before adding another mechanism. UI contracts live under docs/ui_ux; entrypoints remain thin."
    keywords: [clean architecture, owner boundary, thin entrypoint, UI UX, table contract]
    assertionStatus: verified
    source: docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md; docs/ui_ux/00_UI_UX_SYSTEM.md; AGENTS.md

  - type: decision
    topic: calculator standard ownership and unresolved ASNZS evidence
    content: "Standards and compatibility routes have separate owners; Appendix M and M1 must not collapse into one seasonal engine. Historical AS/NZS case3 parity needs matching workbook/component-row evidence; use the linked owners and record for formula, initial scope, and golden details."
    keywords: [calculator, ISO16358, KS C 9306, EN14825, AHRI210240, Appendix M, Appendix M1, SEER, HSPF, Brazil CSPF, ASNZS]
    assertionStatus: verified
    source: .agents/skills/calculator/SKILL.md; docs/architecture/project_architecture.md; result_reports/records/2026-09/2026-09-02-ahri-210-240-m-seer-hspf.md; result_reports/legacy/summaries/054_summary-calculator-ui-iso-separation.md; result_reports/legacy/summaries/132_summary-xfail-archive-pyqt-tkinter-stabilization.md

  - type: decision
    topic: Train Predict runtime and application boundary
    content: "Train/Predict use runtime-neutral DTO/usecase/port boundaries with PySide6 adapters injected by composition roots. Predict has one session/runtime-generation authority; Train owns explicit execution requests/snapshots."
    keywords: [Train, Predict, PySide6, execution port, canonical session, runtime generation]
    assertionStatus: verified
    source: AGENTS.md; docs/architecture/pyside6_train_predict_architecture.md; result_reports/records/2026-07/2026-07-11-clean-hex-mvc-ui-refactor.md

  - type: decision
    topic: Data Definition Data Mapping and ML compatibility ownership
    content: "Data Definition/runtime generation owns Feature/Target and active ml_name truth; schema.csv/features.csv and MODEL_REGISTRY/COLUMNS are projections. Legacy-wide Mapping conversion is bootstrap-only and enters an unsaved reviewable draft; explicit Save owns publication."
    keywords: [Data Definition, Data Mapping, ml_name, training header, features.csv, mapping.json, legacy wide, onboarding]
    assertionStatus: verified
    source: AGENTS.md; docs/designs/2026-07-17-train-admin-phase-4-unified-feature-manager.md; docs/workflows/ml_feature_catalog_workflow.md; docs/designs/2026-07-14-train-admin-phase-1-mapping-data-foundation.md; docs/WORK_PLAN.md

  - type: error
    topic: Data Mapping macOS accessibility interaction risk
    content: "Native AppKit accessibility hierarchy reads reproducibly crashed during Data Mapping table interaction. Owner tests and native rendering do not prove that physical interaction path; consult the linked failure evidence before choosing an acceptance method."
    keywords: [Data Mapping, macOS, AppKit, accessibility, Computer Use, SIGSEGV]
    assertionStatus: verified
    source: result_reports/records/2026-07/2026-07-14-train-admin-phase2-slice2bc-native-blocker.md; result_reports/records/2026-07/2026-07-14-train-admin-phase2-slice2a-native-audit-correction.md

  - type: decision
    topic: Train model lifecycle promotion and experiment boundary
    content: "Candidate publication, Active promotion, experiment execution, recovery, and export have separate authority/lifetimes. Incomplete confirmation recovery abandons and restarts rather than mixing attempts; replay of complete evidence does not authorize automatic promotion."
    keywords: [Train, Phase 5, Candidate, Active, promotion, experiment, confirmation, recovery]
    assertionStatus: verified
    source: docs/designs/2026-07-22-train-model-lifecycle-agent-assisted-experiment-design.md; docs/archive/project_log/2026-07/project_log_2026-07_part01_2026-07-29_to_2026-07-26.md

  - type: decision
    topic: Windows persistence publication and runtime-generation invariants
    content: "Preserve portable bundle identities and containment across Windows path handling. Separator-only legacy metadata is validated read-only; incomplete bootstrap recovery requires matching identity, and path substitution/reparse redirection must not escape containment."
    keywords: [Windows, persistence, Deployment Export, runtime generation, bundle identity, bootstrap recovery, containment]
    assertionStatus: verified
    source: result_reports/records/2026-08/2026-08-06-windows-model-lifecycle-persistence-compatibility.md; result_reports/records/2026-08/2026-08-06-windows-model-lifecycle-substitution-safety-correction.md; result_reports/records/2026-08/2026-08-06-windows-deployment-export-portability.md; result_reports/records/2026-08/2026-08-06-windows-runtime-generation-file-sync-compatibility.md; result_reports/records/2026-08/2026-08-06-windows-runtime-generation-identity-bootstrap-recovery.md; result_reports/records/2026-08/2026-08-06-windows-runtime-generation-containment-correction.md

  - type: decision
    topic: Predict Target authority and Result Review contract
    content: "Predict Target authority comes from the validated generation; each Case derives requested Targets from raw capacity presence before preprocessing. Not-requested Targets project N/A, while Result Review remains a read-only projection with execution-pinned provenance."
    keywords: [Predict, Target authority, requested subset, Result Review, provenance, stale, unavailable]
    assertionStatus: verified
    source: result_reports/records/2026-08/2026-08-01-predict-runtime-target-authority-provenance-recovery.md; result_reports/records/2026-08/2026-08-02-case-scoped-target-applicability.md; result_reports/records/2026-08/2026-08-02-predict-result-review-projection.md; docs/architecture/pyside6_train_predict_architecture.md

  - type: procedure
    topic: execution resume and evidence reuse routing
    content: "Resolve the current acceptance sequence, holds, and reusable native evidence from docs/WORK_PLAN.md. Prior Windows repair cycles taught that already-accepted owner evidence should be reused until materially invalidated; a new repair needs a demonstrated defect, not only an unfinished acceptance pass."
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

- Update memory only when a durable decision, failure, owner relationship, expensive fact, or long-horizon resume clue justifies it.
- Add or update the smallest durable topic; do not append task history.
- Retire stale/superseded state with source trace instead of leaving it active.
- Historical report count never triggers memory cleanup.
