# 307 SASO T3 Section Input Validation Alignment

## Goal

Align `IsoSasoT3Section` validation and input error marking behaviors with the standard `MetricInputTable` visual feedback system. Resolve the section-local validation owner-bypass, ensuring invalid required points block calculation and mark inputs while invalid optional `35 Min` inputs mark the cell and report optional status errors while preserving the required row.

## Scope

- Extend `MetricInputTable.get_numeric_values()` in a backward-compatible manner to validate targeted subsets of field keys.
- Refactor `IsoSasoT3Section` inputs reading to leverage `MetricInputTable.get_numeric_values(fields=...)` for required and optional field keys.
- Mark positivity validation (non-positive numbers) as invalid visual states via `MetricInputTable.set_invalid_fields()`.
- Expand unit tests to verify subset validation, positivity markings, correction restoration, and partial behavior.
- Correct 1 line of wording in the 305 audit report.

## Current Behavior

Prior to this alignment, `IsoSasoT3Section` performed local parsing (`_parse_positive`) that bypassed `MetricInputTable`'s standard validation hook. Although it intercepted invalid inputs:
- Red visual error cells (invalid background color) were not painted on invalid entry focus-out.
- The tone of required validation messages differed from other profiles (Hong Kong/2-point).
- Optional `35 Min` invalid states were handled as localized calculation errors rather than standard table visual marks.

## Implementation

- **`ui_tk/metric_input_table.py`**:
  - Expanded `get_numeric_values(fields=None)` to accept an optional iterable of target keys.
  - Clears previous errors only for the target fields.
  - Updates and merges newly discovered validation errors with the remaining invalid states of other fields.
- **`ui_tk/sections/iso_saso_t3_section.py`**:
  - Replaced localized `_point_values` and `_parse_positive` with direct `MetricInputTable.get_numeric_values()` calls.
  - Required fields are parsed as `_REQUIRED_FIELDS`, and optional fields as `_OPTIONAL_FIELDS`.
  - Positivity check errors are mapped back to `MetricInputTable` using `set_invalid_fields(current_invalid)`.

## Required vs Optional 35 Min Policy

- **Required Point Invalid**: Blocks required calculations entirely, clearing detail panel traces, setting error label to `"입력 오류: 숫자 입력을 확인하세요."` (aligned with Hong Kong/2-Point tone), and highlighting invalid input fields.
- **Optional 35 Min Invalid**: Preserves the required-only (3-point) calculated row in the result table. Highlights only the invalid optional fields (`35 Min`), sets optional-trace statuses to error descriptions, and sets the main status label to `"4-point 입력 오류: 35 Min 숫자 입력을 확인하세요."`.

## Tests

- Added 4 unit tests to `tests/test_ui_tk_metric_input_table_validation.py` verifying get_numeric_values subset parsing, subset-only invalid marking, correction clearance, and KeyError enforcement.
- Updated `TestRecalculate` in `tests/test_ui_tk_iso_saso_t3_controller_switch.py`:
  - `test_recalculate_blocks_on_invalid_required_value`: Verifies visual cell marking and aligned status message.
  - `test_recalculate_blocks_on_required_non_positive_value`: Verifies positivity validation highlights required inputs.
  - `test_recalculate_blocks_on_invalid_optional_value`: Verifies optional invalid highlights only optional fields while required row remains valid.
  - `test_recalculate_blocks_on_optional_non_positive_value`: Verifies optional positivity highlights only optional fields.
  - `test_optional_becomes_valid_after_correction`: Verifies that correcting an invalid optional cell clears its visual invalid state and restores the full 4-point calculation.

## Validation

All regression and focused tests passed cleanly on macOS:
- `pytest tests/test_ui_tk_iso_saso_t3_controller_switch.py`: 10 passed (3 added/modified)
- `pytest tests/test_ui_tk_metric_input_table_validation.py`: 21 passed (4 added)
- Total regression suite (CSPF, HSPF, 2-Point, Parity, Adapter, Validation): 93 tests passed successfully.
- `py_compile` succeeded on modified files.
- `check_code_structure.py` completed with no new violations.
- `git diff --check` passed cleanly (no trailing whitespaces).

## Manual GUI Smoke Required

- Run `python3 app_calculator_tk.py`.
- Select `ISO / SASO T3` profile.
- Enter `not_a_number` or `0` on `46 Full Capacity` (required). Verify cell turns red and calculation blocks with status `"입력 오류: 숫자 입력을 확인하세요."`.
- Restore valid numbers. Verify red styling disappears.
- Enter `not_a_number` or `-100` on `35 Min Capacity` (optional). Verify only `35 Min` cell turns red, the status label indicates a `35 Min` input error, and the bottom `Required only` row is still displayed.
- Restore valid numbers on `35 Min`. Verify red styling disappears and 4-point calculations complete.

## 305 Wording Correction

Modified line 28 of `result_reports/active/305_code_checker_and_reference_map_gate_audit.md`:
- **Old**: `The tools/code_checker framework provides a semantic and structure overview of the codebase`
- **New**: `The tools/code_checker framework provides a symbol/import/hotspot reference overview of the codebase`

## Excluded Scope

- No changes to `HongKongHspfSection`, `HongKongCspfSection`, or `IsoIseer2PointSection`.
- No changes to `IsoSasoT3ResultTable` or optional `35 Min` toggle/state behavior.

## Active Report Count

- 15 active reports present (>10, cleanup pending).

## Lifecycle Maintenance Note

- **Pending**: Deferred to a follow-up lifecycle cleanup slice.

## Next

- Post-SASO T3 controller switch & validation GUI smoke.
