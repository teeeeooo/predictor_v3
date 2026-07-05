# Design Records Index

## Role

`docs/designs/` is a design gate evidence library. Files here preserve
decision context, rejected options, migration notes, and implementation slice
history.

Design records are **not active rule owners**. Repeated rules belong in
active owner documents:

- UI/UX rules: `docs/ui_ux/00_UI_UX_SYSTEM.md` and related `docs/ui_ux/`
  owner docs.
- Architecture boundaries: `docs/architecture/project_architecture.md`.
- Standard or region rules: the relevant standard/region docs.
- Task routing gates: `AGENT_TASK_ROUTER.md`.
- Current execution order: `docs/WORK_PLAN.md`.

## Read Rule

Do not read every design record by default. For a task that mentions prior
design decisions, use this index to find the relevant record, then read only
the title, purpose/decision/status, and necessary surrounding range.

## Lifecycle Status

- `template`: reusable design gate template.
- `active reference`: still directly useful for upcoming work.
- `absorbed by owner docs`: decision is preserved here, but repeated rules
  have moved to active owner docs.
- `historical reference`: past decision/evidence; read only when needed.
- `archive candidate`: mostly historical and may be moved later by a separate
  archive task.

## Index

| File | Status | One-line decision | Current source of truth | Read when |
| --- | --- | --- | --- | --- |
| `TEMPLATE_DESIGN_GATE.md` | template | Standard shape for future design gate records. | `AGENTS.md`, `AGENT_TASK_ROUTER.md` | Creating a new design gate record. |
| `2026-05-06-iso16358-2-hspf-core-boundary.md` | active reference | Keep ISO HSPF core boundaries explicit. | `docs/architecture/project_architecture.md`, ISO docs | ISO HSPF boundary or resolver work. |
| `2026-05-08-asnzs-hspf-excel-compat-boundary.md` | historical reference | Preserve AS/NZS Excel compatibility boundary evidence. | relevant AS/NZS future owner docs | AS/NZS compatibility work resumes. |
| `2026-05-10-iso16358-2-hspf-h8-routing-resolver-design.md` | active reference | Route ISO HSPF H-8 behavior through resolver/design boundaries. | `docs/iso16358/iso16358_dev_notes.md`, architecture docs | ISO HSPF H-8 routing work. |
| `2026-05-17-iso-remaining-work-completion.md` | historical reference | Closed the ISO remaining-work boundary for that phase. | `docs/WORK_PLAN.md`, ISO owner docs | Reviewing old ISO completion scope. |
| `2026-05-17-calculator-horizontal-table-input-ui.md` | absorbed by owner docs | Calculator comparable inputs should use table/matrix surfaces. | `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`, `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` | Investigating original calculator table-input decision. |
| `2026-05-17-calculator-result-envelope-ml-adapter.md` | active reference | Keep calculator result envelope separate from ML adapter input. | `docs/architecture/project_architecture.md` | ML adapter or result schema boundary work. |
| `2026-05-22-calculator-action-model-alignment.md` | absorbed by owner docs | Calculator single-case flow favors immediate recalculation. | `docs/ui_ux/00_UI_UX_SYSTEM.md`, `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` | Reviewing auto-calc vs explicit action history. |
| `2026-05-22-calculator-ui-module-boundary.md` | absorbed by owner docs | Split calculator UI responsibilities by shell/input/result/helper boundary. | `docs/architecture/project_architecture.md`, `AGENTS.md` code-quality gate | Calculator UI module-boundary archaeology. |
| `2026-05-22-lightweight-calculator-ui-feasibility.md` | historical reference | Chose lightweight calculator UI feasibility path and packaging constraints. | `docs/WORK_PLAN.md`, packaging guide | Revisiting Tkinter/PyQt packaging direction. |
| `2026-05-23-tkinter-calculator-final-ux-contract.md` | absorbed by owner docs | Tkinter calculator target UX is matrix input, auto-calc, summary result. | `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`, Tkinter adapter | Checking the original Tkinter final UX decision. |
| `2026-05-24-pyqt-calculator-reference-feature-migration-contract.md` | active reference | PyQt calculator reference features are migration requirements/evidence, not automatic porting instructions. | `docs/WORK_PLAN.md`, UI/UX owner docs | PyQt retirement, parity, or migration-gate tasks. |
| `2026-05-29-tkinter-iso-iseer-2point-result-visual-refinement.md` | absorbed by owner docs | ISO/ISEER comparison results should be easier to compare than stacked summaries. | `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` | Result visual comparison context. |
| `2026-05-29-tkinter-iso-iseer-2point-single-design.md` | historical reference | Added ISO/ISEER 2-point as its own Tkinter mode/profile surface. | `docs/WORK_PLAN.md`, implemented Tkinter section | ISO/ISEER profile/mode history. |
| `2026-05-29-tkinter-saso-t3-profile-design.md` | active reference | Add SASO T3 as a focused Tkinter profile without broad feature expansion. | `docs/WORK_PLAN.md`, SASO implementation | SASO T3 follow-ups. |
| `2026-05-30-tkinter-detail-trace-graph-result-surface-design.md` | active reference | Detail/trace/graph surfaces supplement summary results and remain separate from internal formula trace. | `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`, future detail/bin schema docs | Detail/bin/graph follow-ups. |
| `2026-05-30-tkinter-excel-like-table-contract-recovery.md` | absorbed by owner docs | Tkinter table-like surfaces must recover Excel-like behavior expectations. | `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`, `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md` | Table UX recovery archaeology. |
| `2026-05-30-tkinter-result-surface-export-boundary.md` | absorbed by owner docs | Keep result/export responsibilities small and section-local until reuse is justified. | `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`, table export helpers | Result/export boundary context. |
| `2026-06-20-ahri-210-240-ui-batch-design-specification.md` | active reference | Fix AHRI SEER2/HSPF2 main and two-row batch contracts before implementation. | this implementation contract plus UI/UX and architecture owner docs | AHRI 210/240 main UI, batch, optional-point, or lifecycle work. |
| `2026-06-21-ui-magic-literal-legacy-inventory.md` | active reference | Classify grandfathered UI presentation literals and split migration into bounded semantic-token slices. | `docs/agent_workflows/AGENT_CHANGE_GATES.md`, `apps/calculator/ui/layout_constants.py` | Planning UI literal cleanup or expanding the staged literal gate. |
| `2026-06-21-calculator-sample-data-empty-state-policy.md` | active reference | Keep standard/option defaults, remove product demo performance values only after required detail surfaces exist. | profile UI owners plus future EN14825/AHRI detail design | Planning detail views, sample removal, or calculator empty-state behavior. |
| `2026-06-21-en14825-ahri-detail-view-design.md` | active reference | Define bin-detail ownership, schema direction, and implementation order for EN14825/AHRI profiles. | profile UI/core owners plus result/detail UI contracts | Implementing or reviewing EN14825/AHRI detail surfaces. |
| `2026-06-21-calculator-window-profile-lifecycle-audit.md` | active reference | Classify repeated profile-local lifecycle assembly as structural debt while preserving evidence-based profile predicates and settle policies. | window/viewport policy plus upcoming common lifecycle controller design | Designing or migrating calculator profile visible-content lifecycle ownership. |
| `2026-06-21-profile-visible-content-lifecycle-controller-design.md` | active reference | Centralize profile measurement/shell/scheduler composition in a feature-owned controller with injected predicates and settle policies. | this implementation contract plus window/architecture owners | Implementing or enforcing calculator profile lifecycle ownership. |
| `2026-06-27-pyside6-train-predict-rewrite-design-gate.md` | active reference | Rewrite Train/Predict as new PySide6 apps under `apps/predict/` and `apps/train/`; visual reference assets guide Arc 9.5 layout parity but are not pixel-perfect targets. | `docs/architecture/pyside6_train_predict_architecture.md`, `docs/designs/2026-06-27-pyside6-visual-table-parity-harvest.md`, `PROJECT_CHARTER.md`, `docs/architecture/project_architecture.md`, `docs/WORK_PLAN.md` | Planning Train/Predict rewrite preflight, visual parity, or legacy retirement decisions. |
| `2026-06-27-pyside6-visual-table-parity-harvest.md` | active reference | Preserve project-specific legacy Train/Predict visual, table, mapping, result, train-admin, and token evidence as Arc 9.5 acceptance input. | `docs/architecture/pyside6_train_predict_architecture.md`, `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`, `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`, `docs/designs/assets/predict_ref_img.png`, `docs/designs/assets/train_ref_img.png`, `ui_common.visual_tokens` | Implementing Arc 9.5 Predict/Train visual parity from design assets; not a portable UI/UX owner contract. |
| `2026-06-28-arc10-prediction-worker-progress-design.md` | active reference | Move prediction execution behind focused worker/progress/cancel boundaries while preserving service/adapters, unified table UX, and core ML behavior. | `docs/architecture/pyside6_train_predict_architecture.md`, `docs/WORK_PLAN.md`, `apps/predict/controllers/prediction_controller.py`, `apps/predict/workers/prediction_worker.py` | Implementing or reviewing Arc 10 prediction worker/progress/cancel slices. |
| `2026-06-28-arc11-predict-train-hexagonal-boundary-reopen.md` | active reference | Reopen Arc 11 to correct Predict/Train execution/usecase boundaries; move Calculator correction to Arc 12. | `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`, `docs/architecture/pyside6_train_predict_architecture.md`, `docs/WORK_PLAN.md`, `project_brief.md` | Implementing or reviewing Arc 11 reopened Train/Predict boundary correction slices. |
| `2026-06-28-arc12-calculator-usecase-boundary-audit.md` | active reference | Extract calculator application-usecase orchestration outside Tk sections, starting with ISO/ISEER 2-point single and batch reuse. | `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`, `docs/architecture/project_architecture.md`, `docs/WORK_PLAN.md` | Implementing or reviewing Arc 12 calculator usecase boundary slices. |
| `2026-06-30-arc13-ml-feature-manifest-design-gate.md` | active reference | Narrow Arc 13 entry to ML Feature Manifest SSOT Foundation while keeping runtime constants and registry behavior unchanged in Slice 0. | `docs/architecture/project_architecture.md`, `docs/agent_workflows/ML_PREDICTOR_WORKFLOW.md`, `docs/WORK_PLAN.md` | Implementing Arc 13 feature catalog loader, validator, projection parity, or zero-fill policy slices. |
| `2026-07-01-arc13-5-feature-catalog-editor-design-gate.md` | active reference | Design Arc 13.5 around an `app_train.py` Feature Catalog table editor workflow instead of default direct CSV editing. | `docs/designs/2026-07-01-arc13-5-feature-catalog-editor-design-gate.md`, `docs/WORK_PLAN.md`, `result_reports/summaries/633_summary-arc13-feature-catalog-closeout.md` | Implementing Arc 13.5 viewer, editor, export, or save slices. |
| `2026-07-02-arc13-5-feature-catalog-editor-revised-slice-plan.md` | active reference | Refine Arc 13.5 into design, viewer/validate, export, editable save, and closeout slices with validation/save guardrails. | `docs/designs/2026-07-01-arc13-5-feature-catalog-editor-design-gate.md`, `docs/WORK_PLAN.md` | Implementing or verifying Arc 13.5 slice order, export/save policy, editable whitelist, or stop conditions. |
| `2026-07-03-arc13-5r-predict-schema-mapping-manager-foundation.md` | active reference | Reframe Arc 13.5/14 around Predict Schema Catalog v2, mapping master data, and template-aware cascade management before implementing Data Mapping Manager. | `docs/WORK_PLAN.md`, `docs/architecture/pyside6_train_predict_architecture.md`, future Predict Schema owner docs | Planning column/feature addition, mapping data manager, IDU-Evap cascade, or schema/mapping runtime integration. |
| `2026-07-03-arc13-5r-predict-schema-v2-field-spec-confirmation.md` | active reference | Confirm Predict Schema Catalog v2 fields, enum values, current-to-v2 mapping, one-hot representation, primitive rules, and restart-required schema policy before read-only parity prototyping. | `docs/designs/assets/current_predict_schema_inventory.md`, `docs/WORK_PLAN.md`, future Predict Schema owner docs | Implementing Arc 13.5R-3 read-only schema draft/projection parity or reviewing v2 field/rule contract decisions. |
| `2026-07-03-arc13-5r-readonly-schema-v2-projection-parity.md` | active reference | Prove a read-only Predict Schema Catalog v2 draft can reproduce current 28 core `COLUMNS` order and key metadata without switching runtime ownership. | `config/predict/schema.csv`, `core/predictor_schema/catalog_v2.py`, `core/predictor_schema/catalog_v2_projection.py`, `docs/WORK_PLAN.md` | Reviewing Arc 13.5R-3 parity evidence or planning Arc 13.5R-4 projection owner switch readiness. |
| `2026-07-03-arc13-5r-projection-owner-switch.md` | active reference | Switch Predict core `COLUMNS` assembly to the v2 projection while preserving current adapter compatibility and documenting remaining runtime-owned paths. | `config/predict/schema.csv`, `core/predictor_schema/catalog_v2_projection.py`, `core/predictor_schema/columns.py`, `docs/WORK_PLAN.md` | Reviewing Arc 13.5R-4 owner switch evidence or planning Arc 14A mapping entity / master data foundation. |
| `2026-07-03-arc14a-mapping-entity-master-data-foundation.md` | active reference | Define Qt-free generic mapping entity, attribute, row, catalog, and validation foundation while leaving CSV import/export and runtime cascade for follow-up arcs. | `core/mapping/entity_model.py`, `core/mapping/entity_validation.py`, `docs/WORK_PLAN.md` | Implementing Arc 14B Data Mapping Manager UI, Arc 14C runtime cascade integration, or CSV v2 mapping data import/export. |
| `2026-07-03-arc14b-data-mapping-manager-ui-foundation.md` | active reference | Start the Train/Admin Data Mapping Manager as a read-only service/controller/UI foundation and clarify Arc 14A active/key identity semantics. | `apps/train/services/data_mapping_service.py`, `apps/train/controllers/data_mapping_controller.py`, `apps/train/ui/data_mapping_panel.py`, `core/mapping/entity_validation.py`, `docs/WORK_PLAN.md` | Implementing Arc 14B-2 runtime mapping read adapter, Data Mapping editable CRUD, or CSV v2 loader/exporter. |
| `2026-07-05-arc14b-runtime-mapping-repository-read-adapter.md` | active reference | Switch Data Mapping Manager default loading to the runtime mapping repository through a Qt-free read adapter while keeping write/reload actions disabled. | `core/mapping/entity_runtime_adapter.py`, `apps/train/services/data_mapping_service.py`, `docs/WORK_PLAN.md` | Reviewing Arc 14B-2 runtime adapter evidence or planning Data Mapping editable CRUD / CSV v2 persistence work. |
| `2026-07-01-korea-notebook-entry-subarc-spec.md` | active reference | Add KOREA as a top-level calculator notebook tab through scoped slices for CSPF/HSPF single UI, midpoint guide, batch, and detail surfaces while preserving KS C 9306 core contracts. | `docs/designs/2026-07-01-korea-notebook-entry-subarc-spec.md`, `docs/WORK_PLAN.md`, calculator UI/application owners | Implementing or reviewing KOREA calculator notebook entry slices. |

## Update Triggers

Update this README when:

- a new `docs/designs/*.md` record is added;
- a design record lifecycle status changes;
- a rule is absorbed into or moved between owner docs;
- a design record is referenced as if it were an active rule owner;
- `ACTIVE_DOCUMENTS.md`, `docs/WORK_PLAN.md`, or `AGENT_TASK_ROUTER.md`
  changes how design records are discovered.

Do not update or read this index for ordinary coding tasks unless the task
depends on prior design decisions.
