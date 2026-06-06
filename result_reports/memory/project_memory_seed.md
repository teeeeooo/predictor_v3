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
    assertionStatus: verified
    source: result_reports/summaries/132_summary-xfail-archive-pyqt-tkinter-stabilization.md (covered reports 124-131; PyQt / Tkinter Direction)

  - type: open_question
    topic: deployment and PyQt validation follow-up
    content: Windows PyInstaller size measurement and Python 3.12 or 3.11 or Windows PyQt smoke validation remain pending follow-up work.
    keywords:
      - predictor_v3
      - PyInstaller
      - PyQt
      - validation
    assertionStatus: observed
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
    assertionStatus: verified
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
    resolutionStatus: resolved
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
    assertionStatus: verified
    source: result_reports/summaries/236_summary-window-dialog-batch-viewport-arc.md
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
