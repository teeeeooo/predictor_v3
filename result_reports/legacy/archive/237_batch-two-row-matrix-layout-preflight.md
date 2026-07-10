# 237 Batch Two-row Matrix Layout Preflight

## Goal

Decide whether the current Hong Kong CSPF row-per-case batch table should stay
as-is or move toward a unified two-row matrix layout before the next batch
expansion. This is a design/preflight report only; no UI/code/test
implementation was performed.

## Scope

- Reviewed current batch model, controller, viewport, Hong Kong CSPF batch
  spec/section, and focused batch tests.
- Checked table interaction and input/result surface owner docs for selection,
  paste, copy, read-only result protection, validation/status, and Tk adapter
  constraints.
- Produced a layout contract, MVC/SoC boundary judgment, and implementation
  slice order.

## Non-goals

- No code or test edits.
- No batch two-row foundation implementation.
- No Hong Kong CSPF migration.
- No copy-all / CSV export implementation.
- No xlsx export.
- No calculator core, region config, profile registry, golden fixture, or
  expected-result changes.

## Current Architecture Inventory

### Toolkit-neutral-ish model

- `BatchProfileSpec` defines flat columns and default rows.
- `BatchColumnRole` is column-based: `INPUT`, `RESULT`, `STATUS`.
- `BatchTableModel` stores `rows: list[dict[str, str]]`; each row is one
  logical calculation case.
- `BatchTableModel.input_values(row_index)` returns the input key subset for
  one logical row.
- `set_results(row_index, values)` only permits result/status keys.

Current implication: row identity, editable input storage, result storage, and
calculation index are all the same row index. This is simple for row-per-case
but does not directly model two physical rows per case.

### Tk view / interaction surface

- `BatchCaseTable` owns the Tk Entry/Label grid, table rebuilds, snapshots,
  row add/remove, result variable updates, and viewport sync.
- `BatchCaseTable.row_count()` returns `len(model.rows)`.
- `BatchCaseTable.cell_roles()` maps column roles to common `CellRole`s.
- `set_positions_batch()` translates controller positions to flat
  `(row, column) -> model.rows[row][column_key]` writes and skips non-input
  columns.
- `BatchTableController` is a compatibility wrapper around
  `TkTableController`; the real selection, copy, paste, clear, undo, keyboard
  navigation, and replace-on-type behavior is in `ui_tk.table.controller`.
- `BatchTableViewport` owns vertical scroll containment and wheel routing.

Current implication: the common controller can remain valuable, but the surface
contract is currently column-role oriented. A two-row matrix needs per-cell
role/applicability or a matrix adapter that can answer equivalent questions per
position.

### Hong Kong CSPF batch wiring

- `HONG_KONG_CSPF_BATCH_SPEC` defines one flat case row with input columns:
  `declared_capacity`, `full_capacity`, `full_power`, `half_capacity`,
  `half_power`; result columns: `cspf`, `csec`; no status columns.
- `HongKongCspfBatchHandler.calculate_row(row)` turns one input dict into the
  existing single-case CSPF core path and returns `{cspf, csec}` or blanks.
- `HongKongCspfBatchSection` builds `BatchCaseTable`, wires
  `BatchCalculationController`, debounced recalculation, Add Row / Remove Row,
  and a compact dialog-level valid/blank/invalid summary.
- `HongKongCspfBatchDialog` owns the Toplevel lifecycle and close snapshot.
- The parent `HongKongCspfSection` stores session-local batch snapshots across
  close/reopen.

Current implication: calculation and state persistence already have good
separation. The migration risk is primarily table data shape and surface
address mapping, not calculator logic.

## Two-row Layout Feasibility

Decision: **Accept with constraints**.

The two-row matrix shape is a better long-term fit than preserving
row-per-case for future batch expansion because it groups capacity/performance
and power at the same measurement points, reduces repeated labels, and keeps
profile outputs as case-level result metrics. It should not be implemented by
duplicating the current flat row model into two independent rows.

### Accepted layout contract

- One logical case maps to exactly two physical table rows.
- Fixed leading columns:
  - `Case`: read-only/copyable case identity, shown once or merged-looking
    across the pair.
  - `Row Type`: read-only/copyable label, e.g. `Capacity`/`Power` or
    `Performance`/`Power`.
- Measurement point columns are profile-defined. Candidate point labels include
  `Declared`, `46 Full`, `35 Full`, `35 Half`, `35 Min`, etc. A profile may
  mark some row/point cells as not applicable.
- Hong Kong CSPF initial mapping should be:
  - logical case field `declared_capacity` appears in a case/measurement column
    applicable to the capacity/performance row only;
  - `35 Full` maps capacity row to `full_capacity` and power row to
    `full_power`;
  - `35 Half` maps capacity row to `half_capacity` and power row to
    `half_power`;
  - no default `Status` output column;
  - result metrics remain `CSPF` and `CSEC`.
- Result columns are case-level profile outputs. They should be read-only and
  copyable. Prefer displaying values on the first physical row of the pair and
  using disabled/blank or visually merged-looking cells on the second row to
  avoid duplicate metric values in copy/export.
- Status/error state belongs outside default result metric columns:
  - row/case state in the model;
  - subtle styling on the case or row labels;
  - compact dialog-level summary;
  - optional validation summary later if batch semantics need it.

### Logical / physical mapping

- `logical_case_index = physical_row_index // 2`.
- `physical_row_type = capacity/performance` for even physical rows and `power`
  for odd physical rows.
- Every write target maps through `(logical_case, physical_row_type,
  measurement_column) -> input_key | not_applicable`.
- Every result display maps through `(logical_case, result_metric_column)`.
- Snapshot/restore should be logical-case based, not physical-row based, so a
  later visual layout change does not corrupt persisted dialog state.

### Add / remove behavior

- Add and remove operate on logical cases, not physical rows.
- Add Case creates one logical case and two physical rows, then scrolls to the
  bottom of the viewport.
- Remove removes the last logical case pair and preserves the minimum one case
  rule.
- Paste that extends beyond the current physical row count may create logical
  cases, but it must always create complete physical row pairs.

### Paste behavior

- Keep the Excel-like TSV contract: paste anchors at the selection top-left,
  single-cell source repeats over the selection, a one-row source matching
  selection width fills down, larger sources write outward, and out-of-bounds
  cells are dropped or case-created by an explicit surface policy.
- Editable targets are only input cells whose `(row_type, point)` maps to an
  input key.
- Read-only case labels, row type labels, result metric cells, and
  not-applicable cells are skipped by paste/clear.
- Pasting into result columns must not mutate result storage.
- A paste spanning capacity/performance and power rows is valid when each cell
  maps to an editable input key.
- Invalid pasted values should follow current calculation-batch policy: keep
  row/case result blank or styled while valid rows calculate independently;
  do not turn partial typing into noisy per-cell errors.

### Copy / future export contract

- Copy remains rectangular TSV over the physical grid.
- Read-only result cells are included in copy as rendered values.
- Disabled/not-applicable blank cells should copy as blanks only if they are
  inside the selected rectangle; this preserves rectangular TSV shape.
- The later export hook should expose logical cases plus profile result metrics,
  not just raw physical rows. A separate physical-grid TSV copy can remain the
  controller clipboard behavior.
- CSV export parity is a later slice. xlsx remains deferred.

### Compatibility with existing table contract

The layout is compatible with the toolkit-neutral table contract only if the
new foundation exposes per-cell roles/applicability. The current
`cell_roles() -> tuple[CellRole, ...]` column-only contract is insufficient
because a measurement point column can be editable in one physical row and
editable/different-key/not-applicable in the paired row, while result columns
are case-level display.

## MVC / SoC Boundary Judgment

### Data model

Owns:

- logical case count and case identity;
- profile matrix spec: physical row types, measurement point columns, result
  metric columns, row/point-to-input-key mapping;
- input value storage by logical case and input key;
- result metric storage by logical case and metric key;
- validation/calculation state by logical case.

Should not own:

- Tk widgets;
- keyboard selection state;
- clipboard text;
- calculator core calls.

### Controller

Owns:

- active/anchor selection over the physical grid;
- edit, replace-on-type, paste, clear, undo, keyboard navigation;
- conversion from selected physical positions to model write targets through
  surface-provided role/applicability mapping;
- Add Case / Remove Case commands at logical-case granularity.

The existing `TkTableController` can likely stay as the interaction owner if
the surface protocol is extended or adapted to expose per-cell roles. Avoid
forking another batch-only controller unless a focused helper test proves the
common controller cannot express the matrix semantics.

### View

Owns:

- rendering two physical rows per logical case;
- showing Case and Row Type labels;
- merged-looking case identity and result metric cells where practical;
- input Entry widgets only for editable cells;
- read-only/disabled display for result and not-applicable cells;
- viewport containment and mouse-wheel behavior via the existing
  `BatchTableViewport` pattern.

The view should not translate physical-row values into calculator inputs by
itself; it should delegate through the matrix model/spec.

### Calculation adapter

Owns:

- converting one logical case into the current profile row dict expected by
  `HongKongCspfBatchHandler.calculate_row()`;
- calling the profile handler/controller;
- writing profile output metrics back to the logical case result storage.

For Hong Kong CSPF, the adapter maps the two physical rows back to the current
flat keys: `declared_capacity`, `full_capacity`, `full_power`,
`half_capacity`, `half_power`. The existing calculator path and expected result
values stay unchanged.

## Accepted Layout Contract

Decision: **Accept with constraints**.

Adopt the unified two-row matrix direction for the next implementation arc, but
only after introducing a small foundation/model surface boundary. Do not
migrate Hong Kong CSPF directly by reshaping `BatchCaseTable` in place.

Constraints:

- Keep row-per-case `BatchCaseTable` stable until the matrix foundation has
  headless model/controller tests.
- Keep result columns metric-only (`CSPF`, `CSEC` for Hong Kong CSPF).
- Do not add a default Status column.
- Keep status/error state in case state, styling, compact summary, or a later
  validation summary.
- Keep copy/export implementation out of the first foundation slice.
- Avoid a large generic framework; implement only enough profile matrix spec
  metadata to represent Hong Kong CSPF and foreseeable EN/AHRI/KS measurement
  point layouts.

## Next Implementation Slices

### Slice 1 - Matrix model/spec and mapping helpers

Target files:

- new focused model/helper module under `ui_tk/` if needed;
- focused tests for mapping only.

Work:

- Define matrix spec concepts: logical case, physical row type, measurement
  point, result metric, cell applicability, and row/point-to-input-key mapping.
- Add headless tests for Hong Kong CSPF mapping:
  - one logical case -> two physical rows;
  - editable input address mapping;
  - not-applicable cells;
  - result metric storage;
  - logical snapshot/restore.

Do not build Tk UI in this slice.

### Slice 2 - Per-cell role surface/controller compatibility

Target files:

- common table interaction helper/protocol if needed;
- fake-surface controller tests.

Work:

- Extend or adapt the table surface contract so mutation/copy/selectability can
  be determined per physical cell, not only per column.
- Preserve existing row-per-case batch controller behavior.
- Verify paste/clear/undo skips read-only result and not-applicable cells.
- Verify selected-range fill paste across two physical rows.

Do not migrate Hong Kong CSPF UI yet.

### Slice 3 - Tk two-row matrix table skeleton

Target files:

- new matrix table view/surface module;
- reuse `BatchTableViewport`.

Work:

- Render fixed Case / Row Type columns, measurement point columns, and result
  metric columns.
- Implement Add Case / Remove Case over logical cases.
- Keep result display read-only and copyable.
- Keep compact status summary outside metric columns.
- Add focused Tk/fake tests where possible; use headless tests for mapping and
  controller semantics first.

Do not implement copy-all/CSV export.

### Slice 4 - Hong Kong CSPF migration

Target files:

- Hong Kong CSPF batch spec/section owner files;
- focused Hong Kong CSPF batch tests.

Work:

- Introduce the Hong Kong matrix spec using the two-row contract.
- Adapt the calculation adapter so one logical case still feeds the current
  `HongKongCspfBatchHandler` flat input dict.
- Preserve CSPF/CSEC result values and close/reopen snapshot behavior.
- Preserve batch dialog sizing, viewport containment, and wheel parity.

### Slice 5 - Batch copy/export parity follow-up

Target files:

- batch export data contract;
- clipboard/CSV helper integration.

Work:

- Define logical-case export rows and physical-grid copy behavior explicitly.
- Reuse existing `table_clipboard` / `table_csv_export` direction.
- Keep xlsx export deferred.

## Excluded Scope

- No implementation.
- No tests modified.
- No UI migration.
- No copy/export implementation.
- No xlsx export.
- No calculator/core/profile/config/golden changes.
- No BaseSection or broad framework.

## Validation

- `git diff --check`: PASS.
- `git status --short`: expected docs/report changes only before commit:
  `docs/WORK_PLAN.md`, `project_log.md`,
  `result_reports/active/237_batch-two-row-matrix-layout-preflight.md`.
- Not run by design:
  - pytest
  - py_compile
  - GUI smoke
  - calculator smoke

## Documentation Sync

- `docs/WORK_PLAN.md`: update needed because Next should move from preflight
  to the first implementation slice.
- `project_log.md`: update needed because this preflight makes a durable layout
  decision.
- `result_reports/memory/project_memory_seed.md`: not updated; this is an
  active preflight report, not a summary lifecycle or explicit memory
  maintenance task.
- `docs/designs/`: not created. The active report is sufficient for this
  preflight; a design record can be added later if the matrix foundation becomes
  a broader cross-profile architecture record.
- `ACTIVE_DOCUMENTS.md`: not needed; no active document owner relationship
  changed.

## Project Memory Delta

- type: decision
  topic: batch two-row matrix layout contract
  content: Accept the unified two-row matrix direction with constraints. One
    logical case maps to two physical rows, result columns remain profile output
    metrics, status is not a default result column, and the first
    implementation slice should introduce matrix model/spec mapping before Tk
    migration.
  keywords:
    - batch table
    - two-row matrix
    - logical case
    - result metrics
    - Hong Kong CSPF
  assertionStatus: verified

## Commit / Push

- Commit: final pushed hash recorded in final response to avoid report
  self-reference hash loops.
- Push: final response.
