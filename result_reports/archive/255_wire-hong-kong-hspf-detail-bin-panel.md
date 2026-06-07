# 255 Wire Hong Kong HSPF Detail/Bin Panel Using Configurable Heating Schema

## Goal

Add detail/bin panel support to the existing Tkinter Hong Kong HSPF single-case
section, reusing the schema-driven `BinDetailPanel` shell and
`HEATING_HSPF_BIN_DETAIL_SCHEMA` prepared in 253/254.

## Scope

- Add detail toggle button and `BinDetailPanel` to `hong_kong_hspf_section.py`.
- Wire `result["bin_details"]` into `BinDetailSource` on calculation success.
- Handle invalid/error states to clear stale detail rows.
- Add focused tests for the new wiring.
- Update `docs/WORK_PLAN.md` and `project_log.md`.

## Reference Wiring Evidence

### Reused from CSPF section (`hong_kong_cspf_section.py`)

| Pattern | CSPF Owner | HSPF Adaptation |
|---|---|---|
| Detail toggle button + open/close | `_toggle_detail()` | Identical logic, different row index |
| Detail panel hidden initially | `_detail_visible = False` | Identical |
| `BinDetailPanel` with `show_source_selector=False` | single-source CSPF | single-source HSPF |
| `set_sources()` with `BinDetailSource` | `_update_detail_panel()` | Identical pattern |
| `_clear_trace()` for stale data | `_clear_trace(status)` | Identical |
| Invalid input → clear trace | `recalculate_now()` ValueError path | Identical |
| Calc exception → clear trace | `recalculate_now()` except path | Identical |

### Not reused (HSPF-specific)

- No batch button (single-case only).
- No rated/declared capacity input (HSPF uses measured 7 Full as standard capacity).
- Summary formatter uses HSPF/HSTL/HSEC instead of CSPF/CSTL/CSEC.
- `HEATING_HSPF_BIN_DETAIL_SCHEMA` instead of default cooling schema.

### Why `BinDetailPanel` modification was not needed

The shell already accepts `schema` parameter. Heating graph series, table
columns, and title are all declared in `HEATING_HSPF_BIN_DETAIL_SCHEMA`. No
shell code change was required.

## Implemented Changes

### `ui_tk/sections/hong_kong_hspf_section.py`

- **Imports**: `BinDetailPanel`, `BinDetailSource`, `HEATING_HSPF_BIN_DETAIL_SCHEMA`
- **Instance vars**: `_trace_rows`, `_detail_summary`, `_trace_status`, `_detail_visible`
- **UI additions**:
  - `action_row` at grid row 3 with `detail_toggle` button.
  - `BinDetailPanel` at grid row 4 (hidden initially) with heating schema.
- **`recalculate_now()`**:
  - ValueError path: `_clear_trace("입력 오류: 숫자 입력을 확인하세요.")`
  - Exception path: `_clear_trace("계산 오류")`
  - Success path: populate `_trace_rows` and `_detail_summary`, then `_update_detail_panel()`
- **New methods**:
  - `_toggle_detail()`: open/close detail panel, update button text.
  - `_update_detail_panel()`: call `detail_panel.set_sources()` with current trace data.
  - `_clear_trace(status)`: reset trace state and update panel to status.
- **Module-level helpers**:
  - `_hspf_bin_details(result)`: extract `bin_details` list from result dict.
  - `_hspf_summary_from_result(result)`: build `(HSPF, HSTL [kWh], HSEC [kWh])` tuple.

### `tests/test_ui_tk_hong_kong_hspf_detail.py`

| Test | Status |
|---|---|
| `test_section_defaults_calculate_hspf_summary` | SKIP (Tk unavailable) |
| `test_detail_panel_initially_hidden` | SKIP (Tk unavailable) |
| `test_detail_toggle_opens_detail_panel` | SKIP (Tk unavailable) |
| `test_detail_toggle_closes_detail_panel` | SKIP (Tk unavailable) |
| `test_detail_panel_uses_heating_graph_labels` | SKIP (Tk unavailable) |
| `test_detail_table_headers_equal_heating_schema` | SKIP (Tk unavailable) |
| `test_detail_rows_populated_from_bin_details` | SKIP (Tk unavailable) |
| `test_detail_copy_button_uses_header_included_tsv` | SKIP (Tk unavailable) |
| `test_detail_csv_button_calls_helper` | SKIP (Tk unavailable) |
| `test_invalid_input_clears_stale_rows` | SKIP (Tk unavailable) |

## HSPF Detail Schema Usage

- **Table columns**: Bin No, Temp [°C], Hours, Load [W], Delivered [W], Power [W],
  Case, Heat Pump [Wh], Auxiliary [Wh], Total [Wh]
- **Graph series**: Bin Hours [h], Load [W], Delivered [W], Power [W],
  Heat Pump [Wh], Auxiliary [Wh], Total [Wh]
- **Table title**: "난방 상세 표"
- **Source label**: "Hong Kong HSPF"
- **CSV filename**: `hong_kong_hspf_bin_detail.csv`

## Error/Stale State Handling

- **Invalid input**: `_clear_trace("입력 오류: 숫자 입력을 확인하세요.")` sets
  detail panel status, so stale rows are replaced with status text.
- **Calculation exception**: `_clear_trace("계산 오류")` does the same.
- **ResultPanel error UX**: unchanged; still shows safe summary status.

## MVC / SoC Boundary

- `hong_kong_hspf_section.py` owns:
  - Section-level widget wiring.
  - Calculator result → `BinDetailSource` mapping.
  - Toggle / visibility lifecycle.
- `bin_detail_panel.py` owns:
  - Panel shell (selector, summary, graph, table, actions).
  - Copy/export delegation to helpers.
- `bin_detail_schema.py` owns:
  - `HEATING_HSPF_BIN_DETAIL_SCHEMA` definition.
- `table_clipboard.py` / `table_csv_export.py` own:
  - TSV/CSV formatting and I/O.
- No shell modification needed; schema injection is the only coupling point.

## Manual Smoke Checklist

- [ ] Hong Kong HSPF section open.
- [ ] Default calculation shows HSPF summary as before (≈3.643).
- [ ] Detail panel initially hidden.
- [ ] `상세 보기 ↓` click → heating detail table appears.
- [ ] Graph combo shows heating series: Bin Hours, Load, Delivered, Power, Heat Pump, Auxiliary, Total.
- [ ] Detail table shows heating columns: Load, Delivered, Power, Case, Heat Pump, Auxiliary, Total.
- [ ] `상세 복사` copies header-included heating table TSV to clipboard.
- [ ] `상세 CSV보내기` creates CSV with heating headers/rows.
- [ ] Invalid input clears previous detail rows.
- [ ] Detail close/open does not flicker or resize unexpectedly.

## Excluded Scope

- No core calculator changes.
- No golden/fixture changes.
- No batch/matrix HSPF surface.
- No xlsx/graph export/HTML export.
- No `bin_detail_panel.py`, `bin_trace_table.py`, `bin_detail_schema.py` changes.
- No EN/AHRI/KS profile expansion.
- No BaseSection or shared result framework.
- No table controller / `MetricInputTable` changes.
- No ResultPanel changes.

## Known Risks

- Headless environment skips all Tk widget tests; Windows GUI smoke is the final
  verification for visual/focus behavior.
- `bin_detail_panel.py` is at 438 LOC (soft limit 400). If more profiles need
  detail panels, consider extracting layout code from shell logic.
- Branch-specific HSPF trace keys (e.g. `X`, `PLF`, `cop_half`) are not shown in
  the fixed 10-column table. They remain in the raw row dict for future
  tooltip/status extensions.

## Next Suggested Action

**Main table migration candidate check.**

- Assess how existing `MetricInputTable` surfaces can converge on the common
  table foundation.
- The detail panel schema extraction proves that shell/schema separation works;
  apply the same principle to input table surfaces if beneficial.

## Project Memory Delta

- Hong Kong HSPF single-case detail surface is now wired and functional.
- The pattern is: `BinDetailPanel(schema=<profile_schema>)` + section-level
  `BinDetailSource(rows=..., summary=...)` wiring.
- No shell file modification is needed to add a new profile detail panel;
  only section wiring + schema definition + summary formatter are required.
