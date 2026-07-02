# Project Memory Seed

## Purpose

This document stages backend-neutral long-term memory candidates from existing summary reports. It is a compact decision index for current and future agent work, without defining or requiring any backend.

## Source Coverage

Active seed entries are maintained from source summaries and project log evidence through `result_reports/summaries/654_summary-calculator-maintenance-micro-polish-closeout.md`, plus explicit July 2026 memory maintenance reports. Retired, stale, superseded, resolved, and consolidated-away source entries remain preserved with source traces in `result_reports/memory/archive/project_memory_seed_retired_2026-07.md`.

## Scope and Non-goals

- Seed entries preserve durable decisions, procedures, verified failure states, and unresolved follow-ups that affect later work.
- Active entries are consolidated by owner boundary or current project state so this file stays usable as a compact first-read index.
- Entries derive from summary headings, scoped decision/risk/action sections, project_log evidence, and explicit memory maintenance tasks; archived individual report bodies were not reread for this pass.
- This document does not backfill individual reports, modify summaries or `project_log.md`, move archive files, or connect to a memory backend.
- Hypotheses and uncompleted work are represented as `open_question`, not confirmed decisions.

## Seed Entries

```yaml
entries:
  - type: procedure
    topic: agent workflow and lifecycle boundary
    content: AGENTS.md is the active lite entrypoint and AGENT_TASK_ROUTER.md is the route/gate map. Tracked-file work writes sequential result reports, summaries group arc/workstream evidence, project_log.md records only durable milestone decisions, and memory seed updates happen only through summary lifecycle or explicit maintenance. Durable docs use threshold wording for active report counts; exact counts belong only in terminal output.
    keywords:
      - predictor_v3
      - AGENTS.md
      - AGENT_TASK_ROUTER.md
      - result report
      - project_log
      - memory seed
      - lifecycle
    assertionStatus: verified
    source: consolidated from result_reports/summaries/011_summary-agent-rules-doc-workflow.md, 020_summary-active-report-doc-lifecycle.md, 140_summary-project-memory-delta-workflow.md, 153_summary-agent-workflow-memory-token-log-lifecycle.md, 314_summary-tkinter-table-controller-switch-arc-closeout.md, and 2026-07 memory maintenance reports

  - type: decision
    topic: architecture and source owner boundary
    content: Project-wide code quality requires thin app entrypoints, clean Model/Controller(or Service)/Shell(or Adapter)/View/Policy boundaries, explicit source owner packages before new files, and warning/reference-map evidence only as support. check_code_structure.py remains the stricter structure guard; staged structure work uses the agent change gate against Git index blobs.
    keywords:
      - predictor_v3
      - clean architecture
      - source owner boundary
      - code quality gate
      - check_code_structure
      - agent change gate
    assertionStatus: verified
    source: consolidated from result_reports/summaries/123_summary-calculator-tkinter-quality-xfail.md, 231_summary-architecture-uiux-boundary-and-window-refit-arc.md, 314_summary-tkinter-table-controller-switch-arc-closeout.md, 364_summary-pyqt-retirement-en14825-seer-owner-guard.md, and 416_summary-en14825-batch-agent-change-gate-closeout.md

  - type: decision
    topic: UI UX SSOT and table interaction contract
    content: docs/ui_ux is the portable UI/UX SSOT. Spreadsheet/table-shaped surfaces follow the toolkit-neutral table contract with Excel-like selection, edit mode, copy/paste, clear, undo, navigation, invalid feedback, selected-range fill paste, protected read-only/result cells, and MVC separation between MetricInputTable presentation, controller interaction state, and section-level validation/dispatch.
    keywords:
      - predictor_v3
      - docs/ui_ux
      - spreadsheet table
      - Excel-like
      - TkTableController
      - MetricInputTable
      - MVC separation
    assertionStatus: verified
    source: consolidated from result_reports/summaries/101_summary-calculator-ui-iso-hspf-stabilization.md, 114_summary-ui-ux-ssot-calculator-boundary.md, 165_summary-pyqt-retirement-tkinter-ui-matrix-rules.md, 180_summary-tkinter-calculator-ux-implementation-arc.md, 221_summary-post-main-table-window-refit-arc.md, 231_summary-architecture-uiux-boundary-and-window-refit-arc.md, and 314_summary-tkinter-table-controller-switch-arc-closeout.md

  - type: decision
    topic: window viewport and result-detail surface policy
    content: Calculator UI density may use metric sub-tabs inside standard tabs. Window/refit behavior preserves monitor/x placement, caps automatic height, uses scrollable overflow, avoids hidden-tab selection side effects, and routes detail/nested/profile refits through shared lifecycle helpers. Detail surfaces use schema-driven panels, header-included TSV copy, CSV export where appropriate, outdoor-temperature graph axes when available, and natural BatchMatrix sizing rather than fixed geometry.
    keywords:
      - predictor_v3
      - Tkinter calculator
      - viewport
      - detail panel
      - BinDetailSchema
      - BatchMatrixTable
      - natural sizing
    assertionStatus: verified
    source: consolidated from result_reports/summaries/180_summary-tkinter-calculator-ux-implementation-arc.md, 195_summary-tkinter-detail-panel-copy-graph-arc.md, 200_summary-window-geometry-viewport-ui-pivot-prep-arc.md, 221_summary-post-main-table-window-refit-arc.md, 249_summary-batch-two-row-matrix-and-reference-parity-arc.md, 260_summary-hspf-detail-schema-window-lifecycle-arc-closeout.md, 445_summary-ahri-calculator-ui-batch-lifecycle-closeout.md, and 480_summary-calculator-closeout-token-cleanup-structure-audit.md

  - type: decision
    topic: calculator standard and config ownership
    content: ISO 16358, KS C 9306, AS/NZS compatibility, EN14825, and AHRI 210/240 remain separate calculator responsibilities. Region config is shared static data interpreted by each calculator/profile owner; routing is explicit by calculator_id/profile resolver; EN14825 owns its unified config and SCOP point contract; AHRI keeps separate SEER2/HSPF2 UI and batch contracts. Core formulas, config semantics, profile IDs, fixtures, and public result contracts must not be blended across standards.
    keywords:
      - predictor_v3
      - calculator standard
      - region config
      - profile routing
      - ISO16358
      - KS C 9306
      - EN14825
      - AHRI 210/240
    assertionStatus: verified
    source: consolidated from result_reports/summaries/033_summary-calculator-architecture-ks-profile-dispatch.md, 054_summary-calculator-ui-iso-separation.md, 364_summary-pyqt-retirement-en14825-seer-owner-guard.md, 404_summary-en14825-config-point-contract-ui-workflow-closeout.md, 416_summary-en14825-batch-agent-change-gate-closeout.md, and 445_summary-ahri-calculator-ui-batch-lifecycle-closeout.md

  - type: decision
    topic: calculator envelope and ML boundary
    content: Calculator result envelopes and ML/ranking adapters are separate from calculator public APIs and region config. CalculatorInputEnvelope uses calculator_profile_id, standard, region, mode, metric, measured_inputs, and options; envelope adapters fail fast on unit mismatches and do not perform UI table conversions; ranking consumes RankingCandidateEnvelope rather than raw calculator output.
    keywords:
      - predictor_v3
      - CalculatorInputEnvelope
      - calculator envelope
      - ML adapter
      - ranking
      - unit conversion
    assertionStatus: verified
    source: consolidated from result_reports/summaries/081_summary-calculator-ui-v1-audit-2-3.md, 082_summary-envelope-adapter-four-stage-chain.md, and 101_summary-calculator-ui-iso-hspf-stabilization.md

  - type: error
    topic: ISO16358 HSPF fixture and minus7 trap
    content: ISO16358-2 HSPF official exact fixtures are settled with no active production xfails. The known trap was applying extended minus7 frost factors directly to measured 2 degree Celsius values; the corrected route applies measured-to-default conversion before the extension factor. Obsolete pure-route formula experiments are retired and should not be revived as production evidence.
    keywords:
      - predictor_v3
      - ISO16358-2 HSPF
      - minus7
      - golden fixture
      - xfail
    assertionStatus: verified
    source: consolidated from result_reports/summaries/101_summary-calculator-ui-iso-hspf-stabilization.md and 132_summary-xfail-archive-pyqt-tkinter-stabilization.md

  - type: open_question
    topic: ASNZS case3 full-dump parity
    content: Historical AS/NZS case3 full-dump exact parity remains deferred until matching workbook or full component-row reference data is available.
    keywords:
      - predictor_v3
      - ASNZS
      - case3
      - external reference
    assertionStatus: observed
    source: result_reports/summaries/054_summary-calculator-ui-iso-separation.md; result_reports/summaries/132_summary-xfail-archive-pyqt-tkinter-stabilization.md

  - type: decision
    topic: calculator application and UI boundary
    content: Calculator UI orchestration routes through application usecases, adapters, shared lifecycle controllers, and thin UI shims. EN14825/AHRI detail rows use adapter-preserved, profile-formatted schemas rendered by shared detail panels; matrix batch recalculation, batch dialog handles, detail visibility, and helper extraction are preferred over growing section-local lifecycle code.
    keywords:
      - predictor_v3
      - calculator application boundary
      - usecase adapter
      - profile lifecycle controller
      - batch dialog
      - detail panel
    assertionStatus: verified
    source: consolidated from result_reports/summaries/461_summary-en14825-ahri-detail-lifecycle-closeout.md, 490_summary-calculator-helper-batch-lifecycle-closeout.md, and 622_summary-arc11-arc12-boundary-closeout.md

  - type: decision
    topic: KOREA calculator notebook sub-arc closeout
    content: KOREA is a top-level Tk calculator tab with CSPF/HSPF single calculation, midpoint guide tables, batch dialogs, and official-result detail views. Midpoint guide values are UI design helpers, not official result dict, batch output, or detail view contract fields; recommended Mid capacity reports the rated test-point capacity input needed to place tc at the recommended midpoint, not the raw load. KS C 9306 formula/config/profile/public result contracts remain unchanged.
    keywords:
      - predictor_v3
      - KOREA calculator
      - KS C 9306
      - midpoint guide
      - batch
      - detail
    assertionStatus: verified
    source: result_reports/summaries/644_summary-korea-calculator-subarc-closeout.md; result_reports/summaries/654_summary-calculator-maintenance-micro-polish-closeout.md

  - type: decision
    topic: KS C 9306 HSPF official oracle correction
    content: KS C 9306 HSPF official total and bin-level oracle passes without direct bin-energy override or arbitrary correction factors. For round_test_values=true, non-max frost curves use rounding-aware effective defrost/no-frost ratios from rounded max defrost anchors: capacity 4165/4665 and power 1604/1700. PRH Pheater * frunning remains deferred for future auxiliary-heater models and is non-impact for the current no-aux-heater oracle.
    keywords:
      - predictor_v3
      - KS C 9306
      - HSPF
      - official oracle
      - frost effective ratio
      - round_test_values
      - PRH
    assertionStatus: verified
    source: result_reports/summaries/651_summary-ks-hspf-official-oracle-closeout.md

  - type: decision
    topic: Train Predict PySide6 boundary
    content: app_calculator.py is the canonical Tkinter calculator launch boundary. Train and Predict production work belongs to PySide6 under apps/train/ and apps/predict/ with package-owner imports, core/predictor_schema and core/mapping boundaries, ui_common.visual_tokens, and docs/designs as the PySide6 visual/table parity reference location.
    keywords:
      - predictor_v3
      - app_calculator.py
      - Tkinter calculator
      - PySide6
      - Train Predict
      - package owners
    assertionStatus: verified
    source: consolidated from result_reports/summaries/516_summary-architecture-reset-pyside6-foundation-closeout.md, 536_summary-arc7-arc85-core-owner-wrapper-retirement-closeout.md, and 554_summary-arc9-pyside6-schema-legacy-ui-harvest-closeout.md

  - type: decision
    topic: Predict Train execution boundary
    content: Predict/Train execution keeps UI/runtime-neutral usecases and execution ports separate from PySide adapters. Arc 9.5 accepted the unified case table direction; Arc 10 put prediction behind worker/progress/cancel boundaries; Arc 11 corrected Train execution through a killable process runner adapter and Predict execution through an isolated runner lifecycle.
    keywords:
      - predictor_v3
      - Predict execution
      - Train execution
      - unified case table
      - worker progress
      - hexagonal boundary
    assertionStatus: verified
    source: consolidated from result_reports/summaries/582_summary-arc95-unified-table-manual-smoke-closeout.md, 602_summary-arc10-arc11-worker-train-execution-closeout.md, and 622_summary-arc11-arc12-boundary-closeout.md

  - type: decision
    topic: Arc 13 ML feature catalog closeout
    content: Arc 13 completed the ML feature catalog migration. config/ml/features.csv is the ML feature contract; ml_name is both raw training header and internal ML name; constants, predictor ML-visible columns, one-hot groups, training header guards, and inference zero-fill project from the catalog without a train-header alias layer.
    keywords:
      - predictor_v3
      - Arc 13
      - feature catalog
      - features.csv
      - ml_name
      - zero fill
    assertionStatus: verified
    source: result_reports/summaries/633_summary-arc13-feature-catalog-closeout.md

  - type: decision
    topic: Arc 13.5 feature catalog editor direction
    content: Arc 13.5 should make app_train.py the default Feature Catalog viewer/editor workflow. config/ml/features.csv remains the storage and contract file. Direct CSV editing in Excel or Numbers is not the default user workflow; export design should evaluate an Excel/Numbers-friendly encoding policy such as UTF-8-SIG.
    keywords:
      - predictor_v3
      - Arc 13.5
      - Feature Catalog
      - app_train.py
      - features.csv
      - UTF-8-SIG
    assertionStatus: verified
    source: project_log.md 2026-07-01 Arc 13.5 feature catalog editor direction; result_reports/active/635_planning-doc-sync-arc13-5-feature-catalog-editor.md
```

## Known Gaps

- This active seed is intentionally compact and does not contain every historical memory candidate.
- Retired/stale/superseded/resolved entries and source traces remain in `result_reports/memory/archive/project_memory_seed_retired_2026-07.md`.
- Consolidated source entries are archived rather than deleted, with the active replacement topic recorded in the archive.
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
