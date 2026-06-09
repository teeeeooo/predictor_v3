# 298 Controller Switch Expansion Readiness Preflight

## Goal

Assess the readiness of migrating the remaining calculator input sections to the common `TkTableController` + `interaction_core.py` foundation, identify any blockers/prerequisites, and determine the optimal expansion slice order.

## Scope

- Evaluate the remaining controller switch candidate sections:
  - `HongKongHspfSection`
  - `IsoIseer2PointSection`
  - `IsoSasoT3Section`
- Compare candidate sections against the completed `HongKongCspfSection` pilot.
- Identify blockers, prerequisites, and risk profiles for each candidate.
- Define the next implementation slice, recommended expansion order, and validation plan.

## Evidence Read

- `295_summary-controller-switch-resultpanel-focus-arc.md` & `297_wording_correction_for_295_summary.md` (audit results, flicker root cause, stable update, and focus preservation mechanisms).
- `ui_tk/sections/hong_kong_cspf_section.py` (completed pilot structure).
- `ui_tk/sections/hong_kong_hspf_section.py` (HSPF input structures).
- `ui_tk/sections/iso_iseer_2point_section.py` & `iso_iseer_2point_result_table.py` (2-point layout and custom Treeview comparison table).
- `ui_tk/sections/iso_saso_t3_section.py` & `iso_saso_t3_result_table.py` (T3 layout, 35 Min toggle, and custom Treeview comparison table).
- `tests/test_ui_tk_hong_kong_cspf_controller_switch.py` (pilot test structure reference).

## Section Comparison

| Section | Current Controller | Input Tables | Output Surface | Auto-Calc | Special Behaviors / Characteristics |
|---|---|---|---|---|---|
| **HongKongCspfSection** *(Pilot)* | `TkTableController` | 2 (`rated_table`, `input_table`) | `ResultPanel` | Yes | Has batch multi-case dialog integration. |
| **HongKongHspfSection** | `ExcelLikeTableController` | 1 (`input_table`) | `ResultPanel` | Yes | Most similar to the pilot. Only 1 input table. Uses the same `ResultPanel` (flicker-free stable update and focus preservation directly applicable). |
| **IsoIseer2PointSection** | `ExcelLikeTableController` | 1 (`input_table`) | `IsoIseer2PointResultTable` | Yes | Uses a custom `ttk.Treeview`-based result table instead of `ResultPanel`. Dynamic Treeview updates replace the entire row set (lower flicker risk). |
| **IsoSasoT3Section** | `ExcelLikeTableController` | 1 (`input_table` with 4 columns) | `IsoSasoT3ResultTable` | Yes | Uses a custom `ttk.Treeview`-based result table. Features a `BooleanVar` checkbox toggle (`optional_min_enabled`) that enables/disables the `35 Min` capacity/power Entry inputs. |

## Blockers / Prerequisites

- **No Blockers identified**: `MetricInputTable` already fully conforms to the `TkTableSurface` interface (protocol) required by `TkTableController` (it implements all position-based adapter methods such as `row_count`, `column_count`, `cell_role`, `text_at_position`, and `cell_widget`).
- **Prerequisites**:
  - `IsoSasoT3Section` has an optional 35 Min toggle which controls the tk Entry widget state (`NORMAL` or `DISABLED`). When Entry state changes, the `TkTableController` handles focus and mutation naturally because disabled Entries natively reject keyboard focus and editing in Tk. However, the custom test suite must explicitly verify that cells under the disabled state behave correctly during paste/edit attempts.
  - The custom treeview result tables (`IsoIseer2PointResultTable`, `IsoSasoT3ResultTable`) do not trigger the full label-destruction code path of `ResultPanel`, meaning they do not require ResultPanel-specific stable update modifications.

## Recommended Expansion Order

1. **HongKongHspfSection** (First): Simplest structure, uses the exact same `ResultPanel` as CSPF, inherits all flicker and focus preservation fixes immediately.
2. **IsoIseer2PointSection** (Second): 1 input table with 2 columns, uses a Treeview result table.
3. **IsoSasoT3Section** (Third): 1 input table with 4 columns and an interactive optional 35 Min entry state toggle.

## Next Implementation Slice

- **Migrate `HongKongHspfSection` to `TkTableController`**:
  - Replace `ExcelLikeTableController` with `TkTableController` in `ui_tk/sections/hong_kong_hspf_section.py`.
  - Create `tests/test_ui_tk_hong_kong_hspf_controller_switch.py` to assert controller class, paste behavior, and recalculation parity.

## Validation Plan

For the next implementation slice (`HongKongHspfSection`):
- **Automated Tests**:
  - Run focused pytest: `pytest tests/test_ui_tk_hong_kong_hspf_controller_switch.py`.
- **Structure Check**:
  - Run `python3 -B tools/check_code_structure.py` to ensure no layering violations.
- **Manual Verification**:
  - Run `python3 app_calculator_tk.py` on iMac.
  - Check that typing/pasting valid and invalid numbers in Hong Kong HSPF input table calculates correctly and updates without visual flicker.
  - Verify that invalid text undo (Ctrl+Z) and focus preservation work as expected.

## Excluded Scope

- No production code modified (preflight only).
- No test suite execution or code modification performed in this slice.
- No directory movements or active report archiving.

## Active Report Count

- 6 active reports present (below 10, lifecycle cleanup not needed).

## Next

- Implement `HongKongHspfSection` controller switch.

## Commit / Push

- Work plan & project log update commit: `9a0fdf5`
- Active preflight report commit & push: Pending final execution.

