# 301 Post Type-Replace Selection Fix GUI Smoke Closeout

## Goal

Document the successful iMac GUI smoke test verification of the `TkTableController` type-replace selection carryover fix (implemented in report 300) and close out the type-replace blocker.

## Scope

- Document the verification results of keyboard interactions in both `HongKongHspfSection` and `HongKongCspfSection`.
- Close out the type-replace carryover fix and detail panel integrity checks.
- Set the next implementation task target.

## User GUI Smoke Result

The user successfully executed manual verification on the iMac host environment:
- **`calculator_tk` Execution**: Runs successfully without layout or binding errors.
- **Hong Kong HSPF Profile Selection**:
  - Cell click followed by typing `1`, `10`, `100` works normally:
    - `1` input -> display value becomes `1`.
    - `10` input -> display value becomes `10`.
    - `100` input -> display value becomes `100`.
  - When a cell is clicked, the default value is highlighted. The first typed key replaces the entire default value correctly.
  - Subsequent keys typed (e.g. `0`) are appended at the end of the text, resolving the overwrite bug.
- **Undo / Paste / Clear Integrity**:
  - `Ctrl+Z` rollback works cleanly to restore previous cell states.
  - Valid numeric paste updates values and triggers auto-calculations.
  - Invalid text paste results in an error status summary and is highlighted appropriately.
  - Delete/Clear actions behave as expected.
- **Visual Performance**:
  - Result updates run cleanly without visual flicker in `ResultPanel` (thanks to the stable same-shape updates).
- **Hong Kong CSPF Profile**:
  - Type-replace behaves identically and correctly.
- **Profile Transitions**:
  - Transitioning between CSPF, HSPF, and other sections works without issue.

## Decision

- The type-replace selection carryover fix is verified as robust and complete on the target hardware.
- The keyboard interaction blocker is resolved. We are ready to proceed with the remaining controller switches.

## Remaining Scope

- Migration of `IsoIseer2PointSection` and `IsoSasoT3Section` to the `TkTableController` foundation.

## Active Report Count

- 9 active reports present (below 10, lifecycle cleanup not needed).

## Lifecycle Maintenance Note

- Not needed (active count 9 <= 10).

## Next

- Migrate `IsoIseer2PointSection` to `TkTableController`.

## Commit / Push

- Docs & project log update commit: `740f9a5`
- Active closeout report commit & push: Pending final execution.
