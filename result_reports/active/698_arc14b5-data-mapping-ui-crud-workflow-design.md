# Arc 14B-5A Data Mapping UI CRUD Workflow Design

## Goal

Document the user-facing Data Mapping Manager CRUD workflow before
implementation. The design defines Data Mapping Manager as a Predict input
mapping administration screen, not a raw `mapping.json` editor, generic
entity/attribute/value editor, or export/import spreadsheet editor.

## Files Read

- `AGENT_TASK_ROUTER.md`: Design First, Result Report, Docs Sync, Commit, and
  Notes routing sections.
- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`
- `docs/agent_workflows/DOCUMENT_SYNC_AND_LIFECYCLE.md`
- `docs/WORK_PLAN.md`
- `docs/designs/README.md`
- `docs/designs/2026-07-05-arc14b4-legacy-mapping-csv-to-json-rule-reconstruction-audit.md`
- `docs/designs/2026-07-05-arc14b-runtime-mapping-repository-read-adapter.md`
- `result_reports/active/697_arc14b4-legacy-mapping-csv-to-json-rule-reconstruction-audit.md`
- `result_reports/active/696_data-mapping-user-facing-copy-simplification.md`
- `result_reports/active/693_arc14b-runtime-source-visibility-and-row-identity.md`
- `result_reports/active/692_arc14b-runtime-mapping-repository-read-adapter.md`
- Focused owner/function ranges from `core/mapping/update.py`,
  `core/mapping/autofill.py`, `core/mapping/entity_model.py`,
  `core/mapping/entity_runtime_adapter.py`, `core/mapping/entity_validation.py`,
  `apps/train/services/data_mapping_service.py`,
  `apps/train/controllers/data_mapping_controller.py`,
  `apps/train/ui/data_mapping_panel.py`,
  `apps/train/ui/data_mapping_view_models.py`,
  `apps/predict/adapters/dropdown_option_adapter.py`,
  `apps/predict/controllers/input_edit_controller.py`, and
  `config/predict/schema.csv`.

## Design Decisions

| Area | Decision |
| --- | --- |
| User unit | Edit user-facing Predict mapping groups, not internal runtime sections. |
| Main UX | Groups, Data, Issues, concise status, and file display. `Fields` is not a prominent main edit surface. |
| Import | Excluded or long-term disabled; any future import needs an explicit compatibility-parser design. |
| Export | Read-only review snapshot only; no export-edit-reimport contract. |
| Save | Validation-gated, backup plus temp write plus atomic replace, owned below UI. |
| Reload | Discards draft after confirmation when dirty. |
| Dirty state | Draft edits set dirty true; successful Save clears dirty. |

## User-facing Groups

- IDU
- Evap Index
- ODU
- Compressor
- Refrigerant
- Expansion
- ODU Cond Specs

## ODU Cond Specs Policy

ODU Cond Specs is one user-facing table with columns:

- `ODU`
- `Fin Type`
- `Pi`
- `Row`
- `Cond Area`
- `Cond Volume`

It generates these runtime sections:

- `odu_cascade`
- `cond_specs`
- `fin_type`
- `pi`
- `row`

Users do not edit `Available_Fins`, `Available_Pis`, `Available_Rows`, or the
`ODU Fin Pi Row` composite key directly. Duplicate composite keys are blocking
Issues.

## Save / Reload / Export / Import Policy

- Save: validation must pass; create backup; temp write; atomic replace; dirty
  false after success; UI never writes raw JSON directly.
- Reload: discard draft and reload `mapping.json`; dirty state requires
  confirmation.
- Export: read-only snapshot. XLSX workbook is the human-review candidate;
  pretty JSON is the exact backup/debug candidate.
- Import: excluded until an explicit future compatibility parser decision.

## Internal Boundary

| Layer | Responsibility |
| --- | --- |
| `core/mapping` | Runtime JSON load/save owner, draft model candidate, draft/runtime projection, validation, ODU Cond Specs derived section generation. |
| `apps/train/services` | Load draft, apply edit commands, provide validation result, dirty state, save/reload/export workflow. |
| `apps/train/controllers` | Convert service state into UI table state and forward UI commands. |
| `apps/train/ui` | Display and user input only; no raw JSON parse/write. |

Candidate model/helper names were suggested in the design note only as
implementation aids, not as fixed public APIs.

## Implementation Slices

1. Arc 14B-5B: editor draft projection, runtime `mapping.json` to user-facing
   groups, read-only projection only.
2. Arc 14B-5C: draft validation, Issues generation, Save enable judgment.
3. Arc 14B-5D: editable table commands, Add Row / Duplicate / Delete / Edit
   Cell, dirty state.
4. Arc 14B-5E: Save with backup and atomic write.
5. Arc 14B-5F: Export read-only snapshot.

Import remains excluded.

## Validation

- `git diff --check`: OK.
- `python3 -B tools/check_code_structure.py`: OK with existing soft warnings
  only; this slice changed docs/report files and added no source files.
- `git status --short`: expected docs/design/report changes only before
  staging.
- `py_compile` / `pytest`: not run because this task changes docs/report only
  and production code/tests/data fixtures remain untouched.

## Excluded Scope

- No production code changes.
- No UI implementation.
- No editable CRUD implementation.
- No Import, Export, Save, Reload, runtime reload, or `mapping.json` write.
- No runtime cascade integration.
- No CSV import/export contract.
- No multi-file package.
- No normalized `values.csv`.
- No schema/public API changes.
- No tests, fixtures, golden expected changes, or unrelated refactor.

## Manual Check Required

No manual GUI check is required for this documentation-only slice.

## Next Action

Arc 14B-5B - implement editor draft projection from runtime `mapping.json` to
the seven user-facing groups in read-only mode.

## Commit / Push Note

Final commit/push result will be reported in terminal output.

## Project Memory Delta

- type: decision
  topic: Arc 14B Data Mapping UI CRUD workflow
  content: Data Mapping Manager editable workflow should expose user-facing Predict mapping groups, with ODU Cond Specs generating internal cascade/spec sections; Import is excluded, Export is read-only snapshot, and Save/Reload must stay below the UI raw JSON boundary.
  keywords: predictor_v3, Arc 14B, Data Mapping, CRUD, ODU Cond Specs, mapping.json
