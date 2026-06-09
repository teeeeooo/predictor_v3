# 308 Post-SASO T3 Controller Switch & Validation GUI Smoke Closeout

## Goal

Close out the manual GUI smoke testing blocker for `IsoSasoT3Section` controller switch (304) and input validation alignment (307) after successful validation by the user on the iMac Aqua/Tk GUI environment.

## User GUI Smoke Results

The user verified the manual GUI smoke checklist on iMac and confirmed everything is correct:
- **SASO T3 Required Point Validation**: Entering invalid text, `0`, or negative numbers highlights the target cell in red, blocks calculations, and displays aligned error messages.
- **SASO T3 Optional 35 Min Validation**: Entering invalid text, `0`, or negative numbers highlights the `35 Min` cell in red. The optional row shows an error message, but the required row continues to display correct calculations (partial required fallback behavior verified).
- **Correction Recovery**: Re-entering valid numbers clears the red invalid highlighting and completes the full 4-point calculation.
- **Basic Interactions**: Paste, invalid paste, undo (Ctrl+Z), and clear function correctly.
- **Profile Transitions**: Switching between Hong Kong CSPF/HSPF, ISO/ISEER 2-Point, and SASO T3 profiles works seamlessly with no visual or functional issues.

## Closeout Targets

- **304**: IsoSasoT3Section controller switch migrated to `TkTableController`.
- **307**: IsoSasoT3Section input validation aligned with `MetricInputTable` visual marking.

## Implementation (Cleanup)

- Removed unused `parse_numeric_cell` import from `ui_tk/sections/iso_saso_t3_section.py`.
- Removed unused `_parse_positive()` helper function from `ui_tk/sections/iso_saso_t3_section.py`.

## Validation

All regression and focused tests passed cleanly on macOS:
- `py_compile` succeeded on `ui_tk/sections/iso_saso_t3_section.py`.
- `pytest tests/test_ui_tk_iso_saso_t3_controller_switch.py`: 10 passed
- `pytest tests/test_ui_tk_metric_input_table_validation.py`: 21 passed
- `check_code_structure.py` completed with no new violations.
- `git diff --check` passed cleanly.

## Excluded Scope

- No modifications to PyQt or calculator core code.
- No codebase reference map regeneration performed.
- No lifecycle cleanup or archiving of reports performed.

## Active Report Count

- active report count exceeds lifecycle threshold; cleanup pending.

## Lifecycle Maintenance Note

- **Pending**: Deferred to a follow-up lifecycle cleanup slice after current workflow and metadata slices are completed.

## Next Actions

1. **code_checker metadata & freshness check improvement**
   - Address task number hardcoding and map staleness detection options.
2. **Regenerate reference map and commit milestone changes**
   - Re-run `build_reference_map.py` to sync the codebase reference map with all completed controller switch sections and test suites.
3. **Controller switch arc final summary / closeout**
4. **Active report lifecycle cleanup**
5. **Main table migration check**
6. **ui_tk folder cleanup**
7. **EN14825 / AHRI 210/240 / KS profile expansion**
