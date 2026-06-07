# 257 Refactor Visible Content Measurement to Side-Effect-Free Nested Notebook Policy

## Goal

Fix the Windows flicker/refit loop triggered by 256's re-enabled metric tab
change refit. The root cause was `TkVisibleContentMeasurement` programmatically
selecting hidden notebook tabs to measure them, which fired
`<<NotebookTabChanged>>` events that re-triggered refit.

## Scope

- Refactor `window_measurement.py` to use side-effect-free measurement:
  measure only the currently selected tab, never programmatically select
  hidden tabs.
- Add observed max-width cache for horizontal stability.
- Add focused tests proving no programmatic select occurs during measurement.
- Update `docs/WORK_PLAN.md` and `project_log.md`.

## User Repro

- Hong Kong profile entry caused repeated flickering.
- CSPF/HSPF tabs appeared to switch back and forth automatically.
- Window refit appeared to loop continuously.

## Root Cause

`TkVisibleContentMeasurement._measure_nested_notebook()` (lines 131-143):

```python
with self._suppress_measurement():
    for tab_id in tabs:
        notebook.select(tab_id)
        notebook.update_idletasks()
        widget = notebook.nametowidget(tab_id)
        ...
    notebook.select(current_tab)
```

The `for` loop programmatically selected each hidden tab. On Windows,
`notebook.select(tab_id)` fires a `<<NotebookTabChanged>>` event even when
the selection is later restored. 256 added `self._metric_notebook.bind(
"<<NotebookTabChanged>>", self._on_metric_tab_changed)`, and
`_on_metric_tab_changed()` requests a scheduler refit. The scheduler runs,
which calls `snapshot()`, which calls `_measure_nested_notebook()`, which
selects tabs again... creating a measurement → select → event → refit loop.

The `suppress_measurement()` context manager only suppresses explicit
`request_refit()` calls; it cannot suppress Tk-generated events from the
underlying `select()` call.

## Batch Reference vs Main Visible Refit Standard

### Batch dialog standard (first-show)

- Target: `HongKongCspfBatchDialog`
- Pattern: hidden-first build → layout settle → measure → geometry → show
- Reference: 236 summary, 249 summary
- **Not applicable to main window.** Batch code was not copied into main.

### Main visible refit standard (this work)

- Target: ISO tab, nested notebook, detail open/close, profile switch
- Pattern: content mutation → scheduler request → settle → side-effect-free
  visible snapshot → one geometry apply
- **Measurement must not visibly mutate notebook selection.**

## Implemented Changes

### `ui_tk/window_measurement.py`

- **Removed**: `for tab_id in tabs: notebook.select(tab_id)` loop and
  `suppress_measurement()` context usage from `_measure_nested_notebook()`.
- **Added**: `self._observed_max_tab_width` instance variable for horizontal
  width cache.
- **New behavior**: `_measure_nested_notebook()` now:
  1. Reads `notebook.select()` to get the current tab (no mutation).
  2. Measures only the current tab widget's `winfo_reqwidth()` and
     `winfo_reqheight()`.
  3. Updates `_observed_max_tab_width = max(cache, current_tab_width)`.
  4. Returns `NestedNotebookMeasurement` with:
     - `max_tab_width = observed_max_tab_width`
     - `max_tab_height = current_tab_height`
     - `current_tab_height = current_tab_height`
     - `notebook_height = notebook.winfo_reqheight()`

### `tests/test_ui_tk_window_measurement_side_effect_free.py`

| Test | Result |
|---|---|
| `test_measurement_does_not_select_hidden_tabs` | PASS |
| `test_current_tab_height_is_used` | PASS |
| `test_observed_width_cache_updates` | PASS |
| `test_snapshot_is_side_effect_free_across_repeated_calls` | PASS |
| `test_no_nested_notebook_returns_empty_measurement` | PASS |
| `test_inactive_nested_notebook_returns_empty_measurement` | PASS |

## Side-Effect-Free Measurement Policy

- **Visible main content measurement must not mutate UI state.**
- Hidden tab sizes must not be obtained by programmatic selection.
- Current tab height is the automatic-fit height source.
- Hidden tab width stabilization uses an observed cache updated only from
  visible/current tab measurements.
- Overflow is handled by scroll/viewport policy, not by measuring hidden
  content.

## Tests

### New tests

- `tests/test_ui_tk_window_measurement_side_effect_free.py`: 6 passed

### Regression tests

- `tests/test_ui_tk_window_shell.py`: 10 passed
- `tests/test_ui_tk_window_lifecycle_repair.py`: 2 passed, 9 skipped
- `tests/test_ui_tk_iso_table_autocalc.py -k detail`: 1 passed, 16 skipped
- `tests/test_ui_tk_bin_detail_schema.py`: 7 passed, 14 skipped
- `tests/test_ui_tk_hong_kong_hspf_detail.py`: 10 skipped

## Manual Windows Smoke Checklist

- [ ] Hong Kong profile entry does not auto-switch CSPF/HSPF tabs.
- [ ] Hong Kong profile entry has no flicker/refit loop.
- [ ] CSPF detail open → HSPF tab switch → HSPF current content refit.
- [ ] HSPF detail open → window grows to show detail content.
- [ ] HSPF detail close → window can shrink.
- [ ] CSPF detail close → manual shrink possible.
- [ ] ISO/ISEER detail open/close normal.
- [ ] SASO detail open/close normal.
- [ ] Rapid tab switch/detail open-close has no resize loop or gray screen.

## Excluded Scope

- No core calculator changes.
- No golden/fixture changes.
- No batch/matrix changes.
- No `bin_detail_panel.py`, `bin_trace_table.py`, `bin_detail_schema.py`
  changes.
- No EN/AHRI/KS profile expansion.
- No BaseSection or shared result framework.
- No table controller / `MetricInputTable` changes.
- No ResultPanel changes.
- No 256 repairs rolled back (minsize, callback, tab-change binding remain).

## Known Risks

- Width may initially be smaller than the widest hidden tab until the user
  visits that tab and the observed cache updates. This is an acceptable trade-
  off to eliminate flicker loops.
- Headless environment skips Tk widget tests; Windows GUI smoke is the final
  verification.

## Next Suggested Action

**Main table migration candidate check.**

- With window lifecycle and measurement stable, assess whether
  `MetricInputTable` surfaces can converge on a common table foundation.

## Project Memory Delta

- `TkVisibleContentMeasurement._measure_nested_notebook()` must never
  programmatically select hidden tabs. This is the #1 cause of flicker/refit
  loops when combined with `<<NotebookTabChanged>>` bindings.
- Side-effect-free measurement is a mandatory precondition for loop-safe refit.
- Batch dialog hidden-first lifecycle and main visible refit lifecycle are
  separate standards. Batch code should not be copied into main; instead, apply
  the correct standard for each context.
- `_observed_max_tab_width` cache provides width stability without UI mutation.
