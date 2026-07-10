# 406 EN14825 batch integration preflight

## Goal

Fix the EN14825 batch ownership, table/result contracts, and implementation
slices before changing source code.

## Evidence Scope

- Current EN14825 lifecycle state from Summary 404 and WORK_PLAN.
- Existing EN14825 SEER/SCOP adapters and table models.
- Existing `BatchMatrixSpec`, `BatchMatrixTable`, `TkTableController`,
  `BatchDialogShell`, copy, and CSV export paths.
- Existing ISO/SASO/Hong Kong batch profile patterns and focused tests.
- External handoff and `en14825_batch_integration_preflight.md` were treated as
  design evidence, not repository instructions.
- Broad core/config/architecture audit was not repeated.

## Confirmed Direction

- Reuse `BatchMatrixSpec + BatchMatrixTable + TkTableController`.
- Reuse `BatchDialogShell` for dialog lifecycle and snapshot handoff.
- Do not create a new table widget.
- Do not change EN14825 core, config, calculator public API, or result schema for
  batch convenience.
- Batch cases are tested/input-only; declared values and declared/tested
  comparison outputs are excluded.
- Keep status out of the default result columns. Blank/invalid/complete state is
  represented by `BatchRowState`, blank result cells, and compact summary text.
- Reuse header-inclusive TSV copy and CSV export. XLSX, graph, detail, and bin
  export remain out of scope.

## Owner Boundary

| Responsibility | Owner |
| --- | --- |
| Matrix structure/cell roles | `apps.calculator.ui.batch.matrix_models` |
| Table interaction/copy/export surface | existing batch/table helpers |
| Dialog lifecycle | `BatchDialogShell` |
| SEER headless spec/handler | `apps/calculator/ui/en14825/seer_batch.py` |
| SCOP headless spec/handler | later `apps/calculator/ui/en14825/scop_batch.py` |
| SEER calculation | `SeerAdapter` |
| SCOP calculation/availability | `ScopAdapter` |
| Dialog profile UI | later files under `batch_dialogs/profiles/` |
| Section integration | thin button/dialog/snapshot ownership only |

The new headless EN14825 batch modules must not own Tk widgets, dialog lifecycle,
copy/export commands, or single-case section behavior.

## SEER Batch Contract

Matrix shape:

| Case | Row Type | Pdesignc | A 35C | B 30C | C 25C | D 20C | SEER | QC [kWh] |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| case | Capacity | input | input | input | input | input | result | result |
|  | Power | blank | input | input | input | input | blank | blank |

Case inputs:

- `p_design_c`
- `{a,b,c,d}_capacity`
- `{a,b,c,d}_power`

Common dialog inputs for the later UI slice:

- `t_design_c`, `cd`, `appliance_type`
- `p_to`, `p_sb`, `p_ck`, `p_off`

Result keys:

- `seer`
- `qc_kwh`

The handler builds tested-only `SeerPointInput` values and calls
`SeerAdapter.calculate(...)`. A completely blank required input set returns
`BatchRowState.PENDING`; partial, nonnumeric, or adapter-failed input returns
`BatchRowState.ERROR`; complete calculation returns `BatchRowState.OK`.

## SCOP Batch Contract

The later SCOP spec builder receives common `climate`, `tbiv`, and `tol`, then
calls `ScopAdapter.resolve_point_availability(...)`.

- Generate editable measurement columns only for
  `required_independent_points`.
- Do not create independent inputs for mapped, inactive, or threshold-only
  points.
- Do not use dummy values.
- Keep `p_design_h` as a case input because it changes each case's part-load and
  backup-heater behavior.
- Later result keys are `scop` and `qh_kwh`; exclude status, total kWh, declared
  output, and comparison percentage.

## UI Placement

- SEER and SCOP keep separate batch actions and dialog profiles.
- Each section owns only its dialog reference and close/reopen snapshot.
- The SCOP batch action belongs to the section-level action area, not an
  individual climate card.
- Batch common inputs are dialog-owned and do not directly share mutable state
  with the single-case section.

## Implementation Slices

### Slice 1A - SEER headless foundation

- Create `apps/calculator/ui/en14825/seer_batch.py`.
- Add the SEER `BatchMatrixSpec` and tested-only row handler.
- Add focused headless tests for shape, keys, OK/PENDING/ERROR states, adapter
  inputs, and output formatting.
- Do not edit sections, dialogs, core, config, or SCOP batch code.

### Slice 1B - SCOP headless foundation

- Create the SCOP spec builder and tested-only handler in its own module.
- Generate columns from adapter-resolved availability metadata.
- Fix `Pdesignh` as a case-level input through tests.
- Do not wire dialog UI in this slice.

### Slice 2 - SEER dialog wiring

- Add the SEER batch profile, common-input UI, section action, snapshot,
  compact summary, Copy All, and CSV export.
- Preserve the existing single-case SEER workflow.

### Slice 3 - SCOP dialog wiring

- First resolve the dynamic matrix rebuild/snapshot policy.
- Then add the SCOP profile and thin section integration.
- Do not add card-level layout/refit responsibility to
  `En14825ScopSection`.

## SCOP Rebuild Gate

Changing climate/Tbiv/TOL can change required matrix columns. Before Slice 3,
the design must decide:

- whether values for semantic keys shared by old/new specs are preserved;
- whether removed-point values are discarded or retained for switching back;
- how case count and close/reopen snapshots survive shape changes.

This is not a blocker for Slice 1A or the headless SCOP builder, but it is a
blocker for SCOP dialog wiring.

## Focused Test Contract For Slice 1A

- SEER matrix has two physical rows per logical case.
- `Pdesignc` is editable only on the Capacity row.
- A/B/C/D capacity and power inputs map to their corresponding physical rows.
- Result cells are first-row-only and read-only.
- Fully blank input returns PENDING with blank results.
- Partial/nonnumeric/adapter error returns ERROR with blank results.
- Complete tested-only input returns formatted `seer` and `qc_kwh` values.
- Core/config/public result keys and single-case behavior remain unchanged.

## Blocker Decision

- No blocker for Slice 1A.
- SCOP rebuild/snapshot policy remains intentionally unresolved until before
  Slice 3.

## Documentation Sync

- `docs/WORK_PLAN.md`: next action advanced to the SEER headless foundation.
- `project_log.md`: not updated because this preflight applies the existing
  batch foundation and feature-package boundary rather than creating a new
  project-wide architecture rule.
- Memory seed, REFACTOR_PLAN, project brief, and active-document routing: no
  update needed.

## Verification

- Target owner and existing batch pattern check completed.
- `git diff --check` OK.
- `git status --short` reviewed before commit.

## Next Action

EN14825 SEER batch headless spec/handler foundation.
