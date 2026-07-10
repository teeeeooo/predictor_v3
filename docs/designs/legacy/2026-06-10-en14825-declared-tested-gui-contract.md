# EN14825 Declared/Tested GUI Design Contract

This design contract outlines the UI specifications, data models, behavior rules, visual designs, and implementation slices for the EN14825 SEER and SCOP calculations in the polished Tkinter application, prior to actual GUI development.

## 1. Goal
* Define a robust, contract-backed spreadsheet-like interface for the EN14825 calculator.
* Support both manufacturer declared specifications (Declared) and actual measured values (Tested) simultaneously, including partial configurations (Declared-only, Tested-only, or Declared + Tested).
* Ensure real-time, automatic calculations as inputs change, eliminating the need for a "Calculate" button.

## 2. Non-Goals
* Modification of production Python source files, test suites, or the current directory layout under `apps/calculator/ui/` in this slice.
* Changing or refactoring the core calculator logic (`core/calculators/standards/en14825.py`).
* Providing image mockups (the design contract is purely text/schema-based).
* Addressing core structure debt (flat structure remains untouched).
* Supporting multi-climate simultaneous batch processing in this slice.

## 3. Current Code Boundaries
* Current Calculator UI package: [apps/calculator/ui/](../../apps/calculator/ui/).
* Deprecated PyQt calculator-only files ([ui/calc_window.py](../../ui/calc_window.py), [ui/calculators_2point.py](../../ui/calculators_2point.py), [ui/calculator_errors.py](../../ui/calculator_errors.py)) are retired and must not be imported or used.
* The public API of [core/calculators/standards/en14825.py](../../core/calculators/standards/en14825.py) is preserved as-is.

## 4. Core API Contract
The UI adapter/controller layer interacts with the core calculator using the following methods:

### SEER: `calculate_seer`
* **Method Signature**:
  ```python
  def calculate_seer(self, test_points: dict, p_to: float, p_sb: float, p_ck: float, p_off: float,
                     p_design_c: float, t_design_c: float = T_DESIGN_C, cd: float = CD_DEFAULT) -> dict
  ```
* **Required Input Parameters**:
  * `test_points`: Dictionary with keys `"A"`, `"B"`, `"C"`, `"D"`. Each value is a list/tuple `(capacity, power)` in **kW**.
  * `p_to`, `p_sb`, `p_ck`, `p_off`: Standby and auxiliary mode power in **kW**.
  * `p_design_c`: Design cooling load in **kW**.
* **Output Dictionary**:
  * `{"seer": float, "seer_on": float, "qc_kwh": float}`

### SCOP: `calculate_scop`
* **Method Signature**:
  ```python
  def calculate_scop(self, test_points: dict, p_to: float, p_sb: float, p_ck: float, p_off: float,
                     p_design_h: float, climate: str, cd: float = None, appliance_type: str = None,
                     tbiv_temp_c: float = None, tol_temp_c: float = None) -> dict
  ```
* **Required Input Parameters**:
  * `test_points`: Dictionary with keys `"A"`, `"B"`, `"C"`, `"D"`, `"TOL"`, `"Tbiv"`. Each value is a dictionary `{"capacity": float, "power": float, "temp_c": float}` in **kW** and **°C**.
  * `p_to`, `p_sb`, `p_ck`, `p_off`: Standby/auxiliary mode power in **kW**.
  * `p_design_h`: Design heating load in **kW**.
  * `climate`: Climate zone name (`"average"`, `"warmer"`, `"colder"`).
* **Output Dictionary**:
  * `{"scop": float, "SCOP": float, "scop_on": float, "qh_kwh": float, "active_kwh": float, "standby_kwh": float, "total_kwh": float, "bin_details": list}`

## 5. Unit Policy
* **GUI Inputs**: All power, capacity, and standby inputs are entered in Watts (**W**) in the UI.
* **GUI Outputs**: All energy outputs are displayed in Kilowatt-hours (**kWh**). COP, EER, SEER, and SCOP are dimensionless.
* **Core Inputs**: The core calculations require Kilowatts (**kW**).
* **Adapter Transformation**:
  * UI-to-Core: `kW = W / 1000.0` (applied to capacity, power, design loads, and standby parameters).
  * Core-to-UI: Energy outputs (`qc_kwh`, `qh_kwh`, `active_kwh`, etc.) are returned in **kWh** and can be formatted directly for display.

## 6. Declared / Tested Data Model
The EN14825 calculator supports two independent source types per test point:

1. **Declared Specifications (Declared)**:
   * Values provided by manufacturers (typically registered in databases).
   * User inputs: `Declared capacity [W]`, `Declared EER` (SEER) or `Declared COP` (SCOP).
   * **Note**: No `Declared power` row is displayed in the UI.
   * Derived internally in the adapter to create core-compatible input pairs:
     $$\text{declared\_power\_w} = \frac{\text{declared\_capacity\_w}}{\text{declared\_eer\_or\_cop}}$$
2. **Tested Measurements (Tested)**:
   * Actual measured performance values.
   * User inputs: `Tested capacity [W]`, `Tested power [W]`.
   * Derived read-only values shown in UI:
     $$\text{tested\_eer\_or\_cop} = \frac{\text{tested\_capacity\_w}}{\text{tested\_power\_w}}$$

### Calculation Fallback Logic
* Both inputs are **optional**; however, at least one complete set must be provided.
* **Declared-only**: Computes results based on declared values. Tested output fields are blank. No validation errors are triggered for missing tested values.
* **Tested-only**: Computes results based on tested values. Declared output fields are blank. No validation errors are triggered for missing declared values.
* **Declared + Tested**: Computes both declared and tested results. Automatically enables comparison percentage columns.

## 7. SEER Main GUI Contract
The cooling tab features a main table layout combined with common inputs and a guide card.

### Common Inputs
Located in a top card, shared by the active profile:
* `p_to` (Thermostat-off), `p_sb` (Standby), `p_ck` (Crankcase heater), `p_off` (Off mode) — Entered in **W** (defaulting to 0).
* `p_design_c` (Design cooling load) — Entered in **W**.
* **Note**: Common standby parameters are preserved when switching profiles.

### Column Definitions
* Columns: `A`, `B`, `C`, `D`
* Header Row (Outdoor Air dry-bulb Temperature):
  * **A**: 35°C
  * **B**: 30°C
  * **C**: 25°C
  * **D**: 20°C

### Row Definitions
1. **Condition / Temp** (Read-only text showing test points and temperatures)
2. **Part load %** (Read-only calculated load ratio from core/adapter)
3. **Part load [W]** (Read-only calculated part load in Watts: $p\_design\_c\_w \times \text{Part load \%} / 100$)
4. **Declared capacity [W]** (Editable float)
5. **Declared EER** (Editable float)
6. **Tested capacity [W]** (Editable float)
7. **Tested power [W]** (Editable float)
8. **Tested EER** (Read-only, computed: $\text{tested\_capacity} / \text{tested\_power}$)
9. **Capacity %** (Read-only, computed: $\text{tested\_capacity} / \text{declared\_capacity} \times 100$)
10. **EER %** (Read-only, computed: $\text{tested\_eer} / \text{declared\_eer} \times 100$)

## 8. SCOP Main GUI Contract
The heating tab features a climate-card selector, auxiliary inputs, a main table, and a guide card.

### Climate Selector Cards
* Supported climates: `Average`, `Warmer`, `Colder`.
* `Average` is active by default.
* Toggles (e.g., checkbox headers) activate/deactivate each climate card independently.
* Multiple climates can be active simultaneously, calculating and showing separate results.

### Climate-specific Auxiliary Inputs
For each active climate card:
* `Pdesign_h` (Design heating load) — Entered in **W**.
* `Tbiv` (Bivalent temperature) — Entered in **°C**.
* `TOL` (Limit operating temperature) — Entered in **°C**.
* **Defaults (User-Editable UI Defaults)**:
  * **Average**: Tbiv = -10°C, TOL = -11°C
  * **Warmer**: Tbiv = 2°C, TOL = -11°C
  * **Colder**: Tbiv = -15°C, TOL = -22°C
  * *Note*: These values are prefilled defaults in the UI input fields. They are fully **user-editable** rather than immutable standard values. The currently modified UI values for Tbiv and TOL must be passed to the core calculator. The maximum bounds (`tbiv_max_c`, `tol_max_c`) from `en14825_scop.json` represent validation limits, not UI prefill defaults.

### Column Definitions
* Columns: `A`, `B`, `C`, `D`, `TOL`, `Tbiv`
* Header Row (Outdoor Air dry-bulb Temperature):
  * Fixed test conditions for EN14825 test point schema are: **A = -7°C**, **B = 2°C**, **C = 7°C**, **D = 12°C**. These values are resolved condition values to be displayed in the header/condition row and the guide card.
  * TOL and Tbiv temperatures are variable values based on the climate defaults and user override values.

### Row Definitions
1. **Condition / Temp** (Read-only text)
2. **Part load %** (Read-only, computed: $\text{part load} / \text{p\_design\_h} \times 100$)
3. **Part load [W]** (Read-only, calculated from `p_design_h` and EN14825 heating load line)
4. **Declared capacity [W]** (Editable float)
5. **Declared COP** (Editable float)
6. **Tested capacity [W]** (Editable float)
7. **Tested power [W]** (Editable float)
8. **Tested COP** (Read-only, computed: $\text{tested\_capacity} / \text{tested\_power}$)
9. **Capacity %** (Read-only, computed: $\text{tested\_capacity} / \text{declared\_capacity} \times 100$)
10. **COP %** (Read-only, computed: $\text{tested\_cop} / \text{declared\_cop} \times 100$)

## 9. Comparison and Coloring Rules
Comparison percentage rows (`Capacity %`, `EER %`, `COP %`) and final result metrics (`SEER %`, `SCOP %`) are computed only if **both** Declared and Tested inputs exist for the target point or metric. Otherwise, cells remain blank or show a neutral "N/A" state.

Visual judgment is cell-color-coded (no OK/NG text row is added):
* **Capacity %**: Red-tinted if $< 90\%$ or $\ge 110\%$. Otherwise normal/pass-tinted.
* **EER % / COP %**: Red-tinted if $< 90\%$. Otherwise normal/pass-tinted.
* **Final SEER % / SCOP %**: Computed only when both Declared and Tested results exist. Red-tinted if **< 92%**. Otherwise normal/pass-tinted (no upper bound limit is applied).
* **Normal cell**: White or standard input/label background.
* **Pass-tinted cell**: Pale green.
* **Invalid-tinted cell**: Pale red.
* **Constraints**: No OK/NG text row or final pass/fail labels are allowed.

## 10. Result Panel Contract
The result panel displays calculated metrics in real-time as a bottom card containing compact metric tiles.

### SEER Metrics
* **Declared SEER** (Dimensionless, e.g., `5.642`)
* **Declared Qc** (kWh, annual cooling energy demand)
* **Tested SEER** (Dimensionless)
* **Tested Qc** (kWh)
* **SEER %** (Tested SEER / Declared SEER * 100)

### SCOP Metrics
Renders results for each active climate zone:
* **Climate Label** (Average, Warmer, Colder)
* **Declared SCOP** / **Declared Qh** (kWh)
* **Tested SCOP** / **Tested Qh** (kWh)
* **SCOP %** (Tested SCOP / Declared SCOP * 100)

## 11. Guide Card Contract
The guide cards display reference information in a side panel (two-column layout with the main inputs). These cards contain auxiliary helper text only and are never used as direct calculation sources.

### SEER Guide Card
* **Title**: `SEER Test Conditions`
* **Content**: Details on points A/B/C/D specifying outdoor dry-bulb temperatures (35°C, 30°C, 25°C, 20°C) and part load ratios.
* **Constraints**:
  * Do not display outdoor wet-bulb conditions.
  * Do not include indoor condition notes.
  * Do not explain symbolic meanings (e.g., definition of part load).

### SCOP Guide Card
* **Title**: `SCOP Test Conditions`
* **Content**: Details on points A/B/C/D/TOL/Tbiv specifying outdoor dry-bulb temperatures and part load ratios (A = -7°C, B = 2°C, C = 7°C, D = 12°C; Tbiv/TOL are climate defaults or user overrides).
* **Constraints**:
  * Outdoor wet-bulb temperatures are included **only** if they are available in the config/reference schema.
  * Do not include indoor condition notes.
  * Do not use the card to explain symbolic meanings such as "bivalent temperature" or "limit operation temperature." (Do not design it as a glossary or definitions card).

## 12. Visual Style Contract
* **Theme**: Light engineering-tool look. EN14825 may improve upon existing layouts with a polished interface (e.g., cleaner tables or guide card arrangements), but it must strictly adhere to the existing `apps/calculator/ui` architecture patterns.
  * **Architectural Boundaries**:
    * Clean section separation using the **section owner** pattern.
    * Decoupled business logic via a **thin adapter/controller boundary**.
    * Reuse of **reusable table/model/result components where practical** (e.g., `MetricInputTable`, `ResultPanel`).
    * High priority on **existing theme/layout token reuse**.
  * **Visual Constraints**:
    * Introducing a new dashboard framework or independent visual system is **strictly prohibited**.
    * Hardcoding new color palettes is forbidden. If additional color tokens are required, the need for a new token owner must be explicitly reported in the implementation slice.
    * Do not enforce exact styling alignment with Hong Kong, SASO, or ISO profiles; however, any styling enhancements made in EN14825 are candidates for future reverse-rollout to other profiles, which remains a future work item.
  * Page background: Very light gray.
  * Card backgrounds: Solid white with small border radii and subtle light-gray borders.
  * Spacing: Compact yet highly readable.
  * Active accents: Vibrant blue (for active tabs or profile selectors).
  * Typography: Dark gray/near black primary text, muted gray secondary text.
  * Color tints: Pale green for matching criteria, pale red for non-compliant/warning cells.
* **Layout**:
  * Two-column setup: Main table area on the left, Guide Card on the right.
  * SEER: Main table + right guide card.
  * SCOP: Stacked climate configuration cards (Average, Warmer, Colder) + right guide card.
  * Bottom area: Integrated Result Panel featuring compact summary tiles.
* **Interactions**: No "Calculate" button. Inputs automatically trigger debounced updates.

## 13. Batch Contract
Batch computation will not be implemented in this slice but must align with these specs:
* **Tested-only Mode**: Batch calculations are restricted to Tested-only scenarios (no declared values).
* **Common Inputs**: `p_to`, `p_sb`, `p_ck`, `p_off` are dialog-level inputs, configured once instead of repeating per row.
* **SEER Batch Layout**:
  * Row-level inputs: `p_design_c`, A/B/C/D tested capacity, and A/B/C/D tested power.
* **SCOP Batch Layout**:
  * Climate selection is dialog-level (single climate zone per batch run).
  * Row-level inputs: `p_design_h`, Tbiv, TOL, and capacity/power values for all six heating points (A/B/C/D/TOL/Tbiv).
  * Multi-climate simultaneous batch processing is deferred.

## 14. Implementation Slices
Development of this interface will proceed in the following order:

1. **Slice 1 (Recommended Next Action)**:
   * **Scope**: Implement EN14825 SEER data model, table model, and adapter.
   * **Goal**: Establish core-to-UI data structures, Watts-to-Kilowatts adapter conversion, and result calculation flow for cooling.
2. **Slice 2**:
   * **Scope**: EN14825 SEER section integration with real-time updates.
   * **Goal**: Assemble cooling GUI section, configure live calculations, and paint visual color coding.
3. **Slice 3**:
   * **Scope**: EN14825 SCOP final details audit.
   * **Goal**: Review and map climate parameters and defaults from config files to prepare for SCOP UI adaptation.
4. **Slice 4**:
   * **Scope**: EN14825 SCOP data model, table model, and adapter.
   * **Goal**: Define heating data models, dynamic TOL/Tbiv mappings, and coordinate-to-core translations.
5. **Slice 5**:
   * **Scope**: EN14825 SCOP section integration.
   * **Goal**: Integrate stacked climate views, guide card rendering, and bottom result panel.
6. **Slice 6**:
   * **Scope**: EN14825 SEER batch tested-only interface.
   * **Goal**: Add multi-run testing support for cooling batches.
7. **Slice 7**:
   * **Scope**: EN14825 SCOP batch single-climate tested-only interface.
   * **Goal**: Add multi-run testing support for heating batches.

## 15. Open Questions / Decisions Needed
1. **Config Defaults Hierarchy & Prefill Policy**:
   * *Contract Policy*: EN14825 GUI uses explicit UI default owners rather than blindly deriving all UI defaults from config files.
   * SCOP A/B/C/D outdoor dry-bulb conditions are config/schema-backed fixed test conditions (A = -7°C, B = 2°C, C = 7°C, D = 12°C).
   * SCOP Tbiv/TOL prefill defaults are explicitly confirmed UI defaults:
     * Average: Tbiv = -10°C, TOL = -11°C
     * Warmer: Tbiv = 2°C, TOL = -11°C
     * Colder: Tbiv = -15°C, TOL = -22°C
   * All Tbiv/TOL prefill defaults are **user-editable**. The current UI values (not the initial defaults) are passed to the core calculator.
   * Config-derived boundaries such as `tbiv_max_c`/`tol_max_c` from `en14825_scop.json` may be used as validation limits or metadata, but NOT as UI prefill defaults.
   * Any future config/default merge policy must preserve this explicit UI default contract.
2. **Color Palette Mapping**: Standardize the exact hex color codes for "pale green" (pass) and "pale red" (invalid) tinting to match the existing theme tokens in `ui/theme.py`.
