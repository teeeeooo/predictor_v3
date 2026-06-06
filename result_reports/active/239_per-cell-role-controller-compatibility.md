# 239 Per-Cell Role Controller Compatibility

## Goal

Connect the batch two-row matrix per-cell role/applicability foundation to the
existing table controller flow without building a Tk matrix UI skeleton.

## Scope

- Add a minimal common controller compatibility path for per-cell role
  resolution.
- Keep existing row-per-case batch surfaces on the column-role fallback path.
- Verify paste, clear, undo, and copy behavior with a headless fake matrix
  surface.
- Keep Hong Kong CSPF UI, handlers, calculator core, export, and migration out
  of scope.

## Non-goals

- No Tk two-row matrix widget/table skeleton.
- No Hong Kong CSPF batch UI migration.
- No copy-all, CSV export, xlsx export, or export data contract.
- No calculator core, region config, profile registry, golden fixture, or
  existing expected changes.

## Current Controller / Surface Inventory

- `TkTableController` owned selection, paste, clear, undo, copy/navigation, and
  editability checks.
- Before this slice, mutation and copy helpers resolved role by column through
  `cell_roles()[column]`.
- Column-role resolution remains correct for existing row-per-case batch
  surfaces, where a whole column is editable, read-only, result, or disabled.
- Two-row matrix layout needs per-physical-cell resolution because the same
  visible column can be editable on one physical row, blank read-only on another,
  result-only on the first row, or not-applicable on the second row.

## Compatibility Design

- `ui_tk.table.interaction_core` now exposes by-role resolver variants for
  copy, clear, and paste target calculation.
- Existing column-role helper APIs remain as wrappers over the new resolver
  variants.
- `TkTableController` resolves roles through an optional `cell_role(position)`
  hook when a surface provides it, otherwise it falls back to
  `cell_roles()[column]`.
- `ui_tk.table.surface` documents this optional contract as
  `PerCellRoleTableSurface`.
- Copy and selection continue to operate on physical rectangular grid positions;
  only mutation eligibility changes from column-role-only to per-cell capable.

## MVC / SoC Boundary

- The controller still owns interaction state and applies paste/clear/copy
  behavior.
- The table surface owns cell role facts for its physical grid.
- The matrix model/spec owns logical-case to physical-cell mapping only.
- No profile-specific Hong Kong input keys were added to the controller.
- No keyboard, mouse, clipboard, or widget responsibilities were added to the
  matrix model.

## Tests

- Added `tests/test_ui_tk_table_controller_per_cell_roles.py`.
- The fake matrix surface uses `HONG_KONG_CSPF_MATRIX_SPEC` and provides
  `cell_role(position)`.
- Covered behaviors:
  - paste mutates editable input cells only;
  - Case cells, result cells, blank read-only cells, and not-applicable cells
    are skipped by paste/clear;
  - selected-range fill paste across two physical rows writes only editable
    physical cells;
  - clear creates an undoable mutation group without changing skipped cells;
  - copy preserves physical rectangular TSV shape, including blank second-row
    Case/result positions.

## Existing Behavior Regression Check

- Existing row-per-case batch controller tests still pass.
- Existing Hong Kong CSPF batch spec tests still pass.
- Row-per-case surfaces do not need to implement `cell_role(position)` because
  the controller fallback path still uses `cell_roles()[column]`.

## Verification

- `python -m pytest tests/test_ui_tk_table_controller_per_cell_roles.py` - pass
- `python -m pytest tests/test_ui_tk_batch_matrix_models.py` - pass
- `python -m pytest tests/test_ui_tk_batch_table_controller.py` - pass
- `python -m pytest tests/test_ui_tk_hong_kong_cspf_batch_spec.py` - pass
- `python3 -B tools/check_code_structure.py` - pass with existing soft LOC
  warning for `ui_tk/sections/bin_detail_panel.py`
- `python3 -m py_compile ui_tk/table/interaction_core.py ui_tk/table/controller.py ui_tk/table/surface.py tests/test_ui_tk_table_controller_per_cell_roles.py` - pass
- `git diff --check` - pass
- `git status --short` - checked before commit

## Changed Files

- `ui_tk/table/interaction_core.py`
- `ui_tk/table/controller.py`
- `ui_tk/table/surface.py`
- `tests/test_ui_tk_table_controller_per_cell_roles.py`
- `docs/WORK_PLAN.md`
- `project_log.md`
- `result_reports/active/239_per-cell-role-controller-compatibility.md`

## Known Failures / Risks

- This is a headless controller/surface compatibility slice only. It does not
  prove visual layout, focus traversal over real Tk widgets, or Windows GUI
  behavior for a future two-row matrix table.
- Undo coverage is limited to clear in the fake-surface harness; paste target
  filtering is covered, but a future Tk skeleton should keep undo coverage in
  its controller tests once real widgets exist.

## Next Suggested Action

Build the Tk two-row matrix table skeleton on top of this controller/surface
contract, still without migrating the current Hong Kong CSPF row-per-case batch
dialog until the skeleton is guarded.

## Scope Compliance

- Did not modify `ui_tk/batch_case_table.py`.
- Did not modify `ui_tk/batch_table_viewport.py`.
- Did not modify Hong Kong CSPF batch section/spec/handler owner files.
- Did not modify calculator core, region config, profile registry, golden
  fixtures, or existing expected values.
- Did not implement Tk matrix UI, migration, copy-all, CSV export, or xlsx
  export.

## Commit / Push

- Final commit hash and push result are recorded in the final response to avoid
  a self-referential report update loop.

## Project Memory Delta

- type: decision
  topic: Batch two-row matrix controller compatibility
  content: The common Tk table controller supports optional per-cell
    `cell_role(position)` role resolution while preserving the existing
    `cell_roles()[column]` fallback for row-per-case surfaces.
  keywords:
    - batch-matrix
    - table-controller
    - per-cell-role
    - row-per-case-compatibility
  assertionStatus: verified
  source: result_reports/active/239_per-cell-role-controller-compatibility.md
