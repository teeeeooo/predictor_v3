# 258 Repair Nested Notebook Current-State Width/Height Replacement for Detail Open/Close Refit

## Goal

Fix the remaining Hong Kong nested notebook window size refit issue after 257:
- detail open should expand window
- detail close should shrink window
- tab switch should refit to current tab's size

## Scope

- Update `window_measurement.py` to use current tab width (not sticky observed max)
- Replace the no-op height correction with a chrome estimate that properly handles
  sticky notebook heights
- Update tests for shrink behavior
- Update `docs/WORK_PLAN.md` and `project_log.md`

## User Repro

1. CSPF detail open → HSPF tab switch: window stayed at CSPF detail-open size
2. Detail open → close: window didn't shrink
3. These issues occurred only in Hong Kong (nested notebook), not in other profiles

## Non-Hong Kong vs Hong Kong Refit Path

| Aspect | Non-Hong Kong (ISO/ISEER, SASO) | Hong Kong (CSPF/HSPF) |
|---|---|---|
| Content structure | Section frame directly in `_content` | Notebook in `_content`, section in notebook tab |
| Nested notebook | No | Yes (`_metric_notebook`) |
| `notebook_height` in `snapshot()` | `0` (skipped) | `> 0` (correction runs) |
| Width source | `_content.winfo_reqwidth()` directly | `max(_content.winfo_reqwidth(), max_tab_width)` |
| Height source | `_content.winfo_reqheight()` directly | `_content.winfo_reqheight()` + correction formula |
| Detail open/close before 258 | Works | Width sticky, height formula no-op |

## Width Root Cause

`_measure_nested_notebook()` used `self._observed_max_tab_width`, a sticky cache
that only grew. When switching from a wide tab (CSPF detail-open) to a narrow tab
(HSPF detail-closed), `content_width = max(content_reqwidth, observed_max)` stayed
at the observed max, preventing width shrink.

**Fix**: `max_tab_width` is now `current_tab_width`, which reflects the currently
visible tab and shrinks when the tab narrows.

## Height Root Cause

The height correction formula:
```python
content_height = content_reqheight - notebook_height + chrome + current_tab_height
```

With 257's changes, `max_tab_height = current_tab_height`, so:
```
chrome = max(0, notebook_height - current_tab_height)
content_height = content_reqheight - notebook_height + (notebook_height - current_tab) + current_tab
content_height = content_reqheight  # no-op
```

If `content_reqheight` doesn't shrink (because the notebook widget reports a
sticky height), the window stays large.

**Fix**: Compute a one-time chrome estimate (`notebook_height - current_tab_height`
on first measurement) and use it in the formula instead of `max_tab_height`:
```python
content_height = content_reqheight - notebook_height + chrome_estimate + current_tab_height
```

This works even when `notebook_height` is sticky at a previous max tab height.

## Current-State Replacement Policy

- **Width**: `max_tab_width = current_tab_width` (visible tab only)
- **Height**: `content_height = content_reqheight - notebook_height + chrome_estimate + current_tab_height`
- **Chrome estimate**: computed once as `max(0, notebook_height - current_tab_height)`
- **No hidden tab selection**: 257's side-effect-free principle is preserved
- **No sticky cache**: width no longer uses a monotonically-growing cache

## Implemented Changes

### `ui_tk/window_measurement.py`

- **Added** `current_tab_width` to `NestedNotebookMeasurement`
- **Removed** `_observed_max_tab_width` instance variable
- **Added** `_chrome_estimate: int | None = None` instance variable
- **`_measure_nested_notebook()`**:
  - `max_tab_width` set to `current_tab_width` (no sticky cache)
  - `max_tab_height` set to `current_tab_height`
  - `current_tab_width` added to returned measurement
  - On first measurement: `chrome_estimate = max(0, notebook_height - current_tab_height)`
- **`snapshot()`**:
  - Width: `content_width = max(content_reqwidth, nested.max_tab_width)` where
    `max_tab_width` is current tab width
  - Height: formula now uses `self._chrome_estimate` instead of `max_tab_height`
  - Diagnostic field `chrome_estimate` added
  - Diagnostic field `nested_current_tab_width` added

### `tests/test_ui_tk_window_measurement_side_effect_free.py`

- **Updated** `test_current_tab_height_is_used` → `test_current_tab_width_and_height_are_used`
- **Removed** `test_observed_width_cache_updates` (cache removed)
- **Added** `test_width_shrinks_when_switching_to_narrow_tab`
- **Added** `test_height_shrinks_when_detail_closes`
- **Added** `test_chrome_estimate_computed_once`
- **Updated** `test_no_nested_notebook_returns_empty_measurement` and
  `test_inactive_nested_notebook_returns_empty_measurement` for new fields

## Tests

### New/updated tests

| Test | Result |
|---|---|
| `test_measurement_does_not_select_hidden_tabs` | PASS |
| `test_current_tab_width_and_height_are_used` | PASS |
| `test_width_shrinks_when_switching_to_narrow_tab` | PASS |
| `test_height_shrinks_when_detail_closes` | PASS |
| `test_chrome_estimate_computed_once` | PASS |
| `test_snapshot_is_side_effect_free_across_repeated_calls` | PASS |
| `test_no_nested_notebook_returns_empty_measurement` | PASS |
| `test_inactive_nested_notebook_returns_empty_measurement` | PASS |

### Regression tests

- `tests/test_ui_tk_window_shell.py`: 10 passed
- `tests/test_ui_tk_window_lifecycle_repair.py`: 2 passed, 9 skipped
- `tests/test_ui_tk_iso_table_autocalc.py -k detail`: 1 passed, 16 skipped
- `tests/test_ui_tk_hong_kong_hspf_detail.py`: 10 skipped
- `tests/test_ui_tk_bin_detail_schema.py`: 7 passed, 14 skipped

## Manual Windows Smoke Checklist

- [ ] Hong Kong profile entry does not auto-switch CSPF/HSPF tabs
- [ ] Hong Kong profile entry has no flicker/refit loop
- [ ] Hong Kong CSPF detail open → window grows if needed
- [ ] Hong Kong CSPF detail close → window shrinks to compact state
- [ ] Hong Kong CSPF detail close → manual shrink possible
- [ ] Hong Kong CSPF detail open → HSPF tab switch → HSPF current compact state refit
- [ ] Hong Kong HSPF detail open → window grows to show detail content
- [ ] Hong Kong HSPF detail close → window shrinks to compact state
- [ ] ISO/ISEER detail open/close normal
- [ ] SASO detail open/close normal
- [ ] Rapid tab switch/detail open-close has no resize loop or gray screen

## Excluded Scope

- No core calculator changes
- No golden/fixture changes
- No batch/matrix changes
- No `bin_detail_panel.py`, `bin_trace_table.py`, `bin_detail_schema.py` changes
- No EN/AHRI/KS profile expansion
- No BaseSection or shared result framework
- No table controller / `MetricInputTable` changes
- No ResultPanel changes
- 256 minsize repair and 257 side-effect-free measurement preserved

## Known Risks

- Width might initially be narrower than a hidden wide tab until that tab is
  visited. The window will refit when the user switches to that tab.
- Chrome estimate is computed once. If the notebook's tab bar height changes
  (e.g., due to font/size changes), the estimate might be slightly off.
- Headless environment skips Tk widget tests; Windows GUI smoke is the final
  verification.

## Next Suggested Action

**Main table migration candidate check.**

## Project Memory Delta

- `max_tab_width` must use `current_tab_width`, not a sticky observed cache.
- Height correction must use a cached `chrome_estimate` (tab bar height)
  rather than `max_tab_height`, because `max_tab_height` is no longer available
  without selecting hidden tabs.
- The formula `content_height = content_reqheight - notebook_height + chrome + current_tab`
  correctly replaces a sticky notebook height with the current visible tab height.
- Chrome estimate = `notebook_height - current_tab_height` on first measurement,
  when the notebook is guaranteed to be sized to the current tab.
