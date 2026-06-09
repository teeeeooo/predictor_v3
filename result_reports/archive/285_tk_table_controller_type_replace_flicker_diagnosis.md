# 285 Diagnose TkTableController Type-Replace ResultPanel Flicker

## Goal

Identify the root cause of the ResultPanel flicker observed in Hong Kong CSPF
after the controller switch pilot (284), where Hong Kong HSPF (still using
ExcelLikeTableController) does not flicker.

## Scope

- Diagnostic-only: tests and instrumentation only.
- No production code changes.
- No controller switch expansion.
- No rollback.

## Windows Observation

- Hong Kong CSPF (TkTableController): ResultPanel flickers with each keystroke.
- Hong Kong HSPF (ExcelLikeTableController): ResultPanel does not flicker.
- Both use `ResultPanel.set_summaries()` which destroys/recreates child widgets.
- Both use `DebouncedAutoCalc` with 200 ms delay.

## Controller Flow Comparison

### TkTableController._type_replace (controller.py:208–222)

```python
def _type_replace(self, event, position):
    ...
    if self.table.set_positions_batch({position: event.char}):
        self._mode = "edit"
        self._replace_pending = False
        self.table.focus_widget(position).focus_set()   # <-- present
        widget = self.table.focus_widget(position)
        widget.icursor("end")
    return "break"
```

### ExcelLikeTableController._type_replace (excel_like_table_controller.py:360–374)

```python
def _type_replace(self, event, position):
    ...
    if self.table.set_address_values_batch({...}):
        self._mode = "edit"
        self._replace_pending = False
    entry = self._entry_at(position)
    entry.icursor("end")
    entry.configure(insertontime=600)
    return "break"
```

**Key behavioral difference**: TkTableController calls `focus_set()` on the entry
widget after writing the character; ExcelLikeTableController does not.

The entry already has focus when `_type_replace` handles a key event (it
received the `<KeyPress>` event). Calling `focus_set()` on a widget that
already has focus is redundant on most platforms, but on Windows it can
generate an extra focus/visual event that causes a window repaint.

## Callback/Render Count Diagnostic

8 tests in `tests/test_ui_tk_controller_type_replace_flicker_diagnostic.py`:

| Test | CSPF | HSPF | Meaning |
|------|------|------|---------|
| Schedule count after type_replace | 1 | 1 | Identical |
| Schedule count after native edit | 1 | 1 | Identical |
| set_summaries count after flush | 1 | 1 | Identical |
| ResultPanel rebuild on set_summaries | rebuild | rebuild | Identical mechanism |
| CSPF/HSPF parity | equal | equal | No count duplication |

**Result**: Callback and render counts are **identical** between the two
controllers. The flicker is not caused by duplicate scheduling or extra
`set_summaries` calls.

## ResultPanel Rebuild Diagnostic

Confirmed: `ResultPanel.set_summaries()` calls `_clear_summary_tables()` which
`destroy()`s all existing child widgets before `_render_summary_table()`
creates new ones. Both CSPF and HSPF exhibit this full rebuild behavior.

This is a known visual mechanism, but by itself it does not explain why CSPF
flickers and HSPF does not, because both rebuild.

## Likely Root Cause

The redundant `focus_set()` in `TkTableController._type_replace` is the only
behavioral difference that can explain the discriminating observation:

1. Both controllers produce the same callback/render counts.
2. Both use the same ResultPanel rebuild mechanism.
3. The only discriminating variable is `TkTableController._type_replace`'s
   `focus_set()` call, which on Windows may trigger an unnecessary focus/visual
   event that amplifies the ResultPanel rebuild flicker.

## Recommended Next Fix Slice

**Remove the redundant `focus_set()` call from `TkTableController._type_replace`.**

The entry widget already has focus when the `<KeyPress>` binding fires.
Calling `focus_set()` again serves no purpose in the normal case and appears
to cause a Windows-specific visual side effect.

If an edge case exists where the frame (rather than the entry) has focus and
receives the key event, that scenario should be handled separately (e.g., by
ensuring the entry gets focus during cell selection/navigation, which already
happens in `_click` and `_navigate`).

## Excluded Scope

- No production code changes in this diagnostic slice.
- No controller switch expansion.
- No rollback.

## Next

- **Fix slice**: Remove redundant `focus_set()` from `TkTableController._type_replace`.
- **Verification**: Re-run Windows app smoke for HongKongCspfSection after fix.
- **If flicker persists**: Investigate `TkTableController._paint_selection` full-grid
  configure vs ExcelLikeTableController editable-only configure as secondary
  candidate.

## Risks

- Removing `focus_set()` might affect an edge case where the cell frame (not
  the entry) has focus and receives the `<KeyPress>` event. This should be
  mitigated by ensuring focus is on the entry during selection/navigation.
- ResultPanel full rebuild remains a visual inefficiency even after the focus
  fix; a stable-update redesign may be needed later for overall smoothness.
