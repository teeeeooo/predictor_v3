# EN14825/AHRI Detail View Design

## Status

Design reference for the next EN14825/AHRI detail-view implementation slices.

This document records the agreed detail-view direction before implementation. It does not authorize sample-data removal, result contract changes, or broad UI token cleanup.

## Goal

Add Hong Kong-style detail views to the following calculator profiles before removing launch-time product performance sample values:

1. EN14825 SCOP
2. EN14825 SEER
3. AHRI 210/240 HSPF2
4. AHRI 210/240 SEER2

The first implementation goal is a practical bin detail table that helps the user understand how the seasonal metric was calculated from bin data.

## Background

The calculator sample/empty-state policy requires product performance demo values to be removed later, but EN14825 and AHRI must first have a diagnostic detail surface comparable to the existing Hong Kong detail view.

Existing reference pattern:

- Section-owned detail toggle.
- Reusable `BinDetailPanel`.
- Explicit no-data / input-waiting / error status.
- Bin table.
- Lightweight graph/table surface where already supported by the panel.
- CSV/export boundary owned by the detail panel or section-specific detail owner.
- Visible-content resize callback when detail visibility changes.

The Hong Kong implementation is a reference pattern, not a schema to copy directly into EN14825/AHRI.

## Confirmed Decisions

### Detail targets

All four profiles require detail views:

| Profile | Detail needed | Implementation order |
| --- | --- | --- |
| EN14825 SCOP | Yes | 1 |
| EN14825 SEER | Yes | 2 |
| AHRI HSPF2 | Yes | 3 |
| AHRI SEER2 | Yes | 4 |

### Primary detail surface

The first detail surface is a bin detail table.

Do not implement point contribution tables in this arc.

Do not claim that A/B/C/D, H01/H11/H32, or other test points have direct seasonal contribution percentages from a single calculation. Test points define capacity and efficiency curves, interpolation anchors, and case boundaries. Per-test-point contribution would require a separate sensitivity/what-if analysis arc.

### Seasonal summary

A compact seasonal summary may be shown only when values are already unambiguous in the calculation result or can be safely summed from bin rows.

Allowed examples:

- Total load.
- Total energy.
- Active energy.
- Standby energy.
- Auxiliary / backup energy.
- Defrost multiplier or defrost metadata where already available.

These are summary values, not point-level contribution attribution.

### Sample-data removal dependency

Do not remove EN14825/AHRI launch-time product performance samples until detail views are implemented and verified.

Do not mix detail-view implementation and sample-data removal in the same slice.

## Data Source Audit

### EN14825 SCOP

Current source availability: core already returns bin details.

Core `calculate_scop()` returns:

- `scop`
- `scop_on`
- `qh_kwh`
- `active_kwh`
- `standby_kwh`
- `total_kwh`
- `bin_details`

SCOP `bin_details` currently include values such as:

- `temp_c`
- `hours`
- `ph`
- `pdh`
- `cop_pl`
- `equivalent_power`
- `cop_bin`
- `cr`
- `degradation_factor`
- `capacity_source`
- `cop_source`
- `denominator_contribution`
- `heat_pump_load`
- `elbu`
- `operating_case`
- `interpolation`

Current gap:

- `ScopAdapter` calculates declared/tested results but does not preserve the core `bin_details` in `ScopResultSummary`.

Design implication:

- Core change should not be needed for first SCOP detail implementation.
- Extend the adapter/model boundary to retain declared/tested detail payloads.
- Add a profile-specific detail formatter/schema that maps raw core keys to UI labels and units.

### EN14825 SEER

Current source availability: core has bin-loop logic but does not return bin details.

Core SEER flow computes:

- cooling bin temperatures and hours
- `Pc(Tj)`
- `EERpl(Tj)`
- numerator contribution
- denominator contribution

Current return includes:

- `seer`
- `seer_on`
- `qc_kwh`

Current gap:

- No returned `bin_details`.

Design implication:

- Do not duplicate SEER calculation logic in the UI section.
- Add an additive core helper or detail path that can produce bin details without changing existing public result keys.
- Preferred direction:
  - Keep existing `calculate_seer()` contract compatible.
  - Add a small internal helper used by `calculate_seer()` and a detail-capable wrapper, or add an optional/additive detail payload if compatible with tests.
  - Avoid UI-side reimplementation of the SEER bin loop.

### AHRI SEER2

Current source availability: core already returns bin details.

Core `calculate_seer2()` returns:

- `SEER2`
- `EER2_A_Full`
- `EER2_B_Low`
- `total_cooling_Btu`
- `total_energy_Wh`
- `system_type`
- `bin_details`

SEER2 `bin_details` currently include values such as:

- `bin`
- `temp_F`
- `BL`
- `q_Low`
- `q_Int`
- `q_Full`
- `P_Int`
- `EER_Low`
- `EER_Int`
- `EER_Full`
- `EER_IntBin`
- `case`
- `q_j`
- `E_j`

Current gap:

- `AhriSeer2Adapter` does not preserve `bin_details` in `AhriSeer2Summary`.

Design implication:

- Core change should not be needed.
- Extend adapter summary with a detail payload.
- Format in a profile-specific detail schema.

### AHRI HSPF2

Current source availability: core already returns bin details.

Core `calculate_hspf2()` v3 path returns:

- `HSPF2`
- `raw_hspf2`
- `rounded_hspf2`
- `total_heating_btu`
- `total_energy_wh`
- `summary`
- `bin_table`
- `bin_details`

HSPF2 `bin_details` currently include values such as:

- `bin_no`
- `temp_F`
- `hours`
- `fractional_hours`
- `operating_case`
- `building_load`
- `delta_j`
- `HLF_j`
- `PLF_j`
- `q_low`
- `p_low`
- `q_int`
- `p_int`
- `q_full`
- `p_full`
- `COP_low`
- `COP_int`
- `COP_full`
- `COP_bin`
- `q_comp`
- `e_comp`
- `q_aux`
- `e_aux`
- `q_j`
- `E_j`
- `aux_ratio`
- `debug_info`

Current gap:

- `AhriHspf2Adapter` does not preserve `bin_details` in `AhriHspf2Summary`.

Design implication:

- Core change should not be needed.
- Extend adapter summary with detail payload and selected metadata.
- Keep existing main UI source display contract unchanged.

## Detail Schema Direction

### Common UI pattern

Use a shared detail-view pattern instead of profile-local UI hacks:

- Detail toggle button below the main result/action area.
- `BinDetailPanel` or a small reusable wrapper around it.
- Source selector when multiple detail sources exist.
- No-data status when input is incomplete.
- Error status when calculation fails.
- CSV/export behavior where the existing detail panel supports it.
- `on_trace_visibility_changed` callback so window fitting reacts to detail show/hide.

Do not add fixed geometry or profile-specific min-size inflation to make detail fit.

### Source selector

| Profile | Source selector direction |
| --- | --- |
| EN14825 SCOP | Multi-source: climate + declared/tested. Example: `Average Declared`, `Average Tested`, `Warmer Declared`, `Warmer Tested`, `Colder Declared`, `Colder Tested`. Only show sources that have data. |
| EN14825 SEER | Multi-source: `Declared`, `Tested`. Only show sources that have data. |
| AHRI HSPF2 | Single source: `HSPF2`. Source selector can be hidden if the common panel supports that. |
| AHRI SEER2 | Single source: `SEER2`. Source selector can be hidden if the common panel supports that. |

### EN14825 SCOP first-pass columns

Recommended compact bin table columns:

| Key | Label | Unit / format | Notes |
| --- | --- | --- | --- |
| `temp_c` | Tj | °C | Outdoor bin temperature |
| `hours` | Hours | h | Bin hours |
| `ph` | Heating Load | kW or W after formatter decision | Keep unit consistent with existing UI |
| `pdh` | HP Capacity | kW or W after formatter decision | Heat pump available capacity |
| `heat_pump_load` | HP Load | kW or W | Heat pump-covered load |
| `elbu` | Backup | kW or W | Electric backup load |
| `cop_pl` | COPpl | - | Part-load COP |
| `denominator_contribution` | Energy | kWh-equivalent | Denominator contribution |
| `operating_case` | Case | text | Compact display preferred |
| `interpolation` | Source | text | Optional if too wide; may be hidden initially |

SCOP should remain the first implementation target because it exercises climate/source handling and backup energy.

### EN14825 SEER first-pass columns

Recommended compact bin table columns:

| Key | Label | Unit / format | Notes |
| --- | --- | --- | --- |
| `temp_c` | Tj | °C | Outdoor bin temperature |
| `hours` | Hours | h | Bin hours |
| `pc` | Cooling Load | kW or W after formatter decision | Cooling load |
| `eer_pl` | EERpl | - | Interpolated part-load EER |
| `energy_contribution` | Energy | kWh-equivalent | Denominator contribution |
| `source` or `interpolation` | Source | text | Optional compact source string |

SEER requires additive detail data in core or adapter boundary because the current core public return does not expose bin details.

### AHRI HSPF2 first-pass columns

Recommended compact bin table columns:

| Key | Label | Unit / format | Notes |
| --- | --- | --- | --- |
| `temp_F` | Tj | °F | AHRI native bin temperature |
| `hours` | Hours | h | Bin hours |
| `operating_case` | Case | text | Case 0/I/II/III |
| `building_load` | Building Load | Btu/h | |
| `q_low` | Low Cap | Btu/h | |
| `q_int` | Int Cap | Btu/h | |
| `q_full` | Full Cap | Btu/h | |
| `COP_bin` | COPbin | - | |
| `q_comp` | Comp Heat | Btu | |
| `e_comp` | Comp Energy | Wh | |
| `q_aux` | Aux Heat | Btu | |
| `e_aux` | Aux Energy | Wh | |
| `q_j` | Total Heat | Btu | |
| `E_j` | Total Energy | Wh | |

The debug metadata can stay out of the first UI table unless a later diagnostics view is approved.

### AHRI SEER2 first-pass columns

Recommended compact bin table columns:

| Key | Label | Unit / format | Notes |
| --- | --- | --- | --- |
| `temp_F` | Tj | °F | AHRI native bin temperature |
| `BL` | Building Load | Btu/h | Cooling building load |
| `q_Low` | Low Cap | Btu/h | |
| `q_Int` | Int Cap | Btu/h | |
| `q_Full` | Full Cap | Btu/h | |
| `EER_Low` | EER Low | - | |
| `EER_Int` | EER Int | - | |
| `EER_Full` | EER Full | - | |
| `EER_IntBin` | EER Bin | - | Blank for cases where not used |
| `case` | Case | text/number | 1, 2.1, 2.2, 3 |
| `q_j` | Cooling | Btu | |
| `E_j` | Energy | Wh | |

## Adapter and Model Boundary

### Preferred direction

Keep core/domain logic separate from UI formatting.

Recommended boundary:

1. Core returns raw calculation result and bin details.
2. Adapter preserves detail payload in summary model or a profile-specific detail object.
3. Section owns visible state and source selection.
4. Detail formatter maps raw keys to display rows/columns.
5. `BinDetailPanel` displays already formatted rows.

### Do not

- Do not make `BinDetailPanel` know EN14825/AHRI raw key semantics.
- Do not make UI section recompute seasonal formulas when core already has details.
- Do not change existing result summary keys just to support detail view.
- Do not remove sample data in detail implementation commits.
- Do not invent point-level contribution percentages.
- Do not add broad token cleanup or unrelated UI refactor.

## Implementation Slices

### Slice 1: Detail design formalization

Current document.

No production code changes.

### Slice 2: EN14825 SCOP detail foundation

Purpose:

- Preserve SCOP declared/tested `bin_details` in adapter/model.
- Add section detail state and `BinDetailPanel`.
- Add source selection for climates and declared/tested datasets.
- No sample-data removal.

Expected files:

- `apps/calculator/ui/en14825/scop_models.py`
- `apps/calculator/ui/en14825/scop_adapter.py`
- `apps/calculator/ui/sections/en14825_scop_section.py`
- possibly a new `apps/calculator/ui/en14825/scop_detail.py`
- focused tests

### Slice 3: EN14825 SEER detail data path

Purpose:

- Add additive SEER bin detail source without duplicating calculation in UI.
- Preserve declared/tested detail in adapter/model.
- No sample-data removal.

Expected files:

- `core/calculators/standards/en14825.py`
- `apps/calculator/ui/en14825/seer_models.py`
- `apps/calculator/ui/en14825/seer_adapter.py`
- `apps/calculator/ui/sections/en14825_seer_section.py`
- possibly a new `apps/calculator/ui/en14825/seer_detail.py`
- focused tests

Core changes must be additive and must not break existing public result keys.

### Slice 4: AHRI HSPF2 detail view

Purpose:

- Preserve HSPF2 `bin_details` in adapter summary.
- Add section detail state and single-source detail panel.
- Keep main UI source display unchanged.
- No sample-data removal.

Expected files:

- `apps/calculator/ui/ahri/hspf2_adapter.py`
- `apps/calculator/ui/sections/ahri_hspf2_section.py`
- possibly a new `apps/calculator/ui/ahri/hspf2_detail.py`
- focused tests

### Slice 5: AHRI SEER2 detail view

Purpose:

- Preserve SEER2 `bin_details` in adapter summary.
- Add section detail state and single-source detail panel.
- No sample-data removal.

Expected files:

- `apps/calculator/ui/ahri/seer2_adapter.py`
- `apps/calculator/ui/sections/ahri_seer2_section.py`
- possibly a new `apps/calculator/ui/ahri/seer2_detail.py`
- focused tests

### Slice 6: Sample-data removal

Only after the relevant detail slices are implemented and verified.

Purpose:

- Remove product performance demo prefill values.
- Keep option/standard defaults.
- Ensure launch state is input-waiting, not demo-calculated.

This must be profile-focused and separate from detail implementation.

## Testing Strategy

Use focused tests, not broad full-suite verification by default.

Minimum test coverage per implementation slice:

- Detail source map is empty/input-waiting when calculation is incomplete.
- Detail source map is populated after valid calculation.
- Detail panel toggle updates visibility and calls visible-content callback.
- Source selector labels match expected sources.
- CSV/export rows use formatted display schema if existing panel supports export.
- Existing result panel summaries remain unchanged.
- Existing batch behavior remains unchanged.
- No sample-data removal occurs in detail implementation slices.

For EN14825 SEER detail data path:

- Existing SEER result keys and rounding remain compatible.
- New detail path does not change SEER metric output.
- Bin detail rows align with the same bin data and load line used by SEER calculation.

## Manual Verification

After each profile detail implementation:

- Open profile.
- Confirm existing result UI still works.
- Click detail toggle.
- Confirm table appears and does not break window fitting.
- Confirm no extra white space/clipping regression.
- Confirm incomplete input shows no-data/input-waiting detail state.
- Confirm valid sample/current input produces bin rows.
- Confirm source selector behavior where applicable.

## Deferred Future Work

- Point-level contribution or sensitivity analysis.
- What-if / perturbation analysis per test point.
- Advanced graphing of bin curves.
- Detailed debug metadata viewer for AHRI HSPF2.
- Broad legacy UI token cleanup.
- Sample-data removal, until detail implementation is complete.
- Legacy `app_calculator_tk.py` cleanup.
