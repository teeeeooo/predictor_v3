# 402 MetricInputTable unavailable cell presentation

## Goal

Correct EN14825 SCOP unavailable input cells so they render as true static table
cells instead of disabled editable Entries.

## Scope

- Added `MetricInputTable.set_readonly_addresses(...)` as a reusable presentation
  API for editable cells that need static/read-only display.
- Switched readonly presentation by hiding the editable Entry and showing a
  same-cell static label with the existing static table background.
- Updated SCOP point availability wiring to use the table API instead of
  directly configuring `editable_entries`.
- Kept SCOP availability calculation, adapter/model logic, core, config, SEER,
  batch, ML, and golden expected values unchanged.

## Table API

- `set_readonly_addresses(addresses, display_values=None)` accepts editable cell
  addresses and returns whether the presentation changed.
- Readonly presentation keeps the Entry widget in normal state but hidden,
  exposes a static label through `cell_widget(...)`, and reports
  `CellRole.READONLY`.
- Restoring editable presentation hides the label, repacks the original Entry,
  restores normal Entry state, and preserves existing invalid/editable visual
  state handling.

## SCOP Usage

- `_apply_point_availability(...)` now blanks unavailable SCOP input values and
  passes unavailable addresses to `MetricInputTable.set_readonly_addresses(...)`.
- The section no longer monkeypatches table `cell_role` or directly disables
  Entry widgets.
- The table controller is refreshed only when presentation widgets change so
  selection/paste bindings stay aligned with the visible widget.

## Expected Visual Behavior

- Warmer A/TOL/Tbiv unavailable input cells are blank static labels with the
  existing static/read-only gray background.
- Required SCOP cells continue to show editable Entry widgets.
- macOS disabled Entry background behavior is no longer part of unavailable cell
  rendering.

## code_map_check

- Pre-edit targeted code map check covered `MetricInputTable`,
  `En14825ScopSection`, `CellRole`, and editable cell references.
- Regenerated `docs/code_map/CODEBASE_REFERENCE_MAP.md` after source LOC/symbol
  changes; the diff is metadata plus updated LOC ordering for the touched UI
  files.

## Verification

- `python3 -B -m py_compile apps/calculator/ui/metric_input_table.py apps/calculator/ui/sections/en14825_scop_section.py`
  OK.
- `python3 -B -m pytest tests/test_ui_tk_metric_input_table_adapter.py tests/test_ui_tk_metric_input_table_validation.py tests/test_ui_tk_metric_input_table_controller_parity.py tests/test_apps_calculator_ui_en14825_scop.py`
  OK: 107 passed.
- `python3 -B tools/check_code_structure.py` OK with existing SEER/SCOP section
  LOC soft warnings.
- `git diff --check` OK.
- `git status --short` reviewed.

## Skipped

- GUI/manual smoke was not run by request.
- Full pytest was not run by request.

## Next Action

EN14825 SCOP UI point availability manual smoke.
