# 252 Hong Kong HSPF Detail/Bin Trace Schema Preflight

## Goal

Determine whether Hong Kong HSPF single-case detail/bin trace support can be
added by reusing existing UI/detail contracts, or if a core trace-output design
slice is needed first.

## Scope

- Inspect current Hong Kong HSPF UI surface and result handling.
- Inspect core ISO16358 HSPF calculator output, specifically `bin_details`.
- Compare with existing CSPF/detail/bin reference behavior.
- Propose heating bin/detail schema.
- Recommend next action (implementation vs blocked).

## Current Hong Kong HSPF UI Owner

- **File**: `ui_tk/sections/hong_kong_hspf_section.py` (123 LOC)
- **Components**:
  - `MetricInputTable` for 7 Full / 7 Half capacity and power.
  - `ResultPanel` showing HSPF / HSTL / HSEC summary card.
  - `DebouncedAutoCalc` for automatic recalculation.
- **Missing**: No detail panel, no trace table, no copy/CSV export for details.
- The section calls `core.calculator_dispatcher.create_calculator_for_profile`
  with `profile_id='hong_kong_hspf'` and then `calc.calculate_hspf(measured)`.

## Core HSPF Result/Detail Availability

### Calculator paths

The core `calculator_iso16358.py` has two `calculate_hspf` paths:

1. **Generic HSPF** (line 1710-1800): returns `bin_details` with fields
   `tj`, `hours`, `load`, `available_capacity`, `compressor_heat`,
   `compressor_energy`, `heat_pump_energy`, `auxiliary_heat`,
   `auxiliary_energy`, `bin_load`, `bin_energy`.

2. **ISO16358-2 HSPF common** (`calculate_hspf_iso16358_common`, line 1640-1709):
   used by the Hong Kong profile (`profile='iso16358_2_hspf'`).

### Hong Kong HSPF result keys (confirmed by smoke test)

```python
{
    'hspf': 3.643,
    'hstl_wh': <float>,
    'hsec_wh': <float>,
    'heat_pump_energy_wh': <float>,
    'auxiliary_energy_wh': <float>,
    'bin_details': [...],
}
```

### Hong Kong HSPF bin detail item schema

Every `bin_details` item contains these common keys:

| Key | Meaning | Type |
|---|---|---|
| `tj` | Outdoor temperature [°C] | float |
| `nj` | Bin hours | float |
| `bl_h` | Heating load at this bin [W] | float |
| `frost` | Frost condition flag | bool |
| `pi_j` | Delivered heating capacity at this bin [W] | float |
| `P_j` | Power consumption at this bin [W] | float |
| `case` | Calculation branch case name | str |
| `heat_pump_energy` | Heat pump energy at this bin [Wh] | float |
| `auxiliary_energy` | Auxiliary energy at this bin [Wh] | float |
| `E_j` | Total energy at this bin [Wh] | float |

Branch-specific flattened trace keys (merged into the top-level detail dict):

- **cycling**: `X` (load ratio), `PLF` (part-load factor), `cycling_stage`
- **formula45_half_full**: `branch`, `cop_half`, `cop_full`, `cop_hf`
- **formula47_full_extended**: varies by formula result
- **formula49_half_full_frost**: varies by formula result
- **formula50_full_extended_frost**: `branch`, `P_fe`, `pi_ext_f`, `p_ext_f`, `backup_heat`
- **saturated**: `saturated_stage`, `backup_heat`
- **min_half_interpolation / min_half_interpolation_frost**: `branch`

The trace sub-dict exists as a key (`trace`) but is empty because the helper
flattens trace fields via `detail.update(branch_result["trace"])` before
returning.

**Conclusion: core trace output already exists.** No separate core trace-output
design slice is needed.

## Existing CSPF/Detail/Bin Reference Behavior

- **Reference file**: `ui_tk/sections/hong_kong_cspf_section.py`
- **Detail panel**: `BinDetailPanel` (`ui_tk/sections/bin_detail_panel.py`, 437 LOC)
- **Trace table**: `BinTraceTable` (`ui_tk/sections/bin_trace_table.py`, 174 LOC)
- **Wiring**: the CSPF section maps `result["bin_details"]` directly into
  `BinDetailSource(rows=...)` and passes it to `detail_panel.set_sources(...)`.
- **Columns** (cooling hardcoded in `bin_trace_table.py`):
  `Bin No`, `Temp [°C]`, `Hours`, `Load [W]`, `Capacity [W]`, `Power [W]`,
  `EER`, `CSTL [Wh]`, `CSEC [Wh]`.
- **Graph series** (cooling hardcoded in `bin_detail_panel.py`):
  `nj`, `lc`, `capacity`, `power`, `eer`, `cstl_bin`, `csec_bin`.
- **Export/copy**: `BinDetailPanel` delegates to `BinTraceTable.table_export_data()`
  and uses `table_clipboard` / `table_csv_export` helpers.

## Comparison: Cooling vs Heating Bin Detail Contracts

| Aspect | Cooling (CSPF) | Heating (HSPF, iso16358_2) |
|---|---|---|
| Core returns `bin_details` | Yes | Yes |
| Detail dict keys | `tj`, `nj`, `lc`, `capacity`, `power`, `eer`, `cstl_bin`, `csec_bin` | `tj`, `nj`, `bl_h`, `pi_j`, `P_j`, `case`, `heat_pump_energy`, `auxiliary_energy`, `E_j`, plus branch trace |
| Temperature field | `tj` | `tj` |
| Hours field | `nj` | `nj` |
| Load field | `lc` | `bl_h` |
| Capacity field | `capacity` | `pi_j` (delivered heat) |
| Power field | `power` | `P_j` |
| Efficiency field | `eer` | No direct COP at top level; trace has `cop_half`, `cop_full`, etc. |
| Energy summary fields | `cstl_bin`, `csec_bin` | `heat_pump_energy`, `auxiliary_energy`, `E_j` |
| Branch case name | Not present | `case` (cycling, formula45, etc.) |

## Proposed Heating Bin/Detail Schema

A user-facing HSPF trace table should present the data the user can interpret.
Two candidate schemas:

### Candidate A: Field-preserving schema (maps core keys directly)

| Column | Source key | Notes |
|---|---|---|
| Bin No | index | derived |
| Temp [°C] | `tj` | |
| Hours | `nj` | |
| Load [W] | `bl_h` | |
| Delivered [W] | `pi_j` | heating capacity delivered |
| Power [W] | `P_j` | |
| Case | `case` | branch name (cycling, formula45, etc.) |
| Heat Pump [Wh] | `heat_pump_energy` | |
| Auxiliary [Wh] | `auxiliary_energy` | |
| Total [Wh] | `E_j` | |

### Candidate B: Simplified schema (hides branch detail)

Same as Candidate A but omits `Case` column for a cleaner view. The branch name
can remain visible in a tooltip or detail status if needed.

### Graph series for heating

A heating `BinDetailGraph` should allow plotting these series:

| Label | Key | Notes |
|---|---|---|
| Bin Hours [h] | `nj` | same as cooling |
| Load [W] | `bl_h` | heating load |
| Delivered [W] | `pi_j` | delivered heat |
| Power [W] | `P_j` | power consumption |
| Heat Pump [Wh] | `heat_pump_energy` | |
| Auxiliary [Wh] | `auxiliary_energy` | |
| Total [Wh] | `E_j` | |

Note: there is no single `cop` or `eer` key at the top level for every bin. COP
can be computed as `pi_j / P_j` where `P_j > 0`, but it is not a core output
field.

## Blockers

### 1. `BinTraceTable` is cooling-hardcoded

- `BIN_TRACE_COLUMNS` and `_COLUMN_KEYS` are module-level tuples in
  `bin_trace_table.py`. They cannot represent heating fields without code
  change.
- **Impact**: A new heating trace table (or parameterized trace table) is
  required.

### 2. `BinDetailPanel._GRAPH_SERIES` is cooling-hardcoded

- The graph series tuple references cooling-only keys (`eer`, `cstl_bin`,
  `csec_bin`, `lc`, `capacity`, `power`).
- **Impact**: A heating graph series config (or parameterized config) is
  required.

### 3. `BinDetailPanel` instantiates `BinTraceTable` internally

- Line 119: `self.table = BinTraceTable(self._frame, title="상세 표")`
- There is no constructor parameter to inject a different trace table class.
- **Impact**: Either `BinDetailPanel` needs parameterization, or a new heating
  detail panel class is needed.

## Does Core Trace Output Already Exist?

**Yes.**

- The Hong Kong HSPF profile (`iso16358_2_hspf`) already returns `bin_details`
  with temperature, load, capacity, power, energy, branch case, and
  branch-specific trace fields.
- No new core calculator output, no new trace schema design, and no new core
  API is needed.

## Implementation Recommendation

### Option A: New heating-specific classes (safer, less coupling)

1. Create `HspfBinTraceTable` in a new file or alongside `bin_trace_table.py`,
   using the heating column/key schema (Candidate A or B).
2. Create `HspfBinDetailPanel` (or parameterized `BinDetailPanel`) with a
   heating `_GRAPH_SERIES` tuple.
3. Update `hong_kong_hspf_section.py` to instantiate the detail panel and wire
   toggle + copy + CSV export, following the CSPF section pattern.
4. Add section-level helpers `_hspf_bin_details(result)` and
   `_hspf_summary_from_result(result)` analogous to the CSPF helpers.

### Option B: Parameterize existing classes (less duplication)

1. Add `columns` and `column_keys` parameters to `BinTraceTable.__init__`.
2. Add `graph_series` parameter to `BinDetailPanel.__init__`.
3. Pass heating parameters from `hong_kong_hspf_section.py`.
4. Risk: touches existing CSPF/ISEER surfaces; requires regression verification.

**Recommended**: Option A for the next slice. It keeps existing cooling surfaces
untouched and respects the proven surface contract. Option B can be evaluated
later if heating and cooling detail panels converge enough to justify
unification.

### Next action

- **Proceed with UI implementation slice** (create heating trace table + detail
  panel + section wiring). No core change needed.
- **Not blocked** by missing core trace data.
- **Before implementation**, confirm the exact user-facing column set (Candidate
  A vs B) and whether the `Case` column is desired.

## Excluded Scope

- No core calculator changes.
- No golden fixture changes.
- No batch/matrix HSPF surface.
- No PyQt5 AHRI HSPF2 migration.
- No xlsx/graph export beyond existing Canvas graph.
- No `ResultPanel` changes.
- No code changes in this audit slice.

## Known Risks

- Branch-specific trace keys vary by bin (e.g. `X`/`PLF` for cycling, `cop_half`
  for formula45). A fixed-column trace table cannot show all branch-specific
  fields simultaneously. The `case` column can indicate the branch; branch fields
  that are missing for a given row can display `-` or empty.
- If future profiles need yet another detail schema, further trace table variants
  may be needed. Parameterization may become worthwhile at that point.
- `BinDetailPanel` is 437 LOC. Adding a subclass or parameter increases surface
  complexity. Keep the new panel class thin (only override table/graph config).

## Project Memory Delta

- Core HSPF `bin_details` is already available for Hong Kong (`iso16358_2_hspf`).
- The existing `BinTraceTable` and `BinDetailPanel` are cooling-hardcoded and
  cannot display heating traces without modification.
- Heating detail implementation is unblocked at the core level. The next slice
  should create heating-specific trace table / detail panel classes and wire
  them into `hong_kong_hspf_section.py`.
- The `trace` sub-dict in core HSPF bin details is empty because trace fields
  are flattened into the top-level detail dict. UI consumers should read
  branch-specific keys from the top level, not from a nested `trace` key.
