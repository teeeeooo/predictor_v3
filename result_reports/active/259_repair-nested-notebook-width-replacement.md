# 259 Repair Nested Notebook Width Replacement Using Chrome-Width Estimate

## Goal

Fix the remaining Hong Kong nested notebook window width refit issue after 258:
- CSPF detail open → HSPF tab switch: width must shrink to HSPF compact state.
- HSPF detail open/close: width must grow/shrink with current visible state.
- All profiles must behave consistently for detail open/close width changes.

## Scope

- Update `window_measurement.py` to apply width chrome estimate and replacement
  formula, matching the already-working height replacement from 258.
- Update tests for width shrink behavior with sticky content width.
- Update `07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md` if the visible-main-refit
  policy text is stale.

## User Repro

1. Hong Kong profile → CSPF tab → open detail → window grows.
2. Switch to HSPF tab (compact state).
3. **Expected**: window width shrinks to HSPF compact width.
4. **Before 259**: width stayed at CSPF detail-open width because
   `max(content_reqwidth, current_tab_width)` kept the sticky large notebook
   width.

## Width Root Cause

`snapshot()` computed width as:
```python
content_width = max(self._content.winfo_reqwidth(), nested.max_tab_width)
```

In Hong Kong, `_content` contains the nested notebook. When the notebook is
sticky at a previous wide tab or detail-open state, `content_reqwidth` is large.
`max(large_sticky_value, current_tab_width)` never shrinks.

Height was already fixed in 258 with:
```python
content_height = content_reqheight - notebook_height + chrome_estimate + current_tab_height
```

Width needed the same treatment: subtract the sticky notebook width and add
back only the current visible tab's width plus chrome.

## Implemented Width Replacement Formula

```python
content_width = self._content.winfo_reqwidth()
if nested.notebook_width > 0 and self._chrome_width_estimate is not None:
    content_width = (
        content_width
        - nested.notebook_width
        + self._chrome_width_estimate
        + nested.current_tab_width
    )
elif nested.max_tab_width > 0:
    content_width = max(content_width, nested.max_tab_width)
```

Where:
- `notebook_width` = `notebook.winfo_reqwidth()` (measured once per snapshot)
- `chrome_width_estimate` = `max(0, notebook_width - current_tab_width)`
  (computed once on first nested notebook visit, cached)
- `current_tab_width` = visible tab widget `winfo_reqwidth()`

This mirrors the height formula and guarantees shrink when switching from a
wide detail-open tab to a narrow compact tab.

## Preserved 256/257/258 Repairs

| Repair | Status |
|---|---|
| `fit_visible_content()` does not update `root.minsize()` | Preserved |
| `_measure_nested_notebook()` does not `select(hidden_tab)` | Preserved |
| HSPF detail visibility callback wiring | Preserved |
| Metric tab change refit via scheduler | Preserved |
| Height replacement formula | Preserved (renamed `_chrome_estimate` → `_chrome_height_estimate`) |
| Side-effect-free repeated snapshot | Preserved |

## MVC/SoC Boundary

- `ui_tk/window_measurement.py` owns the measurement policy (width + height
  chrome estimates, replacement formulas, diagnostics).
- `ui_tk/window_shell.py` owns `fit_visible_content()` shell geometry apply.
- `ui_tk/window_refit.py` owns scheduler-based settled refit.
- `ui_tk/tabs/iso16358_tab.py` owns metric tab change event binding.
- Section files (`hong_kong_cspf_section.py`, `hong_kong_hspf_section.py`) own
  detail toggle callbacks; they were not modified in this slice.

## Tests

### New/updated tests

| Test | Result |
|---|---|
| `test_measurement_does_not_select_hidden_tabs` | PASS |
| `test_current_tab_width_and_height_are_used` | PASS |
| `test_width_shrinks_when_switching_to_narrow_tab` | PASS (updated with sticky content width) |
| `test_height_shrinks_when_detail_closes` | PASS |
| `test_chrome_height_estimate_computed_once` | PASS (renamed from `test_chrome_estimate_computed_once`) |
| `test_chrome_width_estimate_computed_once` | PASS (new) |
| `test_snapshot_is_side_effect_free_across_repeated_calls` | PASS |
| `test_no_nested_notebook_returns_empty_measurement` | PASS |
| `test_inactive_nested_notebook_returns_empty_measurement` | PASS |

### Regression tests

| Suite | Result |
|---|---|
| `tests/test_ui_tk_window_shell.py` | 10 passed |
| `tests/test_ui_tk_window_lifecycle_repair.py` | 2 passed, 9 skipped |
| `tests/test_ui_tk_iso_table_autocalc.py -k "detail or hspf"` | 1 passed, 16 skipped |

### Compile / structure checks

| Check | Result |
|---|---|
| `py_compile` window_measurement.py, window_refit.py, window_shell.py, window_geometry.py, iso16358_tab.py, hong_kong_hspf_section.py | OK |
| `tools/check_code_structure.py` | 2 warnings (pre-existing soft limit in batch_matrix_table.py, bin_detail_panel.py) |
| `git diff --check` | clean |

## Manual Windows Smoke Checklist

- [ ] Hong Kong profile 진입 시 CSPF/HSPF 탭 자동 왕복 없음.
- [ ] Hong Kong profile 진입 시 flicker/refit loop 없음.
- [ ] Hong Kong CSPF detail open → window grows if needed.
- [ ] Hong Kong CSPF detail close → width/height 모두 compact state로 shrink.
- [ ] Hong Kong CSPF detail open → HSPF tab 이동 → width/height 모두 HSPF current compact state로 refit.
- [ ] Hong Kong HSPF detail open → width/height 모두 detail content 기준으로 grow.
- [ ] Hong Kong HSPF detail close → width/height 모두 compact state로 shrink.
- [ ] ISO/ISEER detail open/close remains normal.
- [ ] SASO detail open/close remains normal.
- [ ] Rapid tab switch/detail open-close에서 resize loop나 gray screen 없음.

## Excluded Scope

- No core calculator changes.
- No golden/fixture changes.
- No batch/matrix changes.
- No `bin_detail_panel.py`, `bin_trace_table.py`, `bin_detail_schema.py` changes.
- No EN/AHRI/KS profile expansion.
- No BaseSection or shared result framework.
- No table controller / `MetricInputTable` changes.
- No ResultPanel changes.
- 256 minsize repair, 257 side-effect-free measurement, 258 height replacement preserved.

## Known Risks

- Chrome width estimate is computed once. If the notebook's horizontal chrome
  (tab border/padding) changes later, the estimate may be slightly off.
- Width might initially be narrower than a hidden wide tab; the window refits
  when the user visits that tab.
- Headless environment skips Tk widget tests; Windows GUI smoke is the final
  verification.

## Next Suggested Action

**Main table migration candidate check.**
Proceed only after Windows smoke confirms all checklist items pass.

## Project Memory Delta

- Width replacement formula mirrors height replacement:
  `content_width = content_reqwidth - notebook_width + chrome_width + current_tab_width`
- `_chrome_estimate` was split into `_chrome_height_estimate` and
  `_chrome_width_estimate` to keep each axis explicit and independent.
- `NestedNotebookMeasurement` now carries `notebook_width` alongside
  `notebook_height`.
- Visible main refit width/height must both replace sticky container
  contributions with current visible tab contributions.
- Chrome estimates (tab bar height, tab border width) are computed once on
  first measurement and cached; they are not sticky target sizes.
