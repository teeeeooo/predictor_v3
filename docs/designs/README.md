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
