# Legacy Design Records

## Role And Read Rule

This index covers design records that no longer belong in the active design
root. Search by topic or keyword and read one matching record only when current
owner docs, source, tests, or Git history do not provide enough context. These
records are not default reads.

Statuses:

- `absorbed`: durable rules moved into current owner documents.
- `deferred-resume`: intentionally paused work that may resume from this record.
- `superseded`: a newer design or owner contract replaced this direction.
- `completed`: the designed slice was implemented or formally closed.

Moved bodies are byte-preserved historical evidence and may contain old root
paths, statuses, or self-links. The current physical path and this index win
over historical path literals inside a moved body.

## Index

| Record | Status | Reason | Read when |
| --- | --- | --- | --- |
| `2026-05-06-iso16358-2-hspf-core-boundary.md` | absorbed | ISO HSPF boundaries live in architecture/standard owners. | Auditing the original core boundary. |
| `2026-05-10-iso16358-2-hspf-h8-routing-resolver-design.md` | absorbed | H-8 routing rules moved to ISO implementation owners. | Investigating original resolver intent. |
| `2026-05-17-calculator-horizontal-table-input-ui.md` | absorbed | Table/input rules live in UI/UX owners. | Tracing the original matrix decision. |
| `2026-05-22-calculator-action-model-alignment.md` | absorbed | Action behavior is owned by current UI contracts. | Reviewing auto-calc history. |
| `2026-05-22-calculator-ui-module-boundary.md` | absorbed | Calculator UI boundaries moved to architecture owners. | UI module-boundary archaeology. |
| `2026-05-23-tkinter-calculator-final-ux-contract.md` | absorbed | Target UX is captured by current input/result owners. | Reviewing original Tkinter UX intent. |
| `2026-05-29-tkinter-iso-iseer-2point-result-visual-refinement.md` | absorbed | Comparison presentation lives in result-surface policy. | Tracing visual comparison rationale. |
| `2026-05-30-tkinter-excel-like-table-contract-recovery.md` | absorbed | Table parity lives in the table contract/adapters. | Investigating table UX recovery. |
| `2026-05-30-tkinter-result-surface-export-boundary.md` | absorbed | Result/export boundaries live in current UI owners. | Tracing export boundary history. |
| `2026-06-10-en14825-declared-tested-gui-contract.md` | absorbed | EN GUI rules are in standard and UI owners. | Reviewing declared/tested GUI origins. |
| `2026-06-11-en14825-scop-gui-integration-design.md` | absorbed | SCOP integration behavior is implemented and owned. | Investigating initial integration design. |
| `2026-06-21-calculator-window-profile-lifecycle-audit.md` | absorbed | Lifecycle findings moved to window/profile owners. | Reviewing the original lifecycle audit. |
| `2026-06-21-en14825-ahri-detail-view-design.md` | absorbed | Detail behavior is owned by result-surface contracts. | Tracing detail-view decisions. |
| `2026-06-21-profile-visible-content-lifecycle-controller-design.md` | absorbed | Visible-content lifecycle has active owners. | Auditing controller design origins. |
| `2026-06-21-ui-magic-literal-legacy-inventory.md` | absorbed | Literal policy moved to active change gates/tokens. | Investigating grandfathered UI literals. |
| `2026-05-08-asnzs-hspf-excel-compat-boundary.md` | deferred-resume | AS/NZS workbook compatibility remains paused. | Resuming AS/NZS compatibility work. |
| `2026-05-30-tkinter-detail-trace-graph-result-surface-design.md` | deferred-resume | Internal trace/graph follow-up remains deferred. | Resuming trace or graph surfaces. |
| `2026-06-21-calculator-sample-data-empty-state-policy.md` | deferred-resume | Sample/empty-state follow-up awaits its trigger. | Resuming sample/default removal work. |
| `2026-06-30-arc13-ml-feature-manifest-design-gate.md` | superseded | Data Definition replaced Feature Manifest ownership. | Reviewing the pre-owner-switch design. |
| `2026-07-01-arc13-5-feature-catalog-editor-design-gate.md` | superseded | Feature Catalog is now legacy compatibility/read/export. | Reviewing the former editor direction. |
| `2026-07-02-arc13-5-feature-catalog-editor-revised-slice-plan.md` | superseded | Revised editor slices no longer govern schema work. | Auditing old Arc 13.5 sequencing. |
| `2026-07-02-arc13-5a-feature-catalog-manager-correction-design.md` | superseded | Data Definition owns feature-definition changes. | Reviewing manager correction history. |
| `2026-07-03-arc13-5r-predict-schema-mapping-manager-foundation.md` | superseded | Later Data Definition/mapping owners replaced it. | Tracing schema/mapping foundation history. |
| `2026-07-03-arc13-5r-predict-schema-v2-field-spec-confirmation.md` | superseded | Current schema owner now holds field rules. | Auditing v2 field decisions. |
| `2026-07-03-arc13-5r-projection-owner-switch.md` | superseded | Later owner switch and implementation replaced it. | Reviewing projection transition history. |
| `2026-07-03-arc13-5r-readonly-schema-v2-projection-parity.md` | superseded | Read-only parity was an intermediate stage. | Reviewing parity evidence. |
| `2026-05-17-iso-remaining-work-completion.md` | completed | The scoped ISO completion phase closed. | Auditing old completion scope. |
| `2026-05-22-lightweight-calculator-ui-feasibility.md` | completed | The calculator feasibility direction was implemented. | Reviewing feasibility/packaging origins. |
| `2026-05-24-pyqt-calculator-reference-feature-migration-contract.md` | completed | Reference migration contract served its transition. | Reviewing calculator parity history. |
| `2026-05-29-tkinter-iso-iseer-2point-single-design.md` | completed | The 2-point single surface was delivered. | Auditing its original slice. |
| `2026-05-29-tkinter-saso-t3-profile-design.md` | completed | The SASO T3 profile slice was delivered. | Reviewing SASO implementation intent. |
| `2026-06-20-ahri-210-240-ui-batch-design-specification.md` | completed | AHRI UI/batch contract was implemented. | Auditing AHRI UI/batch history. |
| `2026-06-27-pyside6-visual-table-parity-harvest.md` | completed | Visual parity evidence was harvested and consumed. | Reviewing legacy visual evidence. |
| `2026-06-28-arc10-prediction-worker-progress-design.md` | completed | Prediction worker/progress slices were completed. | Auditing Arc 10 behavior. |
| `2026-06-28-arc11-predict-train-hexagonal-boundary-reopen.md` | completed | The reopened boundary correction closed. | Reviewing Arc 11 reopening rationale. |
| `2026-06-28-arc11-train-execution-boundary-design.md` | completed | Train execution boundary work completed. | Auditing training execution design. |
| `2026-06-28-arc12-calculator-usecase-boundary-audit.md` | completed | Calculator usecase correction completed. | Reviewing Arc 12 audit evidence. |
| `2026-07-01-korea-notebook-entry-subarc-spec.md` | completed | The KOREA notebook sub-arc completed. | Auditing KOREA entry slices. |
| `2026-07-03-arc14a-mapping-entity-master-data-foundation.md` | completed | Mapping entity/master-data foundation completed. | Reviewing Arc 14A scope. |
| `2026-07-03-arc14b-data-mapping-manager-ui-foundation.md` | completed | Data Mapping UI foundation completed. | Reviewing Arc 14B foundation. |
| `2026-07-05-arc14b-runtime-mapping-repository-read-adapter.md` | completed | Runtime read adapter completed. | Auditing mapping read ownership. |
| `2026-07-05-arc14b4-legacy-mapping-csv-to-json-rule-reconstruction-audit.md` | completed | Reconstruction audit reached its decision. | Reviewing rejected import recovery. |
| `2026-07-05-arc14b5-data-mapping-ui-crud-workflow-design.md` | completed | CRUD workflow design was implemented/closed. | Auditing CRUD interaction intent. |
| `2026-07-05-arc14c-runtime-cascade-integration.md` | completed | Runtime cascade integration completed. | Reviewing cascade decisions. |
| `2026-07-06-arc14d-data-mapping-xlsx-export-ui-polish.md` | completed | XLSX export/UI polish completed. | Auditing Arc 14D behavior. |
