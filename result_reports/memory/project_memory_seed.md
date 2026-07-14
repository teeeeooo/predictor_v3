# Project Memory Seed

## Purpose

This document is a backend-neutral current memory bank for long-running,
branching project work. It preserves a compact set of durable decisions,
invariants, resume points, repeated errors, and open questions.

## Source Coverage

Active entries draw from owner docs, project-log evidence, durable result
records, and pre-cutover summaries through the clean/hexagonal desktop
refactor. Retired,
superseded, and resolved entries remain preserved with source traces under
`result_reports/memory/archive/`.

## Scope and Non-goals

- Seed entries preserve durable decisions, procedures, verified failure states, and unresolved follow-ups that affect later work.
- Active entries are consolidated by owner boundary or current project state so this file stays usable as a compact first-read index.
- Entries derive from Memory Review Gate decisions, owner docs, scoped durable
  evidence, and project-log decisions; legacy report bodies are not broad-read.
- This document does not backfill or rewrite result records, summaries,
  `project_log.md`, or legacy evidence.
- Hypotheses and uncompleted work are represented as `open_question`, not confirmed decisions.

## Seed Entries

```yaml
entries:
  - type: procedure
    topic: agent workflow and lifecycle boundary
    content: AGENTS.md is the lite entrypoint and AGENT_TASK_ROUTER.md is the route map. Ordinary tracked-file work does not create reports. Durable compact records are limited to contract/policy/migration/manual-evidence and non-obvious regression triggers, use date-based final paths plus REPORT_INDEX, and are committed with their source changes. Memory Review replaces report-count lifecycle cleanup and is required for new records, milestone/branch closeout, explicit handoff, and return to a long-paused workstream. Pre-cutover evidence is read-only under result_reports/legacy/archive and result_reports/legacy/summaries; legacy bodies preserve historical paths and commands.
    keywords:
      - predictor_v3
      - AGENTS.md
      - AGENT_TASK_ROUTER.md
      - result report
      - result record
      - project_log
      - memory seed
      - memory review
      - report index
    assertionStatus: verified
    source: result_reports/records/2026-07/2026-07-10-agent-harness-report-policy-bootstrap.md; result_reports/records/2026-07/2026-07-10-result-report-legacy-migration.md; docs/designs/2026-07-10-agent-harness-report-lifecycle-redesign.md

  - type: decision
    topic: architecture and source owner boundary
    content: Project-wide code quality requires thin app entrypoints, clean Model/Controller(or Service)/Shell(or Adapter)/View/Policy boundaries, explicit source owner packages before new files, and targeted sibling/owner/reuse search as warning-first evidence. check_code_structure.py remains the stricter structure guard; staged structure work uses the agent change gate against Git index blobs.
    keywords:
      - predictor_v3
      - clean architecture
      - source owner boundary
      - code quality gate
      - check_code_structure
      - agent change gate
    assertionStatus: verified
    source: consolidated from result_reports/legacy/summaries/123_summary-calculator-tkinter-quality-xfail.md, 231_summary-architecture-uiux-boundary-and-window-refit-arc.md, 314_summary-tkinter-table-controller-switch-arc-closeout.md, 364_summary-pyqt-retirement-en14825-seer-owner-guard.md, and 416_summary-en14825-batch-agent-change-gate-closeout.md; result_reports/records/2026-07/2026-07-10-code-map-and-read-budget-retirement.md

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
    source: consolidated from result_reports/legacy/summaries/101_summary-calculator-ui-iso-hspf-stabilization.md, 114_summary-ui-ux-ssot-calculator-boundary.md, 165_summary-pyqt-retirement-tkinter-ui-matrix-rules.md, 180_summary-tkinter-calculator-ux-implementation-arc.md, 221_summary-post-main-table-window-refit-arc.md, 231_summary-architecture-uiux-boundary-and-window-refit-arc.md, and 314_summary-tkinter-table-controller-switch-arc-closeout.md

  - type: decision
    topic: Calculator table family architecture
    content: Active Tk Calculator tables use three explicit families: Editable Matrix keeps existing models/controllers, Compact Result Grid owns small fixed read-only results, and Scrollable Data Table retains Treeview only for large detail data through the shared style adapter. All active single/common/profile and batch matrices consume shared grid primitives; fixed ISO/SASO/Brazil/Korea/SCOP results use compact primitives; BinTraceTable is the sole active Treeview. Profile schemas, status meaning, calculations, and export documents remain local. Every active Single result exposes Copy/Export CSV through a presentation helper while native result owners keep payload shape; SCOP composes its payload from active visible climate surfaces rather than the hidden compatibility ResultPanel. ISO/KS Single surfaces reserve their final table structure with non-exportable pending placeholders; validation placeholders are invalid, while successful values restore calculated or Brazil pass/fail presentation in place. SASO partial results retain both exportable rows, keep the required row calculated, and mark only the optional error row's non-identity cells invalid before in-place recovery. Nested Notebook lifecycle measures and preserves real chrome before applying the selected child's client allocation, then refreshes the scrollregion and fits the shell; measurement snapshots do not select or configure widgets. AHRI/Korea visibility uses Tk widget identity.
    keywords:
      - predictor_v3
      - Calculator table
      - Editable Matrix
      - Compact Result Grid
      - Scrollable Data Table
      - Tk visual policy
      - ISO ISEER
      - BinTraceTable
    assertionStatus: verified
    source: docs/designs/2026-07-12-calculator-table-architecture-design.md; result_reports/records/2026-07/2026-07-12-calculator-table-foundation.md; result_reports/records/2026-07/2026-07-12-calculator-table-slice6.md; result_reports/records/2026-07/2026-07-12-calculator-result-actions-notebook-correction.md; result_reports/records/2026-07/2026-07-12-calculator-scop-visible-export-correction.md; result_reports/records/2026-07/2026-07-12-calculator-table-architecture-merge-closeout.md; result_reports/records/2026-07/2026-07-13-calculator-initial-result-and-nested-sizing.md; result_reports/records/2026-07/2026-07-13-calculator-nested-placeholder-audit-correction.md; result_reports/records/2026-07/2026-07-13-saso-partial-row-tone-correction.md

  - type: decision
    topic: window viewport and result-detail surface policy
    content: Calculator startup is hidden-first and settles geometry before the first show. Main content and batch tables use scrollable overflow, including horizontal batch scrolling and Shift+wheel, while parent-centered dialogs preserve off-primary monitor coordinates. Qt Train/Predict shells share an available-screen policy that caps and centers initial size without assuming the primary display. Detail surfaces continue to use schema-driven panels, header-included TSV copy, CSV export where appropriate, and natural BatchMatrix sizing rather than fixed geometry.
    keywords:
      - predictor_v3
      - Tkinter calculator
      - viewport
      - horizontal scroll
      - multi-monitor
      - window policy
      - detail panel
      - BinDetailSchema
      - BatchMatrixTable
      - natural sizing
    assertionStatus: verified
    source: consolidated from result_reports/legacy/summaries/180_summary-tkinter-calculator-ux-implementation-arc.md, 195_summary-tkinter-detail-panel-copy-graph-arc.md, 200_summary-window-geometry-viewport-ui-pivot-prep-arc.md, 221_summary-post-main-table-window-refit-arc.md, 249_summary-batch-two-row-matrix-and-reference-parity-arc.md, 260_summary-hspf-detail-schema-window-lifecycle-arc-closeout.md, 445_summary-ahri-calculator-ui-batch-lifecycle-closeout.md, and 480_summary-calculator-closeout-token-cleanup-structure-audit.md; result_reports/records/2026-07/2026-07-11-clean-hex-mvc-ui-refactor.md

  - type: decision
    topic: calculator standard and config ownership
    content: ISO 16358, KS C 9306, AS/NZS compatibility, EN14825, and AHRI 210/240 remain separate calculator responsibilities. Region config is shared static data interpreted by each calculator/profile owner; routing is explicit by calculator_id/profile resolver and profile resources resolve statically without repo-cwd dependence or runtime discovery. EN, ISO, and KS keep stable public facades over standard-local private config, point, performance, seasonal, and result owners; facade config replacement shares the same context object. ISO HSPF supports only the explicit `iso16358_2_hspf` profile, ISO CSPF profile selectors are strict enums, and KS rejects ISO `cspf_test_profile` schema. Brazil compliance remains capability-owned composite policy; AS/NZS remains disabled compatibility evidence. Cross-standard interpolation/division is intentionally not commonized without identical units, rounding, boundaries, and exceptions. AHRI keeps separate SEER2/HSPF2 UI and batch contracts. AHRI production HSPF2 owners are variable-capacity, dual-stage, and triple-capacity-northern; the separate v2 seasonal engine and public v2 method are retired, while active aliases normalize through a neutral public-point owner. Existing user-confirmed expected results are official-calculator golden while deep-result fingerprints are structural characterization. The official multi-capacity synthetic evidence fixtures live under tests/fixtures/ahri210240/official_calculator/ with separate M/M1 raw results, full input/result raw-field projections, normalized seasonal/bin/cutout/state evidence, and provenance. Dual-stage k1/k2 are performance curve groups; load-capacity regimes use only the three raw building-load/low-high-capacity comparisons, while compressor availability and auxiliary heat are independent per-bin state projections. Triple Northern alone uses `activated_operating_cases` for raw official case_name values. The fixture oracle is AHRI 210/240 (2023) Appendix M/M1 evidence; AHRI 210/240-2026 final-formula use requires a separate standards audit. Their raw CSVs do not expose explicit bin temperatures/hours, and calculator version remains not displayed. Core formulas, config semantics, profile IDs, fixtures, and public result contracts must not be blended across standards; unsupported or cross-standard schemas fail fast rather than selecting another engine.
    keywords:
      - predictor_v3
      - calculator standard
      - region config
      - profile routing
      - ISO16358
      - KS C 9306
      - EN14825
      - AHRI 210/240
      - multi-capacity audit
      - cutout delta
    assertionStatus: verified
    source: consolidated from result_reports/legacy/summaries/033_summary-calculator-architecture-ks-profile-dispatch.md, 054_summary-calculator-ui-iso-separation.md, 364_summary-pyqt-retirement-en14825-seer-owner-guard.md, 404_summary-en14825-config-point-contract-ui-workflow-closeout.md, 416_summary-en14825-batch-agent-change-gate-closeout.md, and 445_summary-ahri-calculator-ui-batch-lifecycle-closeout.md; docs/designs/2026-07-12-ahri-seer2-hspf2-core-refactor-design.md; docs/designs/2026-07-13-all-standards-core-refactor-design.md; result_reports/records/2026-07/2026-07-13-all-standards-core-refactor-closeout.md; result_reports/records/2026-07/2026-07-13-silent-fallback-retirement.md; result_reports/records/2026-07/2026-07-12-ahri-core-refactor-contract-lock.md; result_reports/records/2026-07/2026-07-12-ahri-multicapacity-official-fixtures.md; result_reports/records/2026-07/2026-07-12-ahri-multicapacity-audit-correction.md; result_reports/records/2026-07/2026-07-12-ahri-multicapacity-state-schema-correction.md

  - type: decision
    topic: calculator strict selector and retired-surface boundary
    content: Explicit invalid calculator selectors fail fast rather than selecting another calculation. ISO CSPF allows measured/declared building load and capacity_linear/iso_boundary_eer power interpolation while preserving omitted-key defaults; facade reassignment uses the same context allowlist. KS CSPF requires its non-empty point/derived schema, measured/declared load source, and ks_intersection; every default rule requires a non-self source and finite positive capacity/power factors. KS HSPF requires ks_c_9306_hspf, required points, unique finite-numeric `tj`/`nj` bin rows, and a finite positive rated_cooling_capacity config load line before any user load-line override is considered. AHRI HSPF2 config/context/facade contains no v2 bin/temperature/constants surface; variable public alias normalization is exactly A_Full to A2 and accepts only required H01/H11/H1N/H2Int/H32/A2 plus optional H12/H22/H42. Full-schema H2V and B2/C2/D2/E2 are rejected before H12/H22 fallback, while dual/triple aliases remain product-local. Derived H12 accepts only normalized split or packaged unit types and rejects conflicts.
    keywords:
      - predictor_v3
      - silent selector
      - strict config
      - ISO CSPF
      - KS C 9306
      - AHRI HSPF2
      - public alias
      - unit type
    assertionStatus: verified
    source: result_reports/records/2026-07/2026-07-13-all-standards-final-audit-correction.md; result_reports/records/2026-07/2026-07-13-remaining-silent-fallback-closure.md; result_reports/records/2026-07/2026-07-13-ahri-variable-exact-point-allowlist.md

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
    source: consolidated from result_reports/legacy/summaries/081_summary-calculator-ui-v1-audit-2-3.md, 082_summary-envelope-adapter-four-stage-chain.md, and 101_summary-calculator-ui-iso-hspf-stabilization.md

  - type: decision
    topic: Brazil CSPF composite capability boundary
    content: Brazil CSPF is a core-owned composite capability `brazil.cspf_compliance`, not a generic region/metric UI route or SASO optional-point variant. The fixed Brazil profile uses the ISO 16358 T1 required-only resolver with Brazil bins; the handler independently runs 3-point and 2-point ISO calculations, preserves raw results, derives exact CSPF/rule values from diagnostics, and owns final Rule 1 OR Rule 2 compliance. Application single and batch surfaces call the composite capability once per case and only format the returned domain result.
    keywords:
      - predictor_v3
      - Brazil CSPF
      - brazil.cspf_compliance
      - capability allowlist
      - ISO T1
      - Rule 1
      - Rule 2
      - batch calculator
    assertionStatus: verified
    source: result_reports/records/2026-07/2026-07-11-brazil-cspf-compliance.md

  - type: decision
    topic: Brazil CSPF batch package ownership
    content: Brazil CSPF batch UI remains a feature-local composition over shared batch infrastructure. The package exposes schema/spec and row result contracts separately from the Brazil application row adapter, while Tk section/view and dialog/snapshot composition remain UI owners. The package preserves the former module's public imports; schema and row adapter stay free of Tk dependencies, and Brazil-specific keys do not move into common batch code.
    keywords:
      - predictor_v3
      - Brazil CSPF
      - batch package
      - schema owner
      - row adapter
      - Tk section
      - dialog composition
      - public import compatibility
    assertionStatus: verified
    source: result_reports/records/2026-07/2026-07-11-brazil-cspf-batch-package-split.md

  - type: decision
    topic: Brazil CSPF UI presentation and batch result boundary
    content: Brazil single-result detail presentation consumes application-provided 3-point/2-point bin sources and summaries through the shared BinDetailPanel and DetailPanelVisibility lifecycle; Rule 1/Rule 2 are rendered from core-owned left/right/passed values in a cell-rendered table. The Brazil batch UI exposes only the nine compliance result columns and omits 2-point CSTL/CSEC and Row Status from display/export/snapshot while controller-only PENDING/ERROR/OK state, single results, raw results, and core formulas remain unchanged.
    keywords:
      - predictor_v3
      - Brazil CSPF
      - BinDetailPanel
      - DetailPanelVisibility
      - Rule table
      - batch result columns
      - CSTL
      - CSEC
      - Row Status
    assertionStatus: verified
    source: result_reports/records/2026-07/2026-07-11-brazil-cspf-ui-polish.md; result_reports/records/2026-07/2026-07-11-brazil-cspf-ui-export-correction.md

  - type: decision
    topic: Brazil CSPF sectioned export contract
    content: Brazil single Copy/CSV/as_text valid output uses one pure Brazil-local export document with independent Result, Rule, and Final sections. Tk clipboard, file-dialog, and CSV writing are separate feature adapters; Result and Rule headers are never reused across row schemas. Empty/invalid states retain the existing Status export fallback, and table_export_data remains result-table-only compatibility output.
    keywords:
      - predictor_v3
      - Brazil CSPF
      - sectioned export
      - clipboard TSV
      - variable-width CSV
      - Result section
      - Rule section
      - Final section
      - export adapter
    assertionStatus: verified
    source: result_reports/records/2026-07/2026-07-11-brazil-cspf-export-section-schema.md; result_reports/records/2026-07/2026-07-11-brazil-cspf-ui-export-correction.md

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
    source: consolidated from result_reports/legacy/summaries/101_summary-calculator-ui-iso-hspf-stabilization.md and 132_summary-xfail-archive-pyqt-tkinter-stabilization.md

  - type: open_question
    topic: ASNZS case3 full-dump parity
    content: Historical AS/NZS case3 full-dump exact parity remains deferred until matching workbook or full component-row reference data is available.
    keywords:
      - predictor_v3
      - ASNZS
      - case3
      - external reference
    assertionStatus: observed
    source: result_reports/legacy/summaries/054_summary-calculator-ui-iso-separation.md; result_reports/legacy/summaries/132_summary-xfail-archive-pyqt-tkinter-stabilization.md

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
    source: consolidated from result_reports/legacy/summaries/461_summary-en14825-ahri-detail-lifecycle-closeout.md, 490_summary-calculator-helper-batch-lifecycle-closeout.md, and 622_summary-arc11-arc12-boundary-closeout.md

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
    source: result_reports/legacy/summaries/644_summary-korea-calculator-subarc-closeout.md; result_reports/legacy/summaries/654_summary-calculator-maintenance-micro-polish-closeout.md

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
    source: result_reports/legacy/summaries/651_summary-ks-hspf-official-oracle-closeout.md

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
    source: consolidated from result_reports/legacy/summaries/516_summary-architecture-reset-pyside6-foundation-closeout.md, 536_summary-arc7-arc85-core-owner-wrapper-retirement-closeout.md, and 554_summary-arc9-pyside6-schema-legacy-ui-harvest-closeout.md

  - type: decision
    topic: Predict Train execution boundary
    content: Predict and Train build runtime-neutral DTOs, usecases, and execution ports in explicit composition roots, then inject concrete PySide runners. Controllers do not import concrete adapters or own toolkit lifecycle. Predict retains the unified case table and worker/progress/cancel boundary; its controller retains active run case IDs, while the usecase and result mapper convert only still-running rows to terminal errors after an infrastructure failure and summarize actual session states. The Train QProcess adapter owns process signals, cancellation, and cleanup. app_train.py and app_predict.py remain separate thin entrypoints.
    keywords:
      - predictor_v3
      - Predict execution
      - Train execution
      - unified case table
      - worker progress
      - hexagonal boundary
    assertionStatus: verified
    source: consolidated from result_reports/legacy/summaries/582_summary-arc95-unified-table-manual-smoke-closeout.md, 602_summary-arc10-arc11-worker-train-execution-closeout.md, and 622_summary-arc11-arc12-boundary-closeout.md; result_reports/records/2026-07/2026-07-11-clean-hex-mvc-ui-refactor.md

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
    source: result_reports/legacy/summaries/633_summary-arc13-feature-catalog-closeout.md

  - type: decision
    topic: ML feature catalog compatibility boundary
    content: config/ml/features.csv and core/ml/feature_catalog remain the ML feature/target/one-hot compatibility contract. The superseded Arc 13.5 Qt Feature Catalog Manager UI is retired because Arc 15 Data Definition is the active Train/Admin schema surface. No ML capability was added; catalog fingerprint and fixed-artifact numeric compatibility guards remain required for future ML contract changes.
    keywords:
      - predictor_v3
      - ML feature catalog
      - Feature Catalog UI retired
      - Data Definition
      - features.csv
      - catalog fingerprint
      - model compatibility
    assertionStatus: verified
    source: result_reports/legacy/summaries/633_summary-arc13-feature-catalog-closeout.md; result_reports/legacy/summaries/673_summary-arc13-5a-feature-catalog-manager-closeout.md; result_reports/records/2026-07/2026-07-11-clean-hex-mvc-ui-refactor.md

  - type: decision
    topic: Arc 13.5R Predict Schema Catalog v2 owner switch
    content: Predict core column assembly projects from config/predict/schema.csv through the Predict Schema Catalog v2 projection. Feature Catalog remains the ML feature/target/one-hot compatibility source; status/message stay adapter-local virtual columns; mapping/source/mapping_key are legacy compatibility projection fields, while mapping_entity/mapping_attribute/trigger_column/rule_id are the generic semantic schema fields. Schema, column, and rule changes remain restart-required.
    keywords:
      - predictor_v3
      - Arc 13.5R
      - Predict Schema Catalog v2
      - config/predict/schema.csv
      - COLUMNS
      - mapping_entity
      - restart required
    assertionStatus: verified
    source: result_reports/legacy/summaries/687_summary-arc13-5r-arc14b-data-mapping-foundation-closeout.md

  - type: decision
    topic: Arc 14 Data Mapping foundation state
    content: Mapping Entity / Master Data is a generic Qt-free core model separate from Predict Schema Catalog v2. Data Mapping Manager defaults to runtime mapping.json data and now supports user-facing draft projection, validation, editable row CRUD, validation-gated save with backup/temp/atomic replace, dirty reload confirmation, JSON export, and generated XLSX read-only snapshot export. Train/Admin Mapping/Data Foundation Phase 1 Slices 1A–1D plus the dynamic payload/type and hidden-payload persistence corrections are complete for repository-automated scope, the final audit is approved, and PR #14 is the merge target. Phase 2 begins only from merged main on a separate branch after separate instruction. The repository-only `tests/fixtures/mapping/mapping_runtime_equivalent.json` is the exact deterministic projection of the approved legacy bootstrap and is shared by populated Data Mapping and Predict integration tests; it is never installed as `data/mapping.json`. Definition-backed dynamic mapping attributes carry type/required metadata into editor validation and persistence across simple keyed groups, Refrigerant/Expansion option payloads, and ODU Cond Specs; boolean values persist as canonical JSON booleans and every mapping number must be finite. Undeclared runtime payload remains hidden from editor/review schema but is preserved from its current row backing data across unrelated Save/reload and key rename, while visible fields overlay canonical values and row deletion removes the payload. Non-identity attributes never join condenser identity. row_key remains canonical row identity, key_attribute remains future import/export metadata, and active controls management visibility/eligibility rather than structural validation.
    keywords:
      - predictor_v3
      - Arc 14
      - Data Mapping Manager
      - Mapping Entity
      - mapping.json
      - row_key
      - key_attribute
      - active
    assertionStatus: verified
    source: result_reports/legacy/summaries/687_summary-arc13-5r-arc14b-data-mapping-foundation-closeout.md; result_reports/legacy/summaries/700_summary-arc14b-runtime-data-mapping-crud-design-closeout.md; result_reports/legacy/summaries/710_summary-arc14b-crud-cascade-xlsx-prearc15-closeout.md; result_reports/records/2026-07/2026-07-14-train-admin-mapping-foundation-slice-1b.md; result_reports/records/2026-07/2026-07-14-train-admin-mapping-foundation-slice-1c.md; result_reports/records/2026-07/2026-07-14-train-admin-mapping-data-foundation-phase-1-closeout.md; result_reports/records/2026-07/2026-07-14-train-admin-mapping-data-foundation-audit-correction.md; result_reports/records/2026-07/2026-07-14-train-admin-mapping-data-foundation-persistence-correction.md; result_reports/records/2026-07/2026-07-14-train-admin-mapping-data-foundation-merge-closeout.md

  - type: error
    topic: Data Mapping Computer Use accessibility crash
    content: Data Mapping Computer Use onscreen smoke previously crashed during macOS/AppKit accessibility hierarchy reads. Removing initial programmatic selectRow stabilized the earlier Slice 2A bounded state checks, but the Slice 2B+2C populated spreadsheet table again reproduced the failure on two independent native AX element/coordinate click attempts. Python terminated with EXC_BAD_ACCESS/SIGSEGV on the main thread in NSAccessibility hierarchy accessors, while injected keyboard shortcuts did not reach the Qt table. Native rendering alone and the passing automated owner suite do not establish the three required interaction scenarios; record them as blocked until the accessibility bridge is resolved or a separately authorized manual path supplies evidence.
    keywords:
      - predictor_v3
      - Data Mapping
      - Computer Use
      - accessibility
      - PySide6
      - AppKit
      - SIGSEGV
    assertionStatus: verified
    source: result_reports/legacy/summaries/687_summary-arc13-5r-arc14b-data-mapping-foundation-closeout.md; result_reports/legacy/summaries/700_summary-arc14b-runtime-data-mapping-crud-design-closeout.md; result_reports/records/2026-07/2026-07-14-train-admin-phase2-slice2bc-native-blocker.md

  - type: decision
    topic: Train Admin Phase 2 Data Mapping interaction and source state
    content: Data Mapping cached draft existence and runtime source availability are independent. Non-destructive Refresh reprojects the service-owned draft without provider reload and preserves group selection, values, validation, exact baseline-diff dirty state, and command history; Reload alone reads the provider and preserves current draft/baseline/history on missing or load failure. Successful Reload resets draft/baseline/history, and successful Save advances baseline while failed Save preserves it. Empty-message exceptions use a stable class-name summary. Slice 2A native macOS evidence covers populated, dynamic, empty, missing, load-error, dirty-source-missing, compact, and collapsed-detail states. Slice 2B places toolbar and spreadsheet selection/clipboard/key behavior in feature-local Qt owners, pure snapshot projection outside controller orchestration, and current draft plus draft-level undo history in a service-owned session. Edit, rectangular paste, clear, CRUD, and F&T-to-PFC Pi clearing are one command each; PFC Pi is protected in both UI flags and the service command boundary without shifting clipboard coordinates. Slice 2C uses structured validation group/row/field identifiers for issue-to-cell navigation and never parses messages; source/save/reload issues have no cell target. The Batch audit correction resolves built-in and definition-backed column types through one Qt-free mapping value policy, canonicalizes only valid numeric/boolean mutation input before exact dirty comparison, keeps invalid input raw, atomically blocks any out-of-bounds paste before command history, and uses one complete rectangle for selection, copy, paste anchor, and clear.
    keywords:
      - predictor_v3
      - Data Mapping
      - Phase 2
      - Slice 2A
      - Refresh
      - Reload
      - dirty draft
      - native macOS
      - spreadsheet interaction
      - grouped undo
      - baseline diff
      - issue navigation
    assertionStatus: verified
    source: result_reports/records/2026-07/2026-07-14-train-admin-phase2-slice2a-native-audit-correction.md; result_reports/records/2026-07/2026-07-14-train-admin-phase2-slice2b-spreadsheet.md; result_reports/records/2026-07/2026-07-14-train-admin-phase2-slice2c-workflow.md; result_reports/records/2026-07/2026-07-14-train-admin-phase2-slice2bc-audit-correction.md

  - type: decision
    topic: Train Admin Phase 2 exchange export boundary
    content: Slice 2D keeps the existing JSON/XLSX review snapshot and export_csv_v2 contract separate from the official mapping exchange contract. Exchange export is owned by the Qt-free core/mapping/exchange package and consumes the service-owned current draft without provider Reload. One operation deterministically serializes the current visible seven-group projection into seven canonical group CSVs and a sectioned mapping_bundle_v1 CSV, preserves standard CSV quoting and typed canonical text, blanks PFC Pi, excludes hidden payload, and stages all eight files before rollback-aware publish. The bundle filename is user-selected but case-insensitive canonical group filenames are reserved. Initial Slice 2E import policy is exact-header: every current visible projection header must occur once; missing, unknown, or duplicate headers block the full replacement before draft/session/runtime state changes.
    keywords:
      - predictor_v3
      - Train Admin
      - Data Mapping
      - mapping_bundle_v1
      - exchange export
      - exact header
      - review snapshot
  assertionStatus: verified
  source: result_reports/records/2026-07/2026-07-15-train-admin-phase2-slice2d-exchange-export.md

  - type: decision
    topic: Train Admin Phase 2 bundle import boundary
    content: Slice 2E accepts only marker-owned sectioned mapping_bundle_v1 input and never infers format or section identity from filename. Exact-header policy requires every current Data Definition visible projection column exactly once, including optional dynamic columns; header order is projected by name, and missing/unknown/duplicate headers block the full import with group/column guidance to re-export. A valid seven-section bundle becomes a typed full-replacement candidate, previews visible identity/value changes, preserves matching hidden row payload and unowned sections, applies only to the service-owned unsaved draft as one undo command, rejects stale previews, and leaves runtime mapping unchanged until explicit Save. Review snapshots and clipboard TSV remain separate contracts.
    keywords:
      - predictor_v3
      - Train Admin
      - Data Mapping
      - Phase 2
      - Slice 2E
      - mapping_bundle_v1
      - exact header
      - unsaved draft
      - grouped undo
      - hidden payload
    assertionStatus: verified
    source: result_reports/records/2026-07/2026-07-15-train-admin-phase2-slice2e-bundle-import.md

  - type: decision
    topic: Arc 14B Data Mapping import/export and CRUD direction
    content: Historical single-wide CSV conversion is not recoverable as a general import contract. The Phase 1 legacy-wide parser is a strict bootstrap-only adapter into the existing editor draft and validated runtime projection; normal Data Mapping Import remains excluded. JSON and XLSX Export are read-only review snapshots rather than edit/reimport contracts; Save/Reload/dirty-state behavior stays below the UI raw JSON boundary.
    keywords:
      - predictor_v3
      - Arc 14B
      - Data Mapping
      - mapping.json
      - CSV import
      - Export
      - CRUD
      - dirty state
    assertionStatus: verified
    source: result_reports/legacy/summaries/700_summary-arc14b-runtime-data-mapping-crud-design-closeout.md; result_reports/legacy/summaries/710_summary-arc14b-crud-cascade-xlsx-prearc15-closeout.md; result_reports/records/2026-07/2026-07-14-train-admin-mapping-bootstrap-slice-1a.md

  - type: decision
    topic: Arc 14B ref exp mapping SSOT
    content: mapping.json is the SSOT for Refrigerant and Expansion options. Refrigerant projects to required ref_type and Expansion projects to required exp_type; Predict dropdown hard-coded fallback options have been removed, and missing or empty sections become validation/status-visible issues rather than generated options.
    keywords:
      - predictor_v3
      - Arc 14B
      - Data Mapping
      - mapping.json
      - ref_type
      - exp_type
      - Predict dropdown
      - validation
    assertionStatus: verified
    source: result_reports/legacy/summaries/700_summary-arc14b-runtime-data-mapping-crud-design-closeout.md; result_reports/legacy/summaries/710_summary-arc14b-crud-cascade-xlsx-prearc15-closeout.md

  - type: decision
    topic: Arc 14C runtime cascade integration
    content: Predict runtime dropdowns and autofill consume Data Mapping Manager generated mapping.json sections for ODU Cond Specs cascade behavior. Condenser identity is Fin-Type-dependent: F&T and every non-PFC Fin Type use ODU + Fin Type + Pi + Row, while PFC uses ODU + Fin Type + Row. Any PFC Pi placeholder or stale value is canonically empty before editor/runtime key, cascade, option, persistence, converter, or Predict consumption. The Excel converter rejects incomplete condenser identities before writing, and ODU Cond Specs identity edits keep source_key synchronized with current canonical row values. odu_cascade, cond_specs, fin_type, pi, and row remain runtime SSOT sections; missing or invalid mapping states remain empty/status-visible and do not recreate hard-coded fallback behavior.
    keywords:
      - predictor_v3
      - Arc 14C
      - Runtime Cascade
      - Data Mapping
      - mapping.json
      - odu_cascade
      - cond_specs
      - autofill
    assertionStatus: verified
    source: result_reports/legacy/summaries/710_summary-arc14b-crud-cascade-xlsx-prearc15-closeout.md; result_reports/records/2026-07/2026-07-14-train-admin-mapping-bootstrap-slice-1a.md; result_reports/records/2026-07/2026-07-14-train-admin-mapping-bootstrap-slice-1a-correction.md; result_reports/records/2026-07/2026-07-14-train-admin-mapping-bootstrap-slice-1a-final-correction.md

  - type: decision
    topic: dependency and Excel policy
    content: Requirements are app-scoped. Train and Predict share requirements/ml_runtime.txt with joblib, numpy, pandas, scikit-learn, and xgboost; Predict excludes training-only optuna. Generated XLSX write/export uses openpyxl, while existing user Excel reads remain an xlwings/Excel automation workflow when needed. Requirements remain unpinned unless a future version policy is introduced.
    keywords:
      - predictor_v3
      - requirements
      - ml_runtime
      - Predict
      - Train
      - openpyxl
      - xlwings
      - Excel
    assertionStatus: verified
    source: result_reports/legacy/summaries/710_summary-arc14b-crud-cascade-xlsx-prearc15-closeout.md

  - type: open_question
    topic: Pre Arc 15 config mapping source relationship
    content: Before Arc 15 direction is finalized, audit the relationship between config/ml/features.csv, config/predict/schema.csv, tests/fixtures/mapping/mapping_tables_legacy_wide.csv, Data Mapping Manager outputs, and real training data outside the repo. Do not decide whether the config CSV split is final design or accumulated duplication, and do not commit to a Unified Data Definition Manager direction before that audit.
    keywords:
      - predictor_v3
      - Pre Arc 15
      - config/ml/features.csv
      - config/predict/schema.csv
      - legacy mapping
      - Data Mapping Manager
      - training data
      - Unified Data Definition Manager
    assertionStatus: observed
    source: result_reports/legacy/summaries/710_summary-arc14b-crud-cascade-xlsx-prearc15-closeout.md
    resolutionStatus: resolved_by_arc15_foundation
    resolvedBy: result_reports/legacy/summaries/725_summary-arc15-data-definition-foundation-closeout.md

  - type: decision
    topic: Arc 15 Data Definition foundation owner state
    content: Data Definition is the Train/Admin schema and feature-definition owner. It projects config/predict/schema.csv plus explicit derived policy, provides read-only/report and in-memory draft edit/save-preview UI, and saves schema-backed edits only through the guarded schema writer to an explicit schema path. Until a features.csv projection writer exists, a draft that changes the active ML compatibility fingerprint is blocked from saving schema.csv; label and notes remain writable because they are outside that fingerprint. Data Mapping remains the mapping.json value owner with dynamic requirements projected from Data Definition. The Phase 1 DEV alignment validator pairs selector metadata with the unchanged numeric/one-hot training frame and resolves schema-backed values from the repository runtime-equivalent mapping fixture, including conditional F&T/PFC identities; invalid options/combinations and mismatched training values fail fast. The separate Feature Catalog UI is retired; core ML catalog compatibility remains. Mock readiness does not establish model quality or production readiness.
    keywords:
      - predictor_v3
      - Arc 15
      - Data Definition
      - schema.csv
      - Feature Catalog
      - Data Mapping
      - readiness
      - schema writer
    assertionStatus: verified
    source: result_reports/legacy/summaries/725_summary-arc15-data-definition-foundation-closeout.md; result_reports/records/2026-07/2026-07-11-clean-hex-mvc-ui-refactor.md; result_reports/records/2026-07/2026-07-14-train-admin-mapping-foundation-slice-1d.md
```

## Known Gaps

- This active seed is intentionally compact and does not contain every historical memory candidate.
- Retired/stale/superseded/resolved entries and source traces remain in `result_reports/memory/archive/project_memory_seed_retired_2026-07.md`.
- Consolidated source entries are archived rather than deleted, with the active replacement topic recorded in the archive.
- The seed does not reconstruct fine-grained evidence from individual archived reports.
- Open questions remain unresolved until an explicitly scoped implementation, verification, or policy task addresses them.

## Next Maintenance Rule

- Memory Review Gate trigger에서만 `updated` 또는 `no-change + reason`을
  판단한다.
- ordinary source/code/docs 작업은 durable memory가 바뀌지 않으면 seed를
  수정하지 않는다.
- 새 durable decision/error/open_question은 가장 작은 관련 entry를 갱신하거나
  1개 entry만 추가한다.
- 대체된 entry는 source trace를 보존하고 superseded/retired 처리한다.
- report 수는 memory cleanup trigger가 아니다. 검색성이 나빠지거나 stale
  active entry가 누적될 때만 전용 maintenance를 수행한다.
- result record와 legacy evidence는 memory 내용에 맞추기 위해 소급 수정하지
  않는다.
