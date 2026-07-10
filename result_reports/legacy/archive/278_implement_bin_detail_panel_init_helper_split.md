# 278 Implement BinDetailPanel.__init__ Setup Helper Split

## Goal

Split `BinDetailPanel.__init__` (115 LOC) into private setup helpers without
changing behavior or public contract.

## Scope

- `ui_tk/sections/bin_detail_panel.py`: split `__init__` widget construction
  into `_build_*` helpers.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`: regenerate after structural
  code change.

## Excluded Scope

- `BinDetailGraph._draw` (deferred to later slice requiring Windows smoke)
- `BinDetailGraph._plot_points` (already well-factored)
- Module-level graph helpers (`_number`, `_flatten`, `_tick_text`,
  `_scale_value_text`)
- `BinDetailSource` dataclass fields
- Public contract methods (`set_sources`, `set_status`, `copy_table`,
  `export_csv`, `grid`, `grid_remove`, `is_visible`)
- `_refresh_current_source()` behavior
- Any other files

## Reference Evidence Gate Usage

Per `docs/agent_workflows/DIFF_READ_BUDGET.md`:

- Map read: targeted `grep` on `BinDetailPanel`, `bin_detail_panel` in
  `CODEBASE_REFERENCE_MAP.md` to confirm hotspot.
- Code read: `rg` for `__init__` and `_draw` boundaries, then targeted range
  reads.
- Map regenerated after structural code changes (new helper methods).

## Helper Split Summary

`__init__` reduced from 115 LOC to ~15 LOC (state init + frame creation +
helper calls + initial refresh):

```python
def __init__(self, parent, *, ...):
    # state init (~8 LOC)
    self._frame = ttk.Frame(parent)
    self._frame.columnconfigure(0, weight=1)

    self._build_selector_row(show_source_selector)
    self._build_summary_label()
    self._build_graph_row()
    self._build_graph_canvas()
    self._build_table()
    self._build_action_buttons()

    self._refresh_current_source()
```

New private helpers:

- `_build_selector_row(show_source_selector)` — selector frame, label,
  combobox, single-source label
- `_build_summary_label()` — summary text label
- `_build_graph_row()` — graph row frame, label, combobox
- `_build_graph_canvas()` — `BinDetailGraph` creation and grid
- `_build_table()` — `BinTraceTable` creation and grid
- `_build_action_buttons()` — copy + CSV buttons

All widget construction order, grid positions, attribute names, callback
bindings, and visible UI text preserved exactly.

## Contract Preservation

- `BinDetailSource` dataclass fields unchanged.
- `set_sources(...)` signature and behavior unchanged.
- `set_status(...)` signature and behavior unchanged.
- `copy_table()` / `export_csv()` return type and behavior unchanged.
- `grid` / `grid_remove` / `is_visible` behavior unchanged.
- `_refresh_current_source()` refresh policy unchanged.

## Code Map Regeneration Result

- Ran `python3 -B tools/code_checker/build_reference_map.py`.
- `ui_tk/sections/bin_detail_panel.py` active hotspot entry:
  - **Before**: `__init__(115), _draw(87)`
  - **After**: `_draw(87)`
  - `__init__` no longer appears as a long function.
- File LOC increased from 388 to 406 (helper method LOC), but each helper
  is under 60 LOC.

## Validation

| Check | Command | Result |
|-------|---------|--------|
| Structural guard | `python3 -B tools/check_code_structure.py` | No new violations; 4 pre-existing soft-limit warnings |
| Compile check | `py_compile ui_tk/sections/bin_detail_panel.py` | OK |
| Bin detail tests | `pytest tests/test_ui_tk_bin_detail_schema.py` | 7 passed, 14 skipped (headless) |
| Code map regen | `python3 -B tools/code_checker/build_reference_map.py` | OK, 226 lines; `__init__` removed from long-function list |
| Git diff check | `git diff --check` | Clean |

## Modified Files

- `ui_tk/sections/bin_detail_panel.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`

## Next

- `BinDetailGraph._draw` helper split (needs Windows GUI smoke)
- Or controller switch design preflight

## Risks

- None for this slice (pure `__init__` refactoring with zero behavior change).
