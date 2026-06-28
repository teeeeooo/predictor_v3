# Project Memory Seed

## Purpose

This document stages backend-neutral long-term memory candidates from existing summary reports. It is suitable as input for a future local index or memory backend import, without defining or requiring any backend.

## Source Summaries

- `result_reports/summaries/011_summary-agent-rules-doc-workflow.md` (covered reports `001-010`)
- `result_reports/summaries/020_summary-active-report-doc-lifecycle.md` (covered reports `012-019`)
- `result_reports/summaries/033_summary-calculator-architecture-ks-profile-dispatch.md` (covered reports `021-032`)
- `result_reports/summaries/054_summary-calculator-ui-iso-separation.md` (covered reports `034-053`)
- `result_reports/summaries/081_summary-calculator-ui-v1-audit-2-3.md` (covered reports `055-068`)
- `result_reports/summaries/082_summary-envelope-adapter-four-stage-chain.md` (covered reports `069-080`)
- `result_reports/summaries/101_summary-calculator-ui-iso-hspf-stabilization.md` (covered reports `082-100`)
- `result_reports/summaries/114_summary-ui-ux-ssot-calculator-boundary.md` (covered reports `102-113`)
- `result_reports/summaries/123_summary-calculator-tkinter-quality-xfail.md` (covered reports `115-122`)
- `result_reports/summaries/132_summary-xfail-archive-pyqt-tkinter-stabilization.md` (covered reports `124-131`)
- `result_reports/summaries/140_summary-project-memory-delta-workflow.md` (covered reports `133-139`)
- `result_reports/summaries/153_summary-agent-workflow-memory-token-log-lifecycle.md` (covered reports `141-152`)
- `result_reports/summaries/165_summary-pyqt-retirement-tkinter-ui-matrix-rules.md` (covered reports `154-164`)
- `result_reports/summaries/180_summary-tkinter-calculator-ux-implementation-arc.md` (covered reports `166-179e`)
- `result_reports/summaries/191_summary-tkinter-iso-profile-expansion-arc.md` (covered reports `184-190a2`)
- `result_reports/summaries/195_summary-tkinter-detail-panel-copy-graph-arc.md` (covered reports `190b-194e` plus `194f` hotfix)
- `result_reports/summaries/200_summary-window-geometry-viewport-ui-pivot-prep-arc.md` (covered reports `196-a-199-c`)
- `result_reports/summaries/221_summary-post-main-table-window-refit-arc.md` (covered reports `202-221b`, with `221c` kept active as next-decision evidence)
- `result_reports/summaries/231_summary-architecture-uiux-boundary-and-window-refit-arc.md` (covered reports `221c-228` and `230a-230d`, with `229` kept active as next-code-slice evidence)
- `result_reports/summaries/236_summary-window-dialog-batch-viewport-arc.md` (covered reports `229`, `231`, `232`, `233A-233F guard`, `234`, and `235`)
- `result_reports/summaries/249_summary-batch-two-row-matrix-and-reference-parity-arc.md` (covered reports `237-248`)
- `result_reports/summaries/260_summary-hspf-detail-schema-window-lifecycle-arc-closeout.md` (covered reports `250-259`)
- `result_reports/summaries/292_summary-paste-policy-validation-arc.md` (covered reports `261-291`)
- `result_reports/summaries/293_summary-reference-map-code-checker-arc.md` (covered reports `270-272`)
- `result_reports/summaries/294_summary-result-formatting-bin-detail-cleanup-arc.md` (covered reports `276-289`)
- `result_reports/summaries/295_summary-controller-switch-resultpanel-focus-arc.md` (covered reports `290-291`)
- `result_reports/summaries/314_summary-tkinter-table-controller-switch-arc-closeout.md` (covered reports `298-313`)
- `result_reports/summaries/334_summary-batch-dialog-doc-memory-lifecycle-closeout.md` (covered reports `315-333`)
- `result_reports/summaries/346_summary-batch-foundation-apps-calculator-relocation-closeout.md` (covered reports `335-345`)
- `result_reports/summaries/364_summary-pyqt-retirement-en14825-seer-owner-guard.md` (covered reports `347-363`)
- `result_reports/summaries/385_summary-en14825-ui-correction-lifecycle-closeout.md` (covered reports `365-384`)
- `result_reports/summaries/404_summary-en14825-config-point-contract-ui-workflow-closeout.md` (covered reports `386-403`)
- `result_reports/summaries/416_summary-en14825-batch-agent-change-gate-closeout.md` (covered reports `405-415`)
- `result_reports/summaries/445_summary-ahri-calculator-ui-batch-lifecycle-closeout.md` (covered reports `417-444`)
- `result_reports/summaries/461_summary-en14825-ahri-detail-lifecycle-closeout.md` (covered reports `449-461`)
- `result_reports/summaries/480_summary-calculator-closeout-token-cleanup-structure-audit.md` (covered reports `448`, `462-475`, with `476-479` kept active as next-decision evidence)
- `result_reports/summaries/490_summary-calculator-helper-batch-lifecycle-closeout.md` (covered reports `476-479`, `481-489`)
- `result_reports/summaries/516_summary-architecture-reset-pyside6-foundation-closeout.md` (covered reports `491-492`, `507-515`)
- `result_reports/summaries/536_summary-arc7-arc85-core-owner-wrapper-retirement-closeout.md` (covered reports `517-535`)
- `result_reports/summaries/554_summary-arc9-pyside6-schema-legacy-ui-harvest-closeout.md` (covered reports `537-553`)

## Scope and Non-goals

- Seed entries preserve durable decisions, procedures, verified failure states, and unresolved follow-ups that affect later work.
- Entries derive from summary headings and scoped decision/risk/action sections; archived individual report bodies were not read for this seed.
- This document does not backfill individual reports, modify summaries or `project_log.md`, move archive files, or connect to a memory backend.
- Hypotheses and uncompleted work are represented as `open_question`, not confirmed decisions.

## Seed Entries

```yaml
entries:
  - type: procedure
    topic: predictor_v3 result report lifecycle
    content: predictor_v3 agent work stores tracked-file task outcomes as committed Markdown result reports using global sequential numbering across active, summaries, and archive; report numbering uses current checkout state without agent-initiated pull, merge, or rebase.
    keywords:
      - predictor_v3
      - result report
      - global numbering
      - lifecycle
    assertionStatus: verified
    source: result_reports/summaries/011_summary-agent-rules-doc-workflow.md (covered reports 001-010; Major Decisions and Result Report Workflow Decisions)

  - type: procedure
    topic: predictor_v3 report summary and project log boundary
    content: predictor_v3 summaries group reports by workstream or arc, and summary-time project_log review records only durable decision, failure, lesson, or process-rule changes rather than copying report bodies.
    keywords:
      - predictor_v3
      - summary
      - project_log
      - process rule
    assertionStatus: verified
    source: result_reports/summaries/011_summary-agent-rules-doc-workflow.md (covered reports 001-010; Major Decisions and Project Log Sync Judgment)

  - type: decision
    topic: predictor_v3 active agent rule ownership
    content: AGENTS.md is the active lite entrypoint, AGENT_TASK_ROUTER.md owns task routing and result report workflow, and docs/archive/AGENTS_FULL.md is an archived detailed reference rather than an active rules source.
    keywords:
      - predictor_v3
      - AGENTS.md
      - AGENT_TASK_ROUTER.md
      - archived reference
    assertionStatus: verified
    source: result_reports/summaries/011_summary-agent-rules-doc-workflow.md (covered reports 001-010; Documentation System Changes)

  - type: procedure
    topic: predictor_v3 report lifecycle check modes
    content: AGENT_TASK_ROUTER.md owns metadata-only lifecycle checks and compact, full, and no-report report modes; routine checks are intended to avoid rereading archived report bodies.
    keywords:
      - predictor_v3
      - lifecycle check
      - compact report
      - metadata-only
    assertionStatus: verified
    source: result_reports/summaries/020_summary-active-report-doc-lifecycle.md (covered reports 012-019; Consolidated Result)

  - type: decision
    topic: predictor_v3 calculator standard ownership
    content: ISO 16358, KS C 9306, and AS/NZS workbook compatibility remain separate calculator responsibilities; ISO common logic must not absorb KS behavior or AS/NZS workbook conventions.
    keywords:
      - predictor_v3
      - ISO16358
      - KS C 9306
      - ASNZS
    assertionStatus: verified
    source: result_reports/summaries/033_summary-calculator-architecture-ks-profile-dispatch.md (covered reports 021-032; Key Decisions and Architecture / Process Rules Fixed)

  - type: decision
    topic: predictor_v3 region config ownership
    content: data/region_configs is a shared static standard and region config store, while each calculator interprets its own configuration; korea.json is interpreted by KSC9306Calculator rather than the ISO common path.
    keywords:
      - predictor_v3
      - region config
      - korea.json
      - calculator boundary
    assertionStatus: verified
    source: result_reports/summaries/033_summary-calculator-architecture-ks-profile-dispatch.md (covered reports 021-032; Key Decisions)

  - type: decision
    topic: predictor_v3 calculator profile routing
    content: Calculator routing is explicit through calculator_id; the profile resolver selects manifest metadata and core/calculator_dispatcher.py creates calculator instances rather than activating calculators from region or standard metadata alone.
    keywords:
      - predictor_v3
      - calculator_id
      - profile resolver
      - dispatcher
    assertionStatus: verified
    source: result_reports/summaries/033_summary-calculator-architecture-ks-profile-dispatch.md (covered reports 021-032; Key Decisions and Architecture / Process Rules Fixed)

  - type: open_question
    topic: predictor_v3 ISO profile dispatcher coverage
    content: ISO16358 profile manifest registration and dispatcher routing were deferred after the KS and AHRI dispatcher foundation; a later authorized slice must decide and implement ISO region-profile routing.
    keywords:
      - predictor_v3
      - ISO16358
      - dispatcher
      - profile manifest
    assertionStatus: observed
    source: result_reports/summaries/033_summary-calculator-architecture-ks-profile-dispatch.md (covered reports 021-032; Remaining Risks and Next Suggested Action)

  - type: decision
    topic: predictor_v3 canonical ISO and compatibility separation
    content: Rebuilt ISO 16358 CSPF and HSPF common logic excludes KS and AS/NZS workbook responsibilities; AS/NZS workbook compatibility is an explicit opt-in path and does not claim official production formula parity.
    keywords:
      - predictor_v3
      - ISO16358
      - ASNZS_EXCEL_COMPAT
      - compatibility
    assertionStatus: verified
    source: result_reports/summaries/054_summary-calculator-ui-iso-separation.md (covered reports 034-053; Workstream Summary and Decisions Preserved)

  - type: open_question
    topic: ASNZS case3 full-dump parity
    content: Historical AS/NZS case3 full-dump exact parity remains deferred until matching workbook or full component-row reference data is available.
    keywords:
      - predictor_v3
      - ASNZS
      - case3
      - external reference
    assertionStatus: observed
    source: result_reports/summaries/054_summary-calculator-ui-iso-separation.md (covered reports 034-053; Decisions Preserved); result_reports/summaries/132_summary-xfail-archive-pyqt-tkinter-stabilization.md (covered reports 124-131; Key Decisions)

  - type: decision
    topic: calculator result envelope and ML boundary
    content: Calculator result envelope and ML adapter responsibilities are separated from calculator public APIs, with boundary guards preventing runtime, ML, and ranking terms from entering region configuration.
    keywords:
      - predictor_v3
      - calculator envelope
      - ML adapter
      - schema boundary
    assertionStatus: verified
    source: result_reports/summaries/081_summary-calculator-ui-v1-audit-2-3.md (covered reports 055-068; Workstream Summary)

  - type: decision
    topic: CalculatorInputEnvelope schema
    content: CalculatorInputEnvelope uses the shape calculator_profile_id, standard, region, mode, metric, measured_inputs, and options; source is stored in options and source vocabulary is limited to manual_candidate, ml_prediction, and fixture.
    keywords:
      - predictor_v3
      - CalculatorInputEnvelope
      - source vocabulary
      - adapter schema
    assertionStatus: verified
    source: result_reports/summaries/082_summary-envelope-adapter-four-stage-chain.md (covered reports 069-080; Decisions Preserved)

  - type: decision
    topic: calculator envelope unit conversion boundary
    content: Envelope adapters do not perform unit conversion; AHRI SEER2 envelope inputs require Btu/h capacity and W power and fail fast on unit mismatches.
    keywords:
      - predictor_v3
      - unit conversion
      - AHRI SEER2
      - fail fast
    assertionStatus: verified
    source: result_reports/summaries/082_summary-envelope-adapter-four-stage-chain.md (covered reports 069-080; Decisions Preserved)

  - type: decision
    topic: ranking consumption boundary
    content: Ranking layers consume RankingCandidateEnvelope fields instead of raw calculator output; raw_result and diagnostics are intentionally not exposed downstream by the minimum ranking adapter slice.
    keywords:
      - predictor_v3
      - RankingCandidateEnvelope
      - ranking
      - calculator result
    assertionStatus: verified
    source: result_reports/summaries/082_summary-envelope-adapter-four-stage-chain.md (covered reports 069-080; Workstream Summary and Decisions Preserved)

  - type: open_question
    topic: calculator envelope profile expansion
    content: Input, predicted-points, and ranking adapter slices initially support AHRI SEER2 only; EN, KS, and ISO profile coverage remains a follow-up decision and implementation task.
    keywords:
      - predictor_v3
      - envelope adapter
      - ISO16358
      - profile coverage
    assertionStatus: observed
    source: result_reports/summaries/082_summary-envelope-adapter-four-stage-chain.md (covered reports 069-080; Decisions Preserved)

  - type: decision
    topic: spreadsheet table UX contract
    content: PyQt table surfaces use the UI/UX system spreadsheet table contract as their single owner and default to Excel-like copy, paste, clear, undo, keyboard navigation, and invalid-numeric feedback behavior.
    keywords:
      - predictor_v3
      - spreadsheet table
      - Excel-like
      - UI UX SSOT
    assertionStatus: verified
    source: result_reports/summaries/101_summary-calculator-ui-iso-hspf-stabilization.md (covered reports 082-100; Key Decisions); result_reports/summaries/114_summary-ui-ux-ssot-calculator-boundary.md (covered reports 102-113; Key Decisions)

  - type: decision
    topic: profile-native unit conversion owner
    content: ML W to profile-native unit conversion for horizontal table inputs is owned by core/calculator_unit_adapter.py rather than UI table components.
    keywords:
      - predictor_v3
      - calculator_unit_adapter
      - unit conversion
      - table input
    assertionStatus: verified
    source: result_reports/summaries/101_summary-calculator-ui-iso-hspf-stabilization.md (covered reports 082-100; Key Decisions)

  - type: error
    topic: ISO16358-2 HSPF extended minus7 default factor
    content: ISO16358-2 HSPF mismatch was caused by applying 0.734 or 0.877 directly to 2 degree Celsius frost measured values in _iso_hspf_extended_minus7_default; the corrected path applies the measured-to-default step before the extension factor.
    keywords:
      - predictor_v3
      - ISO16358-2 HSPF
      - minus7
      - frost factor
    assertionStatus: verified
    source: result_reports/summaries/101_summary-calculator-ui-iso-hspf-stabilization.md (covered reports 082-100; Key Decisions)

  - type: fact
    topic: ISO16358-2 HSPF official exact fixture status
    content: After source audit and the extended minus7 factor correction, the ISO16358-2 HSPF official exact fixture expected values became the final golden and XFAIL_CASE_IDS was empty.
    keywords:
      - predictor_v3
      - ISO16358-2 HSPF
      - golden
      - xfail
    assertionStatus: verified
    source: result_reports/summaries/101_summary-calculator-ui-iso-hspf-stabilization.md (covered reports 082-100; Key Decisions and Completed Work)

  - type: open_question
    topic: ISO table and unit adapter follow-up
    content: ISO input and read-only result table alignment plus ISO, KS, and EN unit-adapter expansion remained queued after HSPF stabilization.
    keywords:
      - predictor_v3
      - ISO table
      - calculator_unit_adapter
      - follow-up
    assertionStatus: observed
    source: result_reports/summaries/101_summary-calculator-ui-iso-hspf-stabilization.md (covered reports 082-100; Remaining Work and Next Suggested Actions)

  - type: decision
    topic: predictor_v3 UI UX source of truth
    content: docs/ui_ux is the active UI and UX source-of-truth root, while the legacy spreadsheet contract text is retained only as historical source material under docs/ui_ux/_source.
    keywords:
      - predictor_v3
      - docs/ui_ux
      - SSOT
      - UI contract
    assertionStatus: verified
    source: result_reports/summaries/114_summary-ui-ux-ssot-calculator-boundary.md (covered reports 102-113; Key Decisions)

  - type: decision
    topic: calculator action model
    content: Calculator UI action alignment selected auto-calc unified Option A, with implementation ordered through recompute wiring, result/status surface unification, and error feedback alignment.
    keywords:
      - predictor_v3
      - calculator UI
      - auto-calc
      - action model
    assertionStatus: verified
    source: result_reports/summaries/114_summary-ui-ux-ssot-calculator-boundary.md (covered reports 102-113; Key Decisions and Remaining Work)

  - type: decision
    topic: calculator UI module boundary
    content: Calculator UI refactoring targets a thin calc_window shell, per-tab EN and AHRI modules, and shared error, recompute, and result-panel helpers; module extraction precedes recompute and result-panel slices.
    keywords:
      - predictor_v3
      - calculator UI
      - module boundary
      - calc_window
    assertionStatus: verified
    source: result_reports/summaries/114_summary-ui-ux-ssot-calculator-boundary.md (covered reports 102-113; Key Decisions and Architecture / Design Decisions)

  - type: open_question
    topic: Train and Predict UI deferred refactor
    content: Train and Predict UI literal and result-key duplication was observed but intentionally deferred until ML or inverse-search work resumes, rather than mixed into Calculator action-model slices.
    keywords:
      - predictor_v3
      - Train UI
      - Predict UI
      - ML return
    assertionStatus: observed
    source: result_reports/summaries/114_summary-ui-ux-ssot-calculator-boundary.md (covered reports 102-113; Key Decisions and Remaining Work)

  - type: decision
    topic: lightweight calculator deployment direction
    content: PyQt calculator-only packaging direction is on hold while a lightweight Tkinter calculator direction is evaluated; the initial single-file Tkinter spike was rejected as a lasting module structure.
    keywords:
      - predictor_v3
      - Tkinter
      - PyQt
      - deployment
    assertionStatus: verified
    source: result_reports/summaries/123_summary-calculator-tkinter-quality-xfail.md (covered reports 115-122; Key Decisions)

  - type: decision
    topic: project-wide new code quality gate
    content: New code quality rules apply project-wide, requiring thin app entrypoints, layer import boundaries, focused module responsibilities, and structure-guard verification for structure-impacting work.
    keywords:
      - predictor_v3
      - code quality gate
      - app entrypoint
      - layer boundary
    assertionStatus: verified
    source: result_reports/summaries/123_summary-calculator-tkinter-quality-xfail.md (covered reports 115-122; Architecture / Quality Gate Decisions)

  - type: decision
    topic: ISO pure-route obsolete xfail retirement
    content: ISO pure-route Formula 45, 49, 47, and 50 xfails were classified as obsolete experiments and removed; the production official-exact path remains protected by fixture, workbook-reference, cycling, boundary, and auxiliary guards.
    keywords:
      - predictor_v3
      - ISO16358
      - xfail
      - obsolete experiment
    assertionStatus: verified
    source: result_reports/summaries/132_summary-xfail-archive-pyqt-tkinter-stabilization.md (covered reports 124-131; Key Decisions and Xfail Status)

  - type: fact
    topic: remaining diagnostic xfail ownership
    content: Seventeen tests under tests/_legacy remain legacy workbook-oracle diagnostic or reference xfails, and two AS/NZS case3 xfails remain external-reference prerequisites rather than production ISO16358 failures.
    keywords:
      - predictor_v3
      - tests/_legacy
      - ASNZS case3
      - xfail
    assertionStatus: verified
    source: result_reports/summaries/132_summary-xfail-archive-pyqt-tkinter-stabilization.md (covered reports 124-131; Key Decisions and Xfail Status)

  - type: error
    topic: PyQt macOS Python 3.14 test environment
    content: macOS 15.7.3 arm64 with Python 3.14.4 and PyQt5 5.15.11 or Qt 5.15.14 can abort natively during selected QTableView subclass construction paths; four PyQt widget test files are skipped only on this known-bad environment.
    keywords:
      - predictor_v3
      - PyQt5
      - macOS
      - SIGABRT
    assertionStatus: verified
    source: result_reports/summaries/132_summary-xfail-archive-pyqt-tkinter-stabilization.md (covered reports 124-131; Key Decisions)

  - type: decision
    topic: PyQt and Tkinter calculator direction
    content: PyQt Predict and Train applications remain candidates for retention, while PyQt calculator-only assets are candidates for a read-only retirement audit; the Tkinter calculator direction proceeds from the clean foundation and pure ISO helper split.
    keywords:
      - predictor_v3
      - PyQt
      - Tkinter
      - calculator-only
    assertionStatus: superseded
    resolutionStatus: superseded
    supersededBy: Tkinter calculator active direction and PyQt/PySide6 UI transition
    source: result_reports/summaries/132_summary-xfail-archive-pyqt-tkinter-stabilization.md (covered reports 124-131; PyQt / Tkinter Direction)

  - type: open_question
    topic: deployment and PyQt validation follow-up
    content: Windows PyInstaller size measurement and Python 3.12 or 3.11 or Windows PyQt smoke validation remain pending follow-up work.
    keywords:
      - predictor_v3
      - PyInstaller
      - PyQt
      - validation
    assertionStatus: stale
    resolutionStatus: stale
    source: result_reports/summaries/132_summary-xfail-archive-pyqt-tkinter-stabilization.md (covered reports 124-131; Remaining Work and Next Suggested Actions)

  - type: procedure
    topic: predictor_v3 Project Memory Delta staging workflow
    content: predictor_v3 result reports record durable memory candidates in a backend-neutral Project Memory Delta format, serialize new keywords as YAML lists, and stage consolidated summary-level memory in result_reports/memory/project_memory_seed.md with source traceability rather than retroactively rewriting original reports.
    keywords:
      - predictor_v3
      - project memory delta
      - memory seed
      - backend-neutral
    assertionStatus: verified
    source: result_reports/summaries/140_summary-project-memory-delta-workflow.md (covered reports 133-139; Key Decisions and Project Memory Seed Sync Judgment)

  - type: procedure
    topic: predictor_v3 agent workflow token leakage hardening and project_log archive lifecycle
    content: predictor_v3 agent workflow implements token-leakage prevention via wc -l/du -sh pre-checks, rg-based heading navigation, Quick Route Index, group summary modified lines, and capped-segment project_log archive under docs/archive/project_log/YYYY-MM/. AGENTS_FULL stale references were removed from all active workflow documents.
    keywords:
      - predictor_v3
      - token-leakage
      - workflow-hardening
      - project-log-archive
      - quick-route-index
    assertionStatus: verified
    source: result_reports/summaries/153_summary-agent-workflow-memory-token-log-lifecycle.md (covered reports 141-152; Key Decisions)

  - type: procedure
    topic: predictor_v3 memory seed sync and maintenance policy
    content: predictor_v3 memory seed updates require an explicit Project Memory Seed Sync Judgment during summary lifecycle or memory maintenance tasks, limited to 1-2 summary-level entries per update. Seed maintenance uses importance levels, stale/superseded/resolutionStatus marking instead of deletion, supersedes references, and 50-entry audit / 75-entry mandatory maintenance thresholds.
    keywords:
      - predictor_v3
      - memory-seed
      - sync-judgment
      - maintenance-policy
      - project-memory-delta
    assertionStatus: verified
    source: result_reports/summaries/153_summary-agent-workflow-memory-token-log-lifecycle.md (covered reports 141-152; Key Decisions)

  - type: decision
    topic: project-wide visual and input-result surface SSOT
    content: predictor_v3 adopts docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md and docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md as project-wide UI/UX owners; repeated structured inputs use headered matrix tables and primary results use summary surfaces, while graph/detail surfaces remain a lightweight later phase.
    keywords:
      - predictor_v3
      - UI/UX SSOT
      - visual design
      - input matrix
      - result surface
      - graph detail
    assertionStatus: verified
    source: result_reports/summaries/165_summary-pyqt-retirement-tkinter-ui-matrix-rules.md (covered reports 158-164; Key Decisions and UI/UX SSOT Changes)

  - type: decision
    topic: Tkinter calculator matrix UI and PyQt retirement gate
    content: Tkinter ISO Hong Kong CSPF and HSPF use matrix input, auto-calc, and summary result surfaces while retaining existing calculation routes and smoke values; PyQt calculator-only source retirement remains held pending Tkinter UX and Windows packaging judgment, with shared PyQt utilities retained on hold.
    keywords:
      - predictor_v3
      - Tkinter calculator
      - Hong Kong
      - auto-calc
      - PyQt calculator retirement
      - packaging
    assertionStatus: superseded
    resolutionStatus: superseded
    supersededBy: Tkinter calculator active direction and PyQt/PySide6 UI transition
    source: result_reports/summaries/165_summary-pyqt-retirement-tkinter-ui-matrix-rules.md (covered reports 158-164; Tkinter Calculator Status and PyQt Calculator Retirement Status)

  - type: decision
    topic: Excel-like table state machine and Tkinter controller UX
    content: Spreadsheet-like table interaction follows a toolkit-agnostic state machine with Selection mode and Edit mode. Type-to-replace, same-cell second click, double click, and F2 enter Edit mode. Esc or focus loss commits the edit and returns to Selection mode. Cross-table click commits the current edit before selecting the new cell. MetricInputTable provides address lookup and notify-once batch mutation APIs; ExcelLikeTableController owns interaction state and bindings.
    keywords:
      - predictor_v3
      - Excel-like table
      - selection mode
      - edit mode
      - state machine
      - Tkinter controller
      - cross-table commit
    assertionStatus: verified
    source: result_reports/summaries/180_summary-tkinter-calculator-ux-implementation-arc.md (covered reports 166-179e; Key Decisions and Completed Work)

  - type: decision
    topic: Tkinter calculator metric sub-tab amendment
    content: Top-level standard tabs and region selectors remain. Per-region tabs and standard-tab replacement remain rejected. When content density makes a single vertical view impractical, metric sub-tabs or equivalent segmented metric navigation inside a standard tab are permitted. ISO Hong Kong CSPF/HSPF defaults to same-view but metric separation is recommended. EN 14825 SEER/SCOP and AHRI 210/240 SEER2/HSPF2 follow the same principle.
    keywords:
      - predictor_v3
      - Tkinter calculator
      - metric sub-tab
      - design amendment
      - content density
      - ISO Hong Kong
      - CSPF
      - HSPF
    assertionStatus: verified
    source: result_reports/summaries/180_summary-tkinter-calculator-ux-implementation-arc.md (covered reports 166-179e; Key Decisions)

  - type: decision
    topic: Tkinter ISO profile expansion and result comparison
    content: The Tkinter ISO tab now uses an ISO profile selector with ISO / ISEER 2-point as the default and Hong Kong as the existing CSPF/HSPF profile. ISO / ISEER 2-point results are displayed in a section-local read-only comparison table for ISO 16358-1 and India ISEER. Hong Kong keeps the existing ResultPanel path. Profile-switch geometry exact-fits the current rendered preferred size, applies one measured-overflow correction if needed, and resets scroll to top.
    keywords:
      - predictor_v3
      - Tkinter calculator
      - ISO profile
      - ISO / ISEER 2-point
      - Hong Kong
      - result comparison
      - window geometry
    assertionStatus: verified
    source: result_reports/summaries/191_summary-tkinter-iso-profile-expansion-arc.md (covered reports 184-190a2; Main Decisions and Implementation Outcomes)

  - type: decision
    topic: SASO T3 Tkinter design direction
    content: SASO T3 is designed as a future dedicated Tkinter ISO section using the existing saso_t3_cspf profile/config path. Required inputs are 46 Full, 35 Full, and 35 Half; optional input is 35 Min. The intended result surface compares Required only (3-point) and With 35 Min (4-point) scenarios. This is a design decision only; SASO T3 implementation remains pending.
    keywords:
      - predictor_v3
      - Tkinter calculator
      - SASO T3
      - Design First Gate
      - required-only
      - optional min
      - result comparison
    assertionStatus: verified
    source: result_reports/summaries/191_summary-tkinter-iso-profile-expansion-arc.md (covered reports 190a and 190a2; SASO T3 Design Decision)

  - type: decision
    topic: Tkinter ISO detail panel IA and table copy/export policy
    content: Tkinter ISO result detail parity follows the PyQt reference IA. Main result surfaces expose a detail toggle, while source selector, summary strip, Canvas graph, detail table, detail TSV copy, and detail CSV export live inside the detail panel. Result comparison tables provide header-included TSV copy only; detail/bin tables provide header-included TSV copy plus CSV export.
    keywords:
      - predictor_v3
      - Tkinter calculator
      - PyQt reference IA
      - detail panel
      - TSV copy
      - CSV export
      - BinTraceTable
    assertionStatus: verified
    source: result_reports/summaries/195_summary-tkinter-detail-panel-copy-graph-arc.md (Important Decisions)

  - type: decision
    topic: Tkinter ISO detail graph axis mapping
    content: Tkinter ISO detail panel graphs use outdoor temperature bin tj as the x-axis, displayed as Outdoor Temp [°C], with row index fallback only when tj is unavailable. The selected graph series is the y-axis; Bin Hours [h] remains a y-series backed by nj.
    keywords:
      - predictor_v3
      - Tkinter calculator
      - detail graph
      - graph axis
      - tj
      - outdoor temperature
      - bin hours
    assertionStatus: verified
    source: result_reports/summaries/195_summary-tkinter-detail-panel-copy-graph-arc.md (Completed Work and Important Decisions)

  - type: open_question
    topic: Tkinter calculator multi-monitor geometry clipping
    content: Superseded by the 196-a through 199-c window geometry/viewport arc. Multi-monitor detail open/profile switch clipping was handled without changing result/detail semantics; see the 200 summary entry.
    keywords:
      - predictor_v3
      - Tkinter calculator
      - multi-monitor
      - geometry
      - clipping
      - hotfix
    assertionStatus: resolved
    source: result_reports/summaries/195_summary-tkinter-detail-panel-copy-graph-arc.md (Known Remaining Issues), superseded by result_reports/summaries/200_summary-window-geometry-viewport-ui-pivot-prep-arc.md

  - type: decision
    topic: Tkinter window geometry and viewport policy before UI pivot
    content: The 196-a through 199-c arc closed MetricInputTable single-click replace-on-type, multi-monitor detail/profile geometry, first-launch/detail auto-fit, 80% automatic height cap, top-safe y positioning, and viewport policy documentation. The reusable policy owner is docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md. Automatic fit caps visible height but must not block manual resize; profile/detail fit preserves current x/current monitor and avoids primary recenter. Windows calculator_tk packaged size of approximately 11 MB is acceptable for the current lightweight calculator candidate. Next decision is the UI technology pivot design gate.
    keywords:
      - predictor_v3
      - Tkinter calculator
      - window geometry
      - viewport policy
      - multi-monitor
      - replace-on-type
      - auto-fit
      - top-safe
      - UI technology pivot
    assertionStatus: verified
    source: result_reports/summaries/200_summary-window-geometry-viewport-ui-pivot-prep-arc.md

  - type: decision
    topic: common Tk table foundation for table-shaped UI
    content: Tkinter table-shaped UI should use the predictor_v3 common Tk table foundation before adding independent controllers. The foundation first slice owns reusable interaction helpers, cell roles, surface protocol, and Tk controller behavior; calculator main table migration remains pending.
    keywords:
      - predictor_v3
      - Tkinter
      - common table foundation
      - table-shaped UI
      - Excel-like
    assertionStatus: verified
    source: result_reports/summaries/221_summary-post-main-table-window-refit-arc.md

  - type: decision
    topic: SPOT table UX evidence boundary
    content: SPOT is concrete desired-UX evidence for table interaction feel, not a source of truth, dependency, vendor target, or copy target. The toolkit-neutral table source of truth remains docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md.
    keywords:
      - predictor_v3
      - SPOT
      - table UX
      - evidence
      - source of truth
    assertionStatus: verified
    source: result_reports/summaries/221_summary-post-main-table-window-refit-arc.md

  - type: decision
    topic: selected-range fill paste table contract
    content: Selected-range fill paste is part of the common table UX target; a 1 x N clipboard pasted into an M x N editable selection repeats the clipboard row for each selected row, and a 1 x 1 clipboard can fill the selected editable range while read-only/result cells remain protected.
    keywords:
      - predictor_v3
      - selected-range fill paste
      - table UX
      - read-only result cells
      - Excel-like
    assertionStatus: verified
    source: result_reports/summaries/221_summary-post-main-table-window-refit-arc.md

  - type: open_question
    topic: common dynamic content refit owner
    content: Dynamic and nested content refit is a toolkit-neutral owner-boundary problem. Hong Kong direct metric tab-change refit caused a Windows resize loop and was disabled in 221C. The common dynamic content refit owner first slice now exists; the unresolved follow-up moved to visible content measurement/provider extraction.
    keywords:
      - predictor_v3
      - dynamic content refit
      - nested notebook
      - Hong Kong
      - window geometry
    assertionStatus: superseded
    resolutionStatus: retired
    supersededBy: result_reports/summaries/231_summary-architecture-uiux-boundary-and-window-refit-arc.md
    source: result_reports/summaries/221_summary-post-main-table-window-refit-arc.md; result_reports/summaries/231_summary-architecture-uiux-boundary-and-window-refit-arc.md

  - type: decision
    topic: codebase-wide Clean Architecture boundary owner
    content: Model, Controller or Service, Shell or Adapter, View, and Policy responsibility boundaries are owned by docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md. Concrete project, interface, or integration names are examples/evidence rather than scope boundaries.
    keywords:
      - clean architecture
      - MVC boundary
      - owner boundary
      - responsibility boundary
    assertionStatus: verified
    source: result_reports/summaries/231_summary-architecture-uiux-boundary-and-window-refit-arc.md

  - type: decision
    topic: portable UI UX rule set
    content: docs/ui_ux is a portable UI/UX rule set. 00_UI_UX_SYSTEM.md remains the root SSOT, 01 through 07 are portable principle/policy owners, adapters are interface-framework-specific, and _source files are historical/evidence sources. Concrete names are evidence or adoption notes, not principle scope boundaries.
    keywords:
      - UI UX
      - portable docs
      - examples evidence
      - adapter documents
    assertionStatus: verified
    source: result_reports/summaries/231_summary-architecture-uiux-boundary-and-window-refit-arc.md

  - type: open_question
    topic: Tk visible content measurement adapter extraction
    content: Superseded by the 232-235 window/dialog/batch viewport arc. The visible measurement adapter was extracted, the measurement snapshot and mapped-surface lifecycle slices resolved the Hong Kong lower blank space/refit loop, and batch dialog sizing/state/viewport wheel behavior were accepted for the current arc.
    keywords:
      - Tkinter
      - visible content measurement
      - window_shell
      - Hong Kong lower blank space
    assertionStatus: superseded
    resolutionStatus: retired
    supersededBy: result_reports/summaries/236_summary-window-dialog-batch-viewport-arc.md
    source: result_reports/summaries/231_summary-architecture-uiux-boundary-and-window-refit-arc.md; result_reports/summaries/236_summary-window-dialog-batch-viewport-arc.md

  - type: decision
    topic: batch two-row matrix layout preflight boundary
    content: After the 229/232/233/234/235 window-dialog-table-batch viewport arc, the next batch work is a design/preflight for a unified two-row matrix layout: one logical case maps to capacity/performance and power physical rows, result columns are profile output metrics such as Hong Kong CSPF/CSEC, and status/error state stays outside default result metric columns. Batch export/copy-all and xlsx export remain out of scope for the preflight.
    keywords:
      - batch table
      - two-row matrix
      - Hong Kong CSPF
      - result metrics
      - export deferred
    assertionStatus: superseded
    resolutionStatus: retired
    source: result_reports/summaries/236_summary-window-dialog-batch-viewport-arc.md
    supersededBy: result_reports/summaries/249_summary-batch-two-row-matrix-and-reference-parity-arc.md

  - type: decision
    topic: batch two-row matrix path completed and Hong Kong CSPF migration stabilized
    content: The batch two-row matrix foundation is complete through reports 237-248. Key results: two-row matrix layout accepted (blank read-only cells, no merge, no repeated Case); BatchMatrixSpec + per-cell cell_role(position) + TkTableController is the standard integration path; Hong Kong CSPF batch dialog migrated to BatchMatrixTable via HongKongCspfMatrixController adapter; row-per-case code preserved as fallback; MxN paste repeat-fill fixed in common helper; same-shape restore preserves widget continuity; copy/export parity uses existing table_clipboard and table_csv_export helpers.
    keywords:
      - batch table
      - two-row matrix
      - Hong Kong CSPF
      - BatchMatrixSpec
      - BatchMatrixTable
      - TkTableController
      - reference parity
    assertionStatus: verified
    source: result_reports/summaries/249_summary-batch-two-row-matrix-and-reference-parity-arc.md

  - type: decision
    topic: main notebook legacy vs batch newer stable path and BatchMatrixTable LOC containment
    content: The main notebook/tab path (Iso16358Tab) is a partially corrected legacy path with nested notebook, profile switch, and dynamic refit scheduler. The batch dialog/table path is a newer stable path with hidden-first sizing, internal viewport, and common table foundation. Apparent duplication between BatchCaseTable and BatchMatrixTable is shape-specific construction, not generic boilerplate; a base class would be premature with only two concrete shapes. BatchMatrixTable is at 422 LOC; the next responsibility addition must trigger helper extraction, not file growth.
    keywords:
      - main notebook
      - batch dialog
      - lifecycle
      - BatchMatrixTable
      - LOC containment
      - helper extraction
    assertionStatus: verified
    source: result_reports/summaries/249_summary-batch-two-row-matrix-and-reference-parity-arc.md

  - type: decision
    topic: schema-driven bin detail shell for cooling and heating profiles
    content: BinDetailPanel, BinTraceTable, and BinDetailGraph are schema-driven shells parameterized by a BinDetailSchema. COOLING_BIN_DETAIL_SCHEMA is the default; HEATING_HSPF_BIN_DETAIL_SCHEMA is used for Hong Kong HSPF. No cooling-specific hardcode remains in the UI shells. Future profile-specific detail traces should declare a schema rather than modify the shell.
    keywords:
      - BinDetailPanel
      - BinTraceTable
      - BinDetailSchema
      - schema-driven
      - HSPF detail
      - heating profile
    assertionStatus: verified
    source: result_reports/summaries/260_summary-hspf-detail-schema-window-lifecycle-arc-closeout.md

  - type: decision
    topic: side-effect-free nested notebook visible content measurement
    content: TkVisibleContentMeasurement._measure_nested_notebook() must never programmatically select hidden tabs. Main visible refit width and height both use replacement formulas that subtract the sticky container contribution and add back chrome + current visible tab contribution. Chrome estimates are one-time computed helpers per axis, not sticky target sizes. fit_visible_content() must not update root.minsize().
    keywords:
      - window measurement
      - side-effect-free
      - nested notebook
      - current-state replacement
      - chrome estimate
      - minsize
    assertionStatus: verified
    source: result_reports/summaries/260_summary-hspf-detail-schema-window-lifecycle-arc-closeout.md

  - type: decision
    topic: mvc separation of concerns for tkinter table surfaces
    content: MetricInputTable owns presentation rendering and visual invalid status marking. TkTableController + interaction_core.py manages grid controls like paste, undo stacks, and value synchronization. Section classes (e.g., IsoSasoT3Section) own positivity validation, required/optional grouping, and calculator dispatching.
    keywords:
      - MVC separation
      - MetricInputTable
      - TkTableController
      - IsoSasoT3Section
      - input validation
    assertionStatus: verified
    source: result_reports/summaries/314_summary-tkinter-table-controller-switch-arc-closeout.md

  - type: decision
    topic: code_checker as structure reference evidence
    content: code_checker is a structure reference evidence tool providing warning-first freshness checks against the HEAD commit, not a semantic hard gate or pre-commit checker. Strict quality guardrails are enforced by check_code_structure.py.
    keywords:
      - code_checker
      - reference map
      - warning-first
      - check_code_structure
    assertionStatus: verified
    source: result_reports/summaries/314_summary-tkinter-table-controller-switch-arc-closeout.md

  - type: decision
    topic: durable wording policy for active report count
    content: To prevent exact active report count mismatches, durable documentation (e.g., WORK_PLAN.md, project_log.md, report bodies) must use threshold status wording (e.g., count exceeds threshold) instead of writing exact numbers. The exact count is reported only in the final terminal output.
    keywords:
      - wording policy
      - active report count
      - threshold wording
      - terminal output
    assertionStatus: verified
    source: result_reports/summaries/314_summary-tkinter-table-controller-switch-arc-closeout.md

  - type: decision
    topic: Tkinter calculator active direction and PyQt/PySide6 UI transition
    content: PyQt calculator-only path is a read-only reference during the Tkinter calculator transition. Keep PyQt calculator reference only while EN14825 and AHRI 210/240 implementation still needs it. When reference need ends, PyQt calculator-only path may be retired. Predict and Train PyQt applications are separate from the calculator and remain retained for now. Future Predict/Train UI rewrite should target PySide6 and conform to shell/MVC boundary policy because current Predict/Train PyQt predates the shell/MVC structure. app_calculator_tk.py to app_calculator.py handover remains a separate future task.
    keywords:
      - predictor_v3
      - PyQt calculator
      - Tkinter calculator
      - PySide6
      - Predict Train UI
      - entrypoint handover
      - EN14825
      - AHRI 210/240
      - MVC boundary
    assertionStatus: verified
    source: result_reports/active/332_memory_seed_maintenance_execution.md (user-confirmed direction corrections after 331 audit)

  - type: decision
    topic: predictor_v3 source file owner boundary policy
    content: Before creating any new source file, the feature/domain owner boundary must be determined. Adding feature-specific flat files under broad folders (ui root, core root, sections, tests, tools) is forbidden. Calculator UI features likely to expand to multiple files must be isolated inside a feature package directory (e.g., apps/calculator/ui/en14825/) where model, adapter, table model, controller, and helper files are separated. Static checks in check_code_structure.py block flat feature file additions in ui root and sections/ as hard errors, and flag core helper, tests mega naming, and unregistered directories as warnings.
    keywords:
      - predictor_v3
      - source owner boundary
      - feature package
      - check_code_structure
      - flat file guard
    assertionStatus: verified
    source: result_reports/summaries/364_summary-pyqt-retirement-en14825-seer-owner-guard.md

  - type: decision
    topic: EN14825 GUI prefill defaults hierarchy
    content: EN14825 prefill defaults are user-editable UI inputs independent of config maximum/minimum validation limits. The core calculator receives the user-edited resolved values from the UI, not the config prefill default directly. Declared power is treated as an adapter/model-internal derived value (declared_power_w_for_core) for the core calculator and is never exposed in the UI as a table row.
    keywords:
      - predictor_v3
      - EN14825
      - prefill defaults
      - UI input
      - adapter boundary
    assertionStatus: verified
    source: result_reports/summaries/364_summary-pyqt-retirement-en14825-seer-owner-guard.md

  - type: decision
    topic: EN14825 unified config ownership
    content: EN14825 uses data/region_configs/en14825.json as its single active config owner with namespaced seer and scop sections. SEER calculation and UI defaults flow through config/adapter ownership, legacy EN14825 config and fallback paths are removed, and the calculator constructor accepts config_path.
    keywords:
      - predictor_v3
      - EN14825
      - unified config
      - config ownership
      - adapter defaults
    assertionStatus: verified
    source: result_reports/summaries/404_summary-en14825-config-point-contract-ui-workflow-closeout.md (covered reports 395-400)

  - type: decision
    topic: EN14825 SCOP point contract propagation
    content: EN14825 SCOP logical point availability is owned by scop.point_contract, including required, mapped, inactive, and threshold-only states. Core resolution is propagated through adapter and table-model boundaries to the UI, where unavailable points are blank static/read-only presentations rather than independent inputs.
    keywords:
      - predictor_v3
      - EN14825
      - SCOP
      - point contract
      - unavailable input
      - UI adapter boundary
    assertionStatus: verified
    source: result_reports/summaries/404_summary-en14825-config-point-contract-ui-workflow-closeout.md (covered reports 398, 401-402)

  - type: decision
    topic: EN14825 SCOP batch rebuild and snapshot state policy
    content: SCOP batch profile state separates draft common values, last valid active conditions, and case values. Invalid Apply preserves the active matrix while retaining the draft for correction; reopen builds the matrix from active conditions, restores visible case keys, and preserves hidden point values across condition-driven rebuilds. Parent section wiring remains a separate thin lifecycle slice.
    keywords:
      - predictor_v3
      - EN14825
      - SCOP batch
      - active conditions
      - dynamic matrix
      - snapshot restoration
    assertionStatus: verified
    source: result_reports/summaries/416_summary-en14825-batch-agent-change-gate-closeout.md (covered reports 409, 412)

  - type: procedure
    topic: staged agent change gate evidence policy
    content: Structure-impacting staged work is checked through tools/check_agent_change_gate.py --cached. Only staged active reports may supply the closed change_gate block, report selection is explicit when multiple reports are staged, local no-report exemptions require a literal allowed_paths manifest, and source size, hotspot growth, class count, whitespace, and code-map judgment are evaluated from Git index blobs rather than the working tree.
    keywords:
      - predictor_v3
      - agent change gate
      - staged report
      - Git index blob
      - task manifest
      - code map
    assertionStatus: verified
    source: result_reports/summaries/416_summary-en14825-batch-agent-change-gate-closeout.md (covered reports 413-415)

  - type: decision
    topic: AHRI 210/240 calculator UI and batch contract
    content: AHRI 210/240 exposes separate SEER2 and HSPF2 main/batch surfaces. HSPF2 A2 is capacity-only at the UI boundary, optional H42/H12/H22 state uses draft options plus last-valid active options and a superset case store, source normalization remains a main-UI contract, and HSPF2 batch exports only the primary HSPF2 result.
    keywords:
      - predictor_v3
      - AHRI 210/240
      - SEER2
      - HSPF2
      - batch
      - A2 capacity-only
    assertionStatus: verified
    source: result_reports/summaries/445_summary-ahri-calculator-ui-batch-lifecycle-closeout.md (covered reports 425-444)

  - type: decision
    topic: UI literal gate and BatchMatrix natural sizing policy
    content: New staged production UI width, min-size, geometry, and color literals are constrained by the UI magic-literal gate and semantic token owners. BatchMatrix leading columns use common tokens, vertical viewports preserve natural requested width, and batch dialog initial geometry derives from natural content with screen caps and parent centering rather than fixed geometry or profile min-size inflation.
    keywords:
      - predictor_v3
      - UI magic literal
      - BatchMatrix
      - natural content size
      - dialog geometry
      - design tokens
    assertionStatus: verified
    source: result_reports/summaries/445_summary-ahri-calculator-ui-batch-lifecycle-closeout.md (covered reports 437-443)

  - type: decision
    topic: calculator profile lifecycle and EN14825/AHRI detail ownership
    content: ISO16358, EN14825, and AHRI210240 profile tabs delegate visible-content measurement, scheduler, shell fit, suppression, named detail/nested/parent triggers, and scroll reset to ProfileVisibleContentLifecycleController. EN14825 SCOP/SEER and AHRI HSPF2/SEER2 detail rows are adapter-preserved, profile-formatted schemas rendered by the shared BinDetailPanel; production tabs are structure-gated against direct lifecycle primitive assembly.
    keywords:
      - predictor_v3
      - profile lifecycle controller
      - EN14825 detail
      - AHRI detail
      - BinDetailPanel
      - structure gate
    assertionStatus: verified
    source: result_reports/summaries/461_summary-en14825-ahri-detail-lifecycle-closeout.md (covered reports 449-461)

  - type: decision
    topic: calculator closeout token cleanup and structure helper boundaries
    content: Calculator production profiles launch without product-performance demo prefills, live docs/tests use app_calculator.py as the canonical launch wrapper, calculator cell backgrounds and cleaned-up UI presentation values route through semantic owners, and the next implementation is limited to a pure detail formatting coercion helper. Profile field mapping and precision remain profile-local; the matrix controller, batch dialog handle, and detail toggle candidates remain separate later decisions with their recorded design boundaries.
    keywords:
      - predictor_v3
      - calculator empty state
      - UI tokens
      - detail formatting helper
      - matrix controller
      - dialog handle
      - detail toggle
    assertionStatus: verified
    source: result_reports/summaries/480_summary-calculator-closeout-token-cleanup-structure-audit.md (covered reports 448, 462-475; active reports 476-479 retained)

  - type: decision
    topic: calculator helper batch detail lifecycle closeout
    content: The post-closeout calculator helper bundle is implemented and lifecycle-closed: detail formatting uses pure display coercion helpers while profile mapping and precision remain local; matrix batch recalculation uses BatchMatrixCalculationController; batch dialog state uses BatchDialogHandle; detail show/hide mechanics use DetailPanelVisibility; batch open buttons use `일괄 입력`; Hong Kong HSPF batch is implemented and visually smoked with HSPF/HSTL/HSEC results; the duplicate empty-state line was not present.
    keywords:
      - predictor_v3
      - detail formatting helper
      - BatchMatrixCalculationController
      - BatchDialogHandle
      - DetailPanelVisibility
      - Hong Kong HSPF
      - batch smoke
    assertionStatus: verified
    source: result_reports/summaries/490_summary-calculator-helper-batch-lifecycle-closeout.md (covered reports 476-479, 481-489)
    supersedes: result_reports/summaries/480_summary-calculator-closeout-token-cleanup-structure-audit.md active reports 476-479 retained status

  - type: decision
    topic: core package owner paths and root wrapper retirement
    content: Arc 7 and Arc 8 moved ML, predictor schema, mapping, common paths, calculator routing/adapters, and calculator standard engines under package owner paths; Arc 8.5 retired root compatibility wrappers and migrated active production code, legacy-reference imports, and tests to the owner paths directly.
    keywords:
      - predictor_v3
      - core owners
      - wrapper retirement
      - core/ml
      - core/predictor_schema
      - core/mapping
      - core/calculators
    assertionStatus: verified
    source: result_reports/summaries/536_summary-arc7-arc85-core-owner-wrapper-retirement-closeout.md (covered reports 517-535)

  - type: decision
    topic: PySide6 Predict schema mapping recovery
    content: Arc 9 recovered the PySide6 Predict path against package owners: schema/table models use `core/predictor_schema`, mapping/autofill uses `core/mapping` with app-side repository/controller boundaries, and row-to-ML/result adapters use schema metadata plus `core/ml` targets without changing ML behavior.
    keywords:
      - predictor_v3
      - PySide6
      - core/predictor_schema
      - core/mapping
      - core/ml
      - PredictWorkspace
    assertionStatus: verified
    source: result_reports/summaries/554_summary-arc9-pyside6-schema-legacy-ui-harvest-closeout.md (covered reports 537-553)

  - type: decision
    topic: legacy Train Predict ui retirement and token ownership
    content: Arc 9.1 retired the legacy Train/Predict `ui/` path and legacy PyQt tests; `ui_common.visual_tokens` is the active toolkit-neutral token owner for upcoming PySide6 visual parity work.
    keywords:
      - predictor_v3
      - legacy ui retirement
      - ui_common.visual_tokens
      - PySide6 visual parity
    assertionStatus: verified
    source: result_reports/summaries/554_summary-arc9-pyside6-schema-legacy-ui-harvest-closeout.md (covered reports 537-553)

  - type: decision
    topic: PySide6 visual table parity harvest location
    content: Arc 9.2 moved the project-specific PySide6 visual/table parity harvest from `docs/ui_ux/` to `docs/designs/2026-06-27-pyside6-visual-table-parity-harvest.md`; `docs/ui_ux/` remains the portable UI/UX rule set, while the moved harvest is an Arc 9.5 design/acceptance reference.
    keywords:
      - predictor_v3
      - PySide6
      - visual table parity
      - docs/designs
      - docs/ui_ux
      - Arc 9.5
    assertionStatus: verified
    source: result_reports/summaries/554_summary-arc9-pyside6-schema-legacy-ui-harvest-closeout.md (covered reports 537-553)
```

## Known Gaps

- This seed covers summary-compressed knowledge through the listed summaries; active reports introduced after the listed summaries are outside this seed.
- The seed does not reconstruct fine-grained evidence from individual archived reports.
- Open questions remain unresolved until an explicitly scoped implementation, verification, or policy task addresses them.

## Next Maintenance Rule

- seed는 summary lifecycle의 `Project Memory Seed Sync Judgment` 또는 명시적 memory maintenance task에서만 갱신한다.
- 일반 source/code/doc 작업 중에는 seed를 수정하지 않는다.
- 새 summary-level durable rule, error, open_question이 있으면 1~2개 entry만 추가한다.
- 기존 entry가 대체되면 `supersedes` 또는 `resolutionStatus`를 사용한다.
- 오래되었거나 덜 쓰이는 entry는 즉시 삭제하지 않고 `stale` / `superseded` / `retired` 후보로 표시한다.
- seed entry가 50개를 넘으면 memory maintenance audit 후보로 보고하고, 75개를 넘으면 반드시 유지보수를 수행한다.
- Do not retroactively modify individual reports or summaries to match this seed.
- Keep seed/index staging separate from any future backend import step.
