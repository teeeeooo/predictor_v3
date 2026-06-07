# 253 Configurable Bin-Detail Schema Extraction

## Goal

Separate hardcoded cooling-specific bin detail schema from `BinTraceTable` /
`BinDetailPanel` so that Hong Kong HSPF (and future profile) detail/bin traces
can reuse the same UI shell via schema injection.

## Scope

- Extract `BinDetailSchema` dataclass with column labels, keys, graph series,
  and table title.
- Parameterize `BinTraceTable` to accept a schema (default: cooling).
- Parameterize `BinDetailPanel` and `BinDetailGraph` to accept graph series
  via schema (default: cooling).
- Define optional heating schema for later HSPF wiring.
- Add focused tests for default behavior preservation and schema injection.
- Update `docs/WORK_PLAN.md` and `project_log.md`.

## Reference / Hardcode Inventory

### Before extraction

| Component | Hardcoded | Location |
|---|---|---|
| `BinTraceTable` column labels | `BIN_TRACE_COLUMNS` | module-level tuple, line 19 |
| `BinTraceTable` value keys | `_COLUMN_KEYS` | module-level tuple, line 31 |
| `BinTraceTable` title | `"상세 표"` | constructor default |
| `BinDetailPanel` graph series | `_GRAPH_SERIES` | module-level tuple, line 25 |
| `BinDetailPanel._selected_graph_key()` | iterates `_GRAPH_SERIES` | line 227 |
| `BinDetailGraph.__init__` default series key | `_GRAPH_SERIES[0][1]` | line 246 |
| `BinDetailGraph._series_label()` | iterates `_GRAPH_SERIES` | line 396 |

### After extraction

| Responsibility | Owner | Notes |
|---|---|---|
| Schema definition | `bin_detail_schema.py` | `BinDetailSchema` dataclass + default schemas |
| Table shell (display, copy, export) | `BinTraceTable` | schema-driven, default cooling |
| Panel shell (selector, summary, graph, table, actions) | `BinDetailPanel` | schema-driven, default cooling |
| Graph shell (Canvas line plot) | `BinDetailGraph` | `graph_series` parameter, default cooling |
| Copy/export formatting | `table_clipboard.py` / `table_csv_export.py` | unchanged |

## Schema Extraction Design

### `BinDetailSchema` (immutable dataclass)

```python
@dataclass(frozen=True)
class BinDetailSchema:
    column_labels: tuple[str, ...]
    column_keys: tuple[str, ...]
    graph_series: tuple[tuple[str, str], ...]
    table_title: str = "상세 표"
```

Validation in `__post_init__`:
- `column_labels` and `column_keys` must have equal length.
- Neither columns nor graph_series may be empty.

### Default cooling schema

Identical to the previous hardcoded values:
- Columns: `Bin No`, `Temp [°C]`, `Hours`, `Load [W]`, `Capacity [W]`, `Power [W]`, `EER`, `CSTL [Wh]`, `CSEC [Wh]`
- Keys: `bin_no`, `tj`, `nj`, `lc`, `capacity`, `power`, `eer`, `cstl_bin`, `csec_bin`
- Graph series: 7 cooling-specific series

### Optional heating schema (`HEATING_HSPF_BIN_DETAIL_SCHEMA`)

- Columns: `Bin No`, `Temp [°C]`, `Hours`, `Load [W]`, `Delivered [W]`, `Power [W]`, `Case`, `Heat Pump [Wh]`, `Auxiliary [Wh]`, `Total [Wh]`
- Keys: `bin_no`, `tj`, `nj`, `bl_h`, `pi_j`, `P_j`, `case`, `heat_pump_energy`, `auxiliary_energy`, `E_j`
- Graph series: 7 heating-specific series
- **Not wired to any section yet.**

## Implemented Changes

### New file

- `ui_tk/sections/bin_detail_schema.py`
  - `BinDetailSchema` dataclass
  - `COOLING_BIN_DETAIL_SCHEMA`
  - `HEATING_HSPF_BIN_DETAIL_SCHEMA`

### Modified files

- `ui_tk/sections/bin_trace_table.py`
  - Import `BinDetailSchema` and `COOLING_BIN_DETAIL_SCHEMA`
  - `__init__` accepts `schema` parameter with cooling default
  - `column_labels` sourced from `schema.column_labels`
  - `set_data()` passes `schema.column_keys` to `_trace_row()`
  - `_trace_row()` accepts `column_keys` parameter

- `ui_tk/sections/bin_detail_panel.py`
  - Import `BinDetailSchema` and `COOLING_BIN_DETAIL_SCHEMA`
  - `BinDetailPanel.__init__` accepts `schema` parameter with cooling default
  - `graph_combo` values sourced from `schema.graph_series`
  - Passes `schema` to internal `BinTraceTable`
  - Passes `schema.graph_series` to internal `BinDetailGraph`
  - `_selected_graph_key()` uses `schema.graph_series`
  - `BinDetailGraph.__init__` accepts `graph_series` parameter
  - `BinDetailGraph._series_label()` uses instance `graph_series`

- `tests/test_ui_tk_iso_table_autocalc.py`
  - `test_bin_detail_graph_returns_y_scale_for_selected_series`: manually set
    `_graph_series` to match new `BinDetailGraph.__init__` contract.

- `tests/test_ui_tk_bin_detail_schema.py`
  - New test file: 18 tests covering schema validation, default/custom/heating
    table headers, row conversion, graph series labels, and graph label lookup.

- `docs/WORK_PLAN.md`
  - Updated next actions: HSPF detail/bin extension is now the current focus.

- `project_log.md`
  - Added milestone entry for configurable schema extraction decision.

## MVC / SoC Boundary

- `bin_detail_schema.py` owns pure schema definitions (no Tkinter, no core).
- `BinTraceTable` owns read-only table shell (display, selection, copy, export).
- `BinDetailPanel` owns panel shell (selector, summary, graph, table, actions).
- `BinDetailGraph` owns Canvas plotting shell.
- Domain-specific column/key/series knowledge lives in schema instances, not in
  the shell classes.
- Existing copy/export helpers (`table_clipboard`, `table_csv_export`) remain
  unchanged; they only know the generic `(headers, rows)` contract.

## Tests

### New tests (`tests/test_ui_tk_bin_detail_schema.py`)

| Test | Result |
|---|---|
| `test_cooling_schema_lengths_match` | PASS |
| `test_heating_schema_lengths_match` | PASS |
| `test_schema_post_init_rejects_mismatched_lengths` | PASS |
| `test_schema_post_init_rejects_empty_columns` | PASS |
| `test_schema_post_init_rejects_empty_graph_series` | PASS |
| `test_default_headers_are_cooling` | SKIP (Tk unavailable) |
| `test_default_table_export_data_with_rows` | SKIP (Tk unavailable) |
| `test_default_status_when_no_rows` | SKIP (Tk unavailable) |
| `test_custom_schema_headers` | SKIP (Tk unavailable) |
| `test_custom_schema_row_conversion` | SKIP (Tk unavailable) |
| `test_heating_schema_row_conversion` | SKIP (Tk unavailable) |
| `test_default_graph_series_labels` | SKIP (Tk unavailable) |
| `test_default_graph_series_first_selected` | SKIP (Tk unavailable) |
| `test_custom_graph_series_labels` | SKIP (Tk unavailable) |
| `test_custom_graph_series_first_selected` | SKIP (Tk unavailable) |
| `test_heating_graph_series_labels` | SKIP (Tk unavailable) |
| `test_custom_series_label_lookup` | PASS |
| `test_custom_series_fallback_label` | PASS |

### Regression tests (`tests/test_ui_tk_iso_table_autocalc.py -k detail`)

- 1 passed (`test_bin_detail_graph_returns_y_scale_for_selected_series`)
- 16 skipped (Tk unavailable)

## Excluded Scope

- No Hong Kong HSPF section wiring (`hong_kong_hspf_section.py` unchanged).
- No core calculator changes.
- No golden/fixture changes.
- No ResultPanel changes.
- No batch matrix changes.
- No xlsx/graph export/HTML export.
- No `HspfBinTraceTable` / `HspfBinDetailPanel` duplicate classes.
- No BaseSection or shared result framework.
- No table controller / `MetricInputTable` changes.
- No EN/AHRI/KS profile expansion.

## Known Risks

- `bin_detail_panel.py` now exceeds the 400 LOC soft limit (449 LOC). This is
  primarily from adding import lines and minimal schema parameter handling, not
  new responsibilities. A future refactor could split schema-aware shell code
  from layout code if the file grows further.
- `HEATING_HSPF_BIN_DETAIL_SCHEMA` defines fixed user-facing columns. Branch-
  specific trace keys (e.g. `X`, `PLF`, `cop_half`) that vary by bin are not
  displayed in the fixed column set; they remain available in the raw row dict
  for future tooltip/status extensions.
- Headless environment skips Tk widget tests; Windows GUI smoke remains the
  final verification for visual/focus behavior.

## Next Suggested Action

**Hong Kong HSPF detail/bin panel wiring.**

- Update `hong_kong_hspf_section.py` to:
  - Instantiate a detail toggle button.
  - Instantiate `BinDetailPanel` with `HEATING_HSPF_BIN_DETAIL_SCHEMA`.
  - Map `result["bin_details"]` into `BinDetailSource(rows=...)` on recalculate.
  - Wire toggle open/close and `_update_detail_panel()` similar to CSPF section.
- No new helper or class creation needed; reuse parameterized shells.

## Project Memory Delta

- Configurable `BinDetailSchema` is the canonical way to parameterize detail
  trace tables and graphs for new profiles.
- `COOLING_BIN_DETAIL_SCHEMA` preserves all existing CSPF/SASO/ISEER detail
  panel behavior.
- `HEATING_HSPF_BIN_DETAIL_SCHEMA` is ready for Hong Kong HSPF section wiring.
- UI shell classes (`BinTraceTable`, `BinDetailPanel`, `BinDetailGraph`) are
  now schema-driven with cooling defaults; they do not contain profile-specific
  hardcodes.
