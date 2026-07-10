# 254 Cleanup Legacy Cooling Constants After Configurable Bin-Detail Schema Extraction

## Goal

Remove unused legacy cooling hardcode constants from `BinTraceTable` and
`BinDetailPanel` now that schema-driven parameterization is in place. Ensure
`BinTraceTable` uses the schema's `table_title` as its default title when no
explicit title is provided.

## Scope

- Remove unused `BIN_TRACE_COLUMNS` and `_COLUMN_KEYS` from `bin_trace_table.py`.
- Remove unused `_GRAPH_SERIES` from `bin_detail_panel.py`.
- Update `BinTraceTable.__init__()` to default title from schema when not
  explicitly provided.
- Add focused tests for title default behavior.
- Verify existing cooling behavior is preserved.

## Legacy Constant Inventory

| Constant | File | Status | Reason |
|---|---|---|---|
| `BIN_TRACE_COLUMNS` | `bin_trace_table.py` | **Unused** | Replaced by `schema.column_labels` |
| `_COLUMN_KEYS` | `bin_trace_table.py` | **Unused** | Replaced by `schema.column_keys` |
| `_GRAPH_SERIES` | `bin_detail_panel.py` | **Unused** | Replaced by `schema.graph_series` |

All three constants were module-level tuples that duplicated the values now
owned by `COOLING_BIN_DETAIL_SCHEMA` in `bin_detail_schema.py`. No external
imports or references exist for any of them.

## Cleanup Changes

### `ui_tk/sections/bin_trace_table.py`

- **Removed**: `BIN_TRACE_COLUMNS` module-level tuple (lines 23-33).
- **Removed**: `_COLUMN_KEYS` module-level tuple (lines 35-45).
- **Modified**: `BinTraceTable.__init__()`
  - `title` parameter changed from `str = "상세 표"` to `str | None = None`.
  - Label text resolves to `title if title is not None else schema.table_title`.
  - This means:
    - Default cooling table title remains `"상세 표"`.
    - Direct `BinTraceTable(parent, schema=HEATING_HSPF_BIN_DETAIL_SCHEMA)`
      now automatically uses `"난방 상세 표"`.
    - Explicit `title="Custom Title"` still overrides the schema title.

### `ui_tk/sections/bin_detail_panel.py`

- **Removed**: `_GRAPH_SERIES` module-level tuple (lines 29-37).
- No other changes needed; all graph series references already use
  `self._schema.graph_series`.

### `tests/test_ui_tk_bin_detail_schema.py`

- **Added**: `test_default_title_is_cooling_schema_title`
- **Added**: `test_heating_schema_default_title`
- **Added**: `test_explicit_title_overrides_schema_title`

## MVC / SoC Boundary

- Schema definitions remain in `bin_detail_schema.py`.
- `BinTraceTable` and `BinDetailPanel` remain pure shells with no embedded domain
  knowledge.
- The only default domain value remaining in the shell files is
  `COOLING_BIN_DETAIL_SCHEMA` as the constructor default, which is a thin
  adapter pattern, not hardcode.

## Tests

### New / updated tests (`tests/test_ui_tk_bin_detail_schema.py`)

| Test | Result |
|---|---|
| `test_default_title_is_cooling_schema_title` | SKIP (Tk unavailable) |
| `test_heating_schema_default_title` | SKIP (Tk unavailable) |
| `test_explicit_title_overrides_schema_title` | SKIP (Tk unavailable) |

### All tests in `test_ui_tk_bin_detail_schema.py`

- 7 passed, 14 skipped (Tk unavailable in headless environment).

### Regression tests (`test_ui_tk_iso_table_autocalc.py -k detail`)

- 1 passed (`test_bin_detail_graph_returns_y_scale_for_selected_series`)
- 16 skipped (Tk unavailable)

## Excluded Scope

- No Hong Kong HSPF section wiring.
- No core calculator changes.
- No golden/fixture changes.
- No ResultPanel changes.
- No batch matrix changes.
- No new duplicate classes.
- No BaseSection or shared result framework.

## Known Risks

- `bin_detail_panel.py` is at 438 LOC (soft limit 400). This is still within
  acceptable range for a Tkinter panel shell, and the count decreased from 449
  LOC after removing the unused constant. No new responsibilities were added.
- Headless environment skips Tk widget tests; Windows GUI smoke remains the final
  verification for visual/focus behavior.

## Next Suggested Action

**Hong Kong HSPF detail/bin panel wiring.**

The shell is now fully schema-driven with no cooling hardcode. The next slice
should wire `HEATING_HSPF_BIN_DETAIL_SCHEMA` into `hong_kong_hspf_section.py`
following the same pattern as the existing CSPF section.

## Project Memory Delta

- `BIN_TRACE_COLUMNS`, `_COLUMN_KEYS`, and `_GRAPH_SERIES` legacy constants are
  removed. The canonical source for these values is `COOLING_BIN_DETAIL_SCHEMA`.
- `BinTraceTable` defaults its title from the schema when no explicit title is
  provided. This makes direct `BinTraceTable(parent, schema=...)` usage
  consistent for any profile.
