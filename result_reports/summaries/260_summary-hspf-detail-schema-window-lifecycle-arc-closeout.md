# 260 Summary: HSPF Detail/Schema and Shared Tk Window Lifecycle Repair Arc Closeout

## Arc Scope

This summary covers the complete work arc from 250 through 259:
- 250: Summary wording correction (249 smoke status)
- 251–255: Hong Kong HSPF detail panel, bin trace schema extraction, and wiring
- 256–259: Shared Tk visible content measurement and window lifecycle repair

## Completed Work

### HSPF Detail/Schema Arc (251–255)

| # | Work | Status |
|---|---|---|
| 251 | Audit result/detail/export common contract | Complete |
| 252 | HSPF detail/bin trace schema preflight | Complete |
| 253 | Configurable `BinDetailSchema` extraction | Complete |
| 254 | Legacy cooling constants cleanup | Complete |
| 255 | Hong Kong HSPF detail/bin panel wiring | Complete |

**Key outcomes:**
- `BinDetailPanel` / `BinTraceTable` / `BinDetailGraph` are now schema-driven shells.
- `HEATING_HSPF_BIN_DETAIL_SCHEMA` defines heating-specific columns, keys, graph series, and title.
- `COOLING_BIN_DETAIL_SCHEMA` remains the default for cooling profiles.
- No hardcoded cooling constants remain in `bin_trace_table.py` or `bin_detail_panel.py`.
- Hong Kong HSPF single-case section now has detail toggle, trace table, graph, copy, and CSV export.

### Window Lifecycle Repair Arc (256–259)

| # | Work | Status |
|---|---|---|
| 256 | Remove `root.minsize()` from `fit_visible_content()` | Complete, smoke OK |
| 257 | Side-effect-free nested notebook measurement | Complete, smoke OK |
| 258 | Current-state width/height replacement | Complete, smoke OK |
| 259 | Width replacement using chrome-width estimate | Complete, smoke OK |

**Key outcomes:**
- Window minsize is no longer permanently locked by detail-open content.
- Metric notebook tab changes trigger refit via `DynamicContentRefitScheduler`.
- HSPF detail visibility callback wiring matches CSPF pattern.
- `TkVisibleContentMeasurement._measure_nested_notebook()` never programmatically selects hidden tabs.
- Width and height both use replacement formulas:
  - `content_width = content_reqwidth - notebook_width + chrome_width + current_tab_width`
  - `content_height = content_reqheight - notebook_height + chrome_height + current_tab_height`
- Chrome estimates are computed once per axis and cached; they are not sticky targets.

## Windows Manual Smoke Closeout

All window lifecycle items confirmed OK on Windows:

- [x] Hong Kong profile entry does not auto-switch CSPF/HSPF tabs.
- [x] Hong Kong profile entry has no flicker/refit loop.
- [x] Hong Kong CSPF detail open grows window if needed.
- [x] Hong Kong CSPF detail close shrinks to compact state (width and height).
- [x] Hong Kong CSPF detail open → HSPF tab switch refits to HSPF current compact state (width and height).
- [x] Hong Kong HSPF detail open grows to show detail content (width and height).
- [x] Hong Kong HSPF detail close shrinks to compact state (width and height).
- [x] ISO/ISEER detail open/close remains normal.
- [x] SASO detail open/close remains normal.
- [x] Rapid tab switch/detail open-close has no resize loop or gray screen.

## Durable Decisions

1. `BinDetailPanel` / `BinTraceTable` / `BinDetailGraph` remain schema-driven shells for new profiles.
2. HSPF detail uses `HEATING_HSPF_BIN_DETAIL_SCHEMA`; no heating-specific hardcode in UI shells.
3. Window measurement must not mutate visible UI state (no hidden tab select).
4. Main visible refit uses current visible tab/detail state for both width and height.
5. `fit_visible_content()` does not update `root.minsize()`; minsize is a baseline floor set during init.
6. Batch dialog hidden-first lifecycle and main visible refit lifecycle are separate standards.
7. Chrome estimates (`_chrome_height_estimate`, `_chrome_width_estimate`) are one-time computed helpers, not sticky target sizes.
8. Asymmetric measurement policies (one axis replaced, the other `max()` fallback) cause asymmetric shrink/grow behavior and must be avoided.

## Excluded / Deferred

- Main table migration candidate check (next action).
- EN/AHRI/KS profile expansion.
- BaseSection or shared result framework.
- Batch matrix table convergence.
- Graph export (PNG/SVG) or HTML export.

## Known Risks

- Chrome estimates are computed once. If notebook chrome (tab bar height, tab border width) changes after first measurement, the estimate may be slightly off.
- Width may initially be narrower than a hidden wide tab; window refits when that tab is visited.
- Headless environment skips Tk widget tests; Windows GUI smoke remains the final verification for measurement policy changes.

## Next

**Main table migration candidate check** (design-gated analysis).
- Focus surface: `MetricInputTable` and main single-case input/result surfaces.
- Driver: architectural convergence and cleanup before future profile expansion.
- Not a current user-facing bug fix.
