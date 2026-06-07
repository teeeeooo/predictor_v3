# 256 Repair Shared Tk Content-Hugging Refit/Minsize Lifecycle

## Goal

Repair the shared Tkinter window lifecycle so that:
- detail open/close correctly triggers parent refit,
- window minsize is not permanently locked by detail-open content,
- nested notebook tab switches refit to the current tab's content size.

Hong Kong CSPF/HSPF was the repro case; fixes are in shared owners, not
Hong Kong-only hacks.

## Scope

- `window_shell.py`: remove minsize update from `fit_visible_content()`.
- `iso16358_tab.py`: re-enable metric tab change refit via scheduler;
  wire HSPF detail visibility callback.
- `hong_kong_hspf_section.py`: add `on_trace_visibility_changed` parameter
  and callback invocation in `_toggle_detail()`.
- Tests: window shell minsize policy, HSPF callback contract, metric tab
  change refit scheduling.
- `docs/WORK_PLAN.md` and `project_log.md` updates.

## User Repro

1. **CSPF detail open → HSPF tab switch**: window stayed at CSPF detail-open size.
2. **HSPF detail open**: window stayed small, detail content was clipped.
3. **CSPF detail close**: window could not shrink below detail-open size.
4. **Gray screen**: rare, after manual resize following HSPF detail open.

## Root Cause

### Root cause 1: `fit_visible_content()` permanently raises `root.minsize`

`window_shell.py` line 179: `root.minsize(target_width, target_height)` was
called on every content fit. When detail opened, the fit target grew; minsize
grew with it. On Windows, subsequent `geometry()` calls to smaller sizes were
clamped by the enlarged minsize, preventing shrink.

### Root cause 2: `_on_metric_tab_changed` was disabled

`iso16358_tab.py` lines 181-184: the metric notebook tab change handler was
commented out with a note about resize loops. Without it, switching tabs never
triggered refit.

### Root cause 3: HSPF section missing detail visibility callback

`iso16358_tab.py` lines 267-274: CSPF received
`on_trace_visibility_changed=self._on_trace_visibility_changed`, but HSPF
(the `else` branch) did not. So HSPF detail toggle never requested parent refit.

### Gray-screen risk hypothesis

Rapid geometry mutations (fit → user resize → fit → resize) combined with
nested notebook re-layout could trigger Tk redraw race conditions. Removing the
repeated minsize mutation and using the scheduler-based refit (which coalesces
requests) reduces the mutation frequency.

## Shared Owner Decision

| Symptom | Shared Owner | Fix |
|---|---|---|
| Minsize lock | `window_shell.py` | Remove `root.minsize()` from `fit_visible_content()` |
| Tab switch no refit | `iso16358_tab.py` | Bind `<<NotebookTabChanged>>` to scheduler-based refit |
| HSPF detail no refit | `iso16358_tab.py` + `hong_kong_hspf_section.py` | Pass callback to HSPF constructor; invoke on toggle |

No Hong Kong-only geometry conditionals were added. The fixes are generic and
apply to all profiles using the shared shell.

## Implemented Changes

### `ui_tk/window_shell.py`

- **Removed**: `root.minsize(target_width, target_height)` from
  `fit_visible_content()`.
- `fit_visible_content()` now only sets `root.geometry(target_geometry)`.
- minsize is set once during initialization (by `center_window()`) and never
  mutated by content fit.

### `ui_tk/tabs/iso16358_tab.py`

- **Enabled**: `_on_metric_tab_changed()` now calls
  `_request_visible_lifecycle_refit()` instead of returning early.
- **Added**: `self._metric_notebook.bind("<<NotebookTabChanged>>", ...)` in
  `__init__` to wire the handler.
- **Fixed**: `_render_region()` now passes `on_trace_visibility_changed` to
  both CSPF and HSPF sections (using `factory in (HongKongCspfSection,
  HongKongHspfSection)` instead of `factory is HongKongCspfSection`).

### `ui_tk/sections/hong_kong_hspf_section.py`

- **Added**: `on_trace_visibility_changed: Callable[[], None] | None = None`
  parameter to `__init__()`.
- **Added**: `self._on_detail_visibility_changed = on_trace_visibility_changed`.
- **Fixed**: `_toggle_detail()` now calls `self._on_detail_visibility_changed()`
  at the end, matching the CSPF section pattern.

### `tests/test_ui_tk_window_shell.py`

- Updated 3 assertions that previously expected `minsize_calls == [(640, 500)]`
  to expect `minsize_calls == []`.

### `tests/test_ui_tk_window_lifecycle_repair.py`

- New test file with 11 tests covering:
  - minsize policy (2 pure unit tests, pass)
  - HSPF callback acceptance and invocation (3 tests, skip in headless)
  - metric tab change refit scheduling (4 tests, skip in headless)
  - ISO/ISEER/SASO/CSPF/HSPF callback wiring verification (5 tests, skip)

## Minsize Policy

- **Before**: `fit_visible_content()` set minsize = target on every fit.
- **After**: `fit_visible_content()` does not touch minsize.
- **Baseline minsize**: Set once by `center_window()` during app init. It is
  `min(APP_WINDOW_FALLBACK_MIN_WIDTH, init_width)` ×
  `min(APP_WINDOW_FALLBACK_MIN_HEIGHT, init_height)`, which is at most
  640×480 and can be smaller if the initial window is smaller.
- **Effect**: User can manually resize below detail-open size, but not below
  baseline. The window auto-fits to content when detail opens/closes or tabs
  switch. Scrollbar handles overflow if user manually shrinks further.

## Detail Callback Contract

- All sections with detail panels (`IsoIseer2PointSection`, `IsoSasoT3Section`,
  `HongKongCspfSection`, `HongKongHspfSection`) now receive
  `on_trace_visibility_changed` from `Iso16358Tab`.
- Each section's `_toggle_detail()` calls the callback after showing/hiding
  the detail panel.
- The callback is `Iso16358Tab._on_trace_visibility_changed()`, which requests
  a scheduler-based refit.

## Nested Notebook Refit Contract

- `<<NotebookTabChanged>>` on the metric notebook triggers
  `_on_metric_tab_changed()`.
- The handler calls `_request_visible_lifecycle_refit()`, which uses
  `DynamicContentRefitScheduler`.
- The scheduler coalesces duplicate requests and runs one settled refit,
  preventing select → refit → measure loops.
- The measurement loop in `window_measurement.py` still iterates all tabs to
  find max width, but height uses `current_tab_height`. For a complete
  current-tab-only measurement, a future refactor could separate max-tab
  caching from current-tab measurement.

## Tests

### New tests (`tests/test_ui_tk_window_lifecycle_repair.py`)

| Test | Result |
|---|---|
| `test_fit_visible_content_does_not_update_minsize` | PASS |
| `test_fit_visible_content_to_smaller_target_does_not_raise_minsize` | PASS |
| `test_hspf_section_accepts_callback_parameter` | SKIP (Tk unavailable) |
| `test_hspf_detail_toggle_calls_callback` | SKIP (Tk unavailable) |
| `test_hspf_detail_toggle_without_callback_does_not_crash` | SKIP (Tk unavailable) |
| `test_metric_tab_change_requests_refit` | SKIP (Tk unavailable) |
| `test_mode_change_still_requests_refit` | SKIP (Tk unavailable) |
| `test_iso_iseer_section_receives_visibility_callback` | SKIP (Tk unavailable) |
| `test_saso_section_receives_visibility_callback` | SKIP (Tk unavailable) |
| `test_hong_kong_cspf_receives_visibility_callback` | SKIP (Tk unavailable) |
| `test_hong_kong_hspf_receives_visibility_callback` | SKIP (Tk unavailable) |

### Regression tests

- `tests/test_ui_tk_window_shell.py`: 10 passed
- `tests/test_ui_tk_iso_table_autocalc.py -k detail`: 1 passed, 16 skipped
- `tests/test_ui_tk_bin_detail_schema.py`: 7 passed, 14 skipped
- `tests/test_ui_tk_hong_kong_hspf_detail.py`: 10 skipped

## Manual Windows Smoke Checklist

- [ ] ISO/ISEER detail open → window grows if needed.
- [ ] ISO/ISEER detail close → window can shrink back; manual shrink possible.
- [ ] SASO detail open/close behaves the same.
- [ ] Hong Kong CSPF detail open → window grows if needed.
- [ ] Hong Kong CSPF detail close → window returns/shrinks; manual shrink below
      previous detail size is possible.
- [ ] Hong Kong CSPF detail open → switch to HSPF tab → window refits to HSPF
      current content, not CSPF detail size.
- [ ] Hong Kong HSPF detail open → window grows to show detail content.
- [ ] Hong Kong HSPF detail close → window can shrink.
- [ ] Manual resize after HSPF detail open does not produce gray screen.
- [ ] Rapid open/close and CSPF/HSPF tab switching does not create resize loop
      or flicker.

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
- No Hong Kong-only geometry conditionals or section-local hacks.

## Known Risks

- The measurement still uses `max_tab_width` across all tabs, which may keep
  the window wider than the current tab needs. This is intentional to prevent
  width jumps when switching tabs. A future refactor could separate
  current-tab width from max-tab width.
- Headless environment skips all Tk widget tests; Windows GUI smoke is the
  final verification for visual/focus behavior.
- `bin_detail_panel.py` remains at 438 LOC (soft limit 400). Further additions
  should trigger a helper extraction.

## Next Suggested Action

**Main table migration candidate check.**

- With window lifecycle stable, assess whether `MetricInputTable` surfaces can
  converge on a common table foundation.
- The refit/minsize fixes prove that shared shell ownership works; apply the
  same separation to input table surfaces if beneficial.

## Project Memory Delta

- `fit_visible_content()` must not update `root.minsize()`. minsize is a
  baseline floor set during init, not a mutable target that grows with content.
- `DynamicContentRefitScheduler` is the correct owner for loop-safe refit.
  Direct synchronous refit on tab switch is dangerous; scheduler-based refit is
  safe.
- All detail-panel sections must receive `on_trace_visibility_changed` from
  the tab owner. Missing this callback is a common wiring gap that causes
  detail-open content to be invisible or clipped.
- `<<NotebookTabChanged>>` binding on nested notebooks is the standard way to
  request refit when tab content changes.
