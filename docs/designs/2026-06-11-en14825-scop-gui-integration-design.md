# EN14825 SCOP GUI Integration Design

This design document defines the specification for the EN14825 SCOP (heating) comparison GUI, data models, adapter, table model, and integration plan.

## 1. Goal
* Support EN14825 heating season (SCOP) calculations within a structured, spreadsheet-like interface.
* Support manufacturer declared specifications (Declared) and measured data (Tested) simultaneously, matching the SEER dual-path design.
* Handle multiple climate zones (`Average`, `Warmer`, `Colder`) dynamically and independently (including simultaneous calculation and display).
* Ensure real-time updates as inputs change using debounced automatic calculations (no "Calculate" button).
* Adhere to Clean Architecture principles by separating data models, adapter mapping, headless table models, and view/controller glue.

## 2. Non-Goals
* Modification of the core heating calculator logic in `core/calculators/standards/en14825.py`.
* Changing configuration file `data/region_configs/en14825_scop.json`.
* Modifying the SEER (cooling) tab implementation.
* Creating shared tab-level base classes (BaseSection) or refactoring existing profiles in this slice.
* Displaying the full `bin_details` table in this phase (deferred).

## 3. Current Core/Config Contract

The core calculator `calculate_scop()` has the following signature:
```python
def calculate_scop(
    self,
    test_points: dict,
    p_to: float,
    p_sb: float,
    p_ck: float,
    p_off: float,
    p_design_h: float,
    climate: str,
    cd: float = None,
    appliance_type: str = None,
    tbiv_temp_c: float = None,
    tol_temp_c: float = None,
) -> dict
```

### Core Input Schema
* `test_points`: Dictionary with keys `"A"`, `"B"`, `"C"`, `"D"`, `"TOL"`, `"Tbiv"`.
  * Each value is a dictionary `{"capacity": float, "power": float, "temp_c": float}` in **kW** and **°C**.
* `p_to`, `p_sb`, `p_ck`, `p_off`: Standby and auxiliary mode power in **kW**.
* `p_design_h`: Design heating load in **kW**.
* `climate`: Climate zone name (`"average"`, `"warmer"`, `"colder"`).
* `cd`: Degradation coefficient (dimensionless, defaults to `0.25`).
* `appliance_type`: Appliance type (reversible vs heating_only, defaults to `"reversible"`).
* `tbiv_temp_c`: User bivalent temperature override in **°C**.
* `tol_temp_c`: User TOL temperature override in **°C**.

### Core Output Schema
* `{"scop": float, "SCOP": float, "scop_on": float, "qh_kwh": float, "active_kwh": float, "standby_kwh": float, "total_kwh": float, "bin_details": list}`

### Config Schema (`data/region_configs/en14825_scop.json`)
* Valid climates: `average`, `warmer`, `colder`.
  * Average: `t_design_h_c = -10°C`, `tbiv_max_c = 2°C`, `tol_max_c = -7°C`.
  * Warmer: `t_design_h_c = 2°C`, `tbiv_max_c = 7°C`, `tol_max_c = 2°C`.
  * Colder: `t_design_h_c = -22°C`, `tbiv_max_c = -7°C`, `tol_max_c = -15°C`.
* Default prefill values (defined at UI layer per design contract):
  * **Average**: Tbiv = -10°C, TOL = -11°C
  * **Warmer**: Tbiv = 2°C, TOL = -11°C
  * **Colder**: Tbiv = -15°C, TOL = -22°C
* Validation limits: Tbiv and TOL inputs must not exceed `tbiv_max_c` and `tol_max_c` respectively.

## 4. UI Input Contract

### Unit Conversion Policy
* **UI Inputs**: Entered in Watts (**W**) for capacities and powers, and dry-bulb Celsius (**°C**) for temperatures.
* **UI Outputs**: Dimensionless COP, SCOP, and percentages. Energy values in **kWh**.
* **Adapter Translation**:
  * Inputs: `kW = W / 1000.0`
  * Outputs: Directly displayed in **kWh** as returned from core.

### Declared / Tested Dual-Path Data Model
* **Declared specifications**:
  * User inputs: `Declared capacity [W]` and `Declared COP`.
  * UI Row: No `Declared power` row is shown.
  * Adapter derives: `declared_power_w = declared_capacity / declared_cop`.
* **Tested measurements**:
  * User inputs: `Tested capacity [W]` and `Tested power [W]`.
  * Derived read-only row: `Tested COP = tested_capacity / tested_power`.
* **Fallback Behavior**:
  * Declared-only: Calculates and shows declared results. Tested results are blank.
  * Tested-only: Calculates and shows tested results. Declared results are blank.
  * Declared + Tested: Calculates both, enabling comparison columns.

### Column and Row Definitions
* **Columns**: `A`, `B`, `C`, `D`, `TOL`, `Tbiv`
* **Column Headers**:
  * Fixed: A (-7°C), B (2°C), C (7°C), D (12°C).
  * Dynamic: TOL and Tbiv display their active temperature values (e.g. `TOL (-11°C)`, `Tbiv (-10°C)`).
* **Rows**:
  1. `condition_temp`: "Condition / Temp" (Read-only text)
  2. `part_load_ratio`: "Part load %" (Read-only)
  3. `part_load_w`: "Part load [W]" (Read-only)
  4. `declared_capacity`: "Declared capacity [W]" (Editable)
  5. `declared_cop`: "Declared COP" (Editable)
  6. `tested_capacity`: "Tested capacity [W]" (Editable)
  7. `tested_power`: "Tested power [W]" (Editable)
  8. `tested_cop`: "Tested COP" (Read-only, computed: `tested_capacity / tested_power`)
  9. `capacity_percent`: "Capacity %" (Read-only, computed: `tested_capacity / declared_capacity * 100`)
  10. `cop_percent`: "COP %" (Read-only, computed: `tested_cop / declared_cop * 100`)

### Table Grouping and Visual Style
* `section_break_before_rows` is set to `("declared_capacity", "tested_capacity", "capacity_percent")`.
* Tinting states (applied to labels/cells based on comparison):
  * `Capacity %`: Pale red (invalid) if `< 90%` or `>= 110%`. Pale green (pass) otherwise.
  * `COP %`: Pale red (invalid) if `< 90%`. Pale green (pass) otherwise.
  * Final `SCOP %`: Pale red (invalid) if `< 92%`. Pale green (pass) otherwise.

## 5. Model/Adapter/Table Model Boundary

To respect clean architecture boundaries, the SCOP feature is separated into:

```
[ ScopPointInput ] -> [ ScopAdapter ] -> [ ScopResultSummary ]
                          |
                          v (maps to)
                    [ ScopTableModel ]
```

1. **`ScopPointInput`** / **`ScopPointComputed`**: Simple dataclasses holding inputs and intermediate states per point.
2. **`ScopAdapter`**: Decoupled engine call manager. Converts W to kW, runs `calculate_scop()`, builds `ScopResultSummary` per active climate.
3. **`ScopTableModel`**: Headless representation of the table rows and columns. Provides cell values, editability rules, and state colors. Since there can be multiple active climates, we instantiate one `ScopTableModel` per active climate.

## 6. Proposed File Owner Boundary
The files will be created in the following directory layout:
* `apps/calculator/ui/en14825/scop_models.py`: Contains input, computed, and summary dataclasses.
* `apps/calculator/ui/en14825/scop_adapter.py`: Contains the W-to-kW unit translation and core invocation logic.
* `apps/calculator/ui/en14825/scop_table_model.py`: Implements row/column definitions and formatted value resolution.
* `apps/calculator/ui/sections/en14825_scop_section.py`: View layer containing stacked climate cards, Tk Table controllers, guide card, and result panel.

## 7. Proposed Implementation Slices

### Slice 1: SCOP Foundation Models & Tests
* **Deliverables**: `scop_models.py`, `scop_adapter.py`, `scop_table_model.py`.
* **Testing**: Comprehensive unit tests (in parity with `test_apps_calculator_ui_en14825.py`) verifying:
  * W to kW conversion.
  * Declared-only, Tested-only, and Declared + Tested calculations.
  * Validation rules (`TOL <= Tbiv` and limit bounds).
  * Cell color tint states.

### Slice 2: Stacked Climate GUI Integration
* **Deliverables**: `en14825_scop_section.py` (Tkinter section).
* **Details**:
  * Top card for standby parameters.
  * Stacked climate panels (Average, Warmer, Colder) each with:
    * Climate active checkbox toggle.
    * Climate-specific auxiliary inputs (Pdesignh, TOL, Tbiv).
    * `MetricInputTable` with TOL/Tbiv columns and section breaks.
  * Real-time calculation triggers (debounced tracing).
  * Static cell color repaint rules.

### Slice 3: Tab Composition & Polish
* **Deliverables**: Update `apps/calculator/ui/tabs/en14825_tab.py` to instantiate and pack the SCOP section (under a notebook or side-by-side with SEER).
* **Details**: Window auto-refit geometry tuning on climate activation toggles.

### Slice 4: Verification & Closeout
* **Deliverables**: Manual GUI smoke test runs on Windows/macOS/Linux, verifying type-replace selection carryover, copy/paste parity, and result panel rendering.

## 8. Test Plan
* **Unit Tests**:
  * Verify `ScopPointInput` initialization.
  * Verify bivalent/TOL temperature defaults mapping.
  * Verify calculation fallback logic (Declared-only, Tested-only, Both).
  * Verify validation errors for negative values, `TOL > Tbiv`, and bounds.
  * Verify W-to-kW conversion on input points, standby parameters, and design loads.
  * Verify table model formatting (e.g. capacity to integer, COP to two decimal places).
* **Integration Tests**:
  * Verify that a mock core calculator receives correct kW parameters.
  * Verify computed state mappings for green/red tinting.

## 9. Manual Smoke Plan
* **Launch UI**: Run `python3 apps/calculator/main.py`.
* **Input Changes**: Edit declared/tested capacities/powers and verify real-time debounced updates in both table cells and result summaries.
* **Validation Triggers**: Set `TOL > Tbiv` and verify status message error. Set TOL or Tbiv above max bounds and check UI styling/error.
* **Climate Toggling**: Toggle Average/Warmer/Colder checkbuttons, verify that inactive cards collapse/grey out and active cards refresh and refit the window size cleanly.
* **Clipboard Interaction**: Paste values into the table and verify cells are marked correctly. Copy values and verify TSV contents.

## 10. Open Questions
* **Climate Tab or Stacked Cards Layout**: Should the three climates be displayed as tabs inside a sub-notebook (mutually exclusive view) or as stacked label frames (which can be toggled on/off independently)?
  * *Recommendation*: The design contract specifies "toggles activate/deactivate each climate card independently" and "multiple climates can be active simultaneously". Stacked label frames inside a scrollable viewport are recommended to support simultaneous comparison.
* **Result Panel Layout for Multiple Climates**: How should the bottom result panel layout display average, warmer, and colder results concurrently?
  * *Recommendation*: The result panel will display multiple `ResultSummary` cards (one card per active climate zone) inside the shared bottom result surface.
