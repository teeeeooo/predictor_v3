# Work Plan

## Purpose

- Maintain the current slice, next action, active blockers/open decisions,
  active constraints, and deferred/hold items.
- Keep Phase / Arc / Milestone direction in `project_brief.md`.
- Keep long-term goals and Phase 1~5 direction in `PROJECT_CHARTER.md`.
- Keep completed work history in `project_log.md`, `result_reports/summaries/`,
  and `result_reports/archive/`.
- Keep refactor candidates and structural triggers in `docs/REFACTOR_PLAN.md`.

## Work Plan Update Rule

- `WORK_PLAN.md` is the near-term execution board, not a roadmap, task log, or
  report index.
- Update only when current slice, next action, execution order, active
  constraints, blockers/open decisions, or hold status changes.
- Do not append completed report lists, full report content, terminal output, or
  repeated next-action history.
- Arc and milestone status belong to `project_brief.md`; only reference them here
  when they directly constrain the current slice.
- Ordinary work plan maintenance does not create or update `Session Handoff`.
  That section exists only when the user explicitly requests a session or
  next-agent handoff, following
  `docs/agent_workflows/DOCUMENT_SYNC_AND_LIFECYCLE.md`.

## Current Slice

- Arc 13 is complete for the automated feature catalog migration scope. The
  closeout summary is
  `result_reports/summaries/633_summary-arc13-feature-catalog-closeout.md`.
- Arc 13.5 Feature Catalog Editor Bridge is complete for automated scope:
  `app_train.py` now has a Feature Catalog tab for validate, Excel-safe export,
  whitelisted edit, and validation-gated canonical save.
- Arc 13.5A Feature Catalog Manager correction is complete: dropdown UX,
  user-confirmed GUI smoke, narrowed model compatibility fingerprint, and active
  fingerprint payload dedup are closed out.
- Active report lifecycle cleanup is complete for Arc 13.5/13.5A and summarized
  in `result_reports/summaries/673_summary-arc13-5a-feature-catalog-manager-closeout.md`.
- Current next action is Arc 13.5R, Predict Schema Catalog v2 design/audit,
  before implementing Arc 14 Data Mapping Manager. Data Mapping Manager depends
  on a generic schema contract for columns, mapping entities, mapping
  attributes, trigger columns, and cascade/autofill rules. The current
  `app_train.py` Data Mapping tab remains a placeholder: mapping source
  selection says it belongs to a follow-up arc and mapping update controls are
  disabled.
- Arc 13.5R-1 current Predict schema inventory is captured in
  `docs/designs/assets/current_predict_schema_inventory.md`.
- Arc 13.5R-4 projection owner switch is complete: Predict core `COLUMNS` now
  load from the v2 projection while current adapter compatibility fields,
  mapping/autofill behavior, case-table virtual status/message columns, and
  one-hot ML input projection remain on their existing runtime owners.
- Arc 14A Mapping Entity / Master Data Model Foundation is complete: generic
  Qt-free mapping entity definitions, attribute definitions, row values,
  catalog lookup, and focused validation now live under `core/mapping`.
  Canonical CSV v2 direction is entity/attribute/row based, while import/export
  and mapping JSON write/reload remain follow-up work.
- Arc 14B-1 Data Mapping Manager UI Foundation is complete for read-only scope:
  active/key identity validation semantics are clarified, and Train/Admin now
  has a service/controller-backed Data Mapping tab showing entity, attribute,
  row, validation, and disabled future action surfaces from a foundation sample
  provider.
- Arc 14B-2 Runtime Mapping Repository Read Adapter is complete for read-only
  scope: `DataMappingService()` now defaults to a runtime mapping provider that
  adapts repository data into `MappingEntityCatalog`; sample provider usage is
  explicit test/fallback injection only. Missing `data/mapping.json` surfaces as
  a load error instead of a silent sample fallback.
- Arc 14B-2F Runtime Source Visibility and Row Identity Display follow-up is
  complete: load failures preserve the runtime source/path in UI state, and the
  read-only row table shows row identity only as `Row Key` instead of repeating
  the entity key attribute as an empty adjacent value column.
- Arc 14B-4 Legacy Mapping CSV to JSON reconstruction audit is complete:
  current runtime consumes section-shaped `mapping.json` data through existing
  repository/autofill/dropdown owners, while the current CSV converter only
  creates a `Sheet1` section and no deleted single-wide-CSV parser/header
  contract was found. Direction C is selected: design UI CRUD next, keep Import
  disabled, and treat Export as a read-only review snapshot rather than an
  edit/reimport contract.
- Arc 14B-5A Data Mapping UI CRUD workflow design is complete: the editable
  path is framed as user-facing Predict mapping groups, not a raw JSON or
  generic entity editor. ODU Cond Specs is one user table that generates
  `odu_cascade`, `cond_specs`, `fin_type`, `pi`, and `row`; Import remains
  excluded, Export is read-only snapshot, and Save/Reload/Issues/dirty-state
  boundaries are documented for implementation slices.
- Arc 14B-5B~5G Data Mapping Manager implementation and blocker hardening are
  complete for user-facing draft projection, mapping-backed ref/exp dropdowns,
  draft validation, editable row CRUD, validation-gated save with backup and
  atomic replace, JSON read-only snapshot export, ODU Cond Specs composite-key
  validation, dirty reload confirmation, and Save/Export feedback.
- Arc 14C Runtime Cascade Integration is complete: Predict runtime dropdowns
  and autofill now consume Data Mapping Manager generated `mapping.json`
  sections for ODU Cond Specs cascade behavior while preserving mapping JSON as
  the SSOT and keeping missing/invalid mapping states empty/status-visible.

## Next Actions

1. Pre-Arc 15 Audit - Config CSV / Legacy Mapping Source / Manager Output
   Relationship Audit.
2. Arc 15 direction decision after the audit.
3. Real model prediction success smoke after `model/model.pkl` is available.

## Active Blockers / Open Decisions

- Real model prediction success smoke is not complete in this checkout because
  `model/model.pkl` is absent.
- Mock smoke can cover workflow readiness, but it cannot validate prediction
  accuracy, physical trends, feature importance, or production model quality.
- Arc 13.5 GUI manual smoke in a real desktop session remains pending; automated
  Qt tests used offscreen mode.
- A future explicit DEV/demo sample loader remains optional and is not part of
  the production empty-state contract.
- Schema/column/rule changes use an initial restart-required policy; live schema
  reload remains a future decision.
- IDU-Evap and ODU-Cond are initial examples/default presets, not the schema
  boundary; the boundary must be generic mapping entity / attribute / rule.
- Legacy single CSV import reconstruction is not feasible enough to use as the
  next implementation. If import returns later, it must be an optional
  compatibility parser with explicit aliases and validation, not inferred from
  the legacy wide fixture. The immediate Data Mapping path is UI CRUD workflow
  design; Export should be a read-only review snapshot.
- Data Mapping editable UX should expose user-facing groups only: IDU, Evap
  Index, ODU, Compressor, Refrigerant, Expansion, and ODU Cond Specs. Internal
  `odu_cascade`, `cond_specs`, `fin_type`, `pi`, and `row` sections are derived
  from ODU Cond Specs rather than edited directly.
- `mapping.json` is the SSOT for Refrigerant and Expansion options:
  `ref_type` and `exp_type` are required mapping sections, and Predict dropdown
  hard-coded fallback options have been removed.
- Data Mapping UI now uses the runtime mapping repository by default, but this
  checkout currently lacks `data/mapping.json`; runtime-data visual smoke needs
  that file or an explicit temp runtime provider harness.
- One-hot ML input projection is not yet v2-owned. Arc 14A/14C kept semantic
  mapping fields separate from legacy `mapping`, `source`, and `mapping_key`
  compatibility fields.
- Bundle 2A-F records dependency correction: Train/Predict share
  `requirements/ml_runtime.txt`; Predict includes XGBoost/scikit-learn runtime
  for real `model.pkl` inference while excluding training-only `optuna`; Excel
  policy remains `openpyxl` for generated XLSX write/export and `xlwings` for
  existing user Excel reads in Windows user environments.
- Arc 14D-R is complete: Data Mapping Manager export supports JSON and
  `openpyxl` XLSX read-only review snapshots, export preserves dirty drafts
  without saving `mapping.json`, Import remains unsupported, and Predict
  invalid mapping status is distinct from missing mapping status.
- `tests/fixtures/mapping/mapping_tables_legacy_wide.csv` appears to be the
  existing legacy mapping-form source/evidence behind the Data Mapping Manager
  direction; its current path and relationship to generated manager outputs
  must be re-audited before Arc 15 direction is finalized.
- Real training CSV data is not in this checkout; the real training data remains
  on the user's local PC.
- `config/ml/features.csv` currently reads as the ML feature contract, while
  `config/predict/schema.csv` currently reads as the Predict UI/runtime schema
  contract. Do not decide whether this split is final design or accumulated
  duplication until the Pre-Arc 15 audit.
- Data Mapping Manager, Runtime Cascade, and XLSX snapshot export completion do
  not by themselves settle the Feature Catalog ↔ Predict Schema ↔ Data Mapping
  Manager relationship.
- Do not commit to a `Unified Data Definition Manager` direction until the
  config CSV / legacy mapping source / manager output relationship audit is
  complete.

## Active Constraints

- Do not restore production performance prefills; focused tests own any samples
  needed for calculation and detail regression coverage.
- Preserve `app_calculator.py` → `apps.calculator.app:main` as the canonical
  calculator launch boundary.
- Preserve calculator, schema, config, fixture, golden, and public result
  contracts.
- Keep Train/Predict rewrite separate from the Tkinter calculator path.
- Do not recreate the retired legacy `ui/` Train/Predict path; PySide6
  Predict/Train work belongs under `apps/predict/` and `apps/train/`.
- Use focused verification rather than full pytest by default.

## Deferred / Hold

- AS/NZS Excel compatibility remains in the deferred Z-phase.
- Data Mapping Manager implementation can proceed from the Arc 14A foundation.
  Existing `scripts/update_mapping.py` and `core.mapping.update` conversion
  logic were reviewed for the Arc 14B-4 audit; the GUI must still not own raw
  file conversion directly.
- Broad ML / predictor algorithm and real dataset readiness work remains
  deferred to Arc 15; later prediction execution work must preserve core ML
  behavior.
- Internal formula trace and broad code-quality refactors remain on hold; their
  candidates belong in `docs/REFACTOR_PLAN.md`.

## Reference Anchors

- Active Arc / Milestone map: `project_brief.md`.
- Last closed EN14825 batch/workflow summary:
  `result_reports/summaries/416_summary-en14825-batch-agent-change-gate-closeout.md`.
- AHRI calculator and supporting UI/workflow closeout:
  `result_reports/summaries/445_summary-ahri-calculator-ui-batch-lifecycle-closeout.md`.
- Calculator helper/batch/detail lifecycle closeout:
  `result_reports/summaries/490_summary-calculator-helper-batch-lifecycle-closeout.md`.
- PySide6 Train/Predict rewrite design gate:
  `docs/designs/2026-06-27-pyside6-train-predict-rewrite-design-gate.md`.
- PySide6 Train/Predict governing architecture contract:
  `docs/architecture/pyside6_train_predict_architecture.md`.
- PySide6 Train/Predict visual/table parity harvest:
  `docs/designs/2026-06-27-pyside6-visual-table-parity-harvest.md`.
- Arc 13.5 Feature Catalog editor design gate:
  `docs/designs/2026-07-01-arc13-5-feature-catalog-editor-design-gate.md`.
- Arc 13.5 revised slice plan:
  `docs/designs/2026-07-02-arc13-5-feature-catalog-editor-revised-slice-plan.md`.
- Arc 13.5R Predict Schema / Mapping Manager foundation:
  `docs/designs/2026-07-03-arc13-5r-predict-schema-mapping-manager-foundation.md`.
- Arc 13.5R projection owner switch:
  `docs/designs/2026-07-03-arc13-5r-projection-owner-switch.md`.
- KOREA calculator notebook entry sub-arc:
  `docs/designs/2026-07-01-korea-notebook-entry-subarc-spec.md`.
- KS C 9306 HSPF official oracle closeout:
  `result_reports/summaries/651_summary-ks-hspf-official-oracle-closeout.md`.
- B-option unified case table visual reference:
  `docs/designs/assets/predict_ref_img.png`.
- Spreadsheet table UX baseline:
  `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`.
- Input/result surface shaping:
  `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`.
- UI literal legacy inventory and cleanup plan:
  `docs/designs/2026-06-21-ui-magic-literal-legacy-inventory.md`.
- Calculator sample/default inventory and empty-state policy:
  `docs/designs/2026-06-21-calculator-sample-data-empty-state-policy.md`.
- AHRI implementation contract:
  `docs/designs/2026-06-20-ahri-210-240-ui-batch-design-specification.md`.
- Milestone decisions and detailed completed history belong in `project_log.md`
  and the result-report lifecycle directories.
