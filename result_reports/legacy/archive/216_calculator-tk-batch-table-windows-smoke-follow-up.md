# 216 — calculator_tk Batch Table Windows Smoke Follow-up

## Goal

Close the Windows GUI smoke gaps found after 213 by aligning the Hong Kong CSPF
batch table with the 214A toolkit-neutral table parity gate.

## Preflight

Windows smoke found five issues:

1. Ctrl+Z behaved like cell-local undo instead of restoring the last user
   action group.
2. `Case` remained an input column and new rows showed blank case cells.
3. Excel single-column multi-row paste only populated the first row.
4. Arrow-key navigation was missing in the batch table.
5. The main calculator showed excessive lower blank space.

The affected owners were:

- `ui_tk/batch_table.py`
- `ui_tk/batch_table_controller.py`
- `ui_tk/batch_case_table.py`
- `ui_tk/sections/hong_kong_cspf_batch_spec.py`
- `ui_tk/tabs/iso16358_tab.py`

No blocker was found.

## Changes

### Case Column / Row Header

- Removed `Case` from visible Hong Kong CSPF batch input columns.
- Kept row identity as a visual row header: `1`, `2`, `3`, ...
- Row headers update automatically after Add Row / Remove Row.
- Row headers are not editable, not paste targets, and not calculation inputs.
- Row header values are not included in data-cell copy. The batch table copy
  operation copies the selected data-cell rectangle only.

### Paste

- Added/covered helper behavior for single-column multi-row TSV paste.
- Paste now applies one Excel column downward from the active editable cell.
- Multi-column TSV paste applies across editable columns and skips result
  columns.
- Paste expands row count when needed.
- Paste remains one undo group.

### Undo

- Added controller-level coverage that grouped clear and paste restore as a
  table-level action, independent of active cell position.
- Result cells remain unchanged by clear/paste and after undo.

### Arrow Navigation

- Added `Left`, `Right`, `Up`, and `Down` navigation in selection mode.
- Directional movement includes selectable result cells.
- Edit mode leaves arrow keys to the underlying entry cursor behavior.

### Main Window Spacing

- Reduced excessive lower blank space by capping vertical preferred-size
  safety margin in `Iso16358Tab.preferred_initial_size()`.
- Width still keeps the existing content safety margin.
- This is a minimal geometry correction; Windows smoke should confirm the
  perceived blank space is acceptable.

### Carried Pending Workflow Change

- Included the previously staged `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`
  update that requires active report count checking before final output for
  report-backed commit/push tasks.

## 214A Parity Checklist Evidence

| Item | Evidence |
| --- | --- |
| multi-cell rectangular selection | Existing controller selection model retained; Windows smoke still recommended. |
| copy and paste as TSV | Existing copy/paste retained; helper tests cover paste target behavior. |
| single-column multi-row paste | PASS: `test_batch_table_controller_single_column_paste_fills_multiple_rows`. |
| Delete/Backspace clear | PASS: grouped clear tests cover editable-only clear and result protection. |
| grouped undo | PASS: grouped clear undo and active-cell-independent undo tests added. |
| Tab/Enter navigation | PASS: existing helper test retained. |
| arrow-key navigation | PASS: adjacent arrow helper test added; controller key bindings added. |
| click/type replace-on-type | Existing controller behavior retained; Windows smoke still recommended. |
| read-only result cell copy | Existing result-selectable/copyable behavior retained; Windows smoke still recommended. |
| read-only result mutation prevention | PASS: paste/clear tests verify result columns are skipped. |
| row identity as row header | PASS: Case column removed; row header test added. |
| layout sizing acceptance | PARTIAL: vertical preferred margin capped; Windows smoke needed for visual confirmation. |

## Modified Files

- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`
- `ui_tk/batch_table.py`
- `ui_tk/batch_table_controller.py`
- `ui_tk/batch_case_table.py`
- `ui_tk/sections/hong_kong_cspf_batch_spec.py`
- `ui_tk/tabs/iso16358_tab.py`
- `tests/test_ui_tk_batch_table_controller.py`
- `tests/test_ui_tk_hong_kong_cspf_batch_spec.py`
- `tests/test_ui_tk_iso_table_autocalc.py`

## Verification

- `python -m pytest -q tests/test_ui_tk_batch_table_controller.py` — passed.
- `python -m pytest -q tests/test_ui_tk_hong_kong_cspf_batch_spec.py` — passed.
- `python -m pytest -q tests/test_ui_tk_batch_models.py` — passed.
- `python -m pytest -q tests/test_ui_tk_iso_table_autocalc.py` — passed with Tk-dependent skips in the headless environment.
- `python -m pytest -q tests/test_ui_tk_calculator_foundation.py` — passed with Tk-dependent skips in the headless environment.
- `python -m pytest -q tests/test_ui_tk_iso16358_helpers.py tests/test_ui_tk_profile_resolver.py` — passed.
- `python3 -B tools/check_code_structure.py` — passed with the pre-existing `ui_tk/sections/bin_detail_panel.py` LOC soft warning.
- `git diff --check` — passed.

Not run:

- `python app_calculator_tk.py` — not run because this environment is headless.

## Manual Windows Smoke Needed

- Confirm no `Case` input column appears.
- Confirm row headers show `1`, `2`, `3`, ... and update after Add/Remove Row.
- Paste one Excel column into multiple rows.
- Paste multi-column TSV and confirm result cells do not mutate directly.
- Clear a multi-cell editable range and press Ctrl+Z once.
- Move active cell away, press Ctrl+Z, and confirm the last action group still
  restores.
- Confirm arrow-key navigation across input and result cells.
- Confirm result cells are selectable/copyable but not editable.
- Confirm main calculator lower blank space is reduced.

## Excluded

- No core calculator formula changes.
- No region config, golden expected, or fixture changes.
- No Hong Kong HSPF changes.
- No HSPF/EN/AHRI/KS batch implementation.
- No detail/bin, graph/export, internal formula trace, or C# WPF work.
- No docs/designs changes.

## Next Action

Windows GUI smoke closeout for the corrected batch table UX. Active report
count is above 10, so summary/archive lifecycle maintenance should be handled
as a separate follow-up.
