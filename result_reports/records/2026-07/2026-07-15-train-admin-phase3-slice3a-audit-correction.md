record:
  date: 2026-07-15
  topic: train-admin-phase3-slice3a-audit-correction
  tags: train-admin, data-definition, phase-3, slice-3a, audit-correction, save-retry, filter
  memory_review: updated
  memory_reason: Slice 3A now separates plan capability, last Save evidence, and action state and resolves filters before final projection.

# Change Reason

Slice 3A audit found three presentation-state mismatches: recoverable write errors
disabled retry, candidate-validation issues were absent from Focused Detail, and a
removed filter option could display `All` while the inventory still used its stale
value.

# Contract / Behavior Changed

- `can_save_schema` again means only the current save plan's capability. A
  separate UI-facing action state allows retry after writer `error`, blocks an
  unchanged candidate-validation `blocked` draft, and disables clean or
  save-plan-blocked drafts.
- Structured last-result issues are preserved alongside existing Save Result
  diagnostics. Focused Detail combines them with current save-plan blockers,
  deduplicates by issue code, and distinguishes an unchanged selected definition
  from the definition rows that changed.
- Inventory projection resolves category/source/lifecycle selections against
  current canonical metadata before filtering. The panel applies those resolved
  values under signal blocking, so Combo display, visible rows, selection, and
  detail share one deterministic final projection.

# Evidence And Verification

- 18 focused action-state, blocker-projection, and filter-reconciliation tests
  passed, including a one-shot `os.replace` failure followed by successful retry.
- 182 impacted tests passed across Data Definition state/presentation/UI/writer,
  Data Mapping dynamic requirements, Train shell, Predict schema adapters, and ML
  catalog compatibility.
- `tools/check_code_structure.py` reported only the existing unrelated soft
  warnings and no new changed-owner warning.
- Native Computer Use was not rerun, as required by the correction scope.

# Changed Files

- Data Definition state builder, inventory/detail presentation, and panel filter
  wiring
- focused inventory and guarded-save UI tests
- Work Plan, result index, and active memory

# Known Risks

- Candidate validation issues remain writer-owned and identify their schema row
  in the existing message rather than introducing a new persistence or issue
  schema.
- Controlled Add/Edit commands and every Slice 3B+3C behavior remain deferred.
- No production schema, mapping data, configuration, training data, or model
  artifact was changed.
