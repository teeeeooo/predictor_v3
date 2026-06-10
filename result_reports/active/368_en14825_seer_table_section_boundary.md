# EN14825 SEER Table Row Section Boundary Report

## Goal
* Visually partition the SEER input table into distinct row groups (Condition / Part load, Declared, Tested, Comparison) without altering the row model data structure.

## Scope / Non-goals
### Scope
* Add the feature-neutral `section_break_before_rows` parameter to `MetricInputTable` to allow custom top grid gaps.
* Group table rows in `En14825SeerSection` by breaking before `declared_capacity`, `tested_capacity`, and `capacity_percent`.
* Define the visual constant `TABLE_SECTION_BREAK_GAP` in `layout_constants.py`.
* Implement focused tests in both `tests/test_ui_tk_metric_input_table_adapter.py` and `tests/test_apps_calculator_ui_en14825.py`.

### Non-goals
* No blank separator rows added to the table model.
* No splitting into separate tables.
* No Calculate or Clear buttons.
* No right-side info panel.

## Design Judgment
* Grid pady manipulation was chosen to partition sections cleanly. An option `section_break_before_rows` in `MetricInputTable` accepts arbitrary row keys and increases their top grid pady to `TABLE_SECTION_BREAK_GAP`, ensuring visual section breaks are handled entirely at the presentation/grid layout layer.

## MVC/SoC Judgment
* **View/Presentation**: `MetricInputTable` remains a feature-neutral presentation component that is unaware of SEER specific semantics. Section break definitions are specified by the section view subclass.
* **Model**: `SeerTableModel` is unmodified and does not contain artificial separator keys, preventing copy/paste or Excel-like cell navigation bugs.

## SCOP Extensibility Judgment
* The `section_break_before_rows` option is completely generic and key-neutral, allowing the future `En14825CopSection` or other tables to define custom breaks easily.

## Changed Files
* `apps/calculator/ui/metric_input_table.py`
* `apps/calculator/ui/layout_constants.py`
* `apps/calculator/ui/sections/en14825_seer_section.py`
* `tests/test_ui_tk_metric_input_table_adapter.py`
* `tests/test_apps_calculator_ui_en14825.py`
* `docs/WORK_PLAN.md`

## Test Results
* `test_section_break_option` verified that `section_break_before_rows` correctly applies a top pady of `6` without changing `row_count` or `column_count`.
* `test_en14825_section_breaks` verified that breaks are correctly applied to the SEER input table rows.
* All 15 tests in `tests/test_apps_calculator_ui_en14825.py` and 26 tests in `tests/test_ui_tk_metric_input_table_adapter.py` passed successfully.

## Manual Check Need
* **Needed**: Manual smoke testing on Windows to visually verify that the top spacing is well proportioned and readable.

## Known Risks / Gaps
* None.

## Next Suggested Action
* Proceed to the EN14825 SCOP integration design/preflight phase.

## Project Memory Delta
* None.
