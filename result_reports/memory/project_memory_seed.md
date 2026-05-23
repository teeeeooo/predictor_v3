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
```

## Known Gaps

- This seed covers summary-compressed knowledge through reports `131`; active reports introduced after the listed summaries are outside this seed.
- The seed does not reconstruct fine-grained evidence from individual archived reports.
- Open questions remain unresolved until an explicitly scoped implementation, verification, or policy task addresses them.

## Next Maintenance Rule

- Add or supersede seed entries through a separate authorized memory document task, citing source reports or summaries in every changed entry.
- Do not retroactively modify individual reports to match this seed.
- Keep seed/index staging separate from summary/archive lifecycle operations and from any future backend import step.
