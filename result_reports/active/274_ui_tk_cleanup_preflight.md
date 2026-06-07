# 274 ui_tk Cleanup Preflight Using Reference Evidence Gate

## Goal

Apply the Reference Evidence Gate to identify the safest first cleanup slice in
`ui_tk/`, focusing on table/controller/detail hotspots and duplicate helpers.
No code changes in this slice.

## Scope

- Reference Evidence Gate usage on `docs/code_map/CODEBASE_REFERENCE_MAP.md`.
- Classification of `ui_tk/` active hotspots.
- Table/controller convergence boundary assessment.
- Detail/export/window duplication audit.
- Recommendation for next implementation slice.

## Excluded Scope

- No code changes.
- No test changes.
- No map regeneration (no structural code changes).
- No controller switch implementation.
- No ui_tk cleanup implementation.

## Reference Evidence Gate Usage (Task 1)

Applied per `docs/agent_workflows/DIFF_READ_BUDGET.md`:

- Map read: targeted `grep` on keywords (`Active Hotspots`, `Duplicate`, `table`,
  `controller`, `detail`, `export`, `window`) followed by 30–80 line range reads.
- No broad map reads.
- No map regeneration (code structure unchanged).

## Map Evidence Summary

From `docs/code_map/CODEBASE_REFERENCE_MAP.md` (272-calibrated map):

**ui_tk Active Hotspots** (LOC > 250 or near 400 soft limit):

| File | LOC | Classes | Long Functions |
|------|-----|---------|--------------|
| ui_tk/excel_like_table_controller.py | 398 | 1 | - |
| ui_tk/metric_input_table.py | 388 | 1 | - |
| ui_tk/sections/bin_detail_panel.py | 388 | 3 | __init__(115), _draw(87) |
| ui_tk/batch_matrix_table.py | 364 | 1 | - |
| ui_tk/batch_case_table.py | 321 | 1 | - |
| ui_tk/table/controller.py | 310 | 1 | - |
| ui_tk/table/interaction_core.py | 261 | 1 | - |

**Duplicate / Adjacent Helpers** in `ui_tk/`:

- `_bin_details`: 3 files (hong_kong_cspf_section, iso_iseer_2point_section, iso_saso_t3_section) — identical implementation
- `_metric_value`: 2 files (iso_iseer_2point_section, iso_saso_t3_section) — identical implementation
- `_kwh_value`: 2 files (iso_iseer_2point_section, iso_saso_t3_section) — identical implementation
- `editable_paste_targets`: batch_table.py (thin wrapper), table/interaction_core.py (canonical)
- `editable_clear_targets`: batch_table.py (thin wrapper), table/interaction_core.py (canonical)

## Hotspot Classification (Task 2)

**Category A: Legacy controller (deferred, high regression risk)**

- `ui_tk/excel_like_table_controller.py` (398 LOC)
  - This is the OLD controller used by 4 section files.
  - `TkTableController` (310 LOC, `table/controller.py`) is the new common foundation.
  - Switching sections from `ExcelLikeTableController` to `TkTableController` is the
    eventual goal, but it requires behavior parity validation across paste,
    selection, undo, and navigation.
  - **Verdict**: Do NOT touch in first slice. Controller switch needs its own
    design slice with focused smoke tests.

**Category B: View + adapter hybrid (safe to split)**

- `ui_tk/metric_input_table.py` (388 LOC)
  - Owns widget construction AND `TkTableSurface` adapter methods
    (`row_count`, `column_count`, `text_at_position`, `set_positions_batch`,
    `snapshot`, `cell_frame`, `cell_widget`, etc.).
  - The adapter methods account for a significant portion of the 388 LOC.
  - **Verdict**: Could extract adapter methods into a separate module, but
    `MetricInputTable` is actively used by 4 sections + batch. Risk of
    regression if adapter extraction is not pure.
  - **Defer**: after controller switch stabilizes.

- `ui_tk/batch_matrix_table.py` (364 LOC)
  - Same pattern as `MetricInputTable`: view construction + adapter methods.
  - **Verdict**: Same as MetricInputTable. Defer until common adapter pattern
    is established.

**Category C: Detail panel with long init/draw (good cleanup candidate)**

- `ui_tk/sections/bin_detail_panel.py` (388 LOC)
  - `__init__(115)` and `_draw(87)` are flagged as long functions.
  - Contains `BinDetailPanel` + `BinDetailGraph` classes.
  - **Verdict**: Splitting `__init__` into helper setup methods and `_draw` into
    layout/data/paint phases is a good candidate, but it requires Windows GUI
    smoke for visual regression.
  - **Defer**: needs focused smoke slice.

**Category D: Common foundation (stable, do not split yet)**

- `ui_tk/table/controller.py` (310 LOC) — `TkTableController`
  - This IS the common foundation. Splitting it now would destabilize batch.
  - **Verdict**: Keep stable. Revisit only if it grows beyond 400 LOC.

- `ui_tk/table/interaction_core.py` (261 LOC)
  - Shared clipboard, selection, undo, navigation helpers.
  - **Verdict**: Keep stable. Well-factored pure helpers.

## Table/Controller Convergence Boundary (Task 3)

**Current state:**

- `ExcelLikeTableController` (old, 401 LOC, `ui_tk/excel_like_table_controller.py`)
  - Used by: `hong_kong_cspf_section.py`, `hong_kong_hspf_section.py`,
    `iso_iseer_2point_section.py`, `iso_saso_t3_section.py`
  - Duplicates clipboard parsing, selection bounds, paste validation that already
    exists in `interaction_core.py`.
  - Has its own `parse_clipboard_matrix`, `encode_selection_to_clipboard`,
    `resolve_selection_bounds`, `clip_paste_targets`, `validate_paste_matrix`.

- `TkTableController` (new, 310 LOC, `ui_tk/table/controller.py`)
  - Used by: `batch_table_controller.py` (inherits), `hong_kong_cspf_batch_section.py`
  - Delegates to `interaction_core.py` for clipboard, selection, undo.
  - Is the canonical Excel-like controller for Tk table surfaces.

- `MetricInputTable`
  - Implements `TkTableSurface` adapter methods.
  - Still wired to `ExcelLikeTableController` in the 4 main sections.
  - **Migration precondition**: The adapter methods must be complete and stable.
  - **Risk**: `ExcelLikeTableController` and `TkTableController` have different
    event binding strategies. Direct switch may break keyboard navigation or
    selection behavior.

**Migration path assessment:**

1. Controller switch is NOT the safest first slice.
2. The common foundation (`TkTableController` + `interaction_core`) is stable.
3. The risk is in the section-level wiring and behavior parity.
4. A controller switch slice needs:
   - One pilot section (e.g., `iso_saso_t3_section.py`)
   - Feature parity checklist (paste, undo, selection, keyboard nav)
   - Windows GUI smoke
   - Rollback plan

**Verdict**: Controller switch is a valid later slice, but not the first.

## Detail/Export/Window Duplication (Task 4)

**Clear extraction candidates:**

1. `_bin_details(result) -> list[dict]`
   - Identical in 3 files: `hong_kong_cspf_section.py:246`,
     `iso_iseer_2point_section.py:237`, `iso_saso_t3_section.py:331`
   - 4 lines each. Pure function. Zero side effects.
   - **Extraction value**: High. Establishes SSOT for bin detail normalization.

2. `_metric_value(result, key) -> str`
   - Identical in 2 files: `iso_iseer_2point_section.py:261`,
     `iso_saso_t3_section.py:355`
   - A canonical version already exists in `result_formatting.py`.
   - However, the section versions have a slightly simpler signature than the
     `result_formatting.py` version.
   - **Extraction value**: Medium. Could unify with `result_formatting.py` or
     create a shared `ui_tk/sections/result_helpers.py`.

3. `_kwh_value(result, aliases) -> str`
   - Identical in 2 files: `iso_iseer_2point_section.py:266`,
     `iso_saso_t3_section.py:360`
   - A canonical version already exists in `result_formatting.py`.
   - **Extraction value**: Medium. Same as `_metric_value`.

**Not extraction candidates:**

- `editable_paste_targets` / `editable_clear_targets` in `batch_table.py`:
  These are thin wrapper adapters (converting `BatchColumnRole` to `CellRole`),
  not duplication. This is intentional adapter pattern.

- `_toggle_detail`: This is a class method on section classes, not a top-level
  helper. Each section's detail toggle may have subtle differences.

**Window-related hotspots:**

- `ui_tk/window_shell.py` (151 LOC, 4 classes): Small, stable.
- `ui_tk/window_measurement.py` (131 LOC, 3 classes, `snapshot(61)`): `snapshot`
  is borderline long. Could be split, but low priority.
- `ui_tk/table_grid_model.py` (132 LOC, 4 classes): Stable grid model.

**Verdict**: Detail/export duplication is the safest cleanup target. No UI
behavior change, no Windows smoke needed.

## Recommended Next Implementation Slice (Task 5)

**Slice name**: Extract section-level result formatting helpers

**Goal**: Move duplicated `_bin_details`, `_metric_value`, `_kwh_value` from
section files into a shared helper module.

**Files to modify**:
- `ui_tk/sections/result_formatting.py` (add `_bin_details`, update imports)
- `ui_tk/sections/hong_kong_cspf_section.py` (remove `_bin_details`, import from
  result_formatting)
- `ui_tk/sections/iso_iseer_2point_section.py` (remove `_bin_details`,
  `_metric_value`, `_kwh_value`; import from result_formatting)
- `ui_tk/sections/iso_saso_t3_section.py` (remove `_bin_details`,
  `_metric_value`, `_kwh_value`; import from result_formatting)

**Files NOT to modify**:
- `ui_tk/sections/hong_kong_hspf_section.py` (does not have these duplicates)
- Any controller, table, or batch files
- Any calculator/core files

**Behavior change**: None. Pure function extraction.

**Verification**:
- `python3 -B -m py_compile` on modified files
- `python3 -B tools/check_code_structure.py`
- `git diff --check`
- No pytest needed (pure refactoring, no logic change)
- No Windows smoke needed (no UI behavior change)

**Why this slice first**:
1. Zero behavior change risk.
2. Reduces 3 section file LOC simultaneously.
3. Establishes SSOT pattern for result formatting.
4. Does not block or depend on controller switch.
5. Reference Evidence Gate confirmed the duplication is real and identical.

**Alternative slices** (deferred):
- Controller switch pilot (e.g., `iso_saso_t3_section.py`): valid but needs
  Windows smoke and parity checklist.
- `BinDetailPanel` `__init__`/`_draw` split: valid but needs visual smoke.
- `MetricInputTable` adapter extraction: valid but touching active surface
  with many consumers.

## Excluded Scope

- Controller switch implementation.
- `MetricInputTable` / `BatchMatrixTable` adapter extraction.
- `BinDetailPanel` visual refactoring.
- Any file outside `ui_tk/sections/result_formatting.py` and the 3 section
  files listed above.

## Risks

- Section files may have subtle differences in `_bin_details` usage that are
  not visible in the 4-line function body. Need to verify call sites during
  implementation.
- `result_formatting.py` currently only exports `summarize_cspf_result` and
  `summarize_hspf_result`. Adding `_bin_details` changes its public surface
  slightly. The helper names (`_metric_value`, `_kwh_value`) are already
  private-prefixed, so this is low risk.

## Project Memory Delta

- Reference Evidence Gate confirmed: `_bin_details`, `_metric_value`,
  `_kwh_value` are identical across section files and safe to extract.
- Controller switch is a valid future slice but requires behavior parity
  validation and Windows smoke.
- `ExcelLikeTableController` remains the legacy controller for 4 main
  calculator sections.
- `TkTableController` + `interaction_core.py` are the stable common foundation
  for batch and future migration.

## Next

- **Immediate**: Implement slice "Extract section-level result formatting helpers"
  (move `_bin_details`, `_metric_value`, `_kwh_value` into
  `result_formatting.py`).
- **Later**: Controller switch pilot for one section using `TkTableController`.
