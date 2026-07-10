# 233D - Batch Dialog Sizing/UX Under Window Shell Policy

## Goal

Stabilize the Hong Kong CSPF batch dialog first-show sizing, placement, viewport behavior, and lower blank-space risk under the current hidden-first window/dialog lifecycle policy.

This was intentionally limited to dialog sizing/UX. It did not change batch table interaction, copy/export behavior, calculation logic, or the future two-row matrix batch layout.

## Current Flow Audit

The current batch dialog owner is `HongKongCspfBatchDialog` in `ui_tk/sections/hong_kong_cspf_batch_section.py`.

Before this change the dialog flow was:

1. Create a visible `tk.Toplevel`.
2. Apply fixed geometry `1120x420` and fixed minsize `920x360`.
3. Build and pack the batch section.
4. Let the user-visible window settle after the content is already visible.

That flow was not aligned with the hidden-first first-show policy and could preserve avoidable lower blank space because the default window height was independent from the content's requested height.

The batch surface itself has no scroll container. The likely blank-space sources were fixed default geometry and min height, not batch calculation or table model behavior.

## MVC / SoC Boundary

- `HongKongCspfBatchSection` remains the view/content owner for the batch table, buttons, status label, and auto-calc callback.
- `HongKongCspfBatchDialog` remains the dialog shell consumer that owns the toplevel first-show sequence.
- `ui_tk/window_geometry.py` now owns the reusable geometry primitive for parent-centered content-sized dialogs.
- Batch data/model/calculation/export responsibilities were not mixed with dialog sizing.

No new large shell framework was introduced. The helper is a small geometry primitive, and the dialog uses it only for first-show preparation.

## Implementation

Changed `ui_tk/window_geometry.py`:

- Added `parent_centered_content_geometry()`.
- It sizes to requested content, respects a caller-provided minimum size, applies the existing screen cap policy, centers on the parent window, and clamps to visible screen bounds.

Changed `HongKongCspfBatchDialog`:

- Withdraws the new `Toplevel` immediately.
- Builds and packs content while hidden.
- Settles layout once with `update_idletasks()`.
- Applies content-measured, parent-centered geometry.
- Shows the dialog with a single `deiconify()` after geometry is applied.
- Replaced fixed `1120x420` with content-measured sizing and reduced the minimum height from 360 to 320.

The implementation avoids repeated withdraw/deiconify, fixed-size masking, and update flooding.

## Tests

Added/updated focused tests:

- `tests/test_ui_tk_calculator_foundation.py`
  - verifies parent-centered content geometry uses content size and min size;
  - verifies oversized dialog geometry is capped to screen.
- `tests/test_ui_tk_iso_table_autocalc.py`
  - verifies the Hong Kong CSPF batch dialog open path calls the sizing helper;
  - preserves existing assertions that batch opens as a dialog, not a metric tab, and keeps 5 rows/no status column/no run button behavior.

## Validation

Executed:

- `python -m pytest -q tests/test_ui_tk_calculator_foundation.py` - 13 passed, 11 skipped.
- `python -m pytest -q tests/test_ui_tk_iso_table_autocalc.py` - 8 passed, 46 skipped.
- `python -m pytest -q tests/test_ui_tk_hong_kong_cspf_batch_spec.py tests/test_ui_tk_batch_table_controller.py` - 18 passed.
- `python3 -B tools/check_code_structure.py` - passed with one pre-existing soft warning: `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `git diff --check` - passed.
- `git status --short` - expected modified/new files only.

GUI smoke was not run in this environment. Windows manual smoke remains required.

## Windows Manual Smoke Needed

Check on Windows:

- Batch dialog first show has less visible intermediate resize/flicker.
- Batch dialog lower blank space is reduced.
- Dialog appears near the parent/current calculator window.
- Dialog stays on screen.
- Manual resize still works.
- Existing batch calculation behavior is unchanged.
- Existing batch table paste/add/remove behavior is unchanged.
- Hong Kong main profile lower blank fix remains stable.
- No refit loop returns.

## Excluded Scope

Not changed:

- batch copy-all/export;
- CSV/xlsx export;
- two-row matrix batch layout;
- batch calculation logic;
- region config or calculator core;
- main profile switch flicker;
- UI/UX policy docs;
- architecture docs;
- report lifecycle/archive.

## Next Action

Windows smoke - main and batch window sizing.
