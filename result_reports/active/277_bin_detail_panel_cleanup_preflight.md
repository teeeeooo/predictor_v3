# 277 BinDetailPanel Cleanup Preflight

## Goal

Assess `ui_tk/sections/bin_detail_panel.py` hotspot to determine the safest
first cleanup slice for `BinDetailPanel.__init__` and `BinDetailGraph._draw`
long functions.

## Scope

- Reference Evidence Gate usage on `CODEBASE_REFERENCE_MAP.md`.
- `BinDetailPanel` responsibility classification.
- `__init__` split candidate assessment.
- `_draw` split candidate assessment.
- External contract and regression risk analysis.
- Recommendation for next implementation slice.

## Excluded Scope

- No code changes.
- No test changes.
- No map regeneration (no structural code changes).
- No controller switch.
- No result formatting helper extraction (completed in 276).

## Reference Evidence Gate Usage (Task 1)

Per `docs/agent_workflows/DIFF_READ_BUDGET.md`:

- Map read: targeted `grep` on `bin_detail_panel`, `BinDetailPanel`,
  `BinDetailGraph`, `Active Hotspots` followed by 30–80 line range reads.
- Code read: `rg` for class/function definitions, then targeted range reads
  for `__init__`, `_draw`, `_refresh_current_source`, and public contract
  methods.
- No broad map reads.

## Map Evidence Summary

From `docs/code_map/CODEBASE_REFERENCE_MAP.md`:

| File | LOC | Classes | Long Functions |
|------|-----|---------|--------------|
| `ui_tk/sections/bin_detail_panel.py` | 388 | 3 | `__init__`(115), `_draw`(87) |

## Responsibility Classification (Task 2)

**BinDetailPanel** (class, ~147 LOC of methods + 115 LOC __init__):

1. **State management** — `_sources` dict, `_panel_status`, `_source_order`
2. **Widget construction** — `__init__` builds: frame, selector row, summary
   label, graph row, graph canvas, table, action buttons
3. **Source selection** — `set_sources()`, `selected_source()`,
   `_on_source_changed()`
4. **Status display** — `set_status()`
5. **Refresh coordination** — `_refresh_current_source()` (updates table,
   graph, summary label based on current source)
6. **Copy/export delegation** — `copy_table()`, `export_csv()`
7. **Graph series selection** — `_on_graph_changed()`, `_selected_graph_key()`

**BinDetailGraph** (class, ~87 LOC of _draw + 45 LOC _plot_points):

1. **Canvas construction** — `tk.Canvas` creation in `__init__`
2. **Data storage** — `_rows`, `_series_key`
3. **Drawing orchestration** — `_draw()` (canvas clear, dimensions, no-data
   state, axes, labels, line, dots, series label)
4. **Point calculation** — `_plot_points()` (data filtering, x/y extraction,
   coordinate mapping)
5. **Label formatting** — `_series_label()`, `_series_scale_label()`

**Bottom-level helpers** (module-level functions):

- `_number()` — safe float conversion
- `_flatten()` — flatten point tuples for canvas.create_line
- `_tick_text()` — axis tick formatting
- `_scale_value_text()` — series value formatting with precision

Assessment: `_number`, `_flatten`, `_tick_text`, `_scale_value_text` are already
well-factored pure helpers. `_plot_points` is already a data/coordinate
calculation helper. The long functions are `__init__` (widget construction
sequence) and `_draw` (canvas drawing sequence).

## `__init__` Split Assessment (Task 3)

**Current `__init__` (115 LOC) structure:**

1. Parameter/state storage (~8 LOC)
2. Frame creation (~3 LOC)
3. Selector row + source combobox/label (~25 LOC)
4. Summary label (~8 LOC)
5. Graph row + graph series combobox (~20 LOC)
6. Graph canvas (`BinDetailGraph`) (~8 LOC)
7. Table (`BinTraceTable`) (~8 LOC)
8. Action buttons (copy + export) (~22 LOC)
9. Initial refresh call (~1 LOC)

**Split candidates** (private setup helpers, zero behavior change):

- `_build_selector_row()` — selector frame, label, combobox, single-source label
- `_build_summary_label()` — summary text label
- `_build_graph_row()` — graph row frame, label, combobox
- `_build_action_buttons()` — copy + CSV buttons

**Risk**: LOW. These are pure widget construction sequences. No state logic,
no callbacks beyond simple bind. Splitting does not change construction order
or widget hierarchy.

**Test/smoke need**: None beyond `py_compile` and existing integration tests.
No visual change.

## `_draw` Split Assessment (Task 4)

**Current `_draw` (87 LOC) structure:**

1. Canvas clear + dimension calculation (~8 LOC)
2. Point calculation via `_plot_points()` (~5 LOC)
3. No-data state text (~8 LOC)
4. Y-axis + X-axis lines (~8 LOC)
5. X-axis label + tick labels (~14 LOC)
6. Y-axis tick labels (~14 LOC)
7. Data line + dots (~5 LOC)
8. Series label text (~5 LOC)

`_plot_points` (45 LOC) already extracts data filtering and coordinate mapping.

**Split candidates:**

- `_draw_axes()` — axis lines
- `_draw_x_labels()` — x-axis label and tick texts
- `_draw_y_labels()` — y-axis tick texts
- `_draw_line_and_dots()` — data line + point circles

**Risk**: MEDIUM. Canvas drawing is order-sensitive and has side effects.
Splitting into helpers is safe if each helper just wraps a group of
`canvas.create_*` calls, but any helper must not re-order or skip operations.

**Test/smoke need**: `py_compile` is sufficient for compilation, but visual
regression requires Windows GUI smoke because canvas rendering is not easily
unit-testable.

**Verdict**: `_draw` split is valid but should be a separate slice after
`__init__` split is complete and stable.

## External Contract and Regression Risk (Task 5)

**Public-ish contract methods (called by 4 section files):**

- `set_sources(sources, *, source_order, selected, panel_status)` — MUST
  preserve signature and behavior.
- `set_status(status)` — MUST preserve signature.
- `copy_table() -> bool` — MUST preserve signature.
- `export_csv() -> bool` — MUST preserve signature.
- `selected_source() -> str` — Internal but used by `set_sources`.
- `grid(**kwargs)` / `grid_remove()` / `is_visible()` — Window shell contract.

**Internal coordination:**

- `_refresh_current_source()` — Coordinates table, graph, summary updates.
  This is the "refresh policy." Splitting `__init__` does not touch this.
- `_on_source_changed()` / `_on_graph_changed()` — Event callbacks. Preserve.

**Contract preservation checklist for any cleanup slice:**

1. `BinDetailSource` dataclass fields must not change.
2. `set_sources` parameter names and defaults must not change.
3. `copy_table` and `export_csv` return type must not change.
4. `grid` / `grid_remove` / `is_visible` behavior must not change.
5. `_refresh_current_source` refresh policy must not change.

## Recommended Next Implementation Slice (Task 6)

**Slice name**: `BinDetailPanel.__init__` setup helper split

**Goal**: Split `BinDetailPanel.__init__` (115 LOC) into private setup helpers
without changing behavior or public contract.

**Files to modify**:
- `ui_tk/sections/bin_detail_panel.py` only

**Proposed helper structure:**

```python
def __init__(...):
    # parameter storage + state init (unchanged)
    self._frame = ttk.Frame(parent)
    self._frame.columnconfigure(0, weight=1)
    self._build_selector_row()
    self._build_summary_label()
    self._build_graph_row()
    self._build_graph_canvas()
    self._build_table()
    self._build_action_buttons()
    self._refresh_current_source()
```

**Excluded in this slice:**
- `BinDetailGraph._draw` changes
- `BinTraceTable` changes
- Section file changes
- Schema changes
- Copy/export behavior changes

**Verification**:
- `python3 -B -m py_compile ui_tk/sections/bin_detail_panel.py`
- `python3 -B tools/check_code_structure.py`
- `git diff --check`
- No pytest needed (pure refactoring, no logic change)
- No Windows smoke needed (no visual change)

**Why this slice first**:
1. Zero behavior change.
2. Single file, low blast radius.
3. No visual regression risk.
4. Easy to verify with compile + structure guard.
5. `_draw` split deferred to a later slice with Windows smoke.

**Alternative slices** (deferred):
- `BinDetailGraph._draw` helper split: valid but needs Windows GUI smoke.
- Controller switch pilot: valid but higher regression risk.

## Excluded Scope

- `BinDetailGraph._draw` split
- `BinTraceTable` changes
- Section file changes
- Schema changes
- Controller switch
- Result formatting helper extraction (completed in 276)

## Risks

- `__init__` helper extraction could accidentally change widget construction
  order. Must preserve exact grid/pack sequence.
- `self._refresh_current_source()` at end of `__init__` must remain.

## Next

- Implement `BinDetailPanel.__init__` setup helper split.
- After stable: `BinDetailGraph._draw` split or controller switch pilot.
