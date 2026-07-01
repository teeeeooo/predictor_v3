# Project Memory Seed Retired Entries - 2026-07

## Purpose

This archive preserves retired, stale, superseded, or resolved memory seed entries removed from the active `project_memory_seed.md` during July 2026 maintenance.

## Trace Policy

Entries are preserved with their original source traces. This archive is not the active memory staging document; use `result_reports/memory/project_memory_seed.md` for current recall.

## Retired Entries

```yaml
entries:
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
    topic: Arc 11 trainer execution foundation closeout
    content: Arc 11 trainer execution foundation is complete for the current automated scope: Train execution runs through Qt-free service contracts, a cooperative worker, controller-owned QThread lifecycle, and Train UI wiring; DEV-only Train E2E smoke uses the mock bundle and verifies Predict against the Train-produced model artifact. Manual GUI smoke, optional expensive real-core training smoke, and Data Mapping update execution remain follow-up work.
    keywords:
      - predictor_v3
      - Arc 11
      - Train execution
      - TrainController
      - TrainWorker
      - mock smoke
      - Data Mapping
    assertionStatus: verified
    source: result_reports/summaries/602_summary-arc10-arc11-worker-train-execution-closeout.md (covered reports 583-601)
```
