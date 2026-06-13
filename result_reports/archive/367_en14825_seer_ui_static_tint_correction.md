# EN14825 SEER UI Parity Correction & MetricInputTable Static Cell Tint Fix Report

## Goal
* Address layout aesthetics, part-load percentage displays, static cell background tinting bugs, and visual token cleanups.

## Scope / Non-goals
### Scope
* Group auxiliary design specs and standby/aux power variables into separate labeled sub-LabelFrames.
* Correct part-load % display format to integer percent on the UI (e.g., 74%).
* Store and return static label widgets in `MetricInputTable` to allow correct selection/status background coloring.
* Extract the custom pass state color to `TABLE_PASS_BG` in `layout_constants.py` and remove raw hex colors from the section file.

### Non-goals
* No right-side info panel addition.
* No Calculate button or Clear button addition.
* No SCOP or AHRI calculation changes.

## Cause Analysis
* **Static Cell Tinting Issue**: `MetricInputTable.cell_widget` returned the cell container Frame for read-only cells instead of the actual `tk.Label` widget inside. Because the Label occupied the entire frame space with a static background color, the frame's updated background color was obscured. Returning the `tk.Label` as the widget ensures both the frame and label backgrounds are configured upon controller selection updates.

## MVC/SoC Judgment
* UI layout, widget groupings, formatting, and colors are isolated at the View layer.
* Exact calculations and values remain decoupled in `SeerAdapter` and `SeerTableModel`.

## Changed Files
* `apps/calculator/ui/metric_input_table.py`
* `apps/calculator/ui/layout_constants.py`
* `apps/calculator/ui/sections/en14825_seer_section.py`
* `apps/calculator/ui/en14825/seer_table_model.py`
* `tests/test_apps_calculator_ui_en14825.py`
* `tests/test_ui_tk_metric_input_table_adapter.py`
* `docs/WORK_PLAN.md`

## Test Results
* `test_seer_table_model_behavior` was updated to assert the integer percent formatting.
* `test_en14825_static_cell_tint` was added to verify static cell widget exposure and background tinting.
* `test_cell_widget_readonly_returns_label` was updated in `test_ui_tk_metric_input_table_adapter.py`.
* All 14 tests in `tests/test_apps_calculator_ui_en14825.py` and 25 tests in `tests/test_ui_tk_metric_input_table_adapter.py` passed successfully.

## Manual Check Need
* **Needed**: Manual verification on target OS (e.g. Windows) to visually confirm the visual grouping frame borders, table headers, and the cell status highlights.

## Known Risks / Gaps
* None.

## Next Suggested Action
* Proceed to the EN14825 SCOP integration design/preflight phase.

## Project Memory Delta
* None.
