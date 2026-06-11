# 370. EN14825 SCOP Foundation Report

This report summarizes the implementation of the EN14825 SCOP (heating) comparison headless foundation (models, adapter, table model, and tests).

## Goal
Implement the data models, adapter layer, and headless table model for the EN14825 SCOP calculator, and add a comprehensive unit test suite to guarantee correctness prior to GUI development.

## Scope
* Created `scop_models.py` defining `ScopPointInput`, `ScopPointComputed`, and `ScopResultSummary`.
* Created `scop_adapter.py` handling W-to-kW conversion, fallback calculation flow, temperature bivalent/TOL overrides, and error mapping.
* Created `scop_table_model.py` exposing heating table rows, column formatting (W integer, COP 2 decimals, percent 1 decimal), dynamic TOL/Tbiv column labels, and cell editability/coloring state metadata.
* Registered new classes in `apps/calculator/ui/en14825/__init__.py`.
* Created unit tests inside `tests/test_apps_calculator_ui_en14825_scop.py`.

## Non-goals
* No Tkinter section code, window registration, tab changes, or layout modifications.
* No changes to `core/calculator_en14825.py` logic.
* No changes to configuration files, EER/SEER paths, or test fixtures.

## Source Owner Boundary
New files are correctly placed inside `apps/calculator/ui/en14825/` feature package to keep package boundaries clean.

## MVC/SoC Judgment
The separation of concerns is maintained:
* Models represent pure data shapes.
* The adapter handles W-to-kW unit translation and coordinates core calculator calls.
* The table model acts as a headless controller for cell values, labels, and color states.

## Implemented Model/Adapter/Table Model Contract
* `ScopPointInput` & `ScopPointComputed`: Hold raw and computed details for A, B, C, D, TOL, Tbiv.
* `ScopAdapter`: Instantiates the core `EN14825Calculator` via dependency injection. Exposes `compute_points()` and `calculate()`.
* `ScopTableModel`: Defines row keys, column keys, formatting, cell states (`pass` if capacity/COP is within bounds, `invalid` if out of bounds, `neutral` for inputs, `unavailable` for unsupplied inputs). Exposes dynamic headers e.g., `TOL (-12°C)` based on active input temperature overrides.

## Unit Conversion Contract
* UI Inputs: Watts (`W`) and dry-bulb Celsius (`°C`).
* Core Inputs: Kilowatts (`kW`) and dry-bulb Celsius (`°C`).
* Boundary: `kW = W / 1000.0` is performed in `ScopAdapter` when translating point capacity/power, design load, and standby inputs.
* Output: Energy values are returned in `kWh` and displayed directly.

## Fallback Behavior
* Declared-only: Run core calculation with derived declared power (`declared_capacity / declared_cop`), tested results remain `None`.
* Tested-only: Run core calculation with tested capacity/power, declared results remain `None`.
* Declared + Tested: Run both calculations and compute comparison metrics.
* Incomplete: Returns `status_code = "input_incomplete"` if neither set is fully complete.
* Temperature overrides logic: Catch `ValueError` (e.g. `TOL > Tbiv`) from core and return `status_code = "invalid_temp_override"`.

## Test Results
11 unit tests successfully pass in `tests/test_apps_calculator_ui_en14825_scop.py`:
* `test_scop_imports`: Exports are importable from `apps.calculator.ui.en14825`.
* `test_scop_point_input_init`: Input dataclass initialization checks.
* `test_scop_part_load_calculations`: Part-load ratio and load W formulas.
* `test_scop_adapter_compute_points`: Derived values and state transitions.
* `test_scop_adapter_w_to_kw_conversion`: Correct scaling of point inputs and auxiliary inputs.
* `test_scop_adapter_fallback_scenarios`: Fallbacks (Declared-only, Tested-only, Both).
* `test_scop_adapter_validation_failures`: Bad input handling (TOL > Tbiv, incomplete inputs).
* `test_scop_table_model_definitions`: Row/column definitions (no declared power row).
* `test_scop_table_model_formatting_and_labels`: String formatting and dynamic column label mapping.
* `test_scop_table_section_breaks`: Correct separation row tags.
* `test_scop_integration_with_real_calculator`: Basic verification with actual core engine.

All 15 SEER tests also pass successfully with no regression.

## Known Risks / Gaps
None. All boundary mappings and fallback options are verified with unit tests.

## Next Suggested Action
Proceed to **Slice 2: section UI integration** (`en14825_scop_section.py`) to build the stacked climate cards and bind dynamic events.

## Project Memory Delta
- none
