# 220 — Selected-range Fill Paste and Main Sizing Follow-up

## Goal

Close the two Windows smoke follow-up gaps left after 219:

1. selected-range fill paste;
2. excessive lower blank space on the main calculator CSPF screen.

This is not a common foundation redesign. It keeps the 219 foundation and
adds the missing paste behavior plus a minimal sizing correction.

## Windows Smoke Result Reflected

User smoke indicated most 219 table interaction behavior passed. Remaining
gaps:

- Copying one Excel row of N columns and pasting into a selected M x N range
  should repeat that row across all selected rows.
- The main calculator CSPF screen still showed unnecessary lower blank space.

## Selected-range Fill Paste Requirement

Accepted behavior:

- `1 x N` clipboard + `M x N` selected range -> repeat the clipboard row for
  each selected row.
- `1 x 1` clipboard + `M x N` selected range -> fill all editable cells in the
  selected range.
- Single-cell anchor paste keeps the existing behavior:
  - `1 x N` clipboard writes rightward;
  - `N x 1` clipboard writes downward;
  - `M x N` clipboard writes from the top-left anchor.
- Read-only/result cells inside the selection are skipped as mutation targets.
- Paste is one undo group.

## Docs Update

### 03 Contract

Updated `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`:

- selected-range fill paste is now part of the toolkit-neutral paste contract;
- `1 x N` source repeated over `M x N` selection is explicit;
- read-only/result cells are skipped as mutation targets;
- the target applies to Tkinter, PySide, WPF, Web, and future table surfaces.

### Tkinter Adapter

Updated `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md`:

- common Tk foundation must verify selected-range fill paste at helper and
  controller/fake-surface level;
- OS keyboard smoke remains final platform confirmation, not the first
  validation layer for core paste semantics.

## Paste Core Change

Modified `ui_tk/table/interaction_core.py`.

`editable_paste_targets()` now distinguishes:

- single-cell selection / anchor paste;
- selected range paste;
- single-cell fill paste;
- one-row selected-range fill paste;
- non-repeatable multi-cell paste, which keeps top-left paste/clip behavior.

Read-only/result filtering still happens through `CellRole` policy.

## Controller / Surface Actual Path

No new controller class was added. `TkTableController._paste()` already passes
the actual selection bounds into `editable_paste_targets()`, so the actual
controller path now receives the new selected-range fill behavior through the
common helper.

Focused fake-surface/controller tests cover:

- controller selected-range fill paste;
- result column skip;
- grouped undo restoring the state before selected-range fill paste;
- existing single-column multi-row anchor paste and MxN paste behavior.

## Main Lower Blank Space

Owner:

- `ui_tk/tabs/iso16358_tab.py`
- `ui_tk/window_geometry.py`

Cause:

- Hong Kong preferred height was derived from the tallest hidden metric tab so
  the visible CSPF tab could inherit blank space from taller hidden HSPF/detail
  content.
- Window minsize also needed to stay compatible with preferred-content fitting
  rather than forcing the fallback minimum when the preferred size is smaller.

Change:

- `Iso16358Tab.preferred_initial_size()` still measures all Hong Kong metric
  tabs for width safety, but height now follows the currently visible tab plus
  notebook chrome.
- `center_window()` min height now respects the preferred content height when
  provided.

Risk:

- Hidden tab width remains protected.
- Hidden tab height is now handled by the existing profile/tab switch refit
  path. Windows smoke should confirm CSPF, HSPF, detail toggle, and profile
  switching.

## Existing OK Items Preserved

- result/read-only cells remain protected from paste/delete/type mutation;
- copy can include result cells;
- paste remains grouped undo;
- repeated Ctrl+Z behavior is covered by existing controller tests;
- row headers remain non-input row identity;
- Hong Kong CSPF batch calculation path remains unchanged.

## Validation

- `python -m pytest -q tests/test_ui_tk_table_interaction_core.py` — passed.
- `python -m pytest -q tests/test_ui_tk_table_controller.py` — passed.
- `python -m pytest -q tests/test_ui_tk_batch_table_controller.py` — passed.
- `python -m pytest -q tests/test_ui_tk_hong_kong_cspf_batch_spec.py` — passed.
- `python -m pytest -q tests/test_ui_tk_batch_models.py` — passed.
- `python -m pytest -q tests/test_ui_tk_iso_table_autocalc.py` — passed with
  Tk-dependent skips in the headless environment.
- `python -m pytest -q tests/test_ui_tk_calculator_foundation.py` — passed with
  Tk-dependent skips in the headless environment.
- `python -m pytest -q tests/test_ui_tk_iso16358_helpers.py tests/test_ui_tk_profile_resolver.py` — passed.
- `python3 -B tools/check_code_structure.py` — passed with existing soft
  warning that `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `git diff --check` — passed.
- `git status --short` — reviewed before commit.

Not run:

- `python app_calculator_tk.py` — `DISPLAY` is not set in the Codex
  environment.

## Windows Manual Smoke Needed

- Copy one Excel row with N values and paste into an M x N selected range.
- Copy one Excel cell and paste into an M x N selected range.
- Confirm result columns inside the selection do not mutate.
- Ctrl+Z once after selected-range fill paste restores the previous state.
- Confirm existing single-column multi-row paste still works.
- Confirm existing MxN top-left paste still works.
- Check CSPF main lower blank space.
- Check HSPF tab, profile switching, detail toggle, and batch dialog sizing.

## Excluded Scope

- No foundation redesign.
- No main table migration.
- No HSPF / EN14825 / AHRI / KS batch implementation.
- No calculator core, region config, fixture/golden changes.
- No detail/bin schema, graph/export, SPOT, or docs/designs work.
- No report lifecycle/archive maintenance.

## Next Action

Windows GUI smoke closeout retry for selected-range fill paste and main sizing.
